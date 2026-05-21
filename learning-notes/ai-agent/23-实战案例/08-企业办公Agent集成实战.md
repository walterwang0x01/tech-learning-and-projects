# 企业办公 Agent 集成实战
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

企业办公 Agent 集成是 2025-2026 年 AI 落地最活跃的方向之一。核心理念：**让 AI Agent 能直接操作企业协作平台**（飞书、Slack、Notion、Jira 等），在员工日常工作流中完成任务，而不是让员工离开工作环境去找 AI。

```
┌─────────────────────────────────────────────────────────────┐
│                    企业办公 Agent 集成全景                      │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  接入层    CLI / MCP Server / REST API / Webhook             │
│           ─────────────────────────────────────              │
│  Agent层   LangGraph │ CrewAI │ Copilot Studio │ 自研       │
│           ─────────────────────────────────────              │
│  协议层    MCP │ A2A │ OAuth2 │ OpenAPI                      │
│           ─────────────────────────────────────              │
│  平台层    飞书/Lark │ Slack │ Notion │ Jira │ M365         │
│           ─────────────────────────────────────              │
│  能力域    消息 │ 文档 │ 日历 │ 任务 │ 邮件 │ 审批          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### 三种集成模式

| 模式 | 说明 | 代表产品 | 适用场景 |
|------|------|---------|---------|
| CLI/Skills 模式 | Agent 通过命令行调用平台能力 | lark-cli、GitHub CLI | 开发者工具链、终端 Agent |
| MCP Server 模式 | 平台暴露 MCP 协议接口 | Notion MCP、Slack MCP | IDE Agent（Cursor/Claude Code） |
| 平台内嵌 Agent | 平台自带 AI Agent 能力 | Copilot Studio、Rovo、飞书智能伙伴 | 企业全员使用、低代码场景 |

## 2. 主流产品案例

### 2.1 飞书 lark-cli — Agent 原生 CLI

飞书官方开源的命令行工具，专为 AI Agent 设计，覆盖 11 大业务域、200+ 命令、19 个 Agent Skills。

```bash
# 安装
npm install -g @larksuite/cli
npx skills add larksuite/cli -y -g

# 配置（交互式引导）
lark-cli config init
lark-cli auth login --recommend

# 三层调用架构
# 1. 快捷命令（人机友好）
lark-cli calendar +agenda
lark-cli im +messages-send --chat-id "oc_xxx" --text "Hello"
lark-cli docs +create --title "周报" --markdown "# 本周进展"

# 2. API 命令（100+ 精选，与平台端点一一对应）
lark-cli calendar events instance_view --params '{"calendar_id":"primary"}'

# 3. 通用调用（覆盖 2500+ API）
lark-cli api GET /open-apis/calendar/v4/calendars
```

**Agent Skills 列表（19 个）：**

| Skill | 能力 |
|-------|------|
| lark-shared | 应用配置、认证登录、身份切换、权限管理 |
| lark-calendar | 日历日程、议程查看、忙闲查询、时间建议 |
| lark-im | 发送/回复消息、群聊管理、消息搜索、文件上传下载 |
| lark-doc | 创建、读取、更新、搜索文档（基于 Markdown） |
| lark-drive | 上传下载文件、管理权限与评论 |
| lark-sheets | 电子表格 CRUD、查找、导出 |
| lark-base | 多维表格、字段、记录、视图、仪表盘 |
| lark-task | 任务、子任务、提醒、成员分配 |
| lark-mail | 邮件浏览/搜索/发送/回复/转发、草稿管理 |
| lark-contact | 用户搜索（姓名/邮箱/手机号） |
| lark-wiki | 知识空间、节点、文档 |
| lark-event | 实时事件订阅（WebSocket） |
| lark-vc | 会议记录、会议纪要 |
| lark-minutes | 妙记 AI 产物（总结、待办、章节） |
| lark-workflow-* | 工作流：会议纪要汇总、日程待办摘要 |
| lark-skill-maker | 自定义 Skill 创建框架 |

**生产实践要点：**

```bash
# 身份切换：用户身份 vs 机器人身份
lark-cli calendar +agenda --as user
lark-cli im +messages-send --as bot --chat-id "oc_xxx" --text "Hello"

# Dry Run：预览副作用操作
lark-cli im +messages-send --chat-id oc_xxx --text "hello" --dry-run

# 输出格式控制
--format json      # 完整 JSON（默认，适合 Agent 解析）
--format table     # 表格（适合人类阅读）
--format ndjson    # 换行 JSON（适合管道处理）

