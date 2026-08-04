"""
RAG 检索器
"""
import logging
from typing import List, Dict
from openai import AsyncOpenAI

from app.rag.vector_store import VectorStore
from app.core.config import settings

logger = logging.getLogger(__name__)


class Retriever:
    """RAG 检索器"""
    
    def __init__(self, vector_store: VectorStore):
        self.vector_store = vector_store
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    
    async def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        检索相关文档
        
        Args:
            query: 查询文本
            top_k: 返回前K个结果
            
        Returns:
            相关文档列表
        """
        try:
            # 1. 将查询文本向量化
            embedding_response = await self.openai_client.embeddings.create(
                model=settings.EMBEDDING_MODEL,
                input=query
            )
            query_embedding = embedding_response.data[0].embedding
            
            # 2. 向量相似度搜索
            results = await self.vector_store.search_similar(
                query_embedding=query_embedding,
                top_k=top_k
            )
            
            logger.info(f"检索完成: query={query[:50]}..., 返回 {len(results)} 个结果")
            return results
            
        except Exception as e:
            logger.error(f"检索失败: {str(e)}", exc_info=True)
            return []

