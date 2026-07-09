# RAG 架构与核心流程
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. RAG 演进路线

```
Naive RAG → Advanced RAG → Modular RAG

Naive RAG:    检索 → 生成（简单拼接）
Advanced RAG: 预检索优化 → 检索 → 后检索优化 → 生成
Modular RAG:  可插拔模块，灵活组合检索、改写、重排、生成
```

## 2. 核心流程

```
┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ 文档加载  │ → │ 文本分块  │ → │ 向量化   │ → │ 存入向量库│
│ Loading   │   │ Chunking │   │ Embedding│   │ Indexing  │
└──────────┘   └──────────┘   └──────────┘   └──────────┘

┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐
│ 用户查询  │ → │ 检索     │ → │ 重排序   │ → │ 生成回答  │
│ Query     │   │ Retrieval│   │ Reranking│   │ Generation│
└──────────┘   └──────────┘   └──────────┘   └──────────┘
```

## 3. 文档加载与分块

```python
from langchain_community.document_loaders import (
    PyPDFLoader, TextLoader, CSVLoader, UnstructuredMarkdownLoader
)
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 加载文档
loader = PyPDFLoader("report.pdf")
documents = loader.load()

# 分块策略
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,        # 每块大小
    chunk_overlap=50,      # 重叠区域
    separators=["\n\n", "\n", "。", "，", " "],  # 中文友好分隔符
    length_function=len,
)
chunks = splitter.split_documents(documents)
print(f"文档分为 {len(chunks)} 个块")
```

```python
# LlamaIndex 语义分块
from llama_index.core.node_parser import SemanticSplitterNodeParser
from llama_index.embeddings.openai import OpenAIEmbedding

splitter = SemanticSplitterNodeParser(
    embed_model=OpenAIEmbedding(),
    buffer_size=1,
    breakpoint_percentile_threshold=95,  # 语义断点阈值
)
nodes = splitter.get_nodes_from_documents(documents)
```

## 4. Embedding 模型选择

<!-- version-check: Embedding 模型对比, jina-embeddings-v5 (2026-02-18), checked 2026-05-13 -->

| 模型 | 维度 | 中文支持 | 特点 |
|------|------|---------|------|
| text-embedding-3-small | 1536 | 好 | OpenAI，性价比高 |
| text-embedding-3-large | 3072 | 好 | OpenAI，精度最高 |
| bge-m3 | 1024 | 优秀 | 开源，多语言多粒度 |
| jina-embeddings-v5 | 1024 | 好 | 开源，多语言，Matryoshka 维度 |

```python
from langchain_openai import OpenAIEmbeddings

embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vector = embeddings.embed_query("AI Agent 是什么？")
print(f"向量维度: {len(vector)}")  # 1536
```

## 5. 检索与重排

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import Chroma

# 构建向量库
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=OpenAIEmbeddings(model="text-embedding-3-small"),
    persist_directory="./chroma_db",
)

# 基础检索
retriever = vectorstore.as_retriever(
    search_type="mmr",       # mmr = 最大边际相关性（兼顾相关性和多样性）
    search_kwargs={"k": 5, "fetch_k": 20},
)
docs = retriever.invoke("RAG 的核心流程是什么？")

# Reranking 重排序
from langchain.retrievers import ContextualCompressionRetriever
from langchain_cohere import CohereRerank

reranker = CohereRerank(model="rerank-v3.5", top_n=3)
compression_retriever = ContextualCompressionRetriever(
    base_compressor=reranker,
    base_retriever=retriever,
)
reranked_docs = compression_retriever.invoke("RAG 的核心流程是什么？")
```

## 6. 生成与引用

```python
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# RAG Chain
template = """基于以下上下文回答问题。如果上下文中没有相关信息，请说明。
在回答中标注引用来源 [1][2]。

上下文：
{context}

问题：{question}

回答："""

prompt = ChatPromptTemplate.from_template(template)
llm = ChatOpenAI(model="gpt-5.5", temperature=0)  # <!-- 修复于 2026-07-09: gpt-5.2 → gpt-5.5 -->

def format_docs(docs):
    return "\n\n".join(f"[{i+1}] {doc.page_content}" for i, doc in enumerate(docs))

rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

answer = rag_chain.invoke("RAG 有哪些优化策略？")
print(answer)
```
## 🎬 推荐视频资源

- [DeepLearning.AI - Building and Evaluating Advanced RAG](https://www.deeplearning.ai/short-courses/building-evaluating-advanced-rag/) — 高级RAG构建与评估（免费）
- [freeCodeCamp - RAG Tutorial](https://www.youtube.com/watch?v=T-D1OfcDW1M) — RAG完整教程
- [DeepLearning.AI - LangChain Chat with Your Data](https://www.deeplearning.ai/short-courses/langchain-chat-with-your-data/) — 用LangChain构建RAG（免费）
### 📺 B站（Bilibili）
- [RAG从入门到精通](https://www.bilibili.com/video/BV1PD421E7mN) — RAG完整中文教程
- [李沐 - 检索增强生成论文精读](https://space.bilibili.com/1567748478) — RAG论文精读

### 🎓 DeepLearning.AI（免费）
- [Building and Evaluating Advanced RAG](https://www.deeplearning.ai/short-courses/building-evaluating-advanced-rag/) — 高级RAG构建
