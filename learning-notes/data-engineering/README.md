# 数据工程

> Author: Walter Wang

<!-- version-check: Airflow 3.3, dbt 1.11, Iceberg 1.11, Debezium 3.6.0.Final, Flink 2.3, checked 2026-07-08 -->
<!-- 修复于 2026-07-08: dbt 1.10 已 EOS，更新为 1.11 -->

数据工程连接事件驱动架构和数据分析，是 AI Agent 时代"数据供给"的关键环节。

## 📁 目录结构

```
data-engineering/
├── 01-现代数据栈概览.md           # Lakehouse、ELT、Data Mesh、Data Contract
├── 02-Airflow与Dagster编排.md    # 调度、DAG、Asset-first
├── 03-dbt数据建模.md              # SQL-first 转换、测试、文档
├── 04-Iceberg-Delta-Hudi对比.md  # Lakehouse 表格式
├── 05-CDC与Debezium.md           # 变更数据捕获、实时同步
├── 06-Flink与流式处理.md           # 实时计算、物化视图
└── 07-数据质量与契约.md            # Great Expectations、Soda、Data Contract
```

## 🎯 核心转变

```
过去（2010s）：
  传统数据仓库（Teradata、Oracle）
  ETL：先转换再加载
  Schema On Write
  批处理为主

现代（2020s）：
  Lakehouse（Snowflake / Databricks / 自建 Iceberg）
  ELT：先加载再转换（SQL / dbt）
  Schema On Read + Schema Evolution
  流批一体
  Data Contract 显式化上下游依赖
```

## 🔗 关联内容

- **事件驱动架构** → [architecture/01-事件驱动架构.md](../architecture/01-事件驱动架构.md)
- **Python 数据分析** → [python/02-数据分析/](../python/02-数据分析/)
- **ClickHouse OLAP** → [databases/06-ClickHouse分析数据库.md](../databases/06-ClickHouse分析数据库.md)
- **可观测性** → [observability-sre/](../observability-sre/)

## 📚 权威参考

- [Designing Data-Intensive Applications (DDIA)](https://dataintensive.net/)
- [Apache Iceberg 文档](https://iceberg.apache.org/)
- [dbt 官方](https://www.getdbt.com/)
- [Data Engineering Weekly](https://www.dataengineeringweekly.com/)
