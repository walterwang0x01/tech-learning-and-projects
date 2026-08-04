"""高级研究员 Agent — 负责深度调研主题"""

from crewai import Agent
from crewai_tools import SerperDevTool, ScrapeWebsiteTool


def create_researcher() -> Agent:
    """创建高级研究员 Agent

__author__ = "Walter Wang"

    职责：
    - 使用搜索引擎调研指定主题
    - 抓取权威网页获取详细信息
    - 整理研究成果供后续 Agent 使用
    """
    return Agent(
        role="高级研究员",
        goal="针对给定主题进行全面深入的调研，收集权威资料、最新动态和关键数据",
        backstory=(
            "你是一位经验丰富的技术研究员，擅长从海量信息中筛选出最有价值的内容。"
            "你精通搜索技巧，能够快速定位权威来源，并善于将复杂的技术概念提炼为清晰的要点。"
            "你的研究报告以全面、准确、有深度著称。"
        ),
        tools=[SerperDevTool(), ScrapeWebsiteTool()],
        verbose=True,
        allow_delegation=False,
    )
