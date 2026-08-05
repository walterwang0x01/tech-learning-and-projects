# AI Agent 技术学习笔记

> 本目录包含 AI Agent 与大模型应用开发的完整知识体系，覆盖 2024-2026 主流技术

## 📁 知识体系结构

按学习路径从基础到高级组织，共 24 个分类、90 个文档。

```
ai-agent/
│
│  ═══════════════ 第一层：认知基础 ═══════════════
│
├── 00-基础概念/                    # 入门必读
│   ├── AI Agent概述与发展.md       # Agent 定义、分类、演进趋势
│   ├── 大语言模型基础.md           # GPT/Claude/Gemini/Llama 对比
│   └── Prompt Engineering.md      # 提示词工程（Harness 的起点）
│
├── 01-Agentic设计模式/             # 架构蓝图（先理解模式再选框架）
│   ├── Anthropic Agent设计模式.md  # 官方 5 大 Workflow + Agent 模式
│   ├── Agentic设计模式大全.md      # 15+ 生产级设计模式
│   └── Agent工作流编排模式.md      # DAG/状态机/事件驱动/并行扇出
│
│  ═══════════════ 第二层：协议标准 ═══════════════
│
├── 02-Agent协议/                   # Agent 通信的"TCP/IP"
│   ├── Agent协议全景图.md          # ★ 全协议关系图（MCP/A2A/AG-UI/ANP）
│   ├── MCP模型上下文协议.md        # Agent ↔ 工具（垂直连接）
│   ├── A2A Agent间通信协议.md      # Agent ↔ Agent（水平协作）
│   ├── ACP与协议生态.md            # ACP/ANP 轻量协议
│   ├── Agent支付协议.md            # ★ ACP(OpenAI)/AP2(Google)/Mastercard/x402
│   └── 协议转换工具.md             # ★ Open-CLI/CLI-Anything/Higress
│
│  ═══════════════ 第三层：开发框架 ═══════════════
│
├── 03-Agent框架/                   # 主流框架（选一个深入）
│   ├── LangGraph工作流编排.md      # ★ 生产级首选，图结构编排
│   ├── CrewAI多Agent协作.md        # ★ 角色化多 Agent，最快上手
│   ├── OpenAI Agents SDK.md       # 快速原型，GPT 生态
│   ├── Google ADK详解.md           # ADK 全功能，A2A 原生
│   ├── AWS Strands与Bedrock AgentCore.md  # AWS 生态
│   ├── Microsoft Agent Framework.md       # SK+AutoGen 合并
│   ├── Google ADK与Bedrock Agents.md      # 云厂商方案概览
│   └── AG2-PydanticAI-Agno.md     # 其他框架
│
├── 04-Agent框架补充/               # 框架生态补充
│   ├── LlamaIndex Agent与Workflow.md  # 事件驱动编排
│   ├── Anthropic Claude Agent能力.md  # Claude 全能力解析
│   └── Agent框架选型指南.md        # ★ 10+ 框架对比矩阵
│
├── 05-Java-TS Agent生态/           # 多语言 Agent 开发
│   ├── Spring AI Agent.md         # Java 生态
│   ├── Vercel AI SDK Agent开发.md  # TypeScript 生态
│   └── Dapr Agents分布式运行时.md  # 分布式 Agent
│
│  ═══════════════ 第四层：核心能力 ═══════════════
│
├── 06-RAG进阶/                     # 检索增强生成
│   ├── RAG架构与核心流程.md        # Naive → Advanced → Modular RAG
│   ├── 向量数据库选型.md           # Pinecone/Weaviate/Qdrant/Chroma
│   ├── 高级RAG策略.md             # HyDE/Self-RAG/Agentic RAG
│   └── GraphRAG知识图谱.md        # 图+向量混合检索
│
├── 07-工具与Function Calling/      # 工具调用
│   ├── Function Calling机制.md    # OpenAI/Claude/Gemini 对比
│   ├── MCP Server开发.md          # Python/TS SDK 实战
│   └── 工具编排与安全.md           # 权限/审计/沙箱
│
├── 08-工具平台与沙箱/              # 工具基础设施
│   ├── Composio工具平台.md        # 1000+ 工具，MCP Gateway
│   ├── E2B代码沙箱.md             # 安全隔离执行环境
│   ├── Web数据工具详解.md          # ★ Firecrawl/Tavily/Exa/Jina/Brave/Apify
│   └── Agent工具生态总览.md        # 搜索/浏览器/数据/代码沙箱
│
├── 09-多Agent系统/                 # 多 Agent 协作
│   ├── 多Agent架构模式.md          # Supervisor/Swarm/Hierarchical
│   ├── Agent通信与协调.md          # 消息传递/Handoff/冲突解决
│   └── 人机协作与监督.md           # HITL/审批/渐进式自主
│
├── 10-记忆与状态/                  # Agent 记忆
│   ├── 短期与长期记忆.md           # 缓冲/摘要/向量/实体记忆
│   ├── 对话管理与上下文.md         # 多轮对话/上下文压缩
│   └── 知识库与经验学习.md         # 知识库/反思/自我改进
│
├── 11-Agent记忆框架/               # 记忆专用框架
│   ├── Mem0记忆层.md              # 图记忆，Y Combinator $24M
│   ├── Letta-MemGPT记忆系统.md    # OS 级分层记忆
│   └── Zep与LangMem.md           # 时序知识图谱
│
│  ═══════════════ 第五层：基础设施 ═══════════════
│
├── 12-模型服务/                    # LLM 接入与部署
│   ├── OpenAI与Claude API.md     # API 调用/流式/多模态
│   ├── 开源模型部署.md             # vLLM/Ollama/量化部署
│   └── 模型路由与网关.md           # LiteLLM/负载均衡
│
├── 13-AI网关与路由/                # AI 基础设施
│   ├── LiteLLM统一接口.md         # 100+ 模型统一 API
│   ├── Vercel AI SDK与Gateway.md  # TypeScript AI 网关
│   └── Portkey与AI网关对比.md     # 网关方案对比
│
├── 14-可观测与评估/                # 监控与评估
│   ├── LLM可观测性.md             # 链路追踪/Token 监控
│   ├── 可观测性平台详解.md         # LangSmith/LangFuse/Phoenix
│   ├── Agent评估与基准.md         # RAGAS/SWE-bench
│   └── 安全与对齐.md              # 注入防御/PII/Guardrails
│
├── 15-Agent安全与治理/             # 安全与治理
│   ├── Agent身份与权限.md         # OAuth2/RBAC/审计
│   └── Agent治理框架.md           # 四大支柱/合规/企业检查清单
│
│  ═══════════════ 第六层：工程化 ═══════════════
│
├── 16-Harness Engineering/         # ★ 核心方法论
│   ├── Harness Engineering完整指南.md  # 五大实践/自主循环/检查清单
│   ├── Context Engineering详解.md     # 六大上下文维度
│   ├── Kiro Harness实战配置.md        # Steering/Hooks/Specs 模板
│   ├── Harness Engineering开源项目.md  # ★ 开源项目与资源
│   └── Harness Engineering与CI-CD集成.md # ★ GitHub Actions 自动循环
│
├── 17-Coding Agent/                # 编程 Agent
│   ├── Claude Code与终端Agent.md  # 终端原生/CLAUDE.md/多 Agent
│   ├── Cursor-Kiro-Windsurf IDE Agent.md # IDE Agent 对比
│   ├── Devin与自主开发Agent.md    # 自主开发/SWE-bench
│   └── Vibe Coding与AI应用构建.md  # ★ Replit/v0/Bolt/Lovable
│
│  ═══════════════ 第七层：垂直场景 ═══════════════
│
├── 18-OpenClaw与Agent生态/         # Agent 生态系统
│   ├── 浏览器自动化Agent详解.md    # ★ Browser-Use/Skyvern/Agent-S 等
│   ├── Computer Use与浏览器Agent.md # Claude Computer Use/Nova Act
│   ├── OpenClaw平台详解.md        # Skills/Heartbeat/20+ 渠道
│   ├── Agent Skills生态.md        # Skills/Tools/Plugins 对比
│   ├── AgentOS生态.md             # ★ OpenClaw/ZeroClaw/OpenFang
│   └── SkillHub企业技能注册中心.md  # ★ 讯飞开源，企业私有技能注册中心
│
├── 19-Voice Agent/                 # ★ 语音 Agent（2026 热门方向）
│   ├── 语音Agent与实时交互.md      # OpenAI Realtime/ElevenLabs/LiveKit/Vapi
│   └── 语音Agent开发实战.md        # 完整开发指南 + 设计模式
│
├── 20-Agent支付/                   # ★ AI Agent 支付体系
│   ├── 01-入门/                          # 零基础入门读物
│   │   ├── 01-支付系统基础与安全.md       # 四方模型/授权捕获结算/Tokenization/KYC/PCI DSS
│   │   ├── 02-支付行业术语小白指南.md     # 术语字典，随时查阅
│   │   └── 03-X402开发者区块链最小知识.md # 链上基础概念
│   ├── 02-行业知识/                      # 行业深度分析
│   │   ├── 01-Agent支付协议与产品设计.md  # 协议对比/产品架构
│   │   ├── 02-AI Agent支付行业全景图.md   # 行业格局/趋势判断
│   │   ├── 03-AgentToken产品设计分析与竞品对比.md  # 竞品分析
│   │   ├── 04-Agent支付落地案例与中国市场.md       # 落地案例
│   │   └── 05-Agent支付风控与经济学.md    # 风控/经济模型
│   ├── 03-工程实现/                      # 工程落地指南
│   │   ├── 01-AgentToken-CLI设计规范与数据模型.md  # CLI 设计
│   │   ├── 02-Agent支付全生命周期与费用结构.md     # 生命周期
│   │   ├── 03-X402链上支付基础设施工程实战.md      # X402 实战
│   │   ├── 04-AgentToken后端工程落地指南.md        # 后端工程
│   │   ├── 05-多签钱包与AWS-KMS签名基础.md        # 多签/KMS
│   │   ├── 06-支付系统记账入门.md                  # 记账基础
│   │   ├── 07-复式记账与对账生产级指南.md          # 复式记账
│   │   └── 08-多钱包与多链扩展方案.md              # 多链扩展
│   └── 04-项目需求/                      # 项目需求文档
│       └── X402-需求参考方案-v2.md        # 需求方案
│
│  ═══════════════ 第八层：平台与部署 ═══════════════
│
├── 21-云厂商Agent方案/             # 云厂商解决方案
│   ├── 阿里云百炼与通义.md         # 百炼/Qwen/DashScope
│   └── 云厂商Agent方案对比.md      # AWS/Azure/GCP/阿里/百度/腾讯/字节
│
├── 22-低代码平台/                  # 可视化构建
│   ├── Dify平台实践.md            # 工作流/知识库/Agent
│   ├── Coze与FastGPT.md          # Bot 构建/插件市场
│   └── n8n与Flowise.md           # 自动化工作流
│
│  ═══════════════ 第九层：技术更新 ═══════════════
│
├── 24-2026技术更新/                # ★ 2026 年技术动态追踪
│   └── 2026年AI Agent技术更新总览.md  # 框架/协议/Coding Agent 全面更新
│
│  ═══════════════ 第十层：实战 ═══════════════
│
└── 23-实战案例/                    # 项目实践
    ├── 智能客服Agent.md           # 多轮对话/知识库/人工转接
    ├── 代码助手Agent.md           # 代码生成/审查/MCP 集成
    ├── 数据分析Agent.md           # NL2SQL/可视化/报表
    ├── 研究助手Agent.md           # 多源搜索/论文分析
    ├── 自动化运维Agent.md         # 监控/告警/自动修复
    └── 内容创作Agent.md           # 多 Agent 协作创作
```

