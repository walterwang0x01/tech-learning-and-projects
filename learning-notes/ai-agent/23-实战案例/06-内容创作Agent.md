# 内容创作 Agent
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 系统架构

```
┌─────────────────────────────────────────────────────┐
│                 内容创作 Agent                        │
├──────────┬──────────┬──────────┬───────────────────┤
│ 选题调研  │ 内容撰写  │ 编辑优化  │ SEO 优化          │
├──────────┼──────────┼──────────┼───────────────────┤
│ 热点分析  │ 大纲生成  │ 语法检查  │ 关键词优化        │
│ 竞品调研  │ 分段写作  │ 风格统一  │ 元数据生成        │
│ 素材收集  │ 配图建议  │ 事实核查  │ 发布排期          │
└──────────┴──────────┴──────────┴───────────────────┘
         ↕ 质量评估循环（评分 < 8 则重写）↕
```

## 2. CrewAI 多 Agent 实现

```python
from crewai import Agent, Task, Crew, Process
from crewai.tools import tool
from langchain_community.tools import TavilySearchResults

# 工具定义
search_tool = TavilySearchResults(max_results=5)

@tool
def analyze_seo(keyword: str) -> str:
    """分析关键词的 SEO 竞争度和搜索量"""
    return f"""关键词分析：{keyword}
- 月搜索量：约 12,000
- 竞争度：中等
- 相关长尾词：{keyword} 教程, {keyword} 最佳实践, {keyword} 入门指南
- 建议标题包含关键词，H2 使用相关长尾词"""

@tool
def check_facts(claims: str) -> str:
    """核查文章中的事实性声明"""
    return f"事实核查结果：所有声明基本准确，建议补充数据来源引用。"
```

## 3. Agent 角色定义

```python
# 研究员 Agent
researcher = Agent(
    role="资深内容研究员",
    goal="深入调研主题，收集高质量素材和数据",
    backstory="""你是经验丰富的内容研究员，擅长从多个来源收集信息，
    识别热点趋势，提供有数据支撑的调研报告。""",
    tools=[search_tool],
    llm="gpt-5.2",
    verbose=True,
)

# 作者 Agent
writer = Agent(
    role="技术内容作者",
    goal="撰写高质量、有深度的技术文章",
    backstory="""你是资深技术作者，文风清晰简洁，善于用通俗语言解释复杂概念。
    你的文章结构清晰，代码示例实用，读者反馈一直很好。""",
    llm="gpt-5.2",
    verbose=True,
)

# 编辑 Agent
editor = Agent(
    role="内容编辑",
    goal="确保文章质量、准确性和可读性",
    backstory="""你是严格的内容编辑，关注语法、逻辑、事实准确性。
    你会检查文章结构、论证逻辑、数据引用，确保发布质量。""",
    tools=[check_facts],
    llm="gpt-5.2",
    verbose=True,
)

# SEO 优化 Agent
seo_optimizer = Agent(
    role="SEO 优化专家",
    goal="优化文章的搜索引擎排名",
    backstory="""你是 SEO 专家，了解搜索引擎算法，
    能优化标题、元描述、关键词密度、内链外链策略。""",
    tools=[analyze_seo],
    llm="gpt-5.2",
    verbose=True,
)
```

## 4. 任务定义

```python
# 任务1：选题调研
research_task = Task(
    description="""调研主题：{topic}

    要求：
    1. 搜索该主题的最新信息和趋势
    2. 收集 3-5 个关键数据点
    3. 分析竞品文章的角度和不足
    4. 提供独特的写作角度建议

    输出：结构化调研报告""",
    agent=researcher,
    expected_output="包含数据、趋势、竞品分析的调研报告",
)

# 任务2：撰写文章
writing_task = Task(
    description="""基于调研报告撰写技术文章。

    要求：
    1. 标题吸引人，包含核心关键词
    2. 开头用 hook 吸引读者
    3. 正文分 3-5 个主要章节
    4. 包含代码示例（如适用）
    5. 结尾有总结和行动建议
    6. 全文 1500-2500 字

    输出：完整的 Markdown 格式文章""",
    agent=writer,
    expected_output="Markdown 格式的完整文章",
    context=[research_task],  # 依赖调研结果
)

# 任务3：编辑审查
editing_task = Task(
    description="""审查和编辑文章。

    检查项：
    1. 语法和拼写错误
    2. 逻辑连贯性
    3. 事实准确性（使用 fact-check 工具）
    4. 代码示例正确性
    5. 可读性和流畅度

    输出：修改后的文章 + 修改说明""",
    agent=editor,
    expected_output="编辑后的文章和修改说明",
    context=[writing_task],
)

# 任务4：SEO 优化
seo_task = Task(
    description="""对文章进行 SEO 优化。

    优化项：
    1. 标题优化（包含关键词，60字符内）
    2. 元描述（155字符内，包含关键词）
    3. H2/H3 标题优化
    4. 关键词密度检查（1-2%）
    5. 内链建议
    6. 图片 alt 文本建议

    输出：SEO 优化后的最终文章 + 元数据""",
    agent=seo_optimizer,
    expected_output="SEO 优化后的文章和元数据",
    context=[editing_task],
)
```

