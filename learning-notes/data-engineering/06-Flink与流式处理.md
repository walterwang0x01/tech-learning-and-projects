# Flink 与流式处理

> Author: Walter Wang

<!-- version-check: Apache Flink 2.0, Flink CDC 3.4, RisingWave 2.2, Materialize, checked 2026-05-10 -->

## 1. 流处理 vs 批处理

```
批处理：
├─ 有界数据（一份文件、一天的日志）
├─ 高吞吐，延迟分钟到小时
└─ 代表：Spark、dbt

流处理：
├─ 无界数据（事件流、CDC 流）
├─ 低延迟（毫秒到秒）
├─ 增量计算
└─ 代表：Flink、Kafka Streams、RisingWave

流批一体（2020s 趋势）：
└─ 同一个计算模型，流和批语义统一
   ├─ Flink SQL
   ├─ Beam
   └─ RisingWave
```

## 2. Flink 核心概念

```
DataStream API（偏底层）
SQL / Table API（推荐大多数场景）

事件时间（Event Time）：
  数据本身的时间（发生时间）
  处理乱序和延迟数据
  Watermark 机制追踪进度

处理时间（Processing Time）：
  处理数据的时间（墙钟）
  简单但结果不一致

精确一次（Exactly-Once）：
  Flink 通过 Checkpoint 实现
  失败恢复不会重复处理

窗口（Windows）：
  ├─ Tumbling：不重叠（每 5 分钟一个）
  ├─ Sliding：滑动（每 1 分钟输出最近 5 分钟）
  ├─ Session：按活动间隔分（用户停止操作 30 分钟为一次会话）
  └─ Global：自定义触发
```

## 3. Flink SQL 实战

### 3.1 从 Kafka 读，写 Postgres

```sql
-- 创建 Kafka Source
CREATE TABLE orders_source (
    order_id BIGINT,
    user_id BIGINT,
    amount DECIMAL(18, 2),
    status STRING,
    event_time TIMESTAMP_LTZ(3),
    WATERMARK FOR event_time AS event_time - INTERVAL '5' SECOND
) WITH (
    'connector' = 'kafka',
    'topic' = 'orders',
    'properties.bootstrap.servers' = 'kafka:9092',
    'format' = 'json',
    'scan.startup.mode' = 'earliest-offset'
);

-- 创建 Postgres Sink
CREATE TABLE hourly_revenue (
    window_start TIMESTAMP,
    window_end TIMESTAMP,
    total_orders BIGINT,
    total_revenue DECIMAL(18, 2),
    PRIMARY KEY (window_start) NOT ENFORCED
) WITH (
    'connector' = 'jdbc',
    'url' = 'jdbc:postgresql://pg:5432/analytics',
    'table-name' = 'hourly_revenue',
    'username' = 'analytics'
);

-- 流式聚合
INSERT INTO hourly_revenue
SELECT
    TUMBLE_START(event_time, INTERVAL '1' HOUR) AS window_start,
    TUMBLE_END(event_time, INTERVAL '1' HOUR) AS window_end,
    COUNT(*) AS total_orders,
    SUM(amount) AS total_revenue
FROM orders_source
WHERE status = 'paid'
GROUP BY TUMBLE(event_time, INTERVAL '1' HOUR);
```

### 3.2 流表 Join

```sql
-- 实时补充维度数据（订单 + 用户信息）
CREATE TABLE users_dim (
    user_id BIGINT PRIMARY KEY NOT ENFORCED,
    name STRING,
    country STRING
) WITH ('connector' = 'jdbc', ...);

SELECT
    o.order_id,
    o.amount,
    u.name,
    u.country
FROM orders_source AS o
LEFT JOIN users_dim FOR SYSTEM_TIME AS OF o.proc_time AS u
    ON o.user_id = u.user_id;
```

### 3.3 CDC 源

```sql
CREATE TABLE orders_cdc (
    id BIGINT PRIMARY KEY NOT ENFORCED,
    user_id BIGINT,
    amount DECIMAL(18, 2),
    status STRING
) WITH (
    'connector' = 'postgres-cdc',
    'hostname' = 'postgres',
    'port' = '5432',
    'database-name' = 'mydb',
    'schema-name' = 'public',
    'table-name' = 'orders',
    'slot.name' = 'flink_slot'
);

-- 写 Iceberg
INSERT INTO iceberg.db.orders SELECT * FROM orders_cdc;
```

详见 [05-CDC与Debezium.md](./05-CDC与Debezium.md)。

## 4. DataStream API（复杂场景）

```java
// Java / Scala（2026 年也有 Python API 日益成熟）
StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();

DataStream<Order> orders = env
    .fromSource(
        KafkaSource.<Order>builder()
            .setTopics("orders")
            .setBootstrapServers("kafka:9092")
            .setDeserializer(new OrderDeserializer())
            .build(),
        WatermarkStrategy.<Order>forBoundedOutOfOrderness(Duration.ofSeconds(5))
            .withTimestampAssigner((o, ts) -> o.eventTime.toEpochMilli()),
        "orders-source"
    );

DataStream<Alert> alerts = orders
    .filter(o -> o.status.equals("failed"))
    .keyBy(o -> o.userId)
    .window(TumblingEventTimeWindows.of(Duration.ofMinutes(5)))
    .aggregate(new FailureCountAggregator())
    .filter(agg -> agg.count >= 3)
    .map(agg -> new Alert(agg.userId, "multiple failures"));

alerts.sinkTo(
    KafkaSink.<Alert>builder()
        .setBootstrapServers("kafka:9092")
        .setRecordSerializer(new AlertSerializer())
        .build()
);

env.execute("fraud-detection");
```

