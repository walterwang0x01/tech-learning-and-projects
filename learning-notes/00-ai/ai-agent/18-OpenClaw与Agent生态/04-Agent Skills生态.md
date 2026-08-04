# Agent Skills 生态
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 什么是 Agent Skills

Agent Skills 是模块化的能力扩展单元，让 Agent 获得特定领域的知识和工具调用能力。不同框架对 Skills 的实现方式各异，但核心理念一致：即插即用、可组合、可复用。

```
┌─────────────── Agent Skills 生态 ───────────────┐
│                                                   │
│  ┌─────────┐  ┌─────────┐  ┌─────────────────┐  │
│  │ Skills  │  │  Tools  │  │    Plugins      │  │
│  │ 行为+工具│  │ 纯函数   │  │  工具集合+配置   │  │
│  │ 指令+规则│  │ 无状态   │  │  有生命周期     │  │
│  └─────────┘  └─────────┘  └─────────────────┘  │
│       ↕             ↕              ↕              │
│  ┌───────────────────────────────────────────┐   │
│  │        MCP — 统一工具协议层                  │   │
│  └───────────────────────────────────────────┘   │
└──────────────────────────────────────────────────┘
```

## 2. Skills vs Tools vs Plugins

| 维度 | Skills | Tools | Plugins |
|------|--------|-------|---------|
| 定义 | 行为指令 + 工具 + 规则 | 单个可调用函数 | 工具集合 + 配置 |
| 粒度 | 粗（领域能力） | 细（单一操作） | 中（功能模块） |
| 包含内容 | 指令、工具、记忆、规则 | 函数签名 + 实现 | 多个工具 + 元数据 |
| 状态 | 可有状态 | 通常无状态 | 可有状态 |
| 示例 | "日程管理助手" | `create_event()` | CalendarPlugin |
| 代表框架 | OpenClaw | LangChain | Semantic Kernel |

## 3. OpenClaw Skills

基于 Markdown 的 Skill 定义，人类可读，易于编写和分享。

```markdown
# skills/research-assistant/skill.md

## Identity
You are a research assistant specialized in academic papers.

## Capabilities
- Search academic databases (arXiv, Google Scholar)
- Summarize papers and extract key findings
- Compare multiple papers on the same topic
- Generate literature review outlines

## Tools Required
- web_search: Search the web for papers
- pdf_reader: Extract text from PDF files
- note_taker: Save research notes

## Workflow
1. Understand the research topic from user
2. Search for relevant papers
3. Read and summarize top results
4. Present findings with citations

## Rules
- Always cite sources with paper title and authors
- Distinguish between peer-reviewed and preprint papers
- Flag potential biases in studies
```

```bash
# 安装和管理 Skills
openclaw skill install research-assistant
openclaw skill list
openclaw skill update research-assistant
openclaw skill remove research-assistant
```

## 4. Semantic Kernel Plugins

```python
from microsoft.agents import plugin, skill

@plugin
class MathPlugin:
    """数学计算插件"""

    @skill
    def calculate(self, expression: str) -> str:
        """计算数学表达式"""
        return str(eval(expression))  # 简化示例

    @skill
    def unit_convert(self, value: float, from_unit: str, to_unit: str) -> str:
        """单位转换"""
        conversions = {"km_to_mile": 0.621371, "kg_to_lb": 2.20462}
        key = f"{from_unit}_to_{to_unit}"
        result = value * conversions.get(key, 1)
        return f"{value} {from_unit} = {result:.2f} {to_unit}"
```

## 5. LangChain Tools 生态

```python
from langchain_community.tools import (
    WikipediaQueryRun,
    ArxivQueryRun,
    DuckDuckGoSearchRun,
    ShellTool,
)
from langchain.tools import tool

# 社区工具
wiki = WikipediaQueryRun()
arxiv = ArxivQueryRun()
search = DuckDuckGoSearchRun()

# 自定义工具
@tool
def query_database(sql: str) -> str:
    """执行 SQL 查询"""
    return db.execute(sql)

# LangChain 工具生态
# ├─ 搜索：Google, Bing, DuckDuckGo, Tavily
# ├─ 知识：Wikipedia, Arxiv, PubMed
# ├─ 代码：Python REPL, Shell
# ├─ 数据：SQL, Pandas, CSV
# ├─ API：Requests, OpenAPI
# └─ 文件：File System, PDF, Office
```

## 6. MCP 作为统一 Skill 协议

```
MCP 的统一价值：
┌─────────────────────────────────────────┐
│  任何框架的 Agent                         │
│  (LangChain / CrewAI / ADK / OpenClaw)  │
│              ↕ MCP 协议                   │
│  ┌─────┐ ┌─────┐ ┌─────┐ ┌──────────┐ │
│  │GitHub│ │Slack│ │ DB  │ │ 自定义    │ │
│  │Server│ │Server│ │Server│ │ Server  │ │
│  └─────┘ └─────┘ └─────┘ └──────────┘ │
└─────────────────────────────────────────┘
```

```python
# MCP Server 即 Skill
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("project-management")

@mcp.tool()
def create_task(title: str, assignee: str, priority: str = "medium") -> dict:
    """创建项目任务"""
    return {"id": "TASK-001", "title": title, "assignee": assignee}

@mcp.tool()
def list_tasks(status: str = "open") -> list:
    """列出任务"""
    return [{"id": "TASK-001", "title": "示例任务", "status": status}]

@mcp.resource("project://status")
def project_status() -> str:
    """项目状态概览"""
    return "进行中: 5 个任务, 已完成: 12 个任务"
```

## 7. 构建自定义 Skill 最佳实践

```
设计原则：
├─ 单一职责：一个 Skill 解决一个领域问题
├─ 明确边界：清晰定义 Skill 能做什么、不能做什么
├─ 工具最小化：只暴露必要的工具，避免过度授权
├─ 错误友好：工具返回清晰的错误信息
├─ 文档完整：每个工具有准确的描述和参数说明
└─ 可测试：Skill 的每个工具可独立测试

目录结构：
my-skill/
├── skill.md          # Skill 指令和规则
├── skill.yaml        # 配置和元数据
├── tools/            # 工具实现
│   ├── __init__.py
│   └── handlers.py
├── tests/            # 测试
│   └── test_tools.py
└── README.md         # 使用文档
```

## 8. Skills 市场与发现

| 市场 | 类型 | 数量 | 特点 |
|------|------|------|------|
| ClawHub | OpenClaw Skills | 100+ | Markdown 定义，社区驱动 |
| SkillHub | 企业技能注册 | 自托管 | ★ 讯飞开源，私有部署，RBAC+审计 |
| MCP Server 目录 | MCP 工具 | 1000+ | 协议标准化，跨框架 |
| LangChain Hub | Chains/Tools | 500+ | Python 生态，成熟 |
| Copilot Extensions | GitHub 插件 | 100+ | GitHub 生态集成 |
| Coze 插件商店 | Bot 插件 | 200+ | 低代码，中文生态 |
| Dify 工具市场 | 工作流工具 | 100+ | 可视化集成 |
## 🎬 推荐视频资源

### 🌐 YouTube
- [Composio - Agent Tools Platform](https://www.youtube.com/watch?v=nMGCE4GU1kc) — Composio工具平台介绍

### 📖 官方文档
- [Composio Docs](https://docs.composio.dev/) — Composio官方文档
