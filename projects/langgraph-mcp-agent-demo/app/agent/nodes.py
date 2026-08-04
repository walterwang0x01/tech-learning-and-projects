"""LangGraph 图节点定义"""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langgraph.types import interrupt

from app.agent.state import AgentState
from app.agent.prompts import SYSTEM_PROMPT, ROUTER_PROMPT
from app.config import settings


def get_llm():
    """根据配置获取 LLM 实例"""

__author__ = "Walter Wang"
    if settings.llm_provider == "anthropic":
        return ChatAnthropic(
            model=settings.llm_model,
            api_key=settings.anthropic_api_key,
        )
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.openai_api_key,
    )


async def route_intent(state: AgentState) -> dict:
    """路由节点：判断用户意图"""
    llm = get_llm()
    last_message = state["messages"][-1]
    response = await llm.ainvoke([
        SystemMessage(content=ROUTER_PROMPT),
        HumanMessage(content=last_message.content),
    ])
    intent = response.content.strip().lower()
    if intent not in ("chat", "rag", "tool", "sensitive"):
        intent = "chat"
    return {"intent": intent}


async def retrieve_context(state: AgentState) -> dict:
    """RAG 检索节点：从知识库检索相关内容"""
    from app.rag.retriever import retrieve

    last_message = state["messages"][-1]
    context = await retrieve(last_message.content)
    return {"context": context}


async def call_tools(state: AgentState) -> dict:
    """工具调用节点：通过 MCP 调用工具"""
    llm = get_llm()
    # 绑定 MCP 工具
    from app.mcp_servers.db_server import get_db_tools
    from app.mcp_servers.file_server import get_file_tools

    tools = get_db_tools() + get_file_tools()
    llm_with_tools = llm.bind_tools(tools)

    response = await llm_with_tools.ainvoke(state["messages"])

    tool_results = []
    if response.tool_calls:
        for call in response.tool_calls:
            # 查找并执行对应工具
            tool_fn = next((t for t in tools if t.name == call["name"]), None)
            if tool_fn:
                result = await tool_fn.ainvoke(call["args"])
                tool_results.append({"tool": call["name"], "result": str(result)})

    return {"tool_results": tool_results, "messages": [response]}


async def human_approval(state: AgentState) -> dict:
    """人工审批节点：敏感操作需要人工确认"""
    last_message = state["messages"][-1]
    approval = interrupt({
        "action": "sensitive_operation",
        "message": f"检测到敏感操作，是否批准？\n内容: {last_message.content}",
    })
    if approval != "approved":
        return {"messages": [AIMessage(content="操作已取消。")]}
    # 批准后转到工具调用
    return await call_tools(state)


async def generate_response(state: AgentState) -> dict:
    """生成节点：综合所有信息生成最终回答"""
    llm = get_llm()
    context = state.get("context", "")
    memory = state.get("memory", "")
    tool_results = state.get("tool_results", [])

    # 构建系统提示
    system = SYSTEM_PROMPT.format(memory=memory or "无", context=context or "无")

    # 如果有工具结果，追加到上下文
    if tool_results:
        tool_info = "\n".join(f"- {r['tool']}: {r['result']}" for r in tool_results)
        system += f"\n\n## 工具调用结果\n{tool_info}"

    messages = [SystemMessage(content=system)] + state["messages"]
    response = await llm.ainvoke(messages)
    return {"messages": [response]}


def decide_next(state: AgentState) -> str:
    """条件路由：根据意图决定下一个节点"""
    intent = state.get("intent", "chat")
    if intent == "rag":
        return "retrieve"
    elif intent == "tool":
        return "tools"
    elif intent == "sensitive":
        return "approval"
    else:
        return "generate"
