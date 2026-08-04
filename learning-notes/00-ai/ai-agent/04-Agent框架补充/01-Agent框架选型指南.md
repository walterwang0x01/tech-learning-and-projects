# Agent 框架选型指南
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 框架全景

<!-- version-check: Agent 框架全景, checked 2026-05-05 -->

> 🔄 更新于 2026-05-05

```
┌─────────────────────────────────────────────────────────┐
│                 AI Agent 框架全景（2026）                  │
├──────────────┬──────────────┬──────────────┬────────────┤
│  Python 原生  │  云厂商       │  Java/TS     │  轻量级     │
│  LangGraph   │  AWS Strands │  Spring AI   │  smolagents│
│  CrewAI      │  Google ADK  │  Vercel SDK  │  PydanticAI│
│  LlamaIndex  │  MS Agent FW │  Dapr Agents │  Agno      │
│  OpenAI SDK  │  Bedrock     │              │            │
└──────────────┴──────────────┴──────────────┴────────────┘
```

## 2. 决策树

```
你的场景是什么？

快速原型/PoC？
├─ Python → OpenAI Agents SDK（最简单）
├─ TypeScript → Vercel AI SDK
└─ 多 Agent 协作 → CrewAI（角色定义直观）

复杂生产工作流？
├─ 需要精细控制 → LangGraph（图编排，行业标准）
├─ 数据/RAG 密集 → LlamaIndex Workflows
└─ 需要评估迭代 → LangGraph + LangSmith

云原生部署？
├─ AWS → Strands Agents + Bedrock AgentCore
├─ GCP → Google ADK + Vertex AI
├─ Azure → Microsoft Agent Framework
└─ 多云 → LangGraph（云无关）

企业级需求？
├─ Java 团队 → Spring AI
├─ .NET 团队 → Microsoft Agent Framework
├─ 微服务架构 → Dapr Agents
└─ 类型安全 Python → PydanticAI

极简主义？
├─ 最少代码 → smolagents（HuggingFace）
├─ 高性能 → Agno（异步优先）
└─ 类型安全 → PydanticAI
```

## 3. 综合对比矩阵

| 框架           | 语言    | 学习曲线 | 生产就绪 | 多Agent | MCP | 模型锁定 | 社区  |
|---------------|---------|---------|---------|---------|-----|---------|-------|
| LangGraph     | Python  | ★★★    | ★★★★★ | ✅      | ✅  | 无      | 最大  |
| CrewAI        | Python  | ★★     | ★★★★  | ✅ 核心 | ✅  | 无      | 大    |
| OpenAI SDK    | Python  | ★      | ★★★★  | ✅      | ❌  | OpenAI  | 大    |
| Google ADK    | Python  | ★★     | ★★★★  | ✅      | ✅  | 无*     | 中    |
| AWS Strands   | Python  | ★★     | ★★★★  | ❌      | ✅  | 无      | 中    |
| MS Agent FW   | .NET    | ★★★    | ★★★★  | ✅      | ✅  | 无      | 中    |
| LlamaIndex    | Python  | ★★     | ★★★★  | ✅      | ✅  | 无      | 大    |
| PydanticAI    | Python  | ★★     | ★★★★  | ✅      | ✅  | 无      | 大    |
| Agno          | Python  | ★      | ★★★   | ✅      | ✅  | 无      | 小    |
| smolagents    | Python  | ★      | ★★    | ✅      | ✅  | 无      | 中    |
| Spring AI     | Java    | ★★     | ★★★★  | ❌      | ✅  | 无      | 大    |
| Vercel AI SDK | TS      | ★★     | ★★★★  | ❌      | ✅  | 无      | 大    |
| Dapr Agents   | 多语言  | ★★★    | ★★★★  | ✅      | ❌  | 无      | 小    |

## 4. 场景化推荐

### 快速原型

```python
# OpenAI Agents SDK — 最简单的 Agent（v0.8+ Sandbox 架构）
from agents import Agent, Runner

agent = Agent(
    name="assistant",
    instructions="你是有用的助手",
    model="gpt-5.5",
)
result = Runner.run_sync(agent, "你好")
print(result.final_output)
```

