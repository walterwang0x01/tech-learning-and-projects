# Lakehouse 表格式：Iceberg / Delta / Hudi

> Author: Walter Wang

<!-- version-check: Iceberg 1.11.0 (released 2026-05-19), 1.10.1/1.10.2, V4 spec design progressing, Delta Lake 4.0, Hudi 1.0, Polaris 1.5.0 (released 2026-05-18), DuckLake 1.0 GA (2026-04-13), checked 2026-05-28 -->

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

| 维度 | Iceberg 1.11 | Delta Lake 4.0 | Hudi 1.0 |
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
    .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.11.0") \
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

## 13. Iceberg 1.10 → 1.11 版本演进

> 🔄 更新于 2026-05-28

Iceberg 1.10.0（2026-01）→ 1.10.1（2025-12-22）→ **1.11.0（2026-05-19 正式发布）**。
<!-- 修复于 2026-05-28: 将"1.11.0 RC"改为"1.11.0 正式发布"，社区已在 2026-05-19 完成投票 -->

### 13.1 1.10 核心新特性

| 特性 | 说明 |
|------|------|
| **Spark 4.0 + Flink 2.0 支持** | 与最新批处理和流处理引擎对齐 |
| **V3 Spec 成熟** | 多值字段（List/Map 分区）、默认值、行级 lineage |
| **流式 Schema Evolution** | 输入流 schema 变更自动传播到 Iceberg 表，无需手动 ALTER |
| **REST Catalog 增强** | 标准化 Catalog API，多引擎互操作的基础 |
| **C++ SDK 0.2.0** | 高性能原生读取，DuckDB/Arrow 生态集成 |

