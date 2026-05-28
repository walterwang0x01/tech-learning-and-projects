# SQL 进阶

> Author: Walter Wang

<!-- version-check: SQL:2023 standard, PostgreSQL 18.4, checked 2026-05-28 -->

## 1. 窗口函数全解

窗口函数是 SQL 进阶的分水岭。**能用窗口函数解决的问题，就不要用子查询或应用层循环**。

```sql
SELECT
    user_id,
    amount,
    created_at,
    -- 行号
    ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY created_at) AS seq,
    -- 排名（相同值相同排名，跳号）
    RANK() OVER (ORDER BY amount DESC) AS rank,
    -- 密集排名（相同值相同排名，不跳号）
    DENSE_RANK() OVER (ORDER BY amount DESC) AS dense_rank,
    -- 分桶
    NTILE(4) OVER (ORDER BY amount) AS quartile,
    -- 前值 / 后值
    LAG(amount, 1) OVER (PARTITION BY user_id ORDER BY created_at) AS prev_amount,
    LEAD(amount, 1) OVER (PARTITION BY user_id ORDER BY created_at) AS next_amount,
    -- 首值 / 末值
    FIRST_VALUE(amount) OVER (PARTITION BY user_id ORDER BY created_at) AS first_amount,
    LAST_VALUE(amount) OVER (
        PARTITION BY user_id ORDER BY created_at
        ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
    ) AS last_amount,
    -- 累计
    SUM(amount) OVER (
        PARTITION BY user_id ORDER BY created_at
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) AS cumulative_sum,
    -- 移动平均
    AVG(amount) OVER (
        PARTITION BY user_id ORDER BY created_at
        ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
    ) AS moving_avg_7d
FROM orders;
```

## 2. 窗口函数的实战

### 2.1 Top-N per group

```sql
-- 每个分类销量前 3
SELECT * FROM (
    SELECT *,
           ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY sales DESC) AS rn
    FROM products
) t
WHERE rn <= 3;
```

### 2.2 Gap and Island（连续区间）

```sql
-- 找连续登录 7 天的用户
WITH daily AS (
    SELECT DISTINCT user_id, login_date
    FROM logins
),
grouped AS (
    SELECT
        user_id,
        login_date,
        login_date - (ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY login_date))::INT AS grp
    FROM daily
)
SELECT user_id, MIN(login_date), MAX(login_date), COUNT(*) AS days
FROM grouped
GROUP BY user_id, grp
HAVING COUNT(*) >= 7;
```

### 2.3 去重保留最新

```sql
-- 每个用户保留最新一条记录
SELECT DISTINCT ON (user_id) *
FROM events
ORDER BY user_id, timestamp DESC;

-- 或用窗口函数（跨库兼容）
SELECT * FROM (
    SELECT *, ROW_NUMBER() OVER (PARTITION BY user_id ORDER BY timestamp DESC) AS rn
    FROM events
) t WHERE rn = 1;
```

## 3. CTE 与递归

```sql
-- 普通 CTE：让复杂查询可读
WITH
  new_users AS (
    SELECT id FROM users WHERE created_at > NOW() - INTERVAL '30 days'
  ),
  their_orders AS (
    SELECT * FROM orders WHERE user_id IN (SELECT id FROM new_users)
  )
SELECT AVG(amount) FROM their_orders;

-- 递归 CTE：文件系统、评论树、组织架构
WITH RECURSIVE subordinates AS (
    SELECT id, name, manager_id, 1 AS level
    FROM employees WHERE id = 1   -- 根节点

    UNION ALL

    SELECT e.id, e.name, e.manager_id, s.level + 1
    FROM employees e
    JOIN subordinates s ON e.manager_id = s.id
)
SELECT * FROM subordinates ORDER BY level;

-- 递归生成数据（比如填充日期序列）
WITH RECURSIVE dates AS (
    SELECT DATE '2026-01-01' AS d
    UNION ALL
    SELECT d + INTERVAL '1 day'
    FROM dates
    WHERE d < DATE '2026-12-31'
)
SELECT d FROM dates;
-- 或者在 PG 用 generate_series
SELECT generate_series('2026-01-01'::date, '2026-12-31'::date, '1 day');
```

## 4. LATERAL JOIN

LATERAL 让子查询能引用左边的表：

```sql
-- 每个用户的最近 3 个订单
SELECT u.id, u.name, o.order_id, o.amount
FROM users u
CROSS JOIN LATERAL (
    SELECT order_id, amount FROM orders
    WHERE user_id = u.id
    ORDER BY created_at DESC
    LIMIT 3
) o;

-- LEFT JOIN LATERAL：用户没订单也保留
SELECT u.id, u.name, o.total
FROM users u
LEFT JOIN LATERAL (
    SELECT SUM(amount) AS total FROM orders WHERE user_id = u.id
) o ON TRUE;
```

## 5. GROUPING SETS / ROLLUP / CUBE

多维聚合一次出结果：

```sql
-- 同时按 region、category、两者组合聚合
SELECT region, category, SUM(revenue)
FROM sales
GROUP BY GROUPING SETS (
    (region, category),
    (region),
    (category),
    ()                   -- 全部
);

-- ROLLUP：层级汇总
SELECT year, quarter, month, SUM(revenue)
FROM sales
GROUP BY ROLLUP(year, quarter, month);

-- CUBE：所有组合
SELECT a, b, c, SUM(x)
FROM t
GROUP BY CUBE(a, b, c);

-- GROUPING() 函数识别是哪一行
SELECT
    region,
    category,
    SUM(revenue),
    GROUPING(region) AS is_region_total,
    GROUPING(category) AS is_category_total
FROM sales
GROUP BY ROLLUP(region, category);
```

