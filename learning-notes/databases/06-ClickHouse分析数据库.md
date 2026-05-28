# ClickHouse 分析数据库

> Author: Walter Wang

<!-- version-check: ClickHouse 26.5 (2026-05-21 GA), 26.4 stable, 26.3 LTS, checked 2026-05-28 -->

## 1. 为什么要了解 ClickHouse

2026 年 ClickHouse 已经是开源 OLAP 领域的事实标准。SigNoz、Uptrace、PostHog、Plausible 这些现代可观测性平台的底层都是它。

```
┌──────── ClickHouse 的独特之处 ────────┐
│                                        │
│  写入：百万行/秒（单节点）               │
│  查询：亿行表秒级聚合                    │
│  存储：列式 + 高压缩比（10-100x）         │
│  SQL：兼容，加了大量 OLAP 函数           │
│  架构：Shared-Nothing，水平扩展简单       │
│                                        │
│  不擅长：                                │
│  ├─ 点查（用 PG / KV）                  │
│  ├─ 频繁 UPDATE / DELETE                │
│  ├─ 事务                                │
│  └─ 复杂 JOIN                           │
└────────────────────────────────────────┘
```

## 2. 核心概念：Engine

CH 的每张表要指定 Engine，决定了数据的存储和处理方式：

```sql
-- MergeTree：最常用，支持数据分区、主键、索引
CREATE TABLE events (
    timestamp DateTime64(3),
    user_id UInt64,
    event_type LowCardinality(String),  -- 字典编码，极度节省空间
    properties Map(String, String),
    revenue Float64
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)       -- 按月分区
ORDER BY (event_type, user_id, timestamp)
TTL timestamp + INTERVAL 1 YEAR;       -- 1 年后自动过期

-- ReplicatedMergeTree：带复制（生产必用）
CREATE TABLE events_replicated (...)
ENGINE = ReplicatedMergeTree('/clickhouse/tables/{shard}/events', '{replica}')
...;

-- ReplacingMergeTree：按主键去重
-- SummingMergeTree：按主键自动求和聚合
-- AggregatingMergeTree：和物化视图配合做实时聚合
-- CollapsingMergeTree：用于记录变更历史

-- Log：小表、临时数据
-- Memory：纯内存
-- Distributed：跨分片查询的虚拟表
-- Kafka：直接消费 Kafka 数据
-- MaterializedPostgreSQL：实时复制 PG（CDC）
```

## 3. 建表最佳实践

```sql
-- 生产建议
CREATE TABLE metrics (
    -- 时间作为 ORDER BY 的最后一列
    service LowCardinality(String),
    metric_name LowCardinality(String),
    tags Map(String, String) CODEC(ZSTD(3)),
    value Float64 CODEC(Gorilla, LZ4),   -- 时序数据专用编码
    timestamp DateTime64(3) CODEC(DoubleDelta, LZ4)
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(timestamp)
ORDER BY (service, metric_name, timestamp)
PRIMARY KEY (service, metric_name)   -- 可以比 ORDER BY 短，减少索引内存
SETTINGS index_granularity = 8192;
```

**技巧**：
- 低基数字符串一律用 `LowCardinality(String)`
- 时序数据用 `CODEC(DoubleDelta, LZ4)` 压缩时间戳
- 浮点数用 `CODEC(Gorilla, LZ4)`
- Map 类型存动态标签，比 JSONB 高效
- PARTITION BY 控制单分区不超过几亿行

## 4. 查询示例

