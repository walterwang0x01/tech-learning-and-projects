# Affinidi Trust Fabric — Agent 信任网关
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

Affinidi Trust Fabric 是一个安全代理（Proxy）基础设施，为 AI Agent 通信提供加密身份、策略执行和可观测性。它不负责运行 Agent，而是作为 Agent 之间的"信任网关"，在跨组织边界通信时保证端到端安全与合规。

```
┌──────────── Affinidi Trust Fabric 定位 ────────────┐
│                                                      │
│  传统 API Gateway：人/应用 → 服务                     │
│  Trust Fabric：    Agent → Agent / Agent → 服务       │
│                                                      │
│  核心差异：                                           │
│  ├─ 去中心化身份（DID），不依赖中心化 IdP              │
│  ├─ 多协议支持（A2A / MCP / DIDComm / x402）         │
│  ├─ 多跳路由，跨组织 Gateway 链式连接                 │
│  └─ OPA 策略引擎，细粒度访问控制                      │
└──────────────────────────────────────────────────────┘
```

## 2. 核心架构

Trust Gateway 作为拦截代理（intercepting proxy），处于 Agent 和目标服务之间：

```
Agent A ──→ Trust Gateway ──→ 目标服务 / Agent B
               │
               ├─ 验证身份，分配 DID
               ├─ 执行 OPA 策略
               ├─ 捕获指标和 payload
               ├─ 注入元数据
               └─ 转发请求
```

### 请求生命周期

```
┌─────────── Trust Gateway 请求流程 ───────────┐
│                                                │
│  1. Agent 发送请求（A2A/MCP）经 Channel 进入   │
│     ↓                                          │
│  2. Gateway 验证 Agent 身份                     │
│     ├─ 提取身份字段（LLM provider/model/region）│
│     └─ 生成或查找 DID                           │
│     ↓                                          │
│  3. OPA 策略评估                                │
│     ├─ 检查 Agent DID / 元数据                  │
│     ├─ 检查请求内容 / 方法 / 参数               │
│     ├─ 检查上下文（时间/限流/角色）              │
│     └─ 决定：允许 / 拒绝                        │
│     ↓                                          │
│  4. 注入元数据 + 捕获指标                       │
│     ↓                                          │
│  5. 转发到目标服务                              │
│     ↓                                          │
│  6. 响应原路返回，同样经过策略和指标处理         │
└────────────────────────────────────────────────┘
```

## 3. 六大核心能力

### 3.1 加密身份（Cryptographic Identity）

Trust Gateway 自动为每个 Agent 生成唯一的去中心化标识符（DID），基于可配置的身份字段。

```
DID 生成机制：
├─ 输入：Agent 的 LLM provider + model + 部署 region
├─ 输出：唯一 DID（持久标识，不随 IP 变化）
├─ 签名：Ed25519 用于 Gateway 间通信
└─ 缓存：DID 解析结果缓存，提升性能

示例：
Agent 配置 = { provider: "anthropic", model: "claude-4", region: "us-east-1" }
    ↓
DID = did:affinidi:agent:sha256(anthropic+claude-4+us-east-1)
    ↓
所有该 Agent 的请求都关联到这个 DID
```

与传统身份方案的对比：

| 维度 | OAuth2 / API Key | DID（Trust Fabric） |
|------|-------------------|---------------------|
| 颁发方 | 中心化 IdP | 自动生成，去中心化 |
| 绑定对象 | 用户/应用 | Agent 实例 |
| 跨组织 | 需要联邦认证 | 原生支持 |
| 可验证性 | 依赖 IdP 在线 | 密码学自验证 |
| 撤销 | IdP 撤销 | DID 文档更新 |

### 3.2 Channel 管理（路由配置）

Channel 是 Trust Gateway 的核心路由单元，定义了请求从哪来、到哪去、用什么协议、执行什么策略。

