---
inclusion: fileMatch
fileMatchPattern: 'learning-notes/briefings/**'
---

# 📰 简报通用规则（v3 流水线架构）

本文件定义三个简报 hook（AI Agent / 国内科技 / 国际科技）共享的流程和规范。

**自动加载**：通过 `fileMatch` 自动绑定 `learning-notes/briefings/**` 下的所有文件。
**未命中 fileMatch 时**：运行 `python3 scripts/briefing-tools.py show-rules` 显式拉取。

---

## 架构（v3）

```
┌───────────────────────────────────────────────────────────────┐
│ 1. ingest       一次抓全部 RSS 源 → pool.jsonl                  │
│                 （自动跳过熔断源：连续 N 天失败的自动不抓）      │
│ 2. classify     规则打标 + 评分 + main_topic → classified.jsonl │
│                 （可选 LLM 批量分类；失败自动退回规则）           │
│ 3. candidates   按主题分流 → candidates.{topic}.jsonl            │
│    └─ 过滤：已发布 / 其他主题已写 md / 低分 / 可选语义去重       │
│    └─ 可选 require-main-topic 排除多主题歧义                    │
│ 4. [agent]      subagent 读候选 + web search → 写 md            │
│ 5. validate     校验 md 完整性（缺 H1/H3/链接即 fail）           │
│ 6. register     通过校验后登记 URL 到 published-index            │
│ 7. cleanup      （可选）删除早于 N 天的 run 目录                 │
└───────────────────────────────────────────────────────────────┘
```

**配置外置**：所有源、关键词、阈值都在 `.kiro/briefings/config.json`。改源不用动代码。

**topic 是 tag 不是 bucket**：一条可同时带 `ai-agent + global-tech`。main_topic 根据 priority 决定（默认 ai-agent > china-tech > global-tech），curate 阶段可选 `--require-main-topic` 排除多主题歧义。

---

## 通用流程

### Phase 0：幂等性检查

1. 确认今天日期
2. 检查 `learning-notes/briefings/{topic}/YYYY/MM/YYYY-MM-DD.md`：
   - **已存在** → 告知用户"今日已完成"并结束
   - **不存在** → 继续

### Phase 1：确定性流水线

```bash
python3 scripts/briefing-tools.py run-all
```

串行跑 ingest → classify → candidates → cleanup。产出：
- `.kiro_tmp/briefings/runs/YYYY-MM-DD/pool.jsonl`
- `.kiro_tmp/briefings/runs/YYYY-MM-DD/classified.jsonl`
- `.kiro_tmp/briefings/runs/YYYY-MM-DD/candidates.{topic}.jsonl` × 3
- `.kiro_tmp/briefings/runs/YYYY-MM-DD/metrics.json`
- `.kiro_tmp/briefings/runs/YYYY-MM-DD/candidates.{topic}.stats.json` × 3

**流水线幂等**：重复跑 `run-all` 不会污染简报文件，只覆盖 run 目录。

### Phase 2：Web Search 补充

候选集来自 RSS + HN API。Web search 补充长尾官博、论文、安全动态。关键词见 `.kiro/briefings/prompts/curate.{topic}.md`。

**搜索规则**：禁止硬编码年月，用当前日期动态生成。

### Phase 3：精选

**优先**：candidates.{topic}.jsonl 中 score.total ≥ 15 的条目（已打分）
**其次**：web search 结果按人工判断
**评分维度（脚本自动）**：
- 时效性：48h 内 5 / 一周内 3 / 更早 1
- 一手性：官博/研究 5 / 垂媒 4 / 转载 3（可被 `score_overrides` per-topic 覆盖）
- 相关性：命中 Walter 偏好栈（LangGraph/MCP/CrewAI/RAG 等）+2
- 实用性：明确 release/发布/开源动作 +1

### Phase 4：生成简报

使用各自 `.kiro/briefings/prompts/curate.{topic}.md` 中的写作模板。**评分明细 / 标签 / 采集统计不写入正文**。

