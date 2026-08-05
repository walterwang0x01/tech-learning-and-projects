# GitHub 好项目收藏

> Author: Walter Wang
> 创建时间: 2026-04-20
> 说明: 收集值得关注的 GitHub 开源项目，按用途分类，持续更新。

---

## 🎨 AI 生成 & 可视化

### 演示文稿 / 幻灯片

> 🔄 更新于 2026-04-22

**Agent Skill 类**（给 Claude Code / Kiro / Cursor 等 Agent 用）

| 项目 | Stars | 描述 | 链接 |
| ---- | ----- | ---- | ---- |
| zarazhangrui/frontend-slides | — | Claude Code Skill，用自然语言生成动画丰富的 HTML 演示文稿。零依赖单文件输出，12 种视觉风格，支持 PPT 转 Web，可部署到 Vercel 或导出 PDF | [GitHub](https://github.com/zarazhangrui/frontend-slides) |
| MiniMax-AI/skills (pptx-generator) | — | MiniMax 官方 Skill，用 PptxGenJS 从零创建真正的 .pptx 文件（封面、目录、内容、分隔页、总结页），支持通过 XML 编辑已有 PPTX，内置完整设计系统（配色、字体、样式） | [GitHub](https://github.com/MiniMax-AI/skills) |
| mpuig/agent-slides | — | 生产级 Agent Skill，专注企业品牌合规。提取企业模板的布局/配色/字体规则，自动 QA 校验（字号、对比度、溢出），确定性输出，支持 Claude Code / Cursor / Gemini CLI | [GitHub](https://github.com/mpuig/agent-slides) · [官网](https://agent-slides.com/) |
| SlideSpeak/skills | — | SlideSpeak 官方 Skill + MCP Server，调用 SlideSpeak API 生成可编辑 .pptx。支持品牌模板、语气/长度控制、异步任务轮询，500+ 企业在用 | [GitHub](https://github.com/SlideSpeak/skills) |
| tfriedel/claude-office-skills | — | 完整 Office 文档 Skill 套件（PPTX + DOCX + XLSX + PDF）。PPT 部分支持 HTML 转 PPTX、模板替换、缩略图校验、OOXML 直接编辑 | [GitHub](https://github.com/tfriedel/claude-office-skills) |
| Felo Skills (felo-slides) | — | Felo AI 出品，通过 Felo PPT Task API 生成专业幻灯片，npm 一键安装，支持 Claude Code / OpenClaw | [Felo 官网](https://felo.ai/skills/claudecode/felo-slides) |

**独立 AI PPT 生成平台**（可自托管）

| 项目 | Stars | 描述 | 链接 |
| ---- | ----- | ---- | ---- |
| icip-cas/PPTAgent (DeepPresenter) | 2k+ | 中科院出品，EMNLP 2025 / ACL 2026 论文项目。自带微调模型 DeepPresenter-9B，支持深度研究集成、自由排版、自动配图、沙箱环境 + 20 多个工具，有 MCP Server 和 CLI | [GitHub](https://github.com/icip-cas/PPTAgent) |
| presenton/presenton | — | Gamma / Beautiful.ai 的开源替代品（Apache 2.0）。桌面端 + Docker 自托管，支持 OpenAI / Gemini / Anthropic / Ollama，可用已有 PPTX 做模板，内置 MCP Server | [GitHub](https://github.com/presenton/presenton) |

### 技术图表 / 架构图

| 项目 | Stars | 描述 | 链接 |
| ---- | ----- | ---- | ---- |
| yizhiyanhua-ai/fireworks-tech-graph | — | Claude Code Skill，自然语言生成出版级 SVG+PNG 技术图表。7 种视觉风格，14 种 UML 图类型，深度 AI/Agent 领域知识（RAG、Mem0、Multi-Agent 等内置模式），40+ 产品品牌图标 | [GitHub](https://github.com/yizhiyanhua-ai/fireworks-tech-graph) |
| DayuanJiang/next-ai-draw-io | — | 基于 Next.js + draw.io 的 AI 画图 Web 应用。对话式创建和编辑图表，支持图片/PDF 上传复刻，10+ AI 提供商，版本历史，动画连接线，提供 MCP Server，有桌面客户端 | [GitHub](https://github.com/DayuanJiang/next-ai-draw-io) |

---

## 🤖 AI Agent 框架

| 项目 | Stars | 描述 | 链接 |
| ---- | ----- | ---- | ---- |
| langchain-ai/langgraph | — | LangChain 的 Agent 工作流编排框架，图结构状态机，支持持久化检查点和人机协作 | [GitHub](https://github.com/langchain-ai/langgraph) |
| crewAIInc/crewAI | 44.6k | 基于角色的多 Agent 协作框架，v1.12 新增 Agent Skills 和 Cognitive Memory | [GitHub](https://github.com/crewAIInc/crewAI) |
| openai/openai-agents-python | — | OpenAI 官方轻量级多 Agent 框架，原生沙箱执行 + model-native harness | [GitHub](https://github.com/openai/openai-agents-python) |
| NousResearch/hermes-agent | ~95k | Nous Research 的自进化 Agent 框架，闭环学习：执行→生成技能文档→持久化记忆→复用 | [GitHub](https://github.com/NousResearch/hermes-agent) |
| multica-ai/multica | 10k+ | 开源托管 Agent 平台，把编码 Agent 变成真正的"队友"——分配任务、追踪进度、积累可复用 Skill。支持 Claude Code / Codex / Hermes / Gemini / Cursor Agent，Go + Next.js 架构，可自托管 | [GitHub](https://github.com/multica-ai/multica) |

---

## 🔧 MCP 生态

| 项目 | Stars | 描述 | 链接 |
| ---- | ----- | ---- | ---- |
| oraios/serena | 19.8k | 基于语言服务器的 MCP 编码 Agent 工具包，提供语义级代码检索与编辑能力 | [GitHub](https://github.com/oraios/serena) |
| microsoft/markitdown | 14.5k+ | 微软出品的 Python 工具，将 PDF / Word / PPT / Excel / 图片 / 音频 / HTML 等转为 Markdown。专为 LLM 文本分析管线设计，支持 OCR 和语音转录，可用于 RAG 预处理 | [GitHub](https://github.com/microsoft/markitdown) |
| thedotmack/claude-mem | 12.4k+ | Claude Code 持久记忆压缩插件，自动捕获编码会话中的工具操作，AI 压缩摘要后注入未来会话。支持 Claude Code / Gemini CLI / OpenCode，提供 Web 查看器和语义搜索 | [GitHub](https://github.com/thedotmack/claude-mem) |

---

## 🛡️ Agent 安全 & 治理

| 项目 | Stars | 描述 | 链接 |
| ---- | ----- | ---- | ---- |
| Microsoft Agent Governance Toolkit | — | 首个覆盖 OWASP Agentic AI Top 10 的开源治理工具包，7 个模块，5 种语言，MIT 协议 | [GitHub](https://opensource.microsoft.com/blog/2026/04/02/introducing-the-agent-governance-toolkit-open-source-runtime-security-for-ai-agents/) |

---

## 🛠 开发工具 & 最佳实践

> 🔄 更新于 2026-04-24

| 项目 | Stars | 描述 | 链接 |
| ---- | ----- | ---- | ---- |
| awsdataarchitect/kiro-best-practices | — | Kiro 最佳实践模板，包含完整的 steering（Git、Python、安全等）和 hooks 示例，开箱即用的 AI 驱动开发环境 | [GitHub](https://github.com/awsdataarchitect/kiro-best-practices) |
| awslabs/aidlc-workflows | — | AWS 官方 AI 驱动开发生命周期（AI-DLC）steering 规则，适用于 Kiro 和其他 coding agent，覆盖需求→设计→实现→测试→部署全流程 | [GitHub](https://github.com/awslabs/aidlc-workflows) |
| jasonkneen/kiro | — | 社区维护的 Kiro skills 集合，包含多种实用 skill 和配置示例 | [GitHub](https://github.com/jasonkneen/kiro) |

---

## ☁️ 云 & 基础设施

| 项目 | Stars | 描述 | 链接 |
| ---- | ----- | ---- | ---- |
| GoogleCloudPlatform/agent-starter-pack | 6.1k | Google Cloud 的 AI Agent 生产模板，内置 CI/CD、评估和可观测性 | [GitHub](https://github.com/GoogleCloudPlatform/agent-starter-pack) |

---

## 📚 学习资源

| 项目 | Stars | 描述 | 链接 |
| ---- | ----- | ---- | ---- |
| f/prompts.chat | 143k+ | 全球最大的开源 AI Prompt 库（原 Awesome ChatGPT Prompts）。社区驱动的 Prompt 收集与分享平台，兼容 ChatGPT / Claude / Gemini / Llama 等主流模型。提供 MCP Server、CLI 插件、自托管部署，附带免费交互式 Prompt 工程教程（25+ 章节）。被 Forbes 报道，Harvard / Columbia 引用，Hugging Face 最受欢迎数据集 | [GitHub](https://github.com/f/awesome-chatgpt-prompts) · [网站](https://prompts.chat) |
| forrestchang/andrej-karpathy-skills | — | 基于 Andrej Karpathy 对 LLM 编码缺陷观察的 Claude Code 行为优化指南。四大原则：先想再写、简洁优先、精准修改、目标驱动。支持 Claude Code Plugin / CLAUDE.md / Cursor 规则三种安装方式 | [GitHub](https://github.com/forrestchang/andrej-karpathy-skills) |
| addyosmani/agent-skills | 6.4k+ | 🌟 Google Chrome 团队 Addy Osmani 出品的生产级 AI 编码 Skill 包。20 个 Skill 覆盖完整开发生命周期（/spec → /plan → /build → /test → /review → /ship），支持 Claude Code / Cursor / Gemini CLI / **Kiro** / Codex 等 | [GitHub](https://github.com/addyosmani/agent-skills) |
| HKUDS/DeepTutor | 4.5k+ | 港大的 Agent 原生个性化学习助手，v1.0 架构重写约 20 万行。六种模式共享上下文（聊天/深度求解/测验/研究/数学动画/可视化），支持 AI Co-Writer 和 Book Engine，Apache-2.0 协议 | [GitHub](https://github.com/HKUDS/DeepTutor) |
| VoltAgent/awesome-ai-agent-papers | — | 2026 年 AI Agent 研究论文精选集，涵盖工程、记忆、评估、工作流 | [GitHub](https://github.com/VoltAgent/awesome-ai-agent-papers) |

---

## 使用说明

- 🌟 = 个人重点关注 / 已在项目中使用
- 每个分类按实用性排序
- Stars 数据为收录时的近似值，可能已变化
- 新增项目请在对应分类末尾追加，并标注发现日期

> 💡 发现新项目后，告诉 Kiro "收藏这个 GitHub 项目"即可自动追加到本文档。
