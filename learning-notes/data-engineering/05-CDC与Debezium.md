# CDC 与 Debezium

> Author: Walter Wang

<!-- version-check: Debezium 3.2, Flink CDC 3.4, Kafka Connect, checked 2026-05-10 -->

## 1. 什么是 CDC

**Change Data Capture（变更数据捕获）**：实时捕获数据库的 INSERT / UPDATE / DELETE 操作，以事件形式发布。

```
应用 → 写 DB
         ↓
    DB WAL/Binlog（数据库内部的变更日志）
         ↓
      CDC Engine
         ↓
   Kafka / Pulsar / S3 / 下游库
```

## 2. 为什么要 CDC

```
传统方案的问题：
├─ 双写（应用同时写 DB + Kafka）
│   → 容易不一致（一个成功一个失败）
│
├─ 定时拉取（SELECT * WHERE updated_at > X）
│   → 延迟高、抓不到 DELETE、有压力
│
└─ 应用层发事件
    → 耦合业务代码，容易漏

CDC 的优势：
├─ 零侵入（从 WAL / Binlog 读）
├─ 保证一致（DB 提交 = 事件必然发出）
├─ 低延迟（毫秒级）
├─ 捕获所有操作（包括删除）
└─ 业务代码不用改
```

## 3. 应用场景

```
CDC 的典型用途：
├─ 数据库同步（主从、异构迁移）
├─ Data Warehouse 实时同步（OLTP → OLAP）
├─ 缓存失效（DB 变了就清 Redis）
├─ 搜索索引更新（DB → Elasticsearch）
├─ 事件驱动架构（构建事件流）
├─ 审计日志
└─ AI Agent 记忆更新（DB 变化 → 更新向量库）
```

## 4. Debezium 架构

Debezium 是目前最主流的 CDC 引擎，支持 MySQL / Postgres / MongoDB / Oracle / SQL Server / Db2 等。

```
┌────────── Debezium 架构 ──────────┐
│                                    │
│  源数据库                            │
│  └─ WAL / Binlog                  │
│         ↓                          │
│  Debezium Connector                │
│  ├─ 作为 Kafka Connect Source      │
│  └─ 或作为 Server 独立运行          │
│         ↓                          │
│  Kafka Topics（每张表一个 topic）   │
│  └─ mydb.public.orders 等          │
│         ↓                          │
│  Consumer                          │
│  ├─ Sink Connector → 下游库        │
│  ├─ Flink / Spark Streaming        │
│  └─ 自定义应用                      │
└────────────────────────────────────┘
```

## 5. Postgres CDC 实战

### 5.1 Postgres 配置

```ini
# postgresql.conf
wal_level = logical
max_wal_senders = 10
max_replication_slots = 10
```

```sql
-- 创建复制用户
CREATE ROLE replicator WITH REPLICATION LOGIN PASSWORD 'secret';
GRANT CONNECT ON DATABASE mydb TO replicator;
GRANT USAGE ON SCHEMA public TO replicator;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO replicator;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT ON TABLES TO replicator;

-- 创建复制槽（Debezium 会自动创建）
-- SELECT pg_create_logical_replication_slot('debezium', 'pgoutput');

-- 创建 Publication
CREATE PUBLICATION dbz_publication FOR ALL TABLES;
```

### 5.2 Debezium Connector 配置

```json
{
  "name": "postgres-orders-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "replicator",
    "database.password": "secret",
    "database.dbname": "mydb",
    "plugin.name": "pgoutput",
    "publication.name": "dbz_publication",
    "slot.name": "debezium_slot",
    "topic.prefix": "mydb",
    "table.include.list": "public.orders,public.users",
    "snapshot.mode": "initial",
    "heartbeat.interval.ms": "10000"
  }
}
```

```bash
# 注册
curl -X POST http://kafka-connect:8083/connectors \
  -H "Content-Type: application/json" \
  -d @postgres-connector.json
```

### 5.3 生成的事件

```json
{
  "schema": { ... },
  "payload": {
    "before": null,
    "after": {
      "id": 123,
      "user_id": 1,
      "amount": 99.9,
      "status": "pending"
    },
    "source": {
      "version": "3.2.0.Final",
      "connector": "postgresql",
      "name": "mydb",
      "ts_ms": 1715328000000,
      "snapshot": "false",
      "db": "mydb",
      "schema": "public",
      "table": "orders",
      "lsn": 12345678,
      "xmin": null
    },
    "op": "c",    // c=create, u=update, d=delete, r=read (snapshot)
    "ts_ms": 1715328000100
  }
}
```

## 6. Outbox 模式：业务事件和 DB 写入原子化

"我不想发出所有 DB 变更事件，只想发业务事件" → Outbox 模式：

```sql
-- 应用在一个事务里写两张表
BEGIN;
INSERT INTO orders (...) VALUES (...);
INSERT INTO outbox (aggregate_id, event_type, payload)
VALUES (123, 'OrderPlaced', '{"order_id": 123, ...}');
COMMIT;
```

Debezium 从 `outbox` 表捕获事件，配合 **Outbox Event Router** 可以路由到不同 topic：

```json
{
  "transforms": "outbox",
  "transforms.outbox.type": "io.debezium.transforms.outbox.EventRouter",
  "transforms.outbox.table.field.event.key": "aggregate_id",
  "transforms.outbox.table.field.event.type": "event_type",
  "transforms.outbox.route.by.field": "event_type",
  "transforms.outbox.route.topic.replacement": "events.${routedByValue}"
}
```

好处：
- 业务事件和 DB 操作原子化
- 事件 Schema 可控（不暴露 DB 内部字段）
- 历史事件在 outbox 表里可查

## 7. Flink CDC：流入流出一体

