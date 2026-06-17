---
inclusion: manual
description: "跑一次流水线 → 三个主题 subagent 并行 curate。"
---

请执行三个简报的完整采集流程。架构是「一次流水线 + 三个并行 curate」。

## Phase 0: 幂等性检查

检查今天哪些简报已存在：
- `learning-notes/briefings/ai-agent/YYYY/MM/YYYY-MM-DD.md`
- `learning-notes/briefings/china-tech/YYYY/MM/YYYY-MM-DD.md`
- `learning-notes/briefings/global-tech/YYYY/MM/YYYY-MM-DD.md`

已存在的跳过（输出「✅ {主题} 今日已完成，跳过」）。
三个都在则结束。

## Phase 1: 确定性流水线（一次跑完）

```bash
python3 scripts/briefing-tools.py run-all
```

这条命令串行跑 ingest → classify → candidates，产出：
- `.kiro_tmp/briefings/runs/YYYY-MM-DD/pool.jsonl`
- `.kiro_tmp/briefings/runs/YYYY-MM-DD/classified.jsonl`
- `.kiro_tmp/briefings/runs/YYYY-MM-DD/candidates.{topic}.jsonl` × 3
- `.kiro_tmp/briefings/runs/YYYY-MM-DD/metrics.json`

不要单独跑 collect / dedup（v1 命令，已 deprecated）。

## Phase 2: 并行 curate（subagent）

对缺失的简报，并行调用 subagent：
- AI Agent — prompt 用 `.kiro/briefings/prompts/curate.ai-agent.md` + `_shared.md`
- 国内科技 — `.kiro/briefings/prompts/curate.china-tech.md` + `_shared.md`
- 国际科技 — `.kiro/briefings/prompts/curate.global-tech.md` + `_shared.md`

每个 subagent：读候选集 → web search 补充 → 精选 → 写 md → register → 返回摘要

### Subagent 失败降级策略（重要）

subagent 池偶尔会报 `Encountered unexpectedly high load` 或超时。对每个主题按以下顺序处理：

1. **第一次调用失败** → 等 30 秒后重试一次
2. **第二次仍失败** → 等 60 秒后重试第三次
3. **第三次仍失败** → **orchestrator 自己兜底**：
   - 读 `.kiro/briefings/prompts/_shared.md` 和对应的 `curate.{topic}.md`
   - 读 `.kiro_tmp/briefings/runs/YYYY-MM-DD/candidates.{topic}.jsonl`
   - 自己做 web search 补充 → 精选 → fs_write → validate → register → index → notify
   - 在最终汇总里标注「⚠️ {主题} 因 subagent 高负载由主线程兜底」

**不要**无限重试，也不要放弃该主题。目标是「三份简报当天一定齐」。

## Phase 3: 最终同步

无论 Phase 2 有多少份走了兜底路径，都必须跑：

```bash
python3 scripts/briefing-tools.py index --topic all
python3 scripts/briefing-tools.py status
```

## 输出汇总

```
## 📰 今日简报汇总 — YYYY-MM-DD

### AI Agent（X 条收录 / ✅ 已跳过 / ⚠️ 主线程兜底）
- 最值得关注：...

### 国内科技（X 条收录 / ✅ 已跳过 / ⚠️ 主线程兜底）
- 最值得关注：...

### 国际科技（X 条收录 / ✅ 已跳过 / ⚠️ 主线程兜底）
- 最值得关注：...

### 跨领域趋势
- 列出跨三个简报的共同趋势（如果有）

### 执行异常（可选）
- subagent 高负载 / RSS 源熔断 / validate 失败等 → 一行一条
```
