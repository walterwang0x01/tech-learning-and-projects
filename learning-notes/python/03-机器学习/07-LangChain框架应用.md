# LangChain 框架应用
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> LangChain 是一个用于构建基于大语言模型（LLM）应用的框架

## 1. LangChain 概述

LangChain 是一个强大的框架，用于开发由语言模型驱动的应用程序。它提供了：
- **模块化组件**：可组合的链、代理、提示等
- **预构建链**：常见任务的即用型链
- **数据连接**：与各种数据源集成
- **代理系统**：让 LLM 使用工具和环境

## 2. 核心概念

### 2.1 组件架构

```
LangChain 应用
├── LLM/聊天模型
├── 提示模板（Prompt Templates）
├── 输出解析器（Output Parsers）
├── 链（Chains）
├── 代理（Agents）
├── 记忆（Memory）
└── 数据连接（Data Connections）
```

### 2.2 安装

```bash
pip install langchain
pip install langchain-openai  # OpenAI 集成
pip install langchain-community  # 社区集成
```

## 3. 基础使用

### 3.1 LLM 调用

```python
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

# 初始化模型
llm = ChatOpenAI(
    model_name="gpt-5.2",
    temperature=0.7,
    api_key="your-api-key"
)

# 简单调用
messages = [
    SystemMessage(content="你是一个有用的AI助手"),
    HumanMessage(content="什么是Python？")
]
response = llm.invoke(messages)
print(response.content)
```

### 3.2 提示模板

```python
from langchain.prompts import ChatPromptTemplate

# 创建提示模板
template = ChatPromptTemplate.from_messages([
    ("system", "你是一个专业的{role}"),
    ("human", "{question}")
])

# 格式化提示
prompt = template.format_messages(
    role="Python开发工程师",
    question="如何优化Python代码性能？"
)

response = llm.invoke(prompt)
print(response.content)
```

### 3.3 链（Chains）

> ⚠️ **废弃警告**：`LLMChain` 在 LangChain 1.0 中已废弃并移除。推荐使用 LCEL（LangChain Expression Language）替代。

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# 定义提示模板
prompt = PromptTemplate(
    input_variables=["topic"],
    template="用一句话解释什么是{topic}？"
)

# LCEL 方式（推荐）
llm = ChatOpenAI(model_name="gpt-5.2")
chain = prompt | llm

# 运行链
result = chain.invoke({"topic": "机器学习"})
print(result.content)
```

## 4. 数据连接

### 4.1 文档加载器

```python
from langchain_community.document_loaders import TextLoader, PyPDFLoader

# 加载文本文件
loader = TextLoader("data.txt")
documents = loader.load()

# 加载PDF文件
pdf_loader = PyPDFLoader("document.pdf")
pdf_docs = pdf_loader.load()
```

### 4.2 文本分割

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

# 创建文本分割器
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)

# 分割文档
chunks = text_splitter.split_documents(documents)
```

### 4.3 向量存储

```python
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS

# 创建嵌入模型
embeddings = OpenAIEmbeddings()

# 创建向量存储
vectorstore = FAISS.from_documents(chunks, embeddings)

# 相似度搜索
query = "什么是机器学习？"
docs = vectorstore.similarity_search(query, k=3)
```

## 5. 检索增强生成（RAG）

> 🔄 更新于 2026-05-21：使用 LCEL 重写，替代已废弃的 `RetrievalQA` 和 `ConversationalRetrievalChain`。

### 5.1 基础 RAG 实现（LCEL 方式）

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 初始化组件
llm = ChatOpenAI(model_name="gpt-5.2")
embeddings = OpenAIEmbeddings()

# 假设 vectorstore 已创建（参见第 4 节）
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 定义 RAG 提示模板
rag_prompt = ChatPromptTemplate.from_messages([
    ("system", "根据以下上下文回答用户问题。如果上下文中没有相关信息，请说明。\n\n上下文：\n{context}"),
    ("human", "{question}")
])

