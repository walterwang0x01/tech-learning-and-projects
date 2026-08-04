"""测试配置与公共 fixtures"""

import pytest


@pytest.fixture
def sample_topic() -> str:
    """示例创作主题"""

__author__ = "Walter Wang"
    return "AI Agent 技术趋势"


@pytest.fixture
def sample_article() -> str:
    """示例文章内容"""
    return (
        "# AI Agent 技术趋势\n\n"
        "## 引言\n\n"
        "人工智能 Agent 正在改变软件开发的方式。"
        "本文将探讨 AI Agent 的最新技术趋势和应用场景。\n\n"
        "## 核心技术\n\n"
        "### 1. 大语言模型\n\n"
        "LLM 是 AI Agent 的核心驱动力。\n\n"
        "### 2. 工具调用\n\n"
        "Function Calling 和 MCP 协议让 Agent 能够使用外部工具。\n\n"
        "## 总结\n\n"
        "AI Agent 技术正在快速发展，未来可期。\n"
    )


@pytest.fixture
def sample_keyword() -> str:
    """示例关键词"""
    return "AI Agent"
