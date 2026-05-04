# 研究助手 Agent
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 系统架构

```
┌─────────────────────────────────────────────────────┐
│                 研究助手 Agent                        │
├──────────┬──────────┬──────────┬───────────────────┤
│ 文献搜索  │ 论文分析  │ 知识整合  │ 报告生成          │
├──────────┼──────────┼──────────┼───────────────────┤
│ Arxiv    │ PDF 解析  │ 交叉引用  │ Markdown 输出     │
│ Scholar  │ 摘要提取  │ 主题聚类  │ 结构化报告        │
│ Web 搜索 │ 方法分析  │ 趋势分析  │ 参考文献          │
└──────────┴──────────┴──────────┴───────────────────┘
         ↕ 记忆层（研究上下文持久化）↕
```

## 2. 工具定义

```python
from langchain_core.tools import tool
import arxiv
import requests

@tool
def search_arxiv(query: str, max_results: int = 5) -> str:
    """搜索 Arxiv 论文"""
    client = arxiv.Client()
    search = arxiv.Search(query=query, max_results=max_results, sort_by=arxiv.SortCriterion.Relevance)
    results = []
    for paper in client.results(search):
        results.append({
            "title": paper.title,
            "authors": [a.name for a in paper.authors[:3]],
            "summary": paper.summary[:300],
            "url": paper.entry_id,
            "published": paper.published.strftime("%Y-%m-%d"),
        })
    import json
    return json.dumps(results, ensure_ascii=False, indent=2)

@tool
def search_web(query: str) -> str:
    """使用 Tavily 搜索互联网"""
    from tavily import TavilyClient
    client = TavilyClient()
    result = client.search(query, search_depth="advanced", max_results=5)
    return "\n".join(f"- {r['title']}: {r['content'][:200]}" for r in result["results"])

@tool
def read_webpage(url: str) -> str:
    """读取网页内容"""
    response = requests.get(f"https://r.jina.ai/{url}")
    return response.text[:5000]

@tool
def analyze_pdf(pdf_url: str) -> str:
    """下载并分析 PDF 论文"""
    response = requests.get(pdf_url)
    from io import BytesIO
    from pypdf import PdfReader
    reader = PdfReader(BytesIO(response.content))
    text = "\n".join(page.extract_text() for page in reader.pages[:10])
    return text[:8000]
```

## 3. LangGraph 研究工作流

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated
from operator import add

class ResearchState(TypedDict):
    topic: str
    messages: Annotated[list, add]
    papers: list[dict]
    web_findings: list[str]
    analysis: str
    report: str

llm = ChatOpenAI(model="gpt-4o")

# 节点1：文献搜索
async def search_literature(state: ResearchState) -> dict:
    agent = create_react_agent(llm, tools=[search_arxiv, search_web])
    result = await agent.ainvoke({
        "messages": [("user", f"搜索关于 '{state['topic']}' 的最新论文和资料，至少找5篇")]
    })
    last_msg = result["messages"][-1].content
    return {"messages": [("assistant", f"文献搜索完成：{last_msg}")]}

# 节点2：深度分析
async def deep_analysis(state: ResearchState) -> dict:
    agent = create_react_agent(llm, tools=[analyze_pdf, read_webpage])
    result = await agent.ainvoke({
        "messages": [("user", f"深入分析以下研究材料，提取关键方法和发现：\n{state['messages'][-1]}")]
    })
    return {"analysis": result["messages"][-1].content}

# 节点3：报告生成
async def generate_report(state: ResearchState) -> dict:
    prompt = f"""基于以下研究分析，生成结构化研究报告：

主题：{state['topic']}
分析：{state['analysis']}

报告格式：
# 研究报告：{{主题}}
## 1. 研究背景
## 2. 关键发现
## 3. 方法对比
## 4. 趋势分析
## 5. 结论与建议
## 参考文献
"""
    response = await llm.ainvoke(prompt)
    return {"report": response.content}

# 节点4：质量检查
async def quality_check(state: ResearchState) -> str:
    response = await llm.ainvoke(
        f"评估研究报告质量(1-10)，只输出分数：\n{state['report'][:2000]}"
    )
    score = int(response.content.strip().split()[0])
    return "output" if score >= 7 else "deep_analysis"

# 构建图
graph = StateGraph(ResearchState)
graph.add_node("search", search_literature)
graph.add_node("deep_analysis", deep_analysis)
graph.add_node("generate_report", generate_report)
graph.add_node("output", lambda s: s)

graph.add_edge(START, "search")
graph.add_edge("search", "deep_analysis")
graph.add_edge("deep_analysis", "generate_report")
graph.add_conditional_edges("generate_report", quality_check)
graph.add_edge("output", END)

research_agent = graph.compile()
```

## 4. 运行研究助手

```python
import asyncio

async def run_research(topic: str) -> str:
    result = await research_agent.ainvoke({
        "topic": topic,
        "messages": [],
        "papers": [],
        "web_findings": [],
        "analysis": "",
        "report": "",
    })
    return result["report"]

report = asyncio.run(run_research("2025年大语言模型Agent的最新进展"))
print(report)
```

## 5. 研究记忆管理

```python
from mem0 import Memory

memory = Memory()

