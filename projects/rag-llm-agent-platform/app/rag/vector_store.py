"""
向量存储实现（基于 PostgreSQL + pgvector）
"""
import logging
import asyncpg
from typing import List, Dict
from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """向量存储类"""
    
    def __init__(self):
        self.connection_pool = None
    
    async def connect(self):
        """建立连接池"""
        if not self.connection_pool:
            self.connection_pool = await asyncpg.create_pool(
                host=settings.POSTGRES_HOST,
                port=settings.POSTGRES_PORT,
                database=settings.POSTGRES_DB,
                user=settings.POSTGRES_USER,
                password=settings.POSTGRES_PASSWORD,
                min_size=5,
                max_size=20
            )
            logger.info("向量数据库连接池创建成功")
    
    async def close(self):
        """关闭连接池"""
        if self.connection_pool:
            await self.connection_pool.close()
            logger.info("向量数据库连接池已关闭")
    
    async def insert_vector(
        self,
        content: str,
        embedding: List[float],
        metadata: Dict = None
    ) -> str:
        """
        插入向量
        
        Args:
            content: 文本内容
            embedding: 向量嵌入
            metadata: 元数据
            
        Returns:
            插入的文档ID
        """
        await self.connect()
        
        async with self.connection_pool.acquire() as conn:
            doc_id = await conn.fetchval(
                """
                INSERT INTO documents (content, embedding, metadata)
                VALUES ($1, $2::vector, $3)
                RETURNING id
                """,
                content,
                str(embedding),
                metadata or {}
            )
        
        logger.info(f"向量插入成功: doc_id={doc_id}")
        return str(doc_id)
    
    async def search_similar(
        self,
        query_embedding: List[float],
        top_k: int = 5
    ) -> List[Dict]:
        """
        相似度搜索
        
        Args:
            query_embedding: 查询向量
            top_k: 返回前K个结果
            
        Returns:
            相似文档列表
        """
        await self.connect()
        
        async with self.connection_pool.acquire() as conn:
            rows = await conn.fetch(
                """
                SELECT id, content, metadata,
                       embedding <=> $1::vector AS distance
                FROM documents
                ORDER BY embedding <=> $1::vector
                LIMIT $2
                """,
                str(query_embedding),
                top_k
            )
        
        results = []
        for row in rows:
            results.append({
                "id": str(row["id"]),
                "content": row["content"],
                "metadata": row["metadata"],
                "distance": float(row["distance"])
            })
        
        logger.info(f"相似度搜索完成: 返回 {len(results)} 个结果")
        return results