# 自动分页
--page-all         # 自动翻页获取所有数据
--page-limit 5     # 最多 5 页
```

### 2.2 Notion MCP Server — 官方托管 MCP

Notion 官方提供的 MCP Server，让 Cursor、Claude Code 等 IDE Agent 直接操作 Notion 工作区。

```json
// Cursor/Kiro MCP 配置
{
  "mcpServers": {
    "notion": {
      "command": "npx",
      "args": ["-y", "@notionhq/notion-mcp-server"],
      "env": {
        "OPENAPI_MCP_HEADERS": "{\"Authorization\":\"Bearer ntn_xxx\",\"Notion-Version\":\"2022-06-28\"}"
      }
    }
  }
}
```

**支持的操作：**
- 页面：创建、读取、更新、搜索、归档
- 数据库：查询、创建条目、更新属性
- 评论：添加、读取
- 用户：列出工作区成员

**生产实践：**
- Notion 提供官方托管 MCP（`https://mcp.notion.com`），支持 OAuth 认证，无需自建
- Custom Agents 支持 MCP 连接，可在 Notion 内部触发外部工具
- 建议使用 Integration Token 而非个人 Token，便于权限管控

### 2.3 Slack — Agentic OS 定位

Slack 将自己定位为"企业 Agentic OS"，提供多层 Agent 集成能力。

```python
# Slack MCP Server 配置
{
  "mcpServers": {
    "slack": {
      "command": "npx",
      "args": ["-y", "@anthropic/slack-mcp-server"],
      "env": {
        "SLACK_BOT_TOKEN": "xoxb-xxx",
        "SLACK_TEAM_ID": "T0xxx"
      }
    }
  }
}
```

**三层 Agent 能力：**

| 层级 | 能力 | 说明 |
|------|------|------|
| Slackbot AI | 内置 AI 助手 | 搜索、摘要、对话，开箱即用 |
| Agentforce in Slack | Salesforce Agent | CRM 数据查询、客户跟进、销售预测 |
| MCP Server | 外部 Agent 接入 | 实时搜索 API + MCP 协议，Agent 可读取频道上下文 |

**生产实践：**
- 使用 Real-Time Search API 让 Agent 获取频道上下文
- Block Kit Tables 提供结构化数据展示
- 建议为 Agent 创建专用 Bot User，限制频道访问范围


### 2.4 Microsoft 365 Copilot — 企业级 Agent 平台

微软通过 Copilot Studio 提供企业级 Agent 构建和编排能力，深度集成 M365 全家桶。

**核心组件：**

| 组件 | 定位 | 能力 |
|------|------|------|
| Copilot Studio | Agent 构建平台 | 低代码构建 Agent，支持多 Agent 编排 |
| M365 Agent Builder | 声明式 Agent | 在 M365 Copilot 内快速创建 Agent |
| Azure AI Agent Service | 开发者 SDK | 代码级 Agent 开发，支持 MCP |
| Semantic Kernel | 开源框架 | C#/Python/Java Agent 编排框架 |

**Agent 能力覆盖：**
- Teams：会议摘要、任务分配、频道管理
- Outlook：邮件分类、日程安排、自动回复
- SharePoint：文档搜索、知识库问答
- Excel/PowerPoint：数据分析、报告生成

**生产实践：**
```
# Copilot Studio 多 Agent 编排
用户请求 → Copilot 路由 → 选择合适 Agent → 执行 → 返回结果
                              ├─ Sales Agent（Salesforce 数据）
                              ├─ IT Agent（ServiceNow 工单）
                              └─ HR Agent（Workday 查询）
```

### 2.5 Atlassian Rovo — Jira/Confluence AI 队友

Atlassian 的 AI 产品 Rovo，定位为"AI 队友"，深度集成 Jira、Confluence、JSM。

**三大能力：**

| 能力 | 说明 |
|------|------|
| Rovo Search | 跨 Atlassian + 第三方工具的语义搜索 |
| Rovo Chat | AI 对话，可直接创建 Issue、添加评论、预约会议 |
| Rovo Studio | 低代码构建自定义 Agent，支持 Forge 扩展 |

**Agent Skills 开发（Forge 平台）：**

```yaml
# manifest.yml — Rovo Agent 定义
modules:
  rovo:agent:
    - key: sprint-planner
      name: Sprint Planner Agent
      description: 自动规划 Sprint，分配任务
      prompt: |
        你是一个 Sprint 规划助手。根据 Backlog 中的 Issue 优先级、
        团队成员的工作负载和历史 Velocity，生成 Sprint 计划。
      actions:
        - jira:issue:search
        - jira:issue:update
        - confluence:page:create
```

