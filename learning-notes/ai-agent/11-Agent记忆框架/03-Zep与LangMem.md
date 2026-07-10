# Zep 与 LangMem
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Zep：时序知识图谱记忆

<!-- version-check: Zep Cloud V3 SDK + Graphiti v0.29.x OSS, checked 2026-07-10 -->
<!-- 修复于 2026-07-10: 3 处 gpt-5.2 已过时，更新为 gpt-5.6（GPT-5.6 已于 2026-07-09 GA） -->

Zep 为 AI Agent 提供基于时序知识图谱的记忆服务，自动从对话中提取事实、构建实体图谱、追踪时间变化。核心引擎 Graphiti 开源。

> 🔄 更新于 2026-04-18
>
> **Zep 定位升级为"上下文工程平台"**：不再仅是记忆层，而是结合 Agent 记忆、Graph RAG、自动化上下文组装的完整平台。在 LoCoMo 基准上多个配置超越 Mem0，提供精度/延迟/Token 效率的灵活权衡。
> 来源：[Zep 官网](https://www.getzep.com/mem0-alternative)
>
> **Graphiti 开源引擎**：时序感知知识图谱引擎，支持非结构化对话数据和结构化业务数据的动态合成，双时间戳模型（事件时间 + 摄入时间），融合时间/全文/语义/图算法的混合查询。提供 MCP Server 集成。
> 来源：[Graphiti GitHub](https://github.com/getzep/graphiti)、[arXiv 论文](https://arxiv.org/abs/2501.13956)
>
> **Zep Cloud vs Graphiti OSS**：Zep Cloud 提供托管服务（基于信用额度），Graphiti 是底层开源图引擎，需自行管理图数据库。

```
┌──────────────────────────────────────┐
│              Zep Memory              │
│  ┌──────────┐  ┌─────────────────┐  │
│  │事实提取   │  │时序知识图谱      │  │
│  │Fact      │  │Temporal KG     │  │
│  │Extraction│  │                 │  │
│  └──────────┘  └─────────────────┘  │
│  ┌──────────┐  ┌─────────────────┐  │
│  │实体图谱   │  │对话分类          │  │
│  │Entity    │  │Dialog          │  │
│  │Graph     │  │Classification  │  │
│  └──────────┘  └─────────────────┘  │
└──────────────────────────────────────┘
```

```python
from zep_cloud.client import Zep

zep = Zep(api_key="z_xxx")

# 创建用户和会话
user_id = "alice"
zep.user.add(user_id=user_id, metadata={"role": "engineer"})
session = zep.memory.add_session(session_id="s1", user_id=user_id)

# 添加对话记忆
zep.memory.add(
    session_id="s1",
    messages=[
        {"role_type": "user", "content": "我刚从阿里跳槽到字节，做 AI 平台"},
        {"role_type": "assistant", "content": "恭喜！字节的 AI 平台团队很强"},
        {"role_type": "user", "content": "是的，我负责模型推理优化"},
    ],
)

# Zep 自动提取事实（带时间戳）
facts = zep.memory.get(session_id="s1")
# → [{"fact": "Alice 在字节跳动工作", "created_at": "2025-07-01"},
#    {"fact": "Alice 之前在阿里巴巴", "valid_until": "2025-07-01"},
#    {"fact": "Alice 负责模型推理优化", "created_at": "2025-07-01"}]
```

## 2. Zep 核心特性

```python
# 语义搜索记忆
results = zep.memory.search(
    session_id="s1",
    text="她的工作经历",
    search_type="similarity",
    limit=5,
)

# 获取用户实体图谱
graph = zep.user.get_facts(user_id="alice")
# → 实体关系：
# Alice --[就职于]--> 字节跳动 (2025-07至今)
# Alice --[曾就职于]--> 阿里巴巴 (至2025-07)
# Alice --[负责]--> 模型推理优化

# 时序感知：Zep 知道哪些事实已过期
# "Alice 在阿里工作" → 标记为历史事实
# "Alice 在字节工作" → 当前有效事实
```

## 3. Zep 与 LangChain 集成

> ⚠️ 注意：`langchain_community.memory.ZepMemory` 已随 Zep V2 SDK 废弃（2026-02 废弃波次）。Zep V3 SDK 推荐直接使用 `zep_cloud.client.Zep` 客户端或 Graphiti MCP Server 集成。以下代码为 legacy 参考。

```python
from langchain_community.memory import ZepMemory
from langchain_openai import ChatOpenAI
from langchain.chains import ConversationChain

# 使用 Zep 作为 LangChain 记忆后端（legacy V2 API）
memory = ZepMemory(
    session_id="session-001",
    url="https://api.getzep.com",
    api_key="z_xxx",
    memory_key="chat_history",
)

chain = ConversationChain(
    llm=ChatOpenAI(model="gpt-5.6"),
    memory=memory,
)

response = chain.predict(input="我在准备系统设计面试")
# Zep 自动提取并存储事实
```

## 4. LangMem：LangChain 的记忆库

LangMem 是 LangChain 官方的记忆管理库，专为 LangGraph Agent 设计，支持三种记忆类型。

```
┌──────────────────────────────────────────┐
│              LangMem                      │
│  ┌────────────┐ ┌──────────┐ ┌────────┐ │
│  │Semantic    │ │Procedural│ │Episodic│ │
│  │语义记忆     │ │程序记忆   │ │情景记忆 │ │
│  │(事实/知识) │ │(技能/规则)│ │(经历)  │ │
│  └────────────┘ └──────────┘ └────────┘ │
│         ↕ LangGraph State ↕              │
└──────────────────────────────────────────┘
```

```python
from langmem import create_memory_store_manager

# 创建记忆管理器
memory_manager = create_memory_store_manager(
    "openai:gpt-5.6",
    memory_types=[
        {
            "name": "semantic",
            "description": "用户相关的事实和知识",
            "update_mode": "patch",  # 增量更新
        },
        {
            "name": "procedural",
            "description": "学到的规则和偏好",
            "update_mode": "patch",
        },
        {
            "name": "episodic",
            "description": "重要的交互经历",
            "update_mode": "insert",  # 追加
        },
    ],
)
```

## 5. LangMem 与 LangGraph 集成

```python
from langgraph.graph import StateGraph, START, END
from langgraph.store.memory import InMemoryStore
from langmem import create_memory_store_manager, create_manage_memory_tool

# 创建记忆存储
store = InMemoryStore()

# 方式1：后台自动提取记忆
memory_manager = create_memory_store_manager(
    "openai:gpt-5.6",
    namespace=("memories", "{user_id}"),
)

# 方式2：Agent 主动管理记忆（工具方式）
manage_memory = create_manage_memory_tool(namespace=("memories", "{user_id}"))

def chat_node(state, config, store):
    user_id = config["configurable"]["user_id"]
    # 检索相关记忆
    memories = store.search(("memories", user_id), query=state["query"])
    memory_str = "\n".join(m.value["content"] for m in memories)

    response = llm.invoke(
        f"记忆：{memory_str}\n\n用户：{state['query']}"
    )
    return {"response": response.content}

graph = StateGraph(ChatState)
graph.add_node("chat", chat_node)
graph.add_edge(START, "chat")
graph.add_edge("chat", END)
app = graph.compile(store=store)
```

## 6. LangMem 记忆类型详解

```python
# 语义记忆（Semantic）：事实和知识
# "用户是 Python 开发者" → 持久存储，可更新
semantic_memories = [
    {"content": "用户精通 Python 和 Go", "type": "skill"},
    {"content": "用户在字节跳动工作", "type": "fact"},
]

# 程序记忆（Procedural）：学到的规则和模式
# "用户喜欢简洁的代码" → 影响 Agent 行为
procedural_memories = [
    {"content": "回答时使用中文", "type": "preference"},
    {"content": "代码示例优先使用 Python", "type": "rule"},
]

# 情景记忆（Episodic）：具体经历
# "上次帮用户调试了内存泄漏" → 参考历史
episodic_memories = [
    {"content": "2025-06-15 帮助调试 OOM 问题，原因是未关闭数据库连接", "type": "episode"},
]
```

## 7. Google Always-On Memory Agent

Google 于 2026 年 3 月开源的持续记忆 Agent 方案。

```
核心思路：
├─ 后台持续运行的记忆 Agent
├─ 监听所有对话，自动提取和整理记忆
├─ 定期合并、去重、更新记忆
└─ 为前台 Agent 提供记忆检索服务

架构：
┌──────────┐     ┌──────────────┐     ┌──────────┐
│ 前台Agent │←───→│ Memory Agent │←───→│ 记忆存储  │
│ (对话)    │     │ (后台常驻)    │     │ (向量DB) │
└──────────┘     └──────────────┘     └──────────┘
                       ↑
                  定期整理/合并
```

## 8. 记忆框架选型指南

> 🔄 更新于 2026-04-18

| 维度         | Mem0        | Letta       | Zep          | LangMem      |
|-------------|-------------|-------------|--------------|--------------|
| 记忆提取     | 自动（v2.0 新算法）| Agent自主 + Omni-Tool | 自动   | 自动/工具     |
| 时序感知     | ✅ v2.0 新增 | ❌          | ✅ 核心特性   | ❌           |
| 图记忆       | ✅ 仅云服务  | ❌          | ✅ Graphiti  | ❌           |
| Agent运行时  | ❌          | ✅          | ❌           | ❌           |
| LangGraph   | 需适配      | 需适配       | ✅ 插件      | ✅ 原生      |
| MCP 集成     | ✅ 9 个工具  | ❌          | ✅ Graphiti MCP | ❌        |
| 自托管       | ✅          | ✅          | ✅ Graphiti  | ✅           |
| 云服务       | ✅          | ✅          | ✅           | ❌           |

```
选型决策树（2026 更新）：

用 LangGraph？ ──→ YES ──→ LangMem（原生集成）
     │
     NO
     ↓
需要完整上下文工程？ ──→ YES ──→ Zep（Graph RAG + 时序图 + 自动组装）
     │
     NO
     ↓
需要Agent自主管理记忆？ ──→ YES ──→ Letta（OS式记忆 + Omni-Tool）
     │
     NO
     ↓
快速添加记忆层 ──→ Mem0（v2.0 新算法，最简集成）
```
## 🎬 推荐视频资源

### 🌐 YouTube
- [Zep - Long-Term Memory for AI](https://www.youtube.com/watch?v=nMGCE4GU1kc) — Zep记忆系统介绍

### 📖 官方文档
- [Zep Docs](https://help.getzep.com/) — Zep官方文档
- [LangMem Docs](https://langchain-ai.github.io/langmem/) — LangMem文档
