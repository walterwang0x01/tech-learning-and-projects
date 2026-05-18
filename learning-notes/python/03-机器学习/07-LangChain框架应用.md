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
    model_name="gpt-3.5-turbo",
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

```python
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

# 定义提示模板
prompt = PromptTemplate(
    input_variables=["topic"],
    template="用一句话解释什么是{topic}？"
)

# 创建链
chain = LLMChain(llm=llm, prompt=prompt)

# 运行链
result = chain.run("机器学习")
print(result)
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

### 5.1 基础 RAG 实现

```python
from langchain.chains import RetrievalQA

# 创建检索链
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever(),
    return_source_documents=True
)

# 查询
result = qa_chain.invoke({"query": "Python有哪些特性？"})
print(result["result"])
print(result["source_documents"])
```

### 5.2 带记忆的 RAG

```python
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory

# 创建记忆
memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

# 创建对话检索链
qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    retriever=vectorstore.as_retriever(),
    memory=memory
)

# 多轮对话
result1 = qa_chain.invoke({"question": "什么是Python？"})
result2 = qa_chain.invoke({"question": "它有什么优势？"})
```

## 6. 代理（Agents）

### 6.1 工具定义

```python
from langchain.tools import Tool
from langchain_community.utilities import WikipediaAPIWrapper

# 创建工具
wikipedia = WikipediaAPIWrapper()

tools = [
    Tool(
        name="Wikipedia",
        func=wikipedia.run,
        description="用于搜索Wikipedia上的信息"
    ),
    Tool(
        name="Calculator",
        func=lambda x: str(eval(x)),
        description="用于执行数学计算"
    )
]
```

### 6.2 创建代理

```python
from langchain.agents import initialize_agent, AgentType

# 初始化代理
agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)

# 运行代理
result = agent.run("Python是什么？它在Wikipedia上的信息是什么？")
print(result)
```

### 6.3 自定义工具

```python
from langchain.tools import BaseTool
from typing import Optional

class CustomTool(BaseTool):
    name = "custom_tool"
    description = "这是一个自定义工具"
    
    def _run(self, query: str) -> str:
        # 工具逻辑
        return f"处理结果: {query}"
    
    async def _arun(self, query: str) -> str:
        # 异步版本
        return self._run(query)

# 使用自定义工具
custom_tool = CustomTool()
tools.append(custom_tool)
```

## 7. 记忆管理

### 7.1 对话记忆

```python
from langchain.memory import ConversationBufferMemory

memory = ConversationBufferMemory()
memory.save_context(
    {"input": "你好"},
    {"output": "你好！有什么可以帮助你的吗？"}
)
memory.save_context(
    {"input": "Python是什么？"},
    {"output": "Python是一种高级编程语言"}
)

# 获取记忆
print(memory.chat_memory.messages)
```

### 7.2 摘要记忆

```python
from langchain.memory import ConversationSummaryMemory

summary_memory = ConversationSummaryMemory(llm=llm)
summary_memory.save_context(
    {"input": "Python是什么？"},
    {"output": "Python是一种高级编程语言"}
)

# 获取摘要
print(summary_memory.buffer)
```

### 7.3 实体记忆

```python
from langchain.memory import ConversationEntityMemory

entity_memory = ConversationEntityMemory(llm=llm)
entity_memory.save_context(
    {"input": "我的名字是张三"},
    {"output": "好的，张三，很高兴认识你！"}
)
```

## 8. 链的组合

### 8.1 顺序链

```python
from langchain.chains import SimpleSequentialChain

# 创建多个链
chain1 = LLMChain(llm=llm, prompt=prompt1)
chain2 = LLMChain(llm=llm, prompt=prompt2)

# 组合链
overall_chain = SimpleSequentialChain(
    chains=[chain1, chain2],
    verbose=True
)

result = overall_chain.run("Python编程")
```

### 8.2 路由链

```python
from langchain.chains.router import MultiPromptChain
from langchain.chains.router.llm_router import LLMRouterChain

# 定义多个提示
prompt_infos = [
    {
        "name": "python",
        "description": "Python编程相关问题",
        "prompt_template": "你是一个Python专家..."
    },
    {
        "name": "ai",
        "description": "AI相关问题",
        "prompt_template": "你是一个AI专家..."
    }
]

# 创建路由链
chain = MultiPromptChain.from_prompts(llm, prompt_infos, verbose=True)
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
from langchain.schema import OutputParserException

try:
    result = chain.run(input_text)
except OutputParserException as e:
    print(f"解析错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

### 10.2 性能优化

```python
# 使用批处理
inputs = [{"topic": "Python"}, {"topic": "Java"}]
results = chain.batch(inputs)

# 使用缓存
from langchain.cache import InMemoryCache
from langchain.globals import set_llm_cache

set_llm_cache(InMemoryCache())
```

### 10.3 成本控制

```python
# 限制token数量
llm = ChatOpenAI(
    max_tokens=100,
    temperature=0
)

# 使用更便宜的模型
llm = ChatOpenAI(model_name="gpt-3.5-turbo")
```

## 11. 实际应用示例

### 11.1 文档问答系统

```python
from langchain.chains import RetrievalQA
from langchain_community.document_loaders import DirectoryLoader

# 加载文档
loader = DirectoryLoader("./documents", glob="*.txt")
documents = loader.load()

# 处理文档
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000)
chunks = text_splitter.split_documents(documents)

# 创建向量存储
vectorstore = FAISS.from_documents(chunks, embeddings)

# 创建问答链
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore.as_retriever()
)

# 查询
answer = qa_chain.run("如何使用这个系统？")
```

### 11.2 代码生成助手

```python
from langchain.agents import create_python_agent
from langchain.tools.python.tool import PythonREPLTool

# 创建Python代理
agent = create_python_agent(
    llm=llm,
    tool=PythonREPLTool(),
    verbose=True
)

# 执行代码生成任务
result = agent.run("写一个函数计算斐波那契数列的前n项")
```

## 12. 总结

LangChain 提供了构建强大 LLM 应用所需的所有工具：
- **模块化设计**：易于组合和扩展
- **丰富的集成**：支持多种数据源和工具
- **强大的代理系统**：让 LLM 使用外部工具
- **灵活的记忆管理**：支持多种记忆策略

通过 LangChain，可以快速构建从简单的问答系统到复杂的多代理应用。
## 🎬 推荐视频资源

- [DeepLearning.AI - LangChain for LLM Application Development](https://www.deeplearning.ai/short-courses/langchain-for-llm-application-development/) — LangChain入门（免费）
- [freeCodeCamp - LangChain Tutorial](https://www.youtube.com/watch?v=lG7Uxts9SXs) — LangChain完整教程

<!-- version-check: LangChain 1.2.x, LangGraph 1.x, checked 2026-04-22 -->

> 🔄 更新于 2026-04-22

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
llm = ChatOpenAI(model="gpt-4o")
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
