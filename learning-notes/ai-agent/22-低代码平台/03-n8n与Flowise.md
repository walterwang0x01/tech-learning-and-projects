# n8n 与 Flowise
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. n8n 概述

n8n 是一个开源的工作流自动化平台，内置 AI Agent 节点，可将 LLM 能力与 400+ 应用集成。

```
┌─────────────────────────────────────────┐
│              n8n 平台                     │
├──────────┬──────────┬──────────────────┤
│ 触发器    │ AI 节点   │  集成节点         │
├──────────┼──────────┼──────────────────┤
│ Webhook  │ AI Agent  │ Slack/Email      │
│ 定时任务  │ LLM Chain│ 数据库/API       │
│ 事件监听  │ RAG      │ GitHub/Jira      │
└──────────┴──────────┴──────────────────┘
```

## 2. n8n AI Agent 工作流

```python
# n8n 通过 API 触发工作流
import httpx

N8N_API = "http://localhost:5678/api/v1"
N8N_KEY = "n8n-api-key"

# 触发 Webhook 工作流
async def trigger_n8n_workflow(webhook_url: str, data: dict) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(webhook_url, json=data)
        return response.json()

# 示例：触发 AI 客服工作流
result = await trigger_n8n_workflow(
    "http://localhost:5678/webhook/customer-service",
    {"query": "我的订单什么时候发货？", "user_id": "user-123"},
)
```

```json
// n8n AI Agent 工作流配置示例
{
  "nodes": [
    {
      "type": "n8n-nodes-base.webhook",
      "name": "Webhook 触发",
      "parameters": {"path": "customer-service", "httpMethod": "POST"}
    },
    {
      "type": "@n8n/n8n-nodes-langchain.agent",
      "name": "AI Agent",
      "parameters": {
        "agent": "openAiFunctionsAgent",
        "text": "={{ $json.query }}",
        "options": {"systemMessage": "你是客服助手，帮助用户解决问题。"}
      }
    },
    {
      "type": "@n8n/n8n-nodes-langchain.toolHttpRequest",
      "name": "订单查询工具",
      "parameters": {
        "url": "https://api.example.com/orders",
        "description": "查询用户订单信息"
      }
    },
    {
      "type": "n8n-nodes-base.slack",
      "name": "发送 Slack 通知",
      "parameters": {"channel": "#customer-service"}
    }
  ]
}
```

## 3. n8n 自动化集成

```python
# n8n 工作流：文档更新 → 知识库同步 → 通知
# 通过 n8n API 管理工作流

async def create_workflow(workflow_data: dict) -> dict:
    """创建 n8n 工作流"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{N8N_API}/workflows",
            headers={"X-N8N-API-KEY": N8N_KEY},
            json=workflow_data,
        )
        return response.json()

async def execute_workflow(workflow_id: str, data: dict = None) -> dict:
    """手动执行工作流"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{N8N_API}/workflows/{workflow_id}/run",
            headers={"X-N8N-API-KEY": N8N_KEY},
            json={"data": data or {}},
        )
        return response.json()

# 查看执行历史
async def get_executions(workflow_id: str) -> list:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{N8N_API}/executions",
            headers={"X-N8N-API-KEY": N8N_KEY},
            params={"workflowId": workflow_id, "limit": 10},
        )
        return response.json()["data"]
```

## 4. Flowise 概述

Flowise 是一个可视化的 LangChain/LlamaIndex 构建工具，通过拖拽节点创建 LLM 应用。

```
Flowise 核心特点：
├── 可视化 LangChain — 拖拽式构建 Chain/Agent
├── 内置组件丰富 — LLM、向量库、工具、记忆
├── API 一键发布 — 自动生成 REST API
└── 嵌入式部署 — 可嵌入到现有网站
```

## 5. Flowise API 调用

