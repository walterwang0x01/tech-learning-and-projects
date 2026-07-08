# Anthropic Agent 设计模式
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Workflows vs Agents

Anthropic 在 "Building Effective Agents" 指南中将 Agentic 系统分为两大类：

```
┌─────────────────────────────────────────────────────┐
│              Agentic 系统                             │
├────────────────────────┬────────────────────────────┤
│      Workflows         │        Agents              │
│  预定义的编排流程        │  模型自主决策执行路径        │
│  LLM 按固定路径调用      │  LLM 动态选择工具和步骤     │
│  可预测、可控            │  灵活、适应性强             │
│  适合明确流程            │  适合开放式任务             │
└────────────────────────┴────────────────────────────┘
```

核心原则：**从简单开始，仅在必要时增加复杂度。**

<!-- version-check: Claude claude-sonnet-4-6, checked 2026-07-08 -->
<!-- 修复于 2026-07-08: claude-sonnet-4-6-20260401 → claude-sonnet-4-6（4.6 起采用无日期 pinned ID） -->

## 2. Workflow 模式一：Prompt Chaining（提示链）

顺序调用 LLM，前一步输出作为后一步输入，中间可插入验证门控。

```python
from anthropic import Anthropic

client = Anthropic()

def prompt_chaining(topic: str) -> dict:
    """提示链：生成 → 验证 → 优化"""

    # 步骤1：生成初稿
    draft = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"写一篇关于 {topic} 的技术博客大纲"}]
    ).content[0].text

    # 门控：验证质量
    validation = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=256,
        messages=[{"role": "user", "content": f"评估大纲质量，回答 PASS 或 FAIL：\n{draft}"}]
    ).content[0].text

    if "FAIL" in validation.upper():
        return {"status": "rejected", "draft": draft}

    # 步骤2：扩展为完整文章
    article = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": f"基于大纲写完整文章：\n{draft}"}]
    ).content[0].text

    return {"status": "success", "article": article}
```

## 3. Workflow 模式二：Routing（路由分发）

对输入进行分类，路由到不同的专业处理器。

```python
def routing_workflow(user_input: str) -> str:
    """路由：分类 → 分发到专业处理器"""

    # 分类器
    category = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=50,
        messages=[{"role": "user", "content": f"""将以下请求分类为：code_help / general_qa / creative_writing
请求：{user_input}
只输出类别名称。"""}]
    ).content[0].text.strip()

    # 专业处理器
    handlers = {
        "code_help": "你是资深程序员，提供精确的代码解决方案。",
        "general_qa": "你是知识渊博的助手，提供准确简洁的回答。",
        "creative_writing": "你是创意写作专家，文笔优美富有想象力。",
    }

    system_prompt = handlers.get(category, handlers["general_qa"])
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=system_prompt,
        messages=[{"role": "user", "content": user_input}]
    ).content[0].text

    return response
```

## 4. Workflow 模式三：Parallelization（并行化）

将任务拆分为独立子任务并行处理，或多次生成后投票。

```python
import asyncio
from anthropic import AsyncAnthropic

async_client = AsyncAnthropic()

async def parallel_sectioning(topic: str) -> dict:
    """并行分段：同时生成文章各部分"""
    sections = ["引言", "核心概念", "实践案例", "总结"]

    async def generate_section(section: str) -> str:
        resp = await async_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=1024,
            messages=[{"role": "user", "content": f"为 {topic} 文章写 {section} 部分"}]
        )
        return resp.content[0].text

    results = await asyncio.gather(*[generate_section(s) for s in sections])
    return dict(zip(sections, results))

async def parallel_voting(question: str, n_votes: int = 3) -> str:
    """并行投票：多次生成取多数"""
    async def get_answer() -> str:
        resp = await async_client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=100,
            messages=[{"role": "user", "content": f"{question}\n简短回答。"}]
        )
        return resp.content[0].text

    answers = await asyncio.gather(*[get_answer() for _ in range(n_votes)])
    # 简单多数投票（实际可用语义相似度聚类）
    from collections import Counter
    return Counter(answers).most_common(1)[0][0]
```

## 5. Workflow 模式四：Orchestrator-Workers（编排-工作者）

中央编排 LLM 动态分解任务，委派给工作者 LLM 执行。

```python
import json

def orchestrator_workers(task: str) -> dict:
    """编排者动态分解任务，工作者并行执行"""

    # 编排者：分解任务
    plan = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        messages=[{"role": "user", "content": f"""将以下任务分解为子任务，输出 JSON 数组：
任务：{task}
格式：[{{"id": 1, "subtask": "描述", "type": "research|code|write"}}]"""}]
    ).content[0].text

    subtasks = json.loads(plan)

    # 工作者：执行各子任务
    results = {}
    for st in subtasks:
        worker_resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": f"执行以下任务：{st['subtask']}"}]
        ).content[0].text
        results[st["id"]] = worker_resp

    # 编排者：合并结果
    synthesis = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": f"合并以下子任务结果为完整输出：\n{json.dumps(results, ensure_ascii=False)}"}]
    ).content[0].text

    return {"plan": subtasks, "result": synthesis}
```

