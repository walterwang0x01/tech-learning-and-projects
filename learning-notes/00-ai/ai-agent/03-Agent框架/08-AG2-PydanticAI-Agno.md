# AG2 / PydanticAI / Agno
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. AG2（原 AutoGen）

AG2 是微软 AutoGen 项目的社区分支，专注于多 Agent 对话和协作。

```python
from autogen import ConversableAgent

# 定义 Agent
assistant = ConversableAgent(
    name="assistant",
    system_message="你是一个有帮助的AI助手，擅长编程和分析。",
    llm_config={"model": "gpt-5.2", "api_key": "..."},
)

user_proxy = ConversableAgent(
    name="user_proxy",
    human_input_mode="NEVER",  # ALWAYS / TERMINATE / NEVER
    code_execution_config={"work_dir": "workspace", "use_docker": True},
    is_termination_msg=lambda msg: "TERMINATE" in msg.get("content", ""),
)

# 发起对话
result = user_proxy.initiate_chat(
    assistant,
    message="用 Python 分析 iris 数据集，画出分类散点图",
    max_turns=5,
)

# 群聊模式
from autogen import GroupChat, GroupChatManager

coder = ConversableAgent(name="coder", system_message="你是 Python 开发者")
reviewer = ConversableAgent(name="reviewer", system_message="你是代码审查员")

group_chat = GroupChat(
    agents=[user_proxy, coder, reviewer],
    messages=[],
    max_round=10,
    speaker_selection_method="auto",  # auto / round_robin / manual
)
manager = GroupChatManager(groupchat=group_chat, llm_config=llm_config)
user_proxy.initiate_chat(manager, message="开发一个 REST API")
```

## 2. PydanticAI

PydanticAI 是 Pydantic 团队推出的类型安全 Agent 框架，强调类型验证和结构化输出。

```python
from pydantic_ai import Agent
from pydantic import BaseModel

# 定义结构化输出
class CityInfo(BaseModel):
    name: str
    country: str
    population: int
    famous_for: list[str]

# 创建类型安全的 Agent
<!-- version-check: gpt-5.2, checked 2026-04-16 -->
agent = Agent(
    model="openai:gpt-5.2",
    result_type=CityInfo,  # 强制输出类型
    system_prompt="你是一个地理知识专家，提供准确的城市信息。",
)

# 同步运行
result = agent.run_sync("介绍一下东京")
print(result.data.name)        # "东京"
print(result.data.population)  # 13960000
print(result.data.famous_for)  # ["樱花", "寿司", ...]

# 带依赖注入的 Agent
from dataclasses import dataclass

@dataclass
class Deps:
    db_conn: any
    api_key: str

agent = Agent(model="openai:gpt-5.2", deps_type=Deps)

@agent.tool
async def query_database(ctx, sql: str) -> str:
    """执行数据库查询"""
    result = await ctx.deps.db_conn.execute(sql)
    return str(result)

result = await agent.run(
    "查询上月销售额",
    deps=Deps(db_conn=db, api_key="xxx"),
)
```

## 3. Agno（原 Phidata）

Agno 是一个高性能 Agent 运行时，强调速度和轻量。

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools

# 创建 Agent
agent = Agent(
    model=OpenAIChat(id="gpt-5.2"),
    tools=[DuckDuckGoTools(), YFinanceTools(stock_price=True)],
    instructions="你是一个金融分析师，用中文回答。",
    show_tool_calls=True,
    markdown=True,
)

# 运行
agent.print_response("分析苹果公司最近的股价走势", stream=True)

# 团队模式
from agno.team import Team

web_agent = Agent(name="web", tools=[DuckDuckGoTools()])
finance_agent = Agent(name="finance", tools=[YFinanceTools()])

team = Team(
    agents=[web_agent, finance_agent],
    mode="coordinate",  # coordinate / route / collaborate
    model=OpenAIChat(id="gpt-5.2"),
)
team.print_response("对比特斯拉和比亚迪的市场表现")
```

## 4. smolagents

HuggingFace 推出的极简 Agent 框架，代码量极少。

```python
from smolagents import CodeAgent, HfApiModel, tool

@tool
def get_weather(city: str) -> str:
    """获取城市天气信息"""
    return f"{city}: 25°C, 晴天"

agent = CodeAgent(
    tools=[get_weather],
    model=HfApiModel("Qwen/Qwen2.5-72B-Instruct"),
)

