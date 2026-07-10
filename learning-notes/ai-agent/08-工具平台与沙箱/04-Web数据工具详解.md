# Web 数据工具详解
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

AI Agent 需要从互联网获取实时信息，Web 数据工具是 Agent 的"眼睛"和"搜索引擎"。本文覆盖 Firecrawl、Tavily、Exa、Jina Reader、Brave Search、SerpAPI、Apify 七大工具，从搜索到抓取到内容提取的完整链路。

```
┌─────────── Agent Web 数据获取架构 ───────────┐
│                                                │
│  ┌──────────┐                                 │
│  │ AI Agent │                                 │
│  └─────┬────┘                                 │
│        │ 需要外部数据                          │
│  ┌─────┴──────────────────────────────┐       │
│  │         Web 数据工具层              │       │
│  │                                     │       │
│  │  搜索类          抓取类    提取类    │       │
│  │  ┌────────┐  ┌────────┐ ┌───────┐ │       │
│  │  │ Tavily │  │Firecrawl│ │ Jina  │ │       │
│  │  │ Brave  │  │ Apify  │ │Reader │ │       │
│  │  │ Exa    │  │        │ │       │ │       │
│  │  │ Serper │  │        │ │       │ │       │
│  │  └────────┘  └────────┘ └───────┘ │       │
│  └─────────────────┬──────────────────┘       │
│                    │                           │
│              ┌─────┴─────┐                    │
│              │ 清洁数据   │                    │
│              │ Markdown / │                    │
│              │ JSON       │                    │
│              └─────┬─────┘                    │
│                    │                           │
│              ┌─────┴─────┐                    │
│              │ RAG / LLM │                    │
│              │ 处理与回答 │                    │
│              └───────────┘                    │
└────────────────────────────────────────────────┘
```

## 2. Firecrawl（148K+ GitHub Stars）

> 🔄 更新于 2026-07-10

<!-- version-check: Firecrawl v2.11.0（2026-06-19）+ /monitor（2026-07-01），checked 2026-07-10 -->
<!-- 修复于 2026-07-10: v2.9.0 → v2.11.0；GitHub Stars 82K+ → 148K+；补充 /monitor、Research Index -->

Web 抓取 API，将任意 URL 转换为干净的 Markdown/JSON，专为 AI Agent 和 RAG 设计。

```
核心特性：
├─ Scrape：单页面抓取 → 干净 Markdown
├─ Crawl：整站爬取（自动发现链接）
├─ Search：搜索 + 抓取（搜索引擎 + 内容提取）
├─ Extract：结构化数据提取（LLM 驱动）
├─ /monitor：web-scale 全网监控，匹配即告警（v2026-07-01 新增）
├─ /interact：浏览器交互端点
├─ Research Index：3M+ arXiv 论文 + GitHub 代码专用索引（v2.11.0）
├─ Keyless 访问：核心端点无需 API Key，每月 1000 免费额度（v2.11.0）
├─ PII 自动脱敏、deterministicJson 固定结构提取（v2.11.0）
├─ Fire-PDF：Rust 引擎，PDF 解析速度提升 5x，上限提升至 50MB
├─ web-agent：开源 AI Agent 框架
├─ JS 渲染：自动执行 JavaScript（SPA 友好）
├─ 反爬处理：自动处理 Cloudflare 等反爬机制
├─ MCP Server：firecrawl-mcp，Agent 直接调用
├─ SDK：Python、JS、Go、Rust、Java、Elixir、Ruby、PHP、.NET
└─ 自托管：开源，可自行部署
```

