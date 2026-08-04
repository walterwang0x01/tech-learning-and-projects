# A2A Agent 间通信协议
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. A2A 概述

> 🔄 更新于 2026-04-16

<!-- version-check: A2A v1.0 stable, Linux Foundation 托管, 150+ 组织, checked 2026-04-16 -->

A2A（Agent-to-Agent）是 Google 于 2025 年提出的开放协议，用于标准化不同 AI Agent 之间的通信与协作。2025 年 6 月捐赠给 Linux Foundation，2026 年 4 月发布 v1.0 稳定规范。目前 150+ 组织支持（含 AWS、Cisco、Microsoft、Salesforce、SAP、ServiceNow），GitHub 22K+ Stars。与 MCP 互补：MCP 解决 Agent 与工具的连接（垂直集成），A2A 解决 Agent 与 Agent 的协作（水平协作）。来源：[Linux Foundation 公告](https://www.linuxfoundation.org/press/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year)

```
MCP：Agent ↔ 工具/数据（垂直）
A2A：Agent ↔ Agent（水平）

┌─────────┐  A2A  ┌─────────┐  A2A  ┌─────────┐
│ Agent A  │◄────►│ Agent B  │◄────►│ Agent C  │
│ (客服)   │      │ (订单)   │      │ (物流)   │
└────┬─────┘      └────┬─────┘      └────┬─────┘
     │ MCP             │ MCP             │ MCP
┌────┴─────┐      ┌────┴─────┐      ┌────┴─────┐
│ CRM系统   │      │ 订单数据库 │      │ 物流API  │
└──────────┘      └──────────┘      └──────────┘
```

## 2. 核心概念

### 2.1 Agent Card（Agent 名片）

```json
// /.well-known/agent.json — Agent 自我描述
{
  "name": "Order Processing Agent",
  "description": "处理订单查询、创建和状态更新",
  "url": "https://order-agent.example.com",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "pushNotifications": true
  },
  "skills": [
    {
      "id": "query_order",
      "name": "查询订单",
      "description": "根据订单号或用户ID查询订单信息",
      "inputSchema": {
        "type": "object",
        "properties": {
          "order_id": { "type": "string" },
          "user_id": { "type": "string" }
        }
      }
    }
  ],
  "authentication": {
    "schemes": ["oauth2", "apiKey"]
  }
}
```

### 2.2 任务生命周期

```
submitted → working → input-required → working → completed
                                                 → failed
                                                 → canceled

客户端 Agent                    远程 Agent
    │                              │
    │── POST /tasks/send ─────────>│  创建任务
    │<── { status: "working" } ────│
    │                              │  ... 处理中 ...
    │<── { status: "input-required" }│  需要更多信息
    │── POST /tasks/send ─────────>│  补充信息
    │<── { status: "completed",    │
    │     artifacts: [...] } ──────│  返回结果
```

### 2.3 Artifact（产出物）

```json
{
  "taskId": "task-123",
  "status": "completed",
  "artifacts": [
    {
      "name": "order_details",
      "parts": [
        { "type": "text", "text": "订单 #12345 已发货" },
        { "type": "data", "data": { "orderId": "12345", "status": "shipped" } }
      ]
    }
  ]
}
```

## 3. 与 MCP 的关系

| 维度 | MCP | A2A |
|------|-----|-----|
| 解决问题 | Agent 连接工具和数据 | Agent 之间协作 |
| 通信方向 | 垂直（Agent ↔ 工具） | 水平（Agent ↔ Agent） |
| 发现机制 | 配置文件 / MCP Registry | Agent Card（/.well-known/）+ Signed Agent Cards |
| 状态管理 | 无状态工具调用 | 有状态任务生命周期 |
| 传输层 | stdio / Streamable HTTP | HTTP / JSON-RPC / gRPC |
| 安全性 | OAuth 2.1 | Signed Agent Cards + 零信任架构 |
| 典型场景 | 查数据库、调 API | 跨团队 Agent 协作 |
| 治理 | Anthropic 主导 | Linux Foundation 托管 |
| 关系 | 互补，不竞争 | 互补，不竞争 |

## 4. 协议选型

```
单 Agent + 工具调用 → MCP
多 Agent 协作 → A2A
轻量消息传递 → ACP
复杂企业场景 → MCP + A2A 组合
```
## 🎬 推荐视频资源

<!-- 修复于 2026-04-16: 移除重复的视频链接 -->
- [Google Cloud - A2A Protocol Overview](https://www.youtube.com/watch?v=4Fy0gDqSVOg) — Google官方A2A协议介绍
- [AI Jason - Agent Protocols Explained](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — Agent协议生态讲解（含A2A与MCP对比）
