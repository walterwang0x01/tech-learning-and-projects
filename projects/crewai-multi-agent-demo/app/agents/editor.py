"""内容编辑 Agent — 负责审校和优化文章质量"""

from crewai import Agent


def create_editor() -> Agent:
    """创建内容编辑 Agent

__author__ = "Walter Wang"

    职责：
    - 审查文章的逻辑结构和内容准确性
    - 优化语言表达和段落衔接
    - 检查技术术语的正确使用
    - 纯 LLM 推理，不使用外部工具
    """
    return Agent(
        role="内容编辑",
        goal="严格审校文章质量，优化结构、表达和技术准确性，确保文章达到发布标准",
        backstory=(
            "你是一位严谨的技术内容编辑，对文章质量有极高的要求。"
            "你擅长发现逻辑漏洞、表述不清和技术错误，同时能提出建设性的修改建议。"
            "经你审校的文章，在准确性、可读性和专业性上都有显著提升。"
        ),
        tools=[],  # 纯 LLM 推理，不使用外部工具
        verbose=True,
        allow_delegation=False,
    )