# 格式化检索到的文档
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 构建 LCEL RAG 链
rag_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)

# 查询
answer = rag_chain.invoke("Python有哪些特性？")
print(answer)
```

### 5.2 带来源文档的 RAG

```python
from langchain_core.runnables import RunnableParallel

# 同时返回答案和来源文档
rag_chain_with_sources = RunnableParallel(
    {"context": retriever, "question": RunnablePassthrough()}
).assign(
    answer=lambda x: (
        rag_prompt.invoke({"context": format_docs(x["context"]), "question": x["question"]})
        | llm
        | StrOutputParser()
    ).invoke({})
)

# 或者更简洁的写法：分别获取
docs = retriever.invoke("Python有哪些特性？")
answer = rag_chain.invoke("Python有哪些特性？")
print(f"答案: {answer}")
print(f"来源: {[doc.metadata for doc in docs]}")
```

### 5.3 带记忆的 RAG（LangGraph 方式）

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated
from langchain_core.messages import HumanMessage, AIMessage

# 定义状态
class RAGState(TypedDict):
    messages: list
    context: str

# 定义节点
def retrieve(state: RAGState) -> RAGState:
    """检索相关文档"""
    last_message = state["messages"][-1].content
    docs = retriever.invoke(last_message)
    context = format_docs(docs)
    return {"context": context, "messages": state["messages"]}

def generate(state: RAGState) -> RAGState:
    """基于上下文生成回答"""
    last_message = state["messages"][-1].content
    prompt = rag_prompt.invoke({"context": state["context"], "question": last_message})
    response = llm.invoke(prompt)
    return {"messages": state["messages"] + [response], "context": state["context"]}

# 构建图
graph = StateGraph(RAGState)
graph.add_node("retrieve", retrieve)
graph.add_node("generate", generate)
graph.add_edge(START, "retrieve")
graph.add_edge("retrieve", "generate")
graph.add_edge("generate", END)

# 编译（带记忆持久化）
memory = MemorySaver()
rag_app = graph.compile(checkpointer=memory)

# 多轮对话（通过 thread_id 维持上下文）
config = {"configurable": {"thread_id": "user-123"}}
result1 = rag_app.invoke(
    {"messages": [HumanMessage(content="什么是Python？")], "context": ""},
    config=config
)
result2 = rag_app.invoke(
    {"messages": [HumanMessage(content="它有什么优势？")], "context": ""},
    config=config
)
print(result2["messages"][-1].content)
```

## 6. 代理（Agents）

> 🔄 更新于 2026-05-21：使用 `@tool` 装饰器和 LangGraph 重写，替代已废弃的 `initialize_agent`。

### 6.1 工具定义（推荐方式）

```python
from langchain_core.tools import tool
from langchain_community.utilities import WikipediaAPIWrapper

wikipedia = WikipediaAPIWrapper()

@tool
def search_wikipedia(query: str) -> str:
    """搜索 Wikipedia 获取信息。当需要查找百科知识时使用。"""
    return wikipedia.run(query)

@tool
def calculator(expression: str) -> str:
    """执行数学计算。输入应为合法的数学表达式。"""
    try:
        return str(eval(expression))
    except Exception as e:
        return f"计算错误: {e}"

tools = [search_wikipedia, calculator]
```

### 6.2 使用 LangGraph 创建 ReAct Agent

```python
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI

# LangGraph 预构建的 ReAct Agent（推荐方式）
llm = ChatOpenAI(model_name="gpt-5.2")
agent = create_react_agent(llm, tools)

# 运行 Agent
result = agent.invoke({"messages": [("human", "Python是什么？帮我在Wikipedia上查一下")]})
print(result["messages"][-1].content)
```

### 6.3 带状态的 Agent（LangGraph 自定义）

