# 云厂商 Agent 方案对比
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 主要厂商方案总览

```
┌─────────────────────────────────────────────────────────────┐
│                    全球云厂商 Agent 方案                       │
├──────────┬──────────┬──────────┬──────────┬────────────────┤
│   AWS    │ Microsoft│  Google  │ 阿里云    │  其他中国厂商   │
├──────────┼──────────┼──────────┼──────────┼────────────────┤
│ Strands  │ Agent FW │  ADK     │ 百炼平台  │ 百度文心       │
│ AgentCore│ SK+AutoGen│ Vertex  │ DashScope│ 腾讯混元       │
│ Nova Act │ Copilot  │ A2A     │ 通义千问  │ 字节豆包       │
│          │ Studio   │ Protocol│          │                │
└──────────┴──────────┴──────────┴──────────┴────────────────┘
```

## 2. 综合对比表

| 维度 | AWS | Microsoft | Google | 阿里云 |
|------|-----|-----------|--------|--------|
| 开发框架 | Strands SDK | Agent Framework (SK+AutoGen) | ADK | 百炼 SDK |
| 框架类型 | 开源 | 开源 | 开源 | 部分开源 |
| 核心模型 | Claude/Nova/Llama | GPT-4o/o1 | Gemini 2.0 | Qwen-Max/Plus |
| 多模型支持 | Bedrock 全模型 | Azure OpenAI + 开源 | Gemini 为主 | 通义 + 第三方 |
| MCP 支持 | ✅ | ✅ | ✅ 原生 | ✅ |
| A2A 支持 | 有限 | 有限 | ✅ 原生 | 有限 |
| 多 Agent | GraphOrchestrator | AgentGroupChat/GraphFlow | Sequential/Parallel/Loop | 工作流编排 |
| 托管运行时 | AgentCore | Azure AI Foundry | Vertex AI Engine | 百炼应用中心 |
| 浏览器自动化 | Nova Act SDK | - | - | - |
| 低代码构建 | Bedrock Console | Copilot Studio | Agent Builder | 百炼控制台 |
| 可观测性 | CloudWatch | App Insights | Cloud Trace | 日志服务 SLS |
| 身份管理 | IAM | Azure AD | GCP IAM | RAM |
| 护栏/安全 | Bedrock Guardrails | Content Safety | Safety Filters | 内容安全 |

## 3. 中国云厂商对比

| 维度 | 阿里云百炼 | 百度文心 | 腾讯混元 | 字节豆包 |
|------|-----------|---------|---------|---------|
| 核心模型 | Qwen 系列 | ERNIE 系列 | 混元大模型 | 豆包大模型 |
| 开源模型 | Qwen2.5（开源） | ERNIE（部分开源） | 混元（部分开源） | 豆包（未开源） |
| Agent 平台 | 百炼 | 千帆 AppBuilder | 元器 | 扣子(Coze) |
| API 兼容性 | OpenAI 兼容 | 自有 API | OpenAI 兼容 | OpenAI 兼容 |
| 知识库 | ✅ | ✅ | ✅ | ✅ |
| 插件市场 | ✅ | ✅ | ✅ | ✅ 丰富 |
| 工作流 | ✅ | ✅ | ✅ | ✅ |
| 私有化部署 | ✅ | ✅ | ✅ | 有限 |
| 中文优化 | 强 | 强 | 中 | 中 |
| 价格竞争力 | 高 | 中 | 中 | 高 |

## 4. 协议支持对比

| 协议 | AWS | Microsoft | Google | 阿里云 |
|------|-----|-----------|--------|--------|
| MCP | Strands 原生 | Agent FW 集成 | ADK 原生 | API 支持 |
| A2A | 有限支持 | 有限支持 | 发起者，原生 | 跟进中 |
| OpenAPI | Bedrock Action Group | Plugins | FunctionTool | 插件系统 |
| Function Calling | ✅ | ✅ | ✅ | ✅ |

## 5. 部署与定价模型

```
AWS:
  开发: Strands SDK（免费开源）
  生产: AgentCore Runtime（按调用 + 计算时间）
  模型: Bedrock 按 Token 计费

Microsoft:
  开发: Agent Framework（免费开源）
  生产: Azure AI Foundry（按调用）
  低代码: Copilot Studio（按消息数订阅）

Google:
  开发: ADK（免费开源）
  生产: Vertex AI Agent Engine（按调用 + 计算）
  模型: Gemini API 按 Token 计费

阿里云:
  开发: 百炼控制台（免费额度）
  生产: DashScope API（按 Token 计费）
  私有化: 模型部署到 ECS/PAI
```

## 6. 场景选型指南

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| AWS 技术栈企业 | Strands + AgentCore | 原生集成，IAM 统一管理 |
| Microsoft 生态 | Agent Framework + Foundry | Office/Teams 集成，.NET 支持 |
| Google 生态 | ADK + Vertex AI | Gemini 原生，A2A 协议 |
| 中国市场 ToB | 百炼 + Qwen | 中文优化，合规，性价比 |
| 中国市场 ToC | 扣子(Coze) | 低代码，插件丰富，快速上线 |
| 多云/无锁定 | Strands/ADK + 自部署 | 开源框架，模型可切换 |
| 预算敏感 | Qwen 开源 + 自部署 | 模型免费，仅需算力成本 |
| 快速原型 | 任意低代码平台 | 百炼/Coze/千帆均可 |

