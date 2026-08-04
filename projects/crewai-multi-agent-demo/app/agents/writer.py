"""技术作家 Agent — 负责撰写高质量技术文章"""

from crewai import Agent

from app.tools.custom_tools import save_article, word_count


def create_writer() -> Agent:
    """创建技术作家 Agent

__author__ = "Walter Wang"

    职责：
    - 基于研究成果撰写结构清晰的技术文章
    - 确保内容准确、易读、有深度
    - 将文章保存到输出目录
    """
    return Agent(
        role="技术作家",
        goal="基于研究成果撰写高质量、结构清晰、深入浅出的技术博客文章",
        backstory=(
            "你是一位专业的技术内容创作者，拥有多年技术写作经验。"
            "你擅长将复杂的技术概念转化为通俗易懂的文章，同时保持技术深度。"
            "你的文章结构严谨，善用代码示例和图表辅助说明，深受读者喜爱。"
        ),
        tools=[save_article, word_count],
        verbose=True,
        allow_delegation=False,
    )
