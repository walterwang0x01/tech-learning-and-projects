# PostgreSQL 基础

> Author: Walter Wang

<!-- version-check: PostgreSQL 18.4 (2026-05-14 security release, 11 CVE fixes), checked 2026-05-16 -->

## 1. 为什么是 PostgreSQL

```
2026 年 PG 在开源关系型领域的统治地位：
├─ Stack Overflow 开发者调查连续 3 年"最想使用 DB"第一
├─ GitHub 新项目 PG > MySQL（交叉点发生在 2023）
├─ 云厂商 RDS/Aurora/CloudSQL/AlloyDB 深度优化
├─ 扩展生态最丰富（pgvector、TimescaleDB、PostGIS、pg_cron）
└─ AI Agent 记忆层的默认后端
```

## 2. 核心架构

```
┌──────── PG 进程模型 ────────┐
│                              │
│  postmaster（主进程）          │
│    ├─ 监听连接                 │
│    └─ fork 子进程处理每个连接   │
│                              │
│  后台进程：                    │
│  ├─ wal writer（WAL 写入）     │
│  ├─ background writer（脏页刷盘）│
│  ├─ autovacuum launcher        │
│  ├─ checkpointer              │
│  └─ archiver（WAL 归档）       │
│                              │
│  共享内存：                     │
│  └─ shared_buffers            │
└──────────────────────────────┘
```

**关键设计**：PG 是 process-per-connection（每连接一个进程），所以连接数超过 100-200 要用连接池（见 [03-PostgreSQL性能优化.md](./03-PostgreSQL性能优化.md)）。

## 3. 数据类型速查

```sql
-- 数值
INTEGER / INT        4 字节
BIGINT / INT8        8 字节
NUMERIC(p, s)        精确数值（金额推荐）
REAL                 4 字节浮点
DOUBLE PRECISION     8 字节浮点

-- 字符串
TEXT                 可变长（推荐，无性能差异）
VARCHAR(n)           限长
CHAR(n)              定长（很少用）

-- 日期时间
DATE                 日期
TIME                 时间
TIMESTAMP            时间戳（无时区）
TIMESTAMPTZ          带时区（推荐！）
INTERVAL             时间间隔

-- 布尔、UUID
BOOLEAN
UUID                 uuid 类型

-- 二进制
BYTEA

-- 富类型
JSON / JSONB         JSONB 推荐（二进制、索引友好）
ARRAY                原生数组：INTEGER[]
HSTORE               Key-Value（被 JSONB 替代）
ENUM                 自定义枚举

-- 范围类型
INT4RANGE, TSRANGE, TSTZRANGE

-- 几何（PostGIS 扩展）
GEOMETRY, GEOGRAPHY
```

**黄金法则**：
- 时间戳一律用 `TIMESTAMPTZ`，永远不要用 `TIMESTAMP`
- 金额用 `NUMERIC(18, 4)`，不要 FLOAT
- 字符串一律用 `TEXT`，不要 VARCHAR(n)（除非真的要限长）
- JSON 一律用 `JSONB`，不用 `JSON`

## 4. DDL 基础

```sql
-- 建表
CREATE TABLE users (
    id BIGSERIAL PRIMARY KEY,                    -- 自增（传统）
    -- 或 PG 18+
    -- id UUID DEFAULT uuidv7() PRIMARY KEY,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    age INTEGER CHECK (age >= 0),
    status TEXT NOT NULL DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 索引
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
CREATE INDEX idx_users_tags ON users USING GIN(tags);
CREATE INDEX idx_users_metadata ON users USING GIN(metadata);

-- 外键
CREATE TABLE orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    amount NUMERIC(18, 2) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- 视图
CREATE VIEW active_users AS
SELECT * FROM users WHERE status = 'active';

-- 物化视图（缓存查询结果）
CREATE MATERIALIZED VIEW daily_stats AS
SELECT DATE(created_at) AS day, COUNT(*) AS n
FROM orders
GROUP BY DATE(created_at);

REFRESH MATERIALIZED VIEW daily_stats;  -- 手动刷新
REFRESH MATERIALIZED VIEW CONCURRENTLY daily_stats;  -- 不阻塞读
```

## 5. 事务

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
-- 出错 ROLLBACK
```

### 隔离级别

```
READ COMMITTED（默认）
  ├─ 看不到未提交的数据
  └─ 但同一事务两次查询结果可能不同（不可重复读）

REPEATABLE READ
  ├─ 同一事务内数据快照一致
  └─ PG 的 RR 不允许幻读（比标准严格）

SERIALIZABLE
  ├─ 完全可串行化
  └─ 最严格，性能代价最大
```

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
-- ...
COMMIT;
```

### 悲观锁 vs 乐观锁

```sql
-- 悲观锁
SELECT * FROM orders WHERE id = 1 FOR UPDATE;
UPDATE orders SET status = 'paid' WHERE id = 1;

-- 乐观锁（版本号）
UPDATE orders SET status = 'paid', version = version + 1
WHERE id = 1 AND version = $expected_version;
-- 影响行数 = 0 → 冲突
```

## 6. 常用语句

### 6.1 UPSERT

```sql
INSERT INTO user_scores (user_id, score)
VALUES (1, 100)
ON CONFLICT (user_id)
DO UPDATE SET score = user_scores.score + EXCLUDED.score;
```