来源：[Iceberg 1.10 Release](https://iceberg.apache.org/releases/)、[Google Cloud Blog](https://goo.gle/apache-iceberg-1-10)、[Snowflake Blog](https://www.snowflake.com/en/engineering-blog/apache-iceberg-1-10-new-features-fixes/)

### 13.2 1.11.0 关键新特性（2026-05-19 正式发布）

> 🔄 更新于 2026-05-28：1.11.0 已 GA，不再是 RC

| 特性 | 说明 |
|------|------|
| **Partition Statistics Scan API** | 优化器有了支持的接口读取表分区分布 |
| **内置表加密（Envelope Encryption）** | 配合 Google KMS 等密钥管理服务 |
| **Google Storage Analytics 集成** | GCS 读写性能进一步优化 |
| **REST Catalog 联邦能力** | 配合 Polaris 1.5 实现跨 catalog 表读取 |
| **持续向 V4 spec 推进** | 1.11 是 1.10 → V4 之间的过渡版本 |
| **`PartitionStatsHandler` 旧 API 移除** | 1.10 已 deprecated，1.11.0 正式移除 |

**升级到 1.11.0 后启用 partition stats**：

partition stats **不会自动生成**，现有表升级到 1.11.0 后需要显式触发一次计算（增量计算，重复运行开销低）：

```sql
-- Spark SQL：为现有表计算 partition stats
CALL my_catalog.system.compute_partition_stats(
    table => 'db.orders'
    -- 可选：snapshot_id => 12345，默认使用当前快照
);
```

底层调用 `ComputePartitionStatsSparkAction`，从已有 partition stats 的快照之后增量计算到目标快照，写入 `PartitionStatisticsFile`。后续每次大量写入后建议重新触发，配合 compaction 一起调度。

来源：[ComputePartitionStatsSparkAction Javadoc](https://iceberg.apache.org/javadoc/latest/org/apache/iceberg/spark/actions/ComputePartitionStatsSparkAction.html)

来源：[Iceberg 1.11.0 In-Depth Overview](https://medium.com/@alexmercedtech/an-in-depth-overview-of-the-apache-iceberg-1-11-0-release-93b1186199de)、[Announcing Apache Iceberg 1.11.0 - Google](https://www.googblogs.com/announcing-apache-iceberg-1-11-0/)

### 13.3 V4 Spec 设计中（2026 Q2）

Iceberg 社区在 2026 年 4-5 月的 Apache Data Lakehouse Weekly 中持续推进 V4 设计，1.11.0 是 V4 之前的最后一个稳定中转。来源：[Apache Data Lakehouse Weekly 2026-05](https://amdatalakehouse.substack.com/p/apache-data-lakehouse-weekly-may)

**V4 核心设计方向**：

| 维度 | V3 现状 | V4 设计目标 |
|------|---------|-------------|
| metadata.json | 强制存在于根目录 | 可选——支持 catalog-managed metadata 模式 |
| 静态表可移植性 | 隐式依赖根 JSON | 显式 opt-in 语义保留可移植性 |
| 元数据压缩 | 单文件 | 更高效的层级压缩 |
| CDC | 需外部工具 | 原生支持（讨论中） |

**驱动 V4 的关键贡献者**：Anton Okolnychyi、Yufei Gu、Shawn Chang、Steven Wu。来源：[Apache Data Lakehouse Weekly 2026-04](https://amdatalakehouse.substack.com/p/apache-data-lakehouse-weekly-april-29b)

**对工程团队的影响**：

```
现在生产用 1.11.0：
├─ V3 spec 完整功能 + partition stats API + 内置加密
├─ 把 catalog 升级到 Polaris 1.5（federation 能力）
└─ 评估 catalog-managed metadata 模式对运维的简化

2026 H2 准备升级：
├─ V4 spec 预计在 2026 下半年定稿
├─ 主流引擎（Spark / Flink / Trino）会同步支持
└─ 提前规划 metadata 压缩策略，迁移成本相对小
```

### 13.4 版本选择建议

```
新项目：直接用 Iceberg 1.11.0
├─ Spark 4.0 + Flink 2.0 支持
├─ Partition Statistics + 内置加密
└─ V3 Spec 完整功能 + 向 V4 平滑过渡

仍在 1.10.x 项目：
├─ 建议在下次维护窗口升级到 1.11.0（向后兼容）
├─ 重点关注 Partition Stats API 带来的查询计划优化
└─ 注意 Spark/Flink 版本对齐
```

## 📖 参考资料

- [Apache Iceberg 文档](https://iceberg.apache.org/docs/latest/)
- [Delta Lake 文档](https://docs.delta.io/)
- [Apache Hudi](https://hudi.apache.org/)
- [S3 Tables Overview](https://docs.aws.amazon.com/AmazonS3/latest/userguide/s3-tables.html)
- [Iceberg vs Delta vs Hudi](https://www.onehouse.ai/blog/apache-hudi-vs-delta-lake-vs-apache-iceberg-lakehouse-feature-comparison)

## 14. DuckLake 1.0：把元数据放进 SQL 数据库

> 🔄 更新于 2026-05-20

<!-- version-check: DuckLake 1.0 GA (2026-04-13), production-ready, checked 2026-05-20 -->

DuckDB 团队在 2026-04-13 发布 DuckLake v1.0 标准，把 lakehouse 元数据从"分散在对象存储里的成千上万个 JSON 文件"挪进 SQL 数据库。

```
传统 Iceberg / Delta：
  S3 上的目录里
  ├─ metadata/v1.metadata.json
  ├─ metadata/v2.metadata.json
  ├─ snapshots/snap-***.avro
  ├─ manifests/...
  └─ data/*.parquet
  → 每次提交需要原子重写 metadata 指针
  → 列出目录 + 读多个文件才能拿到表的当前状态

DuckLake v1.0：
  Postgres / SQLite / DuckDB 中的几张表保存元数据
  ├─ ducklake_table（表定义）
  ├─ ducklake_snapshot（快照）
  ├─ ducklake_data_file（数据文件清单）
  └─ ducklake_partition_value（分区值）
  + 对象存储里只放 Parquet 数据文件
  → 元数据查询走 SQL，不需要扫目录
  → 多写并发由 SQL 数据库的 ACID 保证
```

### 14.1 设计哲学

DuckLake 的核心论点：lakehouse metadata 是关系型数据，本来就该放进数据库。把元数据 JSON 文件解析成 SQL 表后，原本依赖外部 catalog 服务的能力（多写并发、跨表事务、blob 引用计数）变成了 SQL 自带能力。来源：[DuckDB Blog — DuckLake 1.0](https://duckdb.org/2026/04/13/ducklake-10.html)、[InfoQ — DuckLake 1.0](https://www.infoq.com/news/2026/05/ducklake-sql-catalog/)

### 14.2 v1.0 关键能力

```sql
-- DuckDB 中创建 DuckLake catalog
ATTACH 'ducklake:postgres:host=localhost dbname=metadata' AS lake;
USE lake;

-- 1. Sorted Tables：写入时按列排序，加速范围查询
CREATE TABLE events (
    user_id BIGINT,
    ts TIMESTAMP,
    event_type VARCHAR,
    payload JSON
)
WITH (sort_by = 'ts');

-- 2. Bucket Partitioning（hash 分区，避免数据倾斜）
CREATE TABLE orders (
    order_id BIGINT,
    customer_id BIGINT,
    amount DECIMAL(10, 2),
    created_at TIMESTAMP
)
WITH (partition_by = 'bucket(customer_id, 16)');

-- 3. Data Inlining：小表的数据直接存进元数据库，避免读 Parquet
CREATE TABLE config (
    key VARCHAR PRIMARY KEY,
    value JSON
)
WITH (inline_data = true);  -- 行数 < 阈值时不走 S3
```

### 14.3 v1.0 还有这些

- **Geometry 支持**：GeoParquet 完整集成，用于地理空间分析
- **Iceberg 兼容的 Deletion Vectors**：行级删除走位图，与 Iceberg V3 spec 一致
- **多人多写并发**："multiplayer DuckDB"——多个 DuckDB 进程通过 DuckLake 读写同一数据集，DuckDB 原生 `.duckdb` 格式做不到这一点
- **Iceberg / Delta 互通**：可以把 DuckLake 表导出为 Iceberg 或 Delta，用 Spark/Trino 继续查询

### 14.4 与 Iceberg / Delta / Hudi 的差异

| 维度 | Iceberg / Delta / Hudi | DuckLake 1.0 |
|------|----------------------|---------------|
| 元数据存储 | 对象存储里的 JSON/Avro | SQL 数据库（Postgres/SQLite/DuckDB） |
| Catalog 角色 | 必须有 REST Catalog（Polaris/Glue/Unity） | 元数据库本身就是 catalog |
| 多写并发 | 依赖 catalog 的 atomic compare-and-swap | 依赖 SQL 数据库的事务 |
| 启动门槛 | 需要部署 catalog + Spark/Flink | 一个 DuckDB 进程 + 一个 Postgres |
| 适合场景 | TB - PB 级、跨引擎共享 | GB - 中 TB 级、Agentic Analytics、单机或小集群 |
| 引擎支持 | Spark / Flink / Trino / DuckDB（部分） | DuckDB 原生 + 通过导出与 Iceberg 引擎互通 |

### 14.5 选型建议

```
使用 DuckLake：
├─ 数据规模在 GB ~ 中 TB
├─ 团队不想运维 Polaris/Glue/Unity Catalog
├─ Agentic Analytics 场景：Agent 几秒拉起 lakehouse 跑分析
└─ MotherDuck 用户：托管 DuckLake 已 GA

使用 Iceberg：
├─ PB 级数据 + 跨引擎共享（Spark/Flink/Trino）
├─ 已有 Polaris / Unity / Glue 投入
└─ 需要 V3 spec 的 partition stats、view、object storage 兼容
```

来源：[MotherDuck Blog — DuckLake 1.0 GA](https://motherduck.com/blog/announcing-ducklake-1-0-on-motherduck/)、[ducklake.select](http://ducklake.select/)

## 15. Polaris 1.5.0 GA（2026-05-18 发布）

> 🔄 更新于 2026-05-28

<!-- version-check: Apache Polaris 1.5.0 (released 2026-05-18), Iceberg V4 federation, checked 2026-05-28 -->
<!-- 修复于 2026-05-28: 1.5.0 已正式发布，原文档说"路线图/规划中"过时 -->

Apache Polaris 在 1.4.1 安全补丁（修复 4 个协调披露 CVE）之后，于 **2026-05-18 正式发布 1.5.0**（[官方下载页](https://polaris.apache.org/downloads/1.5.0/)）。

**1.5.0 核心新特性**：

- **Iceberg REST 联邦（GA）**：Polaris 可以代理远端 Iceberg REST Catalog 的表与视图，实现跨 catalog 数据访问（[REST Federation 文档](https://polaris.apache.org/releases/1.5.0/federation/iceberg-rest-federation/)）
- **Hive Metastore 联邦（GA）**：把已有 HMS 直接接入 Polaris，平滑过渡到现代 Catalog 架构（[HMS Federation 文档](https://polaris.apache.org/releases/1.5.0/federation/hive-metastore-federation/)）
- **AI-Native 元数据**：与 Apache Lance 的多模态存储集成（2026-01 已发布），让 Polaris 同时管理 Iceberg 表和 Lance 表（向量 + 多模态）
- **更细粒度的 RBAC**：行级 / 列级权限策略，配合 Iceberg view 用于数据共享场景，支持外部 OPA Policy Decision Point

**1.5.0 与 Iceberg V4 协同**：1.5.0 是 V4 spec 落地的 catalog 端铺垫，催化 catalog-managed metadata 成为可选模式。

来源：[Apache Polaris 1.5.0 Deep-Dive (Dremio)](https://www.dremio.com/blog/apache-polaris-1-5-0-deep-dive-into-the-future-of-open-data-catalogs/)、[Apache Polaris and Lance — AI-Native Storage](https://polaris.incubator.apache.org/blog/2026/01/06/apache-polaris-and-lance-bringing-ai-native-storage-to-the-open-multimodal-lakehouse/)、[Polaris 在 2026-02-15 从 Apache 孵化器毕业为 TLP](https://incubator.apache.org/projects/polaris.html)

> 更新于 2026-07-09

## 16. Delta Lake 4.3.0 与 Iceberg 1.11.0 对齐（2026-06）

| 项目 | 版本 | 关键变化 |
| ---- | ---- | -------- |
| **Apache Iceberg** | **1.11.0**（2026-05-19） | Server-side scan planning、内置表加密、默认构建目标 Spark 4.1 / Flink 2.1 |
| **Delta Lake** | **4.3.0**（2026-06-18） | UniForm Iceberg 转换**原子化 + 增量**；IcebergCompatV3 实验性支持 Deletion Vectors 共存 |

**架构影响**：

- Delta UniForm 大提交可在同一 Delta 事务内原子生成 Iceberg 元数据，消除 bulk-commit 一致性窗口
- UniForm 构建于 Iceberg-spark **1.11.0**，同时支持 Spark 4.0 / 4.1
- Unity Catalog Delta APIs：catalog-managed 表成为 streaming、CDF、UniForm 的统一目标
- Databricks Iceberg v3 GA：deletion vectors、row tracking、VARIANT 类型跨 managed/foreign/UniForm 表

**选型更新**：跨引擎读 Delta 且已有 Iceberg 客户端 → 优先评估 Delta 4.3 UniForm；PB 级开放湖仓 + 多引擎 → Iceberg 1.11 + Polaris 1.5 联邦。

> 来源：[Iceberg 1.11.0 发布公告](https://opensource.googleblog.com/2026/05/announcing-apache-iceberg-1110.html)、[Delta 4.3.0 Release](https://github.com/delta-io/delta/releases/tag/v4.3.0)、[Delta 4.3 博客](https://delta.io/blog/2026-06-22-delta-4-3-release/)、[Databricks Iceberg v3 GA](https://www.databricks.com/blog/unity-catalog-and-next-era-apache-icebergtm)