**生产实践：**
- Rovo 已包含在 Jira/Confluence Premium 和 Enterprise 计划中（2025 年底前全面覆盖）
- Virtual Service Agent 可嵌入 JSM 客户门户，自动处理常见工单
- 支持连接 30+ 第三方数据源（Google Drive、GitHub、Figma 等）

### 2.6 Salesforce Agentforce — CRM Agent 平台

Salesforce 的 Agentforce 360 是目前企业 Agent 领域最成熟的商业产品。

**核心架构：**

```
┌─────────────────────────────────────────┐
│           Agentforce 360                 │
├─────────────────────────────────────────┤
│  Slack（Agentic OS）                     │
│    ├─ Sales Agent（线索跟进、报价）       │
│    ├─ Service Agent（工单处理、知识库）    │
│    ├─ Marketing Agent（活动管理、分析）    │
│    └─ Custom Agent（自定义业务逻辑）      │
├─────────────────────────────────────────┤
│  Data Cloud（统一数据层）                 │
│  Einstein Trust Layer（安全与合规）       │
│  MCP + OpenAI 集成                       │
└─────────────────────────────────────────┘
```

**生产实践：**
- Salesforce 内部已用 Agentforce 处理 83% 的客服请求（官方数据）
- 与 OpenAI、Google Gemini 深度集成，支持多模型路由
- Einstein Trust Layer 提供 PII 脱敏、Prompt 注入防护、审计日志

### 2.7 Google Workspace + Gemini

Google 通过 Gemini 将 AI Agent 能力嵌入 Workspace 全家桶。

**集成方式：**
- Gmail：邮件摘要、智能回复、邮件分类
- Google Docs：文档生成、润色、翻译
- Google Sheets：数据分析、公式生成、图表创建
- Google Meet：会议摘要、实时翻译、待办提取
- Google Chat：AI 助手、自定义 App

**MCP 集成：**
```json
// Google Workspace MCP Server
{
  "mcpServers": {
    "google-workspace": {
      "command": "npx",
      "args": ["-y", "google-workspace-mcp-server"],
      "env": {
        "GOOGLE_APPLICATION_CREDENTIALS": "path/to/credentials.json"
      }
    }
  }
}
```

### 2.8 Composio — 通用 SaaS Agent 集成平台

当你需要连接多个 SaaS 而不想逐一集成时，Composio 是最佳选择。

```python
from composio_openai import ComposioToolSet, Action
from openai import OpenAI

client = OpenAI()
toolset = ComposioToolSet()

# 一行代码连接任意 SaaS
tools = toolset.get_tools(actions=[
    Action.SLACK_SEND_MESSAGE,
    Action.NOTION_CREATE_PAGE,
    Action.JIRA_CREATE_ISSUE,
    Action.GMAIL_SEND_EMAIL,
    Action.GITHUB_CREATE_ISSUE,
])

response = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "在 Slack #general 发消息，同时创建 Jira Issue"}],
    tools=tools,
)
```

**优势：** 1000+ 预构建集成、统一 OAuth 管理、MCP Gateway 模式


## 3. 产品对比矩阵

| 产品 | 厂商 | 集成模式 | 覆盖能力 | 开源 | MCP支持 | 适用场景 |
|------|------|---------|---------|------|---------|---------|
| lark-cli | 飞书/字节 | CLI + Skills | 11域 200+命令 | ✅ MIT | Skills模式 | 飞书生态、开发者 |
| Notion MCP | Notion | MCP Server | 页面/数据库/评论 | ✅ | ✅ 官方托管 | 知识管理、IDE Agent |
| Slack MCP | Slack/Salesforce | MCP + Bot | 消息/频道/搜索 | ✅ | ✅ | 团队协作、Agentic OS |
| Copilot Studio | Microsoft | 平台内嵌 | M365全家桶 | ❌ | ✅ | 企业全员、低代码 |
| Rovo | Atlassian | 平台内嵌 | Jira/Confluence/JSM | ❌ | ❌ | 研发团队、项目管理 |
| Agentforce | Salesforce | 平台内嵌 | CRM全域 | ❌ | ✅ | 销售/客服/营销 |
| Gemini Workspace | Google | 平台内嵌 | Workspace全家桶 | ❌ | ✅ | Google生态用户 |
| Composio | Composio | SDK + MCP | 1000+ SaaS | ✅ | ✅ MCP Gateway | 多平台集成、通用场景 |

## 4. 生产最佳实践

### 4.1 安全与权限

