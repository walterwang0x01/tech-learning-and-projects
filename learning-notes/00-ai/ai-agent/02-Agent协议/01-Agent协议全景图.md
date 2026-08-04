# Agent 协议全景图
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 协议分类

Agent 生态协议分三大类：工具连接、Agent 间通信、Agent 与 UI 交互。

```
┌──────────────────── Agent 协议全景 ────────────────────┐
│  Agent-UI 协议        Agent 间协议        工具连接协议   │
│  (Agent ↔ 人)        (Agent ↔ Agent)    (Agent ↔ 工具) │
│  AG-UI / A2UI         A2A / ACP / ANP     MCP           │
└─────────────────────────────────────────────────────────┘
```

## 2. MCP — Agent 与工具的连接（垂直）

Anthropic 提出，Agent 连接外部工具和数据源的标准协议，生态最大。详见 → [MCP模型上下文协议](./02-MCP模型上下文协议.md)

## 3. Agent 间通信协议（水平）

- **A2A**（Google）：企业级 Agent 协作，Agent Card + 任务管理 + 流式通信。详见 → [A2A Agent间通信协议](./03-A2A%20Agent间通信协议.md)
- **ACP**（IBM）：轻量 HTTP REST 消息传递，异步多模态。详见 → [ACP与协议生态](./04-ACP与协议生态.md)
- **ANP**（社区）：去中心化 Agent 网络，DID 身份认证，Agent 发现与互联

## 4. Agent-UI 协议 — 新兴领域

### AG-UI（Agent-User Interaction Protocol）

标准化 Agent 与前端 UI 的通信，解决"Agent 输出如何展示给用户"。

```typescript
import { AgentUIClient } from "@ag-ui/client";
const client = new AgentUIClient({ agentUrl: "https://my-agent.com/api" });

const stream = client.run({
  messages: [{ role: "user", content: "分析这份数据" }],
});

for await (const event of stream) {
  switch (event.type) {
    case "TEXT_DELTA":      appendToChat(event.text);       break;
    case "TOOL_CALL_START": showToolLoading(event.toolName); break;
    case "TOOL_CALL_END":   showToolResult(event.result);    break;
    case "STATE_UPDATE":    updateAgentStatus(event.state);  break;
  }
}
```

### A2UI（Agent-to-UI）

Agent 动态生成 UI 组件（表单/图表/按钮），前端自动渲染，而非仅返回文本。

## 5. 协议关系全景图

```
                         ┌──────────┐
                         │   用户    │
                         └─────┬────┘
                          AG-UI│A2UI
                         ┌─────┴────┐
                         │ 前端 UI   │
                         └─────┬────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
           ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
           │ Agent A  │   │ Agent B │   │ Agent C │
           └────┬────┘   └────┬────┘   └────┬────┘
             A2A│ACP│ANP      │              │
                │←───────────→│              │
            MCP │          MCP │          MCP │
           ┌────┴────┐   ┌────┴────┐   ┌────┴────┐
           │  Tools   │   │   DB    │   │  API    │
           └─────────┘   └─────────┘   └─────────┘

  纵向 MCP：Agent ↔ 工具    横向 A2A/ACP/ANP：Agent ↔ Agent
  上层 AG-UI/A2UI：Agent ↔ 用户界面
```

## 6. 协议选型对比表

| 协议 | 提出方 | 方向 | 核心用途 | 传输 | 成熟度 |
|------|--------|------|----------|------|--------|
| MCP | Anthropic | Agent↔工具 | 工具/数据集成 | stdio/Streamable HTTP | 高 |
| A2A | Google → Linux Foundation | Agent↔Agent | 企业级协作 | HTTP/JSON-RPC/gRPC | 高（v1.0） |
| ACP | IBM → Linux Foundation | Agent↔Agent | 轻量消息 | REST + OpenAPI | 中（Linux Foundation 托管） |
| ANP | 社区 | Agent↔Agent | 去中心化网络 | HTTP/DID | 早期 |
| AG-UI | CopilotKit | Agent↔UI | 前端交互 | SSE/WebSocket | 早期 |
| A2UI | 社区 | Agent→UI | 动态 UI 生成 | JSON | 概念期 |

