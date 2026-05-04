# Harness Engineering 完整指南
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 从 Prompt 到 Harness 的演进

```
┌─────────────────────────────────────────────────────────────┐
│                    工程方法论演进                               │
├──────────────────┬──────────────────┬───────────────────────┤
│ Prompt Eng.      │ Context Eng.     │ Harness Eng.          │
│ (2023-2024)      │ (2025)           │ (2026)                │
├──────────────────┼──────────────────┼───────────────────────┤
│ 写好一句指令      │ 给对的信息        │ 建好整个系统           │
│ 单次交互         │ 信息编排          │ 自主循环              │
│ 人驱动           │ 人+Agent 协作     │ Agent 驱动，人监督     │
├──────────────────┼──────────────────┼───────────────────────┤
│ "往右转"         │ 给地图和路标       │ 缰绳+围栏+自动导航    │
│                  │                  │ 马自己跑到终点         │
├──────────────────┼──────────────────┼───────────────────────┤
│ 关注：措辞        │ 关注：RAG/记忆/工具│ 关注：约束/反馈/自愈   │
│ 产出：单次回答    │ 产出：增强回答     │ 产出：持续交付的代码    │
└──────────────────┴──────────────────┴───────────────────────┘
```

## 2. 什么是 Harness Engineering

OpenAI 于 2026 年 2 月发布论文，描述了一个实验：3 名工程师从空仓库开始，
不写一行手动代码，完全由 Codex Agent 生成，5 个月产出约 100 万行生产代码，
日均 3.5 个 PR/人，且随团队扩大效率不降反升。

**Harness = 让 Agent 高效工作的脚手架系统**

```
Harness 的组成：
├── 仓库结构（Repository as Context）
│   └── 目录命名、模块划分、注释 → Agent 的"地图"
├── 上下文管理（Context Management）
│   └── Map 文件、执行计划、设计规范 → 精简而非堆砌
├── 架构约束（Architectural Constraints）
│   └── 依赖规则、分层结构 → CI 测试强制执行
├── 持续质量管理（Continuous Quality）
│   └── 后台 Agent 定期扫描、自动修复 → 代码"垃圾回收"
└── Agent 可观测性（Observability for Agents）
    └── 日志、指标、链路追踪 → Agent 能读自己的运行结果
```

核心转变：**工程师的工作不再是写代码，而是创造让 Agent 能可靠写出好代码的条件。**

## 3. 五大实践

### 3.1 仓库即上下文（Repository as Context）

```
传统做法：
  代码在仓库，知识在人脑/Slack/Confluence

Harness 做法：
  一切 Agent 需要知道的，都在仓库里
  ├── 架构决策 → ADR 文件（Architecture Decision Records）
  ├── 领域概念 → 目录结构和命名约定
  ├── 编码规范 → 可执行的 lint 规则
  └── 业务逻辑 → 代码注释和类型定义

原则：如果 Agent 在仓库里找不到，那它就不知道。
```

### 3.2 上下文管理：给地图，不给手册

```
❌ 错误做法：一个 5000 行的 CLAUDE.md / steering 文件
✅ 正确做法：三类精简文档，交叉引用

1. Map（地图）— 系统导航和模块关系
   "用户服务在 src/user/，依赖 src/common/auth"

2. Execution Plan（执行计划）— 具体任务规范
   "实现用户注册 API，输入验证用 Zod，存储用 Prisma"

3. Design Spec（设计规范）— 架构指导原则
   "所有 API 返回统一 Result<T> 格式，错误码见 errors.ts"

关键：每个文档要短（< 200 行），结构化，可机器解析。
```

### 3.3 架构约束机械化执行

```
❌ 靠人 Code Review 维护架构规范
✅ 靠 CI 测试自动拒绝违规代码

示例：分层依赖规则
  Types → Config → Repository → Service → Runtime → UI
  依赖只能向下，不能向上

强制方式：结构测试
```

```python
# tests/test_architecture.py — 架构约束测试
import ast
import os

LAYER_ORDER = ["types", "config", "repository", "service", "runtime", "ui"]

def test_no_upward_dependency():
    """确保依赖方向正确：上层不能导入下层"""
    violations = []
    for root, _, files in os.walk("src"):
        for f in files:
            if not f.endswith(".py"):
                continue
            filepath = os.path.join(root, f)
            current_layer = get_layer(filepath)
            if current_layer is None:
                continue
            with open(filepath) as fh:
                tree = ast.parse(fh.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    imported_layer = get_layer_from_module(node.module)
                    if imported_layer and LAYER_ORDER.index(imported_layer) > LAYER_ORDER.index(current_layer):
                        violations.append(f"{filepath}: {current_layer} → {imported_layer}")
    assert not violations, f"架构违规:\n" + "\n".join(violations)
```

```
Agent 写了违规代码 → CI 测试失败 → Agent 看到失败信息 → 自动修复
这就是"机械化约束"的力量：不靠人提醒，靠系统拒绝。
```

### 3.4 持续质量管理（代码垃圾回收）

