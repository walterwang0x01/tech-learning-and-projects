# AI Agent 周报 — 2026 第 25 周 (06-15 ~ 06-21)

> Author: Walter Wang
> 本周 AI Agent 领域关键事件回顾与趋势研判。

---

## 🏆 本周 Top 5

### 1. GPT-5.6 即将落地：Agent 能力成模型竞赛主轴

OpenAI 首席科学家 Jakub Pachocki 内部确认 GPT-5.6 是 GPT-5.5 的「有意义提升」，release candidate 代号 kindle-alpha 已现身 Codex 路由日志。Polymarket 合约定价 6/22-28 窗口释放概率 83-89%。

核心升级方向非单轮聊天而是 **agentic workflow**：token 效率提升 10-15%、上下文窗口扩展至 1.5M tokens（较 GPT-5.5 增加 43%），定价仅约 Claude Fable 5 的三分之一。这进一步确立了 OpenAI 的六周一模型迭代节奏（5.4 → 5.5 → 5.6），Agent 能力在旗舰模型评估体系中的权重正在超越传统 benchmark。

同期 OpenAI 提交 S-1 冲刺 IPO（估值 $850B）、收购 Ona 增强 Codex runtime 持久化能力，整体叙事清晰：AI Agent 平台化。

### 2. MCP Enterprise-Managed Authorization (EMA) 正式稳定

6 月 18 日 MCP EMA 扩展宣布 stable。企业 IT 管理员可通过 Okta 等 IdP 一次性配置 MCP Connector 权限，员工首次登录自动继承——告别逐人 OAuth 确认窗口。Anthropic 在 Claude 中首发实现，C1 宣布原生支持。

配合此前 MCP 2026-07-28 RC（stateless core + Extensions + Tasks + MCP Apps）和 NSA 安全设计指南的发布，MCP 在 2026 H1 完成了从「开发者协议」到「企业级基础设施」的身份跃迁。截至年中已有 9,400+ 公开 MCP Server、1.5 亿次工具下载。

### 3. Vercel 发布 eve：文件系统优先的 Agent 框架

Vercel 在 Ship London 大会发布 eve——开源、TypeScript、filesystem-first 的 Agent 框架。Markdown 定义 instructions 和 skills，TypeScript 写 tools，一行 `vercel` 命令部署。框架内置：

- 持久执行（durable workflows）
- 沙箱计算
- Human-in-the-loop 审批
- 子 Agent 嵌套
- 多渠道接入（Slack、Web、API）

Guillermo Rauch (Vercel CEO) 称"下一个热门编程语言是 Markdown"。eve 的设计哲学与 ECC (Everything Claude Code, 210K stars) 类似——都在验证「Agent 配置即代码，Markdown 即接口」的范式。

### 4. LangGraph 曝三漏洞链可远程执行代码

安全研究者披露 LangGraph 自托管部署存在漏洞链，可实现 RCE。LangChain 已发布修复。同期 LangSmith 宣布端到端 OTel 支持，LangChain 发表 Loop Engineering 长文解析 Agent 核心循环设计模式。

LangChain 1.0 + LangGraph 3.0 在 IBM 等企业案例中实测 LLM 调用延迟 200-500ms、中位内存占用 1.2GB，但安全事件提醒：自托管 Agent runtime 必须纳入常规安全运维。

### 5. Anthropic 40 万会话研究 + Claude Design 企业化

Anthropic 发表基于 40 万 Claude Code 真实会话的研究，揭示人类专家在 Agent 辅助下依然不可替代的领域（架构决策、跨模块一致性、edge case 处理）。

同时 Claude Design 完成企业化改造：GitHub 设计系统导入、与 Claude Code 双向同步、/design 终端命令、画布直接编辑、企业品牌控制——从病毒式研究预览变成受治理的企业工作区。

---

## 📈 趋势总结