```
┌─ 最小权限原则 ─────────────────────────────────────────┐
│                                                         │
│  1. 按需授权：只授予 Agent 完成任务所需的最小 scope       │
│     lark-cli auth login --domain calendar,task          │
│     （而不是 --recommend 全部授权）                       │
│                                                         │
│  2. 身份隔离：为 Agent 创建专用 Bot/Service Account      │
│     - 飞书：创建独立应用，限制可访问的群组                 │
│     - Slack：专用 Bot User，限制频道                     │
│     - M365：专用 Service Principal                       │
│                                                         │
│  3. 操作审计：记录 Agent 的所有操作                       │
│     - 启用平台审计日志                                    │
│     - Agent 操作前 dry-run 预览                          │
│     - 敏感操作需人工确认（HITL）                          │
│                                                         │
│  4. 凭证安全：                                           │
│     - 使用 OS 原生密钥链（lark-cli 默认行为）             │
│     - 环境变量而非硬编码                                  │
│     - 定期轮换 Token                                     │
│                                                         │
│  5. 输入防注入：                                         │
│     - 净化用户输入（lark-cli 内置防注入）                 │
│     - 限制 Agent 可执行的命令范围                         │
│     - 不要让 Agent 直接拼接 SQL/API 参数                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### 4.2 架构设计模式

**模式一：Hub-and-Spoke（中心辐射）**

适合需要连接多个 SaaS 的场景。

```
                    ┌─────────┐
                    │  Agent  │
                    └────┬────┘
                         │
                  ┌──────┴──────┐
                  │  Composio   │  ← 统一工具层
                  │  MCP Gateway│
                  └──────┬──────┘
            ┌────────┬───┴───┬────────┐
            │        │       │        │
         ┌──┴──┐ ┌──┴──┐ ┌──┴──┐ ┌──┴──┐
         │Slack│ │Jira │ │Gmail│ │Notion│
         └─────┘ └─────┘ └─────┘ └─────┘
```

**模式二：Platform-Native（平台原生）**

适合深度使用单一平台的场景。

```
         ┌─────────────────────────┐
         │    飞书 / Slack / M365   │
         │  ┌───────────────────┐  │
         │  │  内置 AI Agent     │  │
         │  │  (Skills/Copilot) │  │
         │  └────────┬──────────┘  │
         │           │             │
         │  ┌────┬───┴───┬────┐   │
         │  │消息│文档│日历│任务│   │
         │  └────┴───────┴────┘   │
         └─────────────────────────┘
```

**模式三：CLI-First（命令行优先）**

适合开发者和终端 Agent 场景。

```
  Claude Code / Cursor / 终端
         │
         ├─ lark-cli calendar +agenda
         ├─ gh issue create --title "Bug fix"
         ├─ notion-cli search "项目文档"
         └─ slack-cli send "#general" "部署完成"
```

### 4.3 错误处理与重试

```python
import subprocess
import json
import time

