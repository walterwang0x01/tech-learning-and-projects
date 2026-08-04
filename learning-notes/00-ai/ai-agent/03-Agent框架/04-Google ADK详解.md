# Google ADK 详解
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

> 🔄 更新于 2026-04-16

<!-- version-check: Google ADK v1.28+, Python v1.0.0 stable, checked 2026-04-16 -->
<!-- 修复于 2026-04-16: ADK 版本从 v1.22+ 更新到 v1.28+ -->

Google Agent Development Kit（ADK）是 Google 推出的开源、代码优先的 Agent 开发框架。深度集成 Gemini 模型生态，原生支持 A2A 协议和 MCP，提供从原型到生产的完整路径。Python ADK 于 2025 年 5 月发布 v1.0.0 稳定版，目前已迭代到 v1.28+（约双周发布一次）。支持 YAML 定义 Agent（Agent Config）、可视化拖拽 UI、Cloud Run 一键部署，SDK 覆盖 Python/TypeScript/Go/Java 四种语言。A2A 协议已内置到 ADK 中，使用 ADK 构建的 Agent 自动获得 A2A 通信能力。来源：[Google Developers Blog](https://developers.googleblog.com/en/agents-adk-agent-engine-a2a-enhancements-google-io/)、[PyPI](https://pypi.org/project/google-adk/)、[PyPI Stats](https://pypistats.org/packages/google-adk)

```
┌──────────────────── Google ADK ────────────────────┐
│                                                     │
│  Agent 类型                    工具系统              │
│  ├─ LlmAgent（核心）          ├─ FunctionTool       │
│  ├─ SequentialAgent           ├─ Google Search      │
│  ├─ ParallelAgent             ├─ Code Execution     │
│  └─ LoopAgent                 ├─ MCP Tool           │
│                               └─ A2A Tool           │
│  ┌─────────────────────────────────────────────┐   │
│  │  Runner → Session → Memory → Deployment     │   │
│  └─────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────┘
```

## 2. 核心概念

### 2.1 Agent / Tool / Runner / Session

```python
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService

# Agent：核心智能体
<!-- version-check: gemini-3-flash, checked 2026-04-16 -->
agent = Agent(
    name="helper",
    model="gemini-3-flash",
    description="通用助手",
    instruction="你是一个有帮助的助手，用中文回答。",
    tools=[],
)

# Runner：执行引擎
session_service = InMemorySessionService()
runner = Runner(agent=agent, app_name="my_app", session_service=session_service)

# Session：会话管理
from google.genai import types
result = await runner.run(
    user_id="user-1",
    session_id="session-1",
    new_message=types.Content(
        role="user", parts=[types.Part(text="你好")]
    ),
)
for event in result:
    if event.is_final_response():
        print(event.content.parts[0].text)
```

### 2.2 Agent 类型

```python
from google.adk.agents import (
    Agent as LlmAgent,
    SequentialAgent,
    ParallelAgent,
    LoopAgent,
)

# LlmAgent — 核心 Agent，由 LLM 驱动
researcher = LlmAgent(
    name="researcher",
    model="gemini-3-flash",
    instruction="搜索并收集信息",
    tools=[google_search],
)

# SequentialAgent — 按顺序执行子 Agent
pipeline = SequentialAgent(
    name="content_pipeline",
    sub_agents=[researcher, writer, editor],
)

# ParallelAgent — 并行执行子 Agent
parallel = ParallelAgent(
    name="multi_search",
    sub_agents=[news_searcher, paper_searcher, social_searcher],
)

# LoopAgent — 循环执行直到满足条件
iterative = LoopAgent(
    name="refiner",
    sub_agents=[drafter, critic],
    max_iterations=5,
)
```

## 3. 工具系统

```python
from google.adk.tools import FunctionTool, google_search, code_execution

# FunctionTool — 自定义 Python 函数
def calculate_bmi(weight_kg: float, height_m: float) -> dict:
    """计算 BMI 指数"""
    bmi = weight_kg / (height_m ** 2)
    category = "正常" if 18.5 <= bmi < 24 else "偏高" if bmi >= 24 else "偏低"
    return {"bmi": round(bmi, 1), "category": category}

bmi_tool = FunctionTool(func=calculate_bmi)

# 内置工具
agent = LlmAgent(
    name="smart_agent",
    model="gemini-3-flash",
    instruction="你可以搜索信息和执行代码。",
    tools=[google_search, code_execution, bmi_tool],
)
```

### MCP 工具集成

```python
from google.adk.tools.mcp import MCPTool

# 接入 MCP Server 作为工具
mcp_github = MCPTool(
    server_command="npx",
    server_args=["-y", "@modelcontextprotocol/server-github"],
    env={"GITHUB_TOKEN": "ghp_xxx"},
)

agent = LlmAgent(
    name="dev_agent",
    model="gemini-3-flash",
    tools=[mcp_github],
)
```

### A2A 协议原生支持

```python
from google.adk.tools.a2a import A2ATool

# 连接远程 A2A Agent
remote_agent = A2ATool(
    agent_url="https://remote-agent.example.com/.well-known/agent.json",
)

coordinator = LlmAgent(
    name="coordinator",
    model="gemini-3-flash",
    instruction="协调远程 Agent 完成任务。",
    tools=[remote_agent],
)
```

## 4. 多 Agent 编排与上下文

```python
from google.adk.agents import Agent, SequentialAgent

# 子 Agent 通过 output_key 传递数据
planner = Agent(
    name="planner",
    model="gemini-3-flash",
    instruction="将任务分解为步骤，输出 JSON 格式的计划。",
    output_key="plan",  # 结果存入 session state
)

executor = Agent(
    name="executor",
    model="gemini-3-flash",
    instruction="根据 {plan} 执行每个步骤。",  # 引用上游输出
    tools=[google_search, code_execution],
    output_key="result",
)

pipeline = SequentialAgent(
    name="task_pipeline",
    sub_agents=[planner, executor],
)
```

### 上下文层级

```
Static Context  — Agent instruction 中的固定信息
Turn Context    — 当前对话轮次的临时数据
User Context    — 跨会话的用户偏好和记忆
Cache Context   — 工具调用结果缓存，减少重复调用
```

## 5. Vertex AI Agent Engine 部署

```python
from google.adk.deployment import VertexAIAgentEngine

# 部署到 Vertex AI
engine = VertexAIAgentEngine(
    project_id="my-gcp-project",
    location="us-central1",
)

engine.deploy(
    agent=pipeline,
    display_name="task-pipeline-agent",
    scaling={"min_replicas": 1, "max_replicas": 10},
)

# 调用已部署的 Agent
response = engine.invoke(
    agent_name="task-pipeline-agent",
    message="分析 2025 年 Q3 的销售数据趋势",
    session_id="session-001",
)
```

## 6. 音视频流与 Agent Garden

```python
# 双向音视频流（Gemini 2.0 Live API）
from google.adk.streaming import LiveAgent

live_agent = LiveAgent(
    name="video_assistant",
    model="gemini-3-flash",
    instruction="你可以看到用户的视频流并实时回答问题。",
    modalities=["audio", "video"],
)

# Agent Garden — 官方示例 Agent 集合
# https://github.com/google/adk-samples
# 包含：旅行规划、代码审查、数据分析等示例 Agent
```

## 7. 适用场景

| 场景 | 推荐 Agent 类型 |
|------|----------------|
| 简单问答 | LlmAgent |
| 流水线任务 | SequentialAgent |
| 信息聚合 | ParallelAgent |
| 迭代优化 | LoopAgent |
| 跨服务协作 | A2ATool + LlmAgent |
| 生产部署 | Vertex AI Agent Engine |
## 🎬 推荐视频资源

- [Google Cloud - Agent Development Kit](https://www.youtube.com/watch?v=E8pMFNox4Lc) — Google ADK官方介绍
- [Google Cloud - Building AI Agents with ADK](https://www.youtube.com/watch?v=3Vy0V3sBhAo) — ADK实战教程
