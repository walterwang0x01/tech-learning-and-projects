# OpenAI Agents SDK
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

OpenAI Agents SDK 是 OpenAI 官方推出的 Agent 开发工具包，核心设计理念是"少量代码，快速构建"。适合快速原型开发和 GPT 模型生态内的 Agent 构建。

核心概念：Agent（智能体）、Handoff（交接）、Guardrail（护栏）、Tracing（追踪）。

## 2. 基本使用

```python
from agents import Agent, Runner, function_tool

# 定义工具
@function_tool
def get_weather(city: str) -> str:
    """获取城市天气"""
    return f"{city}: 25°C, 晴天"

@function_tool
def search_flights(origin: str, destination: str, date: str) -> str:
    """搜索航班"""
    return f"{origin} → {destination} ({date}): 3个航班可选"

<!-- version-check: gpt-5.2, checked 2026-04-16 -->
# 创建 Agent
travel_agent = Agent(
    name="旅行助手",
    instructions="你是一个旅行规划助手，帮助用户规划旅行行程。",
    tools=[get_weather, search_flights],
    model="gpt-5.2",
)

# 运行
result = Runner.run_sync(travel_agent, "我想下周去东京旅行，帮我看看天气和航班")
print(result.final_output)
```

## 3. Handoff（Agent 间交接）

```python
from agents import Agent, Runner

# 专业 Agent
billing_agent = Agent(
    name="账单专员",
    instructions="你负责处理账单和支付相关问题。",
    tools=[query_billing, process_refund],
    model="gpt-5.2",
)

tech_agent = Agent(
    name="技术支持",
    instructions="你负责处理技术问题和故障排查。",
    tools=[check_system_status, create_ticket],
    model="gpt-5.2",
)

# 主 Agent（路由）
triage_agent = Agent(
    name="客服主管",
    instructions="""你是客服主管，根据用户问题类型转接到对应专员：
    - 账单/支付问题 → 转接账单专员
    - 技术/故障问题 → 转接技术支持""",
    handoffs=[billing_agent, tech_agent],  # 可交接的 Agent
    model="gpt-5.2",
)

# 运行（自动路由到合适的 Agent）
result = Runner.run_sync(triage_agent, "我的订单被重复扣款了")
# → 自动交接给 billing_agent 处理
```

## 4. Guardrail（护栏）

```python
from agents import Agent, InputGuardrail, OutputGuardrail, GuardrailFunctionOutput
from pydantic import BaseModel

class SafetyCheck(BaseModel):
    is_safe: bool
    reason: str

# 输入护栏
@InputGuardrail
async def check_input_safety(ctx, agent, input_text):
    """检查用户输入是否安全"""
    result = await Runner.run(safety_checker, input_text)
    check = result.final_output_as(SafetyCheck)
    return GuardrailFunctionOutput(
        output_info=check,
        tripwire_triggered=not check.is_safe,
    )

# 输出护栏
@OutputGuardrail
async def check_output_pii(ctx, agent, output_text):
    """检查输出是否包含 PII"""
    has_pii = detect_pii(output_text)
    return GuardrailFunctionOutput(
        output_info={"has_pii": has_pii},
        tripwire_triggered=has_pii,
    )

agent = Agent(
    name="安全助手",
    instructions="...",
    model="gpt-5.2",
    input_guardrails=[check_input_safety],
    output_guardrails=[check_output_pii],
)
```

## 5. Tracing（追踪）

```python
from agents import trace, Runner

# 自动追踪（默认开启）
result = Runner.run_sync(agent, "你好")
# 追踪数据自动发送到 OpenAI Dashboard

# 自定义追踪
with trace("custom_workflow"):
    result1 = await Runner.run(agent1, "步骤1")
    result2 = await Runner.run(agent2, result1.final_output)

# 集成外部追踪（LangSmith/LangFuse 等）
from agents.tracing import set_trace_processors
set_trace_processors([custom_processor])
```

## 6. 适用场景

```
✅ 适合：
- 快速原型开发（100行代码内构建 Agent）
- OpenAI 模型生态内的应用
- 简单的多 Agent 交接场景
- 需要输入/输出护栏的场景

❌ 不适合：
- 需要模型无关性的项目
- 复杂的图结构工作流
- 需要精细状态管理的场景
```

> 🔄 更新于 2026-04-16

## 7. 2026 年 4 月重大更新：沙箱与 Harness 架构

<!-- version-check: OpenAI Agents SDK 2026-04-15 update, sandbox + harness, checked 2026-04-16 -->

OpenAI 于 2026 年 4 月 15 日发布 Agents SDK 重大更新，引入沙箱执行和增强的 harness 架构，将 SDK 从原型工具推向企业级生产平台。来源：[TechCrunch](https://techcrunch.com/2026/04/15/openai-updates-its-agents-sdk-to-help-enterprises-build-safer-more-capable-agents/)、[OpenAI 社区](https://community.openai.com/t/the-next-evolution-of-the-agents-sdk/1379072)

### 核心变化

```
Agents SDK 架构演进：
├─ Harness（编排层）
│   ├─ instructions — Agent 指令
│   ├─ tools — 工具注册
│   ├─ approvals — 审批流程
│   ├─ tracing — 追踪
│   ├─ handoffs — Agent 交接
│   └─ resume bookkeeping — 恢复记账
│
├─ Sandbox（沙箱执行）
│   ├─ 隔离的计算环境
│   ├─ 文件操作、命令执行、代码编辑
│   └─ 类似 Codex 风格的 Agent 行为
│
└─ 关键理念：Harness 与 Compute 分离
    ├─ Harness 负责编排和控制
    └─ Sandbox 负责安全执行
```

### 企业级特性

```
新增能力：
├─ 沙箱执行 — Agent 在受控环境中运行，防止意外行为
├─ 增强 Harness — 标准化的 Agent 基础设施
├─ 审批工作流 — 敏感操作需人工确认
├─ 恢复机制 — 中断后可恢复执行
└─ 生产级追踪 — 完整的执行链路追踪
```
## 🎬 推荐视频资源

- [OpenAI - Agents SDK Introduction](https://www.youtube.com/watch?v=JhCl-GeT4jw) — OpenAI官方Agents SDK介绍
- [DeepLearning.AI - Building Agentic RAG with LlamaIndex](https://www.deeplearning.ai/short-courses/building-agentic-rag-with-llamaindex/) — Agentic RAG实战（免费）
