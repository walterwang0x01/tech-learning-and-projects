---
inclusion: manual
---

# Kiro Steering + Hook 治理规范

> 多工作区下所有 `.kiro/hooks/*.kiro.hook` 会被统一加载，Brand Agent 的 `*.py`
> hook 也会在博客站点编辑 Python 时触发——即"外溢"。
> 本文档规定如何组合 steering 与 hook，在零/低成本下达成期望行为。

## 核心理念：事前约束优先，事后兜底补足

Kiro 的两类扩展能力各司其职：

| 能力 | 生效时机 | 成本 | 典型用途 |
| --- | --- | --- | --- |
| **steering** | 每轮对话的系统提示词 | 0 token（进入上下文一次） | 让 agent "天生"按规则生成 |
| **hook (runCommand)** | 事件触发 | 0 token（纯脚本） | 确定性规则兜底（格式、路径、危险命令） |
| **hook (askAgent)** | 事件触发 | 每次一轮 LLM | 需要语义判断才能决定的事 |

**原则：能用 steering 约束的不要用 hook 查；能用 runCommand 脚本做的不要用 askAgent。**

## 决策树

```
想达成某种规范/检查
├── agent 写代码/文档时照做即可 → steering（always 或 fileMatch）
├── 需要事件触发（保存、创建、删除）
│   ├── 规则确定（路径、字符串、扩展名） → hook runCommand 脚本
│   ├── 能被 ruff/eslint/markdownlint 覆盖 → 别写 hook，交 pre-commit
│   └── 需要语义判断（代码审查、内容提取） → hook askAgent
└── 用户手动触发工作流 → hook userTriggered
```

## 组合模式（推荐）

### 模式 A：steering 约束 + runCommand 兜底

最常见、最经济。示例：文档规范。

- `doc-maintenance.md` (fileMatch `learning-notes/**/*.md`)：让 agent 写的时候就加 `> Author`
- `check_doc_format.py` (runCommand)：事后 0.01 秒扫一遍，万一 agent 漏了就提醒

### 模式 B：只用 steering

规则是"生成式"的，不存在"外部输入后检查"的场景。示例：项目架构、语言偏好。

### 模式 C：只用 hook askAgent

规则无法用字符串判断，只能靠 LLM 语义。示例：代码审查、简报热点提取。

## 三层命名契约（hook）

| 前缀 | 作用域 | 位置 | 路径短路 |
| --- | --- | --- | --- |
| `guard-` | 跨项目通用 | `~/.kiro/hooks/` | 不需要 |
| `project-` | 项目专属 | `<project>/.kiro/hooks/` | **必须** |
| `tool-` | 手动触发工具 | `<project>/.kiro/hooks/` | 不需要 |

## 项目专属 hook 路径短路写法

> ⚠️ **关键坑**：Kiro IDE 里的工作区显示名（如"📝 博客站点"）和真实磁盘目录名（如 `portfolio`）可能完全不同。
> **PROJECT_KEY 必须用 `os.path.abspath('.')` 查出的真实目录名**，不是 IDE 显示名。
>
> 当前项目对照表（按需更新）：
>
> | IDE 显示名 | 真实目录名 |
> |---|---|
> | 📝 博客站点 | `portfolio` |
> | 🤖 Brand Agent | `personal-brand-agent` |
> | 📚 技术笔记 | `tech-learning-and-projects` |
> | 🏦 AI Payment | `agenzo` |

### askAgent（prompt 首行）

```
⚠️ **作用域短路**：首先查看目标文件绝对路径。如果不包含 `<真实目录名>`，
立即回复 `✅ 跳过（非本项目文件）` 并结束。

---
（原本的检查内容）
```

### runCommand（脚本开头）

```python
PROJECT_KEY = "真实目录名"  # 用 os.path.abspath('.') 查到的实际磁盘名
target = data.get("path") or data.get("targetFile") or ""
if target and PROJECT_KEY not in os.path.abspath(target):
    sys.exit(0)
```

## User 级 hook 注意事项

User 级 `runCommand` 从任意工作区 cwd 执行：

- **禁止相对路径** `.kiro/hooks/lib/xxx.py`
- **必须绝对路径** `python3 $HOME/.kiro/hooks/lib/xxx.py`

