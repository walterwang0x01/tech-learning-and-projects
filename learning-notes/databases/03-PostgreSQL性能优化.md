# PostgreSQL 性能优化

> Author: Walter Wang

<!-- version-check: PostgreSQL 18.3, pg_stat_statements, checked 2026-05-10 -->

## 1. 优化的思维框架

```
按性价比排序：
1. 查询层：加对索引、改 SQL（80% 的问题在这里）
2. Schema：反规范化、分区、合适的数据类型
3. 参数：work_mem、shared_buffers、effective_cache_size
4. 硬件：SSD、内存、CPU（最后考虑）
```

## 2. 必装：pg_stat_statements

```sql
-- postgresql.conf
shared_preload_libraries = 'pg_stat_statements'

-- 启用
CREATE EXTENSION pg_stat_statements;

-- 找出最耗时的 SQL
SELECT
    substring(query, 1, 100) AS short_query,
    calls,
    total_exec_time::INT AS total_ms,
    (total_exec_time / calls)::INT AS avg_ms,
    rows / calls AS avg_rows,
    100.0 * shared_blks_hit / NULLIF(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;

-- 重置统计
SELECT pg_stat_statements_reset();
```

## 3. EXPLAIN 精读

```sql
EXPLAIN (ANALYZE, BUFFERS, VERBOSE, FORMAT TEXT)
SELECT o.id, u.name, SUM(o.amount)
FROM orders o
JOIN users u ON u.id = o.user_id
WHERE o.created_at > NOW() - INTERVAL '7 days'
GROUP BY o.id, u.name;
```

关键看：

```
Seq Scan vs Index Scan      → 是否走索引
Nested Loop vs Hash Join    → 数据量大应该是 Hash Join
Rows Removed by Filter: N   → Filter 筛掉太多？索引没覆盖
Rows: actual vs estimated   → 统计信息偏差大 → ANALYZE
Buffers: shared hit=N read=M → read 多意味着缓存命中率差
```