```python
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

# 定义节点
def call_model(state: AgentState) -> AgentState:
    """调用 LLM"""
    llm_with_tools = llm.bind_tools(tools)
    response = llm_with_tools.invoke(state["messages"])
    return {"messages": [response]}

def should_continue(state: AgentState) -> str:
    """判断是否需要调用工具"""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return END

# 构建图
graph = StateGraph(AgentState)
graph.add_node("agent", call_model)
graph.add_node("tools", ToolNode(tools))
graph.add_edge(START, "agent")
graph.add_conditional_edges("agent", should_continue, {"tools": "tools", END: END})
graph.add_edge("tools", "agent")

agent_app = graph.compile()

# 运行
result = agent_app.invoke({"messages": [HumanMessage(content="计算 (15 + 27) * 3")]})
print(result["messages"][-1].content)
```

### 6.4 自定义工具（类方式）

```python
from langchain_core.tools import BaseTool
from pydantic import BaseModel, Field

class SearchInput(BaseModel):
    query: str = Field(description="搜索关键词")

class CustomSearchTool(BaseTool):
    name: str = "custom_search"
    description: str = "自定义搜索工具，用于查找特定信息"
    args_schema: type[BaseModel] = SearchInput

    def _run(self, query: str) -> str:
        # 工具逻辑
        return f"搜索结果: {query}"

    async def _arun(self, query: str) -> str:
        return self._run(query)

# 使用
custom_tool = CustomSearchTool()
tools.append(custom_tool)
```

## 7. 记忆与状态管理

> 🔄 更新于 2026-05-21：使用 LangGraph checkpointer 重写，替代已废弃的 `ConversationBufferMemory` 等 legacy memory API。

### 7.1 LangGraph 消息持久化（推荐方式）

LangChain 1.x 中，记忆管理推荐使用 LangGraph 的 checkpointer 机制，而非旧的 `ConversationBufferMemory`。

```python
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages

# 定义状态（消息列表自动累积）
class ChatState(TypedDict):
    messages: Annotated[list, add_messages]

# 定义聊天节点
llm = ChatOpenAI(model_name="gpt-5.2")

def chat(state: ChatState) -> ChatState:
    system = SystemMessage(content="你是一个有用的AI助手")
    response = llm.invoke([system] + state["messages"])
    return {"messages": [response]}

# 构建图
graph = StateGraph(ChatState)
graph.add_node("chat", chat)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)

# 编译（MemorySaver 自动保存每轮对话）
memory = MemorySaver()
chat_app = graph.compile(checkpointer=memory)

# 多轮对话（同一 thread_id 共享历史）
config = {"configurable": {"thread_id": "session-001"}}

r1 = chat_app.invoke({"messages": [HumanMessage(content="我叫张三")]}, config=config)
print(r1["messages"][-1].content)

r2 = chat_app.invoke({"messages": [HumanMessage(content="我叫什么名字？")]}, config=config)
print(r2["messages"][-1].content)  # 能记住"张三"
```

### 7.2 持久化到数据库（生产环境）

```python
# 生产环境推荐使用 PostgreSQL 持久化
from langgraph.checkpoint.postgres import PostgresSaver

# 连接 PostgreSQL
DB_URI = "postgresql://user:password@localhost:5432/langchain"
postgres_saver = PostgresSaver.from_conn_string(DB_URI)

# 编译时使用 PostgresSaver
chat_app = graph.compile(checkpointer=postgres_saver)

# 使用方式与 MemorySaver 完全一致
config = {"configurable": {"thread_id": "user-123"}}
result = chat_app.invoke({"messages": [HumanMessage(content="你好")]}, config=config)
```

### 7.3 消息窗口管理（控制上下文长度）

