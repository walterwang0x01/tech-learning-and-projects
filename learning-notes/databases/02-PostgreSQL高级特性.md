# PostgreSQL 高级特性

> Author: Walter Wang

<!-- version-check: PostgreSQL 18.4 (2026-05-14, 11 CVE security release), async I/O, UUIDv7, virtual generated columns, OAuth 2.0, checked 2026-05-16 -->

## 1. PostgreSQL 18 亮点（2025-09 发布，2026-05 已到 18.4）

Postgres 18 是近年最重要的版本之一，带来了一批开发者/DBA 长期呼吁的特性。

### 1.1 Async I/O

Postgres 首次引入**异步 I/O 子系统**（使用 `io_uring` / POSIX AIO）：

```sql
-- 观察效果的核心参数
SHOW io_method;          -- worker / io_uring / sync
SHOW effective_io_concurrency;
SHOW maintenance_io_concurrency;
```

```
Sequential Scan、Bitmap Heap Scan、VACUUM 性能可提升 2-3 倍（NVMe 下）。
来源：https://postgresql.org/docs/current/release-18.html
```

### 1.2 UUIDv7

时间有序的 UUID（基于时间戳），主键友好：

```sql
-- 原来：随机 UUIDv4 作为主键会让 B-tree 随机插入，性能差
-- 现在：UUIDv7 天然时间有序
CREATE TABLE orders (
    id UUID DEFAULT uuidv7() PRIMARY KEY,
    ...
);

-- UUIDv7 还保留了 Unix 时间戳
SELECT uuid_extract_timestamp('018f4a1e-...');
```

### 1.3 Virtual Generated Columns（默认）

```sql
-- 18 之前：只有 STORED，实际占用存储
-- 18：默认 VIRTUAL，不占存储，查询时计算
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    price_cents INTEGER,
    tax_rate DECIMAL(5, 4),
    total_cents INTEGER GENERATED ALWAYS AS (price_cents * (1 + tax_rate)) VIRTUAL
);

SELECT id, total_cents FROM products;
```

### 1.4 Skip Scan（跳过扫描）

多列索引现在可以在**没有 leading 列过滤**时被使用：

```sql
CREATE INDEX idx_orders_status_created ON orders(status, created_at);

-- 18 之前：这个查询用不到上面的索引
SELECT * FROM orders WHERE created_at > NOW() - INTERVAL '1 day';

-- 18：planner 能自动"跳过"status 列，仍用上索引
```

### 1.5 OAuth 2.0 认证

```
pg_hba.conf 新增 oauth 认证方式
支持和企业 IdP（Keycloak、Okta、Azure AD）集成
```

### 1.6 Temporal Constraints

Primary Key 和 Unique 约束现在支持**时序有效性**：

```sql
-- 同一个 user_id 在不同时间段可以有不同 email
CREATE TABLE user_emails (
    user_id INTEGER,
    email TEXT,
    valid_period TSTZRANGE,
    PRIMARY KEY (user_id, valid_period WITHOUT OVERLAPS)
);
```

### 1.7 其他

- `ALTER TABLE ... ADD COLUMN NOT NULL` 无需全表扫描
- `RETURNING` 支持 `OLD.` / `NEW.` 别名
- `pg_upgrade` 升级速度大幅加快

### 1.8 PostgreSQL 18.4 重大安全更新（2026-05-14）

> 🔄 更新于 2026-05-16

