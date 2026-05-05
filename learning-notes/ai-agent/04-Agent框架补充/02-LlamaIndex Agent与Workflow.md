# LlamaIndex Agent 与 Workflow
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

<!-- version-check: LlamaIndex 0.14.21, checked 2026-05-05 -->

> 🔄 更新于 2026-05-05

LlamaIndex 提供事件驱动的 Workflow 引擎和多种 Agent 类型，专注于 RAG 和数据处理场景的 Agent 开发。截至 2026 年 5 月，LlamaIndex 已拥有 48K+ GitHub Stars、1500万+ PyPI 年下载量，被 40% 的 Fortune 500 公司采用。

**版本跃升**：`llama-index-core` 从 0.12.x 升级至 **0.14.21**（2026-04-21），主要变化：
- 持久化层全面使用 UTF-8 编码
- DocumentSummaryIndex 节点删除修复
- 结构化输出失败的 ValueError/TypeError 处理改进
- Message Block Buffer 解析修复

最新动态：
- **MCP 集成**：支持将 LlamaIndex Workflows 和 Tools 转换为 MCP Server，也支持使用 MCP Tools
- **AG-UI 动态工具**：支持 Agent-UI 协议的动态工具注册
- **NVIDIA 嵌入 HTTP 客户端**：新增 NVIDIA embeddings HTTP client 支持
- **Bedrock Converse**：新增 Google Gemma 模型支持
- **Databricks 改进**：向量存储和 LLM 解析增强
- **LlamaParse 增强**：企业级 OCR、解析、提取和索引

