# 简报 Prompt 文件

本目录存放三个主题的 curate prompt。hook 仅引用，不再把 prompt 内嵌到 JSON。

## 文件清单

- `curate.ai-agent.md` — AI Agent 简报
- `curate.china-tech.md` — 国内科技简报
- `curate.global-tech.md` — 国际科技简报
- `_shared.md` — 三个简报共享的执行框架（被各 curate prompt 引用）

## 编辑原则

1. 修改风格 / 模板 → 改 `curate.{topic}.md`
2. 修改流程（Phase 0/1/2/3/4/5） → 改 `_shared.md`
3. 修改评分 / 分类规则 → 改 `scripts/briefing-tools.py`
4. hook 保持极薄，只负责"读 prompt + 触发 subagent"