PostgreSQL 18.4、17.10、16.14、15.18、14.23 同步发布——**修复 11 个 CVE 和 60+ bug**，是近年来单次发布安全修复最多的版本。来源：[PostgreSQL News](https://www.postgresql.org/about/news/postgresql-184-1710-1614-1518-and-1423-released-3297/)、[The Build Blog](https://thebuild.com/blog/2026/05/14/eleven-cves-walk-into-a-release/)

**关键漏洞类型**：

| 类型 | 影响 | 严重程度 |
|------|------|---------|
| 内存损坏 | 远程攻击者可触发崩溃或潜在 RCE | 3 个 CVSS 8.8 |
| SQL 注入（复制工具） | 通过 `pg_dump` / `pg_dumpall` 利用 | 高 |
| MD5 密码时序泄漏 | 时序侧信道攻击恢复密码哈希 | 高 |
| JSON 函数不变性回归 | 18.0-18.2 已建立的 JSON 索引可能损坏 | 中 |

**18.0 → 18.2 用户必须执行的额外步骤**：

```sql
-- 18.4 升级后必须重建依赖 json_strip_nulls / jsonb_strip_nulls 的索引
-- 因为之前版本错误地把这两个函数标为 STABLE 而非 IMMUTABLE
REINDEX INDEX CONCURRENTLY idx_using_json_strip_nulls;
```

**升级紧迫性**：

```
生产环境运行 18.0-18.3：立即升级（11 CVE，3 个 CVSS 8.8）
生产环境运行 17.x / 16.x / 15.x：按计划升级到对应安全版本
开发环境：升级到最新 minor，验证 JSON 索引完整性
```

**如何验证依赖 json_strip_nulls 的索引**：

```sql
-- 找出所有使用了 json_strip_nulls / jsonb_strip_nulls 的索引
SELECT
    indexrelid::regclass AS index_name,
    indrelid::regclass AS table_name
FROM pg_index
JOIN pg_class ON pg_class.oid = indexrelid
WHERE pg_get_indexdef(indexrelid) ~ 'json_strip_nulls|jsonb_strip_nulls';
```

来源：[PostgreSQL Out-of-cycle Release Feb 2026](https://www.postgresql.org/about/news/out-of-cycle-release-scheduled-for-february-26-2026-3241/)、[Releasebot PostgreSQL May 2026](https://releasebot.io/updates/postgresql)

## 2. JSONB：文档+关系的最佳结合

PG 的 JSONB 是 Mongo 的强力对手，但你还拥有完整的 SQL、事务、JOIN。

```sql
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    data JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 插入
INSERT INTO events (data) VALUES
  ('{"type": "login", "user_id": 1, "ip": "1.2.3.4"}'),
  ('{"type": "purchase", "user_id": 1, "amount": 99.9, "items": ["A", "B"]}');

-- 查询
SELECT * FROM events WHERE data->>'type' = 'login';
SELECT * FROM events WHERE data @> '{"user_id": 1}';
SELECT * FROM events WHERE data->'items' ? 'A';

-- 路径表达式
SELECT data #> '{items, 0}' FROM events;

-- JSONPath（12+）
SELECT data @? '$.items[*] ? (@ == "A")' FROM events;

-- 更新 JSONB 字段
UPDATE events SET data = jsonb_set(data, '{status}', '"done"') WHERE id = 1;
```

### 索引

```sql
-- GIN 索引：支持所有 JSONB 操作
CREATE INDEX idx_events_data ON events USING GIN (data);

-- 只索引特定字段（节省空间）
CREATE INDEX idx_events_type ON events ((data->>'type'));
CREATE INDEX idx_events_user ON events USING GIN ((data -> 'user_id'));

-- jsonb_path_ops：更小，只支持 @> 操作
CREATE INDEX idx_events_data_ops ON events USING GIN (data jsonb_path_ops);
```

## 3. CTE 与递归查询

```sql
-- Common Table Expression（简化复杂查询）
WITH recent_orders AS (
    SELECT * FROM orders WHERE created_at > NOW() - INTERVAL '7 days'
),
high_value AS (
    SELECT user_id, SUM(amount) AS total
    FROM recent_orders
    GROUP BY user_id
    HAVING SUM(amount) > 1000
)
SELECT u.name, hv.total
FROM high_value hv
JOIN users u ON u.id = hv.user_id
ORDER BY hv.total DESC;

-- 递归 CTE：层级查询（组织架构、评论树）
WITH RECURSIVE category_tree AS (
    SELECT id, name, parent_id, 1 AS depth, ARRAY[name] AS path
    FROM categories WHERE parent_id IS NULL

    UNION ALL

    SELECT c.id, c.name, c.parent_id, ct.depth + 1, ct.path || c.name
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT id, name, depth, array_to_string(path, ' > ') AS full_path
FROM category_tree
ORDER BY path;
```

## 4. 窗口函数

```sql
-- 为每个用户排序订单
SELECT
    user_id,
    order_id,
    amount,
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) AS seq,
    RANK() OVER (PARTITION BY user_id ORDER BY amount DESC) AS rank_by_amount,
    LAG(amount) OVER (PARTITION BY user_id ORDER BY created_at) AS prev_amount,
    SUM(amount) OVER (PARTITION BY user_id ORDER BY created_at
                      ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_sum
FROM orders;

-- 找到每个 category 销量前 3
SELECT * FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY sales DESC) AS rn
    FROM products
) t
WHERE rn <= 3;

-- 时间序列：7 日移动平均
SELECT
    date,
    revenue,
    AVG(revenue) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS moving_avg_7d
FROM daily_revenue;
```

## 5. LATERAL：行级子查询

```sql
-- 每个用户的最近 3 个订单（其他 DB 做这个要写存储过程）
SELECT u.name, o.*
FROM users u
CROSS JOIN LATERAL (
    SELECT * FROM orders
    WHERE user_id = u.id
    ORDER BY created_at DESC
    LIMIT 3
) o;
```

## 6. 分区表

海量时序数据/审计日志的标配：

```sql
-- 按月分区
CREATE TABLE events (
    id BIGSERIAL,
    user_id INTEGER,
    data JSONB,
    created_at TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE events_2026_05 PARTITION OF events
    FOR VALUES FROM ('2026-05-01') TO ('2026-06-01');

CREATE TABLE events_2026_06 PARTITION OF events
    FOR VALUES FROM ('2026-06-01') TO ('2026-07-01');

-- 自动化用 pg_partman 扩展
-- 老分区可以分离并归档到冷存储
ALTER TABLE events DETACH PARTITION events_2025_01;
```

## 7. 扩展生态

```
开发必装：
├─ pgcrypto          加密函数
├─ uuid-ossp         UUID 生成（18 开始可以不装，用内置 uuidv7）
├─ pg_trgm           文本相似度、模糊匹配
└─ citext            大小写不敏感文本类型

高级应用：
├─ pgvector          向量检索 → 见 04-pgvector与向量搜索.md
├─ TimescaleDB       时序数据库（超表、连续聚合）
├─ PostGIS           地理空间
├─ pg_cron           数据库内 cron 定时任务
├─ pg_partman        分区自动管理
├─ pglogical         逻辑复制
├─ pg_stat_statements 慢查询分析（必装）
└─ hypopg            虚拟索引（先试试再建）
```

## 8. LISTEN / NOTIFY：轻量消息

小规模场景下，不用 Kafka 也能有事件驱动：

```sql
-- 订阅
LISTEN orders_channel;

-- 发布
NOTIFY orders_channel, '{"id": 123, "status": "paid"}';

-- 触发器自动广播
CREATE OR REPLACE FUNCTION notify_order_change() RETURNS TRIGGER AS $$
BEGIN
    PERFORM pg_notify('orders_channel', row_to_json(NEW)::text);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER orders_notify
AFTER INSERT OR UPDATE ON orders
FOR EACH ROW EXECUTE FUNCTION notify_order_change();
```

客户端（比如 `node-postgres`、`pgx`）可以订阅这个 channel。

## 9. 逻辑复制：构建 CDC

```sql
-- 发布端
CREATE PUBLICATION my_pub FOR TABLE orders, users;

-- 订阅端
CREATE SUBSCRIPTION my_sub
    CONNECTION 'host=primary dbname=mydb user=replicator'
    PUBLICATION my_pub;
```

Debezium / Benthos / Redpanda Connect 都可以消费 PG 的 WAL，把变更事件推到 Kafka，实现 CDC。

## 10. Row-Level Security（RLS）

多租户场景下的强大工具：

```sql
-- 启用 RLS
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;

-- 策略：用户只能看到自己的订单
CREATE POLICY user_orders ON orders
    FOR SELECT
    USING (user_id = current_setting('app.user_id')::INTEGER);

-- 应用层设置 session 变量
SET app.user_id = '123';
SELECT * FROM orders;  -- 只返回 user_id=123 的行
```

Supabase 的核心就是用 RLS 实现"无后端"API。

## 11. 常见坑

```
生产反模式：
├─ EAV 模式滥用（用 JSONB 替代宽表）→ 索引难、查询慢
├─ SELECT * → 冗余字段浪费带宽
├─ 用 OFFSET 做大偏移分页 → 性能退化严重，改用 keyset 分页
├─ 不建 FK 以为能提性能 → 实际失去完整性保护
├─ 不用事务就批量写 → 失败难恢复
├─ 大事务不切片 → WAL 膨胀、锁持有时间过长
├─ 索引建太多 → 写操作放大，VACUUM 负担大
└─ 盲目加索引而不看 pg_stat_statements
```

## 📖 参考资料

- [PostgreSQL 18 Release Notes](https://www.postgresql.org/docs/release/18.0/)
- [Postgres 18 Features by Bytebase](https://www.bytebase.com/blog/what-is-new-in-postgres-18/)
- [Crunchy Data Blog](https://www.crunchydata.com/blog)
- [Supabase RLS 文档](https://supabase.com/docs/guides/database/postgres/row-level-security)
- [Use The Index, Luke!](https://use-the-index-luke.com/)
