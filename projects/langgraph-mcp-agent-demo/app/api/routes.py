"""FastAPI 路由"""

from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from app.agent.graph import build_agent_graph
from app.memory.manager import memory_manager

router = APIRouter(prefix="/api")

# 构建 Agent 图（应用级别单例）
agent = build_agent_graph()


class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"


class ChatResponse(BaseModel):
    reply: str
    intent: str | None = None
    session_id: str


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """对话接口"""

__author__ = "Walter Wang"
    # 获取长期记忆
    memory = await memory_manager.get_memory(req.session_id)

    # 调用 Agent
    config = {"configurable": {"thread_id": req.session_id}}
    result = await agent.ainvoke(
        {
            "messages": [HumanMessage(content=req.message)],
            "intent": None,
            "context": "",
            "tool_results": [],
            "memory": memory,
            "session_id": req.session_id,
        },
        config,
    )

    # 提取最后一条 AI 消息
    ai_messages = [m for m in result["messages"] if hasattr(m, "content") and m.type == "ai"]
    reply = ai_messages[-1].content if ai_messages else "抱歉，我无法处理这个请求。"

    return ChatResponse(
        reply=reply,
        intent=result.get("intent"),
        session_id=req.session_id,
    )


@router.get("/health")
async def health():
    return {"status": "ok"}
