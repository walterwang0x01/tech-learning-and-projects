# Lakehouse 表格式：Iceberg / Delta / Hudi

> Author: Walter Wang

<!-- version-check: Iceberg 1.10.1 stable, 1.11.0 RC, V4 spec design progressing, Delta Lake 4.0, Hudi 1.0, Polaris 1.4.1, checked 2026-05-16 -->

## 1. 为什么需要表格式

Parquet / ORC 只是"文件格式"，不是"表"：

```
只有 Parquet 文件的问题：
├─ 并发写会相互覆盖
├─ 删除和更新要重写整个文件
├─ 没有版本和时间旅行
├─ Schema 变更要重跑所有数据
└─ 不同引擎看到的"表"可能不一致

表格式（Iceberg / Delta / Hudi）：
├─ ACID 事务
├─ Schema Evolution
├─ 分区演进（改分区策略不重写数据）
├─ 时间旅行（看任意历史版本）
├─ 快照 + 隔离
└─ 引擎无关（Spark / Flink / Trino / DuckDB 都能读）
```

## 2. 三足鼎立 → Iceberg 胜出

```
2020 前后：Delta、Iceberg、Hudi 各有优势
2024-2026：Iceberg 在开放生态上胜出，成为事实标准

关键事件：
├─ 2024-06 Databricks 收购 Tabular（Iceberg 创始团队）
│   承诺保持 Iceberg 开放并让 Delta 和 Iceberg 兼容
├─ 2024+ Snowflake、BigQuery、Redshift 全部支持 Iceberg
├─ 2025 AWS S3 Tables（托管 Iceberg）
└─ 2026 Iceberg 1.10+ 成熟：V3 Spec、View、流式 Schema Evolution、V4 设计中
```

## 3. 三者对比

| 维度 | Iceberg 1.10 | Delta Lake 4.0 | Hudi 1.0 |
|------|-------------|-----------------|----------|
| **主导** | Apache（Netflix 起源） | Databricks 主导，开源 | Apache（Uber 起源） |
| **引擎支持** | Spark / Flink / Trino / DuckDB / Snowflake / BQ / Redshift | Spark 最强，Trino / Flink / DuckDB | Spark / Flink / Presto |
| **写并发** | 乐观并发控制 | 乐观并发控制 | MOR / COW 两种 |
| **Schema Evolution** | 最灵活（名字-based） | 灵活（位置-based 为主） | 支持 |
| **分区演进** | ✅（不重写数据） | ⚠️（重写） | ⚠️ |
| **时间旅行** | ✅ | ✅ | ✅ |
| **Row-level 操作** | v2+ Merge-on-Read | Deletion Vectors | MOR 原生 |
| **Catalog** | REST Catalog（标准）/ Hive / Glue / Nessie | Unity Catalog | Hive |
| **View / MV** | ✅（View，MV in dev） | ⚠️ | ⚠️ |
| **开放生态** | 最强 | 强（Databricks 生态） | 中 |

## 4. Iceberg 架构

```
┌──────── Iceberg 数据组织 ────────┐
│                                   │
│  Catalog（表注册中心）              │
│  └─ REST / Hive / Glue / Nessie   │
│           ↓                       │
│  Table Metadata                   │
│  └─ v3.metadata.json（表的最新状态）│
│           ↓                       │
│  Snapshot（每次提交一个快照）        │
│  └─ Manifest List                 │
│           ↓                       │
│  Manifest File（文件级索引）         │
│  └─ Data File（实际的 Parquet）     │
│                                   │
│  特点：                             │
│  ├─ 所有变更生成新快照，不改旧文件      │
│  ├─ 时间旅行只是指向旧快照             │
│  └─ VACUUM / Expire Snapshots 回收空间 │
└───────────────────────────────────┘
```

## 5. 用 Iceberg（Spark 示例）

