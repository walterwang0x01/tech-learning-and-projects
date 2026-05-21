# LangGraph 工作流编排
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

<!-- version-check: LangGraph 1.2 stable, 126K+ Stars, Deep Agents v0.6, Delta Channels GA, Streaming API v3, Managed Deep Agents, checked 2026-05-21 -->
LangGraph 是 LangChain 团队推出的 Agent 工作流编排框架，基于图结构定义 Agent 的执行流程。2025 年 10 月发布 1.0 GA，目前最新版本为 1.2 稳定版，126K+ GitHub Stars，90M+ 月下载量，是目前生产级 Agent 开发的行业标准。Uber、JP Morgan、BlackRock、Cisco、LinkedIn、Klarna、Replit、Elastic 等企业已在生产环境部署。来源：[LangChain Blog](https://blog.langchain.com/langchain-langgraph-1dot0/)、[Releasebot](https://releasebot.io/updates/langchain-ai)

> 🔄 更新于 2026-05-14

**Interrupt 2026 Day 1 发布（2026-05-13）— Deep Agents v0.6 + Managed Deep Agents**：

Deep Agents v0.6 五大核心特性：

1. **Code Interpreter**：轻量级代码执行运行时（QuickJS），Agent 可编写代码组合工具调用、管理中间状态、控制上下文窗口。支持 Programmatic Tool Calling（PTC）——模型写代码调用工具而非逐个 round-trip，减少 Token 消耗和模型调用次数。任何模型（包括开源）都可实现 PTC，不再局限于 Anthropic 的 API 行为。

2. **Harness Profiles**：per-model 调优配置，让开源模型（Kimi K2.6、GLM 5.1、DeepSeek V4）以 20x+ 更低成本达到生产级性能。测试数据：harness 层调优让 gpt-5.2-codex 在 Terminal-Bench 2.0 上从 52.8% → 66.5%，opus-4.7 提升 10%，tau2-bench 上 prompts+middleware 可移动 10-20 分。

3. **Streaming v3**：类型化事件投影（messages、tool calls、subagents、custom channels），前端框架集成（`@langchain/react`、`@langchain/vue`、`@langchain/svelte`、`@langchain/angular` v1），遵循新的 [Agent Streaming Protocol](https://github.com/langchain-ai/agent-protocol/tree/main/streaming)。

4. **Delta Channels**：增量 checkpoint 存储，200 轮编码会话从 5.27 GB 降至 129 MB（约 40x 压缩），O(N²) → O(N) 存储增长。

5. **ContextHub Backend**：Agent 文件系统后端连接 LangSmith Context Hub，技能/策略/记忆版本化存储，跨 run 持续改进。

```python
# Deep Agents v0.6 — Code Interpreter + Harness Profile
from deepagents import create_deep_agent
from langchain_quickjs import REPLMiddleware

# 开源模型 + 代码解释器 = 低成本高性能
agent = create_deep_agent(
    model="baseten:zai-org/GLM-5",  # 开源模型
    middleware=[REPLMiddleware()],    # 代码解释器中间件
)

# Managed Deep Agents — 托管运行时
# 开发者定义 Agent，LangSmith 处理运行时：
# threads、checkpointing、streaming、context、observability
```

**Managed Deep Agents**（2026-05-13）：开源 Deep Agents harness 的托管版本。开发者在 repo 中定义 Agent，LangSmith 处理运行时（线程、检查点、流式传输、上下文、可观测性）。长时运行 Agent 需要持久化上下文，Managed Deep Agents 提供开箱即用的持久化运行环境。来源：[LangChain Blog](https://www.langchain.com/blog/introducing-managed-deep-agents)

来源：[Deep Agents v0.6](https://www.langchain.com/blog/deep-agents-0-6)（Content was rephrased for compliance with licensing restrictions）

**Delta Channels — 长时运行 Agent 的运行时升级**（2026-05-12）：Deep Agents 构建在 LangGraph 运行时之上，每步都做 checkpoint 以支持可观测性、人机交互和故障恢复。但对于运行数小时甚至数天的 Agent，全量 checkpoint 导致存储爆炸和恢复延迟线性增长。Delta Channels 只存储每步的增量（delta），每 K 步写一次完整快照，将恢复延迟限制在常数级别，存储成本不随会话增长而膨胀。现有 LangGraph 线程无需迁移即可透明升级，消息和文件默认走 delta-backed 存储。来源：[LangChain Blog](https://www.langchain.com/blog/delta-channels-evolving-agent-runtime)

**Interrupt 2026 大会**（2026-05-13/14，旧金山）：LangChain 年度 Agent 大会，超过 1000 名开发者参加。演讲嘉宾包括 Andrew Ng、Harrison Chase、Coinbase、Apple 等企业。主题聚焦"Agents at Enterprise Scale"——企业级 Agent 部署的实战经验。来源：[LangChain Blog](https://www.langchain.com/blog/previewing-interrupt-2026-agents-at-enterprise-scale)

> 🔄 更新于 2026-05-19

<!-- version-check: LangChain 1.2.18 (2026-05-13), LangSmith Engine, LangChain Labs, Interrupt 2026 Day 2, checked 2026-05-19 -->

**Interrupt 2026 Day 2 发布（2026-05-14）— LangSmith Engine + LangChain Labs**：

1. **LangSmith Engine — 自治诊断 Agent**：替代"读 trace → 找 pattern → 写修复"的手动循环。Engine 持续监控生产 trace，把失败聚类成命名 issue，对照代码定位根因，并草拟 PR 和 evaluator 等待开发者评审。每解决一个 issue 都会增强 eval 套件，形成"诊断 → 修复 → 评估 → 防回归"的自我强化闭环。来源：[Introducing LangSmith Engine](https://www.langchain.com/blog/introducing-langsmith-engine)、[Everything we shipped at Interrupt](https://www.langchain.com/blog/interrupt-2026-overview)
2. **LangChain Labs**：新成立的研究实验室，聚焦"让 Agent 更好、更便宜、更易评估"。早期方向：cost/latency 折中、模拟与评估环境、跨模型族 prompt 优化。来源：[Introducing LangChain Labs](https://www.langchain.com/blog/introducing-langchain-labs)
3. **LangChain 1.2.18 同步发布**（2026-05-13）：agent tag 回滚、classic 模块废弃清理、依赖项瘦身。配合 LangGraph 1.2 持续迭代。来源：[Releasebot — May 2026](https://releasebot.io/updates/langchain-ai)

> 🔄 更新于 2026-05-21

**LangGraph 1.2 正式版**（2026-05 月中旬）：

LangGraph 从 1.1.x 升级到 1.2，核心改进：

- **Durable Error-Handler Resume**：错误处理器可跨主机崩溃恢复，Agent 在任意节点失败后可从 checkpoint 精确恢复
- **`set_node_defaults()`**：为 StateGraph 设置全局节点默认配置（超时、重试策略等），减少重复代码
- **DeltaChannel 正式 GA**：增量 checkpoint 存储从实验性升级为稳定特性
- **Streaming API v3**：typed-projection API，按 channel 独立消费（messages、values、subgraphs、output），替代旧的 `stream_mode` 分支模式
- **Graceful Shutdown**：节点执行支持优雅关闭，长时间运行的 Agent 可安全停止

```python
# LangGraph 1.2 新 API 示例
from langgraph.graph import StateGraph

# set_node_defaults：全局配置
graph = StateGraph(AgentState)
graph.set_node_defaults(
    timeout=30,           # 每个节点默认 30s 超时
    retry_policy="exponential",  # 指数退避重试
    max_retries=3
)

# Streaming API v3：typed-projection
async for event in graph.astream(input, stream_mode="events"):
    # 按类型独立消费，无需 if/else 分支
    if event.type == "messages":
        print(event.data)  # 只看消息流
```

来源：[LangGraph Streaming Docs](https://docs.langchain.com/oss/python/langgraph/streaming) | [Delta Channels Blog](https://www.langchain.com/blog/delta-channels-evolving-agent-runtime)
4. **生态协同**：Day 2 强调 "observability and governance ship together now" —— LangSmith Engine（诊断）、LangSmith Fleet（治理 + Agent Card 管理）、LangSmith Insights（成本/质量分析）三者形成统一控制面。

```python
# LangSmith Engine 接入示例（最小化 — 实际配置以官方文档为准）
import os
from langsmith import Client

# 启用 Engine 后，trace 自动进入诊断队列
os.environ["LANGSMITH_ENGINE_ENABLED"] = "true"
os.environ["LANGSMITH_PROJECT"] = "production-agent"

client = Client()

# Engine 后台运行：聚类 issue、生成 PR / evaluator
# 开发者只需要在 Pull Request 评审中确认是否合并 Engine 草拟的修复
```

**对工程团队的影响**：

| 工作流环节 | 之前 | LangSmith Engine 之后 |
|------------|------|--------------------- |
| 故障发现 | 手动看 trace / 用户反馈 | Engine 实时聚类成 issue |
| 根因定位 | 工程师手动比对代码 | Engine 自动定位代码段 |
| 修复 | 工程师写代码 + 评估 | Engine 草拟 PR + eval，工程师评审 |
| 回归保护 | 手动写 evaluator | Engine 自动扩 eval 套件 |

**LangGraph v1 稳定性承诺**：v1 是稳定性聚焦的版本，核心图 API 和执行模型保持不变，重点改进类型安全、文档和开发者体验。langgraph-prebuilt 1.0.11 的 ToolNode 增强让工具可以返回 `list[Command | ToolMessage]`，直接控制图的执行流程。来源：[LangGraph v1 Docs](https://docs.langchain.com/oss/python/releases/langgraph-v1)

核心优势：图结构控制流、模型无关、内置检查点、人机交互支持。

## 2. 核心概念

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated
from operator import add

# 1. 定义状态
class AgentState(TypedDict):
    messages: Annotated[list, add]  # 消息列表（累加）
    next_step: str

# 2. 定义节点（函数）
def call_model(state: AgentState) -> dict:
    response = llm.invoke(state["messages"])
    return {"messages": [response]}

def call_tools(state: AgentState) -> dict:
    last_message = state["messages"][-1]
    results = tool_executor.invoke(last_message.tool_calls)
    return {"messages": results}

# 3. 构建图
graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode(tools))

# 4. 定义边（路由）
def should_continue(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

# 5. 编译并运行
app = graph.compile()
result = app.invoke({"messages": [HumanMessage(content="北京今天天气怎么样？")]})
```

## 3. 检查点与状态持久化

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.postgres import PostgresSaver

# 内存检查点（开发用）
memory = MemorySaver()
app = graph.compile(checkpointer=memory)

# PostgreSQL 检查点（生产用）
checkpointer = PostgresSaver.from_conn_string("postgresql://...")
app = graph.compile(checkpointer=checkpointer)

# 使用 thread_id 维护会话状态
config = {"configurable": {"thread_id": "user-123"}}
result = app.invoke({"messages": [HumanMessage("你好")]}, config)
# 后续对话自动恢复上下文
result = app.invoke({"messages": [HumanMessage("继续上面的话题")]}, config)
```

## 4. 人机交互（Human-in-the-Loop）

```python
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command

def sensitive_action(state: AgentState) -> dict:
    """需要人工审批的敏感操作"""
    action = state["pending_action"]

    # 中断执行，等待人工审批
    approval = interrupt({
        "action": action,
        "message": f"是否批准执行: {action['name']}？"
    })

    if approval == "approved":
        result = execute_action(action)
        return {"messages": [AIMessage(content=f"已执行: {result}")]}
    else:
        return {"messages": [AIMessage(content="操作已取消")]}

# 编译时启用中断
app = graph.compile(checkpointer=memory, interrupt_before=["sensitive_action"])

# 恢复执行
app.invoke(Command(resume="approved"), config)
```

## 5. 子图（Subgraph）

```python
# 将复杂流程拆分为子图
research_graph = StateGraph(ResearchState)
# ... 定义研究子图

writing_graph = StateGraph(WritingState)
# ... 定义写作子图

# 主图组合子图
main_graph = StateGraph(MainState)
main_graph.add_node("research", research_graph.compile())
main_graph.add_node("writing", writing_graph.compile())
main_graph.add_edge("research", "writing")
```

## 6. LangGraph Cloud

```python
# langgraph.json — 部署配置
{
    "graphs": {
        "my_agent": "./agent.py:app"
    },
    "dependencies": ["langchain-openai", "langchain-community"]
}

# 部署到 LangGraph Cloud
# langgraph deploy --config langgraph.json
```
## 🎬 推荐视频资源

- [DeepLearning.AI - AI Agents in LangGraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) — 吴恩达+LangChain联合出品（免费）
- [freeCodeCamp - How to Develop AI Agents Using LangGraph](https://www.youtube.com/watch?v=dcgRMOG605w) — LangGraph实战指南
- [LangChain Official - LangGraph Tutorial](https://www.youtube.com/watch?v=9BPCV5TYPmg) — 官方教程
### 📺 B站（Bilibili）
- [LangChain官方 - LangGraph教程中文字幕](https://www.bilibili.com/video/BV1dH4y1P7FY) — LangGraph入门到实战

### 🎓 DeepLearning.AI（免费）
- [AI Agents in LangGraph](https://www.deeplearning.ai/short-courses/ai-agents-in-langgraph/) — 吴恩达+LangChain联合出品
