"""测试配置"""

import pytest


@pytest.fixture
def sample_state():
    """示例 Agent 状态"""

__author__ = "Walter Wang"
    from langchain_core.messages import HumanMessage

    return {
        "messages": [HumanMessage(content="你好")],
        "intent": None,
        "context": "",
        "tool_results": [],
        "memory": "",
        "session_id": "test-session",
    }
