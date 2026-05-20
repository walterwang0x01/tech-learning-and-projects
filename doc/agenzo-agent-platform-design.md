# Agenzo Agent Platform — 设计文档

> Author: Walter Wang
> 版本: v0.1 Draft
> 日期: 2026-05-19
> 定位: 支付行业 AI Agent 的参考架构——安全、成本控制、可观测性、垂直 Skill 的完整实现

## 1. 背景与动机

### 1.1 行业现状

2026 年 Agent 生态正在经历三个并行的结构性变化：

1. **MCP 成为事实标准但安全远落后**：9700 万次安装、加入 Linux Foundation、AWS/Anthropic/Google 三家原生集成。但 OX Security 4 月披露协议层 RCE 影响 20 万台服务器，Help Net Security 报告 25% MCP server 存在 RCE 路径。
2. **Agent 成本失控**：Steinberger 公开账单 3 人 100 agent 月烧 $130 万；Anthropic 6/15 把 Agent SDK 拆出独立计费池起步 $100/月；Cloudflare 裁员 1100 人明确归因 agentic AI。
3. **垂直 Skill Pack 成为商业化标准范式**：Anthropic 一周发 Claude for Finance（10 模板）+ Claude for Legal（20 MCP connector），Addy Osmani Agent Skills 26K stars。

### 1.2 支付行业的特殊需求

支付 toB SaaS 对 Agent 有三个额外约束：
- **合规审计**：每笔 Agent 决策必须可追溯（PCI DSS / 反洗钱 / 数据保护）
- **成本敏感**：交易费率本身薄（0.6%-2.9%），AI 成本失控直接侵蚀利润
- **高可用**：支付链路不能因 LLM 超时/限流而中断

### 1.3 目标

构建一个**支付行业 Agent 开发者平台的参考实现**，包含四个核心模块：
1. MCP Tool Guard（安全）
2. LLM Cost Tracker（FinOps）
3. Agent Trace（可观测性）
4. Payment Skill Pack（垂直能力）

## 2. 架构总览

### 2.1 系统分层

```
┌─────────────────────────────────────────────────────────────────┐
│                        用户 / 商户 / 内部运营                      │
├─────────────────────────────────────────────────────────────────┤
│  Skill Layer          │ Payment Skill Pack                       │
│  (业务能力)            │ ├─ 商户接入引导 Skill                     │
│                       │ ├─ 支付文档问答 Skill                     │
│                       │ ├─ 对账分析 Skill                         │
│                       │ └─ 故障排查 Skill                         │
├─────────────────────────────────────────────────────────────────┤
│  Agent Runtime        │ SceneRouter + LangGraph State Machine     │
│  (编排层)             │ ├─ 意图识别 → 场景路由                     │
│                       │ ├─ 多步工作流编排                          │
│                       │ └─ 人工兜底 / 转接                        │
├─────────────────────────────────────────────────────────────────┤
│  Gateway Layer        │ Unified LLM Client                       │
│  (网关层)             │ ├─ 多模型路由 (Claude/DeepSeek/Qwen/GPT)  │
│                       │ ├─ MCP Tool Guard (安全拦截)              │
│                       │ ├─ Cost Tracker (成本归因)                │
│                       │ └─ Agent Trace (审计日志)                 │
├─────────────────────────────────────────────────────────────────┤
│  Provider Layer       │ AWS Bedrock │ DeepSeek API │ 千问 DashScope│
│  (模型层)             │ OpenAI API  │ 本地 Ollama  │ 其他         │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 核心设计原则

| 原则 | 说明 | 参考 |
|------|------|------|
| Provider-Agnostic | 所有模型通过统一接口调用，切换不改业务代码 | [Portkey AI Gateway](https://github.com/Portkey-AI/gateway) |
| Security by Default | 工具调用默认拒绝，白名单放行 | [Microsoft MCP Control Plane](https://developer.microsoft.com/blog/securing-mcp-a-control-plane-for-agent-tool-execution) |
| Cost-Aware Routing | 按任务复杂度自动选择性价比最优模型 | [Helicone Cost Tracking](https://docs.helicone.ai/features/alerts) |
| Observable | 每次 LLM/工具调用产生结构化 trace | [LangSmith Agent Observability](https://www.langchain.com/blog/agent-observability-powers-agent-evaluation) |
| Skill-as-Package | 业务能力打包为可组合、可评测的标准化单元 | [Google ADK Skills](https://developers.googleblog.com/developers-guide-to-building-adk-agents-with-skills/) |

## 3. 模块一：Unified LLM Client + Cost Tracker

### 3.1 设计参考

| 产品 | 核心能力 | 我们借鉴什么 |
|------|----------|-------------|
| **Portkey AI Gateway** | 统一接口路由 1600+ 模型，fallback/load-balance/cache | 路由策略 + OpenAI 兼容协议 |
| **Helicone** | 一行代码接入，custom properties 做成本归因 | 零侵入接入 + 多维标签 |
| **LangSmith LLM Gateway** | spend limits + PII redaction + trace continuity | 运行时治理策略 |
| **Langfuse** | 开源 observability + cost tracking | 自托管 + 开源方案 |

### 3.2 接口设计

```python
from agenzo.gateway import LLMClient, ModelTier

