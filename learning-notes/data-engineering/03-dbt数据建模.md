# dbt 数据建模

> Author: Walter Wang

<!-- version-check: dbt-core 1.10, dbt Fusion 2.x GA on Snowflake, SQLMesh 0.170, checked 2026-05-16 -->

## 1. 为什么 dbt

dbt（data build tool）把"数据转换"变成软件工程：**SQL 文件 + Git + 测试 + 文档 + CI**，2026 年数据建模的事实标准。

```
┌──────── 传统 vs dbt ────────┐
│                              │
│  传统 ETL：                    │
│  ├─ GUI 拖拽（Informatica）     │
│  ├─ 逻辑难版本化                │
│  ├─ 本地跑不起来                │
│  └─ 改动风险大                  │
│                              │
│  dbt：                         │
│  ├─ SQL + YAML                │
│  ├─ Git 工作流                 │
│  ├─ 本地 dbt run 秒级          │
│  ├─ 内置测试和文档              │
│  └─ 依赖自动推导                │
└──────────────────────────────┘
```

## 2. 安装与初始化

```bash
# dbt-core + 对应数据库适配器
pip install dbt-postgres      # Postgres
pip install dbt-snowflake     # Snowflake
pip install dbt-bigquery      # BigQuery
pip install dbt-duckdb        # DuckDB（本地开发推荐）

# 初始化项目
dbt init my_project
```

项目结构：

```
my_project/
├── dbt_project.yml       # 项目配置
├── profiles.yml          # 数据库连接（通常在 ~/.dbt/）
├── models/
│   ├── staging/          # 对应源表的清洗（bronze→silver）
│   ├── intermediate/     # 业务逻辑中间层
│   └── marts/            # 聚合层（silver→gold）
│       ├── core/
│       └── marketing/
├── tests/                # 自定义测试
├── macros/               # 可复用 SQL 函数
├── seeds/                # CSV 作为数据源
├── snapshots/            # SCD Type 2
└── analyses/             # 探索性查询
```

## 3. 模型（Model）

一个模型 = 一个 `.sql` 文件 = 一个表或视图。

```sql
-- models/staging/stg_orders.sql
{{ config(materialized='view') }}

SELECT
    id AS order_id,
    user_id,
    amount / 100.0 AS amount_dollars,
    status,
    CAST(created_at AS TIMESTAMPTZ) AS created_at
FROM {{ source('raw', 'orders') }}
WHERE deleted_at IS NULL
```

```sql
-- models/marts/core/fct_orders.sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    on_schema_change='fail'
) }}

SELECT
    o.order_id,
    o.user_id,
    u.email,
    o.amount_dollars,
    o.status,
    o.created_at
FROM {{ ref('stg_orders') }} o
LEFT JOIN {{ ref('dim_users') }} u ON u.user_id = o.user_id

{% if is_incremental() %}
  WHERE o.created_at > (SELECT MAX(created_at) FROM {{ this }})
{% endif %}
```

**四种物化方式**：

| materialized | 行为 | 场景 |
|--------------|------|------|
| `view` | 每次查询时计算 | 轻量中间层 |
| `table` | 每次全量重建 | 小表、复杂逻辑 |
| `incremental` | 只追加新数据 | 大表、事实表 |
| `ephemeral` | 不落地，作为 CTE 内联 | 频繁复用的中间结果 |

## 4. Source（数据源）

```yaml
# models/staging/sources.yml
version: 2

sources:
  - name: raw
    database: mydb
    schema: raw
    tables:
      - name: orders
        loaded_at_field: _loaded_at
        freshness:
          warn_after: {count: 12, period: hour}
          error_after: {count: 24, period: hour}
        columns:
          - name: id
            tests: [unique, not_null]
          - name: user_id
            tests: [not_null]
```

在 SQL 中引用：`{{ source('raw', 'orders') }}`。

dbt 会检查：
- 数据新鲜度（freshness）
- 测试在 CI 里自动跑
- 血缘关系（谁用了 raw.orders）

## 5. 测试

### 5.1 内置通用测试

```yaml
# models/staging/schema.yml
version: 2

models:
  - name: stg_orders
    description: "清洗后的订单数据"
    columns:
      - name: order_id
        description: "订单唯一标识"
        tests:
          - unique
          - not_null
      - name: user_id
        tests:
          - not_null
          - relationships:
              to: ref('stg_users')
              field: user_id
      - name: status
        tests:
          - accepted_values:
              values: [pending, paid, cancelled]
      - name: amount_dollars
        tests:
          - dbt_utils.expression_is_true:
              expression: ">= 0"
```

