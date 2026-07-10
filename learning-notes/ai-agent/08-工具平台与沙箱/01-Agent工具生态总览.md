# Agent 工具生态总览
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 工具生态全景图

```
┌─────────────────────────────────────────────────────────┐
│                    AI Agent 工具生态                      │
├──────────────┬──────────────┬──────────────┬────────────┤
│  工具平台     │  代码沙箱     │  浏览器自动化  │  搜索引擎   │
│  Composio    │  E2B         │  Browserbase │  Tavily    │
│  Toolhouse   │  Modal       │  Steel       │  Exa       │
│  Arcade AI   │  Daytona     │  Playwright  │  SerpAPI   │
│              │              │  Puppeteer   │  Brave     │
├──────────────┼──────────────┼──────────────┼────────────┤
│  数据抓取     │  文件处理     │  通信集成     │  MCP 生态   │
│  Firecrawl   │  LlamaParse  │  Slack       │  1000+     │
│  Jina Reader │  Unstructured│  Gmail       │  MCP       │
│  Crawl4AI    │  Docling     │  Teams       │  Servers   │
└──────────────┴──────────────┴──────────────┴────────────┘
```

## 2. 工具平台

### Composio

```python
# 1000+ 工具集成，统一认证
from composio_openai import ComposioToolSet, Action
toolset = ComposioToolSet()
tools = toolset.get_tools(actions=[Action.GITHUB_CREATE_ISSUE])
```

### Toolhouse

```python
# 开发者友好的工具平台
from toolhouse import Toolhouse
th = Toolhouse(api_key="th_xxx")
tools = th.get_tools()  # 获取所有可用工具

response = client.chat.completions.create(
    # <!-- 修复于 2026-07-10: gpt-5.2 → gpt-5.6（OpenAI 于 2026-07-09 发布 GPT-5.6 系列，gpt-5.6 别名默认路由到 gpt-5.6-sol） -->
    model="gpt-5.6", messages=messages, tools=tools,
)
result = th.run_tools(response)  # 自动执行工具调用
```

### Arcade AI

```python
# 专注认证的工具平台
from arcadepy import Arcade
arcade = Arcade(api_key="arc_xxx")

# 授权用户访问 Google Calendar
auth = arcade.tools.authorize(tool_name="Google.ListEvents", user_id="user1")
result = arcade.tools.execute(
    tool_name="Google.ListEvents",
    user_id="user1",
    inputs={"n_events": 5},
)
```

## 3. 代码沙箱

### E2B

```python
from e2b_code_interpreter import Sandbox
with Sandbox() as sbx:
    result = sbx.run_code("print(sum(range(100)))")
```

### Modal

```python
import modal

app = modal.App("agent-sandbox")

@app.function(image=modal.Image.debian_slim().pip_install("pandas", "numpy"))
def run_analysis(code: str) -> str:
    """在 Modal 云端执行代码"""
    exec_globals = {}
    exec(code, exec_globals)
    return str(exec_globals.get("result", "done"))
```

### Daytona

```python
# 开发环境即服务
from daytona_sdk import Daytona

daytona = Daytona()
sandbox = daytona.create(language="python")
response = sandbox.process.code_run('print("Hello")')
print(response.result)
sandbox.delete()
```

## 4. 浏览器自动化

### Browserbase

```python
from browserbase import Browserbase

bb = Browserbase(api_key="bb_xxx")
session = bb.sessions.create(project_id="proj_xxx")

# 与 Playwright 结合
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(session.connect_url)
    page = browser.new_page()
    page.goto("https://example.com")
    content = page.content()
```

### Playwright MCP

```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@playwright/mcp-server"]
    }
  }
}
```

### Steel

```python
from steel import Steel

steel = Steel(api_key="steel_xxx")
session = steel.sessions.create()

# 云端浏览器，支持反检测
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.connect_over_cdp(session.connect_url)
    page = browser.new_page()
    page.goto("https://target-site.com")
    # Steel 自动处理验证码、指纹等
```

## 5. 搜索引擎

### Tavily

```python
from tavily import TavilyClient

tavily = TavilyClient(api_key="tvly-xxx")

# 专为 AI Agent 优化的搜索
result = tavily.search(
    query="LangGraph vs CrewAI 2025 comparison",
    search_depth="advanced",
    max_results=5,
    include_answer=True,  # 直接返回答案摘要
)
print(result["answer"])
for r in result["results"]:
    print(f"- {r['title']}: {r['url']}")
```