```python
from pyspark.sql import SparkSession

spark = SparkSession.builder \
    .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.10.1") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.my_catalog", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.my_catalog.type", "rest") \
    .config("spark.sql.catalog.my_catalog.uri", "http://iceberg-rest:8181") \
    .config("spark.sql.catalog.my_catalog.warehouse", "s3://my-bucket/warehouse") \
    .getOrCreate()

# 建表
spark.sql("""
    CREATE TABLE my_catalog.db.orders (
        order_id BIGINT,
        user_id BIGINT,
        amount DOUBLE,
        status STRING,
        created_at TIMESTAMP
    ) USING iceberg
    PARTITIONED BY (days(created_at))
""")

# 插入
spark.sql("""
    INSERT INTO my_catalog.db.orders VALUES
        (1, 101, 99.9, 'paid', TIMESTAMP '2026-05-10 10:00:00')
""")

# MERGE INTO（upsert）
spark.sql("""
    MERGE INTO my_catalog.db.orders t
    USING updates s
    ON t.order_id = s.order_id
    WHEN MATCHED THEN UPDATE SET t.status = s.status
    WHEN NOT MATCHED THEN INSERT *
""")

# 时间旅行
spark.sql("SELECT * FROM my_catalog.db.orders VERSION AS OF 12345")
spark.sql("SELECT * FROM my_catalog.db.orders TIMESTAMP AS OF '2026-05-01 00:00:00'")

# 回滚
spark.sql("CALL my_catalog.system.rollback_to_snapshot('db.orders', 12345)")

# 分区演进
spark.sql("ALTER TABLE my_catalog.db.orders ADD PARTITION FIELD status")
# 新数据按 (days(created_at), status) 分区，老数据不动
```

## 6. 用 DuckDB 读 Iceberg（无需 Spark）

DuckDB 1.5+ 可以直接读 Iceberg：

```sql
INSTALL iceberg;
LOAD iceberg;

-- 读 Iceberg 表
SELECT count(*) FROM iceberg_scan('s3://my-bucket/warehouse/db/orders/');

-- 配合 REST Catalog
ATTACH 'iceberg_rest' AS rest (TYPE iceberg_catalog);
SELECT * FROM rest.db.orders;
```

## 7. Flink + Iceberg：流入湖

```sql
-- Flink SQL
CREATE CATALOG iceberg WITH (
    'type' = 'iceberg',
    'catalog-type' = 'rest',
    'uri' = 'http://iceberg-rest:8181',
    'warehouse' = 's3://my-bucket/warehouse'
);

-- Kafka 作为源
CREATE TABLE kafka_orders (
    order_id BIGINT,
    user_id BIGINT,
    amount DOUBLE,
    created_at TIMESTAMP(3)
) WITH (
    'connector' = 'kafka',
    'topic' = 'orders',
    'format' = 'json',
    ...
);

-- 流式写入 Iceberg
INSERT INTO iceberg.db.orders
SELECT * FROM kafka_orders;
```

## 8. S3 Tables（AWS 托管 Iceberg）

2024-12 AWS 发布，2026 成熟：

```
S3 Tables：
├─ 托管的 Iceberg 表桶
├─ 自动 compaction（不用自己调度）
├─ 内置 Catalog（兼容 REST）
├─ 比自建 Iceberg 低 3x 存储成本、快 10x 查询
└─ Athena / EMR / Redshift 一键接入
```

这让 "自建 Lakehouse" 的运维门槛大幅降低。

## 9. 维护任务

```sql
-- Expire 旧快照（回收空间）
CALL my_catalog.system.expire_snapshots(
    table => 'db.orders',
    older_than => TIMESTAMP '2026-01-01'
);

-- 小文件合并
CALL my_catalog.system.rewrite_data_files(
    table => 'db.orders',
    strategy => 'binpack',
    options => map('target-file-size-bytes', '134217728')  -- 128 MB
);

-- 孤儿文件清理
CALL my_catalog.system.remove_orphan_files(
    table => 'db.orders',
    older_than => TIMESTAMP '2026-04-01'
);
```

生产建议：每天调度 compaction，每周 expire snapshots。

## 10. Schema Evolution

```sql
-- Iceberg 允许的操作（都不会重写数据）
ALTER TABLE orders ADD COLUMN country STRING;
ALTER TABLE orders ALTER COLUMN amount TYPE DECIMAL(18, 4);
ALTER TABLE orders DROP COLUMN deprecated_col;
ALTER TABLE orders RENAME COLUMN amount TO amount_cents;

-- 老查询仍然能读老数据（schema 按版本解析）
```

## 11. 选型决策

```
选 Iceberg：
├─ 新项目（2026 标准答案）
├─ 多引擎访问（Spark + Trino + DuckDB + BQ）
├─ 需要分区演进
└─ 开放生态优先

选 Delta Lake：
├─ 已在 Databricks 生态
├─ Spark-only 团队
└─ Unity Catalog 需求

选 Hudi：
├─ 有超低延迟写入需求（MOR）
├─ 已在 Hudi 上建设
└─ 新项目少见
```

## 12. 反模式