### 5.2 自定义测试

```sql
-- tests/assert_total_sales_non_negative.sql
SELECT *
FROM {{ ref('fct_orders') }}
GROUP BY date_trunc('day', created_at)
HAVING SUM(amount_dollars) < 0
-- 测试失败条件：存在一天总销售为负
```

### 5.3 Singular vs Generic

```sql
-- 通用测试 macro
-- tests/generic/test_not_negative.sql
{% test not_negative(model, column_name) %}
    SELECT * FROM {{ model }} WHERE {{ column_name }} < 0
{% endtest %}
```

```yaml
models:
  - name: fct_orders
    columns:
      - name: amount_dollars
        tests:
          - not_negative
```

## 6. Jinja 与 Macros

```sql
-- macros/cents_to_dollars.sql
{% macro cents_to_dollars(column_name) %}
    ({{ column_name }} / 100.0)
{% endmacro %}

-- 使用
SELECT
    order_id,
    {{ cents_to_dollars('amount_cents') }} AS amount_dollars
FROM {{ ref('stg_orders') }}
```

### 6.1 变量注入

```yaml
# dbt_project.yml
vars:
  start_date: '2026-01-01'
```

```sql
SELECT * FROM {{ ref('fct_orders') }}
WHERE created_at >= '{{ var("start_date") }}'
```

```bash
# 命令行覆盖
dbt run --vars '{start_date: 2026-05-01}'
```

## 7. 增量模型策略

```sql
{{ config(
    materialized='incremental',
    unique_key='order_id',
    incremental_strategy='merge',  -- merge / delete+insert / append
    on_schema_change='sync_all_columns'
) }}

SELECT ...
FROM {{ source('raw', 'orders') }}

{% if is_incremental() %}
  WHERE updated_at > (SELECT MAX(updated_at) FROM {{ this }})
{% endif %}
```

**三种策略**：

| 策略 | 说明 | 适用 |
|------|------|------|
| `merge` | 按 unique_key upsert | Postgres/Snowflake/BigQuery |
| `delete+insert` | 按 key 删除再插入 | 多数数据库 |
| `append` | 只追加 | 日志类数据 |

## 8. 部署与调度

```bash
# 本地开发
dbt run                  # 运行所有模型
dbt run --select staging # 只运行 staging 层
dbt run --select +fct_orders  # 运行 fct_orders 及其所有依赖
dbt run --select stg_orders+  # 运行 stg_orders 及所有下游

# 测试
dbt test
dbt test --select stg_orders

# 生成文档
dbt docs generate
dbt docs serve           # 本地查看血缘图

# 刷新源的新鲜度
dbt source freshness

# CI 中
dbt build --select state:modified+ --defer --state ./target_main
```

**调度工具**：
- dbt Cloud（托管）
- Airflow + `dbt-airflow`
- Dagster（原生 dbt asset 集成）
- GitHub Actions + cron

## 9. 血缘 + 文档

```bash
dbt docs generate  # 生成 target/manifest.json, catalog.json
dbt docs serve     # 启动本地服务
```

自动生成的文档包含：
- 所有模型的 SQL 和说明
- 字段级血缘图（上游、下游）
- 测试结果
- 新鲜度状态

2026 年推荐集成到 **DataHub / OpenMetadata** 做中心化数据目录。

## 10. Snapshots：SCD Type 2

记录维度表的历史变化：

```sql
-- snapshots/users_snapshot.sql
{% snapshot users_snapshot %}

{{
    config(
        target_schema='snapshots',
        unique_key='user_id',
        strategy='timestamp',
        updated_at='updated_at'
    )
}}

SELECT * FROM {{ source('raw', 'users') }}

{% endsnapshot %}
```

dbt 自动维护 `dbt_valid_from` / `dbt_valid_to` 字段，让你可以查询历史任意时点的数据。

## 11. Semantic Layer

dbt Semantic Layer（基于 MetricFlow）把"指标定义"独立出来：