```sql
-- 聚合（ClickHouse 的强项）
SELECT
    service,
    toStartOfHour(timestamp) AS hour,
    count() AS events,
    uniqExact(user_id) AS unique_users,     -- 精确去重
    uniq(user_id) AS unique_users_approx,   -- HyperLogLog 近似，快 10x
    quantile(0.99)(duration) AS p99,
    sum(revenue) AS total_revenue
FROM events
WHERE timestamp >= now() - INTERVAL 1 DAY
GROUP BY service, hour
ORDER BY hour DESC;

-- 漏斗分析（windowFunnel）
SELECT
    user_id,
    windowFunnel(3600)(
        timestamp,
        event_type = 'page_view',
        event_type = 'add_to_cart',
        event_type = 'checkout',
        event_type = 'purchase'
    ) AS step
FROM events
GROUP BY user_id;

-- 留存分析
SELECT
    toDate(first_event) AS cohort,
    retention(toDate(first_event) = cohort,
              toDate(timestamp) = cohort + INTERVAL 1 DAY,
              toDate(timestamp) = cohort + INTERVAL 7 DAY,
              toDate(timestamp) = cohort + INTERVAL 30 DAY
    ) AS retention_1_7_30
FROM events;

-- 采样（大表上的近似查询）
SELECT count() FROM events SAMPLE 0.1;   -- 只查 10%，快 10x
```

## 5. 物化视图：流式预聚合

```sql
-- 源表
CREATE TABLE events (...) ENGINE = MergeTree() ...;

-- 目标表（预聚合）
CREATE TABLE events_by_hour (
    service LowCardinality(String),
    hour DateTime,
    count UInt64,
    unique_users AggregateFunction(uniq, UInt64),   -- 中间状态
    revenue_sum Float64
) ENGINE = AggregatingMergeTree()
PARTITION BY toYYYYMM(hour)
ORDER BY (service, hour);

-- 物化视图把 events 的每一次 insert 自动同步到 events_by_hour
CREATE MATERIALIZED VIEW events_by_hour_mv TO events_by_hour AS
SELECT
    service,
    toStartOfHour(timestamp) AS hour,
    count() AS count,
    uniqState(user_id) AS unique_users,
    sum(revenue) AS revenue_sum
FROM events
GROUP BY service, hour;

-- 查询物化视图（秒级）
SELECT
    service,
    hour,
    count,
    uniqMerge(unique_users) AS unique_users,
    revenue_sum
FROM events_by_hour
WHERE hour >= now() - INTERVAL 7 DAY
GROUP BY service, hour, count, revenue_sum;
```

这种模式让仪表盘加载从"10 秒扫亿行"变成"100ms 读几百行"。

## 6. 作为 APM / 日志后端

```sql
-- 典型的 Trace 表（SigNoz 风格）
CREATE TABLE signoz_traces (
    timestamp DateTime64(9),
    trace_id String,
    span_id String,
    parent_span_id String,
    name LowCardinality(String),
    service_name LowCardinality(String),
    duration UInt64,
    status_code LowCardinality(String),
    attributes Map(LowCardinality(String), String),
    events Nested(timestamp DateTime64(9), name String, attributes Map(String, String))
) ENGINE = MergeTree()
PARTITION BY toStartOfHour(timestamp)
ORDER BY (service_name, timestamp, trace_id);
```

查询：

```sql
-- 找某个 trace 的所有 span
SELECT * FROM signoz_traces WHERE trace_id = 'abc123' ORDER BY timestamp;

-- 按服务 P99 延迟
SELECT
    service_name,
    quantile(0.99)(duration) / 1e6 AS p99_ms
FROM signoz_traces
WHERE timestamp >= now() - INTERVAL 1 HOUR
GROUP BY service_name
ORDER BY p99_ms DESC;
```

## 7. 直接消费 Kafka

```sql
-- 消费者表
CREATE TABLE events_kafka (
    timestamp DateTime64(3),
    user_id UInt64,
    event_type String,
    properties String
) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'events',
    kafka_group_name = 'clickhouse-consumer',
    kafka_format = 'JSONEachRow';

-- 目标表
CREATE TABLE events (...) ENGINE = MergeTree() ...;

-- 物化视图做转换
CREATE MATERIALIZED VIEW events_mv TO events AS
SELECT
    timestamp,
    user_id,
    event_type,
    JSONExtractString(properties, 'referer') AS referer
FROM events_kafka;
```

Kafka → ClickHouse 全流程零代码。

## 8. 数据导入