### Exa

```python
from exa_py import Exa

exa = Exa(api_key="exa-xxx")

# 语义搜索（理解意图而非关键词匹配）
results = exa.search_and_contents(
    "最新的 AI Agent 框架对比分析",
    type="neural",
    num_results=5,
    text=True,
)
for r in results.results:
    print(f"{r.title}\n{r.text[:200]}\n")
```

### Brave Search

<!-- 修复于 2026-05-13: 包名从 @anthropic/mcp-server-brave-search 更正为 @modelcontextprotocol/server-brave-search -->

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {"BRAVE_API_KEY": "BSA_xxx"}
    }
  }
}
```

## 6. 数据抓取

### Firecrawl

```python
from firecrawl import FirecrawlApp

fc = FirecrawlApp(api_key="fc-xxx")

# 抓取单页（转为 Markdown）
result = fc.scrape_url("https://docs.example.com/guide", params={
    "formats": ["markdown"],
})
print(result["markdown"])

# 爬取整个站点
crawl = fc.crawl_url("https://docs.example.com", params={
    "limit": 50,
    "scrapeOptions": {"formats": ["markdown"]},
})
for page in crawl["data"]:
    print(f"URL: {page['metadata']['url']}")
```

### Jina Reader

```python
import requests

# 将任意 URL 转为 LLM 友好的文本
url = "https://example.com/article"
response = requests.get(f"https://r.jina.ai/{url}")
markdown_content = response.text
```

## 7. MCP Server 生态

```
MCP Server 目录（1000+ 服务器）：

开发工具：
├─ @modelcontextprotocol/server-github     # GitHub 操作
├─ @modelcontextprotocol/server-gitlab     # GitLab 操作
├─ @modelcontextprotocol/server-filesystem # 文件系统
└─ @modelcontextprotocol/server-memory     # 知识图谱

数据库：
├─ @modelcontextprotocol/server-postgres   # PostgreSQL
├─ @modelcontextprotocol/server-sqlite     # SQLite
└─ mcp-server-mongodb                      # MongoDB

搜索与数据：
├─ @anthropic/mcp-server-brave-search      # Brave 搜索
├─ mcp-server-tavily                       # Tavily 搜索
└─ @anthropic/mcp-server-fetch             # URL 抓取

云服务：
├─ mcp-server-aws                          # AWS 操作
├─ @cloudflare/mcp-server-cloudflare       # Cloudflare
└─ mcp-server-kubernetes                   # K8s 管理
```

## 8. 工具发现与选择策略

```
工具选择决策树：

需要连接外部 SaaS？
├─ YES → Composio（1000+ 集成，统一认证）
└─ NO ↓

需要执行代码？
├─ YES → E2B（安全沙箱）/ Modal（云端执行）
└─ NO ↓

需要浏览网页？
├─ YES → Browserbase / Playwright MCP
└─ NO ↓

需要搜索信息？
├─ YES → Tavily（AI优化）/ Exa（语义搜索）
└─ NO ↓

需要抓取网页？
├─ YES → Firecrawl（站点爬取）/ Jina（单页转换）
└─ NO ↓

查找 MCP Server 目录
```

## 9. 构建 vs 购买决策

| 维度       | 自建工具              | 使用平台/MCP Server    |
|-----------|----------------------|----------------------|
| 开发成本   | 高（认证、错误处理）    | 低（开箱即用）         |
| 定制化     | 完全可控              | 受限于平台能力         |
| 维护成本   | 需持续维护 API 变更    | 平台负责维护           |
| 安全性     | 自行保障              | 依赖平台安全           |
| 适用场景   | 核心业务逻辑           | 通用集成（GitHub等）   |

```
建议策略：
├─ 通用集成（GitHub/Slack/Jira）→ 用 Composio / MCP Server
├─ 代码执行 → 用 E2B（安全隔离）
├─ 搜索能力 → 用 Tavily / Brave Search MCP
├─ 核心业务逻辑 → 自建 MCP Server
└─ 内部 API → 自建 MCP Server + 认证
```
## 🎬 推荐视频资源

### 🌐 YouTube
- [AI Jason - Agent Tools Ecosystem](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — Agent工具生态讲解
- [DeepLearning.AI - Functions, Tools and Agents](https://www.deeplearning.ai/short-courses/functions-tools-agents-langchain/) — 工具与Agent（免费）
