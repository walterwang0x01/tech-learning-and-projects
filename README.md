# AI Agent 学习路线图 & 实战项目

> 🇨🇳 中文 | [🇬🇧 English](./README_EN.md)
>
> 从零开始系统学习 AI Agent 开发：101 篇体系化笔记 + 2 个可运行项目，覆盖协议、框架、RAG、记忆、安全、支付全生态。

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](./LICENSE)
[![AI Agent Notes](https://img.shields.io/badge/AI_Agent-101_篇笔记-orange)](./learning-notes/00-ai/ai-agent/)
[![Total Notes](https://img.shields.io/badge/全部笔记-422_篇-green)](./learning-notes/)

## 谁适合看

- 🚀 刚入门 AI Agent，面对一堆框架和协议不知道从哪开始
- 🔍 正在做技术选型，需要 LangGraph vs CrewAI vs OpenAI SDK 这类横向对比
- 🛠️ 已经在做 Agent 项目，需要查 RAG、记忆、安全、支付等具体方案的实现细节

## 这个仓库能帮你什么

面对 AI Agent 生态里几十个框架和协议，这个仓库提供了一条从零到生产的完整学习路径：

```text
基础概念 → 设计模式 → 协议体系 → 框架选型 → RAG/记忆/工具 → 安全治理 → 实战案例
```

每篇笔记的特点：

- 📊 ASCII 架构图 — 复杂概念一图看懂
- 💻 可运行代码 — 不是伪代码，是能跑的示例
- 📋 对比表格 — 框架/协议/方案横向对比，帮你做选型决策
- 🔗 交叉引用 — 笔记之间互相关联，形成知识网络

## ⚡ 快速开始

不知道先看什么？按你的需求选：

| 你的情况 | 推荐路径 |
| -------- | -------- |
| 我是新手，从零开始 | [基础概念](./learning-notes/00-ai/ai-agent/00-基础概念/) → [设计模式](./learning-notes/00-ai/ai-agent/01-Agentic设计模式/) → [Agent 协议](./learning-notes/00-ai/ai-agent/02-Agent协议/) → [Agent 框架](./learning-notes/00-ai/ai-agent/03-Agent框架/) |
| 我要选框架做项目 | [Agent 框架（8 大对比）](./learning-notes/00-ai/ai-agent/03-Agent框架/) → [框架选型指南](./learning-notes/00-ai/ai-agent/04-Agent框架补充/) → [实战案例](./learning-notes/00-ai/ai-agent/23-实战案例/) |
| 我在做 RAG / 记忆 | [RAG 进阶](./learning-notes/00-ai/ai-agent/06-RAG进阶/) → [记忆与状态](./learning-notes/00-ai/ai-agent/10-记忆与状态/) → [记忆框架](./learning-notes/00-ai/ai-agent/11-Agent记忆框架/) |
| 我关注安全和协议 | [Agent 协议](./learning-notes/00-ai/ai-agent/02-Agent协议/) → [安全与治理](./learning-notes/00-ai/ai-agent/15-Agent安全与治理/) → [Agent 支付](./learning-notes/00-ai/ai-agent/20-Agent支付/) |

## 🤖 AI Agent 学习路线（99 篇）

<details open>
<summary>第一阶段：打基础（6 篇）</summary>

| 序号 | 主题 | 篇数 | 你会学到 |
| ---- | ---- | ---- | -------- |
| 00 | [基础概念](./learning-notes/00-ai/ai-agent/00-基础概念/) | 3 | AI Agent 是什么、LLM 基础、Prompt Engineering |
| 01 | [Agentic 设计模式](./learning-notes/00-ai/ai-agent/01-Agentic设计模式/) | 3 | Anthropic 设计模式、工作流编排模式 |

</details>

<details>
<summary>第二阶段：理解协议与框架（20 篇）</summary>

| 序号 | 主题 | 篇数 | 你会学到 |
| ---- | ---- | ---- | -------- |
| 02 | [Agent 协议](./learning-notes/00-ai/ai-agent/02-Agent协议/) | 6 | MCP / A2A / ACP / ANP / AG-UI 全景 + 协议转换 |
| 03 | [Agent 框架](./learning-notes/00-ai/ai-agent/03-Agent框架/) | 8 | LangGraph / CrewAI / OpenAI SDK / Google ADK / AWS Strands 等 8 大框架 |
| 04 | [框架补充](./learning-notes/00-ai/ai-agent/04-Agent框架补充/) | 3 | 框架选型指南、LlamaIndex、Anthropic Claude Agent |
| 05 | [Java/TS 生态](./learning-notes/00-ai/ai-agent/05-Java-TS%20Agent生态/) | 3 | Spring AI / Vercel AI SDK / Dapr Agents |

</details>

<details>
<summary>第三阶段：核心能力深入（21 篇）</summary>

| 序号 | 主题 | 篇数 | 你会学到 |
| ---- | ---- | ---- | -------- |
| 06 | [RAG 进阶](./learning-notes/00-ai/ai-agent/06-RAG进阶/) | 4 | RAG 架构 → 向量数据库 → 高级 RAG → GraphRAG |
| 07 | [工具与 Function Calling](./learning-notes/00-ai/ai-agent/07-工具与Function%20Calling/) | 4 | Function Calling 机制、MCP Server 开发、工具编排 |
| 08 | [工具平台与沙箱](./learning-notes/00-ai/ai-agent/08-工具平台与沙箱/) | 4 | Composio / E2B 沙箱 / Web 数据工具 |
| 09 | [多 Agent 系统](./learning-notes/00-ai/ai-agent/09-多Agent系统/) | 3 | 多 Agent 架构、通信协调、人机协作 |
| 10 | [记忆与状态](./learning-notes/00-ai/ai-agent/10-记忆与状态/) | 3 | 短期/长期记忆、对话管理、知识库 |
| 11 | [Agent 记忆框架](./learning-notes/00-ai/ai-agent/11-Agent记忆框架/) | 3 | Mem0 / Letta(MemGPT) / Zep / LangMem |

</details>

<details>
<summary>第四阶段：工程化与生产（21 篇）</summary>

| 序号 | 主题 | 篇数 | 你会学到 |
| ---- | ---- | ---- | -------- |
| 12 | [模型服务](./learning-notes/00-ai/ai-agent/12-模型服务/) | 3 | OpenAI/Claude API、开源模型部署、模型路由 |
| 13 | [AI 网关与路由](./learning-notes/00-ai/ai-agent/13-AI网关与路由/) | 3 | LiteLLM / Vercel AI Gateway / Portkey |
| 14 | [可观测与评估](./learning-notes/00-ai/ai-agent/14-可观测与评估/) | 6 | LLM 可观测性、评估基准、测试工程、成本优化 |
| 15 | [Agent 安全与治理](./learning-notes/00-ai/ai-agent/15-Agent安全与治理/) | 6 | 身份权限、治理框架、纵深防御、Affinidi Trust Fabric、MCP 安全漏洞、Prompt 注入与记忆投毒 |
| 16 | [Harness Engineering](./learning-notes/00-ai/ai-agent/16-Harness%20Engineering/) | 5 | 完整指南、Context Engineering、CI/CD 集成 |

</details>

<details>
<summary>第五阶段：垂直领域与实战（31 篇）</summary>

| 序号 | 主题 | 篇数 | 你会学到 |
| ---- | ---- | ---- | -------- |
| 17 | [Coding Agent](./learning-notes/00-ai/ai-agent/17-Coding%20Agent/) | 6 | Claude Code / Cursor / Kiro / Devin / Vibe Coding |
| 18 | [浏览器与 Agent 生态](./learning-notes/00-ai/ai-agent/18-OpenClaw与Agent生态/) | 6 | 浏览器自动化、Computer Use、Agent Skills、AgentOS |
| 19 | [Voice Agent](./learning-notes/00-ai/ai-agent/19-Voice%20Agent/) | 2 | 语音 Agent 与实时交互 |
| 20 | [Agent 支付](./learning-notes/00-ai/ai-agent/20-Agent支付/) | 4 | ACP / AP2 / Mastercard Agent Pay / x402 + 行业全景 |
| 21 | [云厂商方案](./learning-notes/00-ai/ai-agent/21-云厂商Agent方案/) | 2 | 阿里云百炼、云厂商 Agent 方案对比 |
| 22 | [低代码平台](./learning-notes/00-ai/ai-agent/22-低代码平台/) | 3 | Dify / Coze / FastGPT / n8n / Flowise |
| 23 | [实战案例](./learning-notes/00-ai/ai-agent/23-实战案例/) | 8 | 客服/代码/数据/研究/运维/内容创作/企业办公 Agent |

</details>

## 🎯 实战项目

### LangGraph + MCP 智能 Agent

`Python` `LangGraph` `MCP` `ChromaDB` `FastAPI`

生产级 Agent 示例：工作流编排 + 工具协议 + RAG 检索 + 记忆管理 + 人机协作。

```text
用户请求 → 意图路由 → RAG检索 / MCP工具 / 人工审批 → LLM生成 → 响应
```

```bash
# 快速启动
cd projects/langgraph-mcp-agent-demo
cp env.example .env          # 填入你的 API Key
docker-compose up
```

→ [查看项目代码和文档](./projects/langgraph-mcp-agent-demo/)

### CrewAI 多 Agent 协作

`Python` `CrewAI` `GPT-4o` `FastAPI`

四角色 Agent 团队协作完成内容创作流水线。

```text
主题输入 → 🔍研究员调研 → ✍️写手撰文 → 📝编辑审校 → 📈SEO优化 → 成品文章
```

```bash
# 快速启动
cd projects/crewai-multi-agent-demo
cp env.example .env          # 填入你的 API Key
make run
```

→ [查看项目代码和文档](./projects/crewai-multi-agent-demo/)

## 📚 全栈技术笔记（323 篇）

AI Agent 之外，这里还有覆盖后端、前端、移动端的完整学习笔记，同样的风格——架构图 + 代码示例 + 对比表格：

| 方向 | 内容 |
| ---- | ---- |
| [Java](./learning-notes/01-languages/java/) | Spring Boot / Spring Cloud / 微服务 / 中间件 / JVM / 设计模式 |
| [Python](./learning-notes/01-languages/python/) | FastAPI / 数据分析 / 机器学习 / 并发 / 爬虫 |
| [前端](./learning-notes/02-frontend/frontend/) | React / Vue3 / TypeScript / Next.js / 工程化 / 性能优化 |
| [iOS](./learning-notes/03-mobile/ios/) | Swift / SwiftUI / UIKit / 架构模式 |
| [Android](./learning-notes/03-mobile/android/) | Kotlin / Jetpack Compose / 架构模式 |
| [架构设计](./learning-notes/04-backend-infra/architecture/) | 事件驱动 / 微服务模式 / DDD / CQRS 与事件溯源 / 系统设计 |

## Star History

如果这个仓库对你有帮助，欢迎 Star ⭐ 支持一下，也是对我持续更新的动力。

有问题或建议？欢迎提 [Issue](../../issues) 交流。

## License

免费阅读与非商业分享，商业用途须获作者书面许可 - 详见 [LICENSE](./LICENSE)
