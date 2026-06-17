---
inclusion: manual
description: "流水线式采集：ingest → classify → candidates → agent curate。"
---

请执行 AI Agent 简报采集。

1. 读取执行框架 `.kiro/briefings/prompts/_shared.md`
2. 读取主题 prompt `.kiro/briefings/prompts/curate.ai-agent.md`
3. 严格按 Phase 0-5 执行

关键命令参考（在 `_shared.md` 中有完整说明）：
- 确认 / 触发流水线：`python3 scripts/briefing-tools.py run-all`
- 读本主题候选集：`.kiro_tmp/briefings/runs/今天日期/candidates.ai-agent.jsonl`
- 写文件 → register → index → notify
