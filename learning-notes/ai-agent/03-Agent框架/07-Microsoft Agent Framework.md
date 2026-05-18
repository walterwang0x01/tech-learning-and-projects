# Microsoft Agent Framework
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

> 🔄 更新于 2026-04-16（2026-05-19 增补 1.0 GA 信息）

<!-- version-check: Microsoft Agent Framework 1.0 GA (2026-04-03), MCP + A2A native, checked 2026-05-19 -->

Microsoft Agent Framework 是微软于 2026 年推出的统一 Agent 开发框架，由 Semantic Kernel（企业级 AI 编排）和 AutoGen（多 Agent 研究框架）合并而来。融合了 SK 的类型安全、遥测、安全能力与 AutoGen 的多 Agent 协作模式。**2026-04-03 正式发布 1.0 GA**（生产就绪），合并了两个前任项目的 75K+ GitHub Stars，承诺长期支持（LTS）和稳定 API。原生支持 MCP（工具协议）+ A2A（Agent 间协议），首发支持 Python 和 .NET 两种语言（Java 路线图后续公布）。来源：[Microsoft DevBlogs — Agent Framework 1.0](https://devblogs.microsoft.com/agent-framework/microsoft-agent-framework-version-1-0/)、[The Future of Agentic AI: Inside Microsoft Agent Framework 1.0](https://techcommunity.microsoft.com/blog/azuredevcommunityblog/the-future-of-agentic-ai-inside-microsoft-agent-framework-1-0/4510698)

```
┌─────────────── Microsoft Agent Framework ───────────────┐
│                                                          │
│  Semantic Kernel 基因          AutoGen 基因               │
│  ├─ 类型安全 Skills/Plugins   ├─ 多 Agent 对话模式        │
│  ├─ 企业级遥测               ├─ 群聊编排                  │
│  ├─ 安全与合规               ├─ 代码执行沙箱              │
│  └─ Connector 生态           └─ 人机协作循环              │
│                                                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │          Azure AI Foundry 集成部署                 │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

## 2. 核心概念

### 2.1 Agent 类型

```python
from microsoft.agents import (
    Agent,
    ChatCompletionAgent,
    OpenAIAssistantAgent,
    AzureAIAgent,
)

# ChatCompletionAgent — 最常用，基于 Chat Completions API
<!-- version-check: gpt-5.2, checked 2026-04-16 -->
agent = ChatCompletionAgent(
    name="assistant",
    instructions="你是一个有帮助的助手。",
    model="gpt-5.2",
    plugins=[search_plugin, math_plugin],
)

# OpenAIAssistantAgent — 基于 OpenAI Assistants API（支持文件、代码解释器）
assistant = OpenAIAssistantAgent(
    name="data_analyst",
    instructions="你是数据分析师，使用代码解释器分析数据。",
    model="gpt-5.2",
    enable_code_interpreter=True,
)

# AzureAIAgent — Azure AI Foundry 托管 Agent
azure_agent = AzureAIAgent(
    name="enterprise_bot",
    project_endpoint="https://xxx.services.ai.azure.com",
    model="gpt-5.2",
)
```

### 2.2 Skills/Plugins 系统（源自 Semantic Kernel）

```python
from microsoft.agents import plugin, skill

# 定义 Plugin（工具集合）
@plugin
class WeatherPlugin:
    """天气查询插件"""

    @skill
    def get_current_weather(self, city: str) -> str:
        """获取当前天气"""
        return f"{city}: 26°C, 多云"

    @skill
    def get_forecast(self, city: str, days: int = 3) -> str:
        """获取天气预报"""
        return f"{city} 未来{days}天：晴→多云→小雨"

# 注册到 Agent
agent = ChatCompletionAgent(
    name="weather_bot",
    instructions="你是天气助手。",
    plugins=[WeatherPlugin()],
)

response = await agent.invoke("北京明天天气怎么样？")
```

## 3. 图编排（AgentGroupChat / GraphFlow）

```python
from microsoft.agents import ChatCompletionAgent
from microsoft.agents.orchestration import AgentGroupChat, GraphFlow

# 定义多个 Agent
planner = ChatCompletionAgent(name="planner", instructions="你负责制定计划。")
coder = ChatCompletionAgent(name="coder", instructions="你负责编写代码。")
tester = ChatCompletionAgent(name="tester", instructions="你负责测试和审查。")

# 方式一：AgentGroupChat（自由讨论）
group_chat = AgentGroupChat(
    agents=[planner, coder, tester],
    max_rounds=10,
    termination_condition=lambda msg: "APPROVED" in msg.content,
)
result = await group_chat.invoke("开发一个用户注册 API")

# 方式二：GraphFlow（图结构编排）
flow = GraphFlow()
flow.add_node("plan", planner)
flow.add_node("code", coder)
flow.add_node("test", tester)
flow.add_edge("plan", "code")
flow.add_edge("code", "test")
flow.add_conditional_edge("test", lambda r: "code" if "bug" in r else "end")

result = await flow.run("开发一个用户注册 API")
```

## 4. MCP 支持

```python
from microsoft.agents import ChatCompletionAgent
from microsoft.agents.mcp import MCPToolProvider

# 通过 MCP 接入外部工具
mcp_tools = MCPToolProvider(
    server_command="npx",
    server_args=["-y", "@modelcontextprotocol/server-github"],
    env={"GITHUB_TOKEN": "ghp_xxx"},
)

agent = ChatCompletionAgent(
    name="dev_assistant",
    instructions="你是开发助手，可以操作 GitHub。",
    tools=await mcp_tools.get_tools(),
)
```

## 5. .NET 支持

```csharp
using Microsoft.Agents;

var agent = new ChatCompletionAgent
{
    Name = "assistant",
    Instructions = "你是一个有帮助的助手。",
    model="gpt-5.2",
    Plugins = [new WeatherPlugin(), new SearchPlugin()],
};

var response = await agent.InvokeAsync("今天天气如何？");
Console.WriteLine(response.Content);
```

## 6. Azure AI Foundry 集成

```python
from microsoft.agents import AzureAIAgent

# 部署到 Azure AI Foundry
agent = AzureAIAgent.create(
    name="enterprise_agent",
    project_endpoint="https://myproject.services.ai.azure.com",
    model="gpt-5.2",
    plugins=[crm_plugin, erp_plugin],
    guardrails=["content_safety", "pii_filter"],
)

# 生产环境调用
response = await agent.invoke(
    message="查询客户 C-001 的最近订单",
    session_id="session-abc",
)
```

## 7. 从 SK / AutoGen 迁移

```
Semantic Kernel 迁移：
  Kernel + Plugin       → Agent + Plugin（API 基本兼容）
  KernelFunction        → @skill 装饰器
  Planner               → GraphFlow
  ChatCompletionService → ChatCompletionAgent

AutoGen 迁移：
  AssistantAgent        → ChatCompletionAgent
  GroupChat             → AgentGroupChat
  UserProxyAgent        → HumanAgent
  Code Executor         → CodeInterpreterTool
```

## 8. 适用场景

| 场景 | 推荐方式 |
|------|---------|
| 企业内部 Bot | AzureAIAgent + Plugins |
| 多 Agent 协作 | AgentGroupChat / GraphFlow |
| 代码分析任务 | OpenAIAssistantAgent + Code Interpreter |
| 跨语言团队 | Python + .NET 混合开发 |
| 快速原型 | ChatCompletionAgent + @skill |
## 🎬 推荐视频资源

### 🌐 YouTube
- [Microsoft - Semantic Kernel Tutorial](https://www.youtube.com/watch?v=pHksBVqH7uI) — Semantic Kernel教程
- [Microsoft - AutoGen Tutorial](https://www.youtube.com/watch?v=vU2S6dVf79M) — AutoGen框架教程

### 🎓 DeepLearning.AI（免费）
- [AI Agentic Design Patterns with AutoGen](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/) — AutoGen设计模式

### 📖 官方文档
- [Semantic Kernel Docs](https://learn.microsoft.com/en-us/semantic-kernel/) — 微软SK官方文档

## 9. Microsoft Agent Framework 1.0 GA 详解

> 🔄 更新于 2026-05-19

<!-- version-check: Microsoft Agent Framework 1.0 GA (2026-04-03), MCP + A2A native, checked 2026-05-19 -->

Microsoft Agent Framework 1.0 于 **2026-04-03 正式 GA**，与 Spring AI 2.0 / Microsoft Foundry Toolkit GA 一起，标志着 2026 Q2 是企业级 Agent 框架的爆发期。来源：[Microsoft Foundry Blog](https://devblogs.microsoft.com/foundry/)、[Digital Applied: Agent Framework 1.0 Guide](https://www.digitalapplied.com/blog/microsoft-agent-framework-1-0-dotnet-python-guide)

### 9.1 1.0 GA 关键事实

| 维度 | 内容 |
| ---- | ---- |
| GA 日期 | 2026-04-03 |
| 语言支持 | .NET（C# 优先）+ Python（首发） |
| 包名（统一） | `Microsoft.Agents.AI`（.NET）/ `microsoft-agents` 系列（Python） |
| 模型提供商 | Azure OpenAI / OpenAI / Anthropic Claude / Amazon Bedrock / Google Gemini / Ollama（一行换 provider）|
| 协议原生 | **MCP**（工具）+ **A2A**（Agent 间） — 1.0 内置而非插件 |
| 长期支持 | **从 GA 起承诺 LTS**，API 表面稳定 |
| 替代关系 | 取代 Semantic Kernel + AutoGen + Azure Prompt Flow（Prompt Flow 已宣告退役） |

> Prompt Flow 已被官方推荐迁移到 Agent Framework 1.0。来源：[Prompt flow is being retired](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/prompt-flow-is-being-retired/4513587)

### 9.2 1.0 风格的 Agent 创建（Python）

```python
# pip install microsoft-agents-ai==1.0.0
from microsoft.agents.ai import ChatAgent
from microsoft.agents.ai.providers import OpenAIChatClient

# Python 1.0 GA — 一行切换 provider，其余代码不变
chat_client = OpenAIChatClient(model="gpt-5.2")
# 想切到 Claude 只需：
# from microsoft.agents.ai.providers import AnthropicChatClient
# chat_client = AnthropicChatClient(model="claude-opus-4-7")

agent = ChatAgent(
    name="research_assistant",
    chat_client=chat_client,
    instructions="你是科研助手，回答问题时引用来源。",
)

# 直接调用，无需 message 列表手动维护
response = await agent.run("总结 transformers 架构。")
print(response.output_text)
```

### 9.3 MCP + A2A 原生支持

```python
# MCP：让 Agent 自动消费 MCP Server 提供的工具
from microsoft.agents.ai.tools import MCPServerTool

agent = ChatAgent(
    name="filesystem_agent",
    chat_client=chat_client,
    tools=[
        MCPServerTool.from_command("uvx mcp-server-filesystem"),
    ],
)

# A2A：把 Agent 暴露为 A2A 服务，被其他 Agent 调用
from microsoft.agents.ai.a2a import A2AServer

server = A2AServer(agent, capabilities=["research", "summarization"])
await server.serve(host="0.0.0.0", port=8080)
```

### 9.4 多 Agent 编排：从 AgentGroupChat 到 GraphFlow

1.0 把多 Agent 协作收敛到两类抽象：

- **`AgentGroupChat`**：保留 AutoGen 风格的"群聊"模式，适合开放式协作
- **`GraphFlow`**：声明式工作流图，适合结构化生产场景（与 LangGraph 思路类似）

```python
# GraphFlow 示例：planner → researcher → writer
from microsoft.agents.ai.workflow import GraphFlow

flow = (
    GraphFlow()
    .add_agent("planner", planner_agent)
    .add_agent("researcher", researcher_agent)
    .add_agent("writer", writer_agent)
    .add_edge("planner", "researcher")
    .add_edge("researcher", "writer")
)
await flow.run({"topic": "Agent 框架选型"})
```

### 9.5 与其他 Agent 框架的定位差异

| 框架 | 优势 | Agent Framework 1.0 对比 |
| ---- | ---- | ----------------------- |
| LangGraph 1.x | 图编排能力最强，生态最完整 | GraphFlow 思路对齐，但企业能力（Foundry / Azure App Service）原生 |
| Spring AI 2.0 | Java 生态、Spring Boot 一等公民 | .NET + Python 一等公民，Java 待补 |
| OpenAI Agents SDK | 与 OpenAI 模型最深绑定 | 6 大 provider 一行切换，无锁定 |
| CrewAI v1.14 | 角色化协作直观 | AgentGroupChat 提供类似能力 + 企业特性 |

### 9.6 选型建议

- **微软栈生产环境**：直接用 1.0 GA + Foundry + Azure App Service
- **Semantic Kernel 老项目**：参照官方 [迁移指南](https://devblogs.microsoft.com/agent-framework/migrate-your-semantic-kernel-and-autogen-projects-to-microsoft-agent-framework-release-candidate/) 升级
- **AutoGen 老项目**：迁移到 GraphFlow / AgentGroupChat
- **跨云 Agent**：1.0 的 6 provider 切换 + MCP + A2A 是当前选择最广的企业级 SDK
- **Java 项目**：暂时仍需用 Spring AI 2.0 / LangChain4j，等微软 Java SDK 路线图

### 9.7 待跟进项

- Java SDK 时间表（官方未公布）
- 1.1.x 路线图（流式工作流、嵌入式评估等）
- 与 Microsoft Foundry Toolkit GA 的协同（同期发布，工作流编排链路已打通）
