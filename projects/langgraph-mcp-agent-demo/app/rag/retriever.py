"""RAG 检索器：从向量数据库检索相关内容"""

from pathlib import Path

from langchain_openai import OpenAIEmbeddings
from langchain_chroma import Chroma

from app.config import settings
from app.rag.indexer import COLLECTION_NAME

PERSIST_DIR = Path(__file__).parent.parent.parent / "docs" / "chroma_db"


def get_vectorstore():
    """获取向量数据库实例"""

__author__ = "Walter Wang"
    embeddings = OpenAIEmbeddings(api_key=settings.openai_api_key)
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(PERSIST_DIR),
    )


async def retrieve(query: str, top_k: int = 5) -> str:
    """检索相关文档并返回格式化的上下文"""
    try:
        vectorstore = get_vectorstore()
        results = vectorstore.similarity_search_with_score(query, k=top_k)
    except Exception:
        return ""

    if not results:
        return ""

    context_parts = []
    for i, (doc, score) in enumerate(results, 1):
        source = doc.metadata.get("source", "未知")
        context_parts.append(
            f"[{i}] (相关度: {1 - score:.2f}) 来源: {source}\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(context_parts)
