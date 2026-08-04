# 多 Agent 架构模式
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 架构模式概览

```
┌─────────────────────────────────────────────────────┐
│              多 Agent 架构模式                        │
├──────────┬──────────┬──────────┬───────────────────┤
│ Supervisor│Hierarchical│ Swarm  │ Network           │
│ 主管模式  │ 层级模式   │ 群体模式│ 网络模式           │
└──────────┴──────────┴──────────┴───────────────────┘
```

## 2. Supervisor 模式（主管模式）

一个主管 Agent 负责任务分配和结果汇总，子 Agent 执行具体任务。

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Literal

class SupervisorState(TypedDict):
    messages: list
    next_agent: str

def supervisor(state: SupervisorState) -> dict:
    """主管 Agent：决定下一步由谁执行"""
    system = """你是任务主管。根据当前对话，决定下一步交给哪个 Agent：
    - researcher: 需要搜索信息
    - coder: 需要编写代码
    - writer: 需要撰写文档
    - FINISH: 任务完成"""

    response = llm.invoke([{"role": "system", "content": system}] + state["messages"])
    return {"next_agent": response.content.strip()}

def researcher(state: SupervisorState) -> dict:
    result = llm.invoke("你是研究员。" + state["messages"][-1])
    return {"messages": [result]}

def coder(state: SupervisorState) -> dict:
    result = llm.invoke("你是程序员。" + state["messages"][-1])
    return {"messages": [result]}

# 构建 Supervisor 图
graph = StateGraph(SupervisorState)
graph.add_node("supervisor", supervisor)
graph.add_node("researcher", researcher)
graph.add_node("coder", coder)

graph.add_edge(START, "supervisor")
graph.add_conditional_edges("supervisor", lambda s: s["next_agent"], {
    "researcher": "researcher",
    "coder": "coder",
    "FINISH": END,
})
graph.add_edge("researcher", "supervisor")
graph.add_edge("coder", "supervisor")

app = graph.compile()
```

## 3. Hierarchical 模式（层级模式）

多层主管，每层管理不同职能的子 Agent。

```
                    ┌──────────┐
                    │ 总主管    │
                    └────┬─────┘
              ┌──────────┼──────────┐
         ┌────┴────┐ ┌───┴────┐ ┌──┴─────┐
         │研究主管  │ │开发主管 │ │测试主管 │
         └────┬────┘ └───┬────┘ └──┬─────┘
          ┌───┴───┐   ┌──┴──┐   ┌──┴──┐
          │搜索   │   │前端 │   │单测  │
          │分析   │   │后端 │   │集成  │
          └───────┘   └─────┘   └─────┘
```

```python
# 子团队作为子图
research_team = create_team_graph(
    supervisor_prompt="你是研究团队主管",
    agents={"searcher": search_agent, "analyst": analysis_agent},
)

dev_team = create_team_graph(
    supervisor_prompt="你是开发团队主管",
    agents={"frontend": fe_agent, "backend": be_agent},
)

# 顶层主管编排子团队
top_graph = StateGraph(TopState)
top_graph.add_node("top_supervisor", top_supervisor)
top_graph.add_node("research_team", research_team.compile())
top_graph.add_node("dev_team", dev_team.compile())
```

## 4. Swarm 模式（群体模式）

Agent 之间通过 Handoff 自主交接，无中心调度。

```python
from openai import OpenAI
from openai.types.beta import AssistantTool

# OpenAI Agents SDK Swarm 模式
from agents import Agent, Runner

triage_agent = Agent(
    name="分诊 Agent",
    instructions="根据用户问题类型，转交给合适的专家 Agent。",
    handoffs=["billing_agent", "tech_agent", "general_agent"],
)

billing_agent = Agent(
    name="账单 Agent",
    instructions="处理账单、支付、退款相关问题。",
    tools=[query_billing, process_refund],
)

tech_agent = Agent(
    name="技术 Agent",
    instructions="处理技术支持、故障排查问题。",
    tools=[check_system_status, create_ticket],
)

# 运行：Agent 自主决定 Handoff
result = await Runner.run(
    triage_agent,
    input="我的上个月账单好像多扣了钱",
)
# triage_agent → 自动 handoff → billing_agent
```

## 5. Network 模式（网络模式）

所有 Agent 可以互相通信，适合复杂协作场景。

```python
class AgentNetwork:
    """Agent 网络：任意 Agent 可以互相通信"""

    def __init__(self):
        self.agents: dict[str, Agent] = {}
        self.message_bus: list[dict] = []

    def register(self, agent: Agent):
        self.agents[agent.name] = agent

    async def send_message(self, from_agent: str, to_agent: str, message: str):
        self.message_bus.append({
            "from": from_agent, "to": to_agent, "content": message
        })
        response = await self.agents[to_agent].process(message)
        return response

    async def broadcast(self, from_agent: str, message: str):
        """广播消息给所有 Agent"""
        responses = {}
        for name, agent in self.agents.items():
            if name != from_agent:
                responses[name] = await agent.process(message)
        return responses

network = AgentNetwork()
network.register(researcher)
network.register(coder)
network.register(reviewer)
```

## 6. 模式选型指南

> 🔄 更新于 2026-04-18

| 模式 | 复杂度 | 适用场景 | 优点 | 缺点 |
|------|--------|---------|------|------|
| Supervisor | 低 | 任务明确、角色固定 | 简单可控 | 主管是瓶颈 |
| Hierarchical | 中 | 大型团队、多职能 | 可扩展 | 层级延迟 |
| Swarm | 中 | 客服、动态路由 | 灵活自主 | 难以调试 |
| Network | 高 | 复杂协作、头脑风暴 | 最灵活 | 消息爆炸 |

> **2026 架构趋势**：
> - **A2A v1.0 + MCP 双协议栈**：MCP 连接 Agent→工具，A2A 连接 Agent→Agent，两者互补形成完整的多 Agent 通信基础设施
> - **跨组织 Agent 协作**：A2A 的 Agent Card 发现机制 + OAuth2/API Key 认证，使不同厂商/框架的 Agent 可以跨组织边界协作
> - **Swarm 模式标准化**：OpenAI Agents SDK 的 Handoff 机制 + A2A 的 Task 生命周期管理，让 Swarm 模式从框架特定走向标准化
> - **Dapr Agents v1.0 GA**：CNCF 托管的分布式 Agent 运行时，为 Network 模式提供生产级基础设施（事件驱动、状态管理、Actor 模型）
## 🎬 推荐视频资源

- [DeepLearning.AI - Multi AI Agent Systems with crewAI](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/) — 多Agent系统实战（免费）
- [DeepLearning.AI - AI Agentic Design Patterns with AutoGen](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/) — Agentic设计模式（免费）