```
❌ Iceberg 上做 OLTP（高频小 INSERT）
   → 大量小文件 + metadata 膨胀
   → 用 Flink 做微批聚合，或直接用 OLTP DB

❌ 不做 compaction
   → 小文件爆炸，查询越来越慢

❌ 无限保留所有快照
   → 元数据膨胀，S3 成本飙升

❌ 跨表事务假设
   → 大多数表格式不支持跨表事务，只有单表 ACID

❌ 直接读底层 Parquet
   → 绕过 metadata 会读到废弃数据
```

## 13. Iceberg 1.10.x 版本演进

> 🔄 更新于 2026-05-13

Iceberg 1.10.0（2026-01）→ 1.10.1（当前最新稳定版），109 PRs / 28 贡献者。

### 13.1 核心新特性

| 特性 | 说明 |
|------|------|
| **Spark 4.0 + Flink 2.0 支持** | 与最新批处理和流处理引擎对齐 |
| **V3 Spec 成熟** | 多值字段（List/Map 分区）、默认值、行级 lineage |
| **流式 Schema Evolution** | 输入流 schema 变更自动传播到 Iceberg 表，无需手动 ALTER |
| **REST Catalog 增强** | 标准化 Catalog API，多引擎互操作的基础 |
| **C++ SDK 0.2.0** | 高性能原生读取，DuckDB/Arrow 生态集成 |

来源：[Iceberg 1.10 Release](https://iceberg.apache.org/releases/)、[Google Cloud Blog](https://goo.gle/apache-iceberg-1-10)、[Snowflake Blog](https://www.snowflake.com/en/engineering-blog/apache-iceberg-1-10-new-features-fixes/)

### 13.2 V4 Spec 设计中（2026 Q2 更新）

> 🔄 更新于 2026-05-16

Iceberg 社区在 2026 年 4-5 月的 Apache Data Lakehouse Weekly 中持续推进 V4 设计，**1.11.0 已经进入 release candidate**（基于多周的 V4 设计跟进工作）。来源：[Apache Data Lakehouse Weekly 2026-05](https://amdatalakehouse.substack.com/p/apache-data-lakehouse-weekly-may)

**V4 核心设计方向**：

| 维度 | V3 现状 | V4 设计目标 |
|------|---------|-------------|
| metadata.json | 强制存在于根目录 | 可选——支持 catalog-managed metadata 模式 |
| 静态表可移植性 | 隐式依赖根 JSON | 显式 opt-in 语义保留可移植性 |
| 元数据压缩 | 单文件 | 更高效的层级压缩 |
| CDC | 需外部工具 | 原生支持（讨论中） |

**驱动 V4 的关键贡献者**：Anton Okolnychyi、Yufei Gu、Shawn Chang、Steven Wu。来源：[Apache Data Lakehouse Weekly 2026-04](https://amdatalakehouse.substack.com/p/apache-data-lakehouse-weekly-april-29b)

**Polaris 1.4.1 + 1.5 路线图**：与 Iceberg V4 同步推进 catalog 端的能力，1.4.1 是 security-focused 补丁，4 个 CVE 协调披露。Polaris 已被多家 Lakehouse 厂商作为标准 Catalog。来源：[Apache Polaris Standard](https://www.dremio.com/blog/apache-polaris-the-catalog-standard-for-lakehouses-and-ai/)

**对工程团队的影响**：

```
现在生产用 1.10.1：
├─ 持续观察 V4 草案，但不要急于试用 1.11.0 RC
├─ 把 catalog 升级到 Polaris 1.4.1（修复 CVE）
└─ 评估 catalog-managed metadata 模式对运维的简化

2026 H2 准备升级：
├─ V4 spec 预计在 2026 下半年定稿
├─ 主流引擎（Spark / Flink / Trino）会同步支持
└─ 提前规划 metadata 压缩策略，迁移成本相对小
```

### 13.3 版本选择建议

```
新项目：直接用 Iceberg 1.10.1
├─ Spark 4.0 + Flink 2.0 支持
├─ REST Catalog 标准化
└─ V3 Spec 完整功能

已有 1.9.x 项目：
├─ 建议升级到 1.10.1（向后兼容）
├─ 流式 Schema Evolution 减少运维负担
└─ 注意 Spark/Flink 版本对齐
```

## 📖 参考资料

- [Apache Iceberg 文档](https://iceberg.apache.org/docs/latest/)
- [Delta Lake 文档](https://docs.delta.io/)
- [Apache Hudi](https://hudi.apache.org/)
- [S3 Tables Overview](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables.html)
- [Iceberg vs Delta vs Hudi](https://www.onehouse.ai/blog/apache-hudi-vs-delta-lake-vs-apache-iceberg-lakehouse-feature-comparison)