### 复杂工作流

```python
# LangGraph — 精细控制每个步骤
from langgraph.graph import StateGraph, START, END

graph = StateGraph(AgentState)
graph.add_node("plan", plan_node)
graph.add_node("execute", execute_node)
graph.add_node("evaluate", evaluate_node)
graph.add_conditional_edges("evaluate", quality_check)
app = graph.compile(checkpointer=PostgresSaver(...))
```

### 团队协作

```python
# CrewAI — 角色定义最直观
from crewai import Agent, Task, Crew

researcher = Agent(role="研究员", goal="深度调研", llm="gpt-4o")
writer = Agent(role="作者", goal="撰写报告", llm="gpt-4o")
crew = Crew(agents=[researcher, writer], tasks=[...])
result = crew.kickoff()
```

### 类型安全

```python
# PydanticAI — Pydantic 原生集成
from pydantic_ai import Agent
from pydantic import BaseModel

class CityInfo(BaseModel):
    name: str
    population: int
    country: str

agent = Agent("openai:gpt-4o", result_type=CityInfo)
result = agent.run_sync("告诉我关于东京的信息")
print(result.data.population)  # 类型安全访问
```

### 云原生 AWS

```python
# AWS Strands — Bedrock 原生集成
from strands import Agent
from strands.models import BedrockModel
from strands_tools import http_request, shell

model = BedrockModel(model_id="us.anthropic.claude-sonnet-4-6-v1:0")  # <!-- 修复于 2026-07-09: 移除日期后缀，与 Anthropic API ID 对齐 -->
agent = Agent(model=model, tools=[http_request, shell])
response = agent("检查 API 健康状态")
```

### TypeScript 全栈

```typescript
// Vercel AI SDK — Next.js 最佳搭档
import { generateText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const { text } = await generateText({
  model: openai('gpt-4o'),
  tools: {
    search: tool({
      parameters: z.object({ query: z.string() }),
      execute: async ({ query }) => `结果: ${query}`,
    }),
  },
  maxSteps: 10,
  prompt: '搜索最新 AI 新闻',
});
```

### Java 企业级

```java
// Spring AI — Spring 生态原生
@RestController
public class AgentController {
    private final ChatClient chatClient;

    public AgentController(ChatClient.Builder builder, MyTools tools) {
        this.chatClient = builder.defaultTools(tools).build();
    }

    @GetMapping("/agent")
    public String agent(@RequestParam String query) {
        return chatClient.prompt().user(query).call().content();
    }
}
```

## 5. 企业级功能对比

| 功能           | LangGraph      | CrewAI         | Strands        | ADK            |
|---------------|----------------|----------------|----------------|----------------|
| 检查点/持久化  | ✅ Postgres    | ❌             | ❌             | ✅ Vertex      |
| 人机交互       | ✅ interrupt   | ✅ human_input | ❌             | ✅ callback    |
| 可观测性       | ✅ LangSmith   | ✅ AgentOps    | ✅ CloudWatch  | ✅ Cloud Trace |
| 流式输出       | ✅             | ✅             | ✅             | ✅             |
| 部署方案       | LangGraph Cloud| CrewAI Ent.    | Bedrock        | Vertex AI      |
| 成本追踪       | ✅ LangSmith   | ❌             | ✅ Bedrock     | ✅ Vertex      |

## 6. 迁移路径

```
常见迁移路径：

原型 → 生产：
  OpenAI SDK → LangGraph（增加控制和持久化）
  CrewAI → LangGraph（需要更精细的流程控制）

单 Agent → 多 Agent：
  LangGraph 单图 → LangGraph 多图 + Supervisor
  PydanticAI → CrewAI（需要角色协作）

Python → 企业级：
  LangGraph → Spring AI（Java 团队）
  LangGraph → Vercel AI SDK（TypeScript 团队）

自托管 → 云原生：
  LangGraph → LangGraph Cloud
  自建 → AWS Strands + Bedrock AgentCore
  自建 → Google ADK + Vertex AI Agent Engine
```