## 🎯 学习路径

```
第一阶段：认知（1-2 天）
  00-基础概念 → 01-设计模式 → 理解 Agent 是什么、怎么设计

第二阶段：协议（1 天）
  02-Agent协议 → 理解 MCP/A2A/AG-UI 生态

第三阶段：框架（3-5 天）
  03-Agent框架 → 选一个深入（推荐 LangGraph 或 CrewAI）
  04-框架补充 → Agent框架选型指南
  05-Java-TS → 多语言 Agent 开发

第四阶段：核心能力（1-2 周）
  06-RAG → 07-工具 → 08-工具平台
  09-多Agent → 10-记忆 → 11-记忆框架

第五阶段：基础设施（3-5 天）
  12-模型服务 → 13-AI网关 → 14-可观测
  15-安全治理

第六阶段：工程化（1 周）
  16-Harness Engineering → 17-Coding Agent
  这是提升 AI coding 效率的关键

第七阶段：垂直场景（按需）
  18-OpenClaw与Agent生态 → 浏览器自动化/Agent OS
  19-Voice Agent → 语音交互
  20-Agent支付 → 支付协议/令牌化/合规体系

第八阶段：平台与部署（持续）
  21-云厂商 → 22-低代码平台

第九阶段：实战（持续）
  23-实战案例 → 选一个方向深入
```