## 6. PIVOT / UNPIVOT（行列转换）

```sql
-- 行转列（Postgres 的 crosstab 或 CASE WHEN）
SELECT
    user_id,
    SUM(CASE WHEN event_type = 'click' THEN 1 ELSE 0 END) AS clicks,
    SUM(CASE WHEN event_type = 'view' THEN 1 ELSE 0 END) AS views,
    SUM(CASE WHEN event_type = 'purchase' THEN 1 ELSE 0 END) AS purchases
FROM events
GROUP BY user_id;

-- FILTER 语法（标准 SQL，PG 支持）
SELECT
    user_id,
    COUNT(*) FILTER (WHERE event_type = 'click') AS clicks,
    COUNT(*) FILTER (WHERE event_type = 'view') AS views,
    COUNT(*) FILTER (WHERE event_type = 'purchase') AS purchases
FROM events
GROUP BY user_id;

-- UNPIVOT（列转行）
SELECT user_id, 'clicks' AS metric, clicks AS value FROM report
UNION ALL
SELECT user_id, 'views', views FROM report
UNION ALL
SELECT user_id, 'purchases', purchases FROM report;
```

## 7. JSON 处理（PG）

```sql
-- 提取
SELECT
    data->>'name' AS name,                 -- 文本
    data->'address'->>'city' AS city,      -- 嵌套
    (data->>'age')::INT AS age,            -- 类型转换
    data #>> '{items, 0, name}' AS first_item_name
FROM users;

-- 过滤
SELECT * FROM events WHERE data @> '{"type": "login"}';
SELECT * FROM events WHERE data ? 'user_id';
SELECT * FROM events WHERE data -> 'tags' ?| array['vip', 'premium'];

-- 聚合构建
SELECT
    user_id,
    json_agg(order_data ORDER BY created_at) AS orders,
    json_object_agg(order_id, amount) AS order_map
FROM orders
GROUP BY user_id;

-- 展开
SELECT
    event_id,
    elem->>'name' AS item_name,
    (elem->>'qty')::INT AS qty
FROM events, jsonb_array_elements(data->'items') elem;

-- JSONPath（12+）
SELECT data @? '$.items[*] ? (@.price > 100)' FROM orders;
```

## 8. Upsert / Merge

```sql
-- Postgres
INSERT INTO counters (key, value)
VALUES ('visits', 1)
ON CONFLICT (key) DO UPDATE
SET value = counters.value + EXCLUDED.value;

-- SQL:2023 标准 MERGE（PG 15+、MySQL 8+、Oracle、SQL Server 都支持）
MERGE INTO counters AS target
USING (VALUES ('visits', 1), ('clicks', 1)) AS source(key, value)
ON target.key = source.key
WHEN MATCHED THEN
    UPDATE SET value = target.value + source.value
WHEN NOT MATCHED THEN
    INSERT (key, value) VALUES (source.key, source.value);
```

## 9. EXISTS / NOT EXISTS vs IN

```sql
-- ❌ 常见错误：NOT IN 遇 NULL 会怪异
SELECT * FROM users WHERE id NOT IN (SELECT user_id FROM orders);
-- 如果 orders.user_id 有 NULL，结果是空

-- ✅ 推荐：NOT EXISTS
SELECT * FROM users u
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.user_id = u.id);
```

## 10. 实用函数

```sql
-- 字符串
SELECT
    CONCAT('Hello, ', name) AS greeting,
    LENGTH(name) AS len,
    LOWER(email),
    REGEXP_MATCHES(text, '[0-9]+'),
    SPLIT_PART('a,b,c', ',', 2),   -- 'b'
    POSITION('@' IN email),
    SUBSTRING(text FROM 1 FOR 100);

-- 日期
SELECT
    DATE_TRUNC('hour', created_at),      -- 截到小时
    EXTRACT(DOW FROM created_at),        -- 周几
    AGE(NOW(), created_at),              -- 间隔
    created_at + INTERVAL '7 days';

-- 数组（PG）
SELECT
    ARRAY[1, 2, 3] AS arr,
    array_length(tags, 1),
    unnest(tags),
    tags || ARRAY['new_tag'],
    tags && ARRAY['vip'],                -- 是否有交集
    tags @> ARRAY['vip', 'premium'];     -- 是否包含

-- 分析
SELECT
    percentile_cont(0.5) WITHIN GROUP (ORDER BY duration) AS median,
    percentile_cont(ARRAY[0.5, 0.95, 0.99]) WITHIN GROUP (ORDER BY duration) AS p50_95_99,
    stddev(duration),
    corr(x, y);
```

## 11. 性能 + 可读性平衡

```
优化顺序：
1. 读懂 EXPLAIN，看到底慢在哪
2. 索引优先（90% 问题在这里）
3. 改写 SQL（分解、加 CTE、避免函数）
4. 改 Schema（反规范化、分区）
5. 物化视图（复杂报表）
6. 应用层缓存
7. 数据库参数（最后再考虑）
```

## 📖 参考资料

- [Modern SQL](https://modern-sql.com/)
- [PostgreSQL 文档 - SQL 语言](https://www.postgresql.org/docs/current/sql.html)
- [SQL 练习：PGExercises](https://pgexercises.com/)
- [Use The Index, Luke!](https://use-the-index-luke.com/)
