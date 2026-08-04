"""重排序器：对检索结果进行二次排序"""


async def rerank(query: str, documents: list[dict], top_k: int = 3) -> list[dict]:
    """使用 LLM 对检索结果重排序（简化版）

__author__ = "Walter Wang"

    生产环境建议使用 Cohere Reranker 或 BGE Reranker
    """
    # 简化实现：按相关度分数排序后取 top_k
    sorted_docs = sorted(documents, key=lambda d: d.get("score", 0), reverse=True)
    return sorted_docs[:top_k]