```
┌─────────── Channel 配置模型 ───────────┐
│                                         │
│  Channel = {                            │
│    listen:    "/agents/research/*"       │  ← 监听路径
│    forward:   "https://research.ai/api"  │  ← 转发目标
│    protocol:  "a2a"                      │  ← 通信协议
│    policies:  ["rate-limit", "acl"]      │  ← 策略列表
│    inject:    { "org": "acme-corp" }     │  ← 注入元数据
│    capture:   { payload: true }          │  ← 日志捕获
│  }                                      │
│                                         │
│  转发目标可以是：                        │
│  ├─ 后端服务（REST API）                │
│  ├─ 另一个 AI Agent                     │
│  └─ 另一个 Trust Gateway（多跳路由）    │
└─────────────────────────────────────────┘
```

### 3.3 策略执行（OPA + Rego）

使用 Open Policy Agent 做细粒度的访问控制，策略用 Rego 语言编写。

```rego
# 示例：基于 Agent DID 和时间的访问控制策略
package trust_gateway

default allow = false

# 允许白名单内的 Agent 访问
allow {
    input.agent.did == data.allowlist[_]
}

# 工作时间内允许写操作
allow {
    input.request.method == "POST"
    time.hour(time.now_ns()) >= 9
    time.hour(time.now_ns()) < 18
}

# 限制特定 Agent 只能调用特定工具
allow {
    input.agent.metadata.role == "reader"
    input.request.method == "GET"
}

# 拒绝超过限流的请求
deny {
    count(data.rate_limiter[input.agent.did]) > 100
}
```

```
OPA 策略可评估的维度：
├─ Agent 身份：DID、元数据字段
├─ 请求内容：方法、参数、Headers
├─ 上下文信息：时间、限流计数、用户角色
├─ 外部数据源：白名单、黑名单、数据库
└─ JWT Claims：Bearer Token 中的声明
```

### 3.4 网络配置（弹性通信）

```
网络弹性特性：
├─ 熔断器（Circuit Breaker）
│   └─ 目标服务故障时自动断开，防止级联失败
├─ 重试逻辑
│   └─ 指数退避重试（exponential backoff）
├─ 超时控制
│   ├─ 请求超时（request timeout）
│   ├─ 连接超时（connect timeout）
│   └─ 空闲超时（idle timeout）
└─ 流量镜像（Traffic Mirroring）
    └─ A/B 测试、影子部署
```

### 3.5 可观测性（Observability）

```
可观测性能力：
├─ 实时仪表盘：活跃连接数、请求速率
├─ 完整 Payload 捕获：按 Channel 配置，用于调试
├─ 多后端指标导出
│   ├─ Prometheus
│   ├─ CloudWatch
│   └─ 本地文件
├─ 结构化日志：关联 ID（Correlation ID）串联请求链路
└─ 审计追踪：每个 Gateway 独立维护审计日志
```

### 3.6 多跳路由（Multi-Hop Routing）

这是 Trust Fabric 最独特的能力——多个 Trust Gateway 可以链式连接，实现跨组织通信。

```
┌─────────── 多跳路由架构 ───────────┐
│                                     │
│  组织 A                  组织 B     │
│  ┌──────────┐           ┌──────────┐│
│  │ Agent    │           │ 目标服务  ││
│  └────┬─────┘           └────┬─────┘│
│       │                      ↑      │
│  ┌────┴─────┐           ┌────┴─────┐│
│  │ Gateway 1│ DIDComm   │ Gateway 2││
│  │ (Org A)  │──────────→│ (Org B)  ││
│  └──────────┘ v2.1 加密  └──────────┘│
│       │                      │      │
│  独立策略              独立策略      │
│  独立审计              独立审计      │
│                                     │
│  关键特性：                          │
│  ├─ DIDComm v2.1 加密消息传递        │
│  ├─ 双向通信                         │
│  ├─ DID 身份验证                     │
│  ├─ OOB（Out-of-Band）邀请建立连接   │
│  └─ 每个 Gateway 独立策略和审计      │
└─────────────────────────────────────┘
```

## 4. 支持的协议

Trust Fabric 的一大亮点是多协议支持，覆盖 Agent 通信的各个场景：