> 来源：[LlamaIndex PyPI](https://pypi.org/project/llama-index/)、[releasebot.io](https://releasebot.io/updates/run-llama)

```
┌─────────────────────────────────────────────────┐
│              LlamaIndex                          │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐      │
│  │Workflow  │ │Agent     │ │Agentic RAG │      │
│  │事件驱动   │ │ReAct/FC │ │智能检索     │      │
│  └──────────┘ └──────────┘ └────────────┘      │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐      │
│  │LlamaParse│ │VectorStore│ │LlamaCloud │      │
│  │文档解析   │ │向量存储   │ │托管服务    │      │
│  └──────────┘ └──────────┘ └────────────┘      │
│  ┌──────────┐ ┌──────────┐                      │
│  │MCP Server│ │AG-UI     │                      │
│  │协议集成   │ │动态工具   │                      │
│  └──────────┘ └──────────┘                      │
└─────────────────────────────────────────────────┘
```

## 2. Workflow 核心概念

```python
from llama_index.core.workflow import (
    Workflow, StartEvent, StopEvent, Event, step, Context
)

# 自定义事件
class ResearchComplete(Event):
    findings: str

class DraftComplete(Event):
    draft: str
    iteration: int

# 定义 Workflow
class ContentWorkflow(Workflow):

    @step
    async def research(self, ctx: Context, ev: StartEvent) -> ResearchComplete:
        """研究阶段"""
        topic = ev.topic
        llm = await ctx.get("llm")
        response = await llm.acomplete(f"调研主题：{topic}，列出关键发现")
        # 存储到上下文（跨步骤共享）
        await ctx.set("topic", topic)
        return ResearchComplete(findings=response.text)

    @step
    async def write(self, ctx: Context, ev: ResearchComplete) -> DraftComplete:
        """写作阶段"""
        topic = await ctx.get("topic")
        llm = await ctx.get("llm")
        response = await llm.acomplete(
            f"基于调研写文章：\n主题：{topic}\n发现：{ev.findings}"
        )
        return DraftComplete(draft=response.text, iteration=1)

    @step
    async def review(self, ctx: Context, ev: DraftComplete) -> DraftComplete | StopEvent:
        """审查阶段（可循环）"""
        llm = await ctx.get("llm")
        review = await llm.acomplete(
            f"审查文章质量(1-10分)，只输出分数：\n{ev.draft[:500]}"
        )
        score = int(review.text.strip().split()[0])

        if score >= 8 or ev.iteration >= 3:
            return StopEvent(result=ev.draft)

        # 重写
        improved = await llm.acomplete(f"改进文章：\n{ev.draft}")
        return DraftComplete(draft=improved.text, iteration=ev.iteration + 1)

# 运行
from llama_index.llms.openai import OpenAI

workflow = ContentWorkflow()
result = await workflow.run(
    topic="AI Agent 2025",
    llm=OpenAI(model="gpt-4o"),
)
```

## 3. Agent 类型

```python
from llama_index.core.agent import ReActAgent, FunctionCallingAgent
from llama_index.core.tools import FunctionTool
from llama_index.llms.openai import OpenAI

# 定义工具
def search(query: str) -> str:
    """搜索互联网获取信息"""
    return f"搜索结果: {query}..."

def calculate(expression: str) -> str:
    """执行数学计算"""
    return str(eval(expression))

tools = [
    FunctionTool.from_defaults(fn=search),
    FunctionTool.from_defaults(fn=calculate),
]

llm = OpenAI(model="gpt-4o")

# ReAct Agent（推理+行动循环）
react_agent = ReActAgent.from_tools(
    tools=tools,
    llm=llm,
    verbose=True,
    max_iterations=10,
)
response = react_agent.chat("全球AI市场2025年规模多少？计算年增长率。")

# Function Calling Agent（原生工具调用）
fc_agent = FunctionCallingAgent.from_tools(
    tools=tools,
    llm=llm,
    verbose=True,
)
response = fc_agent.chat("搜索 LangGraph 最新版本")
```

## 4. Agentic RAG

```python
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core.tools import QueryEngineTool
from llama_index.core.agent import FunctionCallingAgent
from llama_index.llms.openai import OpenAI

# 构建多个知识库索引
api_docs = SimpleDirectoryReader("./docs/api").load_data()
api_index = VectorStoreIndex.from_documents(api_docs)

tutorial_docs = SimpleDirectoryReader("./docs/tutorials").load_data()
tutorial_index = VectorStoreIndex.from_documents(tutorial_docs)

# 将索引包装为工具
api_tool = QueryEngineTool.from_defaults(
    query_engine=api_index.as_query_engine(),
    name="api_docs",
    description="查询 API 文档，包含接口定义和参数说明",
)

tutorial_tool = QueryEngineTool.from_defaults(
    query_engine=tutorial_index.as_query_engine(),
    name="tutorials",
    description="查询教程文档，包含使用示例和最佳实践",
)

# Agentic RAG：Agent 自动选择查询哪个知识库
agent = FunctionCallingAgent.from_tools(
    tools=[api_tool, tutorial_tool],
    llm=OpenAI(model="gpt-4o"),
    system_prompt="你是技术文档助手。根据问题选择合适的知识库查询。",
)

response = agent.chat("如何使用 create_user API？给个完整示例。")
# Agent 自动：先查 API 文档获取接口定义，再查教程获取示例
```

## 5. 多 Agent Workflow

```python
from llama_index.core.workflow import Workflow, StartEvent, StopEvent, Event, step

class AgentTask(Event):
    agent_name: str
    task: str

class AgentResult(Event):
    agent_name: str
    result: str

class MultiAgentWorkflow(Workflow):

    @step
    async def orchestrator(self, ctx: Context, ev: StartEvent) -> AgentTask:
        """编排者：分配任务"""
        # 并行分发任务
        ctx.send_event(AgentTask(agent_name="researcher", task=f"调研：{ev.query}"))
        ctx.send_event(AgentTask(agent_name="analyst", task=f"分析：{ev.query}"))
        # 等待所有结果
        await ctx.set("pending", 2)
        return None  # 不直接返回，等待收集结果

    @step
    async def worker(self, ctx: Context, ev: AgentTask) -> AgentResult:
        """工作者：执行任务"""
        llm = await ctx.get("llm")
        result = await llm.acomplete(f"你是{ev.agent_name}。{ev.task}")
        return AgentResult(agent_name=ev.agent_name, result=result.text)

    @step
    async def synthesizer(self, ctx: Context, ev: AgentResult) -> StopEvent | None:
        """合成者：收集并合并结果"""
        results = await ctx.get("results", default=[])
        results.append({"agent": ev.agent_name, "result": ev.result})
        await ctx.set("results", results)

        pending = await ctx.get("pending") - 1
        await ctx.set("pending", pending)

        if pending == 0:
            llm = await ctx.get("llm")
            combined = "\n".join(f"[{r['agent']}]: {r['result']}" for r in results)
            final = await llm.acomplete(f"综合以下分析：\n{combined}")
            return StopEvent(result=final.text)
        return None
```

## 6. LlamaParse 文档解析

```python
from llama_parse import LlamaParse

# 解析复杂文档（PDF、PPT、Excel 等）
parser = LlamaParse(
    api_key="llx-xxx",
    result_type="markdown",
    language="ch_sim",  # 中文支持
)

documents = parser.load_data("./complex_report.pdf")

# 与 RAG 结合
from llama_index.core import VectorStoreIndex
index = VectorStoreIndex.from_documents(documents)
query_engine = index.as_query_engine()
response = query_engine.query("报告中的主要结论是什么？")
```

## 7. 工具集成

```python
from llama_index.core.tools import FunctionTool
from llama_index.tools.tavily_research import TavilyToolSpec

# Tavily 搜索工具
tavily_tools = TavilyToolSpec(api_key="tvly-xxx").to_tool_list()

# 自定义工具
@FunctionTool.from_defaults
def query_database(sql: str) -> str:
    """执行 SQL 查询"""
    import sqlite3
    conn = sqlite3.connect("app.db")
    result = conn.execute(sql).fetchall()
    return str(result)

# 组合所有工具
all_tools = tavily_tools + [query_database]

agent = ReActAgent.from_tools(
    tools=all_tools,
    llm=OpenAI(model="gpt-4o"),
    verbose=True,
)
```

## 8. 与其他框架对比

| 特性         | LlamaIndex       | LangGraph        | CrewAI           |
|-------------|------------------|------------------|------------------|
| 核心定位     | 数据/RAG 优先     | 通用工作流        | 角色协作          |
| 编排模型     | 事件驱动 Workflow | 图（StateGraph）  | 顺序/层级         |
| RAG 能力    | ✅ 核心优势       | ✅ 需自建         | ✅ 基础           |
| 文档解析     | ✅ LlamaParse    | ❌               | ❌               |
| MCP 支持    | ✅ 双向集成       | ✅               | ✅               |
| Agent 类型  | ReAct / FC       | 自定义            | 角色 Agent        |
| 学习曲线     | 中               | 中高              | 低               |
| 适用场景     | RAG/数据密集型    | 复杂自定义流程     | 团队协作任务       |
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Building Agentic RAG with LlamaIndex](https://www.deeplearning.ai/short-courses/building-agentic-rag-with-llamaindex/) — LlamaIndex Agentic RAG（免费）
- [LlamaIndex - Workflow Tutorial](https://www.youtube.com/watch?v=dcgRMOG605w) — LlamaIndex Workflow教程

### 📖 官方文档
- [LlamaIndex Docs](https://docs.llamaindex.ai/) — LlamaIndex官方文档