### 6.2 RETURNING

```sql
-- INSERT 同时拿到新行
INSERT INTO users (name, email) VALUES ('Alice', 'a@x.com')
RETURNING id, created_at;

-- UPDATE 拿到改之前/之后（PG 18+）
UPDATE orders SET status = 'paid' WHERE id = 1
RETURNING OLD.status AS old_status, NEW.status AS new_status;
```

### 6.3 CTE

```sql
WITH recent AS (
    SELECT * FROM orders WHERE created_at > NOW() - INTERVAL '7 days'
)
SELECT user_id, COUNT(*), SUM(amount)
FROM recent
GROUP BY user_id;
```

### 6.4 DISTINCT ON

```sql
-- 每个用户的最新订单
SELECT DISTINCT ON (user_id) *
FROM orders
ORDER BY user_id, created_at DESC;
```

## 7. 权限管理

```sql
-- 建角色
CREATE ROLE app_user WITH LOGIN PASSWORD 'xxx';
CREATE ROLE readonly NOINHERIT;

-- 授权
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO app_user;

-- 未来创建的表也自动授权
ALTER DEFAULT PRIVILEGES IN SCHEMA public
GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO app_user;

-- 只读用户
GRANT SELECT ON ALL TABLES IN SCHEMA public TO readonly;
```

**生产原则**：
- 应用用户不要 `SUPERUSER`
- 每个应用独立 role
- 分开 read-only 和 read-write 角色

## 8. psql 常用命令

```bash
psql -h host -U user -d db

# 元命令（以 \ 开头）
\l              # 列出数据库
\c dbname       # 切换数据库
\dt             # 列出表
\dt+            # 表详细信息（大小等）
\d table        # 表结构
\di             # 列出索引
\du             # 列出角色
\conninfo       # 当前连接
\timing         # 开启执行时间显示
\x              # 切换扩展显示（长行友好）
\! ls           # 执行 shell 命令
\i script.sql   # 执行 SQL 文件
\copy t FROM 'f.csv' CSV HEADER   # 导入
```

## 9. 备份与恢复

```bash
# 逻辑备份
pg_dump mydb > mydb.sql
pg_dump -Fc mydb > mydb.dump   # 压缩格式（推荐）
pg_dump -Fc -j 4 mydb > mydb.dump  # 并行导出

# 恢复
psql mydb < mydb.sql
pg_restore -d mydb mydb.dump
pg_restore -d mydb -j 4 mydb.dump   # 并行导入

# 只导特定表
pg_dump -t users -t orders mydb > subset.sql

# 物理备份（更快，大表必用）
pg_basebackup -D /backup -Ft -z -P
```

生产推荐：
- **pgBackRest**（开源，功能最全）
- **WAL-G**（增量，云存储友好）
- 云厂商托管备份（AWS RDS、Neon 等）

## 10. 高可用与复制

```
2026 年主流方案：
├─ 流复制（内置）：物理复制
├─ 逻辑复制（内置）：细粒度、跨版本
├─ Patroni：主动故障转移（Kubernetes 常用）
├─ pg_auto_failover
├─ CloudNativePG（K8s Operator）
└─ 云托管：Aurora、Cloud SQL、Neon
```

简单流复制配置：

```ini
# postgresql.conf（主）
wal_level = replica
max_wal_senders = 10
wal_keep_size = 1GB
archive_mode = on
archive_command = 'cp %p /archive/%f'

# pg_hba.conf
host replication replicator 10.0.0.0/8 md5
```

```bash
# 备机
pg_basebackup -h primary -D /var/lib/postgresql/data -U replicator -P -R
```

## 11. 常见反模式

```
❌ 用 CHAR/VARCHAR(n) 而不是 TEXT
   → TEXT 没性能差，少痛苦

❌ 主键用 String（如 email）
   → 索引 bloat 严重，改 BIGSERIAL 或 UUIDv7

❌ 每张表都 ADD 一堆索引
   → 写放大大，VACUUM 慢

❌ SELECT * 到处用
   → 带宽浪费，Covering Index 失效

❌ OFFSET 做大页分页
   → O(N) 扫描，改 keyset 分页

❌ 不用 EXPLAIN
   → 慢查询靠猜

❌ 应用直接连不用连接池
   → PG 连接昂贵

❌ DELETE FROM big_table WHERE condition
   → 可能锁很久，WAL 爆
   → 分批 DELETE

❌ 不用事务包批量操作
   → 失败没法回滚

❌ 用 float 存金额
   → 精度丢失，用 NUMERIC
```

## 12. 快速学习路径

```
新人 7 天路径：
Day 1：基础 SQL + DDL
Day 2：事务、隔离级别、锁
Day 3：索引（B-tree / GIN / BRIN）+ EXPLAIN
Day 4：JSONB + 数组 + 窗口函数
Day 5：性能优化（见 03）
Day 6：扩展生态（pgvector、TimescaleDB）
Day 7：高可用、备份、运维
```

## 📖 参考资料

- [PostgreSQL 官方中文文档](http://www.postgres.cn/docs/)
- [Art of PostgreSQL](https://theartofpostgresql.com/)
- [Crunchy Data Blog](https://www.crunchydata.com/blog)
- [Neon Blog](https://neon.tech/blog)
- [Use The Index, Luke!](https://use-the-index-luke.com/)