client = LLMClient(
    providers={
        "bedrock": {"model": "anthropic.claude-3-5-sonnet", "region": "us-east-1"},
        "deepseek": {"model": "deepseek-chat", "base_url": "https://api.deepseek.com/v1"},
        "qwen": {"model": "qwen-max", "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1"},
    },
    default_tier=ModelTier.FAST,
    daily_budget_usd=50.0,  # 超出报错
)

# 按 tier 路由
response = client.chat(
    messages=[{"role": "user", "content": "查询订单状态"}],
    tier=ModelTier.CHEAP,       # cheap=DeepSeek Flash, fast=DeepSeek Pro, critical=Claude
    metadata={
        "tenant_id": "merchant_abc",
        "scene": "order_query",
        "feature": "intent_detection",
    },
)
```

### 3.3 ModelTier 路由策略

| Tier | 适用场景 | 默认模型 | 价格参考 |
|------|----------|----------|----------|
| `CRITICAL` | 金融决策、合规判断、复杂推理 | Claude Opus 4.7 via Bedrock | ~$25/M output |
| `FAST` | 意图识别、实体提取、摘要 | DeepSeek V4-Pro | ~$3.48/M output |
| `CHEAP` | 分类、格式化、简单问答 | DeepSeek V4-Flash / Qwen | ~$0.5-1/M output |
| `LOCAL` | 隐私敏感、离线场景 | Ollama (Qwen 3.6-27B) | 电费 |

### 3.4 成本归因数据模型

每次调用自动记录：

```python
@dataclass
class LLMCallRecord:
    trace_id: str           # 关联到一次完整业务流程
    tenant_id: str          # 哪个商户
    scene: str              # 哪个业务场景
    feature: str            # 哪个具体功能
    provider: str           # bedrock / deepseek / qwen
    model: str              # 具体模型名
    tier: str               # critical / fast / cheap / local
    input_tokens: int
    output_tokens: int
    cost_usd: float         # 按各 provider 价格表实时计算
    latency_ms: int
    cache_hit: bool         # 是否命中缓存
    ts: datetime
```

### 3.5 浪费识别规则（内置）

| 规则 | 触发条件 | 优化建议 |
|------|----------|----------|
| 重复调用 | 同一 tenant + 同一 prompt hash 在 60s 内出现 3+ 次 | 启用 semantic cache |
| 模型过配 | CRITICAL tier 但 input < 100 tokens 且无工具调用 | 降级到 FAST |
| 上下文膨胀 | input_tokens > 10K 但 output < 200 tokens | 裁剪上下文 |
| 空转循环 | 同一 trace 内 LLM 调用 > 10 次 | 加 max_steps 限制 |

## 4. 模块二：MCP Tool Guard

### 4.1 设计参考

| 产品/论文 | 核心能力 | 我们借鉴什么 |
|-----------|----------|-------------|
| **Microsoft MCP Control Plane** | 验证 MCP 调用是否 permitted、properly scoped、auditable | 三层验证模型 |
| **MCP-SandboxScan** (arXiv) | WASM 隔离 + 静态策略 + 动态 taint 分析 + 异常评分 | 沙箱 + 异常检测 |
| **Nightfall AI MCP Checklist** | 10 步安全清单：发现→身份→最小权限→协议检查→DLP | 运营流程 |
| **Google Cloud MCP Best Practices** | 专用 service account + 最小权限 + 审计 | IAM 模式 |
| **Pomerium Agentic Gateway** | 身份感知代理，per-tool 授权 | 零信任模型 |

### 4.2 安全分层

```
用户请求
  ↓
  ┌─────────────────────────────────────┐
  │ Layer 1: Schema Validation          │  ← 参数类型/格式/长度校验
  │   Pydantic model 严格匹配           │     挡掉 70% 低级注入
  ├─────────────────────────────────────┤
  │ Layer 2: Permission Check           │  ← 白名单：谁能调什么工具
  │   RBAC: user_role × tool_name       │     支持 per-tenant 配置
  ├─────────────────────────────────────┤
  │ Layer 3: Content Inspection         │  ← 参数内容检查
  │   - Shell metachar 检测             │     
  │   - SQL injection 模式              │     
  │   - Path traversal 检测             │     
  │   - PII/敏感数据脱敏                │     
  ├─────────────────────────────────────┤
  │ Layer 4: Sandbox Execution          │  ← 高危工具在沙箱里跑
  │   Docker/gVisor, cap-drop=ALL       │     
  │   网络 allowlist, 文件系统只读       │     
  ├─────────────────────────────────────┤
  │ Layer 5: Audit Log                  │  ← 每次调用留痕
  │   (user_id, tool, params, result)   │     
  └─────────────────────────────────────┘
  ↓
  MCP Server / 外部工具