> **v2.11.0 重大更新**（2026-06-19，[来源](https://www.firecrawl.dev/changelog)）：
> - **Research Index**：专为 AI/ML 研究设计的索引，覆盖 3M+ arXiv 论文和 GitHub 代码
> - **Keyless 访问**：核心端点（scrape/search）无需 API Key 即可调用，每月 1000 次免费额度
> - **PII 自动脱敏**：抓取结果自动检测并遮蔽个人信息
> - **deterministicJson**：可复用的固定结构提取格式，替代每次重新生成 Schema
> - **视频发现**：任意页面自动识别嵌入视频
> - **/monitor**（2026-07-01 新增）：定义搜索 query + goal，Firecrawl 持续监控全网变化，匹配时通过 Webhook/邮件告警

### Python SDK 示例

```python
from firecrawl import FirecrawlApp

app = FirecrawlApp(api_key="fc-xxx")

# ─── 模式 1: Scrape（单页面抓取）───
result = app.scrape_url(
    "https://docs.python.org/3/tutorial/index.html",
    params={
        "formats": ["markdown", "html"],     # 输出格式
        "onlyMainContent": True,             # 只提取主要内容
        "waitFor": 3000,                     # 等待 JS 渲染 3 秒
        "headers": {"Accept-Language": "zh-CN"},
    }
)
print(result["markdown"][:500])  # 干净的 Markdown 内容

# ─── 模式 2: Crawl（整站爬取）───
crawl_result = app.crawl_url(
    "https://docs.example.com",
    params={
        "limit": 50,                         # 最多爬 50 页
        "maxDepth": 3,                       # 最大深度 3 层
        "includePaths": ["/docs/*"],         # 只爬 /docs/ 下的页面
        "excludePaths": ["/blog/*"],         # 排除 /blog/
        "scrapeOptions": {
            "formats": ["markdown"],
            "onlyMainContent": True,
        }
    },
    poll_interval=5,  # 每 5 秒检查一次进度
)
for page in crawl_result.data:
    print(f"URL: {page['metadata']['url']}")
    print(f"内容: {page['markdown'][:200]}...")

# ─── 模式 3: Search（搜索 + 抓取）───
search_result = app.search(
    query="Python asyncio 最佳实践 2025",
    params={
        "limit": 5,                          # 返回 5 条结果
        "lang": "zh",
        "scrapeOptions": {
            "formats": ["markdown"],
            "onlyMainContent": True,
        }
    }
)
for item in search_result.data:
    print(f"标题: {item['metadata']['title']}")
    print(f"URL: {item['metadata']['url']}")
    print(f"内容: {item['markdown'][:300]}...")

# ─── 模式 4: Extract（结构化提取）───
extract_result = app.extract(
    urls=["https://example.com/product/123"],
    params={
        "prompt": "提取商品名称、价格、评分、库存状态",
        "schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "price": {"type": "number"},
                "rating": {"type": "number"},
                "in_stock": {"type": "boolean"},
            }
        }
    }
)
print(extract_result)  # {"name": "...", "price": 299.0, "rating": 4.5, "in_stock": true}
```

### Firecrawl MCP Server 配置

```json
{
  "mcpServers": {
    "firecrawl": {
      "command": "npx",
      "args": ["-y", "firecrawl-mcp"],
      "env": {
        "FIRECRAWL_API_KEY": "fc-xxx"
      }
    }
  }
}
```

## 3. Tavily — AI Agent 专用搜索 API

专为 AI Agent 和 RAG 设计的搜索 API，返回干净、相关的搜索结果，LLM 可直接消费。

```
核心特性：
├─ AI 优化：搜索结果针对 LLM 消费优化
├─ Search：快速搜索，返回摘要 + 原文
├─ Extract：从 URL 提取内容
├─ Deep Research：深度研究（多轮搜索+综合）
├─ LangChain 原生：TavilySearchResults 工具
├─ LlamaIndex 集成：TavilyToolSpec
└─ 免费额度：每月 1000 次免费搜索
```

### Python 示例

```python
from tavily import TavilyClient

client = TavilyClient(api_key="tvly-xxx")

# ─── 基础搜索 ───
results = client.search(
    query="2025 年最好的 Python Web 框架",
    search_depth="advanced",     # basic | advanced（更深入）
    max_results=5,
    include_answer=True,         # 返回 AI 生成的摘要答案
    include_raw_content=True,    # 返回原始页面内容
    include_domains=["github.com", "python.org"],  # 限定域名
)

# AI 生成的摘要答案
print(f"答案: {results['answer']}")

# 搜索结果
for r in results["results"]:
    print(f"标题: {r['title']}")
    print(f"URL: {r['url']}")
    print(f"摘要: {r['content'][:200]}")
    print(f"相关度: {r['score']}")
    print("---")

# ─── 内容提取 ───
extracted = client.extract(
    urls=["https://docs.python.org/3/whatsnew/3.13.html"]
)
for item in extracted["results"]:
    print(f"URL: {item['url']}")
    print(f"内容: {item['raw_content'][:500]}")

# ─── 与 LangChain 集成 ───
from langchain_community.tools.tavily_search import TavilySearchResults

tavily_tool = TavilySearchResults(
    max_results=5,
    search_depth="advanced",
    include_answer=True,
)
# 直接作为 Agent 工具使用
result = tavily_tool.invoke({"query": "LangGraph vs CrewAI 对比"})
```

## 4. Exa（原 Metaphor）— 神经搜索引擎

语义搜索引擎，理解查询的含义而非关键词匹配，最适合研究和知识发现。

```
核心特性：
├─ 语义搜索：理解意图，不只是关键词匹配
├─ 内容提取：搜索结果 + 干净内容
├─ 相似搜索：找到与给定 URL 相似的页面
├─ 类别过滤：论文、新闻、公司、GitHub 等
├─ 时间过滤：按发布日期筛选
└─ 高质量源：偏向高质量内容源
```

### Python 示例

```python
from exa_py import Exa

exa = Exa(api_key="exa-xxx")

# ─── 语义搜索 ───
results = exa.search_and_contents(
    query="使用 Transformer 架构进行时间序列预测的最新研究",
    type="neural",                # neural（语义）| keyword | auto
    num_results=5,
    text=True,                    # 返回页面文本内容
    highlights=True,              # 返回高亮片段
    start_published_date="2025-01-01",  # 只要 2025 年的
    category="research paper",    # 限定类别
)

for r in results.results:
    print(f"标题: {r.title}")
    print(f"URL: {r.url}")
    print(f"发布日期: {r.published_date}")
    print(f"高亮: {r.highlights[:2]}")
    print(f"内容: {r.text[:300]}...")
    print("---")

# ─── 相似页面搜索 ───
similar = exa.find_similar_and_contents(
    url="https://arxiv.org/abs/2306.07967",  # 找与这篇论文相似的
    num_results=5,
    text=True,
)
for r in similar.results:
    print(f"相似: {r.title} — {r.url}")

# ─── 关键词搜索（精确匹配）───
keyword_results = exa.search_and_contents(
    query="FastAPI SQLAlchemy tutorial",
    type="keyword",
    num_results=3,
    text={"max_characters": 2000},  # 限制内容长度
)
```

## 5. Jina Reader — 极简 URL 转文本

最简单的网页内容提取工具，只需在 URL 前加 `r.jina.ai/` 即可获取干净文本。

```
核心特性：
├─ 极简 API：r.jina.ai/{url} 即可使用
├─ 免费额度：有免费调用额度
├─ 多格式：Markdown / 纯文本 / HTML
├─ JS 渲染：自动处理 JavaScript 页面
├─ 图片描述：自动为图片生成 alt 文本
└─ 无需注册：免费版无需 API Key
```

### 使用示例

```python
import httpx

# ─── 方式 1: 直接 HTTP 请求（最简单）───
url = "https://r.jina.ai/https://docs.python.org/3/tutorial/index.html"
response = httpx.get(url, headers={
    "Accept": "text/markdown",           # 返回 Markdown
    "X-With-Generated-Alt": "true",      # 为图片生成描述
})
print(response.text[:500])

# ─── 方式 2: 带 API Key（更高限额）───
response = httpx.get(
    "https://r.jina.ai/https://example.com/article",
    headers={
        "Authorization": "Bearer jina_xxx",
        "Accept": "application/json",    # 返回 JSON 格式
        "X-Return-Format": "markdown",
    }
)
data = response.json()
print(f"标题: {data['data']['title']}")
print(f"内容: {data['data']['content'][:500]}")

# ─── 方式 3: 搜索功能 ───
search_url = "https://s.jina.ai/Python+asyncio+best+practices+2025"
response = httpx.get(search_url, headers={
    "Accept": "application/json",
})
results = response.json()
for item in results["data"]:
    print(f"标题: {item['title']}")
    print(f"URL: {item['url']}")
    print(f"内容: {item['content'][:200]}")
```

## 6. Brave Search API

隐私优先的搜索 API，免费额度慷慨，MCP Server 可用。

```
核心特性：
├─ 隐私优先：不追踪用户
├─ Web 搜索：网页、新闻、图片
├─ 免费额度：每月 2000 次免费
├─ MCP Server：brave-search MCP 可用
├─ 本地搜索：支持地理位置搜索
└─ 结构化结果：FAQ、视频、新闻等分类
```

```python
import httpx

# Brave Search API
headers = {
    "Accept": "application/json",
    "Accept-Encoding": "gzip",
    "X-Subscription-Token": "BSA-xxx",
}

response = httpx.get(
    "https://api.search.brave.com/res/v1/web/search",
    params={
        "q": "AI Agent 开发框架 2025",
        "count": 5,
        "search_lang": "zh-hans",
        "freshness": "pm",  # 过去一个月
    },
    headers=headers,
)

data = response.json()
for result in data["web"]["results"]:
    print(f"标题: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"描述: {result['description']}")
    print("---")
```

### Brave Search MCP 配置

<!-- 修复于 2026-05-13: 包名从 @anthropic/brave-search-mcp 更正为 @modelcontextprotocol/server-brave-search -->

```json
{
  "mcpServers": {
    "brave-search": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-brave-search"],
      "env": {
        "BRAVE_API_KEY": "BSA-xxx"
      }
    }
  }
}
```

## 7. SerpAPI / Serper — Google 搜索结果 API

获取 Google 搜索结构化结果，CrewAI 的 SerperDevTool 基于此。

```
核心特性：
├─ Google 结果：获取真实 Google 搜索结果
├─ 结构化数据：有机结果、知识图谱、FAQ、视频
├─ 多搜索引擎：Google, Bing, Yahoo, Baidu
├─ CrewAI 集成：SerperDevTool 原生支持
└─ 高可靠性：企业级 SLA
```

```python
# ─── Serper（更简单，CrewAI 推荐）───
import httpx

response = httpx.post(
    "https://google.serper.dev/search",
    headers={"X-API-KEY": "serper-xxx"},
    json={
        "q": "best AI agent frameworks 2025",
        "gl": "cn",       # 地区
        "hl": "zh-cn",    # 语言
        "num": 5,
    }
)
data = response.json()

# 有机搜索结果
for r in data.get("organic", []):
    print(f"标题: {r['title']}")
    print(f"链接: {r['link']}")
    print(f"摘要: {r['snippet']}")

# 知识图谱
if "knowledgeGraph" in data:
    kg = data["knowledgeGraph"]
    print(f"知识图谱: {kg.get('title')} — {kg.get('description')}")

# ─── 与 CrewAI 集成 ───
from crewai_tools import SerperDevTool

search_tool = SerperDevTool()
# 直接作为 CrewAI Agent 的工具使用
```

## 8. Apify — 企业级 Web 抓取平台

2000+ 预构建爬虫（Actors），企业级 Web 数据采集平台。

```
核心特性：
├─ 2000+ Actors：预构建爬虫（Amazon/Twitter/Google Maps 等）
├─ 自定义 Actor：用 JavaScript/Python 编写自定义爬虫
├─ MCP 集成：Apify MCP Server
├─ 代理池：自动轮换 IP，绕过反爬
├─ 调度：定时运行爬虫任务
├─ 存储：内置数据集和 Key-Value 存储
└─ 企业级：SLA、合规、大规模并发
```

```python
from apify_client import ApifyClient

client = ApifyClient("apify_api_xxx")

# ─── 使用预构建 Actor: 网页内容抓取 ───
run = client.actor("apify/website-content-crawler").call(
    run_input={
        "startUrls": [{"url": "https://docs.example.com"}],
        "maxCrawlPages": 50,
        "crawlerType": "cheerio",  # cheerio（快）| playwright（JS 渲染）
    }
)

# 获取结果
dataset = client.dataset(run["defaultDatasetId"])
for item in dataset.iterate_items():
    print(f"URL: {item['url']}")
    print(f"标题: {item['metadata']['title']}")
    print(f"内容: {item['text'][:300]}...")

# ─── 使用 Google Search Actor ───
run = client.actor("apify/google-search-scraper").call(
    run_input={
        "queries": "AI Agent 开发教程",
        "maxPagesPerQuery": 1,
        "languageCode": "zh-CN",
    }
)
for item in client.dataset(run["defaultDatasetId"]).iterate_items():
    print(f"标题: {item['title']}")
    print(f"URL: {item['url']}")
    print(f"描述: {item['description']}")
```

## 9. 综合对比表

| 特性 | Firecrawl | Tavily | Exa | Jina Reader | Brave Search | Serper | Apify |
|------|-----------|--------|-----|-------------|-------------|--------|-------|
| 类型 | 抓取+搜索 | AI 搜索 | 语义搜索 | 内容提取 | Web 搜索 | Google 搜索 | 抓取平台 |
| 最佳用途 | 网页→Markdown | Agent 搜索 | 研究发现 | 快速提取 | 隐私搜索 | Google 结果 | 大规模抓取 |
| MCP 支持 | ✅ | ✅ | ❌ | ❌ | ✅ | ❌ | ✅ |
| 免费额度 | 500 页/月 | 1000 次/月 | 1000 次/月 | 有 | 2000 次/月 | 2500 次/月 | 有限 |
| 自托管 | ✅ 开源 | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| GitHub Stars | 148K+ | 15K+ | 7K+ | 25K+ | N/A | N/A | 15K+ |
| JS 渲染 | ✅ | N/A | N/A | ✅ | N/A | N/A | ✅ |
| 整站爬取 | ✅ | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| 结构化提取 | ✅ LLM | ❌ | ❌ | ❌ | ❌ | ✅ | ✅ |
| LangChain | ✅ | ✅ 原生 | ✅ | ✅ | ✅ | ✅ | ✅ |
| 定价 | $19/月起 | $0（免费起） | $0（免费起） | 免费+付费 | 免费+$5/月 | $50/月起 | $49/月起 |

## 10. 选型决策指南

```
你需要什么？
│
├─ 搜索互联网信息
│   ├─ AI Agent 搜索（最佳 LLM 集成）  → Tavily
│   ├─ 隐私优先 + 免费额度大            → Brave Search
│   ├─ 语义搜索（理解意图）             → Exa
│   └─ Google 精确结果                  → Serper / SerpAPI
│
├─ 抓取网页内容
│   ├─ 单页面 → 干净 Markdown           → Firecrawl 或 Jina Reader
│   ├─ 极简使用（无需 SDK）             → Jina Reader（URL 前缀即可）
│   ├─ 整站爬取                         → Firecrawl 或 Apify
│   └─ 结构化数据提取                   → Firecrawl Extract
│
├─ 企业级大规模
│   ├─ 大量页面 + 反爬处理              → Apify
│   ├─ 定时任务 + 数据管道              → Apify
│   └─ 自托管 + 数据安全                → Firecrawl（开源）
│
├─ RAG 知识库构建
│   ├─ 文档站点爬取                     → Firecrawl Crawl
│   ├─ 搜索补充知识                     → Tavily
│   └─ 学术论文搜索                     → Exa
│
└─ 预算有限
    ├─ 完全免费                         → Jina Reader
    ├─ 慷慨免费额度                     → Brave Search (2000/月)
    └─ 开源自托管                       → Firecrawl
```

## 11. 实战：构建 RAG 数据管道

```python
"""使用 Web 数据工具构建 RAG 知识库"""

from firecrawl import FirecrawlApp
from tavily import TavilyClient
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# ─── 步骤 1: 爬取文档站点 ───
firecrawl = FirecrawlApp(api_key="fc-xxx")
docs_crawl = firecrawl.crawl_url(
    "https://docs.example.com",
    params={"limit": 100, "scrapeOptions": {"formats": ["markdown"]}}
)

# ─── 步骤 2: 搜索补充信息 ───
tavily = TavilyClient(api_key="tvly-xxx")
search_results = tavily.search(
    query="example.com API 最佳实践",
    search_depth="advanced",
    max_results=10,
    include_raw_content=True,
)

# ─── 步骤 3: 合并所有内容 ───
all_texts = []
for page in docs_crawl.data:
    all_texts.append(page["markdown"])
for result in search_results["results"]:
    if result.get("raw_content"):
        all_texts.append(result["raw_content"])

# ─── 步骤 4: 分块 + 向量化 ───
splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
)
chunks = splitter.create_documents(all_texts)

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    persist_directory="./chroma_db",
)
print(f"✅ 知识库构建完成，共 {len(chunks)} 个文档块")
```

## 12. 相关文档

<!-- 修复于 2026-07-10: 补全文件名中缺失的编号前缀，与实际目录文件名一致 -->
- Agent 工具生态 → `01-Agent工具生态总览.md`（本目录）
- Composio 平台 → `02-Composio工具平台.md`（本目录，统一工具管理）
- E2B 沙箱 → `03-E2B代码沙箱.md`（本目录，代码执行环境）
- RAG 架构 → `../06-RAG进阶/01-RAG架构与核心流程.md`
- MCP Server → `../07-工具与Function Calling/02-MCP Server开发.md`
- 向量数据库 → `../06-RAG进阶/02-向量数据库选型.md`
## 🎬 推荐视频资源

### 🌐 YouTube
- [Firecrawl - Web Scraping for AI](https://www.youtube.com/watch?v=dcgRMOG605w) — Firecrawl网页抓取
- [Tavily - AI Search API](https://www.youtube.com/watch?v=Ox9DBiJMnHY) — Tavily搜索API

### 📖 官方文档
- [Firecrawl Docs](https://docs.firecrawl.dev/) — Firecrawl文档
- [Tavily Docs](https://docs.tavily.com/) — Tavily文档
- [Jina Reader](https://jina.ai/reader/) — Jina Reader API