可视化工具：[explain.depesz.com](https://explain.depesz.com/)、[explain.dalibo.com](https://explain.dalibo.com/)。

## 4. 索引设计

### 4.1 索引类型

```sql
-- B-tree（默认）：等值、范围、排序
CREATE INDEX ON orders (user_id);
CREATE INDEX ON orders (status, created_at);  -- 组合索引，顺序很重要

-- Hash：只支持等值，较少用
CREATE INDEX ON users USING hash (email);

-- GIN：JSONB、数组、全文检索
CREATE INDEX ON events USING gin (data);

-- GiST：地理、范围类型、全文检索（小）
CREATE INDEX ON events USING gist (time_range);

-- BRIN：超大表的时间戳/自增 id（1 亿行占几十 KB）
CREATE INDEX ON logs USING brin (created_at);

-- Partial Index：只索引满足条件的行
CREATE INDEX ON orders (user_id) WHERE status = 'pending';

-- Covering Index (INCLUDE)：索引直接返回列，不用回表
CREATE INDEX ON orders (user_id) INCLUDE (amount, status);

-- Expression Index：表达式索引
CREATE INDEX ON users (lower(email));   -- 大小写不敏感查询
```

### 4.2 索引的代价

```
每个索引都有代价：
├─ 写放大：INSERT/UPDATE/DELETE 要同步更新索引
├─ 空间：大索引容易超过表本身
├─ VACUUM 负担：膨胀的索引需要定期 REINDEX
└─ Planner 开销：索引太多时 planner 选择慢

原则：
├─ 优先考虑多列组合索引而非多个单列索引
├─ 关注 WHERE、JOIN、ORDER BY 的列
├─ 低基数的列（status 只有 3 个值）单独做索引意义不大，除非加 partial
└─ 定期清理未使用的索引（见下）
```

### 4.3 找未使用的索引

```sql
SELECT
    schemaname,
    relname AS table_name,
    indexrelname AS index_name,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexrelname NOT LIKE '%_pkey'
ORDER BY pg_relation_size(indexrelid) DESC;
```

idx_scan = 0 的索引是浪费。

## 5. VACUUM 与 bloat

PG 的 MVCC 导致更新/删除留下"死元组"。VACUUM 清理它们。

```sql
-- 查看 bloat
SELECT
    schemaname || '.' || relname AS table,
    n_dead_tup,
    n_live_tup,
    round(n_dead_tup * 100.0 / NULLIF(n_live_tup + n_dead_tup, 0), 2) AS dead_pct
FROM pg_stat_user_tables
ORDER BY n_dead_tup DESC;

-- 手动 VACUUM
VACUUM (VERBOSE, ANALYZE) orders;

-- 重建表（比 VACUUM FULL 更优，不锁表）
-- pg_repack 扩展
SELECT pg_repack.repack_table('public.orders');
```

**autovacuum 调优**：

```ini
# 对写多表调整
autovacuum_vacuum_scale_factor = 0.05   # 默认 0.2，调小触发更频繁
autovacuum_analyze_scale_factor = 0.02
autovacuum_vacuum_cost_limit = 2000     # 默认 200，允许更激进
```

## 6. 连接池：PgBouncer

Postgres 每个连接约 10 MB 内存 + CPU 开销，500+ 并发连接就吃不消。

```
应用 (1000 并发)
    ↓
PgBouncer（轻量，几万连接不虚）
    ↓
PostgreSQL（25-100 实际连接）
```

```ini
# pgbouncer.ini
[databases]
mydb = host=localhost port=5432 dbname=mydb

[pgbouncer]
pool_mode = transaction     # transaction / session / statement
max_client_conn = 5000
default_pool_size = 25
reserve_pool_size = 5
```

**Transaction 池化**是最常用的模式：事务结束归还连接。注意：不能用 `SET LOCAL` 以外的会话状态。

## 7. 查询模式优化

### 7.1 Keyset 分页（比 OFFSET 快 N 倍）

```sql
-- ❌ 慢：OFFSET 1000000 要扫描 100 万行
SELECT * FROM orders ORDER BY id DESC OFFSET 1000000 LIMIT 20;

-- ✅ 快：keyset 分页
SELECT * FROM orders
WHERE id < :last_id_from_previous_page
ORDER BY id DESC
LIMIT 20;
```

### 7.2 批量操作

```sql
-- ❌ N 次 INSERT
INSERT INTO logs (level, msg) VALUES ('info', 'msg1');
INSERT INTO logs (level, msg) VALUES ('info', 'msg2');
...

-- ✅ 批量
INSERT INTO logs (level, msg) VALUES
    ('info', 'msg1'),
    ('info', 'msg2'),
    ('info', 'msg3');

-- ✅ 最快：COPY
COPY logs (level, msg) FROM STDIN;
info	msg1
info	msg2
\.
```

### 7.3 UPSERT

```sql
INSERT INTO user_visits (user_id, count)
VALUES (1, 1)
ON CONFLICT (user_id)
DO UPDATE SET count = user_visits.count + 1;
```

### 7.4 避免 SELECT *

```sql
-- 带宽浪费、Covering Index 失效
SELECT * FROM orders WHERE id = 1;

-- 只取需要的列
SELECT id, amount FROM orders WHERE id = 1;
```

## 8. 参数调优速查

```ini
# 内存：机器 16GB 为例
shared_buffers = 4GB              # 25%，PG 自己的缓冲池
effective_cache_size = 12GB       # 75%，告诉 planner 操作系统的缓存
work_mem = 16MB                   # 每个排序/Hash 的内存，不要太大
maintenance_work_mem = 1GB        # VACUUM/CREATE INDEX 用

# 写入
wal_buffers = 16MB
checkpoint_timeout = 15min
max_wal_size = 4GB
checkpoint_completion_target = 0.9  # 让 checkpoint 更平滑

# 并行
max_worker_processes = 8
max_parallel_workers = 8
max_parallel_workers_per_gather = 4

# 日志（生产强烈推荐）
log_min_duration_statement = 1000   # 记录 > 1s 的慢查询
log_lock_waits = on
log_checkpoints = on
```

## 9. 监控指标清单

```
必监控：
├─ 连接数 vs max_connections
├─ 缓存命中率 > 99%
├─ 复制延迟
├─ 磁盘空间
├─ 慢查询 (pg_stat_statements)
├─ 死锁数
├─ VACUUM 进度和队列
├─ 长事务（>5 分钟告警）
├─ WAL 生成速率
└─ pg_stat_activity 中 waiting 状态
```

推荐：`postgres_exporter` + Prometheus + Grafana（有现成 dashboard）。

## 10. 常见慢查询模式

```
模式 1：N+1
  循环里每次查一次
  → 改批量 IN (...) 或 JOIN

模式 2：没走索引
  SELECT * WHERE col1 = 'x' AND col2 > 1
  → 加组合索引 (col1, col2)

模式 3：函数使索引失效
  WHERE DATE(created_at) = '2026-05-10'
  → 改 WHERE created_at >= '2026-05-10' AND created_at < '2026-05-11'
  → 或建函数索引 CREATE INDEX ... ON ... (DATE(created_at))

模式 4：隐式类型转换
  WHERE user_id = '123'   -- user_id 是 INTEGER
  → 强制转换导致无法用索引，改 user_id = 123

模式 5：过多 JOIN
  10 张表 JOIN，planner 计算量爆炸
  → 切分为多个子查询，或先聚合再 JOIN

模式 6：OR 条件
  WHERE col1 = 'a' OR col2 = 'b'
  → 经常走不上索引，改 UNION ALL 分别查再合并
```

## 11. Async I/O（PG 18）带来的变化

PG 18 默认开启 `io_method=worker` 或 `io_uring`（Linux）。对顺序扫描和 VACUUM 影响最大：

```sql
-- 原来
SELECT COUNT(*) FROM huge_table;  -- I/O 受限，CPU 空闲

-- PG 18：多个异步 I/O 并发发出
-- 同样查询时间减少 40-60%
```

相关参数：

```ini
io_method = io_uring  # 或 worker / sync
effective_io_concurrency = 16   # SSD 可以设 100-200
maintenance_io_concurrency = 10
```

## 📖 参考资料

- [PostgreSQL Performance Tuning Guide](https://wiki.postgresql.org/wiki/Performance_Optimization)
- [Postgres Weekly](https://postgresweekly.com/)
- [pgMustard - EXPLAIN 可视化](https://www.pgmustard.com/)
- [pg_repack](https://reorg.github.io/pg_repack/)
- [Use The Index, Luke!](https://use-the-index-luke.com/)