## 6. Workflow 模式五：Evaluator-Optimizer（评估-优化）

一个 LLM 生成，另一个评估，循环迭代直到满足标准。

```python
def evaluator_optimizer(task: str, max_iterations: int = 3) -> str:
    """生成-评估循环"""
    current_output = ""

    for i in range(max_iterations):
        # 生成器
        gen_prompt = f"任务：{task}" if i == 0 else f"任务：{task}\n上次输出：{current_output}\n改进建议：{feedback}\n请改进。"
        current_output = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            messages=[{"role": "user", "content": gen_prompt}]
        ).content[0].text

        # 评估器
        eval_resp = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            messages=[{"role": "user", "content": f"""评估输出质量（1-10分），给出改进建议。
任务：{task}
输出：{current_output}
格式：SCORE: X\nFEEDBACK: ..."""}]
        ).content[0].text

        score = int(eval_resp.split("SCORE:")[1].split("\n")[0].strip())
        feedback = eval_resp.split("FEEDBACK:")[1].strip() if "FEEDBACK:" in eval_resp else ""

        if score >= 8:
            break

    return current_output
```

## 7. 自主 Agent 模式（ReAct 循环）

Agent 在循环中自主决定使用工具，直到完成任务。

```python
import anthropic

tools = [
    {"name": "search", "description": "搜索信息",
     "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}}},
    {"name": "calculator", "description": "数学计算",
     "input_schema": {"type": "object", "properties": {"expression": {"type": "string"}}}},
]

def autonomous_agent(task: str, max_turns: int = 10) -> str:
    """自主 Agent：ReAct 循环"""
    messages = [{"role": "user", "content": task}]

    for _ in range(max_turns):
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            tools=tools,
            messages=messages,
        )

        # 无工具调用 → 任务完成
        if response.stop_reason == "end_turn":
            return next(b.text for b in response.content if b.type == "text")

        # 执行工具调用
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result", "tool_use_id": block.id, "content": result
                })
        messages.append({"role": "user", "content": tool_results})

    return "达到最大轮次限制"
```

## 8. 决策框架：何时用 Workflow vs Agent

```
需求明确、流程固定？ ──→ YES ──→ Workflow
        │
        NO
        ↓
需要动态决策？ ──→ YES ──→ Agent
        │
        NO
        ↓
从最简单的 Prompt Chaining 开始

选择 Workflow 模式：
├─ 线性流程 → Prompt Chaining
├─ 输入分类 → Routing
├─ 可并行   → Parallelization
├─ 动态分解 → Orchestrator-Workers
└─ 需迭代   → Evaluator-Optimizer
```

| 维度       | Workflow           | Agent              |
|-----------|--------------------|--------------------|
| 可预测性   | 高                 | 低                 |
| 灵活性     | 低                 | 高                 |
| 调试难度   | 简单               | 复杂               |
| 成本控制   | 容易               | 需要限制轮次        |
| 适用场景   | 明确流程、高可靠性   | 开放式、探索性任务   |

## 9. 2026 新模式：Managed Agents 与 Agent Teams

> 🔄 更新于 2026-05-21

<!-- version-check: Claude Managed Agents (Dreaming, Outcomes, Multi-Agent Orchestration), Code with Claude 2026-05-06, checked 2026-07-08 -->

### 9.1 Claude Managed Agents（托管 Agent 运行时）