```bash
# CSV
clickhouse-client --query "INSERT INTO events FORMAT CSV" < data.csv

# Parquet（推荐）
clickhouse-client --query "INSERT INTO events FROM INFILE 'data.parquet' FORMAT Parquet"

# 从 S3 直接读
SELECT * FROM s3('https://bucket/path/*.parquet', 'key', 'secret', 'Parquet');

# ClickHouse Local：不用服务就能查本地文件
clickhouse-local --query "SELECT count() FROM file('data.parquet')"
```

## 9. ClickHouse Cloud vs 自建

```
ClickHouse Cloud（托管）
  ├─ 存算分离（S3 + 无状态计算）
  ├─ 按用付费
  └─ 零运维

自建（开源）
  ├─ 成本可控
  ├─ 数据掌握在自己手里
  └─ 需要专人运维
```

生产自建要点：
- ZooKeeper 或 ClickHouse Keeper 做副本协调
- 分片 + 副本：每个分片 2-3 副本
- Backup：`clickhouse-backup` 工具 → S3
- 监控：内置 `system.*` 表 + Prometheus Exporter

## 10. 常见坑

```
❌ 把 CH 当 OLTP 用（高频小 INSERT）
   → 每次 INSERT 产生 part，MergeTree 要合并，开销巨大
   → 改成：批量 INSERT（每批 > 10000 行）或 Buffer 引擎

❌ 频繁 UPDATE / DELETE
   → CH 的 mutation 是异步重写整个 part，非常慢
   → 改用 ReplacingMergeTree 逻辑删除

❌ ORDER BY 顺序错
   → ORDER BY (timestamp, service) 会导致按时间查询快，按服务查询慢
   → 把高选择性、常用于 WHERE 的列放前面

❌ 用 String 存低基数字段
   → 用 LowCardinality(String)，空间节省 10x

❌ 大 JOIN
   → CH 的 JOIN 是 broadcast，右表装进内存
   → 用 Dictionary 或预聚合替代

❌ 不做 TTL
   → 数据无限增长，磁盘很快告急
   → PARTITION + TTL 自动清理
```

## 11. 与 Postgres 的关系

```
决策：业务数据用 PG，分析数据用 CH

常见架构：
  业务写入 → PG
    ↓ CDC（Debezium / PG Replication）
    ↓
  Kafka / S3
    ↓
  ClickHouse（分析、仪表盘、日志）
```

CH 不替代 PG，是互补关系。

## 📖 参考资料

