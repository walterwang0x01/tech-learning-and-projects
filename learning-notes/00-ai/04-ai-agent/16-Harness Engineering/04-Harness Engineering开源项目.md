# Harness Engineering 开源项目
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

Harness Engineering 从理论走向实践，多个开源项目帮助快速落地。

```
理论基础                  开源实现                框架集成
OpenAI 论文 ──────→ ai_harness_engineering ──→ LangChain Deep Agents
nxcode 指南              agent-harness
                         claude-code-harness
```

## 2. LangChain Deep Agents + Harness

LangChain 官方博客描述了如何将 Harness 模式融入 Deep Agent 架构。

```python
from langgraph.graph import StateGraph, END

harness_config = {
    "map": "src/api/ → src/service/ → src/repository/，依赖只能向下",
    "constraints": ["类型注解", "API 层不直接访问 DB", "Result 模式处理错误"],
    "validators": ["pytest -x", "ruff check .", "mypy src/"],
}

# 带 Harness 的 Agent 图
def build_harness_agent():
    graph = StateGraph(AgentState)
    graph.add_node("load_harness", load_harness_context)
    graph.add_node("execute", execute_task)
    graph.add_node("validate", run_validators)
    graph.add_node("fix", analyze_and_fix)

    graph.set_entry_point("load_harness")
    graph.add_edge("load_harness", "execute")
    graph.add_edge("execute", "validate")
    graph.add_conditional_edges("validate", check_result, {
        "pass": END, "fail": "fix",
    })
    graph.add_edge("fix", "validate")  # 修复后重新验证
    return graph.compile()
```

## 3. ai_harness_engineering — 模式与模板集合

Cobus Greyling 维护的可复用配置和最佳实践。包含四大模式（仓库即上下文、架构约束、
质量扫描、自主循环）和多种模板（CLAUDE.md、Kiro Steering、GitHub Actions）。

```bash
# 快速搭建 Harness — 复制模板到你的项目
git clone https://github.com/cobusgreyling/ai_harness_engineering.git
cp ai_harness_engineering/templates/CLAUDE.md.template ./CLAUDE.md
cp ai_harness_engineering/templates/steering.md.template ./.kiro/steering/architecture.md
cp ai_harness_engineering/patterns/quality-sweep/quality-sweep.yml ./.github/workflows/
```

## 4. agent-harness — 通用 Harness 框架

可编程的 Harness 框架，支持定义约束、验证器和反馈循环。

```python
from agent_harness import Harness, Constraint, Validator

harness = Harness(name="my-project", workspace="./src")

harness.add_constraint(Constraint(
    name="layer-dependency",
    description="API 层不能导入 Repository 层",
    check=lambda files: not any(
        "from repository" in f.content for f in files if f.path.startswith("api/")
    ),
))

harness.add_validator(Validator(
    name="tests", command="pytest -x --tb=short",
    on_fail="将失败信息反馈给 Agent",
))

result = harness.run(agent="claude-code", task="实现用户注册 API", max_iterations=5)
```

## 5. claude-code-harness — Claude Code 专用

```bash
pip install claude-code-harness

# 单任务
claude-harness run --task "实现 /api/users CRUD" --constraints constraints.yaml --max-retries 3

# 批量任务
claude-harness batch --tasks tasks.yaml --parallel 3
```

```yaml
# constraints.yaml
constraints:
  architecture:
    layers: [types, config, repository, service, api]
    direction: downward-only
  code_quality:
    - pytest must pass
    - ruff check must pass
validators:
  - name: unit-tests
    command: pytest -x --tb=short
    required: true
  - name: lint
    command: ruff check .
    auto_fix: ruff check --fix .
```

```yaml
# tasks.yaml — 批量任务（按依赖顺序执行）
tasks:
  - name: user-model
    description: "创建 User 模型"
  - name: user-repository
    description: "实现 UserRepository"
    depends_on: [user-model]
  - name: user-api
    description: "实现 /api/users CRUD"
    depends_on: [user-repository]
```

## 6. 关键资源

```
必读：
├─ OpenAI 论文："Harness engineering: leveraging Codex in an agent-first world"
├─ nxcode 指南：nxcode.io/resources/news/harness-engineering-complete-guide
├─ LangChain 博客：blog.langchain.com/improving-deep-agents-with-harness-engineering/
└─ 本系列：Harness Engineering完整指南.md / Context Engineering详解.md / Kiro Harness实战配置.md
```

## 7. 快速上手路径

```
Day 1：读 OpenAI 论文 + 本系列完整指南，理解五大实践
Day 2：从 ai_harness_engineering 复制模板，配置 CLAUDE.md/Steering
Day 3：配置 CI 验证 + Kiro Hooks，测试 Agent → CI → 修复循环
Day 4+：添加质量扫描、完善架构约束、建立质量指标
```
## 🎬 推荐视频资源

### 📖 官方资源
- [OpenAI - Harness Engineering](https://openai.com/index/harness-engineering) — OpenAI官方文章
- [LangChain - Deep Agents](https://blog.langchain.com/improving-deep-agents-with-harness-engineering/) — LangChain Harness Engineering
- [nxcode - Complete Guide](https://www.nxcode.io/resources/news/harness-engineering-complete-guide-ai-agent-codex-2026) — 完整指南
