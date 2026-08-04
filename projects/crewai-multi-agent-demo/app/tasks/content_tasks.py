"""内容创作流水线 — 任务定义"""

from crewai import Agent, Task


def create_research_task(agent: Agent, topic: str) -> Task:
    """创建研究任务

__author__ = "Walter Wang"

    研究员 Agent 针对给定主题进行全面调研，
    输出结构化的研究报告供后续写作使用。
    """
    return Task(
        description=(
            f"针对主题「{topic}」进行全面深入的调研。\n\n"
            "要求：\n"
            "1. 搜索该主题的最新技术动态和发展趋势\n"
            "2. 收集至少 3-5 个权威来源的关键信息\n"
            "3. 整理核心概念、技术原理和实际应用场景\n"
            "4. 标注信息来源以便后续引用\n\n"
            "输出格式：结构化的研究报告，包含要点摘要、详细分析和参考来源。"
        ),
        expected_output="一份结构化的研究报告，包含主题概述、核心要点、技术细节、应用场景和参考来源",
        agent=agent,
    )


def create_writing_task(agent: Agent, topic: str, context: list[Task]) -> Task:
    """创建写作任务

    技术作家 Agent 基于研究成果撰写技术博客文章，
    通过 context 参数接收研究任务的输出。
    """
    return Task(
        description=(
            f"基于研究成果，撰写一篇关于「{topic}」的高质量技术博客文章。\n\n"
            "要求：\n"
            "1. 文章字数 1500-3000 字\n"
            "2. 包含引言、正文（分 3-5 个章节）和总结\n"
            "3. 适当使用代码示例或技术图表辅助说明\n"
            "4. 语言通俗易懂，兼顾技术深度\n"
            "5. 使用 Markdown 格式\n\n"
            "输出格式：完整的 Markdown 格式技术博客文章。"
        ),
        expected_output="一篇完整的 Markdown 格式技术博客文章，包含标题、引言、分章节正文和总结",
        agent=agent,
        context=context,
    )


def create_editing_task(agent: Agent, context: list[Task]) -> Task:
    """创建编辑任务

    内容编辑 Agent 审校文章质量，
    通过 context 参数接收写作任务的输出。
    """
    return Task(
        description=(
            "审校并优化技术博客文章。\n\n"
            "审校要点：\n"
            "1. 检查文章逻辑结构是否清晰连贯\n"
            "2. 验证技术术语和概念的准确性\n"
            "3. 优化语言表达，消除冗余和歧义\n"
            "4. 确保段落衔接自然，阅读体验流畅\n"
            "5. 检查 Markdown 格式是否规范\n\n"
            "输出格式：修改后的完整文章，附带修改说明。"
        ),
        expected_output="经过审校优化的完整文章（Markdown 格式），以及简要的修改说明",
        agent=agent,
        context=context,
    )


def create_seo_task(agent: Agent, topic: str, context: list[Task]) -> Task:
    """创建 SEO 优化任务

    SEO 优化师 Agent 对文章进行搜索引擎优化，
    通过 context 参数接收编辑任务的输出。
    """
    return Task(
        description=(
            f"对关于「{topic}」的技术博客文章进行 SEO 优化。\n\n"
            "优化要点：\n"
            "1. 优化文章标题（包含核心关键词，吸引点击）\n"
            "2. 生成 SEO 友好的 meta description（150-160 字符）\n"
            "3. 合理布局关键词（标题、副标题、正文首段）\n"
            "4. 优化内部链接结构和标题层级\n"
            "5. 添加适当的 alt 文本建议\n\n"
            "输出格式：优化后的完整文章，附带 SEO 元数据（标题、描述、关键词列表）。"
        ),
        expected_output=(
            "SEO 优化后的完整文章（Markdown 格式），"
            "以及 SEO 元数据：优化标题、meta description、目标关键词列表"
        ),
        agent=agent,
        context=context,
    )