## 📊 技术全景图

```
+------------------------------------------------------------------+
|                        AI Agent 技术全景                            |
+------------------------------------------------------------------+
|                                                                    |
|  用户层    AG-UI <-> 前端 UI <-> A2UI                              |
|           ------------------------------------------               |
|  Agent层   Agent A <-A2A/ACP-> Agent B <-ANP-> Agent C            |
|           ------------------------------------------               |
|  工具层    MCP Server | Composio | E2B | Browser-Use              |
|           ------------------------------------------               |
|  转换层    Open-CLI | CLI-Anything | Higress                      |
|           ------------------------------------------               |
|  模型层    GPT-4o | Claude | Gemini | Qwen | Llama | DeepSeek    |
|           ------------------------------------------               |
|  基础设施  LiteLLM | Portkey | LangSmith | LangFuse              |
|           ------------------------------------------               |
|  工程化    Harness Engineering | CI/CD | Kiro Steering            |
|           ------------------------------------------               |
|  运行时    LangGraph | CrewAI | OpenFang | AgentCore              |
|                                                                    |
+------------------------------------------------------------------+
```

## 🔗 相关资源

### 官方文档

- [LangGraph](https://langchain-ai.github.io/langgraph/) | [CrewAI](https://docs.crewai.com/) | [OpenAI Agents SDK](https://openai.github.io/openai-agents-python/)
- [MCP 规范](https://modelcontextprotocol.io/) | [A2A 协议](https://google.github.io/A2A/)
- [Google ADK](https://google.github.io/adk-docs/) | [AWS Strands](https://strandsagents.com/)

### Harness Engineering

- [OpenAI 论文](https://openai.com/index/harness-engineering)
- [LangChain Deep Agents](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/)
- [nxcode 完整指南](https://www.nxcode.io/resources/news/harness-engineering-complete-guide-ai-agent-codex-2026)

### 浏览器自动化

- [Browser-Use](https://browser-use.com/) | [Skyvern](https://github.com/Skyvern-AI/skyvern) | [Agent-S](https://github.com/simular-ai/Agent-S)

### Agent OS

- [OpenClaw](https://github.com/openclaw/openclaw) | [OpenFang](https://github.com/RightNow-AI/openfang)

### 协议转换

- [Higress](https://github.com/alibaba/higress) | [Open-CLI](https://opencli.info/) | [CLI-Anything](https://github.com/HKUDS/CLI-Anything)

### 低代码平台

- [Dify](https://docs.dify.ai/) | [Coze](https://www.coze.com/) | [FastGPT](https://fastgpt.in/)