## 7. 选型总结

```
一句话推荐：

LangGraph    → "需要精细控制的复杂生产工作流"
CrewAI       → "多角色协作，快速上手"
OpenAI SDK   → "最快的原型开发"
Google ADK   → "Google 云生态 + 多 Agent"
AWS Strands  → "AWS 生态 + 简洁 API"
Spring AI    → "Java 团队的首选"
Vercel SDK   → "TypeScript 全栈开发"
PydanticAI   → "类型安全的 Python Agent + Deep Agent 能力"
LlamaIndex   → "RAG 和数据处理优先"
smolagents   → "最少代码，HuggingFace 生态"
```

> 🔄 更新于 2026-05-05

### 2026-05 重要变化

| 变化 | 说明 |
| ---- | ---- |
| **GPT-5.5 发布**（2026-04-23） | $5/M 输入、$30/M 输出，1M 上下文，Responses API 支持 |
| **OpenAI Agents SDK v0.8+** | Sandbox + Harness 架构，支持文件操作、命令执行、代码编辑 |
| **PydanticAI 生态扩展** | pydantic-deep 框架发布：规划、沙箱执行、任务委派、人机协作 |
| **LlamaIndex 0.14.23** | 从 0.12.x 跃升至 0.14.x，核心稳定性修复 |
| **Dapr Agents v1.0 GA** | CNCF 托管，生产就绪度从 ★★★ 升至 ★★★★ |

> 来源：[OpenAI Agents SDK](https://openai.com/index/the-next-evolution-of-the-agents-sdk/)、[GPT-5.5 API](https://openrouter.ai/openai/gpt-5.5)、[pydantic-deep](https://pydantic.dev/articles/pydantic-deep-agents)

> 更新于 2026-07-09

### 2026 年 7 月框架选型增量

| 变化 | 说明 |
| ---- | ---- |
| **CrewAI v1.10.1** | 新增 A2A（Agent-to-Agent）协议支持、流式输出；原型速度仍领先 LangGraph 约 40%，但生产场景建议 PoC 后迁移至 LangGraph |
| **LangGraph 生产标准地位巩固** | 约 400 家企业生产部署；Klarna/Uber/LinkedIn 等案例；checkpoint 恢复是长时 Agent 的刚需 |
| **Spring AI 2.0.0 GA**（2026-07） | Java 团队首选框架生产就绪；2.1 路线图含 Agent 模块（预计 2026-11） |
| **行业共识：CrewAI 原型 → LangGraph 生产** | CrewAI token 开销可达 LangGraph 的 3×；LangGraph 用确定性 Python 路由，CrewAI 委派常触发额外 LLM 调用 |

**选型速查（2026-07）**：

```
内容流水线 / 研究 PoC     → CrewAI（角色隐喻直观，2–4 小时可跑通）
代码生成 + 测试重试循环   → LangGraph（循环图 + checkpoint）
企业 SLA / 合规审计       → LangGraph + LangSmith
Java 微服务内嵌 Agent     → Spring AI 2.0 GA
RAG 密集 + 文档解析       → LlamaIndex Workflows 2.22.x
TypeScript 全栈           → Vercel AI SDK 7.x
```

> 来源：[CrewAI vs LangGraph 2026](https://agentsindex.ai/blog/crewai-vs-langgraph)、[Agentic AI Frameworks 2026](https://uvik.net/blog/agentic-ai-frameworks/)、[Speakeasy 框架对比](https://www.speakeasy.com/blog/ai-agent-framework-comparison)

## 🎬 推荐视频资源

### 🌐 YouTube
- [AI Jason - Best AI Agent Frameworks 2025](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — Agent框架对比评测
- [DeepLearning.AI - Agentic AI](https://www.deeplearning.ai/courses/agentic-ai/) — 框架选型参考（免费）

### 📺 B站
- [AI Agent框架选型指南](https://www.bilibili.com/video/BV1dH4y1P7FY) — 中文框架对比