```
传统：技术债累积 → 某天大规模重构 → 痛苦
Harness：后台 Agent 持续小规模清理 → 债务永远不累积

实践方式：
├── 定时任务：每天后台 Agent 扫描代码质量
├── 自动 PR：发现问题自动开小范围修复 PR
├── 人工审核：每个 PR 小到 1 分钟内可审完
└── 质量评分：维护各模块的质量分数看板
```

```yaml
# .github/workflows/quality-sweep.yml
name: Quality Sweep
on:
  schedule:
    - cron: '0 2 * * *'  # 每天凌晨 2 点

jobs:
  sweep:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run quality scan
        run: |
          # Agent 扫描并自动修复
          claude --pipe "扫描 src/ 目录，找出不符合编码规范的代码，
                         为每个问题创建独立的修复 commit"
      - name: Create PR
        uses: peter-evans/create-pull-request@v6
        with:
          title: "chore: automated quality sweep"
          branch: quality-sweep/${{ github.run_id }}
```

### 3.5 Agent 可观测性

```
传统：人看日志排查问题
Harness：Agent 读自己的日志，自己排查和修复

实践：
├── 结构化日志（JSON 格式，Agent 可解析）
├── 错误追踪（Sentry/类似工具，Agent 可查询）
├── 性能指标（Agent 能看到自己改动的性能影响）
└── 测试报告（Agent 能读 CI 失败的详细信息）
```

## 4. 自动循环：Agent 自主运转直到符合预期

这是你提到的第三个问题的核心。在 Harness Engineering 中，这个模式叫做
**Autonomous Agent Loop（自主 Agent 循环）**：

```
┌──────────────────────────────────────────────────┐
│              Autonomous Agent Loop                │
│                                                   │
│   ┌─────────┐                                    │
│   │ 任务输入 │ ← 人类提供需求/Issue               │
│   └────┬────┘                                    │
│        ▼                                         │
│   ┌─────────┐                                    │
│   │ Agent   │ ← 读取 Harness（地图/规范/约束）    │
│   │ 写代码   │                                    │
│   └────┬────┘                                    │
│        ▼                                         │
│   ┌─────────┐    ┌──────────┐                    │
│   │ CI 运行  │───>│ 全部通过？ │── 是 ──> 开 PR    │
│   │ 测试/lint│    └────┬─────┘         人审核合并  │
│   └─────────┘         │ 否                       │
│                       ▼                          │
│                  ┌─────────┐                     │
│                  │ Agent   │ ← 读取失败日志       │
│                  │ 自动修复 │                     │
│                  └────┬────┘                     │
│                       │                          │
│                       └──── 回到 CI 运行 ────┘    │
│                                                   │
│   退出条件：                                       │
│   ├── CI 全部通过 → 成功，开 PR                    │
│   ├── 循环超过 N 次 → 失败，通知人类               │
│   └── 遇到架构级问题 → 暂停，请求人类决策          │
└──────────────────────────────────────────────────┘
```

这个模式在不同工具中的实现：

```
OpenAI Codex：原生支持，Agent 提交 → CI 反馈 → 自动修复循环
Claude Code：通过 CLAUDE.md + CI hooks 实现
Kiro：通过 Specs + Hooks + Steering 实现
Cursor：通过 .cursorrules + 终端命令实现
```

## 5. 与 Kiro 的整合方案

Kiro 的功能天然对应 Harness 的五大实践：

```
Harness 实践              Kiro 对应功能
─────────────────────────────────────────
仓库即上下文              Steering 文件（.kiro/steering/）
上下文管理（地图）         Specs（需求→设计→任务）
架构约束机械化            Hooks（preToolUse/postToolUse）
持续质量管理              Hooks（fileEdited → 自动 lint/test）
Agent 可观测性            Hooks（agentStop → 运行测试验证）
```

### 5.1 Steering 作为 Harness 地图

```markdown
# .kiro/steering/architecture.md
# inclusion: auto

## 项目架构
分层架构：types → config → repository → service → api
依赖方向：只能向下依赖，不能反向

## 编码规范
- 所有函数必须有类型注解
- 公共 API 必须有 docstring
- 错误处理使用 Result 模式，不用裸 try-catch
- 测试文件与源文件同目录，命名 test_*.py

## 命名约定
- 文件名：snake_case
- 类名：PascalCase
- 常量：UPPER_SNAKE_CASE
- API 路由：kebab-case
```

### 5.2 Hooks 作为反馈循环

```json
// .kiro/hooks/auto-test.hook
{
  "name": "Auto Test on Edit",
  "version": "1.0.0",
  "when": {
    "type": "fileEdited",
    "patterns": ["*.py", "*.ts"]
  },
  "then": {
    "type": "runCommand",
    "command": "pytest -x --tb=short"
  }
}
```

```json
// .kiro/hooks/architecture-check.hook
{
  "name": "Architecture Guard",
  "version": "1.0.0",
  "when": {
    "type": "preToolUse",
    "toolTypes": ["write"]
  },
  "then": {
    "type": "askAgent",
    "prompt": "检查这次写入是否违反分层架构规则：types → config → repository → service → api。如果违反，拒绝写入并说明原因。"
  }
}
```