def call_lark_cli(command: list[str], max_retries: int = 3) -> dict:
    """带重试的 lark-cli 调用封装"""
    for attempt in range(max_retries):
        try:
            result = subprocess.run(
                ["lark-cli"] + command + ["--format", "json"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                return json.loads(result.stdout)

            error = result.stderr
            # Token 过期 → 自动刷新
            if "token expired" in error.lower():
                subprocess.run(["lark-cli", "auth", "login", "--recommend"])
                continue
            # 限流 → 指数退避
            if "rate limit" in error.lower():
                time.sleep(2 ** attempt)
                continue
            # 其他错误 → 直接抛出
            raise RuntimeError(f"lark-cli error: {error}")

        except subprocess.TimeoutExpired:
            if attempt < max_retries - 1:
                continue
            raise

    raise RuntimeError(f"Failed after {max_retries} retries")
```

### 4.4 监控与可观测性

```python
# 生产环境建议的监控指标
METRICS = {
    "agent.api.calls": "Agent API 调用次数（按平台/操作分类）",
    "agent.api.latency": "API 调用延迟（P50/P95/P99）",
    "agent.api.errors": "API 错误率（按错误类型分类）",
    "agent.auth.refreshes": "Token 刷新次数",
    "agent.actions.total": "Agent 执行的操作总数",
    "agent.actions.hitl": "需要人工确认的操作数",
    "agent.cost.tokens": "LLM Token 消耗",
}
```

## 5. 端到端实战：多平台 Agent 助手

一个完整的生产级示例：Agent 同时操作飞书、GitHub、Notion。

```python
"""多平台办公 Agent — 每日站会自动化"""

from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from composio_langchain import ComposioToolSet, Action

# 初始化
llm = ChatOpenAI(model="gpt-5.2")
toolset = ComposioToolSet()

# 获取多平台工具
tools = toolset.get_tools(actions=[
    # 飞书
    Action.LARK_GET_CALENDAR_EVENTS,
    Action.LARK_SEND_MESSAGE,
    # GitHub
    Action.GITHUB_LIST_ISSUES,
    Action.GITHUB_LIST_PULL_REQUESTS,
    # Notion
    Action.NOTION_QUERY_DATABASE,
    Action.NOTION_CREATE_PAGE,
])

agent = create_react_agent(llm, tools)

# 每日站会自动化
result = agent.invoke({
    "messages": [{
        "role": "user",
        "content": """
        执行每日站会准备：
        1. 从飞书日历获取今天的会议安排
        2. 从 GitHub 获取昨天合并的 PR 和未关闭的 Issue
        3. 从 Notion 项目数据库获取本周任务进度
        4. 生成站会摘要，发送到飞书群聊 oc_xxx
        5. 同时在 Notion 创建站会记录页面
        """
    }]
})
```

## 6. 选型决策树

```
你的场景是什么？
│
├─ 深度使用飞书 → lark-cli（开源、200+命令、Agent原生）
│
├─ 深度使用 M365 → Copilot Studio（低代码、多Agent编排）
│
├─ 深度使用 Jira/Confluence → Rovo（内置AI队友、Forge扩展）
│
├─ 深度使用 Salesforce → Agentforce（CRM Agent、Slack集成）
│
├─ IDE Agent 需要操作 SaaS → MCP Server（Notion/Slack/GitHub 官方MCP）
│
├─ 需要连接多个 SaaS → Composio（1000+集成、统一认证）
│
└─ 自研 Agent 需要灵活控制 → CLI 模式 + LangGraph/CrewAI 编排
```

## 7. 趋势与展望

1. **MCP 成为标准** — Notion、Slack、GitHub 等主流平台已提供官方 MCP Server，2026 年将成为 Agent 接入企业 SaaS 的事实标准
2. **CLI Skills 化** — lark-cli 开创的"CLI + Agent Skills"模式正在被更多平台采纳，让 Agent 通过命令行操作一切
3. **多 Agent 编排** — Copilot Studio、Agentforce 已支持多 Agent 协作，一个请求可路由到多个专业 Agent
4. **安全治理前置** — Einstein Trust Layer、lark-cli 内置防注入等安全机制成为标配，而非事后补救
5. **平台 Agentic OS 化** — Slack 自称"Agentic OS"，飞书推出"智能伙伴"，办公平台正从工具变为 Agent 运行时

## 🎬 推荐视频资源

### 🌐 YouTube
- [Salesforce - Agentforce Demo](https://www.youtube.com/watch?v=F8NKVhkZZWI) — Agentforce 360 官方演示
- [Microsoft - Copilot Studio Tutorial](https://www.youtube.com/watch?v=pHksBVqH7uI) — Copilot Studio 教程
- [Notion - MCP Server Introduction](https://www.youtube.com/watch?v=kQmXtrmQ5Zg) — Notion MCP 官方介绍
- [Composio - Agent Tools Platform](https://www.youtube.com/watch?v=nMGCE4GU1kc) — Composio 平台介绍

### 📺 B站
- [飞书开放平台教程](https://www.bilibili.com/video/BV1dH4y1P7FY) — 飞书 API 开发中文教程
- [AI Agent 企业落地实战](https://www.bilibili.com/video/BV1Bm421N7BH) — 企业 Agent 集成中文教程

### 📖 官方文档
- [lark-cli GitHub](https://github.com/larksuite/cli) — 飞书 CLI 开源项目（MIT）
- [Notion MCP Docs](https://developers.notion.com/guides/mcp/mcp) — Notion MCP 官方文档
- [Slack MCP Server](https://github.com/anthropics/slack-mcp-server) — Slack MCP Server
- [Copilot Studio Docs](https://learn.microsoft.com/en-us/microsoft-copilot-studio/) — 微软 Copilot Studio
- [Rovo Developer Docs](https://developer.atlassian.com/platform/forge/manifest-reference/modules/rovo-agent/) — Atlassian Rovo Agent 开发
- [Composio Docs](https://docs.composio.dev/) — Composio 官方文档
- [Google Workspace MCP](https://cloud.google.com/blog/topics/developers-practitioners/use-google-adk-and-mcp-with-an-external-server) — Google MCP 集成指南