## 7. 常见组合模式

```python
patterns = {
    "IDE Agent（Kiro）":     "MCP",
    "企业多 Agent 系统":      "MCP + A2A",
    "Agent Web 应用":        "MCP + AG-UI",
    "全栈 Agent 平台":       "MCP + A2A + AG-UI",
    "轻量微服务 Agent":      "ACP",
    "开放 Agent 网络":       "ANP + A2A",
}
```

## 8. 选型决策指南

```
你需要什么？
├─ Agent 调用工具/数据       → MCP（唯一选择，生态最大）
├─ Agent 之间通信
│   ├─ 企业级、任务管理      → A2A
│   ├─ 轻量、快速集成        → ACP
│   └─ 去中心化、开放网络    → ANP
├─ Agent 输出展示给用户
│   ├─ 流式事件、标准化渲染  → AG-UI
│   └─ 动态生成 UI 组件     → A2UI
└─ 不确定？ → 先用 MCP，按需加 A2A 和 AG-UI
```

## 9. 趋势

```
2024：MCP 一枝独秀
2025：A2A + AG-UI 兴起，多 Agent 协作和前端交互标准化
2026+：协议融合，可能出现统一 Agent 通信标准
```

> 🔄 更新于 2026-04-16

### 2026 年协议生态重要进展

<!-- version-check: A2A v1.0, MCP 2026-03-26 spec, checked 2026-04-16 -->

**A2A 协议里程碑**：2026 年 4 月，A2A 发布 v1.0 稳定规范，标志着从早期协议进入生产就绪阶段。150+ 组织支持（含 AWS、Cisco、Microsoft、Salesforce、SAP），GitHub 22K+ Stars，SDK 覆盖 5 种语言（Python/JS/Java/Go/.NET）。A2A 已由 Linux Foundation 托管治理。v0.3 引入 gRPC 支持和 Signed Agent Cards（加密身份验证），显著提升企业级安全性。来源：[Linux Foundation 公告](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year)、[InfoWorld](https://www.infoworld.com/article/4032776/google-upgrades-agent2agent-protocol-with-grpc-and-enterprise-grade-security.html)

**MCP 协议演进**：2025-03-26 规范引入 Streamable HTTP 传输替代 SSE，2026-03-26 规范正式废弃 SSE。认证升级到 OAuth 2.1（强制 PKCE + HTTPS）。MCP Registry 概念兴起，企业级 MCP 注册中心成为新趋势。来源：[MCP Specification Changelog](https://www.mcpserverspot.com/learn/fundamentals/mcp-specification-changelog)

**Agent 支付协议（AP2）**：作为 A2A 的支付扩展，AP2 已获 60+ 支付和金融服务组织支持，支持 Agent 驱动的安全交易。

**协议成熟度更新**（2026 年 4 月）：

| 协议 | 成熟度 | 关键变化 |
|------|--------|---------|
| MCP | 高（生态最大） | Streamable HTTP 替代 SSE，OAuth 2.1 |
| A2A | 高（v1.0 稳定） | gRPC 支持，Signed Agent Cards，Linux Foundation 托管 |
| ACP | 中（Linux Foundation 托管） | REST + OpenAPI，mDNS 发现，企业采用加速 |
| AG-UI | 中 | 社区活跃度提升 |
## 🎬 推荐视频资源

- [Anthropic - Model Context Protocol](https://www.youtube.com/watch?v=kQmXtrmQ5Zg) — MCP官方介绍
- [Google Cloud - A2A Protocol](https://www.youtube.com/watch?v=4Fy0gDqSVOg) — A2A协议介绍
- [AI Jason - Agent Protocols Explained](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — Agent协议生态讲解
