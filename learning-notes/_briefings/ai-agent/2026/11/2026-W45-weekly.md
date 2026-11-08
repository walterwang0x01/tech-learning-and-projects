# AI Agent 周报 — 2026-W45

> Author: Walter Wang
> 2026-11-02 至 2026-11-08：从常驻异步运行时，到权限、身份与生成式界面。

## 📌 头条

### Top 1｜常驻异步 Agent 成为运行时

DeepSeek 开源的 `dsh-superagent` 用一个常驻 router 接事件，再把任务放进多个隔离 worker session，只在需要决策时找人。

LangChain 同周发布托管 Deep Agents 与异步子 agent 方案，把持久执行、沙箱、可观测性和后台通知做成运行时能力。

AWS 则让 Step Functions 直接成为 agent 工具，把已有的 220 多个服务编排交给 agent 触发。

这几条共同说明，竞争重点正在从“模型会不会调用工具”移到“长任务怎样持续运行、隔离失败并让人随时接管”。

→ [dsh-superagent](https://github.com/deepseek-ai/dsh-superagent-prototype) / [LangChain 异步 Agent](https://www.langchain.com/blog/agents-are-going-async) / [AWS Roundup](https://aws.amazon.com/blogs/aws/aws-weekly-roundup-gpt-6-1-terra-on-bedrock-step-functions-as-agent-tools-and-more-november-2-2026)

---

### Top 2｜Agent 安全扩到完整执行面

MCP 工具投毒研究跑了 12 个框架、18 个模型和 45 种攻击场景，共形成 9720 个测试单元，整体攻击成功率为 22.9%；作者称 12 个框架都没有有意实现这类防护。

Cloudflare 提出的可信委托把 User、Agent、Operator 分开，让服务端不只看到自动流量，还能判断谁授权了谁。

Apiiro 的公开 GitHub 扫描又发现，Claude Code 的永久授权规则可能把命令里的密钥一起写入本地配置，并扩散到 Git 历史和 fork。

本周的安全主线很清楚：prompt injection 只是入口，真正要管的是工具元数据、执行权限、身份委托、凭据存储和撤销。

→ [MCP 投毒研究](https://arxiv.org/abs/2611.03555) / [Cloudflare 委托方案](https://blog.cloudflare.com/trusted-agent-delegation) / [Apiiro 报告](https://apiiro.com/blog/coding-agents-leaking-secrets-github-dont-ask-again)

---

## ⚡ 快讯

- **Top 3｜Kimi K3.1 Pro 开放权重**：Moonshot AI 的官方模型卡将它描述为原生多模态、面向 agent 的 3T 级模型；架构沿用 2.8T 总参数、约 104B 激活参数和 1M token 上下文，开放权重给自托管多了一项强力但昂贵的选择 → [官方模型卡](https://huggingface.co/moonshotai/Kimi-K3.1-Pro)
- **Top 4｜LangSmith BYOC 扩到三大云**：AWS 版正式 GA，Azure 和 Google Cloud 进入 Beta；trace、eval、数据集和 agent 部署留在客户云账户，说明可观测性产品开始把数据主权当成核心交付能力 → [LangChain 公告](https://www.langchain.com/blog/langsmith-byoc-aws-gc-azure)
- **Top 5｜生成式 UI 进入协作软件**：Vercel 把 Chat SDK agent 的 JSON spec 流式转换成 Slack Block Kit 与 Teams Adaptive Cards，并用类型目录、最终校验和平台限额约束输出；agent 回答开始从文字升级为可交互工作界面 → [Vercel 更新](https://vercel.com/changelog/json-render-and-chat-sdk-agents)
- **本周加看｜Agent 记忆开始离线整理**：Anthropic 公开 Claude 的“白天记日志、空闲时回放并改写记忆”做法，和 Zep 从已验证轨迹编译 Skills 的论文一起，把长期记忆从存聊天记录推进到提炼可复用规则 → [Anthropic](https://www.anthropic.com/research/components-of-agent-memory)
- **本周加看｜固定模型再比较 harness**：IBM CUGA 的 90 个 AppWorld 任务对照称，仅替换 harness 就让同一开放模型的完成率从 30% 变到 81%；选框架时应把模型固定、任务固定、成本固定后再测 → [IBM Research 说明](https://huggingface.co/blog/ibm-research/cuga-harness)

## 📦 项目 & 论文

| 热门项目 | 本周看点 | 链接 |
|------|------|------|
| Promethevs | 用 64GB RAM、12GB GPU 和约 1.1TB NVMe 运行 510GB DeepSeek-V4.1-Flash；项目明确标注尚无第二台机器复现 | [→](https://github.com/Magnvs7/Promethevs) |
| Agentic Identity Broker | Zalando 开源的 OAuth 委托代理，为 agent 获取短期、受范围约束的访问凭据 | [→](https://github.com/zalando-incubator/agentic-identity-broker) |
| json-render | 让模型只组合预先允许的组件与动作，再渲染成原生协作软件卡片 | [→](https://github.com/vercel-labs/json-render) |
| Cordonix 0.4.1 | C11 编写的本地 agent 执行与文件工作区工具，本周连续迭代 MCP 说明与更新体验 | [→](https://www.oschina.net/news/503467) |

## 📄 论文精选

| 论文 | 关键贡献 | 链接 |
|------|------|------|
| Internet of Agentics | 用三层架构梳理 MCP、A2A、Skills、运行时、注册发现与跨组织治理 | [→](https://arxiv.org/abs/2611.03066) |
| Learning by Doing | 只用已验证轨迹编译 Skills，让较弱模型通过率提高 4.5 至 18.8 个百分点 | [→](https://arxiv.org/abs/2611.01386) |
| Optimize the Harness, Not the Model | 最小化自托管 agent harness，在作者留出集上达到 83.8% 通过率 | [→](https://arxiv.org/abs/2611.03434) |
| Signed, Sealed, Leaked | 指出 MCP 工具签名只能证明来源，不能证明运行时不会泄露数据 | [→](https://arxiv.org/abs/2611.06585) |

## 🗓 下周预测

- OpenAI Agent Builder 距 11 月 30 日关闭更近，迁移到 Agents SDK 或 Workspace Agents 的实战问题会增多。→ [迁移说明](https://developers.openai.com/api/docs/guides/agent-builder)
- `.claude/`、`.cursor/` 等 agent 配置目录会被更多团队纳入 pre-commit、CI 与 Git 历史密钥扫描。→ [事件核查](https://thehackernews.com/2026/11/claude-codes-dont-ask-again-file.html)
- 生成式 UI 的讨论会从“能画卡片”转向错误修复、权限确认和 Slack、Teams 限额下的降级策略。→ [API 文档](https://json-render.dev/docs/api/chat)
- harness 对照评测会继续升温，固定模型、任务和预算后比较运行框架会比单看模型榜单更有参考价值。→ [CUGA 对照](https://huggingface.co/blog/ibm-research/cuga-harness)

> 注：本周回顾会复用当周日报的一手链接，这是周报汇总所需；外部来源内容已按许可限制要求改写。

## 📈 趋势

- 🆕 协作软件原生生成式 UI：agent 开始直接生成受约束的卡片、表格与按钮
- 🆕 从已验证轨迹编译 Skills：程序性记忆不再只靠人手写
- 🆕 可信 Agent 委托：服务端同时识别用户、agent 与托管方
- 🔺 常驻、异步和事件驱动运行时：长任务与对话线程逐步分离
- 🔺 harness 工程与固定模型对照：框架差异开始被单独量化
- 🔺 身份、权限和凭据治理：安全焦点从输出内容扩到完整执行链
- 🔻 手写全部 agent runtime：托管持久化、沙箱和观测能力正在减少重复建设
- 🔻 只看模型榜单选技术栈：同模型换 harness 的差距足以推翻结论
- 🔻 把明文密钥直接写进命令：永久授权规则会把一次输入变成长久暴露