```python
# Flowise 自动生成 API 端点
FLOWISE_API = "http://localhost:3000/api/v1"

# 调用 Chatflow
async def chat_with_flowise(chatflow_id: str, question: str, session_id: str = "") -> str:
    async with httpx.AsyncClient() as client:
        payload = {
            "question": question,
            "overrideConfig": {
                "sessionId": session_id,  # 会话隔离
            },
        }
        response = await client.post(
            f"{FLOWISE_API}/prediction/{chatflow_id}",
            json=payload,
        )
        return response.json()["text"]

# 上传文档到 Flowise 向量库
async def upload_to_flowise(chatflow_id: str, file_path: str) -> dict:
    async with httpx.AsyncClient() as client:
        with open(file_path, "rb") as f:
            response = await client.post(
                f"{FLOWISE_API}/vector/upsert/{chatflow_id}",
                files={"files": f},
            )
        return response.json()

answer = await chat_with_flowise("chatflow-id", "什么是 RAG？")
```

## 6. 部署与对比

```bash
# n8n Docker 部署
docker run -d --name n8n -p 5678:5678 \
  -v n8n_data:/home/node/.n8n \
  -e N8N_AI_ENABLED=true \
  n8nio/n8n

# Flowise Docker 部署
docker run -d --name flowise -p 3000:3000 \
  -v flowise_data:/root/.flowise \
  flowiseai/flowise
```

| 特性 | n8n | Flowise |
|------|-----|---------|
| 定位 | 工作流自动化 + AI | 可视化 LangChain |
| AI 能力 | Agent 节点 | Chain/Agent 构建 |
| 集成数量 | 400+ 应用 | LangChain 组件 |
| 触发方式 | Webhook/定时/事件 | API 调用 |
| 适用场景 | 业务自动化 + AI | 纯 LLM 应用 |
| 学习曲线 | 中 | 低 |

### Flowise 3.0 与 Workday 收购

> 🔄 更新于 2026-04-29