## 5. Flink 2.0 亮点（2025）

```
├─ Python API 成熟度大幅提升（PyFlink）
├─ Async 状态 API
├─ Disaggregated State（状态和计算分离，云原生友好）
├─ SQL 增强（Lateral Join、Window TVF 改进）
├─ Flink CDC 3.4：支持 Kafka Connect 模式
└─ 移除遗留 API（DataSet API 废弃）
```

## 6. RisingWave：流数据库新贵

RisingWave 把 Flink 和 Postgres 的优点结合：

```
流数据库的价值：
├─ 用 SQL 定义"持续更新的物化视图"
├─ 像 Postgres 一样查询（wire-compatible）
├─ 自动维护状态
└─ 不需要懂 Flink 的 Watermark、State 等细节
```

```sql
-- 连接 Kafka
CREATE SOURCE orders (
    order_id BIGINT,
    user_id BIGINT,
    amount DECIMAL,
    created_at TIMESTAMP
) WITH (
    connector = 'kafka',
    topic = 'orders',
    properties.bootstrap.server = 'kafka:9092'
) FORMAT PLAIN ENCODE JSON;

-- 定义一个持续维护的物化视图
CREATE MATERIALIZED VIEW hourly_revenue AS
SELECT
    window_start,
    SUM(amount) AS revenue,
    COUNT(*) AS order_count
FROM TUMBLE(orders, created_at, INTERVAL '1 HOUR')
GROUP BY window_start;

-- 应用 / Agent 直接查
SELECT * FROM hourly_revenue ORDER BY window_start DESC LIMIT 24;
-- RisingWave 保证结果是最新的
```

**2026 年趋势**：AI Agent 不直接消费 Kafka，而是查 RisingWave 的物化视图（见 [architecture/01-事件驱动架构.md](../architecture/01-事件驱动架构.md#10-2026-年-eda--ai-agent-新范式)）。

## 7. Materialize：类似选择

和 RisingWave 类似的流数据库，2019 年由 Materialize, Inc. 商业化。

```
选型对比（2026）：
├─ Flink：最强大、最成熟、自建复杂
├─ RisingWave：开源、Postgres 兼容、云原生
├─ Materialize：商业托管、incrementally maintained view
└─ Kafka Streams：简单场景、Java/Scala 集成
```

## 8. 状态管理

流处理的难点是"状态"：

```
状态类型：
├─ Keyed State（按 key 分区）
│   ├─ ValueState：单值
│   ├─ ListState：列表
│   ├─ MapState：KV
│   └─ ReducingState / AggregatingState
└─ Operator State（算子级）

状态后端：
├─ HashMap（内存，小状态）
├─ RocksDB（磁盘，大状态，推荐生产）
└─ Flink 2.0 Disaggregated（状态存 S3）

Checkpoint：
├─ Flink 自动把状态 snapshot 到持久存储
├─ 失败从最近 checkpoint 恢复
└─ 实现 exactly-once
```

## 9. 容错与恢复

```
Exactly-once 语义需要：
├─ 源端：支持 offset 回放（Kafka ✅）
├─ 计算：Flink Checkpoint
├─ 目标端：幂等或事务
│   ├─ Kafka：事务性写
│   ├─ JDBC：UPSERT
│   └─ HDFS/S3：两阶段提交
└─ 整个链路的协同（两阶段提交）
```

## 10. 监控指标

```
必监控：
├─ Checkpoint 时间和大小（增长表示状态爆炸）
├─ Backpressure（反压）：哪个算子在拖后腿
├─ Records In/Out
├─ Watermark Lag
├─ Restart 次数（频繁重启表示有问题）
└─ JVM：Heap、GC 时间

工具：
├─ Flink Web UI（内置）
├─ Prometheus + Grafana
├─ AWS/GCP 托管监控
```

## 11. 典型反模式

```
❌ State 无限增长（用 Processing Time 窗口 + 长时间运行）
   → 内存 / RocksDB 爆
   ✅ 用 TTL / Event Time + 合理窗口

❌ 没配 Watermark 或配得太激进
   → 延迟数据被丢 / Window 永远不触发
   ✅ 根据业务合理设置乱序容忍

❌ 把大对象放 State
   → RocksDB I/O 爆
   ✅ 只存必要字段，大 Blob 存外部

❌ Side Effect 在算子里（发邮件、调 API）
   → 重放时重复发
   ✅ Side Effect 放 Sink，幂等

❌ 没做 Backpressure 诊断
   → 吞吐不达标但看不出原因
   ✅ 看 Web UI 的 busy metric
```

## 12. 生产检查清单

```
☐ Checkpoint 启用，频率合理（1 分钟级）
☐ Savepoint 定期保存（升级用）
☐ RocksDB 增量 checkpoint（大状态）
☐ Watermark 策略根据业务定
☐ Exactly-once 链路端到端（source + sink）
☐ 监控：Lag、Backpressure、Restart
☐ 告警：Checkpoint 失败、Lag 超阈值
☐ 资源充足（Memory、Network）
☐ 状态 TTL 配置，防止膨胀
☐ 有 DR 方案（Savepoint 跨集群恢复）
☐ SQL 版本化（Git + CI）
```

## 📖 参考资料

- [Apache Flink 官方](https://flink.apache.org/)
- [Flink CDC](https://nightlies.apache.org/flink/flink-cdc-docs-release-3.4/)
- [RisingWave 文档](https://docs.risingwave.com/)
- [Materialize 文档](https://materialize.com/docs/)
- [Streaming Systems（书）](https://learning.oreilly.com/library/view/streaming-systems/9781491983867/)
- 关联：[architecture/01-事件驱动架构.md](../architecture/01-事件驱动架构.md)
