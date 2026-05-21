# 数据分析 Agent
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 系统架构

```
┌─────────────────────────────────────────────────────┐
│                 数据分析 Agent                        │
├──────────┬──────────┬──────────┬───────────────────┤
│ NL→SQL   │ 数据可视化│ 报告生成  │ 异常检测          │
├──────────┼──────────┼──────────┼───────────────────┤
│ 自然语言  │ 图表生成  │ Markdown │ 统计分析          │
│ →SQL转换 │ 趋势分析  │ PDF导出  │ 阈值告警          │
└──────────┴──────────┴──────────┴───────────────────┘
         ↕ 多数据源（MySQL/PG/CSV/API）↕
```

## 2. NL→SQL 转换

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-5.2", temperature=0)

# 获取数据库 Schema 作为上下文
DB_SCHEMA = """
表：orders (id, user_id, product_id, amount, status, created_at)
表：products (id, name, category, price)
表：users (id, name, email, region, created_at)

关系：orders.user_id → users.id, orders.product_id → products.id
"""

nl2sql_prompt = ChatPromptTemplate.from_template("""你是 SQL 专家。根据用户的自然语言问题生成 SQL 查询。

数据库结构：
{schema}

规则：
1. 只生成 SELECT 查询
2. 使用标准 SQL 语法
3. 对中文字段名使用英文列名
4. 复杂查询添加注释

用户问题：{question}

只输出 SQL，不要其他内容：
""")

async def nl_to_sql(question: str) -> str:
    chain = nl2sql_prompt | llm
    result = await chain.ainvoke({"schema": DB_SCHEMA, "question": question})
    sql = result.content.strip().strip("```sql").strip("```").strip()
    return sql

# 示例
sql = await nl_to_sql("上个月各地区的销售额排名")
# SELECT u.region, SUM(o.amount) as total_sales
# FROM orders o JOIN users u ON o.user_id = u.id
# WHERE o.created_at >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
# GROUP BY u.region ORDER BY total_sales DESC
```

## 3. 安全执行 SQL

```python
import sqlite3
import pandas as pd

class SafeSQLExecutor:
    """安全的 SQL 执行器"""

    FORBIDDEN_KEYWORDS = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "TRUNCATE", "GRANT"]

    def __init__(self, db_path: str):
        self.db_path = db_path

    def validate_sql(self, sql: str) -> bool:
        upper = sql.upper().strip()
        if not upper.startswith("SELECT"):
            return False
        return not any(kw in upper for kw in self.FORBIDDEN_KEYWORDS)

    def execute(self, sql: str) -> pd.DataFrame:
        if not self.validate_sql(sql):
            raise ValueError("只允许 SELECT 查询")
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(sql, conn)
            if len(df) > 10000:
                df = df.head(10000)  # 限制返回行数
            return df
        finally:
            conn.close()

executor = SafeSQLExecutor("business.db")
df = executor.execute(sql)
```

## 4. 数据可视化

```python
import matplotlib.pyplot as plt
import matplotlib
matplotlib.rcParams['font.sans-serif'] = ['SimHei']  # 中文支持

class DataVisualizer:
    """数据可视化生成器"""

    async def auto_visualize(self, df: pd.DataFrame, question: str) -> str:
        """根据数据和问题自动选择图表类型"""
        prompt = f"""根据数据和问题，选择最合适的图表类型。

数据列：{list(df.columns)}
数据行数：{len(df)}
数据示例：{df.head(3).to_string()}
问题：{question}

回答格式：{{"chart_type": "bar/line/pie/scatter", "x": "列名", "y": "列名", "title": "标题"}}"""

        config = eval((await llm.ainvoke(prompt)).content)
        return self._create_chart(df, config)

    def _create_chart(self, df: pd.DataFrame, config: dict) -> str:
        fig, ax = plt.subplots(figsize=(10, 6))
        chart_type = config["chart_type"]

        if chart_type == "bar":
            df.plot(kind="bar", x=config["x"], y=config["y"], ax=ax)
        elif chart_type == "line":
            df.plot(kind="line", x=config["x"], y=config["y"], ax=ax)
        elif chart_type == "pie":
            df.set_index(config["x"])[config["y"]].plot(kind="pie", ax=ax, autopct="%1.1f%%")

        ax.set_title(config["title"])
        path = f"charts/{config['title']}.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        plt.close()
        return path

