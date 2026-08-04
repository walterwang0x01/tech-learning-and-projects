# Agent 工作流编排模式
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. DAG（有向无环图）工作流

任务节点形成有向无环图，支持并行和依赖关系。

```
    ┌───┐     ┌───┐
    │ A │────→│ C │────┐
    └───┘     └───┘    ↓
                     ┌───┐
                     │ E │
                     └───┘
    ┌───┐     ┌───┐    ↑
    │ B │────→│ D │────┘
    └───┘     └───┘
    A,B 并行 → C,D 并行 → E 汇聚
```

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from operator import add
import asyncio

class DAGState(TypedDict):
    results: Annotated[list, add]

async def node_a(state: DAGState) -> dict:
    result = await llm.ainvoke("执行任务A：数据收集")
    return {"results": [f"A: {result.content[:50]}"]}

async def node_b(state: DAGState) -> dict:
    result = await llm.ainvoke("执行任务B：环境检查")
    return {"results": [f"B: {result.content[:50]}"]}

async def node_c(state: DAGState) -> dict:
    return {"results": ["C: 数据处理完成"]}

async def node_d(state: DAGState) -> dict:
    return {"results": ["D: 环境配置完成"]}

async def node_e(state: DAGState) -> dict:
    return {"results": [f"E: 汇总 {len(state['results'])} 个结果"]}

graph = StateGraph(DAGState)
graph.add_node("A", node_a)
graph.add_node("B", node_b)
graph.add_node("C", node_c)
graph.add_node("D", node_d)
graph.add_node("E", node_e)

# DAG 边定义
graph.add_edge(START, "A")
graph.add_edge(START, "B")  # A, B 并行
graph.add_edge("A", "C")
graph.add_edge("B", "D")
graph.add_edge("C", "E")
graph.add_edge("D", "E")   # C, D → E 汇聚
graph.add_edge("E", END)

dag_app = graph.compile()
```

## 2. 状态机工作流

基于当前状态和事件决定下一步转换。

```
┌────────┐  成功  ┌────────┐  成功  ┌────────┐
│ 初始化  │──────→│ 处理中  │──────→│ 已完成  │
└────────┘       └────────┘       └────────┘
                    │ 失败            ↑ 重试成功
                    ↓                │
                 ┌────────┐──────────┘
                 │ 错误    │
                 └────────┘──→ 超过重试 → [终止]
```

```python
from enum import Enum

class WorkflowState(Enum):
    INIT = "init"
    PROCESSING = "processing"
    ERROR = "error"
    COMPLETED = "completed"
    TERMINATED = "terminated"

class StateMachineWorkflow:
    def __init__(self):
        self.state = WorkflowState.INIT
        self.retries = 0
        self.max_retries = 3
        self.transitions = {
            WorkflowState.INIT: {"start": WorkflowState.PROCESSING},
            WorkflowState.PROCESSING: {
                "success": WorkflowState.COMPLETED,
                "failure": WorkflowState.ERROR,
            },
            WorkflowState.ERROR: {
                "retry": WorkflowState.PROCESSING,
                "abort": WorkflowState.TERMINATED,
            },
        }

    def transition(self, event: str) -> WorkflowState:
        valid = self.transitions.get(self.state, {})
        if event not in valid:
            raise ValueError(f"无效转换: {self.state} + {event}")
        if event == "retry":
            self.retries += 1
            if self.retries > self.max_retries:
                self.state = WorkflowState.TERMINATED
                return self.state
        self.state = valid[event]
        return self.state
```

## 3. 事件驱动工作流

通过事件触发和响应驱动流程推进。

```python
from llama_index.core.workflow import Workflow, StartEvent, StopEvent, Event, step

# 自定义事件
class ResearchDone(Event):
    findings: str

class WritingDone(Event):
    draft: str

class ReviewDone(Event):
    feedback: str
    approved: bool

class ResearchWriteWorkflow(Workflow):
    @step
    async def research(self, ev: StartEvent) -> ResearchDone:
        """研究阶段"""
        result = await llm.ainvoke(f"调研：{ev.topic}")
        return ResearchDone(findings=result.content)

    @step
    async def write(self, ev: ResearchDone) -> WritingDone:
        """写作阶段"""
        draft = await llm.ainvoke(f"基于调研写文章：{ev.findings[:500]}")
        return WritingDone(draft=draft.content)

    @step
    async def review(self, ev: WritingDone) -> StopEvent | WritingDone:
        """审查阶段"""
        review = await llm.ainvoke(f"审查文章质量，回答PASS/FAIL：{ev.draft[:500]}")
        if "PASS" in review.content:
            return StopEvent(result=ev.draft)
        return WritingDone(draft=ev.draft)  # 重写

workflow = ResearchWriteWorkflow()
result = await workflow.run(topic="AI Agent 2025趋势")
```

## 4. 条件分支与循环

```python
def route_by_complexity(state: dict) -> str:
    """根据任务复杂度路由"""
    complexity = state.get("complexity", "low")
    if complexity == "high":
        return "deep_analysis"
    elif complexity == "medium":
        return "standard_process"
    return "quick_answer"