result = agent.run("北京今天天气怎么样？")
```

## 5. 框架对比

| 特性 | AG2 | PydanticAI | Agno | smolagents |
|------|-----|-----------|------|-----------|
| 核心理念 | 多 Agent 对话 | 类型安全 | 高性能运行时 | 极简轻量 |
| 类型验证 | 弱 | 强（Pydantic） | 中 | 弱 |
| 多 Agent | 原生群聊 | 手动编排 | Team 模式 | 有限 |
| 代码执行 | Docker 沙箱 | 无 | 无 | 原生 |
| 学习曲线 | 中 | 低 | 低 | 极低 |
| 模型支持 | 多模型 | 多模型 | 多模型 | HuggingFace |
| 适用场景 | 复杂多Agent | 生产级API | 快速开发 | 原型验证 |
> 🔄 更新于 2026-04-23

## 6. 2026 版本演进

### PydanticAI v1.0 稳定版

<!-- version-check: PydanticAI v1.0.1 (2025-09), 15.5K+ Stars, checked 2026-04-23 -->

PydanticAI 于 2025 年 9 月发布 v1.0 稳定版，承诺 API 稳定性直到 v2。15.5K+ GitHub Stars，Pydantic 验证库已达 100 亿+ 下载量。来源：[PydanticAI Changelog](https://pydantic.dev/docs/ai/project/changelog/)、[Pydantic 10B Downloads](https://pydantic.dev/articles/pydantic-validation-10-billion-downloads)

```
v1.0 核心特性：
├─ API 稳定性承诺 — 不会引入破坏性变更直到 v2
├─ MCP 客户端支持 — Agent 可连接 MCP Server 使用工具
├─ A2A 协议支持 — 声明式 Agent 定义（YAML/JSON）
├─ InstrumentationSettings v2 — 默认使用新版追踪
├─ Python 3.10+ — 不再支持 Python 3.9
└─ pydantic_evals — 安全评估框架（移除 Python evaluator）
```

### Agno v2.5.10（2026-03）

<!-- version-check: Agno v2.5.10, 400+ contributors, Apache 2.0, checked 2026-04-23 -->

Agno（原 Phidata）在 2026 年 Q1 经历了爆发式增长，从 v2.0 迭代到 v2.5.10，400+ GitHub 贡献者，许可证从 MIT 切换到 Apache 2.0。来源：[Agno Community Roundup](https://www.agno.com/blog/community-roundup-march-2026)

```
v2.5.0 里程碑（2026-02）：
├─ Team Modes — coordinate / route / collaborate 三种团队模式
├─ HITL for Teams — 团队级人机交互
└─ Apache 2.0 许可 — 从 MIT 切换

v2.5.6 ~ v2.5.10 快速迭代（2026-03）：
├─ Telegram Interface + Tools — 原生 Telegram 集成
├─ WhatsApp Interface V2 — 多媒体、交互消息、团队支持
├─ MLflow Observability — OpenInference 追踪集成
├─ Docling Reader — 多格式文档解析（PDF/DOCX/PPTX/HTML）
├─ Parallel Search for Vertex AI — 并行搜索降低延迟
├─ Built-in Followup Suggestions — followups=True 一行启用
├─ Tool Hook Message History — pre/post hook 访问消息历史
├─ GitlabTools — GitLab 集成（社区贡献）
└─ Extended Gmail/Calendar Tools — Google Workspace 完整集成
```

### 更新后的框架对比

| 特性 | AG2 | PydanticAI | Agno | smolagents |
|------|-----|-----------|------|-----------|
| 最新版本 | 0.6+ | v1.0.1 | v2.5.10 | 1.x |
| 核心理念 | 多 Agent 对话 | 类型安全 | 高性能运行时 | 极简轻量 |
| 类型验证 | 弱 | 强（Pydantic） | 中 | 弱 |
| 多 Agent | 原生群聊 | 手动编排 | Team Modes | 有限 |
| MCP 支持 | 有限 | 原生客户端 | 通过工具 | 有限 |
| A2A 支持 | 无 | 声明式 | 无 | 无 |
| 消息接口 | 无 | 无 | Telegram/WhatsApp | 无 |
| 代码执行 | Docker 沙箱 | 无 | 无 | 原生 |
| 许可证 | Apache 2.0 | MIT | Apache 2.0 | Apache 2.0 |
| 适用场景 | 复杂多Agent | 生产级API | 快速开发+部署 | 原型验证 |

## 🎬 推荐视频资源

### 🌐 YouTube
- [James Briggs - PydanticAI Tutorial](https://www.youtube.com/watch?v=nMGCE4GU1kc) — PydanticAI入门教程
- [Matt Williams - AutoGen Tutorial](https://www.youtube.com/watch?v=vU2S6dVf79M) — AG2/AutoGen教程

### 🎓 DeepLearning.AI（免费）
- [AI Agentic Design Patterns with AutoGen](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/) — AutoGen设计模式