## 7. 开源框架 vs 托管服务

```
开源框架（Strands / ADK / Agent FW）：
  ✅ 灵活定制，无厂商锁定
  ✅ 可切换模型和部署环境
  ✅ 社区生态和透明度
  ❌ 需自行管理基础设施
  ❌ 安全、监控需自建

托管服务（AgentCore / Foundry / Vertex）：
  ✅ 开箱即用，运维托管
  ✅ 内置安全、监控、扩缩容
  ✅ 企业级 SLA
  ❌ 厂商锁定风险
  ❌ 成本随规模增长

推荐策略：开源框架开发 → 托管服务部署生产
```

## 8. 2026 年重大进展

> 🔄 更新于 2026-04-21

<!-- version-check: Cloud Agent Solutions 2026-04, checked 2026-04-21 -->

### 各厂商最新动态

**AWS**：
- AgentCore GA 后持续迭代，新增 InvokeBrowser API（OS 级浏览器控制：鼠标、键盘、截图）
- Spring AI AgentCore SDK 开源，Java 企业级 Agent 开发原生支持
- VPC、PrivateLink、CloudFormation、资源标签全面支持
- 来源：[AWS API Changes](https://awsapichanges.com/archive/service/bedrock-agentcore)

**Microsoft**：
- Azure AI Foundry Agent Service GA（2026-03）：OpenAI 兼容 Responses API、VNet 隔离、Voice Live 预览、内置评估、MCP 认证
- Microsoft Agent Framework 1.0 GA（2026-04）：统一 AutoGen + Semantic Kernel，多 Agent 应用部署到 Azure App Service
- Microsoft Agent 365（2026-05-01 GA）：$15/用户/月，企业级 Agent 治理平台
- 来源：[Microsoft Tech Community](https://techcommunity.microsoft.com/blog/appsonazureblog/build-multi-agent-ai-apps-on-azure-app-service-with-microsoft-agent-framework-1-/4510017)

**Google**：
- Vertex AI Agent Engine Sessions + Memory Bank GA，Code Execution GA
- ADK for Java 1.0 发布：新 App 和 Plugin 架构、外部工具支持
- Agent Builder 持续迭代，定位为最完整的 Agent 开发栈
- 来源：[Google Cloud Release Notes](https://docs.cloud.google.com/vertex-ai/docs/release-notes)

**阿里云**：
- Qwen3 系列发布（2025-04-29）：混合推理 + MoE 架构，36T Token 训练，MoE 模型 131K 上下文窗口<!-- 修复于 2026-05-20: 发布时间从 2026-04 修正为 2025-04-29，上下文 1M 是 Qwen3.6-Plus 的特性 -->
- Qwen3.5-397B-A17B（2026-02-16）：397B 参数 MoE，仅激活 17B，GPQA Diamond 88.4，$0.60/M 输入 Token
- Qwen3.6-Plus / Qwen3.6-Max-Preview（2026-04-20）：增强 Agentic Coding 和多模态推理，Qwen3.6-Plus 提供 1M 上下文，Qwen3.6-Max-Preview 提供 262K 上下文
- Qwen3.6-35B-A3B 开源（Apache 2.0）：35B 总参数 / 3B 激活，SWE-Bench 73.4%
- 战略转向：从纯开源转向开源 + 闭源商业化并行
- 来源：[Alibaba Cloud Model Studio](https://www.alibabacloud.com/help/en/model-studio/newly-released-models)

### 更新后的综合对比表

| 维度 | AWS | Microsoft | Google | 阿里云 |
|------|-----|-----------|--------|--------|
| 开发框架 | Strands SDK | Agent Framework 1.0（SK+AutoGen 统一） | ADK（Python/TS/Java） | 百炼 SDK |
| 框架类型 | 开源 | 开源 | 开源 | 部分开源 |
| 核心模型 | Claude Opus 4.7/Nova/Llama | GPT-5.4/o3 | Gemini 2.5 Pro | Qwen3.6-Max/Plus |
| 多模型支持 | Bedrock 全模型 | Azure OpenAI + 开源 | Gemini 为主 + 开源 | 通义 + 第三方 |
| MCP 支持 | ✅ Stateful MCP | ✅ 原生认证 | ✅ 原生 | ✅ |
| A2A 支持 | 有限 | 有限 | ✅ 原生 | 有限 |
| 托管运行时 | AgentCore（GA） | Foundry Agent Service（GA） | Vertex AI Agent Engine（GA） | 百炼应用中心 |
| 浏览器自动化 | Nova Act + InvokeBrowser | - | - | - |
| 企业级 Agent 管理 | CloudWatch | Agent 365（$15/用户/月） | Agent Builder | 百炼控制台 |
## 🎬 推荐视频资源

### 🌐 YouTube
- [AWS re:Invent - Bedrock Agents](https://www.youtube.com/watch?v=F8NKVhkZZWI) — AWS Bedrock Agents
- [Google Cloud - Vertex AI Agents](https://www.youtube.com/watch?v=E8pMFNox4Lc) — Google Vertex AI Agent
- [Microsoft - Azure AI Agent Service](https://www.youtube.com/watch?v=pHksBVqH7uI) — Azure AI Agent

### 📺 B站
- [云厂商AI Agent方案对比](https://www.bilibili.com/video/BV1dH4y1P7FY) — 中文云厂商方案对比