- [ClickHouse 官方文档](https://clickhouse.com/docs)
- [ClickHouse vs Postgres](https://clickhouse.com/blog/clickhouse-vs-postgres)
- [SigNoz 架构（开源 APM 用 CH）](https://signoz.io/)
- [PostHog 架构（开源分析用 CH）](https://posthog.com/blog/clickhouse-at-posthog)

## 12. 版本演进（2026）

> 🔄 更新于 2026-05-14

```
ClickHouse 2026 版本线：
├─ 26.1（2026-01-29）：常规迭代
├─ 26.2（2026-02-26）：常规迭代
├─ 26.3 LTS（2026-03-26）：长期支持版本 ⭐
│   ├─ 27 个新特性、40 个性能优化、202 个 Bug 修复
│   ├─ Async Inserts 默认开启
│   ├─ JOIN 重排序扩展到 ANTI/SEMI/FULL JOIN
│   ├─ Materialized CTEs
│   └─ 推荐生产环境使用
└─ 26.4（2026-04-30）：最新版本
    ├─ 增强 SQL 兼容性（对 PG/MySQL 用户更友好）
    └─ Bool 类型 IN 操作符语义修正
```

### 26.3 LTS 核心变化

**Async Inserts 默认开启**：此前需要手动设置 `async_insert=1`，现在默认启用。对可观测性场景（数百/数千 Agent 持续发送小批量数据）尤其重要——服务端自动批处理，客户端无需关心攒批逻辑。

```sql
-- 26.3 之前：需要手动开启
SET async_insert = 1;
SET wait_for_async_insert = 0;

-- 26.3 起：默认开启，直接写入即可
INSERT INTO logs (timestamp, level, message)
VALUES (now(), 'INFO', 'Agent completed task');
-- 服务端自动批处理，减少 part 数量
```

**JOIN 重排序扩展**：优化器现在可以对 ANTI、SEMI、FULL JOIN 进行重排序，此前仅支持 INNER/LEFT JOIN。对复杂分析查询性能有显著提升。

**Materialized CTEs**：CTE（WITH 子句）可以被物化，避免重复计算。对多次引用同一 CTE 的查询有明显加速。

### 26.4 SQL 兼容性增强

26.4 重点改善了从 PostgreSQL 和其他 SQL 数据库迁移的体验，让 ClickHouse 的 SQL 方言对传统数据库用户更友好。

### 版本选择建议

| 场景 | 推荐版本 |
|------|---------|
| 生产环境（稳定优先） | 26.3 LTS |
| 开发/测试（新特性） | 26.4 |
| 已有 25.x 部署 | 评估升级到 26.3 LTS |

来源：[ClickHouse Release 26.3](https://clickhouse.com/blog/clickhouse-release-26-03)、[ClickHouse 26.4 SQL 兼容性](https://www.tipranks.com/news/private-companies/clickhouse-enhances-sql-compatibility-in-version-26-4)（Content was rephrased for compliance with licensing restrictions）

### 26.5 已正式发布（2026-05-21 GA）

> 🔄 更新于 2026-05-28（修复：26.5 已正式 GA，不再是预告）

ClickHouse 26.5 在 2026-05-21 Community Call 上正式发布。来源：[ClickHouse Changelog 26.5](https://clickhouse.com/docs/whats-new/changelog)、[Release 26.5 Call presentation](https://presentations.clickhouse.com/2026-release-26.5/)、[ClickHouse 26.5 Performance Highlights](https://www.tipranks.com/news/private-companies/clickhouse-emphasizes-performance-and-iceberg-enhancements-in-version-26-5)（Content was rephrased for compliance with licensing restrictions）

**Negative LIMIT BY**：可以用负数从分组的"末尾开始"返回行，原本要写复杂的 `ROW_NUMBER()` 嵌套。

```sql
-- 之前：每个用户最近 3 条事件，要写窗口函数
SELECT * FROM (
    SELECT *, row_number() OVER (PARTITION BY user_id ORDER BY ts DESC) rn
    FROM events
) WHERE rn <= 3;

-- 26.5：直接用负 LIMIT BY 表达"末尾 N 条"
SELECT * FROM events
ORDER BY user_id, ts
LIMIT -3 BY user_id;
-- 等价于"每个 user_id 取按 ts 升序的最后 3 行"
```

**SYSTEM PAUSE VIEW**：让 refreshable materialized view 进入暂停状态，不再触发刷新但保留状态。运维窗口期或下游系统维护时不需要 DROP/重建。

```sql
SYSTEM PAUSE VIEW analytics.daily_revenue_mv;
-- 维护期间停止刷新

SYSTEM RESUME VIEW analytics.daily_revenue_mv;
-- 维护结束后恢复
```

**Iceberg 增强**：26.5 重点提升了对 Apache Iceberg 表格式的兼容性，包括读取性能和元数据处理。

**Cloud changelog 同步**：2026-05 ClickHouse Cloud 已开始把 *index analysis 阶段*分布式化，对 vector search 和 full-text search 这种重二级索引的表减少了单副本内存压力，查询性能通过分布式并行提升。来源：[ClickHouse Cloud changelog 2026](https://clickhouse.com/docs/whats-new/changelog/cloud)

### 版本选择建议（更新版）

| 场景 | 推荐版本 |
|------|---------|
| 生产环境（稳定优先） | 26.3 LTS |
| 开发/测试（最新特性） | 26.5（已 GA） |
| 已有 25.x 部署 | 评估升级到 26.3 LTS 或 26.5 |