visualizer = DataVisualizer()
chart_path = await visualizer.auto_visualize(df, "各地区销售额对比")
```

## 5. 报告生成

```python
async def generate_report(question: str, sql: str, df: pd.DataFrame, chart_path: str) -> str:
    """生成数据分析报告"""
    stats = df.describe().to_string()

    prompt = f"""基于以下数据分析结果，生成一份简洁的分析报告。

原始问题：{question}
SQL 查询：{sql}
数据统计：
{stats}

数据预览：
{df.head(10).to_string()}

报告要求：
1. 关键发现（3-5 条）
2. 数据洞察
3. 建议措施
使用 Markdown 格式。"""

    report = (await llm.ainvoke(prompt)).content
    # 插入图表
    report += f"\n\n![数据图表]({chart_path})\n"
    return report
```

## 6. 完整 Agent 流程

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict

class AnalysisState(TypedDict):
    question: str
    sql: str
    data: str  # JSON
    chart_path: str
    report: str

async def step_nl2sql(state: AnalysisState) -> dict:
    sql = await nl_to_sql(state["question"])
    return {"sql": sql}

async def step_execute(state: AnalysisState) -> dict:
    df = executor.execute(state["sql"])
    return {"data": df.to_json()}

async def step_visualize(state: AnalysisState) -> dict:
    df = pd.read_json(state["data"])
    path = await visualizer.auto_visualize(df, state["question"])
    return {"chart_path": path}

async def step_report(state: AnalysisState) -> dict:
    df = pd.read_json(state["data"])
    report = await generate_report(state["question"], state["sql"], df, state["chart_path"])
    return {"report": report}

graph = StateGraph(AnalysisState)
graph.add_node("nl2sql", step_nl2sql)
graph.add_node("execute", step_execute)
graph.add_node("visualize", step_visualize)
graph.add_node("report", step_report)
graph.add_edge(START, "nl2sql")
graph.add_edge("nl2sql", "execute")
graph.add_edge("execute", "visualize")
graph.add_edge("visualize", "report")
graph.add_edge("report", END)

analysis_agent = graph.compile()
result = await analysis_agent.ainvoke({"question": "分析上季度各产品线的销售趋势"})
print(result["report"])
```
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - LangChain Chat with Your Data](https://www.deeplearning.ai/short-courses/langchain-chat-with-your-data/) — 数据对话Agent（免费）
- [freeCodeCamp - Data Analysis with AI](https://www.youtube.com/watch?v=T-D1OfcDW1M) — AI数据分析教程

## 7. 2026 年 Agentic Analytics 趋势

> 🔄 更新于 2026-05-04

<!-- version-check: Agentic Analytics 2026, Snowflake Cortex, Databricks Genie, checked 2026-05-04 -->

2026 年数据分析 Agent 从实验性项目进入规模化部署阶段，核心变化：

**市场格局**：
- AI Agent 全球市场预计 2033 年达 $139B，44% CAGR
- 企业报告分析时间缩短 50-70%
- 从"人问数据答"转向"Agent 自主调查"

**三大平台类型**：

| 类型 | 代表产品 | 特点 |
|------|---------|------|
| 个人分析助手 | Julius.ai、ChatGPT | 上传数据即分析，零代码 |
| 数据团队协作 | Snowflake Cortex、Databricks Genie、Hex | NL-to-SQL + 治理 + 协作 |
| 企业 Agentic 平台 | Tellius | 自主根因调查 + 24/7 KPI 监控 |

**关键趋势**：
1. **Agentic Analytics**：Agent 不再等待提问，主动发现异常、调查根因、生成报告
2. **多步自主调查**：Agent 可以规划分析路径、跨数据源查询、解释结果并继续深入
3. **治理内置**：企业级平台将数据权限、审计追踪、SQL 审查内置到 Agent 工作流
4. **MCP 标准化**：数据源通过 MCP Server 暴露给 Agent，统一工具接口

来源：[Best AI Data Analysis Agents 2026](https://s16353.pcdn.co/resources/blog/best-ai-data-analysis-agents-in-2026-12-platforms-compared-for-nl-to-sql-autonomous-investigation-and-governance)、[MindStudio](https://www.mindstudio.ai/blog/ai-agents-data-analysis-ways)

## 8. DuckLake 1.0 与 Agentic Analytics 的契合

> 🔄 更新于 2026-05-20

<!-- version-check: DuckLake 1.0 GA (2026-04-13), Agent-friendly lakehouse, checked 2026-05-20 -->

第 7 节谈到 Agentic Analytics 的核心变化是"Agent 自主调查"——这给底层数据基础设施提出新要求：

```
传统 Lakehouse 启动门槛：
  Spark cluster + Iceberg REST Catalog + 对象存储
  → 设置时间：分钟到小时
  → Agent 等不起

DuckLake 1.0 + DuckDB（2026-04-13 GA）：
  Postgres 元数据 + S3 Parquet + DuckDB 进程
  → 设置时间：秒级
  → Agent 调用一次工具就能拉起
```

### 8.1 为什么 DuckLake 适合 Agent 调查场景

- **元数据走 SQL**：Agent 用 `SELECT * FROM ducklake_snapshot` 就能查表的所有历史，不需要解析散落的 metadata.json
- **多写并发由 Postgres 保证**：多个 Agent 并行写入同一数据集时，事务隔离由元数据库 ACID 处理，不需要外部 catalog
- **Data Inlining**：小表（配置、维度表）直接存元数据库，Agent 查询零 S3 延迟
- **与 Iceberg 互通**：Agent 在 DuckLake 里探索完，可以把表导出成 Iceberg 给 Spark/Trino 跑生产 ETL

### 8.2 Agent 工具示例

```python
# Agent 通过 MCP 工具触发"在 DuckLake 上做分析"
from mcp.server.fastmcp import FastMCP
import duckdb

mcp = FastMCP("ducklake-analytics")

@mcp.tool()
def analyze_with_ducklake(question: str, table_glob: str) -> str:
    """让 Agent 在 DuckLake 上做即席分析。
    table_glob 是 S3 上 Parquet 文件的 glob 模式。"""
    con = duckdb.connect()
    # 几秒内拉起 lakehouse：Postgres 元数据库 + S3 数据
    con.execute("""
        ATTACH 'ducklake:postgres:host=metadb dbname=lake' AS lake
    """)
    con.execute("USE lake")

    # Agent 自己写 SQL 跑分析（NL-to-SQL 已在更上游完成）
    result = con.execute(f"""
        SELECT date_trunc('day', ts) AS day, count(*) AS events
        FROM read_parquet('{table_glob}')
        GROUP BY 1 ORDER BY 1 DESC LIMIT 30
    """).fetchall()
    return str(result)
```

### 8.3 ClickHouse Agentic Data Stack 的对照路线

ClickHouse 在 2026 年同步推出了 [Agentic Data Stack](https://clickhouse.com/ai)：ClickHouse + LibreChat + Langfuse 组合。与 DuckLake 路线的差异：

| 维度 | DuckLake + DuckDB | ClickHouse Agentic Data Stack |
|------|-------------------|------------------------------|
| 数据规模 | GB ~ 中 TB | TB ~ PB |
| 启动方式 | 一个 DuckDB 进程 | 已有 ClickHouse 集群 |
| 元数据 | Postgres 中的元数据表 | ClickHouse 自身 |
| Agent 集成 | MCP 工具 + DuckDB SQL | LibreChat + Langfuse 可观测 |
| 适合场景 | 个人 / 团队级即席分析 | 企业级 OLAP + Agent 联合 |

来源：[ClickHouse — Agentic Data Stack](https://clickhouse.com/ai)、[DuckLake 1.0 GA](https://duckdb.org/2026/04/13/ducklake-10.html)
