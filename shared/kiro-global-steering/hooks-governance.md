---
inclusion: manual
---

# Kiro Hook 治理规范

> 多工作区（multi-root workspace）下，所有打开工作区的 `.kiro/hooks/*.kiro.hook` 会被统一加载。
> 这意味着 Brand Agent 里定义的 `*.py` hook 也会在博客站点编辑 Python 时触发——即"外溢"。
> 本文档规定如何设计、命名和编写 hook，确保作用域清晰、无外溢。

## 三层命名契约

根据命名前缀一眼看出作用域和是否需要路径守卫：

| 前缀 | 作用域 | 存放位置 | 是否需要路径短路 |
|------|--------|----------|------------------|
| `guard-` | 跨项目通用 | `~/.kiro/hooks/` | 否（本身就是全局） |
| `project-` | 项目专属 | `<project>/.kiro/hooks/` | **必须** |
| `tool-` | 手动触发工具 | `<project>/.kiro/hooks/` | 否（userTriggered 不会外溢） |

## 项目专属 hook 必须加路径短路

### askAgent 类（prompt 首行声明）

```
⚠️ **作用域短路**：首先查看目标文件的绝对路径。如果路径**不包含 `<项目关键字>`**，立即回复 `✅ 跳过（非本项目文件）` 并结束，不做任何后续检查。

---
（原本的检查内容）
```

关键字选择工作区目录名中的独特部分，例如 `博客站点`、`Brand Agent`、`技术笔记`、`AI Payment`。

### runCommand 类（脚本首行判断）

```python
import json, os, sys
raw = os.environ.get("KIRO_TOOL_INPUT", "")
if raw:
    data = json.loads(raw)
    target = data.get("path") or data.get("targetFile") or ""
    # 不在本项目路径下直接放行
    PROJECT_KEY = "项目关键字"
    if target and PROJECT_KEY not in os.path.abspath(target):
        sys.exit(0)
```

## User 级 hook 注意事项

User 级 hook 的 `runCommand` 从任意工作区的 `cwd` 执行，所以：

- **不能用相对路径** `.kiro/hooks/lib/xxx.py`
- **必须用绝对路径** `python3 $HOME/.kiro/hooks/lib/xxx.py`

## 避免双触发

如果同一功能的 hook 既在 user 级又在 project 级存在，会触发两次。
迁移到 user 级后，项目级副本应设置 `enabled: false`，并在 description 中注明已迁移。

## Hook schema 快查

```json
{
  "enabled": true,
  "name": "显示名称（emoji + 描述）",
  "description": "做什么 + 作用域",
  "version": "语义版本",
  "when": {
    "type": "fileEdited | fileCreated | fileDeleted | preToolUse | postToolUse | userTriggered | preTaskExecution | postTaskExecution | promptSubmit | agentStop",
    "patterns": ["文件事件才需要，glob"],
    "toolTypes": ["preToolUse/postToolUse 才需要：read | write | shell | web | spec | *"]
  },
  "then": {
    "type": "askAgent | runCommand",
    "prompt": "askAgent 才需要",
    "command": "runCommand 才需要"
  }
}
```

## 新建 hook 的 checklist

- [ ] 前缀正确：`guard-` / `project-` / `tool-`
- [ ] 如果是 project 前缀，prompt 或脚本首行有路径短路
- [ ] 如果是 user 级，runCommand 用了 `$HOME` 绝对路径
- [ ] description 明确说明了作用域
- [ ] 没有与 user 级同功能 hook 冲突（若冲突则禁用 project 副本）