**Workday 收购 Flowise**（2025-08-14）：企业软件巨头 Workday 收购了 Flowise，将其 AI Agent 构建能力整合到 Workday 平台中。收购后 Flowise 继续保持开源（49K+ Stars），但战略方向转向 HR 和财务领域的 AI Agent。来源：[Workday Newsroom](https://en-hk.newsroom.workday.com/2025-08-14-Workday-Acquires-Flowise,-Bringing-Powerful-AI-Agent-Builder-Capabilities-to-the-Workday-Platform)

**Flowise 3.0**（2026-01）：完全重写的版本，核心变化：
- **自然语言创建 Agent**：描述想法即可生成 Agent 草稿
- **模块化构建块**：支持 Chaining、Routing、Parallelization、Hierarchy、Looping、Iteration 六种编排模式
- **每个 LLM/Agent 增强**：Memory、RAG、Tool、Centralized State、Structured Output
- **Human in the Loop**：核心功能，支持审核 Agent 操作、批准/拒绝工具调用
- **Form Input**：除聊天界面外，支持表单触发工作流
- **Evals & Observability**：执行追踪、公开分享、反馈收集
- **Flow Validation**：自动检查工作流配置错误

来源：[Flowise Blog](https://blog.flowiseai.com/coming-soon/)

**⚠️ Flowise 安全警告**（2026-04）：CVE-2025-59528（CVSS 10.0）在 Flowise 3.0.5 的 CustomMCP 节点中发现 RCE 漏洞，12,000+ 实例暴露。**必须升级到 3.0.6+**。来源：[The Hacker News](https://thehackernews.com/2026/04/flowise-ai-agent-builder-under-active.html)

### n8n 安全事件（2026 Q1-Q2）

> 🔄 更新于 2026-04-29

n8n 在 2026 年初遭遇多个严重安全漏洞：

| CVE | 严重性 | 描述 | 修复版本 |
|-----|--------|------|----------|
| CVE-2026-21858 | Critical（10.0） | 未认证 RCE，Webhook 请求解析漏洞 | v2.6+ |
| CVE-2026-27577 | Critical | Expression 沙箱逃逸导致 RCE | v2.9+ |
| CVE-2026-27495 | High | Task Runner 沙箱逃逸 | v2.10+ |
| CVE-2026-27578 | High | 存储型 XSS 导致会话劫持 | v2.10+ |

**影响**：任何认证用户可完全控制服务器，窃取所有存储的凭证、API Key 和密钥。自托管和云实例均受影响。

**建议**：立即升级到 n8n v2.20+（当前稳定版），启用 Task Runner 隔离，限制 Code 节点权限。

来源：[Pillar Security](https://www.pillar.security/blog/n8n-sandbox-escape-critical-vulnerabilities-in-n8n-exposes-hundreds-of-thousands-of-enterprise-ai-systems-to-complete-takeover)、[The Hacker News](https://thehackernews.com/2026/03/critical-n8n-flaws-allow-remote-code.html)

## 7. 2026 版本演进

> 🔄 更新于 2026-04-21

<!-- version-check: n8n 2.20+, Flowise 3.0.6, checked 2026-05-21 -->

### n8n 2.0：安全加固与企业级升级

n8n 于 2025-12-15 发布 v2.0 稳定版，这是自 2023-07 v1.0 以来的首个大版本。核心变化不是新功能，而是安全、可靠性和性能的全面加固。

**安全（Secure by Default）**：
- Task Runner 默认启用：所有 Code 节点在隔离环境中执行
- 环境变量从 Code 节点中屏蔽
- 禁止任意命令执行的节点默认关闭
- 原有宽松行为需显式启用

**可靠性**：
- 移除遗留选项和已停服的服务节点
- 子工作流 + Wait 节点正确返回工作流末尾数据（而非 Wait 节点输入）
- 更少的可选项 = 更少的边界情况 = 更可预测的行为

**性能**：
- 新 SQLite 连接池驱动：基准测试最高 10x 提速
- 文件系统二进制数据处理在高负载下更稳定
- Task Runner 提供更好的隔离和资源管理

**Publish / Save 新范式**：
- v1.x：保存已激活的工作流 = 立即更新生产环境
- v2.0：Save 仅保存编辑，Publish 是独立的显式操作
- 为后续 Autosave 功能奠定基础

**n8n 生态数据**（截至 2026-04）：
- GitHub Stars：160,000+（v1.0 时为 30,000）
- 社区成员：115,192（v1.0 时为 6,267）
- 团队规模：190+ 人（v1.0 时为 30 人）
- 120+ 版本发布（几乎每周一次）

**AI Agent 能力**（n8n 2.0+）：
- 原生 LangChain 支持
- AI Agent 节点：工具选择、记忆检索、多步推理
- Tool Nodes、持久化记忆、向量数据库集成
- Human-in-the-Loop 模式
- 子工作流链式调用

> 来源：[n8n Blog - Introducing n8n 2.0](https://blog.n8n.io/introducing-n8n-2-0/)、[n8n 2.0 Breaking Changes](https://docs.n8n.io/2-0-breaking-changes/)

## 🎬 推荐视频资源

### 🌐 YouTube
- [n8n Official - AI Workflow Tutorial](https://www.youtube.com/watch?v=vU2S6dVf79M) — n8n AI工作流教程
- [Leon van Zyl - n8n AI Agents](https://www.youtube.com/watch?v=nMGCE4GU1kc) — n8n构建AI Agent
- [Flowise AI - Getting Started](https://www.youtube.com/watch?v=tnejrr-0a94) — Flowise入门教程

### 📺 B站
- [n8n自动化工作流中文教程](https://www.bilibili.com/video/BV1dH4y1P7FY) — n8n中文实战

### 📖 官方文档
- [n8n AI Tutorial](https://docs.n8n.io/advanced-ai/intro-tutorial/) — n8n官方AI教程
- [Flowise Docs](https://docs.flowiseai.com/) — Flowise官方文档
