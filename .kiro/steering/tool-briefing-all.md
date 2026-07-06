---
inclusion: manual
description: "跑一次流水线 → 三个主题 subagent 并行 curate → finalize 统一收尾。"
---

请执行三个简报的完整采集流程。架构是「一次流水线 + 三个并行 curate + 一次 finalize」。

## Phase 0: 幂等性检查

```bash
python3 scripts/briefing-tools.py curate-status
```

已存在的跳过。三个都在则结束。

## Phase 1: 确定性流水线（一次跑完）

```bash
python3 scripts/briefing-tools.py run-all
```

## Phase 2: 并行 curate（subagent）

对缺失的简报，并行调用 subagent。每个 subagent：读候选集 → web search → 精选 → render → register。

**subagent 不要跑 index/notify**——由 Phase 3 统一执行。

### Subagent 失败降级

1. 第一次失败 → 等 30 秒重试
2. 第二次失败 → 等 60 秒第三次
3. 第三次仍失败 → orchestrator 兜底，标注「⚠️ 主线程兜底」

## Phase 3: 统一收尾

```bash
python3 scripts/briefing-tools.py finalize --topic all
```

等价于 register(all) + index + notify + status，只推一次 Bark。

## 异常

- 熔断源恢复后：`python3 scripts/briefing-tools.py health-reset "源名称"`
- HN 源 502 时会自动走 Algolia 备用

## 输出汇总

```
## 📰 今日简报汇总 — YYYY-MM-DD
### AI Agent / 国内科技 / 国际科技
### 跨领域趋势
### 执行异常
```