```

### 4.3 权限配置示例

```yaml
# tool_permissions.yaml
roles:
  merchant_basic:
    allowed_tools:
      - order_query
      - payment_status
      - document_search
    denied_tools:
      - refund_execute    # 需要 merchant_admin
      - database_write    # 永远不允许
      - shell_execute     # 永远不允许

  merchant_admin:
    allowed_tools:
      - order_query
      - payment_status
      - document_search
      - refund_execute    # 需要二次确认
    requires_confirmation:
      - refund_execute

  internal_ops:
    allowed_tools: ["*"]
    denied_tools:
      - shell_execute
      - database_drop
```

### 4.4 支付场景特有的安全规则

| 规则 | 说明 | 实现 |
|------|------|------|
| 金额上限 | Agent 单次操作金额不超过阈值 | 参数校验 `amount <= max_amount` |
| 频率限制 | 同一商户每分钟退款操作不超过 N 次 | Redis 滑动窗口 |
| 敏感字段脱敏 | 卡号、CVV 不进 LLM 上下文 | 正则替换 + PII 检测 |
| 操作确认 | 涉及资金变动的操作需人工确认 | 中断 Agent 流程，等待审批 |

## 5. 模块三：Agent Trace（可观测性 + 审计）

### 5.1 设计参考

| 产品 | 核心能力 | 我们借鉴什么 |
|------|----------|-------------|
| **LangSmith** | Trace → Run → Thread 三层结构；Engine 自动聚类故障 | 分层 trace 模型 |
| **SmithDB** | Agent 观测专用分布式 DB，比通用 OLAP 快 12x | 专用存储设计 |
| **Phoenix by Arize** | OpenTelemetry 兼容，开源自托管 | OTel 标准 |
| **Langfuse** | 开源 baseline，支持 score/feedback | 评分机制 |
| **阿里 LoongSuite GenAI SemConv** | AI Agent 标准化可观测语义规范 | 语义约定 |

### 5.2 Trace 数据模型

```
Thread (一次用户会话)
  └─ Trace (一次完整业务流程，如"帮商户查订单")
       ├─ Span: intent_detection (LLM 调用)
       ├─ Span: tool_call.order_query (MCP 工具调用)
       ├─ Span: llm_response_generation (LLM 调用)
       └─ Span: tool_call.send_notification (飞书通知)
