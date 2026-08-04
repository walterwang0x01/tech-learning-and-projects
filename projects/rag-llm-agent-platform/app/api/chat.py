"""
对话接口
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
from typing import Optional
import json
import logging

from app.agents.rag_agent import RAGAgent
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class ChatRequest(BaseModel):
    """聊天请求模型"""
    message: str
    conversation_id: Optional[str] = None
    stream: bool = False


class ChatResponse(BaseModel):
    """聊天响应模型"""
    response: str
    conversation_id: str
    sources: Optional[list] = None


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    非流式聊天接口
    """
    try:
        agent = RAGAgent()
        result = await agent.chat(
            message=request.message,
            conversation_id=request.conversation_id,
            stream=False
        )
        
        return ChatResponse(
            response=result["response"],
            conversation_id=result["conversation_id"],
            sources=result.get("sources")
        )
    except Exception as e:
        logger.error(f"聊天处理错误: {str(e)}", exc_info=True)
        raise


@router.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    """
    WebSocket 流式聊天接口
    实现首字响应时间 ≤ 1s 的流式输出
    """
    await websocket.accept()
    agent = RAGAgent()
    conversation_id = None
    
    try:
        while True:
            # 接收消息
            data = await websocket.receive_text()
            message_data = json.loads(data)
            message = message_data.get("message", "")
            conversation_id = message_data.get("conversation_id", conversation_id)
            
            if not message:
                await websocket.send_json({
                    "error": "消息不能为空"
                })
                continue
            
            # 流式处理
            async for chunk in agent.chat_stream(
                message=message,
                conversation_id=conversation_id
            ):
                await websocket.send_json({
                    "type": "chunk",
                    "content": chunk.get("content", ""),
                    "conversation_id": chunk.get("conversation_id"),
                    "done": chunk.get("done", False)
                })
            
            # 发送完成信号
            await websocket.send_json({
                "type": "done",
                "conversation_id": conversation_id
            })
            
    except WebSocketDisconnect:
        logger.info("WebSocket 连接断开")
    except Exception as e:
        logger.error(f"WebSocket 处理错误: {str(e)}", exc_info=True)
        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })
    finally:
        await websocket.close()

