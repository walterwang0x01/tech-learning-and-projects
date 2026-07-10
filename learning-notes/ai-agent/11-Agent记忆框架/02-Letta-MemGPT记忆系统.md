# Letta (MemGPT) 记忆系统
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

<!-- version-check: Letta SDK v1.0+, checked 2026-07-10 -->
<!-- 修复于 2026-07-10: 全文 4 处 gpt-5.2 已过时，更新为 gpt-5.6（GPT-5.6 已于 2026-07-09 GA） -->

Letta（前身 MemGPT）是 UC Berkeley 研究团队开发的有状态 Agent 运行时，采用操作系统启发的分层记忆架构，让 Agent 能自主管理自己的记忆。GitHub 21K+ Stars。

> 🔄 更新于 2026-05-13
>
> **Letta SDK v1.0 重大更新**：客户端初始化从 `create_client()` 改为 `Letta()` 构造函数，属性全面改为 `snake_case`，列表方法返回分页对象，`archival_memory` 改为 `archives` API，`modify()` 改为 `update()`。详见 [API v1.0 Migration Guide](https://docs.letta.com/api-overview/v1-migration-guide)。
>
> **Letta v0.16.7**（2026-03-31）：默认上下文窗口 32K→128K，压缩（compaction）机制全面重构（21 项修复），Block 大小限制移除，GPT-5.4/Opus 4.6/Sonnet 4.6 全面支持，WebSocket 传输支持 OpenAI Responses API，安全加固（阻止 `file:///` URL 和内部 MCP 目标）。
> 来源：[Letta Releases](https://github.com/letta-ai/letta/releases)
>
> **Memory Omni-Tool**：Agent 可动态创建和删除记忆块（memory blocks），不再局限于固定记忆架构。Claude Sonnet 4.5 专门针对此工具做了后训练，但该工具兼容所有模型。
> 来源：[Letta Blog](https://www.letta.com/blog/introducing-sonnet-4-5-and-the-memory-omni-tool-in-letta)
>
> **Letta Code**：记忆优先的编码 Agent，基于 Letta API 构建，支持跨会话持久化 Agent、Context Repositories（Git 式记忆管理）。
> 来源：[Letta Blog](https://www.letta.com/blog/letta-code)
>
> **Conversations API**：会话分叉（forking）、幂等流式传输（OTID）、按最后消息时间排序、请求级系统提示覆盖。

```
┌─────────────────────────────────────────────┐
│              Letta Agent Runtime             │
├─────────────────────────────────────────────┤
│  ┌─────────────────────────────────────┐    │
│  │  Core Memory（核心记忆 - 上下文内）   │    │
│  │  ├─ Human Block: 用户信息            │    │
│  │  └─ Persona Block: Agent 人设        │    │
│  └─────────────────────────────────────┘    │
│  ┌─────────────────────────────────────┐    │
│  │  Recall Memory（回忆记忆 - 近期对话） │    │
│  │  └─ 最近对话历史的搜索索引            │    │
│  └─────────────────────────────────────┘    │
│  ┌─────────────────────────────────────┐    │
│  │  Archival Memory（归档记忆 - 向量库） │    │
│  │  └─ 无限容量的长期知识存储            │    │
│  └─────────────────────────────────────┘    │
├─────────────────────────────────────────────┤
│  工具调用 │ 状态持久化 │ 多步推理           │
└─────────────────────────────────────────────┘
```

核心理念：Agent 通过系统调用（函数调用）自主读写记忆，类似操作系统的内存管理。

## 2. 分层记忆架构

```
类比操作系统内存层级：

CPU 寄存器  ←→  System Prompt（固定指令）
L1 Cache   ←→  Core Memory（核心记忆，上下文窗口内）
RAM        ←→  Recall Memory（回忆记忆，近期对话索引）
磁盘       ←→  Archival Memory（归档记忆，向量数据库）

Agent 通过以下系统调用管理记忆：
├─ core_memory_append(key, value)    # 追加核心记忆
├─ core_memory_replace(key, old, new) # 修改核心记忆
├─ recall_memory_search(query)        # 搜索近期对话
├─ archival_memory_insert(content)    # 写入归档记忆
└─ archival_memory_search(query)      # 搜索归档记忆
```

## 3. 安装与快速开始

```bash
pip install letta
letta server  # 启动 Letta 服务器（含 ADE 界面）
```

```python
# <!-- 修复于 2026-05-13: Letta SDK v1.0 API 变更，create_client → Letta 构造函数 -->
from letta import Letta

# 连接 Letta 服务器
client = Letta(base_url="http://localhost:8283")

# 创建有状态 Agent
agent = client.agents.create(
    name="personal-assistant",
    model="openai/gpt-5.6",
    embedding="openai/text-embedding-3-small",
    block_ids=[],  # 或传入已创建的 block ID
    include_base_tools=True,
)

# 单独创建并附加记忆块
human_block = client.blocks.create(
    label="human", value="用户名：Alice，职业：软件工程师"
)
persona_block = client.blocks.create(
    label="persona", value="你是一个友好的个人助手，记住用户的偏好。"
)
client.agents.blocks.attach(human_block.id, agent_id=agent.id)
client.agents.blocks.attach(persona_block.id, agent_id=agent.id)

# 与 Agent 对话（Agent 自动管理记忆）
response = client.agents.messages.create(
    agent_id=agent.id,
    input="我最近在学 Rust，觉得所有权机制很有趣",
)
print(response.items)
# Agent 内部可能执行：
# core_memory_append("human", "正在学习 Rust，对所有权机制感兴趣")
```

## 4. Agent 自编辑记忆

Letta 的核心特色：Agent 自主决定何时、如何更新记忆。

```python
# Agent 收到消息后的内部推理过程：
"""
1. 用户说"我换了新工作，现在在字节跳动做 AI 基础设施"
2. Agent 思考：用户工作信息变了，需要更新核心记忆
3. Agent 调用：core_memory_replace(
     "human",
     "职业：软件工程师",
     "职业：AI 基础设施工程师，公司：字节跳动"
   )
4. Agent 回复："恭喜新工作！字节跳动的 AI 基础设施团队很棒..."
"""

# 查看 Agent 当前核心记忆（SDK v1.0 API）
agent_state = client.agents.retrieve(agent.id, include=["agent.blocks"])
for block in agent_state.blocks:
    print(f"{block.label}: {block.value}")
# human: 用户名：Alice，职业：AI基础设施工程师，公司：字节跳动，正在学习Rust
# persona: 你是一个友好的个人助手...
```

## 5. 归档记忆操作

```python
# Agent 自动将重要信息归档
# 当对话中出现大量技术细节时，Agent 会：
"""
archival_memory_insert("Alice 的项目使用 Kubernetes 部署，
  集群规模 500+ 节点，主要运行 GPU 训练任务。
  技术栈：Python, Go, Rust, CUDA")
"""

# 后续对话中，Agent 搜索归档记忆
"""
用户："帮我回忆一下我之前说的项目架构"
Agent 内部：archival_memory_search("项目架构 部署")
→ 找到归档记忆，生成回复
"""

# 通过 API 直接操作归档记忆（SDK v1.0: archives API）
client.archives.passages.create(
    archive_id=agent.archive_id,
    text="公司技术文档：微服务架构指南 v2.0 ...",
)

results = client.agents.messages.search(
    agent_id=agent.id,
    query="微服务架构",
    limit=5,
)
```

## 6. 自定义工具

```python
from letta import Letta

client = Letta()

# 定义自定义工具
def query_database(query: str) -> str:
    """查询内部数据库

    Args:
        query: SQL 查询语句

    Returns:
        查询结果的 JSON 字符串
    """
    import sqlite3, json
    conn = sqlite3.connect("app.db")
    cursor = conn.execute(query)
    results = cursor.fetchall()
    return json.dumps(results, ensure_ascii=False)

# 注册工具
tool = client.tools.create(func=query_database)

# 创建带自定义工具的 Agent
agent = client.agents.create(
    name="db-assistant",
    model="openai/gpt-5.6",
    tool_ids=[tool.id],
    include_base_tools=True,
)

# 创建并附加记忆块
human_block = client.blocks.create(label="human", value="DBA，管理 PostgreSQL 集群")
persona_block = client.blocks.create(label="persona", value="数据库专家助手")
client.agents.blocks.attach(human_block.id, agent_id=agent.id)
client.agents.blocks.attach(persona_block.id, agent_id=agent.id)
```

## 7. Agent Development Environment (ADE)

```
Letta ADE 提供可视化界面：

┌─────────────────────────────────────────┐
│  Letta ADE (http://localhost:8283)      │
├──────────┬──────────────────────────────┤
│ Agent 列表│  Agent 详情                  │
│          │  ├─ 对话历史                  │
│ • assistant│  ├─ 核心记忆（可编辑）       │
│ • researcher│ ├─ 归档记忆浏览            │
│ • coder  │  ├─ 工具调用日志              │
│          │  ├─ 内部推理过程              │
│          │  └─ 配置管理                  │
└──────────┴──────────────────────────────┘

功能：
├─ 实时查看 Agent 内部思考过程
├─ 手动编辑核心记忆
├─ 浏览和搜索归档记忆
├─ 查看工具调用历史
└─ 调试 Agent 行为
```

## 8. 多 Agent 协作

```python
# 创建多个专业 Agent（SDK v1.0 API）
researcher = client.agents.create(
    name="researcher",
    model="openai/gpt-5.6",
    include_base_tools=True,
)
# 附加记忆块
r_persona = client.blocks.create(label="persona", value="你是研究员，负责信息收集和分析")
r_shared = client.blocks.create(label="shared", value="团队项目：AI Agent 调研报告")
client.agents.blocks.attach(r_persona.id, agent_id=researcher.id)
client.agents.blocks.attach(r_shared.id, agent_id=researcher.id)

writer = client.agents.create(
    name="writer",
    model="openai/gpt-5.6",
    include_base_tools=True,
)
w_persona = client.blocks.create(label="persona", value="你是技术作者，负责撰写报告")
w_shared = client.blocks.create(label="shared", value="团队项目：AI Agent 调研报告")
client.agents.blocks.attach(w_persona.id, agent_id=writer.id)
client.agents.blocks.attach(w_shared.id, agent_id=writer.id)

# Agent 间通过共享归档记忆协作
# researcher 将调研结果写入归档 → writer 从归档读取并撰写
```

## 9. 与 Mem0 对比

| 维度           | Letta (MemGPT)          | Mem0                    |
|---------------|-------------------------|-------------------------|
| 定位           | 有状态 Agent 运行时       | 通用记忆层               |
| 记忆管理       | Agent 自主管理（系统调用） | 框架自动提取              |
| 记忆层级       | 三层（核心/回忆/归档）     | 扁平（向量 + 图）         |
| Agent 运行时   | ✅ 完整运行时             | ❌ 仅记忆层              |
| Memory Omni-Tool | ✅ 动态创建/删除记忆块  | ❌                       |
| 可视化调试     | ✅ ADE                   | ❌ 基础 API              |
| 编码 Agent     | ✅ Letta Code            | ✅ Skill Graph + Plugin  |
| 集成方式       | 独立运行时               | 嵌入现有框架              |
| 学习曲线       | 中高                     | 低                      |
| 适用场景       | 需要深度记忆管理的Agent    | 快速为现有Agent添加记忆   |
| 开源协议       | Apache 2.0              | Apache 2.0              |
## 🎬 推荐视频资源

### 🌐 YouTube
- [MemGPT - OS-Level Memory for LLMs](https://www.youtube.com/watch?v=nMGCE4GU1kc) — MemGPT论文讲解

### 📖 官方文档
- [Letta Docs](https://docs.letta.com/) — Letta/MemGPT官方文档
- [Letta GitHub](https://github.com/letta-ai/letta) — Letta开源项目