| 协议 | 描述 | 典型场景 |
|------|------|----------|
| A2A | Google 的 Agent 间通信协议 | 不同框架的 Agent 协作 |
| MCP | JSON-RPC 2.0 工具调用协议，Gateway 通过 `_meta` 字段注入身份追踪 | 监控哪个 AI 模型调用了哪个工具 |
| AP2 | Google 的 Agent 支付协议 | Agent 自主执行支付交易 |
| UCP | Google 的通用商务协议 | Agent 参与电商交易 |
| x402 | HTTP 402 微支付协议 | Agent API 按次计费 |
| DIDComm v2.1 | Gateway 间加密通信 | 跨组织多跳路由 |

## 5. 典型应用场景

```
场景 1：多租户 AI 平台
├─ 每个租户的 Agent 分配唯一 DID
├─ 租户级别的限流、访问策略、可观测边界
└─ 租户间完全隔离

场景 2：跨组织 Agent 协作
├─ 组织 A 和组织 B 各部署 Trust Gateway
├─ 通过 DIDComm 建立安全连接
├─ 各自维护独立策略和审计日志
└─ Agent 跨组织调用服务，端到端加密

场景 3：网络边界穿越
├─ 内部 Agent 通过 DMZ Gateway 访问外部服务
├─ 维护端到端加密
└─ 完整审计追踪跨越网络区域
```

## 6. 与同类方案对比

| 维度 | Affinidi Trust Fabric | AWS Bedrock AgentCore | 传统 API Gateway (Kong/Envoy) |
|------|----------------------|----------------------|-------------------------------|
| 定位 | Agent 信任网关 | Agent 全生命周期平台 | 通用 API 网关 |
| 身份体系 | DID（去中心化） | OAuth + IAM | API Key / OAuth |
| Agent 运行 | ❌ 不负责 | ✅ 托管运行时 | ❌ 不负责 |
| 多跳路由 | ✅ 原生支持 | ❌ | ❌ |
| 协议支持 | A2A/MCP/DIDComm/x402/AP2/UCP | MCP + 自有 Gateway | HTTP/gRPC |
| 策略引擎 | OPA (Rego) | IAM Policy | 插件式 |
| 跨组织协作 | ✅ 核心场景 | ❌ 非核心 | 需额外配置 |
| 厂商绑定 | 无，可独立部署 | 深度绑定 AWS | 开源可选 |
| 可观测性 | Prometheus/CloudWatch/本地 | CloudWatch + OTEL | 插件式 |

```
选型建议：
├─ 需要跨组织 Agent 信任通信 → Trust Fabric
├─ 需要托管运行 Agent → AgentCore
├─ 只需要 HTTP API 管理 → Kong / Envoy
└─ 组合使用：AgentCore 运行 Agent + Trust Fabric 治理通信
```

## 7. 与现有笔记的关联

```
Trust Fabric 涉及的知识点：
├─ Agent 协议
│   ├─ A2A 协议 → 02-Agent协议/03-A2A Agent间通信协议.md
│   ├─ MCP 协议 → 02-Agent协议/02-MCP模型上下文协议.md
│   ├─ 支付协议（AP2/x402） → 02-Agent协议/05-Agent支付协议.md
│   └─ 协议全景 → 02-Agent协议/01-Agent协议全景图.md
├─ Agent 安全
│   ├─ 身份与权限（DID vs OAuth） → 本目录/01-Agent身份与权限.md
│   └─ 治理框架 → 本目录/02-Agent治理框架.md
├─ AI 网关
│   └─ 网关对比 → 13-AI网关与路由/（Trust Fabric 是 Agent 专用网关）
└─ 云厂商方案
    └─ AgentCore 对比 → 21-云厂商Agent方案/
```

## 📖 参考资料

- [Affinidi Trust Fabric 官方文档](https://docs.affinidi.com/products/affinidi-trust-fabric/)
- [Affinidi Trust Network 概览](https://docs.affinidi.com/docs/overview/)
- [Affinidi Radix 信任注册表](https://docs.affinidi.com/products/affinidi-radix/)
