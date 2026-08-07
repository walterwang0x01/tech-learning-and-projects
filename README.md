# AI 工程知识库

> 🇨🇳 中文 | [🇬🇧 English](./README_EN.md)

**571 篇原创技术笔记 + 198 道自测题 + 6 个可运行项目**，覆盖从反向传播推导到生产级 Agent 系统的完整链路。

### 👉 [在线交互式阅读 →](https://walterwang0x01.github.io/portfolio/notes/)

不只是笔记堆放。站点提供三种使用方式：

| | 做什么 |
| --- | --- |
| 🗺️ **学习路线** | 5 个阶段按依赖关系编排，每阶段标注篇数、预计时长、**为什么要先学这个**，带阅读进度追踪 |
| 📖 **阅读** | 目录树导航 + 全文渲染，可标记已读 |
| ✍️ **自测** | 198 道题，先自己答再对照原文，三档自评。**答不上就是需要精读的信号** |

[![交互式学习站](https://img.shields.io/badge/在线阅读-交互式学习站-blue)](https://walterwang0x01.github.io/portfolio/notes/)
[![AI 笔记](https://img.shields.io/badge/AI_工程-191_篇-orange)](./learning-notes/00-ai/)
[![全部笔记](https://img.shields.io/badge/全部笔记-571_篇-green)](./learning-notes/)
[![自测题](https://img.shields.io/badge/自测题-198_道-purple)](https://walterwang0x01.github.io/portfolio/notes/#quiz)

---

## 这个仓库和别的学习资料有什么不同

**一、原理层和应用层都写透，不是只写一半**

大部分 AI 学习资料要么只讲"怎么调 API 做 Agent"，要么只讲"Transformer 数学推导"。这里两层都有，且明确划分：

```
01-machine-learning  反向传播推导 / 优化器 / 正则化 / CNN / RNN / 强化学习     34 篇
02-llm               注意力推导 / 分词算法 / MoE / RLHF / 量化 / 扩散模型      23 篇
04-ai-agent          框架 / 协议 / RAG / 工具 / 记忆 / 安全 / Harness         128 篇
```

想知道「微调为什么没效果」需要前两层，想知道「Agent 为什么会失控」需要第三层。

**二、每篇开头就三个问题，读完能自测**

不是摘要，是**检验标准**。举例（[模型合并](./learning-notes/00-ai/02-llm/04-微调与对齐/05-模型合并.md)）：

> 1. 为什么两个独立微调的模型可以直接在参数空间做加减，这个操作的前提假设是什么？
> 2. TIES 和 DARE 各自解决了朴素权重平均的什么问题，处理手段有何不同？
> 3. 什么情况下模型合并会失败，如何在合并前判断可行性？

答不上就回去精读对应小节。这 198 道题在[站点上是可交互的](https://walterwang0x01.github.io/portfolio/notes/#quiz)。

**三、原理篇都配可运行代码，且结果是实测的**

不是伪代码。每段 NumPy 实现都实际跑过，输出贴的是真实结果。写作过程中出现过多次「预期输出和实测不符」——比如模型崩溃那篇初版用无偏估计根本模拟不出衰减，改成最大似然（有偏）才复现出 sigma 从 0.95 降到 0.35。**这类修正都保留在笔记里，因为踩坑过程本身有信息量。**

**四、写明「什么时候不该用」**

技术选型笔记不只列优点。比如 [模型合并](./learning-notes/00-ai/02-llm/04-微调与对齐/05-模型合并.md) 第 9 节列了六种会失败的场景和判断方法；[从 for 循环到自治系统](./learning-notes/00-ai/04-ai-agent/16-Harness%20Engineering/10-从for循环到自治系统.md) 有专门一节讲「何时不应该上自治」。

---

## 内容地图

### 🧠 AI 工程（191 篇）— [详细导航](./learning-notes/00-ai/README.md)

按学习依赖关系编号，不是字母序：

| 阶段 | 内容 | 篇数 |
| --- | --- | --- |
| [00-入门准备](./learning-notes/00-ai/00-入门准备/) | AI 全景辨析、开发环境与算力、学习路线与常见误区、如何读论文 | 4 |
| [01-machine-learning](./learning-notes/00-ai/01-machine-learning/README.md) | 数学够用篇 → 经典算法 → 特征工程 → **反向传播推导** → 训练工程 → CNN/RNN → 强化学习 | 34 |
| [02-llm](./learning-notes/00-ai/02-llm/README.md) | **注意力推导** → 分词算法 → BERT/GPT/MoE → SFT/LoRA/RLHF/DPO → KV Cache/量化/投机解码 → CLIP/扩散/VLM | 23 |
| [03-实战项目](./learning-notes/00-ai/03-实战项目/) | PyTorch 训练实战、端到端项目 | 2 |
| [04-ai-agent](./learning-notes/00-ai/04-ai-agent/README.md) | 25 个子目录，见下表 | 128 |

<details>
<summary><b>04-ai-agent 的 25 个子目录（点击展开）</b></summary>

| 子目录 | 内容 |
| --- | --- |
| 00-基础概念 | Agent 概述、LLM 基础（32KB）、Prompt Engineering |
| 01-Agentic设计模式 | Anthropic 五种 workflow 模式、15+ 设计模式、工作流编排 |
| 02-Agent协议 | MCP / A2A / ACP / ANP、Agent 支付协议、协议转换工具 |
| 03-Agent框架 | LangGraph / CrewAI / OpenAI SDK / Google ADK / AWS Strands / MS Agent Framework / AG2 / PydanticAI |
| 04-框架补充 | 选型指南、LlamaIndex Workflow、Claude Agent 能力 |
| 05-Java-TS生态 | Spring AI、Vercel AI SDK、Dapr Agents |
| 06-RAG进阶 | RAG 架构、向量库选型、HyDE/Self-RAG/Contextual Retrieval、GraphRAG |
| 07-工具与Function Calling | FC 机制、MCP Server 开发、工具编排与安全、**Agent 可扩展性设计** |
| 08-工具平台与沙箱 | Composio、E2B、Firecrawl/Tavily/Exa 等 Web 数据工具 |
| 09-多Agent系统 | Supervisor / Hierarchical / Swarm / Network 四种架构 |
| 10-记忆与状态 | 短期长期记忆、上下文压缩、经验回放与反思 |
| 11-Agent记忆框架 | Mem0、Letta/MemGPT、Zep、LangMem |
| 12-模型服务 | OpenAI/Claude API、vLLM 部署、模型路由与网关 |
| 13-AI网关与路由 | LiteLLM、Vercel AI Gateway、Portkey |
| 14-可观测与评估 | LangSmith/LangFuse/Phoenix、评估基准、**Agent 测试工程实战（76KB）**、成本优化 |
| 15-Agent安全与治理 | **Agent 身份与权限（60KB）**、治理框架、纵深防御、**MCP 供应链攻击**、**Prompt 注入与记忆投毒** |
| 16-Harness Engineering | 完整指南、Context Engineering、**Context Offloading**、**Agent Version Drifting**、**Company Brain**、从 for 循环到自治系统 |
| 17-Coding Agent | **Claude Code 架构深度解析（44KB）**、Cursor/Kiro/Windsurf、Devin/OpenHands、Vibe Coding |
| 18-OpenClaw与Agent生态 | 浏览器自动化 Agent、Computer Use、Agent Skills、AgentOS、SkillHub |
| 19-Voice Agent | OpenAI Realtime、LiveKit、ElevenLabs（含完整开发实战） |
| 20-Agent支付 | ACP / AP2 / Mastercard Agent Pay / x402 协议 |
| 21-云厂商方案 | 阿里云百炼、云厂商横向对比 |
| 22-低代码平台 | Dify、Coze、FastGPT、n8n、Flowise |
| 23-实战案例 | 客服 / 代码 / 数据分析 / 研究 / 运维 / 内容 Agent、**从 Claude Code 学构建生产级 Agent（64KB）** |
| 24-2026技术更新 | 年度技术动态汇总 |

</details>

### 💻 其他技术栈（380 篇）

| 领域 | 内容 | 篇数 |
| --- | --- | --- |
| [01-languages](./learning-notes/01-languages/) | Python / Java / Go / Rust | 181 |
| [02-frontend](./learning-notes/02-frontend/frontend/README.md) | React / Vue3 / TypeScript / 工程化 / 性能优化 | 66 |
| [03-mobile](./learning-notes/03-mobile/) | iOS（Swift/SwiftUI）、Android（Kotlin/Compose） | 90 |
| [04-backend-infra](./learning-notes/04-backend-infra/) | 架构设计 / 数据库 / 数据工程 / 可观测性 / 平台工程 / 安全 | 43 |

### 📰 每日技术简报（304 篇）

[AI Agent / 国内科技 / 国际科技](./learning-notes/_briefings/) 三个主题，自动化采集流水线（RSS + HN API + web search，含去重、评分、熔断自愈）。

**[在线阅读简报 →](https://walterwang0x01.github.io/portfolio/briefing/)**

### 📖 读物收藏

[reading/](./reading/) — 第三方技术书籍收藏 + 我的读书笔记（版权独立声明，见各子目录 COPYRIGHT.md）。

**[在线阅读 →](https://walterwang0x01.github.io/portfolio/reading/)**

---

## 🎯 实战项目

### LangGraph + MCP 智能 Agent

生产级 Agent 骨架：意图路由 → RAG 检索 / 工具调用 / 人工审批 → 生成回答。

```bash
cd projects/langgraph-mcp-agent-demo
cp env.example .env   # 填入 API Key
docker-compose up -d  # 起 PostgreSQL + ChromaDB
uvicorn app.main:app --reload
```

技术点：LangGraph 状态图与检查点持久化、MCP Server（文件 + 数据库）、ChromaDB RAG、Mem0 长期记忆、敏感操作人工审批。

→ [项目文档](./projects/langgraph-mcp-agent-demo/)

### CrewAI 多 Agent 协作

内容创作流水线：研究员 → 作家 → 编辑 → SEO 优化师，四个 Agent 顺序协作。

```bash
cd projects/crewai-multi-agent-demo
cp env.example .env
python -m app.main --topic "AI Agent 技术趋势"
```

→ [项目文档](./projects/crewai-multi-agent-demo/)

### 其他项目

- [rag-llm-agent-platform](./projects/rag-llm-agent-platform/) — RAG + 工具调用平台（FastAPI + pgvector）
- [spring-boot-microservice-demo](./projects/spring-boot-microservice-demo/) — Spring Cloud 微服务（用户/订单 + Kafka）
- [x402-demo](./projects/x402-demo/) / [x402-python-demo](./projects/x402-python-demo/) — x402 HTTP 原生微支付协议实验

---

## 怎么用这个仓库

**如果你刚入门 AI**：从[学习路线](https://walterwang0x01.github.io/portfolio/notes/)开始，按 00 → 01 → 02 → 03 → 04 的顺序走。别跳过 `01-machine-learning/04-神经网络原理`，那是判断力的来源。

**如果你已经在做 Agent**：直接查 `04-ai-agent/` 下对应子目录。选型看 `04-Agent框架补充/01-Agent框架选型指南`，踩坑看 `15-Agent安全与治理` 和 `14-可观测与评估`。

**如果你想检验自己的水平**：直接去[自测页](https://walterwang0x01.github.io/portfolio/notes/#quiz)，198 道题里挑感兴趣的模块，答不上的再去读对应笔记。这比从头读一遍效率高。

**如果你在准备面试**：`01-languages/*/面试准备/`、`02-frontend/frontend/15-面试准备/`、`03-mobile/*/10-面试准备/` 有专门的题目整理。

---

## 维护方式

这个仓库不是写完就放着的。有一套自动化维护机制：

- **文档质量 CI**：断裂链接检查、文件头规范、版本标记时效性（[ci-docs.yml](./.github/workflows/ci-docs.yml)）
- **内链验证**：841 条内部链接，每次改动后验证零失效
- **简报流水线**：`scripts/briefing_tools/` 232 个单元测试覆盖分类、评分、去重、源健康熔断
- **版本时效标记**：`<!-- version-check -->` 标记的内容会被定期复查更新

写作约定：单篇 8~15KB、开头三个自测问题、原理篇必配可运行示例、超 20KB 拆分。

---

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=walterwang0x01/tech-learning-and-projects&type=Date)](https://star-history.com/#walterwang0x01/tech-learning-and-projects&Date)

---

## 协议

**免费阅读与非商业分享**，转载请注明出处与作者；任何商业用途（出版、培训、付费内容改编）须事先获得书面许可。

`reading/` 目录下为第三方内容，版权归原作者，见各子目录 `COPYRIGHT.md`。

详见 [LICENSE](./LICENSE)。

---

<div align="center">

**如果这个仓库对你有帮助，欢迎 ⭐ Star**

作者：Walter Wang

</div>