def check_quality(state: dict) -> str:
    """质量检查决定是否循环"""
    if state["quality_score"] >= 8:
        return "output"
    if state["iteration"] >= 3:
        return "output"  # 最多3轮
    return "improve"     # 继续改进

graph = StateGraph(TaskState)
graph.add_node("classify", classify_task)
graph.add_node("deep_analysis", deep_analysis)
graph.add_node("standard_process", standard_process)
graph.add_node("quick_answer", quick_answer)
graph.add_node("improve", improve_output)
graph.add_node("output", format_output)

graph.add_conditional_edges("classify", route_by_complexity)
graph.add_conditional_edges("standard_process", check_quality)
```

## 5. 并行 Fan-Out / Fan-In

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from operator import add

class FanState(TypedDict):
    query: str
    partial_results: Annotated[list, add]
    final_answer: str

# Fan-Out：一个输入分发到多个处理器
async def search_web(state: FanState) -> dict:
    return {"partial_results": [{"source": "web", "data": "网页搜索结果..."}]}

async def search_docs(state: FanState) -> dict:
    return {"partial_results": [{"source": "docs", "data": "文档搜索结果..."}]}

async def search_db(state: FanState) -> dict:
    return {"partial_results": [{"source": "db", "data": "数据库查询结果..."}]}

# Fan-In：合并所有结果
async def synthesize(state: FanState) -> dict:
    all_data = "\n".join(r["data"] for r in state["partial_results"])
    answer = await llm.ainvoke(f"综合信息回答：{state['query']}\n{all_data}")
    return {"final_answer": answer.content}

graph = StateGraph(FanState)
graph.add_node("search_web", search_web)
graph.add_node("search_docs", search_docs)
graph.add_node("search_db", search_db)
graph.add_node("synthesize", synthesize)

# Fan-Out
graph.add_edge(START, "search_web")
graph.add_edge(START, "search_docs")
graph.add_edge(START, "search_db")
# Fan-In
graph.add_edge("search_web", "synthesize")
graph.add_edge("search_docs", "synthesize")
graph.add_edge("search_db", "synthesize")
graph.add_edge("synthesize", END)
```

## 6. 子工作流组合

```python
# 子工作流：研究
research_graph = StateGraph(ResearchState)
research_graph.add_node("search", search_node)
research_graph.add_node("analyze", analyze_node)
research_graph.add_edge(START, "search")
research_graph.add_edge("search", "analyze")
research_graph.add_edge("analyze", END)
research_sub = research_graph.compile()

# 子工作流：写作
writing_graph = StateGraph(WritingState)
writing_graph.add_node("draft", draft_node)
writing_graph.add_node("edit", edit_node)
writing_graph.add_edge(START, "draft")
writing_graph.add_edge("draft", "edit")
writing_graph.add_edge("edit", END)
writing_sub = writing_graph.compile()

# 主工作流组合子工作流
main_graph = StateGraph(MainState)
main_graph.add_node("research", research_sub)
main_graph.add_node("writing", writing_sub)
main_graph.add_node("publish", publish_node)
main_graph.add_edge(START, "research")
main_graph.add_edge("research", "writing")
main_graph.add_edge("writing", "publish")
main_graph.add_edge("publish", END)
```

## 7. 错误处理与重试策略

```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

class WorkflowErrorHandler:
    """工作流错误处理"""

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def execute_with_retry(self, func, state):
        return await func(state)

    async def execute_node(self, node_name: str, func, state: dict) -> dict:
        try:
            return await self.execute_with_retry(func, state)
        except Exception as e:
            # 降级策略
            if node_name in self.fallback_handlers:
                return await self.fallback_handlers[node_name](state, e)
            # 记录错误并跳过
            return {"error": str(e), "node": node_name, "skipped": True}
```

## 8. 检查点与恢复

```python
from langgraph.checkpoint.postgres import PostgresSaver

# 生产级检查点
checkpointer = PostgresSaver.from_conn_string("postgresql://user:pass@host/db")
app = graph.compile(checkpointer=checkpointer)

# 执行带检查点的工作流
config = {"configurable": {"thread_id": "workflow-001"}}
result = app.invoke(initial_state, config)

# 从中断处恢复（如服务重启后）
# LangGraph 自动从最近检查点恢复
resumed = app.invoke(None, config)  # 传入 None 表示恢复
```

## 9. 框架编排对比

| 特性         | LangGraph        | CrewAI          | Google ADK       |
|-------------|------------------|-----------------|------------------|
| 编排模型     | 图（StateGraph）  | 顺序/层级        | Agent 树         |
| 并行支持     | 原生 Fan-Out     | 异步任务         | 并行 Agent       |
| 状态管理     | TypedDict + 检查点| 共享内存         | Session + State  |
| 人机交互     | interrupt()      | human_input=True| 回调函数         |
| 子工作流     | 子图嵌套          | 嵌套 Crew       | Sub-Agent        |
| 错误处理     | 条件边 + 重试     | 任务级重试       | 回调 + 重试      |
| 持久化       | Postgres/Redis   | 无内置           | Vertex AI Store  |
| 部署         | LangGraph Cloud  | CrewAI Enterprise| Vertex AI Agent  |
| 适用场景     | 复杂自定义流程    | 角色协作任务      | Google 云原生    |