class ResearchMemory:
    """研究上下文记忆"""

    def __init__(self, project_id: str):
        self.project_id = project_id
        self.memory = Memory()

    def save_finding(self, finding: str):
        self.memory.add(finding, user_id=self.project_id, metadata={"type": "finding"})

    def save_paper(self, title: str, summary: str):
        self.memory.add(
            f"论文：{title}\n摘要：{summary}",
            user_id=self.project_id,
            metadata={"type": "paper"},
        )

    def get_context(self, query: str) -> str:
        results = self.memory.search(query, user_id=self.project_id)
        return "\n".join(f"- {r['memory']}" for r in results)

# 跨会话保持研究上下文
rm = ResearchMemory("ai-agent-research-2025")
rm.save_paper("ReAct: Synergizing Reasoning and Acting", "结合推理和行动的Agent框架...")
context = rm.get_context("Agent 推理方法")
```

## 6. 输出示例

```markdown
# 研究报告：2025年大语言模型Agent的最新进展

## 1. 研究背景
LLM Agent 在 2025 年进入生产化阶段，主要框架趋于成熟...

## 2. 关键发现
- **多Agent协作**成为主流架构模式
- **MCP协议**统一了工具集成标准
- **记忆系统**从简单缓存演进为分层架构
- **可观测性**成为生产部署的必备能力

## 3. 方法对比
| 方法 | 优势 | 局限 | 代表工作 |
|------|------|------|---------|
| ReAct | 通用性强 | 推理链长 | Yao et al. |
| Plan-Execute | 结构化 | 计划僵化 | Wang et al. |
| Reflection | 自我改进 | 成本高 | Shinn et al. |

## 4. 趋势分析
...

## 参考文献
1. [论文标题](URL) - 作者, 2025
2. ...
```
## 🎬 推荐视频资源

### 🌐 YouTube
- [LangChain - Research Assistant Agent](https://www.youtube.com/watch?v=dcgRMOG605w) — 研究助手Agent实战
- [DeepLearning.AI - Building Agentic RAG](https://www.deeplearning.ai/short-courses/building-agentic-rag-with-llamaindex/) — Agentic RAG研究助手（免费）

## 7. 2026 年 Deep Research Agent 趋势

> 🔄 更新于 2026-05-04

<!-- version-check: Deep Research Agent 2026, OpenAI Deep Research MCP, Google Deep Research Max -->

### 7.1 商业 Deep Research Agent 格局

2026 年，Deep Research 从实验性功能演进为独立产品类别。三大平台形成差异化竞争：

| 平台 | 模型 | 定位 | 核心能力 | 来源 |
|------|------|------|---------|------|
| **OpenAI Deep Research** | GPT-5.2 → GPT-5.5 | 交互式研究 | MCP 连接任意数据源、限定可信站点、实时进度追踪、中途修正 | [OpenAI](https://openai.com/index/introducing-deep-research/) |
| **Google Deep Research** | Gemini 3.1 Pro | 低延迟嵌入式 | 协作式计划、MCP Server、原生图表/信息图生成 | [Google AI](https://ai.google.dev/gemini-api/docs/deep-research) |
| **Google Deep Research Max** | Gemini 3.1 Pro（扩展推理） | 深度后台研究 | 93.3% DeepSearchQA、54.6% HLE、数百公开+私有源综合 | [Google AI](https://ai.google.dev/gemini-api/docs/models/deep-research-max-preview-04-2026) |

### 7.2 开源 Deep Research 实现

LangChain 在 2026-03 发布了 `deepagents` 模式，标准化了 Deep Research 工作流：

```python
# 2026 年推荐：使用 LangGraph Deep Agents 模式
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# Deep Research 的核心模式：
# 1. 规划阶段：分解研究问题为子查询
# 2. 搜索阶段：并行执行多源搜索（Web + 论文 + 私有数据）
# 3. 分析阶段：交叉验证、提取关键发现
# 4. 综合阶段：生成带引用的结构化报告
# 5. 质量检查：事实核查 + 覆盖度评估

# MCP 集成让研究 Agent 可以连接企业私有数据
# OpenAI Deep Research 2026-02 更新支持 MCP 连接任意数据源
# Google Deep Research API 原生支持 MCP Server
```

来源：[AI Agent Deep Research Workflow](https://fast.io/resources/ai-agent-deep-research-workflow/)

### 7.3 核心趋势

1. **MCP 成为研究数据连接标准**：OpenAI（2026-02）和 Google（2026-04）都在 Deep Research 中集成 MCP，FactSet、S&P、PitchBook 等金融数据提供商已作为 MCP Server 接入
2. **双层架构成为标准**：快速交互层（低延迟、嵌入产品流）+ 深度研究层（扩展推理、后台运行），Google 的 Deep Research / Deep Research Max 是典型实现
3. **从"搜索+总结"到"自主调查"**：2026 年的研究 Agent 能够自主分解问题、生成假设、设计搜索策略、交叉验证发现，接近人类分析师的工作模式
4. **企业级研究 Agent 兴起**：HBR 报告指出"Deep Industry Research Agents"正在改变金融、生命科学、市场情报等行业的研究工作流。来源：[HBR](https://hbr.org/2026/03/how-deep-industry-research-agents-can-change-your-organization)
5. **ChatGPT Agent 融合研究与行动**：OpenAI 发布 ChatGPT Agent（2026-04），结合 Deep Research 和 Operator 的能力，可以在研究后直接执行操作。来源：[OpenAI](https://openai.com/index/introducing-chatgpt-agent/)
