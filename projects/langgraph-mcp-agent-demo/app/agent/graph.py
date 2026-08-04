"""LangGraph 工作流定义 — Agent 核心图结构"""

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from app.agent.state import AgentState
from app.agent.nodes import (
    route_intent,
    retrieve_context,
    call_tools,
    human_approval,
    generate_response,
    decide_next,
)


def build_agent_graph(checkpointer=None):
    """构建 Agent 工作流图

__author__ = "Walter Wang"

    流程：
    START → 路由(意图识别)
      ├─ chat      → 生成回答 → END
      ├─ rag       → RAG检索 → 生成回答 → END
      ├─ tool      → 工具调用 → 生成回答 → END
      └─ sensitive  → 人工审批 → 生成回答 → END
    """
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("router", route_intent)
    graph.add_node("retrieve", retrieve_context)
    graph.add_node("tools", call_tools)
    graph.add_node("approval", human_approval)
    graph.add_node("generate", generate_response)

    # 定义边
    graph.add_edge(START, "router")
    graph.add_conditional_edges("router", decide_next, {
        "retrieve": "retrieve",
        "tools": "tools",
        "approval": "approval",
        "generate": "generate",
    })
    graph.add_edge("retrieve", "generate")
    graph.add_edge("tools", "generate")
    graph.add_edge("approval", "generate")
    graph.add_edge("generate", END)

    # 编译（带检查点支持会话恢复）
    if checkpointer is None:
        checkpointer = MemorySaver()

    return graph.compile(
        checkpointer=checkpointer,
        interrupt_before=["approval"],
    )