| 类型 | 趋势 |
|------|------|
| 🔺 上升 | **Agent 框架进入「文件系统优先」时代**：eve、ECC 都以目录结构+Markdown 定义 Agent，降低门槛的同时保留工程化可组合性 |
| 🔺 上升 | **MCP 制度化元年**：EMA stable + NSA 安全指南 + 9400 Server + CYFIRMA 攻击面报告——协议走完了从实验到基础设施的全周期 |
| 🔺 上升 | **模型厂商六周迭代节奏**：OpenAI 5.4→5.5→5.6，Agent 能力和 context window 是每次升级核心，对下游框架提出持续适配压力 |
| 🔺 上升 | **Context Engineering 取代 Prompt Engineering**：Sourcegraph、deepset、Taskade 等密集发布实践指南，共识是精心设计 context window 内容可将任务完成率从 30% 拉到 90% |
| 🆕 新兴 | **Agent 安全/治理论文爆发**：Deontic Policies、Sovereign Execution Brokers、Defensive Misdirection、AIBOM-VEX——学界正为产业规模 Agent 部署补安全债 |
| 🆕 新兴 | **具身 Agent 自主进化**：ENPIRE (自改进机器人策略)、RATs (Playful Agentic Robot Learning) 显示 Agent 正在突破纯数字环境 |
| 🔻 下降 | **静态 API 端点范式**：ToolPro 论文明确指出 static endpoint 无法表达 Agent 所需的长时序工作流，executable tool program 是替代方向 |

---

## 📄 论文精选

| 论文 | 核心贡献 | 链接 |
|------|----------|------|
| Deontic Policies for Runtime Governance | 用义务逻辑约束 Agent 运行时行为：显式声明 permitted/prohibited/obligated | [arXiv](https://arxiv.org/abs/2606.19464) |
| Beyond Static Endpoints: ToolPro | 用可执行 Tool Program 替代 REST 端点，支持循环、条件、joins、重试 | [arXiv](https://arxiv.org/abs/2606.19992) |
| ENPIRE: Robot Policy Self-Improvement | Coding Agent 自动搜索算法，在真实世界执行反馈循环实现策略自改进 | [arXiv](https://arxiv.org/abs/2606.19980) |
| Multi-Agent Transactive Memory | 跨 Agent 群体的知识检索基础设施——索引 Agent 产出供其他 Agent 复用 | [arXiv](https://arxiv.org/abs/2606.19911) |
| Sovereign Execution Brokers | 在 Agent 控制平面引入证书绑定强制执行点，隔离非确定性推理与变更权限 | [arXiv](https://arxiv.org/abs/2606.20520) |
| Agentic EDA: A Handoff Perspective | 将 LLM Agent 应用于电子设计自动化，分析多阶段 handoff 中的隐性需求传递 | [arXiv](https://arxiv.org/abs/2606.19795) |

---

## 🔥 热门项目

| 项目 | 描述 | 亮点 |
|------|------|------|
| [Vercel eve](https://vercel.com/blog/introducing-eve) | 文件系统优先 TypeScript Agent 框架 | 本周发布，Durable execution + 一键部署 |
| [ECC](https://www.augmentcode.com/learn/everything-claude-code-github) | Agent harness 配置系统 | 210K stars, 28 agents, 119 skills |
| [CrewAI v1.14+](https://github.com/crewAIInc/crewAI) | 多 Agent 编排框架 | 40K stars, Chat API, Snowflake Cortex |
| [LangGraph](https://github.com/langchain-ai/langgraph) | 状态机 Agent runtime | 3.0 + OTel + Loop Engineering |
| [GodeX](https://github.com/Ahoo-Wang/GodeX) | 开源 Responses API 网关 | 让 Codex CLI 调用国产大模型 |
| [Paca](https://github.com/Paca-AI/paca) | Human-AI 混合看板协作 | Go + WASM 插件 |

---

## 🔮 下周预测

1. **GPT-5.6 正式发布**：Polymarket 89% 概率指向 6/22-28 窗口，预计 agentic workflow benchmark 分数将显著领先 Fable 5
2. **MCP EMA 生态跟进**：更多 IdP（Azure AD / Google Workspace）可能宣布 EMA 适配
3. **Vercel eve 早期采用者反馈**：框架刚发布一周，预期社区会出现首批生产案例和性能基准测试
4. **Agent 安全治理标准化推进**：NSA 指南 + 学术论文密集可能催生行业自律/合规框架的讨论

---

*本周报覆盖 2026-06-15 至 2026-06-21 期间的 AI Agent 领域动态。*
