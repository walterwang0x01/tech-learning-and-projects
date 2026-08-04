# Google ADK 与 Bedrock Agents
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Google ADK 概述

Google Agent Development Kit（ADK）是 Google 推出的开源 Agent 开发框架，深度集成 Gemini 模型和 Google 生态。

```python
from google.adk.agents import Agent
from google.adk.tools import google_search, code_execution

# 创建基础 Agent
<!-- version-check: gemini-3-flash, checked 2026-04-16 -->
agent = Agent(
    name="research_agent",
    model="gemini-3-flash",
    description="一个能搜索和分析信息的研究助手",
    instruction="""你是一位研究助手。
    1. 使用搜索工具获取最新信息
    2. 分析并总结关键发现
    3. 用中文回答""",
    tools=[google_search, code_execution],
)

# 运行 Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

runner = Runner(
    agent=agent,
    app_name="research_app",
    session_service=InMemorySessionService(),
)

result = await runner.run(
    user_id="user-1",
    session_id="session-1",
    new_message="AI Agent 2025 年最新趋势是什么？",
)
```

## 2. ADK 多 Agent 编排

```python
from google.adk.agents import Agent, SequentialAgent, LoopAgent

# 子 Agent 定义
planner = Agent(
    name="planner",
    model="gemini-3-flash",
    instruction="将用户任务分解为具体步骤",
)

executor = Agent(
    name="executor",
    model="gemini-3-flash",
    instruction="执行计划中的每个步骤",
    tools=[google_search, code_execution],
)

reviewer = Agent(
    name="reviewer",
    model="gemini-3-flash",
    instruction="审查执行结果，决定是否需要改进",
)

# 顺序编排
pipeline = SequentialAgent(
    name="research_pipeline",
    sub_agents=[planner, executor, reviewer],
)

# 循环编排（直到满足条件）
iterative = LoopAgent(
    name="iterative_improver",
    sub_agents=[executor, reviewer],
    max_iterations=3,
)
```

## 3. Amazon Bedrock Agents

Bedrock Agents 是 AWS 的全托管 Agent 服务，无需管理基础设施。

```python
import boto3

bedrock_agent = boto3.client("bedrock-agent", region_name="us-east-1")

# 创建 Agent
response = bedrock_agent.create_agent(
    agentName="customer-service-agent",
<!-- version-check: claude-sonnet-4-6-20260401, checked 2026-04-16 -->
    foundationModel="anthropic.claude-sonnet-4-6-20260401-v1:0",
    instruction="""你是客服助手。
    - 查询订单状态
    - 处理退换货请求
    - 回答产品问题""",
    idleSessionTTLInSeconds=1800,
)

# 定义 Action Group（工具）
bedrock_agent.create_agent_action_group(
    agentId=response["agent"]["agentId"],
    actionGroupName="order-management",
    apiSchema={
        "payload": """{
            "openapi": "3.0.0",
            "paths": {
                "/orders/{orderId}": {
                    "get": {
                        "summary": "查询订单状态",
                        "parameters": [{"name": "orderId", "in": "path", "required": true}]
                    }
                }
            }
        }"""
    },
    actionGroupExecutor={"lambda": "arn:aws:lambda:us-east-1:123:function:order-api"},
)
```

```python
# 调用 Bedrock Agent
bedrock_runtime = boto3.client("bedrock-agent-runtime")

response = bedrock_runtime.invoke_agent(
    agentId="AGENT_ID",
    agentAliasId="ALIAS_ID",
    sessionId="session-123",
    inputText="查询订单 ORD-2025-001 的状态",
)

# 流式读取响应
for event in response["completion"]:
    if "chunk" in event:
        print(event["chunk"]["bytes"].decode(), end="")
```

## 4. 云厂商 Agent 方案对比

| 特性 | Google ADK | Bedrock Agents | Azure AI Agent |
|------|-----------|----------------|----------------|
| 类型 | 开源框架 | 全托管服务 | 全托管服务 |
| 模型 | Gemini 为主 | Claude/Llama/Nova | GPT/开源 |
| 工具定义 | Python 函数 | OpenAPI Schema | Function Calling |
| 多 Agent | 原生支持 | 协作模式 | AutoGen 集成 |
| MCP 支持 | 原生 | 有限 | 有限 |
| 部署 | 自管理/Vertex | 全托管 | 全托管 |
| 适用场景 | Google 生态 | AWS 生态 | Azure 生态 |
| 成本模型 | 按 API 调用 | 按调用+步骤 | 按调用 |
## 🎬 推荐视频资源

### 🌐 YouTube
- [Google Cloud - ADK Overview](https://www.youtube.com/watch?v=E8pMFNox4Lc) — Google ADK官方介绍
- [AWS re:Invent - Bedrock Agents](https://www.youtube.com/watch?v=F8NKVhkZZWI) — Bedrock Agents讲解

### 📖 官方文档
- [Google ADK Docs](https://google.github.io/adk-docs/) — ADK官方文档