## 避免双触发

**规则**：判断两个同名/同功能的 hook 是否真的重复，看**策略**不看名字。

- 两个 hook 都是 WARNING 非阻断、规则一致 → **真重复**，禁用 project 级副本
- 两个 hook 一个 WARNING（user 级）、一个 BLOCKED（project 级）→ **不是重复**，是分层防御，保留

### 当前实际部署

| 层级 | 策略 | 范围 | 实现 |
| --- | --- | --- | --- |
| user 级 | WARNING 非阻断 | 所有工作区 | `~/.kiro/hooks/guard-sensitive-files` + `guard-shell-safety`，打印警告，返回 0 |
| project 级 | 无 | — | 暂未部署 BLOCKED 层，以 user 级 WARNING + agent `safety_guardrails` + 用户确认三重兜底 |

WARNING 层已能覆盖绝大多数误操作风险，硬阻断会在 hook 误报时打断任务，目前不划算。如果某个项目未来出现"LLM 必须被物理拦住"的强需求（比如生产数据库操作、加密资产转账），再按下面的扩展模式单独开 BLOCKED 层。

### 扩展 BLOCKED 层的条件与写法

满足以下全部条件才值得加 project 级 BLOCKED：

- user 级 WARNING + agent 自我审查 已经失效过至少一次
- 误操作后果不可逆（资金、生产数据、线上配置）
- 拦截规则是字符串级确定性，不会误报

实现骨架：

```python
# 在 project 级脚本里，命中规则时：
print(f"BLOCKED: {reason}")
sys.exit(1)  # 非 0 退出码，Kiro 会拒绝原工具调用
```

注意：BLOCKED 层启用后，user 级 WARNING 仍正常运行，两层在目标项目里叠加生效，互不干扰（Kiro 取最严格结果）。

### 历史教训

- **2026-05 版本**错误地写"同名 hook 必须禁用 project 级副本"，把 AI Payment 的严格 BLOCKED 版本当作 user 级 WARNING 版本的重复。
- 紧接着发现 AI Payment 的"BLOCKED 版本"实际代码跟 user 级一模一样（都是 `print("WARNING") + return 0`），根本没兑现硬阻断承诺，只是个闲置副本。
- **2026-05 修正**：删除 AI Payment 里的冷备份，文档改为"当前只有 user 级 WARNING"。BLOCKED 层按需扩展，不提前预设。

## Hook schema 快查

```json
{
  "enabled": true,
  "name": "显示名（emoji + 描述）",
  "description": "做什么 + 作用域",
  "version": "语义版本",
  "when": {
    "type": "fileEdited | fileCreated | fileDeleted | preToolUse | postToolUse | userTriggered | preTaskExecution | postTaskExecution | promptSubmit | agentStop",
    "patterns": ["文件事件专用，glob"],
    "toolTypes": ["preToolUse/postToolUse 专用：read | write | shell | web | spec | *"]
  },
  "then": {
    "type": "askAgent | runCommand",
    "prompt": "askAgent 专用",
    "command": "runCommand 专用"
  }
}
```

## 脚本通用骨架（runCommand）

```python
#!/usr/bin/env python3
from __future__ import annotations
import json, os, sys

PROJECT_KEY = "项目关键字"

def main() -> int:
    raw = os.environ.get("KIRO_TOOL_INPUT", "")
    if not raw:
        return 0
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    path = data.get("path") or data.get("targetFile") or ""
    if not path or PROJECT_KEY not in os.path.abspath(path):
        return 0  # 跨项目短路

    # 在此做确定性检查
    # print("WARNING: xxx") 输出警告（非阻断）
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

## 新建 hook 的 checklist

- [ ] 先问：能否用 steering 代替？能就用 steering
- [ ] 再问：能否用 ruff/eslint/markdownlint 代替？能就交 pre-commit
- [ ] 再问：能否用 runCommand 脚本代替 askAgent？能就改脚本
- [ ] 前缀正确：`guard-` / `project-` / `tool-`
- [ ] `project-` 前缀必须有路径短路
- [ ] user 级 runCommand 用 `$HOME` 绝对路径
- [ ] description 写清楚作用域和实现方式（askAgent 还是脚本）
- [ ] 与 user 级同功能 hook 不双触发