## 5. 组装 Crew 并运行

```python
# 创建 Crew
content_crew = Crew(
    agents=[researcher, writer, editor, seo_optimizer],
    tasks=[research_task, writing_task, editing_task, seo_task],
    process=Process.sequential,  # 顺序执行
    verbose=True,
)

# 运行
result = content_crew.kickoff(inputs={
    "topic": "2025年 AI Agent 开发入门指南"
})

print(result.raw)
```

## 6. 质量评估循环

```python
from crewai import Agent, Task, Crew

# 评估 Agent
evaluator = Agent(
    role="内容质量评估师",
    goal="严格评估文章质量",
    backstory="你是内容质量专家，评分标准严格但公正。",
    llm="gpt-5.2",
)

def content_pipeline_with_eval(topic: str, max_iterations: int = 3) -> str:
    """带质量评估循环的内容创作"""

    for iteration in range(max_iterations):
        # 创作流程
        crew = Crew(
            agents=[researcher, writer, editor],
            tasks=[research_task, writing_task, editing_task],
            process=Process.sequential,
        )
        article = crew.kickoff(inputs={"topic": topic}).raw

        # 质量评估
        eval_task = Task(
            description=f"""评估文章质量（1-10分），输出 JSON：
{{"score": 分数, "issues": ["问题1", "问题2"], "suggestions": ["建议1"]}}

文章：
{article[:3000]}""",
            agent=evaluator,
            expected_output="JSON 格式的评估结果",
        )
        eval_crew = Crew(agents=[evaluator], tasks=[eval_task])
        eval_result = eval_crew.kickoff()

        import json
        try:
            evaluation = json.loads(eval_result.raw)
            if evaluation["score"] >= 8:
                print(f"✅ 第 {iteration+1} 轮通过，得分：{evaluation['score']}")
                return article
            print(f"⚠️ 第 {iteration+1} 轮得分：{evaluation['score']}，继续优化")
        except json.JSONDecodeError:
            return article

    return article
```

## 7. 发布集成

```python
from composio_crewai import ComposioToolSet, Action

toolset = ComposioToolSet()

# 获取发布工具
publish_tools = toolset.get_tools(actions=[
    Action.NOTION_CREATE_PAGE,      # 发布到 Notion
    Action.SLACK_SEND_MESSAGE,      # 通知团队
])

publisher = Agent(
    role="内容发布专员",
    goal="将文章发布到指定平台",
    tools=publish_tools,
    llm="gpt-5.2",
)

publish_task = Task(
    description="""将 SEO 优化后的文章发布：
    1. 发布到 Notion 内容库
    2. 在 Slack #content 频道通知团队
    3. 记录发布时间和链接""",
    agent=publisher,
    context=[seo_task],
    expected_output="发布确认和链接",
)
```

## 8. 完整流程图

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ 研究员    │───→│ 作者     │───→│ 编辑     │───→│ SEO优化  │
│ 选题调研  │    │ 撰写文章  │    │ 审查修改  │    │ 关键词   │
└──────────┘    └──────────┘    └──────────┘    └────┬─────┘
                                                      │
                                                      ↓
                                                ┌──────────┐
                                                │ 质量评估  │
                                                │ 分数≥8？  │
                                                └────┬─────┘
                                              YES │    │ NO
                                                  ↓    ↓
                                            ┌──────┐ 返回作者
                                            │ 发布  │ 重写
                                            └──────┘
