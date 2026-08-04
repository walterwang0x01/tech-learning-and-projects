"""SEO 优化师 Agent — 负责搜索引擎优化"""

from crewai import Agent
from crewai_tools import SerperDevTool

from app.tools.custom_tools import keyword_density


def create_seo_optimizer() -> Agent:
    """创建 SEO 优化师 Agent

__author__ = "Walter Wang"

    职责：
    - 分析目标关键词的搜索趋势
    - 优化文章标题、描述和关键词布局
    - 生成 SEO 友好的元数据
    - 确保关键词密度合理
    """
    return Agent(
        role="SEO 优化师",
        goal="优化文章的搜索引擎表现，提升关键词排名和自然流量",
        backstory=(
            "你是一位资深的 SEO 专家，精通搜索引擎算法和内容优化策略。"
            "你能够精准分析关键词竞争度，合理布局关键词，优化文章结构以提升搜索排名。"
            "你深谙技术博客的 SEO 特点，善于在保持内容质量的同时最大化搜索曝光。"
        ),
        tools=[SerperDevTool(), keyword_density],
        verbose=True,
        allow_delegation=False,
    )
