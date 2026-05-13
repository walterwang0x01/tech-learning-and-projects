# Composio 工具平台
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

> 🔄 更新于 2026-04-18

<!-- version-check: Composio SDK TS 0.6.0+, Python 0.11.0+, 50000+ 工具, checked 2026-04-18 -->

Composio 提供 **50,000+** 预构建工具集成（覆盖 **1,000+** 应用、**10,000+** API），让 AI Agent 能连接 GitHub、Slack、Jira、Gmail 等外部服务。核心价值：统一认证管理 + 元工具发现 + MCP Gateway + AI 反馈循环自动优化工具。

> **2026 重大更新**（[来源](https://docs.composio.dev/changelog)）：
> - **SDK 0.6.0+**（2026-01-29）：TypeScript 0.6.0+ / Python 0.11.0+，支持 **Cloudflare Workers**，Breaking Changes
> - **50,000+ 工具**：从 1,000+ 增长到 50,000+ 工具，覆盖 1,000+ 应用（[来源](https://www.cognitiverevolution.ai/your-agent-s-self-improving-swiss-army-knife-composio-cto-karan-vaidya-on-building-smart-tools/)）
> - **AI 反馈循环**：工具执行结果自动反馈，AI 驱动的工具质量持续优化
> - **多账户支持**：Sessions 支持 `multiAccount` 配置，同一 toolkit 可连接多个账户（如工作和个人 Gmail）
> - **废弃工具标记**：~230 个工具（70+ 应用）已标记 `deprecated = True`，通过交叉引用官方 API 文档识别

```
┌─────────────────────────────────────────────┐
│              AI Agent                        │
├─────────────────────────────────────────────┤
│              Composio                        │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │元工具发现  │ │认证管理   │ │MCP Gateway│  │
│  │Meta-Tool │ │OAuth2    │ │            │  │
│  │Discovery │ │Management│ │            │  │
│  └──────────┘ └──────────┘ └────────────┘  │
├─────────────────────────────────────────────┤
│  GitHub │ Slack │ Jira │ Gmail │ 250+ Apps  │
└─────────────────────────────────────────────┘
```

## 2. 快速开始

```bash
pip install composio-core composio-openai
composio login  # 登录 Composio 账户
composio add github  # 连接 GitHub（OAuth 授权）
```

```python
from composio_openai import ComposioToolSet, Action
from openai import OpenAI

client = OpenAI()
toolset = ComposioToolSet()

# 获取 GitHub 工具
tools = toolset.get_tools(actions=[
    Action.GITHUB_CREATE_ISSUE,
    Action.GITHUB_LIST_REPOS,
    Action.GITHUB_STAR_REPO,
])

# 使用 OpenAI Function Calling
# <!-- 修复于 2026-05-13: gpt-4o → gpt-5.2 -->
response = client.chat.completions.create(
    model="gpt-5.2",
    messages=[{"role": "user", "content": "在 my-org/my-repo 创建一个 bug issue，标题是'登录页面500错误'"}],
    tools=tools,
)

# 执行工具调用
result = toolset.handle_tool_call(response)
print(result)
```

## 3. 与 LangChain 集成

```python
from composio_langchain import ComposioToolSet, Action
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

toolset = ComposioToolSet()

# 获取多个服务的工具
tools = toolset.get_tools(actions=[
    Action.GITHUB_CREATE_ISSUE,
    Action.SLACK_SEND_MESSAGE,
    Action.JIRA_CREATE_ISSUE,
    Action.GMAIL_SEND_EMAIL,
])

llm = ChatOpenAI(model="gpt-5.2")
agent = create_react_agent(llm, tools=tools)

result = agent.invoke({
    "messages": [("user", "在 Jira 创建一个高优先级 bug，然后在 Slack #dev 频道通知团队")]
})
```

## 4. 与 CrewAI 集成

```python
from composio_crewai import ComposioToolSet, App
from crewai import Agent, Task, Crew

toolset = ComposioToolSet()

# 按应用获取所有工具
github_tools = toolset.get_tools(apps=[App.GITHUB])
slack_tools = toolset.get_tools(apps=[App.SLACK])

devops_agent = Agent(
    role="DevOps 工程师",
    goal="管理代码仓库和团队通知",
    tools=github_tools + slack_tools,
    llm="gpt-5.2",
)

task = Task(
    description="检查 main 分支最近的 PR，合并已通过审查的，通知团队",
    agent=devops_agent,
)

crew = Crew(agents=[devops_agent], tasks=[task])
result = crew.kickoff()
```

## 5. 认证管理

Composio 统一管理 250+ 应用的 OAuth2 认证。

```python
from composio import ComposioToolSet

toolset = ComposioToolSet()

# 为特定用户创建认证连接
# 方式1：OAuth2 授权流程
auth_url = toolset.initiate_connection(
    app="github",
    entity_id="user-alice",  # 用户标识
    redirect_url="https://myapp.com/callback",
)
# → 返回 OAuth 授权 URL，用户点击授权

# 方式2：API Key 方式
toolset.create_connection(
    app="openai",
    entity_id="user-alice",
    config={"api_key": "sk-xxx"},
)

# 多用户隔离：每个用户独立的认证
alice_tools = toolset.get_tools(
    actions=[Action.GITHUB_LIST_REPOS],
    entity_id="user-alice",  # Alice 的 GitHub
)
bob_tools = toolset.get_tools(
    actions=[Action.GITHUB_LIST_REPOS],
    entity_id="user-bob",    # Bob 的 GitHub
)
```

## 6. MCP Gateway

Composio 作为 MCP 中心网关，统一管理 Agent 与工具的连接。

```json
{
  "mcpServers": {
    "composio": {
      "command": "npx",
      "args": ["-y", "composio-mcp"],
      "env": {
        "COMPOSIO_API_KEY": "your-api-key"
      }
    }
  }
}
```

```python
# 通过 MCP 协议访问 Composio 工具
from composio import ComposioToolSet

toolset = ComposioToolSet()

# MCP 模式：动态发现可用工具
available_tools = toolset.find_actions_by_use_case(
    use_case="管理 GitHub 仓库的 issue 和 PR",
    limit=5,
)
# → 自动推荐最相关的 Action

# 元工具：让 Agent 自己发现需要的工具
meta_tools = toolset.get_tools(actions=[
    Action.COMPOSIO_SEARCH_TOOLS,  # 搜索可用工具
    Action.COMPOSIO_EXECUTE_TOOL,  # 执行任意工具
])
```

## 7. 实战：自动化 DevOps Agent

```python
from composio_openai import ComposioToolSet, Action
from openai import OpenAI

client = OpenAI()
toolset = ComposioToolSet()

tools = toolset.get_tools(actions=[
    Action.GITHUB_LIST_PULL_REQUESTS,
    Action.GITHUB_MERGE_PULL_REQUEST,
    Action.GITHUB_CREATE_ISSUE,
    Action.SLACK_SEND_MESSAGE,
    Action.JIRA_UPDATE_ISSUE,
])

def devops_agent(instruction: str) -> str:
    messages = [
        {"role": "system", "content": """你是 DevOps Agent，负责：
1. 管理 GitHub PR 和 Issue
2. 在 Slack 通知团队
3. 更新 Jira 任务状态
执行操作前确认关键步骤。"""},
        {"role": "user", "content": instruction},
    ]

    while True:
        response = client.chat.completions.create(
            model="gpt-5.2", messages=messages, tools=tools,
        )
        msg = response.choices[0].message

        if not msg.tool_calls:
            return msg.content

        # 执行工具调用
        messages.append(msg)
        for tc in msg.tool_calls:
            result = toolset.execute_tool_call(tc)
            messages.append({
                "role": "tool", "tool_call_id": tc.id,
                "content": str(result),
            })

result = devops_agent("检查 my-org/api-server 的待合并 PR，合并通过 CI 的，通知 #releases 频道")
```

## 8. 支持的应用类别

```
开发工具：GitHub, GitLab, Bitbucket, Linear, Jira
通信协作：Slack, Discord, Teams, Gmail, Outlook
云服务：  AWS, GCP, Azure, Vercel, Netlify
数据库：  PostgreSQL, MySQL, MongoDB, Supabase
CRM：    Salesforce, HubSpot, Pipedrive
文档：    Notion, Confluence, Google Docs
存储：    Google Drive, Dropbox, S3
支付：    Stripe, PayPal
监控：    Datadog, PagerDuty, Sentry
其他：    Zapier, Airtable, Twilio, SendGrid
```

| 特性         | Composio        | Toolhouse       | Arcade AI       |
|-------------|-----------------|-----------------|-----------------|
| 工具数量     | 50,000+         | 100+            | 50+             |
| 认证管理     | ✅ OAuth2 统一  | ✅              | ✅              |
| MCP 支持    | ✅ Gateway      | ✅              | ❌              |
| 框架集成     | 广泛            | OpenAI/LangChain| OpenAI          |
| 元工具发现   | ✅              | ❌              | ❌              |
| 自托管       | ❌ 仅云服务     | ❌              | ❌              |
| AI 反馈优化  | ✅              | ❌              | ❌              |
## 🎬 推荐视频资源

### 🌐 YouTube
- [Composio - 1000+ Tools for AI Agents](https://www.youtube.com/watch?v=nMGCE4GU1kc) — Composio平台介绍
- [AI Jason - Best Agent Tools](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — Agent工具平台对比

### 📖 官方文档
- [Composio Docs](https://docs.composio.dev/) — Composio官方文档