### Phase 5：写入 + 校验 + 登记 + 分发

```bash
# 1. fs_write 到 learning-notes/briefings/{topic}/YYYY/MM/YYYY-MM-DD.md

# 2. 事务性校验（缺头、无正文、无链接都会 fail exit 1）
python3 scripts/briefing-tools.py validate \
    learning-notes/briefings/{topic}/YYYY/MM/YYYY-MM-DD.md

# 3. 通过后登记
python3 scripts/briefing-tools.py register --topic {topic}
python3 scripts/briefing-tools.py index --topic {topic}
python3 scripts/briefing-tools.py notify --topic {topic}
```

**顺序重要**：validate → register。register 内部也会校验，但前置校验让失败时立刻停手、不污染索引。

---

## 配置文件

`.kiro/briefings/config.json` — 所有可调配置：

| 字段 | 含义 |
|------|------|
| `freshness_hours` | 采集时效过滤窗口 |
| `rss_sources[]` | RSS 源（name / url / topic_hints / 可选 timeout） |
| `classify_rules{}` | per-topic 关键词字典 |
| `noise_keywords[]` | 低质关键词（噪声惩罚） |
| `score_overrides{}` | per-topic source 权重覆盖 |
| `main_topic_rules.priority` | 多 tag 冲突时的优先级 |
| `source_circuit_breaker.fail_threshold_days` | 熔断阈值（默认 3） |
| `run_retention_days` | run 目录保留天数 |
| `published_index_retention_days` | 已发布索引保留天数 |
| `llm_classify.enabled` | 开启 LLM 批量分类（需 ANTHROPIC_API_KEY） |
| `semantic_dedup.enabled` | 开启 shingle-based 语义去重 |

---

## 索引与事实来源

| 文件 | 含义 | 维护者 |
|------|------|--------|
| `.published-index.json` | 已写入简报 md 的 URL，跨天去重真值 | `register` + `rebuild-index` |
| `.kiro_tmp/briefings/source-health.json` | 源健康记录（连续失败天数等） | `ingest` 自动 |
| `.kiro_tmp/briefings/runs/YYYY-MM-DD/` | 当日流水线产物 | `ingest` / `classify` / `candidates` |
| `.dedup-index.json`（旧 v1） | 已废弃，保留备份可删除 | — |

### 从零重建

```bash
python3 scripts/briefing-tools.py rebuild-index [--days 60]
```

### 源健康查看 / 重置

```bash
python3 scripts/briefing-tools.py health
python3 scripts/briefing-tools.py health-reset "源名称"
```

---

## 写作原则

- 所有内容用中文，技术术语可用英文
- 每条必须有来源链接，优先一手
- 摘要带分析判断，不搬运
- 关注 Walter 的偏好栈：LangGraph / MCP / CrewAI / Python / TypeScript
- 无高质量内容时诚实说明，不凑数
- 重大事件可用 web_fetch 拉取原文
- **评分 / 标签 / 采集统计不暴露给读者**

---

## 异常处理

- web search / web_fetch / 文件写入失败 → 追加到 `learning-notes/briefings/.errors.log`
- RSS 源失败 → 自动记录到 `source-health.json`，连续 N 天失败自动熔断
- validate 失败 → 不要执行 register，通知用户修复

---

## 测试

```bash
python3 -m unittest discover scripts/tests -v
```

67+ 单元测试覆盖：分类、评分、去重、候选集过滤、源健康熔断、原子写入、md 校验、retention、end-to-end 集成。

---

## Prompt 文件定位

- `.kiro/briefings/prompts/_shared.md` — 共享 Phase 框架
- `.kiro/briefings/prompts/curate.{topic}.md` — 各主题差异化
- 修改模板 / 风格 / 搜索词 → 改 prompt md，不改 hook json
- 修改源 / 规则 / 阈值 → 改 `.kiro/briefings/config.json`
- 修改代码逻辑 → 改 `scripts/briefing_tools/*.py`，跑测试
- hook json 保持极薄（10 行），只负责"读 prompt + 触发 subagent"
