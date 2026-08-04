# AWS Strands Agents SDK 与 Bedrock AgentCore
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Strands Agents SDK 概述

> 🔄 更新于 2026-04-16

<!-- version-check: Strands Agents v1.0 (2025-07), 14M+ 下载, Strands Labs, checked 2026-04-16 -->

Strands Agents SDK 是 AWS 于 2025 年 5 月开源的 Python Agent 框架，7 月发布 v1.0 正式版并新增多 Agent 编排能力。核心理念是"模型驱动"——Agent 自主规划、推理并选择工具，开发者只需定义工具和目标。截至 2026 年，SDK 已被下载 1400 万+ 次。AWS 还推出了 Strands Labs 实验性项目，包含 Steering（引导）等前沿功能，支持活跃的开发者社区。同时支持 Python 和 TypeScript/JavaScript 两种语言。来源：[AWS Blog](https://aws.amazon.com/blogs/opensource/introducing-strands-labs-get-hands-on-today-with-state-of-the-art-experimental-approaches-to-agentic-development/)、[Strands Agents 官网](https://strandsagents.com/)

```
┌─────────────────────────────────────────────┐
│              Strands Agent                   │
│  ┌─────────┐  ┌──────────┐  ┌────────────┐ │
│  │  Model   │→│ Planning  │→│ Tool Select │ │
│  │ (Bedrock)│  │& Reasoning│  │& Execution │ │
│  └─────────┘  └──────────┘  └────────────┘ │
│       ↕            ↕              ↕          │
│  ┌─────────────────────────────────────────┐ │
│  │  Tools: @tool 装饰器定义的 Python 函数   │ │
│  └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

## 2. 基本 Agent 创建

```python
from strands import Agent, tool

# 用 @tool 装饰器定义工具
@tool
def get_weather(city: str) -> str:
    """获取指定城市的天气信息"""
    return f"{city}: 28°C, 晴天，湿度 65%"

@tool
def search_restaurants(city: str, cuisine: str = "local") -> str:
    """搜索城市中的餐厅"""
    return f"在{city}找到 5 家{cuisine}餐厅推荐"

# 创建 Agent — 极简 API
agent = Agent(
    tools=[get_weather, search_restaurants],
    system_prompt="你是一个旅行助手，帮助用户规划行程。",
)

# 直接调用
response = agent("我想去杭州旅行，帮我看看天气和推荐餐厅")
print(response)
```

## 3. 模型驱动方法

Strands 的核心设计：开发者不编排工作流，模型自主决定调用哪些工具、以什么顺序执行。

```python
from strands import Agent, tool
import boto3

@tool
def query_database(sql: str) -> str:
    """执行只读 SQL 查询"""
    # Agent 自主决定何时查询数据库
    return execute_readonly(sql)

@tool
def send_notification(user_id: str, message: str) -> str:
    """发送通知给用户"""
    return f"已通知用户 {user_id}"

# Agent 自主规划：分析问题 → 查询数据 → 通知用户
agent = Agent(
    tools=[query_database, send_notification],
    system_prompt="你是数据分析助手，分析数据并在发现异常时通知相关人员。",
    model="us.amazon.nova-premier-v1:0",  # 指定 Bedrock 模型
)

agent("检查过去 24 小时的订单数据，如果有异常波动请通知管理员 admin-001")
```

## 4. 多 Agent 编排（v1.0）

```python
from strands import Agent, tool
from strands.multiagent import GraphOrchestrator

# 定义专业 Agent
researcher = Agent(
    tools=[web_search, summarize],
    system_prompt="你是研究员，负责收集和整理信息。",
)

writer = Agent(
    tools=[generate_draft, check_grammar],
    system_prompt="你是写作专家，负责撰写高质量内容。",
)

reviewer = Agent(
    tools=[evaluate_quality],
    system_prompt="你是审稿人，负责审查内容质量并给出改进建议。",
)

# 图编排
orchestrator = GraphOrchestrator(
    agents={"researcher": researcher, "writer": writer, "reviewer": reviewer},
    edges=[
        ("researcher", "writer"),
        ("writer", "reviewer"),
    ],
)

result = orchestrator.run("撰写一篇关于量子计算最新进展的技术报告")
```

## 5. Amazon Bedrock AgentCore

Bedrock AgentCore（2025 年 10 月 GA）是 AWS 推出的托管运行时，用于部署和运行生产级 Agent。

```
┌─────────────────── AgentCore ───────────────────┐
│  ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │ Managed  │ │  Tool    │ │   Identity &     │ │
│  │ Memory   │ │  Access  │ │   Guardrails     │ │
│  ├──────────┤ ├──────────┤ ├──────────────────┤ │
│  │ 会话记忆  │ │ MCP/API  │ │ IAM / OAuth2    │ │
│  │ 长期记忆  │ │ Lambda   │ │ 内容过滤        │ │
│  └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌──────────────────────────────────────────────┐│
│  │         Observability（可观测性）              ││
│  │   CloudWatch Traces / Metrics / Logs         ││
│  └──────────────────────────────────────────────┘│
└─────────────────────────────────────────────────┘
```

### 部署到 AgentCore Runtime

```python
from strands import Agent
from strands.agentcore import deploy

agent = Agent(
    tools=[get_weather, search_restaurants],
    system_prompt="旅行助手",
)

# 一键部署到 AgentCore
deploy(
    agent=agent,
    runtime_name="travel-agent-prod",
    memory_config={"type": "managed", "ttl_days": 30},
    guardrails=["content-filter", "pii-detection"],
    identity={"auth_type": "iam", "allowed_roles": ["agent-caller"]},
)
```

## 6. Nova Act SDK（浏览器自动化）

```python
from nova_act import NovaAct

# Nova Act：AI 驱动的浏览器操作
with NovaAct(starting_page="https://www.example.com") as act:
    act.act("搜索框中输入 'AI Agent'")
    act.act("点击第一个搜索结果")
    act.act("提取页面主要内容")
    content = act.act("总结这个页面的关键信息")
    print(content.response)
```

## 7. 与其他云厂商方案对比

| 维度 | AWS Strands + AgentCore | Azure AI Agent | Google ADK + Vertex |
|------|------------------------|----------------|---------------------|
| 框架类型 | 开源 SDK + 托管运行时 | 托管服务 | 开源 SDK + 托管引擎 |
| 核心理念 | 模型驱动，极简 API | SK+AutoGen 融合 | 代码优先，多 Agent |
| 模型支持 | Bedrock 全模型 | GPT/开源 | Gemini 为主 |
| 工具定义 | @tool 装饰器 | Plugins/Skills | FunctionTool |
| 浏览器自动化 | Nova Act SDK | - | - |
| 部署 | AgentCore Runtime | Azure AI Foundry | Vertex AI Engine |
| 可观测性 | CloudWatch 集成 | App Insights | Cloud Trace |
## 🎬 推荐视频资源

### 🌐 YouTube
- [AWS - Bedrock Agents Tutorial](https://www.youtube.com/watch?v=F8NKVhkZZWI) — AWS Bedrock Agents官方教程
- [freeCodeCamp - AWS AI Services](https://www.youtube.com/watch?v=GWB9ApTPTv4) — AWS AI服务概览

### 📖 官方文档
- [AWS Strands Agents](https://strandsagents.com/) — Strands官方文档
- [AWS Bedrock Agents](https://docs.aws.amazon.com/bedrock/latest/userguide/agents.html) — Bedrock Agents文档