<!-- version-check: LangGraph 1.1.9, langgraph-prebuilt 1.0.11, Deep Agents deploy, checked 2026-05-12 -->

> 🔄 更新于 2026-05-12

## 10. 2026 年工作流编排趋势

### 10.1 LangGraph 1.1.9 版本演进

LangGraph 从 1.1.6 更新至 **1.1.9**（2026-04-21），配套生态同步迭代：

| 组件 | 版本 | 关键变化 |
|------|------|---------|
| langgraph | 1.1.9 | 修复子图 ReplayState 传播、stream handler 清理 |
| langgraph-prebuilt | 1.0.11 | ToolNode 支持返回 `list[Command \| ToolMessage]`、ToolRuntime 暴露可用工具 |
| langchain-core | 1.3.2 | content-block-centric streaming v2、tracer metadata 增强 |

来源：[Releasebot LangChain Updates](https://releasebot.io/updates/langchain-ai)

**ToolNode 增强示例**：

```python
from langgraph.prebuilt import ToolNode

# ToolNode 现在支持工具返回 Command 列表
# 允许工具直接控制图的执行流程
async def smart_tool(query: str) -> list:
    """工具可以返回 Command 来控制图的下一步"""
    result = await search(query)
    if result.needs_human_review:
        # 返回 Command 让图跳转到人工审核节点
        return [Command(goto="human_review", update={"data": result})]
    return [ToolMessage(content=result.text)]
```

### 10.2 Deep Agents 与非阻塞后台任务

LangGraph JS 引入 **Deep Agents** 概念（需要 LangSmith Deployment）：

- Agent 可以启动非阻塞后台子任务
- 用户在子 Agent 工作时可继续与主 Agent 交互
- 适用于长时间运行的研究、数据处理等场景

**Deep Agents Deploy**（2026-04-20）：LangChain 发布 `deepagents deploy` 命令，一键将 Deep Agents harness（模型、指令、工具、技能、沙箱）部署为生产就绪的水平扩展服务器。与 Claude Managed Agents 不同，Deep Agents 将记忆存储在开发者拥有和直接查询的标准格式中。

来源：[LangChain Blog - Deep Agents](https://www.langchain.com/blog/deep-agents-deploy-an-open-alternative-to-claude-managed-agents)、[LangChain Blog - Deep Agents Runtime](https://blog.langchain.com/)

### 10.3 Agent Development Lifecycle（2026-05-09）

Harrison Chase 发布 **Agent Development Lifecycle** 概念框架，定义了 Agent 从原型到生产的完整工程流程：

```
Build → Evaluate → Deploy → Monitor → Feedback → Build（循环）
```

核心观点：测试应在 Agent 到达生产之前开始，而非之后。团队需要在部署前测试 Agent、以受控方式部署、监控生产行为、并将学习反馈到下一轮构建和评估周期。

这标志着 Agent 工程从"如何构建"进入"如何运维"的成熟阶段。

来源：[LangChain Blog - The Agent Development Lifecycle](https://www.langchain.com/blog/the-agent-development-lifecycle)

### 10.4 Interrupt 2026 大会（2026-05-13/14）

LangChain 年度大会主题从"Agent 能否在生产中工作？"（2025）转变为"如何让 Agent 在企业规模下工作？"。演讲者包括 Andrew Ng、Harrison Chase，以及 Clay、Rippling 等公司的 AI 团队。

来源：[Interrupt 2026 Preview](https://blog.langchain.com/previewing-interrupt-2026-agents-at-enterprise-scale/)

### 10.3 工作流编排模式演进方向

2026 年工作流编排的三个关键趋势：

1. **工具即控制流**：ToolNode 返回 Command 让工具直接参与图的路由决策，模糊了"工具调用"和"流程控制"的边界
2. **有状态续传标准化**：Cursor 3 减少 80% 数据传输、LangGraph 检查点恢复、CrewAI Checkpoint 系统，断点恢复成为生产级 Agent 的标配
3. **Agent 运行时托管化**：Claude Managed Agents、LangSmith Deployment、CrewAI Enterprise 将编排基础设施从开发者手中转移到平台
## 🎬 推荐视频资源

### 🌐 YouTube
- [Andrew Ng - What's Next for AI Agentic Workflows](https://www.youtube.com/watch?v=sal78ACtGTc) — 吴恩达讲Agentic工作流
- [DeepLearning.AI - AI Agents in LangGraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) — LangGraph工作流编排（免费）

### 📺 B站
- [吴恩达 - Agentic工作流中文字幕](https://www.bilibili.com/video/BV1Bz421B7bG) — Agentic工作流讲解
