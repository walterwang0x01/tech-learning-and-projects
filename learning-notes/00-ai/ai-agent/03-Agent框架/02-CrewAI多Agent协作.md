# CrewAI 多 Agent 协作
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

> 🔄 更新于 2026-04-16

<!-- version-check: CrewAI v1.14.5a4 (alpha), v1.14.2 stable, 38K+ Stars, checked 2026-05-21 -->
CrewAI 是一个角色化多 Agent 协作框架，核心理念是将 AI Agent 组织为一个"团队"（Crew），每个 Agent 扮演特定角色，协作完成复杂任务。GitHub 38K+ Stars，2700 万+ PyPI 下载量，20 亿+ Agent 执行次数。最新稳定版 v1.14.2（checkpoint resume/fork/prune、token tracking 增强），alpha v1.14.5a4（2026-05-09，依赖修复、LLM listings 更新）。已完全独立于 LangChain，从零构建。支持 A2A 协议（含企业版）和 MCP 工具集成（含 Streamable HTTP Transport）、Flows 事件驱动编排。crewAI-examples 仓库已于 2026-04-20 归档，示例代码迁移至主仓库。来源：[CrewAI Changelog](https://docs.crewai.com/en/changelog)、[GitHub](https://github.com/crewAIInc/crewAI)

## 2. 核心概念

```python
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool

# 1. 定义工具
@tool
def search_web(query: str) -> str:
    """搜索互联网获取最新信息"""
    return search_engine.search(query)

@tool
def write_file(filename: str, content: str) -> str:
    """将内容写入文件"""
    Path(filename).write_text(content)
    return f"已写入 {filename}"

# 2. 定义 Agent（角色）
<!-- version-check: gpt-5.2, checked 2026-04-16 -->
researcher = Agent(
    role="高级研究员",
    goal="深入研究给定主题，收集全面准确的信息",
    backstory="你是一位经验丰富的研究员，擅长从多个来源收集和分析信息",
    tools=[search_web],
    llm="gpt-5.2",
    verbose=True,
)

writer = Agent(
    role="技术作家",
    goal="将研究成果转化为高质量的技术文章",
    backstory="你是一位专业的技术作家，擅长将复杂概念用通俗易懂的方式表达",
    tools=[write_file],
    llm="gpt-5.2",
)

reviewer = Agent(
    role="内容审核员",
    goal="审核文章质量，确保准确性和可读性",
    backstory="你是一位严格的编辑，对内容质量有极高的要求",
    llm="gpt-5.2",
)

# 3. 定义任务
research_task = Task(
    description="研究 {topic} 的最新发展趋势和关键技术",
    expected_output="一份详细的研究报告，包含关键发现和数据",
    agent=researcher,
)

writing_task = Task(
    description="基于研究报告撰写一篇技术博客文章",
    expected_output="一篇 2000 字左右的技术文章，结构清晰",
    agent=writer,
    context=[research_task],  # 依赖研究任务的输出
)

review_task = Task(
    description="审核文章，提出修改建议",
    expected_output="审核意见和最终版本",
    agent=reviewer,
    context=[writing_task],
)

# 4. 组建团队
crew = Crew(
    agents=[researcher, writer, reviewer],
    tasks=[research_task, writing_task, review_task],
    process=Process.sequential,  # 顺序执行
    verbose=True,
)

# 5. 执行
result = crew.kickoff(inputs={"topic": "AI Agent 协议标准化"})
print(result)
```

## 3. 执行流程

```python
# 顺序执行
process=Process.sequential  # 任务按顺序执行

# 层级执行（Manager Agent 分配任务）
process=Process.hierarchical
manager_llm="gpt-5.2"  # Manager 使用的模型
```

## 4. MCP 集成

```python
from crewai import Agent
from crewai.tools import MCPServerAdapter

# 连接 MCP Server
mcp_tools = MCPServerAdapter(
    server_params={
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "env": {"GITHUB_TOKEN": "ghp_xxx"},
    }
)

# Agent 使用 MCP 工具
developer = Agent(
    role="开发者",
    goal="管理 GitHub 仓库",
    tools=mcp_tools.tools,  # 自动发现 MCP Server 提供的工具
)
```

## 5. Memory 系统

```python
crew = Crew(
    agents=[...],
    tasks=[...],
    memory=True,  # 启用记忆
    # 短期记忆：当前执行上下文
    # 长期记忆：跨执行的经验
    # 实体记忆：关键实体信息
)
```

## 6. 框架对比

| 特性 | CrewAI | LangGraph | OpenAI SDK |
|------|--------|-----------|------------|
| 核心理念 | 角色协作 | 图工作流 | 快速原型 |
| 多 Agent | 原生支持 | 需手动编排 | Handoff 模式 |
| 学习曲线 | 低 | 中高 | 低 |
| 模型锁定 | 无 | 无 | OpenAI 为主 |
| MCP 支持 | 原生 | 通过工具 | 通过工具 |
| 适用场景 | 团队协作 | 复杂工作流 | GPT 快速原型 |
> 🔄 更新于 2026-04-23

## 7. CrewAI v1.14.2 版本演进

<!-- version-check: CrewAI v1.14.2 stable, v1.14.3a3 alpha, checked 2026-04-23 -->

CrewAI 从 v1.10.1（2026-03）快速迭代到 v1.14.2（2026-04），引入了 checkpoint 系统和企业级 A2A 支持。来源：[CrewAI Changelog](https://docs.crewai.com/en/changelog)

### v1.14.2 核心新特性

```
Checkpoint 系统（v1.14.2）：
├─ checkpoint resume — 从断点恢复执行
├─ checkpoint fork — 分叉执行路径（带 lineage 追踪）
├─ checkpoint prune — 清理旧检查点
├─ checkpoint diff — 对比检查点差异
├─ TUI 树形视图 — 可视化检查点树
└─ from_checkpoint 参数 — Agent.kickoff() 支持从检查点启动

Token 追踪增强（v1.14.2）：
├─ reasoning tokens — 推理 Token 计数
├─ cache creation tokens — 缓存创建 Token 计数
└─ 更精细的成本分析

企业级 A2A（v1.14.2）：
├─ 企业 A2A 功能文档
└─ OSS A2A 文档更新
```

### v1.14.3a3 预览特性

```
新增能力：
├─ E2B 沙箱集成 — Agent 在安全沙箱中执行代码
├─ Bedrock V4 支持 — AWS Bedrock 最新版本
├─ Daytona 沙箱工具 — 增强的沙箱功能
├─ 冷启动优化 — MCP SDK 和事件类型懒加载，~29% 提速
└─ "Build with AI" 文档页 — AI 原生文档，面向 Coding Agent
```

### 版本选择建议

| 场景 | 推荐版本 |
|------|---------|
| 生产环境 | v1.14.2（稳定版，checkpoint 支持） |
| 需要沙箱执行 | v1.14.3a3（alpha，E2B 集成） |
| 简单多 Agent 协作 | v1.14.2（无需 alpha 特性） |

## 🎬 推荐视频资源

- [DeepLearning.AI - Multi AI Agent Systems with crewAI](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/) — 吴恩达出品多Agent系统（免费）
- [CrewAI Official - Getting Started](https://www.youtube.com/watch?v=sPzc6hMg7So) — CrewAI官方入门
- [Matt Williams - CrewAI Tutorial](https://www.youtube.com/watch?v=tnejrr-0a94) — CrewAI完整教程
### 📺 B站（Bilibili）
- [CrewAI多Agent实战教程](https://www.bilibili.com/video/BV1Bm421N7BH) — CrewAI中文实战

### 🎓 DeepLearning.AI（免费）
- [Multi AI Agent Systems with crewAI](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/) — 多Agent系统实战
