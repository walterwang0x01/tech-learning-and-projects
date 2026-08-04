# ACP 与协议生态
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. ACP（Agent Communication Protocol）

ACP 是 IBM 提出的轻量级 Agent 消息传递协议，专注于 Agent 间的异步通信。

```
┌──────────┐   ACP Message   ┌──────────┐
│  Agent A  │ ──────────────> │  Agent B  │
│ (Client)  │ <────────────── │ (Server)  │
└──────────┘   ACP Response   └──────────┘

核心特点：
- 基于 HTTP REST，轻量易集成
- 异步消息传递，支持长时间任务
- 多模态消息（文本、文件、图片）
- 无需了解 Agent 内部实现
```

```python
# ACP 消息格式（RESTful API + JSON payload）
<!-- 修复于 2026-04-16: ACP 使用 REST 风格而非 JSON-RPC，修正消息格式 -->
import httpx

# ACP 任务请求（POST /tasks）
acp_task = {
    "task": "分析这份销售报告",
    "context": {
        "requestedCapabilities": ["data-analysis", "report-generation"],
    },
    "message": {
        "role": "user",
        "parts": [
            {"type": "text", "text": "分析这份销售报告"},
            {"type": "file", "file": {
                "name": "report.csv",
                "mimeType": "text/csv",
                "data": "<base64_encoded_data>"
            }}
        ]
    }
}

# 发送请求到 ACP Agent
async def call_acp_agent(url: str, task: dict):
    async with httpx.AsyncClient() as client:
        # ACP 使用标准 REST 端点，不是 JSON-RPC
        response = await client.post(f"{url}/tasks", json=task)
        return response.json()
```

## 2. ANP（Agent Network Protocol）

ANP 是面向开放互联网的 Agent 网络协议，支持 Agent 发现、身份验证和跨网络通信。

```
┌─────────────────────────────────────────┐
│           Agent Network Protocol         │
├─────────────┬─────────────┬─────────────┤
│  身份层      │  通信层      │  发现层      │
│ DID 身份认证 │ 端到端加密   │ Agent 注册表 │
│ 可验证凭证   │ 消息路由     │ 能力描述     │
└─────────────┴─────────────┴─────────────┘

特点：
- 去中心化身份（DID）
- Agent 能力自描述
- 跨平台 Agent 发现
- 适合开放互联网场景
```

## 3. 协议对比

| 特性 | MCP | A2A | ACP | ANP |
|------|-----|-----|-----|-----|
| 提出方 | Anthropic | Google → Linux Foundation | IBM | 社区 |
| 核心用途 | 模型↔工具 | Agent↔Agent | Agent 消息传递 | Agent 网络 |
| 通信模式 | 同步/流式 | 异步任务 | 异步消息 | P2P |
| 传输层 | stdio/Streamable HTTP | HTTP/JSON-RPC/gRPC | REST + OpenAPI (HTTP/SSE/WS) | HTTP/DID |
| 身份认证 | OAuth 2.1 | Signed Agent Cards + OAuth 2.0 | OAuth2 / API Key | DID |
| Agent 发现 | MCP Registry（新兴） | Agent Card | mDNS / 注册中心 | 注册表 |
| 多模态 | 文本为主 | 多模态 | 多模态 | 多模态 |
| 成熟度 | 高（生态最大） | 高（v1.0 稳定，150+ 组织） | 早期 | 早期 |
| 适用场景 | 工具集成 | 企业 Agent 协作 | 轻量通信 | 开放网络 |

## 4. 协议关系与协作

```
┌─────────────────────────────────────────────┐
│              AI Agent 应用                    │
├──────────────────┬──────────────────────────┤
│   工具层（MCP）   │   Agent 协作层            │
│                  ├────────────┬─────────────┤
│  Agent ↔ 工具    │  A2A       │  ACP        │
│  Agent ↔ 数据    │  企业级协作  │  轻量消息    │
└──────────────────┴────────────┴─────────────┘

MCP + A2A 组合是当前主流方案：
- MCP 负责 Agent 与工具/数据的连接
- A2A 负责 Agent 之间的通信协作
- ACP 作为轻量替代方案
```

## 5. 场景选型指南

```python
def select_protocol(scenario: dict) -> str:
    """根据场景选择合适的协议"""
    if scenario["type"] == "tool_integration":
        return "MCP — Agent 连接外部工具和数据源"

    if scenario["type"] == "agent_collaboration":
        if scenario.get("enterprise"):
            return "A2A — 企业级多 Agent 协作，支持任务管理"
        if scenario.get("lightweight"):
            return "ACP — 轻量级 Agent 间消息传递"

    if scenario["type"] == "open_network":
        return "ANP — 开放互联网 Agent 发现与通信"

    return "MCP + A2A 组合 — 覆盖大多数场景"

# 常见组合模式
patterns = {
    "IDE Agent":       "MCP（工具集成）",
    "客服系统":         "MCP（知识库） + A2A（多 Agent 协作）",
    "企业自动化":       "A2A（Agent 编排） + MCP（系统集成）",
    "轻量微服务":       "ACP（服务间通信）",
}
```
## 🎬 推荐视频资源

### 🌐 YouTube
- [AI Jason - Agent Communication Protocols](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — Agent协议生态讲解
- [Google Cloud - A2A Protocol](https://www.youtube.com/watch?v=4Fy0gDqSVOg) — A2A/ACP协议介绍

### 📺 B站
- [AI协议生态全景解读](https://www.bilibili.com/video/BV1dH4y1P7FY) — MCP/A2A/ACP协议对比