```
## 🎬 推荐视频资源

### 🌐 YouTube
- [DeepLearning.AI - Multi AI Agent Systems with crewAI](https://www.deeplearning.ai/short-courses/multi-ai-agent-systems-with-crewai/) — 多Agent内容创作（免费）
- [CrewAI - Content Creation Crew](https://www.youtube.com/watch?v=sPzc6hMg7So) — CrewAI内容创作实战

## 9. 2026 年 Agentic Marketing 与内容创作趋势

> 🔄 更新于 2026-05-04

<!-- version-check: Agentic Marketing 2026, CrewAI content creation, multi-agent content orchestration -->

### 9.1 从内容创作到 Agentic Marketing

2026 年，内容创作 Agent 从独立工具演进为 Agentic Marketing 系统的核心组件。Gartner 预测 2026 年底 40% 企业应用将嵌入 Agent，McKinsey 报告指出营销工作流正在被 Agent 重塑。

**关键数据**：
- CrewAI 2026 State of Agentic AI 调查：100% 受访企业计划扩大 Agent 使用，73% 视为关键优先级。来源：[CrewAI Survey](https://crewai.com/ai-agent-survey)
- 多 Agent 营销系统可降低运营成本 37%，同时维持或提升产出质量。来源：[Alex Genovese](https://alexgenovese.com/multi-agent-ai-systems-for-marketing-teams-a-practical-guide-to-crewai-in-2026/)
- Netcore 报告：2026 年营销从"Campaign 驱动"转向"Agent 驱动"。来源：[PR Newswire](https://www.prnewswire.com/in/news-releases/netcore-agentic-predictions-2026-report-why-marketing-in-2026-will-be-run-by-agents-not-campaigns-302680136.html)

### 9.2 多 Agent 内容编排架构（2026）

```
┌─────────────────────────────────────────────────────────┐
│              Agentic Content Orchestration               │
├──────────┬──────────┬──────────┬──────────┬────────────┤
│ 策略Agent │ 创作Agent │ SEO Agent │ 分发Agent │ 分析Agent  │
├──────────┼──────────┼──────────┼──────────┼────────────┤
│ 受众分析  │ 多格式生成│ AEO 优化  │ 多渠道发布│ 效果归因   │
│ 竞品监控  │ 品牌一致性│ 结构化数据│ 排期管理  │ 实时优化   │
│ 选题规划  │ 事实核查  │ 内链策略  │ A/B 测试  │ ROI 追踪   │
└──────────┴──────────┴──────────┴──────────┴────────────┘
         ↕ MCP 工具层（CMS + Analytics + Social API）↕
```

### 9.3 核心趋势

1. **从 SEO 到 AEO（Answer Engine Optimization）**：BCG 报告指出，AI Agent 正在改变消费者发现和评估产品的方式，品牌需要同时优化搜索引擎和 AI Agent 的可发现性。来源：[BCG](https://www.bcg.com/publications/2026/agentic-scenarios-every-marketer-must-prepare-for)
2. **多 Agent 系统覆盖完整营销生命周期**：不再是单个内容创作 Agent，而是策略→创作→优化→分发→分析的完整 Agent 编排。CrewAI + NVIDIA NemoClaw 支持自进化 Agent。来源：[CrewAI Blog](https://crewai.com/blog/orchestrating-self-evolving-agents-with-crewai-and-nvidia-nemoclaw)
3. **品牌一致性成为核心挑战**：Adobe 2026 报告强调 AI 生成内容必须"感觉像人类且符合品牌调性"，这需要 Agent 具备品牌知识库和风格约束。来源：[Adobe](https://business.adobe.com/blog/2026-adobe-ai-digital-trends-report-four-key-takeaways)
4. **实时个性化内容生成**：Agent 根据用户画像、行为数据和上下文实时生成个性化内容变体，而非预先创建固定内容。来源：[McKinsey](https://www.mckinsey.com/capabilities/growth-marketing-and-sales/our-insights/reinventing-marketing-workflows-with-agentic-ai)
5. **内容创作 Agent 框架选型（2026）**：CrewAI 仍是多 Agent 内容创作的首选（~35 行代码最小 Agent），Google Gemini API 原生支持 CrewAI 集成。来源：[Google AI](https://ai.google.dev/gemini-api/docs/crewai-example)
