# AI Agent Learning Roadmap & Projects

> [🇨🇳 中文](./README.md) | 🇬🇧 English
>
> A systematic learning path for AI Agent development: 101 structured notes + 2 runnable projects covering protocols, frameworks, RAG, memory, security, and payments.

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![AI Agent Notes](https://img.shields.io/badge/AI_Agent-101_Notes-orange)](./learning-notes/00-ai/ai-agent/)
[![Total Notes](https://img.shields.io/badge/Total-422_Notes-green)](./learning-notes/)

## Who Is This For

- 🚀 New to AI Agents and overwhelmed by the number of frameworks and protocols
- 🔍 Evaluating tech stacks and need side-by-side comparisons of LangGraph vs CrewAI vs OpenAI SDK
- 🛠️ Building Agent projects and need implementation details on RAG, memory, security, or payments

## What You Get

A complete learning path from zero to production-ready AI Agents:

```text
Fundamentals → Design Patterns → Protocols → Frameworks → RAG/Memory/Tools → Security → Real-world Cases
```

Every note includes:

- 📊 ASCII architecture diagrams — complex concepts at a glance
- 💻 Runnable code — real examples, not pseudocode
- 📋 Comparison tables — side-by-side framework/protocol evaluations
- 🔗 Cross-references — notes link to each other, forming a knowledge graph

## ⚡ Quick Start

| Your Situation | Recommended Path |
| -------------- | ---------------- |
| Complete beginner | [Fundamentals](./learning-notes/00-ai/ai-agent/00-基础概念/) → [Design Patterns](./learning-notes/00-ai/ai-agent/01-Agentic设计模式/) → [Protocols](./learning-notes/00-ai/ai-agent/02-Agent协议/) → [Frameworks](./learning-notes/00-ai/ai-agent/03-Agent框架/) |
| Choosing a framework | [Frameworks (8 compared)](./learning-notes/00-ai/ai-agent/03-Agent框架/) → [Selection Guide](./learning-notes/00-ai/ai-agent/04-Agent框架补充/) → [Case Studies](./learning-notes/00-ai/ai-agent/23-实战案例/) |
| Working on RAG / Memory | [Advanced RAG](./learning-notes/00-ai/ai-agent/06-RAG进阶/) → [Memory & State](./learning-notes/00-ai/ai-agent/10-记忆与状态/) → [Memory Frameworks](./learning-notes/00-ai/ai-agent/11-Agent记忆框架/) |
| Interested in security & protocols | [Protocols](./learning-notes/00-ai/ai-agent/02-Agent协议/) → [Security & Governance](./learning-notes/00-ai/ai-agent/15-Agent安全与治理/) → [Agent Payments](./learning-notes/00-ai/ai-agent/20-Agent支付/) |

## 🤖 AI Agent Learning Roadmap (101 Notes)

> Note: All notes are written in Chinese with English code examples.

<details open>
<summary>Phase 1: Fundamentals (6 notes)</summary>

| # | Topic | Notes | What You'll Learn |
| - | ----- | ----- | ----------------- |
| 00 | [Fundamentals](./learning-notes/00-ai/ai-agent/00-基础概念/) | 3 | What is AI Agent, LLM basics, Prompt Engineering |
| 01 | [Agentic Design Patterns](./learning-notes/00-ai/ai-agent/01-Agentic设计模式/) | 3 | Anthropic patterns, workflow orchestration |

</details>

<details>
<summary>Phase 2: Protocols & Frameworks (20 notes)</summary>

| # | Topic | Notes | What You'll Learn |
| - | ----- | ----- | ----------------- |
| 02 | [Agent Protocols](./learning-notes/00-ai/ai-agent/02-Agent协议/) | 6 | MCP / A2A / ACP / ANP / AG-UI overview + protocol bridges |
| 03 | [Agent Frameworks](./learning-notes/00-ai/ai-agent/03-Agent框架/) | 8 | LangGraph / CrewAI / OpenAI SDK / Google ADK / AWS Strands and more |
| 04 | [Framework Extras](./learning-notes/00-ai/ai-agent/04-Agent框架补充/) | 3 | Selection guide, LlamaIndex, Anthropic Claude Agent |
| 05 | [Java/TS Ecosystem](./learning-notes/00-ai/ai-agent/05-Java-TS%20Agent生态/) | 3 | Spring AI / Vercel AI SDK / Dapr Agents |

</details>

<details>
<summary>Phase 3: Core Capabilities (21 notes)</summary>

| # | Topic | Notes | What You'll Learn |
| - | ----- | ----- | ----------------- |
| 06 | [Advanced RAG](./learning-notes/00-ai/ai-agent/06-RAG进阶/) | 4 | RAG architecture → Vector DBs → Advanced RAG → GraphRAG |
| 07 | [Tools & Function Calling](./learning-notes/00-ai/ai-agent/07-工具与Function%20Calling/) | 4 | Function Calling, MCP Server development, tool orchestration |
| 08 | [Tool Platforms & Sandboxes](./learning-notes/00-ai/ai-agent/08-工具平台与沙箱/) | 4 | Composio / E2B sandbox / Web data tools |
| 09 | [Multi-Agent Systems](./learning-notes/00-ai/ai-agent/09-多Agent系统/) | 3 | Multi-Agent patterns, communication, human-in-the-loop |
| 10 | [Memory & State](./learning-notes/00-ai/ai-agent/10-记忆与状态/) | 3 | Short/long-term memory, conversation management |
| 11 | [Memory Frameworks](./learning-notes/00-ai/ai-agent/11-Agent记忆框架/) | 3 | Mem0 / Letta(MemGPT) / Zep / LangMem |

</details>

<details>
<summary>Phase 4: Production Engineering (21 notes)</summary>

| # | Topic | Notes | What You'll Learn |
| - | ----- | ----- | ----------------- |
| 12 | [Model Serving](./learning-notes/00-ai/ai-agent/12-模型服务/) | 3 | OpenAI/Claude API, open-source model deployment, model routing |
| 13 | [AI Gateway & Routing](./learning-notes/00-ai/ai-agent/13-AI网关与路由/) | 3 | LiteLLM / Vercel AI Gateway / Portkey |
| 14 | [Observability & Evaluation](./learning-notes/00-ai/ai-agent/14-可观测与评估/) | 6 | LLM observability, benchmarks, testing, cost optimization |
| 15 | [Security & Governance](./learning-notes/00-ai/ai-agent/15-Agent安全与治理/) | 6 | Identity, governance frameworks, defense in depth, Affinidi Trust Fabric, MCP security vulnerabilities, prompt injection & memory poisoning |
| 16 | [Harness Engineering](./learning-notes/00-ai/ai-agent/16-Harness%20Engineering/) | 5 | Complete guide, Context Engineering, CI/CD integration |

</details>

<details>
<summary>Phase 5: Verticals & Case Studies (31 notes)</summary>

| # | Topic | Notes | What You'll Learn |
| - | ----- | ----- | ----------------- |
| 17 | [Coding Agents](./learning-notes/00-ai/ai-agent/17-Coding%20Agent/) | 6 | Claude Code / Cursor / Kiro / Devin / Vibe Coding |
| 18 | [Browser & Agent Ecosystem](./learning-notes/00-ai/ai-agent/18-OpenClaw与Agent生态/) | 6 | Browser automation, Computer Use, Agent Skills, AgentOS |
| 19 | [Voice Agents](./learning-notes/00-ai/ai-agent/19-Voice%20Agent/) | 2 | Voice agents & real-time interaction |
| 20 | [Agent Payments](./learning-notes/00-ai/ai-agent/20-Agent支付/) | 4 | ACP / AP2 / Mastercard Agent Pay / x402 + industry landscape |
| 21 | [Cloud Provider Solutions](./learning-notes/00-ai/ai-agent/21-云厂商Agent方案/) | 2 | Alibaba Cloud, cloud provider comparison |
| 22 | [Low-Code Platforms](./learning-notes/00-ai/ai-agent/22-低代码平台/) | 3 | Dify / Coze / FastGPT / n8n / Flowise |
| 23 | [Case Studies](./learning-notes/00-ai/ai-agent/23-实战案例/) | 8 | Customer service / Code / Data / Research / DevOps / Content / Enterprise |

</details>

## 🎯 Projects

### LangGraph + MCP Intelligent Agent

`Python` `LangGraph` `MCP` `ChromaDB` `FastAPI`

Production-grade Agent: workflow orchestration + tool protocol + RAG retrieval + memory management + human-in-the-loop.

```text
User Request → Intent Router → RAG / MCP Tools / Human Approval → LLM → Response
```

```bash
cd projects/langgraph-mcp-agent-demo
cp env.example .env          # Add your API Key
docker-compose up
```

→ [View project](./projects/langgraph-mcp-agent-demo/)

### CrewAI Multi-Agent Collaboration

`Python` `CrewAI` `GPT-4o` `FastAPI`

Four-role Agent team for content creation pipeline.

```text
Topic → 🔍Researcher → ✍️Writer → 📝Editor → 📈SEO Optimizer → Published Article
```

```bash
cd projects/crewai-multi-agent-demo
cp env.example .env          # Add your API Key
make run
```

→ [View project](./projects/crewai-multi-agent-demo/)

## 📚 Full-Stack Tech Notes (323 notes)

Beyond AI Agents, this repo includes full-stack development notes with the same style — diagrams + code + comparison tables:

| Area | Topics |
| ---- | ------ |
| [Java](./learning-notes/01-languages/java/) | Spring Boot / Spring Cloud / Microservices / Middleware / JVM / Design Patterns |
| [Python](./learning-notes/01-languages/python/) | FastAPI / Data Analysis / ML / Concurrency / Web Scraping |
| [Frontend](./learning-notes/02-frontend/frontend/) | React / Vue3 / TypeScript / Next.js / Build Tools / Performance |
| [iOS](./learning-notes/03-mobile/ios/) | Swift / SwiftUI / UIKit / Architecture Patterns |
| [Android](./learning-notes/03-mobile/android/) | Kotlin / Jetpack Compose / Architecture Patterns |
| [Architecture](./learning-notes/04-backend-infra/architecture/) | Event-Driven / Microservices / DDD / CQRS & Event Sourcing / System Design |

## Star History

If you find this repo helpful, a Star ⭐ would be appreciated.

Questions or suggestions? Feel free to open an [Issue](../../issues).

## License

Free to read and share non-commercially (with attribution). Commercial use requires written permission - See [LICENSE](./LICENSE)
