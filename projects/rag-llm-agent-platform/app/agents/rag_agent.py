"""
RAG Agent 实现
结合检索增强生成和 Function Calling
"""
import logging
from typing import Optional, Dict, AsyncGenerator
import uuid

from app.rag.vector_store import VectorStore
from app.rag.retriever import Retriever
from app.tools.tool_manager import ToolManager
from app.llm.llm_client import LLMClient
from app.core.config import settings

logger = logging.getLogger(__name__)


class RAGAgent:
    """RAG Agent 主类"""
    
    def __init__(self):
        self.vector_store = VectorStore()
        self.retriever = Retriever(self.vector_store)
        self.tool_manager = ToolManager()
        self.llm_client = LLMClient()
    
    async def chat(
        self,
        message: str,
        conversation_id: Optional[str] = None,
        stream: bool = False
    ) -> Dict:
        """
        处理聊天请求
        
        Args:
            message: 用户消息
            conversation_id: 会话ID
            stream: 是否流式输出
            
        Returns:
            包含响应和会话ID的字典
        """
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # 1. 检索相关文档
        relevant_docs = await self.retriever.retrieve(message, top_k=settings.TOP_K_RESULTS)
        logger.info(f"检索到 {len(relevant_docs)} 个相关文档")
        
        # 2. 构建上下文
        context = self._build_context(relevant_docs)
        
        # 3. 获取可用工具
        available_tools = self.tool_manager.get_available_tools()
        
        # 4. 调用 LLM（带 Function Calling）
        response = await self.llm_client.chat(
            message=message,
            context=context,
            tools=available_tools,
            conversation_id=conversation_id,
            stream=stream
        )
        
        # 5. 处理工具调用（如果有）
        if response.get("tool_calls"):
            tool_results = await self._execute_tools(response["tool_calls"])
            # 再次调用 LLM，传入工具执行结果
            response = await self.llm_client.chat(
                message=message,
                context=context,
                tool_results=tool_results,
                conversation_id=conversation_id,
                stream=stream
            )
        
        return {
            "response": response["content"],
            "conversation_id": conversation_id,
            "sources": [doc.get("source") for doc in relevant_docs]
        }
    
    async def chat_stream(
        self,
        message: str,
        conversation_id: Optional[str] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        流式聊天处理
        
        Yields:
            包含内容块的字典
        """
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
        
        # 检索相关文档
        relevant_docs = await self.retriever.retrieve(message, top_k=settings.TOP_K_RESULTS)
        context = self._build_context(relevant_docs)
        available_tools = self.tool_manager.get_available_tools()
        
        # 流式调用 LLM
        async for chunk in self.llm_client.chat_stream(
            message=message,
            context=context,
            tools=available_tools,
            conversation_id=conversation_id
        ):
            yield {
                "content": chunk.get("content", ""),
                "conversation_id": conversation_id,
                "done": chunk.get("done", False)
            }
    
    def _build_context(self, docs: list) -> str:
        """构建上下文"""
        if not docs:
            return ""
        
        context_parts = ["相关文档内容："]
        for i, doc in enumerate(docs, 1):
            context_parts.append(f"\n[{i}] {doc.get('content', '')}")
            if doc.get('source'):
                context_parts.append(f"来源: {doc['source']}")
        
        return "\n".join(context_parts)
    
    async def _execute_tools(self, tool_calls: list) -> list:
        """执行工具调用"""
        results = []
        for tool_call in tool_calls:
            tool_name = tool_call.get("name")
            tool_args = tool_call.get("arguments", {})
            
            try:
                result = await self.tool_manager.execute_tool(tool_name, tool_args)
                results.append({
                    "tool_name": tool_name,
                    "result": result,
                    "success": True
                })
                logger.info(f"工具调用成功: {tool_name}")
            except Exception as e:
                logger.error(f"工具调用失败: {tool_name}, 错误: {str(e)}")
                results.append({
                    "tool_name": tool_name,
                    "result": f"执行失败: {str(e)}",
                    "success": False
                })
        
        return results

