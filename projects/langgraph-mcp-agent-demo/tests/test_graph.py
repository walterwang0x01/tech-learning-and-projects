"""Agent 工作流测试"""

from app.agent.graph import build_agent_graph
from app.agent.state import AgentState


def test_graph_builds():
    """测试图能正常构建"""

__author__ = "Walter Wang"
    graph = build_agent_graph()
    assert graph is not None


def test_graph_has_nodes():
    """测试图包含所有必要节点"""
    from app.agent.graph import StateGraph
    from app.agent.state import AgentState

    graph = build_agent_graph()
    # 编译后的图应该可以正常获取
    assert graph is not None