```

每个 Span 记录：
- `span_id` / `parent_span_id` / `trace_id`
- `type`: llm_call | tool_call | retrieval | human_handoff
- `input` / `output`（可配置脱敏级别）
- `tokens` / `cost` / `latency`
- `status`: success | error | timeout | rejected
- `metadata`: tenant_id, scene, model, tool_name

### 5.3 支付合规审计需求

支付行业对 Agent 审计有额外要求：

| 合规要求 | Agent Trace 如何满足 |
|----------|---------------------|
| PCI DSS：敏感数据不落盘 | Trace 中卡号/CVV 自动脱敏后再存储 |
| 反洗钱：可疑交易可追溯 | 每笔涉及资金的 Agent 决策有完整 trace |
| GDPR：用户数据可删除 | 按 tenant_id 批量删除 trace |
| 内部审计：谁做了什么 | 每个 trace 关联 operator_id |
| 监管报告：定期导出 | 按时间范围 + 场景导出 CSV/JSON |

### 5.4 告警规则

| 告警 | 触发条件 | 通知渠道 |
|------|----------|----------|
| 成本异常 | 单商户日成本超过历史 P95 的 3 倍 | 飞书群 + 邮件 |
| 错误率飙升 | 某场景 5 分钟内错误率 > 20% | PagerDuty |
| 工具调用异常 | 被 Tool Guard 拦截次数 > 10/min | 安全团队飞书群 |
| 空转检测 | 单 trace 内 LLM 调用 > 15 次未完成 | 开发者飞书 |

## 6. 模块四：Payment Skill Pack

### 6.1 设计参考

| 产品/模式 | 核心能力 | 我们借鉴什么 |
|-----------|----------|-------------|
| **Anthropic Claude for Finance** | 10 个金融 Agent 模板，GitHub 两天 6000 stars | 模板化 + 开源 |
| **Google ADK SkillToolset** | Progressive disclosure，按需加载上下文 | 按需加载 |
| **Spring AI Agent Skills** | 模块化文件夹：instructions + scripts + resources | 文件结构 |
| **Addy Osmani Agent Skills** | 20 个 SDLC 工作流，26K stars | 工程纪律 |
| **skillmatic-ai/awesome-agent-skills** | 社区精选 Skill 目录 | 生态建设 |

### 6.2 Skill Pack 标准结构

```
skills/
├── payment-onboarding/           # 商户接入引导 Skill
│   ├── manifest.yaml             # 元数据：名称、版本、依赖、工具清单
│   ├── prompts/
│   │   ├── system.md             # 系统提示词
│   │   ├── few_shots.yaml        # Few-shot 示例
│   │   └── variants/             # 不同模型的 prompt 变体
│   │       ├── claude.md
│   │       └── deepseek.md
│   ├── tools/
│   │   ├── check_merchant_status.py
│   │   ├── generate_api_key.py
│   │   └── run_integration_test.py
│   ├── workflows/
│   │   └── onboarding_flow.yaml  # 状态机定义
│   ├── evaluations/
│   │   ├── golden_set.yaml       # 20+ 测试 case
│   │   └── metrics.yaml          # 验收指标定义
│   └── docs/
│       └── README.md             # 使用说明
│
├── payment-doc-qa/               # 支付文档问答 Skill
├── reconciliation/               # 对账分析 Skill
└── troubleshooting/              # 故障排查 Skill
```

### 6.3 manifest.yaml 示例

```yaml
name: payment-onboarding
version: "1.0.0"
description: 引导商户完成支付接入全流程
author: Walter Wang
license: MIT

# 依赖
requires:
  models: ["claude-3-5-sonnet", "deepseek-chat"]  # 至少支持其一
  tools: ["check_merchant_status", "generate_api_key", "run_integration_test"]
  context: ["payment_api_docs"]  # 需要加载的知识库

# 适用场景
triggers:
  - intent: "merchant_onboarding"
  - intent: "api_integration_help"
  - keywords: ["接入", "集成", "API Key", "webhook"]

# 工作流
workflow: workflows/onboarding_flow.yaml

# 评测
evaluation:
  golden_set: evaluations/golden_set.yaml
  pass_threshold: 0.85  # 85% case 通过才算合格
  metrics:
    - completion_rate    # 商户是否走完全流程
    - accuracy           # 回答是否正确
    - safety             # 是否泄露敏感信息