```json
// .kiro/hooks/quality-verify.hook
{
  "name": "Quality Verify After Task",
  "version": "1.0.0",
  "when": {
    "type": "postTaskExecution"
  },
  "then": {
    "type": "runCommand",
    "command": "pytest && ruff check . && mypy src/"
  }
}
```

### 5.3 Specs 作为执行计划

```markdown
# .kiro/specs/user-auth/design.md

## 需求
实现用户认证模块，支持注册、登录、Token 刷新

## 设计
- 使用 JWT Token（access + refresh）
- 密码使用 bcrypt 加密
- Token 存储在 Redis

## 任务
- [ ] 创建 User 模型和数据库迁移
- [ ] 实现注册 API（POST /api/auth/register）
- [ ] 实现登录 API（POST /api/auth/login）
- [ ] 实现 Token 刷新 API（POST /api/auth/refresh）
- [ ] 编写完整测试用例
- [ ] 更新 API 文档

## 约束
- 参考 #[[file:src/common/auth/types.py]] 中的类型定义
- 遵循 #[[file:.kiro/steering/architecture.md]] 中的分层规则
```

## 6. 构建你的 Harness 检查清单

```
□ 仓库结构
  □ 目录命名清晰，反映业务领域
  □ ADR（架构决策记录）在仓库内
  □ README 精简，面向 Agent 可读

□ 上下文文档
  □ Steering/CLAUDE.md 短于 200 行
  □ 分为 Map / Plan / Spec 三类
  □ 交叉引用，不重复

□ 架构约束
  □ 分层规则有对应的 CI 测试
  □ 依赖方向有自动检查
  □ 命名规范有 lint 规则

□ 反馈循环
  □ 文件保存自动运行测试
  □ 写操作前检查架构合规
  □ 任务完成后自动验证

□ 质量管理
  □ 定期自动扫描代码质量
  □ 小范围自动修复 PR
  □ 质量指标可追踪

□ 可观测性
  □ 结构化日志（JSON）
  □ CI 失败信息 Agent 可读
  □ 性能指标可查询
```

## 7. 关键认知

```
1. Harness Engineering 不是新技术，是新方法论
   它把已有的工程实践（CI/CD、lint、测试、文档）
   重新组织，让 Agent 而非人类成为主要消费者

2. 投入产出比极高
   前期花 1-2 周搭建 Harness
   后续每个任务的 Agent 产出质量提升数倍

3. 核心公式
   Agent 产出质量 = f(模型能力 × Harness 质量)
   模型能力你控制不了，Harness 质量你完全可以控制

4. 人的角色转变
   写代码 → 设计约束
   Debug → 设计反馈循环
   Code Review → 维护 Harness
```
## 8. LangChain Harness Profile：按模型定制 Harness

> 🔄 更新于 2026-05-04

<!-- version-check: LangChain Deep Agents Harness Profile, checked 2026-05-04 -->

LangChain 于 2026 年 4 月 29 日为 Deep Agents 引入 **Harness Profile** 机制，核心发现：**同一模型在不同 Harness 中表现差异巨大**。

### 性能数据（tau2-bench 子集）

| 模型 | 默认 Harness | 定制 Profile | 提升 |
|------|-------------|-------------|------|
| GPT 5.3 Codex | 33% | 53% | +20 分 |
| Claude Opus 4.7 | 43% | 53% | +10 分 |

### Profile 定制内容

- **OpenAI Codex**：工具替换（`file_edit` → `apply_patch`）、工具命名（`execute` → `shell_command`）、批量并行调用提示
- **Claude Opus**：工具结果反思提示、主动调查而非凭记忆推理

### 使用方式

```python
from deepagents import create_deep_agent

# Profile 自动按模型应用
agent = create_deep_agent(
    model="google_genai:gemini-3.1-pro-preview",
    tools=[internet_search],
    system_prompt=research_instructions,
)
```

自定义 Profile（YAML）：

```yaml
# openai.yaml
base_system_prompt: You are helpful.
system_prompt_suffix: Respond briefly.
excluded_tools:
  - execute
  - grep
excluded_middleware:
  - SummarizationMiddleware
```

### 关键启示

```
Agent 产出质量 = f(模型能力 × Harness 质量)

Harness Profile 证明了：
├─ 提示词差异可以带来 10-20 分的性能提升
├─ 工具命名和配置对模型表现有显著影响
├─ 同一模型在不同 Harness 中排名可以从垫底到前列
└─ Harness 工程是 Agent 性能优化的新维度
```

- **来源**：[LangChain Blog](https://www.langchain.com/blog/tuning-deep-agents-different-models)

## 🎬 推荐视频资源

- [DeepLearning.AI - Agentic AI with Andrew Ng](https://www.deeplearning.ai/courses/agentic-ai/) — 包含Harness Engineering理念（免费）
- [OpenAI - Harness Engineering Blog](https://openai.com/index/harness-engineering) — OpenAI官方Harness Engineering文章