Anthropic 推出 Managed Agents，将 Agent 从"开发者自建 harness"升级为"平台托管运行时"。核心理念：将"大脑"（模型）与"双手"（harness）解耦，harness 编码的假设会随模型进步而过时，因此需要稳定的接口层。来源：[Anthropic Engineering - Decoupling the brain from the hands](https://www.anthropic.com/engineering/managed-agents)

```
传统模式（自建 Harness）:
  开发者 → 构建 Agent 运行时 → 管理工具/环境/会话/错误恢复
  问题：harness 假设随模型升级而过时，维护成本高

Managed Agents 模式（托管运行时）:
  开发者 → 定义 Agent（指令 + 工具 + 约束）→ Anthropic 托管运行时
  提供：Agent 定义、云环境、会话管理、事件流、内置工具
  优势：harness 由 Anthropic 维护，随模型升级自动优化
```

> 🔄 更新于 2026-05-21

### 9.2 Managed Agents 新能力（Code with Claude 2026-05-06）

Anthropic 在 Code with Claude 大会（2026-05-06 旧金山）上发布了 Managed Agents 的三大新能力。来源：[Anthropic 公告](https://claude.com/blog/new-in-claude-managed-agents) | [9to5Mac 报道](https://9to5mac.com/2026/05/07/anthropic-updates-claude-managed-agents-with-three-new-features/)

**Dreaming（研究预览）**

Agent 在会话间"做梦"——离线回顾历史 session，提取模式，自动优化长期记忆：

```
Dreaming 工作流：
  ┌─────────────────────────────────────────────┐
  │  Session 1 → Session 2 → ... → Session N    │
  └──────────────────┬──────────────────────────┘
                     │ 离线触发
                     ▼
  ┌─────────────────────────────────────────────┐
  │              Dreaming 进程                    │
  │  1. 回顾历史 session                         │
  │  2. 提取重复模式和用户偏好                    │
  │  3. 整理/删除过时记忆                         │
  │  4. 生成改进建议                              │
  └──────────────────┬──────────────────────────┘
                     │ 更新记忆
                     ▼
  ┌─────────────────────────────────────────────┐
  │  Session N+1（更好的上下文理解）              │
  └─────────────────────────────────────────────┘
```

控制粒度：
- **自动模式**：Dreaming 直接更新 Agent 记忆，无需人工干预
- **审核模式**：Dreaming 生成变更建议，开发者审核后才生效

**Outcomes（质量评分）**

为 Agent 执行结果定义成功标准，形成评测闭环：

```python
# 概念示例：定义 Agent 的 Outcome 评分标准
outcome_config = {
    "success_criteria": [
        "代码通过所有测试",
        "PR 描述清晰完整",
        "无安全漏洞引入"
    ],
    "scoring": "auto",  # 自动评分
    "feedback_loop": True  # 评分结果反馈给 Dreaming
}
```

**Multiagent Orchestration（多 Agent 编排）**

原生支持 Lead Agent 编排多个 Specialist Agent：

```
多 Agent 编排架构：
  ┌─────────────────────────────────────┐
  │       Lead Agent（编排者）            │
  │  接收任务 → 分解 → 分配 → 汇总       │
  └──────┬──────────┬──────────┬────────┘
         │          │          │
  ┌──────┴──┐ ┌────┴────┐ ┌───┴─────┐
  │ Agent A │ │ Agent B │ │ Agent C │
  │ 代码审查 │ │ 测试编写 │ │ 文档生成 │
  └─────────┘ └─────────┘ └─────────┘
```

配套发布：
- **Webhooks**：Agent 执行完成后通知外部系统
- **Cloudflare Sandboxes**：每个 Agent 会话运行在独立沙箱中（Workers 控制面拉起 microVM 或 V8 Isolate）
- **Claude Finance**：10 个预构建金融 Agent 模板

来源：[Code with Claude 大会](https://claude.com/code-with-claude/san-francisco) | [Cloudflare 博客](https://blog.cloudflare.com/claude-managed-agents)

### 9.3 Claude Code Agent Teams

随 Opus 4.6 发布（2026-02），Claude Code 支持在一个会话中生成独立的 Agent 队友。来源：[Claude Code Agent Teams Guide](https://lushbinary.com/blog/claude-code-agent-teams-multi-agent-development-guide/)

```
Agent Teams 架构：
  ┌─────────────────────────────────────┐
  │          Lead Agent（主 Agent）       │
  │  负责规划、分解任务、协调队友          │
  └──────────┬──────────┬───────────────┘
             │          │
    ┌────────┴──┐  ┌────┴────────┐
    │ Teammate A│  │ Teammate B  │
    │ 研究/调研  │  │ 编码/实现    │
    └─────┬─────┘  └──────┬──────┘
          │               │
          └───── 邮箱通信 ──┘
          （peer-to-peer mailbox）
```

关键特性：
- 每个 Teammate 是独立的 Agent 实例，有自己的上下文和工具
- 通过 peer-to-peer 邮箱机制通信，非中央控制
- Lead Agent 可以动态创建和分配 Teammate
- 适用于大型代码库的并行开发任务
## 🎬 推荐视频资源

- [DeepLearning.AI - Agentic AI with Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/) — Agentic设计模式全面讲解（免费）
- [DeepLearning.AI - AI Agentic Design Patterns with AutoGen](https://www.deeplearning.ai/short-courses/ai-agentic-design-patterns-with-autogen/) — 设计模式实战（免费）
### 📺 B站（Bilibili）
- [吴恩达 - Agentic AI设计模式中文字幕](https://www.bilibili.com/video/BV1Bz421B7bG) — Agentic设计模式讲解

### 🎓 DeepLearning.AI（免费）
- [Agentic AI with Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/) — Agentic AI完整课程
