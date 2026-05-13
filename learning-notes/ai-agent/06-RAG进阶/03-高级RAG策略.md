# 高级 RAG 策略
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Query 改写与扩展

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOpenAI(model="gpt-5.2", temperature=0)  # <!-- 修复于 2026-05-13: gpt-4o 已退役 -->

# 多查询改写：将一个问题改写为多个角度
multi_query_prompt = ChatPromptTemplate.from_template("""
将以下问题从 3 个不同角度改写，以提高检索覆盖率。
每行一个改写结果。

原始问题：{question}
""")

chain = multi_query_prompt | llm
queries = chain.invoke({"question": "RAG 如何提升回答质量？"})
# 用多个改写查询分别检索，合并去重结果

# Step-back Prompting：先问更宏观的问题
stepback_prompt = ChatPromptTemplate.from_template("""
给定以下具体问题，生成一个更宏观的上位问题来辅助回答。

具体问题：{question}
上位问题：
""")
```

## 2. HyDE（假设文档嵌入）

```python
# 先让 LLM 生成假设性答案，再用答案去检索
hyde_prompt = ChatPromptTemplate.from_template("""
请直接回答以下问题（即使不确定也请尝试回答）：
{question}
""")

def hyde_retrieval(question: str, retriever):
    """HyDE: Hypothetical Document Embeddings"""
    # 1. 生成假设性答案
    hypothetical_answer = (hyde_prompt | llm).invoke({"question": question})

    # 2. 用假设答案作为查询去检索（语义更接近真实文档）
    docs = retriever.invoke(hypothetical_answer.content)
    return docs

# HyDE 的优势：假设答案的语义空间比问题更接近文档
docs = hyde_retrieval("Transformer 中注意力机制的作用是什么？", retriever)
```

## 3. Self-RAG（自反思检索）

```python
def self_rag(question: str, retriever, llm) -> str:
    """Self-RAG: 自反思检索增强生成"""

    # 1. 判断是否需要检索
    need_retrieval = llm.invoke(
        f"问题：{question}\n是否需要检索外部知识来回答？回答 yes/no"
    ).content.strip().lower()

    if need_retrieval == "no":
        return llm.invoke(question).content

    # 2. 检索文档
    docs = retriever.invoke(question)

    # 3. 评估每个文档的相关性
    relevant_docs = []
    for doc in docs:
        relevance = llm.invoke(
            f"文档：{doc.page_content}\n问题：{question}\n该文档与问题相关吗？回答 yes/no"
        ).content.strip().lower()
        if relevance == "yes":
            relevant_docs.append(doc)

    # 4. 生成回答
    context = "\n".join(d.page_content for d in relevant_docs)
    answer = llm.invoke(f"基于以下上下文回答问题。\n上下文：{context}\n问题：{question}").content

    # 5. 验证回答是否有幻觉
    hallucination_check = llm.invoke(
        f"上下文：{context}\n回答：{answer}\n回答是否完全基于上下文？回答 yes/no"
    ).content.strip().lower()

    if hallucination_check == "no":
        return "抱歉，检索到的信息不足以准确回答该问题。"
    return answer
```

## 4. Contextual Retrieval

```python
# Anthropic 提出的上下文检索：为每个 chunk 添加上下文前缀
def add_contextual_prefix(chunk: str, full_document: str, llm) -> str:
    """为文档块添加上下文说明"""
    prompt = f"""以下是完整文档的一个片段。
请用 1-2 句话简要说明该片段在文档中的位置和上下文。

完整文档：{full_document[:2000]}
片段：{chunk}

上下文说明："""

    context = llm.invoke(prompt).content
    return f"{context}\n\n{chunk}"  # 前缀 + 原始内容

# 处理所有 chunks
contextualized_chunks = [
    add_contextual_prefix(chunk.page_content, full_doc, llm)
    for chunk in chunks
]
```

## 5. Reranking 策略

```python
# 方式一：Cohere Rerank API
from cohere import Client
co = Client(api_key="xxx")

results = co.rerank(
    model="rerank-v3.5",
    query="RAG 优化策略",
    documents=[doc.page_content for doc in retrieved_docs],
    top_n=3,
)

# 方式二：Cross-Encoder 本地重排
from sentence_transformers import CrossEncoder
reranker = CrossEncoder("BAAI/bge-reranker-v2-m3")

pairs = [(query, doc.page_content) for doc in retrieved_docs]
scores = reranker.predict(pairs)
# 按分数排序取 top-k
```

## 6. Agentic RAG

```python
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from operator import add

class RAGState(TypedDict):
    question: str
    documents: list
    answer: str
    retry_count: int

def decide_retrieval(state: RAGState) -> str:
    """Agent 决定检索策略"""
    question = state["question"]
    # LLM 判断：直接回答 / 向量检索 / 网络搜索 / 数据库查询
    decision = llm.invoke(f"问题：{question}\n选择策略：direct/vector/web/sql").content
    return decision.strip()

def vector_retrieve(state: RAGState) -> dict:
    docs = retriever.invoke(state["question"])
    return {"documents": docs}

def generate_answer(state: RAGState) -> dict:
    context = "\n".join(d.page_content for d in state["documents"])
    answer = llm.invoke(f"上下文：{context}\n问题：{state['question']}").content
    return {"answer": answer}

def quality_check(state: RAGState) -> str:
    """检查回答质量，决定是否重试"""
    if state["retry_count"] >= 2:
        return END
    check = llm.invoke(f"回答是否充分？{state['answer']}\n回答 yes/no").content
    return END if "yes" in check.lower() else "rewrite_query"

# 构建 Agentic RAG 图
graph = StateGraph(RAGState)
graph.add_node("retrieve", vector_retrieve)
graph.add_node("generate", generate_answer)
graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "generate")
graph.add_conditional_edges("generate", quality_check)
app = graph.compile()
```
## 🎬 推荐视频资源

- [DeepLearning.AI - Advanced Retrieval for AI with Chroma](https://www.deeplearning.ai/short-courses/advanced-retrieval-for-ai/) — 高级检索策略（免费）
- [DeepLearning.AI - Building Agentic RAG with LlamaIndex](https://www.deeplearning.ai/short-courses/building-agentic-rag-with-llamaindex/) — Agentic RAG（免费）