Flink CDC（阿里开源）把 Debezium 嵌入 Flink，免去 Kafka 中转。

```sql
-- Flink SQL
CREATE TABLE orders_source (
    id INT PRIMARY KEY NOT ENFORCED,
    user_id INT,
    amount DECIMAL(10, 2),
    status STRING
) WITH (
    'connector' = 'postgres-cdc',
    'hostname' = 'postgres',
    'port' = '5432',
    'username' = 'replicator',
    'password' = 'secret',
    'database-name' = 'mydb',
    'schema-name' = 'public',
    'table-name' = 'orders'
);

-- 直接写到 Iceberg
CREATE TABLE orders_sink (...) WITH ('connector' = 'iceberg', ...);
INSERT INTO orders_sink SELECT * FROM orders_source;

-- 或做聚合
CREATE VIEW daily_sales AS
SELECT DATE(created_at) AS d, SUM(amount) FROM orders_source GROUP BY DATE(created_at);
```

## 8. 下游处理模式

### 8.1 写 Elasticsearch

```json
// Kafka Connect ElasticsearchSinkConnector
{
  "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
  "topics": "mydb.public.orders",
  "connection.url": "http://elasticsearch:9200",
  "key.ignore": "false",
  "behavior.on.null.values": "delete"
}
```

### 8.2 写 ClickHouse

```sql
-- ClickHouse 直接消费 Kafka
CREATE TABLE orders_kafka (
    id UInt64,
    user_id UInt64,
    amount Decimal(10, 2),
    status String,
    op String
) ENGINE = Kafka()
SETTINGS kafka_broker_list = 'kafka:9092',
         kafka_topic_list = 'mydb.public.orders',
         kafka_format = 'JSONEachRow';

CREATE TABLE orders_ch (
    id UInt64,
    user_id UInt64,
    amount Decimal(10, 2),
    status String,
    _version UInt64
) ENGINE = ReplacingMergeTree(_version)
ORDER BY id;

CREATE MATERIALIZED VIEW orders_mv TO orders_ch AS
SELECT
    id, user_id, amount, status,
    toUnixTimestamp(now()) AS _version
FROM orders_kafka
WHERE op != 'd';
```

### 8.3 应用订阅

```python
from confluent_kafka import Consumer
import json

consumer = Consumer({
    "bootstrap.servers": "kafka:9092",
    "group.id": "cache-invalidator",
    "auto.offset.reset": "earliest",
})
consumer.subscribe(["mydb.public.orders"])

while True:
    msg = consumer.poll(1.0)
    if msg is None:
        continue

    event = json.loads(msg.value())
    op = event["payload"]["op"]
    after = event["payload"]["after"]

    if op in ("c", "u"):
        # 更新缓存
        redis.set(f"order:{after['id']}", json.dumps(after))
    elif op == "d":
        redis.delete(f"order:{event['payload']['before']['id']}")
```

## 9. 生产注意事项

### 9.1 Exactly-Once

Debezium + Kafka 默认是 **at-least-once**。下游消费者必须幂等：

```python
# 使用事件中的主键 + LSN/序列号 做去重
def handle_event(event):
    lsn = event["source"]["lsn"]
    op_key = f"{event['source']['table']}:{event['payload']['after']['id']}:{lsn}"

    if redis.set(f"processed:{op_key}", "1", nx=True, ex=3600):
        actually_process(event)
```

### 9.2 Replication Slot 泄漏

Postgres 的复制槽会阻止 WAL 回收。连接器挂掉但槽还在 = 磁盘迅速爆满。

```sql
-- 监控复制延迟
SELECT
    slot_name,
    pg_size_pretty(pg_wal_lsn_diff(pg_current_wal_lsn(), restart_lsn)) AS lag
FROM pg_replication_slots;
```

告警：`lag > 10 GB` 时立即处理。

### 9.3 Schema Evolution

源表加字段：
- Debezium 自动检测
- 下游需要兼容处理（用 Avro Schema Registry 最稳）

源表删字段 / 改类型：
- 需要协调上下游，通常走维护窗口

### 9.4 初始快照

首次启动 Debezium 会对全表做快照，大表（10亿行）可能几天。

解决：
- `snapshot.mode=never` + 用其他方式预同步
- 或 `snapshot.mode=incremental`（3.0+）：切片快照，不阻塞

## 10. 反模式

```
❌ CDC 下游直接改业务库
   → 循环依赖

❌ 把 CDC 当事件驱动唯一方案
   → 业务事件用 Outbox，不要把 DB 内部变化当业务事件

❌ 不监控复制延迟
   → 槽积压导致磁盘爆满

❌ Debezium Single Message Transform 写复杂逻辑
   → SMT 调试困难，复杂转换交给下游 Flink

❌ 忽视删除事件
   → 下游数据无法清理，最终脏数据堆积
```

## 11. 2026 年生态地图

| 工具 | 定位 |
|------|------|
| **Debezium** | 开源 CDC 标准，多数据库支持 |
| **Flink CDC** | 流批一体，去 Kafka 化 |
| **Airbyte** | 托管 ELT，简化版 CDC |
| **Fivetran** | 商业 ELT，覆盖 SaaS 数据源 |
| **Striim** | 企业级实时集成 |
| **AWS DMS** | AWS 托管，侧重迁移场景 |
| **PeerDB** | Postgres → 分析库，性能优化 |

## 📖 参考资料

- [Debezium 文档](https://debezium.io/documentation/)
- [Flink CDC 文档](https://nightlies.apache.org/flink/flink-cdc-docs-release-3.4/)
- [Outbox Pattern](https://microservices.io/patterns/data/transactional-outbox.html)
- [Designing Data-Intensive Applications - Chapter 11](https://dataintensive.net/)