```python
from langchain_core.messages import trim_messages

# 定义消息修剪策略
trimmer = trim_messages(
    max_tokens=4000,
    strategy="last",          # 保留最近的消息
    token_counter=llm,        # 使用 LLM 的 tokenizer 计数
    include_system=True,      # 始终保留 system message
    allow_partial=False,
)

def chat_with_trim(state: ChatState) -> ChatState:
    """带消息修剪的聊天节点"""
    system = SystemMessage(content="你是一个有用的AI助手")
    # 修剪消息以控制上下文窗口
    trimmed = trimmer.invoke([system] + state["messages"])
    response = llm.invoke(trimmed)
    return {"messages": [response]}
```

### 7.4 摘要记忆（长对话压缩）

```python
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# 摘要链
summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "请将以下对话历史压缩为简洁的摘要，保留关键信息："),
    ("human", "{conversation}")
])
summary_chain = summary_prompt | llm | StrOutputParser()

class ChatWithSummaryState(TypedDict):
    messages: Annotated[list, add_messages]
    summary: str

def maybe_summarize(state: ChatWithSummaryState) -> ChatWithSummaryState:
    """当消息过多时生成摘要"""
    messages = state["messages"]
    if len(messages) > 10:
        # 对前 8 条消息生成摘要
        conversation = "\n".join(
            f"{m.type}: {m.content}" for m in messages[:8]
        )
        summary = summary_chain.invoke({"conversation": conversation})
        # 保留摘要 + 最近 2 条消息
        return {"messages": messages[-2:], "summary": summary}
    return state
```

## 8. 链的组合（LCEL）

> 🔄 更新于 2026-05-21：使用 LCEL（LangChain Expression Language）重写，替代已废弃的 `SimpleSequentialChain` 和 `MultiPromptChain`。

### 8.1 顺序组合（管道语法）

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

llm = ChatOpenAI(model_name="gpt-5.2")

# 第一步：生成大纲
outline_prompt = ChatPromptTemplate.from_messages([
    ("human", "为主题「{topic}」生成一个简短的三点大纲")
])

# 第二步：基于大纲扩展
expand_prompt = ChatPromptTemplate.from_messages([
    ("human", "基于以下大纲，写一段 200 字的介绍：\n{outline}")
])

# LCEL 顺序组合（管道语法）
chain = (
    outline_prompt
    | llm
    | StrOutputParser()
    | (lambda outline: {"outline": outline})
    | expand_prompt
    | llm
    | StrOutputParser()
)

result = chain.invoke({"topic": "Python编程"})
print(result)
```

### 8.2 并行组合

```python
from langchain_core.runnables import RunnableParallel

# 并行执行多个链
parallel_chain = RunnableParallel(
    summary=ChatPromptTemplate.from_messages([
        ("human", "用一句话总结{topic}")
    ]) | llm | StrOutputParser(),
    
    keywords=ChatPromptTemplate.from_messages([
        ("human", "列出{topic}的5个关键词，用逗号分隔")
    ]) | llm | StrOutputParser(),
    
    difficulty=ChatPromptTemplate.from_messages([
        ("human", "评估学习{topic}的难度（1-10分），只回答数字")
    ]) | llm | StrOutputParser(),
)

# 一次调用，三个结果并行生成
result = parallel_chain.invoke({"topic": "机器学习"})
print(result["summary"])
print(result["keywords"])
print(result["difficulty"])
```

### 8.3 条件路由

```python
from langchain_core.runnables import RunnableLambda, RunnableBranch

# 定义不同领域的提示
python_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个 Python 专家，擅长解答 Python 编程问题。"),
    ("human", "{question}")
])

ai_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个 AI 专家，擅长解答人工智能相关问题。"),
    ("human", "{question}")
])

general_prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个通用助手。"),
    ("human", "{question}")
])

# 路由函数
def classify_question(input_dict):
    question = input_dict["question"].lower()
    if "python" in question or "代码" in question:
        return "python"
    elif "ai" in question or "机器学习" in question or "深度学习" in question:
        return "ai"
    return "general"

# 条件分支
branch = RunnableBranch(
    (lambda x: classify_question(x) == "python", python_prompt | llm | StrOutputParser()),
    (lambda x: classify_question(x) == "ai", ai_prompt | llm | StrOutputParser()),
    general_prompt | llm | StrOutputParser(),  # 默认分支
)

