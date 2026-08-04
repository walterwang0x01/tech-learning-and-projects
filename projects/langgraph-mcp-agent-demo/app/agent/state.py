"""Agent 状态定义"""

from typing import Annotated, Literal
from operator import add

from langchain_core.messages import BaseMessage
from typing_extensions import TypedDict


class AgentState(TypedDict):
    """LangGraph Agent 状态

__author__ = "Walter Wang"

    messages: 对话消息列表（累加）
    intent: 用户意图分类
    context: RAG 检索到的上下文
    tool_results: MCP 工具调用结果
    memory: 长期记忆信息
    session_id: 会话 ID
    """

    messages: Annotated[list[BaseMessage], add]
    intent: Literal["chat", "rag", "tool", "sensitive"] | None
    context: str
    tool_results: list[dict]
    memory: str
    session_id: str