```yaml
# models/marts/metrics.yml
version: 2

metrics:
  - name: total_revenue
    type: simple
    type_params:
      measure: revenue
    description: "总收入（美元）"

semantic_models:
  - name: orders
    defaults:
      agg_time_dimension: created_at
    entities:
      - name: order
        type: primary
        expr: order_id
      - name: user
        type: foreign
        expr: user_id
    measures:
      - name: revenue
        agg: sum
        expr: amount_dollars
    dimensions:
      - name: created_at
        type: time
      - name: status
        type: categorical
```

价值：BI 工具 / AI Agent 查询"total_revenue by status"会得到一致结果，不会因为谁写 SQL 不同而有偏差。

## 12. 2026 年趋势：dbt Fusion（Rust 引擎）

dbt Labs 正在推出基于 Rust 的新引擎 **dbt Fusion**（前代号 dbt-cloud-fusion）：

- 解析速度 10-100x
- 本地 SQL type-check（不用连数据库就能校验）
- 更好的 LSP（IDE 提示）
- 兼容现有 dbt-core 项目

**SQLMesh** 是强力的竞争者（同样 Rust 风格性能 + 更强的 incremental 语义）。2026 年两者并存。

### 12.1 dbt Fusion GA（2026 Q2 更新）

> 🔄 更新于 2026-05-16

dbt Fusion 已经在 dbt platform 上对 **Snowflake 用户全面可用（GA）**，其他适配器仍处于 preview 状态。来源：[dbt Fusion Availability](https://docs.getdbt.com/docs/fusion/fusion-availability)、[Fusion Releases](https://docs.getdbt.com/docs/fusion/fusion-releases)

**版本号变化**：dbt Fusion 引擎采用语义化版本，从 **2.0** 开始（区别于 dbt-core 1.x）。来源：[About dbt versions](https://docs.getdbt.com/docs/dbt-versions)

**何处可用 Fusion**：

| 场景 | 状态 |
|------|------|
| dbt Studio IDE（Snowflake） | GA |
| VS Code / Cursor / Windsurf 扩展 | GA |
| 本地 dbt 命令行（Snowflake） | GA |
| 其他适配器（Postgres、BigQuery、Databricks 等） | Preview |
| dbt Canvas 可视化建模 | GA |

**Copilot 与 Developer Agent**：

dbt Studio IDE 现在原生集成 Copilot 和 Developer Agent，AI 自动补全、模型生成、测试建议。Studio Commands 标签会用 🤖 图标区分 Agent 运行的命令和手动运行的命令。来源：[dbt Release Notes](https://docs.getdbt.com/docs/dbt-versions/release-notes/Jan-2024/partial-parsing)

**升级路径（dbt-core 1.x → Fusion 2.x）**：

```bash
# 1. 检查项目兼容性
dbt fusion validate

# 2. 在 Studio IDE 启用 Fusion（新建项目默认启用）
# Settings → Engine → dbt Fusion 2.x

# 3. 本地切换 VS Code 扩展（推荐）
# 安装 dbt VS Code Extension，自动使用 Fusion 引擎

# 4. CI/CD 中切换
# 从 `dbt-core` 改为 `dbt-fusion`，命令保持不变
```

非 Snowflake 用户当前仍应使用 dbt-core 1.10，等待 Fusion 在自己的适配器上 GA。Snowflake 用户可以放心切换。

## 13. 生产检查清单

```
☐ 分层清晰：staging / intermediate / marts
☐ 所有关键模型有 unique/not_null/relationships 测试
☐ Sources 有 freshness 检查
☐ 核心模型启用 contract
☐ 增量模型定期全量重建（每周）避免漂移
☐ 命名规范统一：stg_*、dim_*、fct_*、agg_*
☐ CI：dbt build + dbt test + dbt source freshness
☐ 生产跑 dbt 有监控（Airflow / Dagster + 告警）
☐ 数据血缘在 DataHub / OpenMetadata 中心化
☐ Semantic Layer 定义关键指标
```

## 📖 参考资料

- [dbt 官方文档](https://docs.getdbt.com/)
- [dbt Style Guide](https://docs.getdbt.com/best-practices/how-we-style/0-how-we-style-our-dbt-projects)
- [dbt-utils](https://github.com/dbt-labs/dbt-utils)
- [SQLMesh](https://sqlmesh.com/)
- [Analytics Engineering Roadmap](https://www.getdbt.com/analytics-engineering/)
