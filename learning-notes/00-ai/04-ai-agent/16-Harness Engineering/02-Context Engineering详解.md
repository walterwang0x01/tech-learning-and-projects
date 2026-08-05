# Context Engineering 详解
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

Context Engineering 是 Harness Engineering 的前置基础。如果说 Prompt Engineering
关注"说什么"，Context Engineering 关注"给什么信息"，那么 Harness Engineering
关注"建什么系统"。三者是递进关系，不是替代关系。

```
生产级 Agent 的上下文预算分配：
┌─────────────────────────────────────────┐
│  Prompt（提示词）          ≈ 5%          │
│  Context（上下文信息）     ≈ 95%         │
│    ├── 系统指令            10%           │
│    ├── 检索结果（RAG）     30%           │
│    ├── 工具定义            15%           │
│    ├── 对话历史            20%           │
│    ├── 记忆/用户信息       10%           │
│    └── 当前任务上下文      10%           │
└─────────────────────────────────────────┘
```

## 2. Context Engineering 的六大维度

### 2.1 指令上下文（Instruction Context）

```python
# 系统提示词 — 精简、结构化、可机器解析
SYSTEM_PROMPT = """
## 角色
你是一个后端开发助手，专注于 Python FastAPI 项目。

## 能力
- 编写符合项目规范的代码
- 使用工具查询数据库和操作文件
- 从知识库检索技术文档

## 约束
- 遵循 src/ 下的分层架构
- 所有函数必须有类型注解
- 不直接修改数据库，通过 Repository 层操作
"""
```

### 2.2 检索上下文（Retrieval Context）

```python
# RAG 检索 — 给 Agent 相关的背景知识
# 关键：检索质量 > 检索数量

# ❌ 错误：塞入 20 个检索结果
# ✅ 正确：精选 3-5 个最相关的，经过 Reranker 排序

retriever = vectorstore.as_retriever(
    search_type="mmr",          # 最大边际相关性（多样性）
    search_kwargs={"k": 5, "fetch_k": 20},
)
```

### 2.3 工具上下文（Tool Context）

```python
# 工具定义 — 描述要精确，参数要明确
# Agent 根据工具描述决定何时调用

@tool
def query_orders(
    user_id: int,
    status: str = "",
    limit: int = 10,
) -> str:
    """查询用户的订单列表。

    当用户询问订单状态、购买记录、物流信息时使用此工具。
    不要用于查询用户个人信息（那个用 query_users）。

    Args:
        user_id: 用户ID（必填）
        status: 订单状态筛选（可选：pending/shipped/completed）
        limit: 返回数量上限（默认10）
    """
```

### 2.4 对话上下文（Conversation Context）

```python
# 对话历史管理 — 不是越多越好

# 策略1：滑动窗口（保留最近 N 轮）
messages = conversation_history[-10:]

# 策略2：摘要压缩（长对话压缩为摘要）
if len(messages) > 20:
    summary = llm.summarize(messages[:15])
    messages = [SystemMessage(content=f"之前的对话摘要：{summary}")] + messages[-5:]

# 策略3：语义过滤（只保留与当前话题相关的历史）
relevant = filter_by_relevance(messages, current_query)
```

### 2.5 记忆上下文（Memory Context）

```python
# 长期记忆 — 跨会话的用户信息和偏好
memory_context = """
用户偏好：
- 喜欢简洁的代码风格
- 偏好函数式编程
- 常用技术栈：FastAPI + PostgreSQL
- 上次讨论了用户认证模块的设计
"""
```

### 2.6 任务上下文（Task Context）

```python
# 当前任务的具体信息
task_context = """
当前任务：实现订单查询 API
相关文件：
- src/service/order_service.py（业务逻辑）
- src/repository/order_repo.py（数据访问）
- src/api/routes/orders.py（路由定义）
- tests/test_orders.py（测试文件）

依赖：OrderService 依赖 OrderRepository
参考：src/api/routes/users.py 中的用户 API 实现模式
"""
```

## 3. Context Engineering vs Harness Engineering

```
Context Engineering 解决：Agent 知道什么
  → 给对的信息，在对的时间

Harness Engineering 解决：Agent 如何被约束和验证
  → 即使 Agent 犯错，系统也能捕获并纠正

两者的关系：
  Context 让 Agent 做对的概率从 30% 提升到 70%
  Harness 让剩下 30% 的错误被自动捕获和修复
  组合效果：接近 95% 的可靠性
```

## 4. 实践建议

```
1. 上下文要精简，不要堆砌
   200 行精准的上下文 > 2000 行模糊的上下文

2. 结构化优于自然语言
   JSON/YAML/Markdown 表格 > 长段落描述

3. 动态组装优于静态模板
   根据当前任务动态选择相关上下文

4. 测量上下文质量
   追踪 Agent 首次通过率，低于 70% 说明上下文需要优化
```

## 5. 2026 年 Context Engineering 趋势

> 🔄 更新于 2026-04-21

<!-- version-check: Context Engineering 2026 landscape, checked 2026-04-21 -->

Context Engineering 在不到一年内从小众概念成为 AI 工程的核心学科。Gartner 预测 2026 年底 40% 的企业应用将嵌入 AI Agent（2025 年不到 5%）。

```
2026 年关键趋势：

1. 从 Prompt 到 Context 到 Harness 的演进已成共识
   ├─ Prompt Engineering：写好一句指令（2023-2024）
   ├─ Context Engineering：给对的信息（2025）
   └─ Harness Engineering：建好整个系统（2026）

2. Context 不再是静态的，而是动态信息架构
   ├─ 工程师设计上下文管道（Context Pipeline）
   ├─ Agent 在运行时遍历这个信息架构
   └─ 包括：记忆、RAG、历史压缩、工具解析

3. 有状态续传成为标准
   ├─ Cursor 3：服务端缓存上下文，客户端数据减少 80%+
   ├─ Claude Code：Ultraplan 云端规划 + 本地执行
   └─ 缓存上下文可将执行时间提升 15-29%

4. 上下文质量 > 上下文数量
   ├─ 最小高信号 Token 集 = 最高成功概率
   └─ 追踪 Agent 首次通过率作为上下文质量指标
```

来源：[Towards Data Science: Context Engineering for AI Agents](https://towardsdatascience.com/deep-dive-into-context-engineering-for-ai-agents/)（Content was rephrased for compliance with licensing restrictions）
来源：[Stepto.net: Context Engineering 2026](https://stepto.net/blog/context-engineering-ai-agents-production-2026)（Content was rephrased for compliance with licensing restrictions）

## 🎬 推荐视频资源

- [LangChain - Context Engineering for AI Agents](https://www.youtube.com/watch?v=9BPCV5TYPmg) — Context Engineering实战
- [DeepLearning.AI - Building Systems with ChatGPT API](https://www.deeplearning.ai/short-courses/building-systems-with-chatgpt/) — 系统级上下文管理（免费）
