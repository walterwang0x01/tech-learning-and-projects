---
inclusion: manual
description: "补充采集层生产实践：B站/V2EX 等社区源接入 ingest 流水线。"
---

# 补充采集层（Supplement Sources）

> Agent-Reach 理念的生产落地：**不把交互式 CLI 嵌进 hook**，而是把**可脚本化、无 Cookie** 的能力接入确定性 `run-all`。

## 架构

```
ingest
  ├─ RSS（27 源）
  ├─ follow-builders（X + 播客）
  ├─ HN Algolia 备用
  └─ supplement（B站 / V2EX）  ← 新增
        ↓
   pool.jsonl → classify → candidates → curate
```

- **curate 阶段不再单独搜 B站/V2EX**——候选已在 pool 里。
- **Agent-Reach 可选增强**：本机若装了 `bili-cli`，supplement 自动优先 CLI（绕过 API 412）。

## 配置

`.kiro/briefings/config.json` → `supplement_sources`：

| 源 | 默认 | 说明 |
|----|------|------|
| bilibili | on | 国内科技/AI 视频；服务器 412 时装 `bili-cli` |
| v2ex | on | 开发者社区热点；hot + programmer/cloud/create |

## 运维

```bash
# 查看 supplement 是否进 pool
python3 scripts/briefing-tools.py run-all
# 日志行：📎 supplement: N 条 (...)

# B站持续失败时（412）
pip install agent-reach   # 或单独装 bili-cli
agent-reach doctor

# 健康与熔断
python3 scripts/briefing-tools.py health
```

## 不接入 supplement 的源（留给 curate / Agent-Reach 交互）

- 小红书、Twitter 搜索、Reddit — 需 Cookie，不适合无人值守 ingest
- YouTube 字幕 — 适合 curate 阶段按需深读单条链接