```

### 6.4 支付场景 Skill 优先级

| Skill | 价值 | 难度 | 建议顺序 |
|-------|------|------|----------|
| **支付文档问答** | 高（降低客服成本） | 低（RAG 标准场景） | 第 1 个做 |
| **商户接入引导** | 高（加速 GMV 起量） | 中（有状态流程） | 第 2 个做 |
| **故障排查** | 中（减少工单） | 中（需要接监控数据） | 第 3 个做 |
| **对账分析** | 中（省 BD 时间） | 高（需要 BI 数据） | 第 4 个做 |

## 7. 技术选型

### 7.1 核心技术栈

| 层 | 选型 | 理由 |
|----|------|------|
| 语言 | Python 3.12+ | 团队已有 FastAPI 经验，LLM SDK 生态最完整 |
| Agent 框架 | LangGraph | 状态机编排 + 异步子 Agent + 生产验证 |
| LLM SDK | OpenAI 兼容协议 | DeepSeek/千问/Bedrock 都支持，一套代码切换 |
| 工具调用 | MCP 协议 | 行业标准，但必须加 Tool Guard |
| 可观测性 | OpenTelemetry + 自建 | OTel 标准 + 支付合规定制 |
| 存储 | ClickHouse (trace) + Redis (热数据) + S3 (归档) | 分层存储 |
| 前端 | Vue 3 + Naive UI | 与 agenzo 现有栈一致 |
| 部署 | Docker + K8s | 公司现有基础设施 |

### 7.2 外部依赖

| 依赖 | 用途 | 替代方案 |
|------|------|----------|
| AWS Bedrock | Claude 模型调用 | Anthropic 直连 API |
| DeepSeek API | 高性价比模型 | 千问 DashScope |
| Ollama | 本地模型（开发/测试） | vLLM |
| ClickHouse | Trace 存储 + 分析 | PostgreSQL (小规模) |
| Redis | 缓存 + 限流 + 权限热加载 | — |
| Grafana | Dashboard 可视化 | 自建 Vue 页面 |

## 8. 执行计划

### 8.1 Phase 1：基础层（第 1-2 周）

**目标**：统一 LLM Client + 成本追踪跑通

| 天 | 任务 | 产出 |
|----|------|------|
| D1-2 | 实现 `LLMClient` 类，支持 Bedrock + DeepSeek 两个 provider | `agenzo/gateway/client.py` |
| D3 | 实现 `ModelTier` 路由逻辑 + 价格表 | `agenzo/gateway/router.py` |
| D4-5 | 实现 `LLMCallRecord` 数据模型 + JSON 文件落盘 | `agenzo/gateway/tracker.py` |
| D6-7 | 跑通一次完整的 payment-api skill 调用，看到成本数据 | 第一份真实数据 |
| D8-10 | 接 Grafana dashboard（或简单 CLI 报表） | 可视化 |

**验收标准**：
- [ ] 用同一份代码调用 Claude 和 DeepSeek，输出格式一致
- [ ] 每次调用自动记录 tokens + cost + latency
- [ ] 能按 tenant_id / scene / model 维度查询成本
- [ ] daily_budget_usd 超出时报错而不是默默扣费

### 8.2 Phase 2：Skill Pack 标准化（第 3-4 周）

**目标**：把现有 payment-api skill 升级为标准化 Skill Pack

| 天 | 任务 | 产出 |
|----|------|------|
| D1-3 | 重构 `agenzo-payment-api.md` 为标准目录结构 | `skills/payment-doc-qa/` |
| D4-5 | 编写 20 个评测 case（golden_set.yaml） | 验收基线 |
| D6-7 | 实现 Skill 加载器（读 manifest → 注入 prompt + tools） | `agenzo/skills/loader.py` |
| D8-10 | 跑评测，记录 Claude vs DeepSeek 在这些 case 上的通过率 | 第一份模型对比数据 |

**验收标准**：
- [ ] Skill 目录结构符合 manifest.yaml 规范
- [ ] 20 个评测 case 覆盖正常流程 + 边界情况 + 安全测试
- [ ] 评测通过率 ≥ 85%（Claude）/ ≥ 75%（DeepSeek）
- [ ] 新 Skill 上线只需要加一个目录，不改框架代码

### 8.3 Phase 3：安全层（第 5-6 周）

**目标**：MCP Tool Guard 核心功能上线

| 天 | 任务 | 产出 |
|----|------|------|
| D1-3 | 实现 Schema Validation + Permission Check | `agenzo/guard/validator.py` |
| D4-5 | 实现 Content Inspection（shell/SQL/path 检测） | `agenzo/guard/inspector.py` |
| D6-7 | 实现权限配置加载（YAML → Redis 热加载） | `agenzo/guard/permissions.py` |
| D8-10 | 写 demo：接一个恶意 MCP server，演示拦截 | 安全演示 |

**验收标准**：
- [ ] 参数注入（`; rm -rf /`）被 Layer 3 拦截
- [ ] 未授权工具调用被 Layer 2 拒绝
- [ ] 每次拦截产生审计日志
- [ ] 权限配置变更不需要重启服务

### 8.4 Phase 4：可观测性（第 7-8 周）

**目标**：Agent Trace 接入 + 合规审计导出

| 天 | 任务 | 产出 |
|----|------|------|
| D1-3 | 实现 trace decorator（OTel 兼容） | `agenzo/trace/decorator.py` |
| D4-5 | 实现 trace 存储（ClickHouse schema） | `agenzo/trace/storage.py` |
| D6-7 | 实现 trace 可视化（Grafana 或 Vue 页面） | Dashboard |
| D8-10 | 实现合规导出（按 tenant + 时间范围导出） | 审计工具 |

### 8.5 Phase 5：整合 + 开源（第 9-10 周）

| 天 | 任务 | 产出 |
|----|------|------|
| D1-3 | 四个模块整合测试 | 端到端 demo |
| D4-5 | 写 README（中英文） | 开源文档 |
| D6-7 | 写 2-3 篇博客 | 个人品牌内容 |
| D8-10 | GitHub 发布 + 社区推广 | 开源项目 |

## 9. 风险与缓解

| 风险 | 概率 | 影响 | 缓解 |
|------|------|------|------|
| 公司不允许开源 | 中 | 高 | 先做内部版本，开源版脱敏后单独维护 |
| DeepSeek API 不稳定 | 中 | 中 | 多 provider fallback，千问做备选 |
| 评测 case 覆盖不足 | 高 | 中 | 持续从生产 trace 中提取新 case |
| 安全层性能开销 | 低 | 中 | Schema 校验 < 1ms，Redis 权限查询 < 0.5ms |
| 团队没时间配合 | 中 | 高 | 先自己做 Gateway 层，不依赖其他团队 |

## 10. 成功指标

| 阶段 | 指标 | 目标 |
|------|------|------|
| Phase 1 完成 | 能看到每日 LLM 成本分布 | 第一份 dashboard |
| Phase 2 完成 | Skill 评测通过率 | ≥ 85% |
| Phase 3 完成 | 安全拦截演示 | 100% 拦截已知攻击模式 |
| Phase 4 完成 | Trace 覆盖率 | 100% LLM/工具调用有 trace |
| 开源后 3 个月 | GitHub Stars | 500+ |
| 公司内 6 个月 | LLM 成本优化 | 降低 30%+ |

---

## 附录 A：竞品对比

| 维度 | Portkey | Helicone | LangSmith | 本方案 |
|------|---------|----------|-----------|--------|
| 开源 | ✅ Gateway | ✅ 全栈 | ❌ SaaS | ✅ 全栈 |
| 多模型路由 | ✅ 1600+ | ✅ 100+ | ❌ | ✅ 5+ (够用) |
| 成本归因 | ✅ | ✅ | ✅ | ✅ |
| MCP 安全 | ✅ (新) | ❌ | ❌ | ✅ (核心) |
| Skill Pack | ❌ | ❌ | ❌ | ✅ (核心) |
| 支付行业定制 | ❌ | ❌ | ❌ | ✅ (核心) |
| 中文支持 | 部分 | 部分 | 部分 | ✅ 原生 |
| 自托管 | ✅ | ✅ | ❌ | ✅ |

**差异化**：本方案不是通用 AI Gateway，是**支付行业 Agent 的完整参考架构**——安全、成本、审计、垂直能力四合一，且原生中文。

## 附录 B：参考资料

- [Portkey AI Gateway](https://github.com/Portkey-AI/gateway) — 开源多模型路由
- [Helicone](https://docs.helicone.ai/) — 开源 LLM 可观测性
- [LangSmith](https://www.langchain.com/blog/interrupt-2026-overview) — Agent 生产平台
- [Microsoft MCP Control Plane](https://developer.microsoft.com/blog/securing-mcp-a-control-plane-for-agent-tool-execution) — MCP 安全
- [MCP-SandboxScan](https://arxiv.org/html/2601.01241v1) — MCP 沙箱安全框架
- [Nightfall AI MCP Checklist](https://www.nightfall.ai/blog/how-to-monitor-mcp-usage-a-10-step-security-checklist-for-2026) — MCP 安全 10 步清单
- [Google ADK Skills](https://developers.googleblog.com/developers-guide-to-building-adk-agents-with-skills/) — Skill 架构设计
- [Spring AI Agent Skills](https://spring.io/blog/2026/01/13/spring-ai-generic-agent-skills) — Skill 文件结构
- [Anthropic Structuring Agents, Skills, and MCPs](https://medium.com/@intuitmachine/structuring-agents-skills-and-mcps-best-practices-from-anthropic-9312849ccea6) — Anthropic 最佳实践
- [阿里 LoongSuite GenAI SemConv](https://my.oschina.net/u/3874284/blog/19666808) — AI Agent 可观测语义规范