# 使用
answer = branch.invoke({"question": "Python的GIL是什么？"})
print(answer)
```

### 8.4 带回退的链

```python
from langchain_core.runnables import RunnableWithFallbacks

# 主模型 + 回退模型
main_llm = ChatOpenAI(model_name="gpt-5.2", temperature=0)
fallback_llm = ChatOpenAI(model_name="gpt-5-mini", temperature=0)

# 如果主模型失败，自动切换到回退模型
prompt = ChatPromptTemplate.from_messages([("human", "{question}")])
chain_with_fallback = (
    prompt | main_llm.with_fallbacks([fallback_llm]) | StrOutputParser()
)

result = chain_with_fallback.invoke({"question": "解释量子计算"})
```

## 9. 流式输出

```python
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# 创建流式回调
streaming_llm = ChatOpenAI(
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()],
    temperature=0
)

# 流式调用
response = streaming_llm.invoke(messages)
```

## 10. 最佳实践

### 10.1 错误处理

```python
from langchain_core.exceptions import OutputParserException

try:
    result = chain.invoke({"topic": input_text})
except OutputParserException as e:
    print(f"解析错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

### 10.2 性能优化

```python
# 使用批处理（LCEL 原生支持）
inputs = [{"topic": "Python"}, {"topic": "Java"}]
results = chain.batch(inputs)

# 异步批处理（更高吞吐）
import asyncio
results = asyncio.run(chain.abatch(inputs))

# 使用缓存
from langchain_community.cache import InMemoryCache
from langchain.globals import set_llm_cache

set_llm_cache(InMemoryCache())
```

### 10.3 成本控制

```python
# 限制 token 数量
llm = ChatOpenAI(
    model_name="gpt-5.2",
    max_tokens=100,
    temperature=0
)

# 使用更便宜的模型处理简单任务
cheap_llm = ChatOpenAI(model_name="gpt-5-mini")

# 通过 with_fallbacks 实现成本分级
chain = prompt | cheap_llm.with_fallbacks([llm]) | StrOutputParser()
```

## 11. 实际应用示例

### 11.1 文档问答系统（LCEL 完整示例）

```python
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.document_loaders import DirectoryLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 1. 加载文档
loader = DirectoryLoader("./documents", glob="*.txt")
documents = loader.load()

# 2. 处理文档
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(documents)

# 3. 创建向量存储
embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(chunks, embeddings)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 4. 构建 RAG 链
llm = ChatOpenAI(model_name="gpt-5.2")

prompt = ChatPromptTemplate.from_messages([
    ("system", "你是一个文档问答助手。根据以下上下文回答问题，如果不确定请说明。\n\n{context}"),
    ("human", "{question}")
])

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

qa_chain = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

# 5. 查询
answer = qa_chain.invoke("如何使用这个系统？")
print(answer)
```

### 11.2 代码生成助手（LangGraph Agent）

```python
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_experimental.tools import PythonREPLTool

# Python REPL 工具
python_repl = PythonREPLTool()

@tool
def run_python(code: str) -> str:
    """执行 Python 代码并返回结果。用于验证代码是否正确。"""
    return python_repl.run(code)

# 创建代码助手 Agent
llm = ChatOpenAI(model_name="gpt-5.2")
code_agent = create_react_agent(
    llm,
    tools=[run_python],
    state_modifier="你是一个 Python 编程助手。当用户要求写代码时，先写代码，然后用工具验证。"
)

# 执行代码生成任务
result = code_agent.invoke({
    "messages": [("human", "写一个函数计算斐波那契数列的前n项，并测试 n=10")]
})
print(result["messages"][-1].content)
```

## 12. 总结

LangChain 1.x + LangGraph 提供了构建生产级 LLM 应用所需的完整工具链：
- **LCEL 管道语法**：通过 `|` 运算符组合 prompt → model → parser，简洁且可组合
- **LangGraph 状态图**：用于构建有状态的 Agent、多轮对话、复杂工作流
- **丰富的集成**：支持多种数据源、向量数据库和工具
- **内置持久化**：通过 checkpointer 实现对话记忆和状态恢复
- **流式与批处理**：LCEL 原生支持 `.stream()`、`.batch()`、`.astream()` 等

核心依赖关系：
```
langchain-core    → 基础抽象（Runnable、Messages、Tools）
langchain         → 高层组件（Prompts、Parsers、Retrievers）
langchain-openai  → OpenAI 模型集成
langgraph         → Agent 工作流编排、状态管理
langchain-community → 社区集成（向量数据库、文档加载器等）
```
## 🎬 推荐视频资源

- [DeepLearning.AI - LangChain for LLM Application Development](https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/) — LangChain入门（免费）
- [freeCodeCamp - LangChain Tutorial](https://www.youtube.com/watch?v=lG7Uxts9SXs) — LangChain完整教程

<!-- version-check: LangChain 1.2.18, LangGraph 1.1.9, checked 2026-05-21 -->

> 🔄 更新于 2026-05-21

## 13. LangChain 1.0 / 1.2.x 版本演进

### 13.1 LangChain 1.0 正式发布

LangChain 和 LangGraph 在 2025 年底同时发布了 **1.0 正式版**，标志着从实验性框架到生产级工具的转变。当前稳定版为 **1.2.x**，1.3.0 alpha 已在测试中。

核心变化：
- **聚焦 Agent 循环**：langchain 核心包专注于 Agent 构建
- **Middleware 概念**：新增中间件机制，提供灵活的请求/响应拦截
- **模型集成升级**：支持最新的内容类型（图片、音频、视频）
- **语义版本控制**：遵循 semver，minor 版本不会引入 Breaking Change

### 13.2 包结构变化

```bash
# 2026 年推荐安装方式
uv add langchain              # 核心包（1.2.x）
uv add langchain-openai       # OpenAI 集成
uv add langchain-anthropic    # Anthropic 集成
uv add langchain-community    # 社区集成
uv add langgraph              # Agent 工作流编排（1.x）
```

### 13.3 新版 Agent 创建方式

```python
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from langchain.tools import tool

@tool
def search(query: str) -> str:
    """搜索互联网获取信息"""
    return f"搜索结果: {query}"

# 1.x 新版 create_agent API
llm = ChatOpenAI(model="gpt-5.2")
agent = create_agent(
    llm=llm,
    tools=[search],
    system_prompt="你是一个有帮助的助手。"
)

# 运行 Agent
result = agent.invoke({"input": "今天天气怎么样？"})
```

### 13.4 LangSmith Fleet（原 Agent Builder）

LangSmith 从可观测性平台升级为 **Agent 管理平台**（2026-03 更名为 Fleet）：

- **中央 Chat Agent**：统一的 Agent 交互界面
- **Agent 身份管理**：共享权限和人工审批
- **定时报告**：Insights Agent 支持 cron 调度
- **自托管 v0.13**：企业级部署支持

来源：[LangChain 1.0 发布公告](https://blog.langchain.com/langchain-langgraph-1dot0/) | [LangChain Changelog](https://changelog.langchain.com/)

## 14. Interrupt 2026 与 LangChain 1.2.18

> 🔄 更新于 2026-05-19

<!-- version-check: LangChain 1.2.18 (2026-05-13), LangSmith Engine, LangChain Labs, Interrupt 2026 (May 13-14), checked 2026-05-19 -->

LangChain 在 **Interrupt 2026 大会**（2026-05-13/14 旧金山，1000+ 开发者参加）期间发布了一系列重要更新，标志着 LangChain 从"框架"全面转向"Agent 平台"。来源：[Everything we shipped at Interrupt](https://www.langchain.com/blog/interrupt-2026-overview)

### 14.1 LangChain 1.2.18（2026-05-13）

```bash
# Interrupt 2026 同步发布的版本
uv add langchain==1.2.18
uv add langchain-core==1.2.18
uv add langgraph==1.1.9
```

主要内容：

- **agent tag 回滚机制**：支持回滚 agent tag，方便灰度回退
- **classic 模块废弃清理**：旧的 `langchain.chains` / `langchain.agents` 兼容层进一步收敛
- **依赖项瘦身**：减少传递依赖，加快 `pip install` / `uv add`

来源：[Releasebot — May 2026](https://releasebot.io/updates/langchain-ai)

### 14.2 LangSmith Engine — 自治诊断 Agent

`LangSmith Engine` 把"读 trace → 找 pattern → 写修复"的人工循环自动化：

```python
import os
from langsmith import Client

# Engine 启用后，所有 trace 自动进入诊断队列
os.environ["LANGSMITH_ENGINE_ENABLED"] = "true"
os.environ["LANGSMITH_PROJECT"] = "my-prod-agent"

client = Client()

# 工程师只需要在 PR 评审中确认 Engine 草拟的修复 / evaluator
# 每解决一个 issue，eval 套件就被自动扩充
```

工作流变化：

| 环节 | 之前 | LangSmith Engine 之后 |
|------|------|--------------------- |
| 故障发现 | 用户反馈 / 手动看 trace | Engine 实时聚类成命名 issue |
| 根因定位 | 工程师比对代码 | Engine 对照 repo 自动定位 |
| 修复 | 写代码 + 加 eval | Engine 草拟 PR + evaluator |
| 回归保护 | 手动维护 eval 套件 | Engine 自动扩充 |

来源：[Introducing LangSmith Engine](https://www.langchain.com/blog/introducing-langsmith-engine)

### 14.3 LangChain Labs

新成立的研究实验室，聚焦让 Agent **更好、更便宜、更易评估**：

- 早期方向：cost/latency 折中、模拟与评估环境、跨模型族 prompt 优化
- 与 LangChain 主仓维持开源协同，研究成果会回流到 LangChain / LangGraph 主线

来源：[Introducing LangChain Labs](https://www.langchain.com/blog/introducing-langchain-labs)

### 14.4 LangSmith 控制面收敛（Engine + Fleet + Insights）

Day 2 的核心叙事是 "observability and governance ship together now"：

```
┌────────────────── LangSmith 统一控制面 ──────────────────┐
│                                                          │
│  ┌────────────┐   ┌────────────┐   ┌────────────┐      │
│  │   Engine   │   │   Fleet    │   │  Insights  │      │
│  │ (诊断/PR)  │   │ (治理/RBAC)│   │ (成本/质量)│      │
│  └─────┬──────┘   └─────┬──────┘   └─────┬──────┘      │
│        │                 │                 │            │
│        └─────────────────┴─────────────────┘            │
│                          │                              │
│            ┌─────────────▼──────────────┐               │
│            │  Production Trace Storage  │               │
│            │  + 30+ Evaluator Templates │               │
│            └────────────────────────────┘               │
└──────────────────────────────────────────────────────────┘
```

### 14.5 选型与升级建议

| 当前状态 | 建议 |
|----------|------|
| 还在 langchain 0.x | 直接升级到 1.2.18，参考 [migration guide](https://docs.langchain.com/oss/python/versioning) |
| 已在 1.0 / 1.1 | `uv lock --upgrade-package langchain` 升级到 1.2.18，无 Breaking |
| 仅用 LangSmith 做可观测性 | 启用 Engine 试跑（先在 staging 项目，避免误改生产代码） |
| 多 Agent 治理 | 升级到 LangSmith Fleet，启用 Agent Card + Approval 工作流 |
| 想跟踪研究方向 | 关注 [LangChain Labs](https://www.langchain.com/blog/introducing-langchain-labs) 公开仓库 |
