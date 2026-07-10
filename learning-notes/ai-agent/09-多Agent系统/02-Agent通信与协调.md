# Agent 通信与协调
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 消息传递模式

```
直接消息：Agent A → Agent B（点对点）
广播消息：Agent A → All Agents（一对多）
发布订阅：Agent A → Topic → 订阅者（解耦）
共享状态：Agent A → State Store ← Agent B（间接通信）
```

## 2. 共享状态通信

```python
from typing import TypedDict, Annotated
from operator import add
from langgraph.graph import StateGraph, START, END

class SharedState(TypedDict):
    """多 Agent 共享状态"""
    messages: Annotated[list, add]
    research_data: dict
    code_artifacts: list[str]
    review_comments: list[str]
    status: str

def researcher(state: SharedState) -> dict:
    """研究 Agent 写入研究数据"""
    data = perform_research(state["messages"][-1])
    return {"research_data": data, "status": "research_done"}

def developer(state: SharedState) -> dict:
    """开发 Agent 读取研究数据，写入代码"""
    code = generate_code(state["research_data"])
    return {"code_artifacts": [code], "status": "code_done"}

def reviewer(state: SharedState) -> dict:
    """审查 Agent 读取代码，写入评审意见"""
    comments = review_code(state["code_artifacts"][-1])
    return {"review_comments": comments, "status": "review_done"}

graph = StateGraph(SharedState)
graph.add_node("researcher", researcher)
graph.add_node("developer", developer)
graph.add_node("reviewer", reviewer)
graph.add_edge(START, "researcher")
graph.add_edge("researcher", "developer")
graph.add_edge("developer", "reviewer")
graph.add_edge("reviewer", END)
```

## 3. 任务委派与 Handoff

```python
from agents import Agent, handoff

# OpenAI Agents SDK Handoff 机制
support_agent = Agent(
    name="客服 Agent",
    instructions="处理一般咨询。复杂技术问题转交技术专家。",
    handoffs=[
        handoff(
            agent=tech_expert,
            tool_name="transfer_to_tech",
            tool_description="将复杂技术问题转交给技术专家",
        ),
        handoff(
            agent=billing_expert,
            tool_name="transfer_to_billing",
            tool_description="将账单问题转交给账单专家",
        ),
    ],
)

# Handoff 时传递上下文
from agents import handoff

def create_handoff_with_context(target_agent, summary_fn):
    """带上下文摘要的 Handoff"""
    return handoff(
        agent=target_agent,
        tool_name=f"transfer_to_{target_agent.name}",
        on_handoff=lambda ctx: summary_fn(ctx.messages),  # 传递摘要
    )
```

## 4. 冲突解决

```python
class ConflictResolver:
    """多 Agent 意见冲突解决器"""

    def __init__(self, llm):
        self.llm = llm

    async def resolve_by_voting(self, opinions: dict[str, str]) -> str:
        """投票法：多数意见胜出"""
        prompt = f"""以下是多个 Agent 的意见：
{chr(10).join(f'- {name}: {opinion}' for name, opinion in opinions.items())}

请分析各方观点，选择最合理的意见并说明理由。"""
        return (await self.llm.ainvoke(prompt)).content

    async def resolve_by_synthesis(self, opinions: dict[str, str]) -> str:
        """综合法：融合多方意见"""
        prompt = f"""以下是多个 Agent 的不同观点：
{chr(10).join(f'- {name}: {opinion}' for name, opinion in opinions.items())}

请综合各方观点，生成一个融合了各方优点的最终方案。"""
        return (await self.llm.ainvoke(prompt)).content

resolver = ConflictResolver(llm)
final = await resolver.resolve_by_synthesis({
    "Agent A": "应该使用微服务架构",
    "Agent B": "单体架构更适合当前阶段",
    "Agent C": "建议模块化单体，后续拆分",
})
```

## 5. A2A 协议实践

> 🔄 更新于 2026-07-10

<!-- version-check: A2A v1.0.0（正式稳定版，已取代 v0.3.0 Draft）, 150+ 组织, Linux Foundation 托管, checked 2026-07-10 -->
<!-- 修复于 2026-07-10: A2A 已从 v0.3.0 Draft 正式升级到 v1.0.0 稳定版；JSON-RPC 方法名从旧版 tasks/send、tasks/get 更新为 v1.0 规范方法名 SendMessage、GetTask -->

```python
# Google A2A 协议：Agent 间标准化通信
# A2A v1.0.0 稳定版，Linux Foundation 托管，150+ 组织支持
import httpx

# Agent Card（能力描述）
agent_card = {
    "name": "data-analyst",
    "description": "数据分析 Agent，支持 SQL 查询和可视化",
    "url": "https://agent.example.com",
    "capabilities": {
        "streaming": True,
        "pushNotifications": False,
    },
    "skills": [
        {"id": "sql_query", "name": "SQL 查询", "description": "执行数据库查询"},
        {"id": "visualize", "name": "数据可视化", "description": "生成图表"},
    ],
    "authentication": {
        "schemes": ["oauth2", "apiKey"],  # v0.3.0 新增安全认证
    },
}

# 发送任务（v1.0 JSON-RPC 绑定：方法名为 SendMessage，旧版别名 message/send、tasks/send 已废弃）
async def send_a2a_task(agent_url: str, task: dict):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            agent_url,  # v1.0 JSON-RPC 绑定为单一端点，不再是 /tasks
            json={
                "jsonrpc": "2.0",
                "id": "req-001",
                "method": "SendMessage",
                "params": {
                    "message": {
                        "role": "user",
                        "parts": [{"kind": "text", "text": task["description"]}],
                    }
                },
            },
        )
        return response.json()

# 查询任务状态（v1.0 方法名为 GetTask，旧版别名 tasks/get 已废弃）
async def check_task_status(agent_url: str, task_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            agent_url,
            json={
                "jsonrpc": "2.0",
                "id": "req-002",
                "method": "GetTask",
                "params": {"id": task_id},
            },
        )
        return response.json()  # status: submitted/working/completed/failed
```

> **A2A 2026 生态现状**：
> - **v1.0.0 正式稳定版**（已取代此前 v0.3.0 Draft）：Linux Foundation 托管，150+ 组织支持（AWS、Cisco、Microsoft、Salesforce、SAP 等）（[来源](https://letsdatascience.com/blog/a2a-protocol-agent-to-agent)）
> - **三种协议绑定**：JSON-RPC 2.0（方法名如 `SendMessage`/`GetTask`）、gRPC、HTTP+JSON/REST（如 `POST /message:send`），能力在 Agent Card 的 `supportedInterfaces[]` 中声明
> - **官方 SDK**：Python、Go、JavaScript、Java、.NET 五种语言
> - **MCP + A2A 互补**：MCP 处理 Agent→工具连接，A2A 处理 Agent→Agent 委派和跨组织协作
> - **JetBrains Central**（2026-03）：首个以多 Agent 互操作为核心的编排平台
> - **主流框架集成**：CrewAI、Google ADK、Dapr Agents 等均已内置 A2A 支持
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Multi AI Agent Systems with crewAI](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/) — 多Agent通信实战（免费）
- [LangChain - Multi-Agent Collaboration](https://www.youtube.com/watch?v=9BPCV5TYPmg) — 多Agent协作模式

### 📺 B站
- [多Agent系统架构讲解](https://www.bilibili.com/video/BV1Bm421N7BH) — 多Agent协作中文教程
