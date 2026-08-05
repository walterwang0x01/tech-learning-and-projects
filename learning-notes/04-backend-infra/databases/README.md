# 数据库

> Author: Walter Wang

<!-- version-check: PostgreSQL 18.4, Redis 8.6, MongoDB 8.x, ClickHouse 26.6, pgvector 0.8.4, checked 2026-07-08 -->
<!-- 修复于 2026-07-08: README version-check 与正文文档版本线对齐（PG 18.4、ClickHouse 26.6、pgvector 0.8.4） -->

这个目录补齐 Java/Python 之外的数据库通用知识。PostgreSQL 在 2026 年已经是开源关系型的事实标准，向量、JSON、地理、时序、Agent 记忆都可以由它一站式支持。

## 📁 目录结构

```
databases/
├── 01-PostgreSQL基础.md          # 架构、数据类型、索引、事务
├── 02-PostgreSQL高级特性.md       # JSONB、CTE、窗口函数、分区、Async I/O
├── 03-PostgreSQL性能优化.md       # EXPLAIN、VACUUM、参数调优
├── 04-pgvector与向量搜索.md        # AI 时代的 RAG 基础设施
├── 05-PostgreSQL运维.md           # 复制、备份、升级、监控
├── 06-ClickHouse分析数据库.md     # OLAP 新王，日志/可观测/分析
├── 07-数据库选型指南.md            # 关系/KV/时序/图/向量/OLAP
└── 08-SQL进阶.md                  # 窗口函数、递归 CTE、LATERAL
```

## 🎯 为什么要独立成册

- **Postgres 爆炸式增长**：Stack Overflow 2024/2025 开发者调查中，PG 超过 MySQL 成为最想使用的数据库
- **一个 PG 解决 N 个问题**：pgvector（向量）、TimescaleDB（时序）、PostGIS（地理）、pg_cron（定时）、logical replication（CDC）
- **AI Agent 记忆**：Mem0、Letta、Zep 的默认后端都是 PG + 向量扩展

## 🔗 关联内容

- **MySQL 深入** → [java/07-数据库/](../../01-languages/java/07-数据库/)
- **Python ORM** → [python/07-数据库操作/](../python/07-数据库操作/)
- **向量检索架构** → [ai-agent/06-RAG进阶/02-向量数据库选型.md](../../00-ai/04-ai-agent/06-RAG进阶/02-向量数据库选型.md)
- **事件溯源** → [architecture/04-CQRS与事件溯源.md](../architecture/04-CQRS与事件溯源.md)

## 📚 权威参考

- [PostgreSQL 官方文档](https://www.postgresql.org/docs/current/)
- [Use The Index, Luke!](https://use-the-index-luke.com/)
- [ClickHouse 官方](https://clickhouse.com/docs)
- [PostgreSQL Weekly](https://postgresweekly.com/)
