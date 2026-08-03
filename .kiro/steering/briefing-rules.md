---
inclusion: fileMatch
fileMatchPattern: 'learning-notes/briefings/**'
---

# 📰 简报通用规则（v3.1 流水线架构）

本文件定义三个简报 hook（AI Agent / 国内科技 / 国际科技）共享的流程和规范。

**自动加载**：通过 `fileMatch` 自动绑定 `learning-notes/briefings/**` 下的所有文件。
**未命中 fileMatch 时**：运行 `python3 scripts/briefing-tools.py show-rules` 显式拉取。

---

## 架构（v3.1）

```
┌── run-all：确定性流水线，一条命令跑完 ─────────────────────────┐
│ 1. ingest       一次抓全部 RSS 源 → pool.jsonl                  │
│    └─ enabled=false 的源直接不抓（已知长期不可达）              │
│    └─ 熔断源跳过；但距最后失败满 retry_after_days 的放行一次     │
│       half-open 试探，成功即自动恢复                            │
│    └─ 可选 follow-builders 中心化 feed（X 推文 + AI 播客         │
│       transcript，统一打 ai-agent tag）与 supplement 补充源      │
│ 2. classify     规则打标 + 评分 + main_topic → classified.jsonl │
│                 （可选 LLM 批量分类；失败自动退回规则）           │
│ 3. candidates   按主题分流 → candidates.{topic}.jsonl            │
│    └─ 过滤：已发布 / 低分 / 可选语义去重                        │
│    └─ require_main_topic 默认开启 → 三个主题候选集互斥          │
│ 4. cleanup      删除早于 run_retention_days 的 run 目录         │
└───────────────────────────────────────────────────────────────┘
┌── curate：每主题一个 subagent，三个并行 ───────────────────────┐
│ 5. [agent]      读候选 + web search → 写 draft JSON             │
│ 6. render       JSON → md，自动串跑三道校验：                   │
│    └─ validate（缺 H1/H3/链接即 fail，exit 2）                  │
│    └─ skeleton 对比 golden（结构漂移 exit 3）                   │
│    └─ URL 复用检查（跨天 / 跨主题，只警告不阻断）               │
│ 7. register     通过校验后登记 URL 到 published-index            │
└───────────────────────────────────────────────────────────────┘
┌── finalize：orchestrator 跑一次，subagent 不要碰 ──────────────┐
│ 8. finalize     register(all) → index → notify → 待办汇总      │
└───────────────────────────────────────────────────────────────┘
```

**配置外置**：所有源、关键词、阈值都在 `.kiro/briefings/config.json`。改源不用动代码。

**topic 是 tag 不是 bucket**：一条可同时带 `ai-agent + global-tech`。main_topic 根据 priority 决定（默认 ai-agent > china-tech > global-tech）。

**`require_main_topic` 现在默认开启（`candidates_require_main_topic: true`），不再是可选项。** 原因：三个主题**并行** curate 时，candidates 里那条「其他主题今日已写 md」的跨主题去重判据必然失效——subagent 同时在写，互相看不见。只有在候选集生成阶段按 main_topic 做互斥切分才拦得住重复。代价是跨主题条目按 priority 归属，优先级低的主题会少拿到这类内容。**改回 false 必须同时把 curate 改为串行。**

**去重是两层，不是一层**：候选集互斥只管候选集。curate 阶段 web search 补充的链接从未进过候选集，绕过全部过滤，由第 5 步的 URL 复用检查兜底。

---

## 通用流程

### Phase 0：幂等性检查

⚠️ **工作目录必须是 `/Users/administrator/PycharmProjects/tech-learning-and-projects/`**。
简报的所有操作（检查、脚本执行、文件写入）都在此项目下，不在 agenzo 或其他 workspace 下。
多 workspace 环境中容易混淆——**每次执行前先确认 cwd**。

1. 确认今天日期
2. 在 **tech-learning-and-projects** 项目下检查 `learning-notes/briefings/{topic}/YYYY/MM/YYYY-MM-DD.md`：
   - **已存在** → 告知用户"✅ {主题} 今日已完成，跳过"并结束
   - **不存在** → 继续
3. 三个主题都已存在 → 输出汇总后终止，**不执行 run-all**

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

### Phase 5：渲染 + 校验 + 登记 + 分发

不要手写 md，写 BriefingDoc JSON 交给 `render`（schema 见 `scripts/briefing_tools/doc_schema.py`）：

```bash
# 1. 写 draft JSON 到 .kiro_tmp/briefings/runs/YYYY-MM-DD/draft.{topic}.json
# 2. render 产出 md 并自动串跑 validate + skeleton + URL 复用检查
python3 scripts/briefing-tools.py render \
    --json .kiro_tmp/briefings/runs/YYYY-MM-DD/draft.{topic}.json

# 3. 通过后登记（subagent 只做到这一步）
python3 scripts/briefing-tools.py register --topic {topic}
```

**必须处理 render 结尾的「⚠️ N 条 URL 此前已收录」**，这不是可忽略的提示：

- **有实质新进展** → 可保留，但正文要写出新增的是什么，不能把昨天讲过的事换个说法再讲
- **只是同一件事换个说法** → 换来源或弃收该条目
- **`[跨天]` 命中同一主题** → 先核对原文发布日期，这往往说明把一篇旧文当成了今天的新闻（已实际发生过：把 07-10 的 Cloudflare 文章写成「同一天发布」）

判断完改 JSON 重跑 render。

**收尾（orchestrator 跑，subagent 不要碰）**：

```bash
python3 scripts/briefing-tools.py finalize --topic all   # 或 --topic {topic}
```

`finalize` = register → index → notify → status，末尾用分隔线框出**待人工确认块**：URL 复用 / 索引一致性 / 基线异常。无待办时明确输出「✅ 无需人工介入」——所以「没看到警告」和「确实没有警告」不会混淆。每天只需看这一屏。

状态面板里的「📝 今日简报条目」是脚本按结构数出来的。**不要采信 curate agent 自报的条目数**，已多次对不上（漏算自由块区块）。

---

## 配置文件

`.kiro/briefings/config.json` — 所有可调配置：

| 字段 | 含义 |
|------|------|
| `freshness_hours` | 采集时效过滤窗口 |
| `rss_sources[]` | RSS 源（name / url / topic_hints / 可选 timeout / fallback_url） |
| `rss_sources[].enabled` | `false` = 已知长期不可达，不采也不进熔断告警。**与熔断是两种语义**：熔断表示「临时故障待恢复」，停用表示「别再提醒我」。优先级高于 half-open 试探 |
| `classify_rules{}` | per-topic 关键词字典 |
| `noise_keywords[]` | 低质关键词（噪声惩罚） |
| `score_overrides{}` | per-topic source 权重覆盖 |
| `main_topic_rules.priority` | 多 tag 冲突时的优先级 |
| `candidates_require_main_topic` | 候选集互斥切分，当前为 `true`。并行 curate 的前提，详见上方架构说明 |
| `candidates_top_n{}` | per-topic 候选上限（`_default` 兜底）。各主题候选池规模差好几倍，一刀切会让信息密集主题损失太多 |
| `source_circuit_breaker.fail_threshold_days` | 连续失败几天后熔断（当前 `2`） |
| `source_circuit_breaker.retry_after_days` | half-open 试探间隔（当前 `7`）。设 `0` 关闭自愈，退回纯人工 `health-reset` |
| `run_retention_days` | run 目录保留天数 |
| `published_index_retention_days` | 已发布索引保留天数 |
| `llm_classify.enabled` | 开启 LLM 批量分类（`borderline_only` 时只对规则未命中的条目调） |
| `semantic_dedup.enabled` | 开启 shingle-based 语义去重 |
| `follow_builders.enabled` | 拉取 X 推文 + AI 播客 transcript 中心化 feed |
| `supplement_sources{}` | 无 Cookie 社区源（B站 / V2EX 等） |

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
- RSS 源失败 → 自动记录到 `source-health.json`，连续 `fail_threshold_days` 天失败自动熔断
- **熔断会自愈**：熔断源距最后一次失败满 `retry_after_days` 后放行一次 half-open 试探，成功则 `consecutive_failures` 归零、源自动恢复；失败则刷新 `last_fail_date` 重新计时。`health` 命令会显示「N 天后自动试探」。
  ⚠️ 熔断源被跳过时不会调用 `record_source_result`，所以在没有试探机制的旧版里 `consecutive_failures` 会永久冻结在阈值上——**看到熔断告警不要默认它需要人工干预，先看试探提示**
- **判断熔断源是否值得救**：先 `curl -sS -o /dev/null -w "%{http_code}" --max-time 20 <源URL>`。返回 `000`（连接超时）说明网络层不可达，`health-reset` 无用，考虑改用镜像源或设 `enabled: false`；返回 `404` / `301` 是 RSS 路径变了，改 `url` 后再 reset；返回 `200` 才是真临时故障
- validate 失败 → 不要执行 register，通知用户修复
- **不要因为「已经 register 过」而把已知错误留在正文里**。改完重跑 validate + `doctor --fix` 即可，`file_hash` 告警只是提示同步 README，不是错误

---

## 测试

```bash
python3 -m unittest discover scripts/tests -v
```

224 个单元测试覆盖：分类、评分、去重、候选集过滤、源健康熔断与 half-open 自愈、源筛选三分支、URL 复用检查、条目计数、收尾报告、原子写入、md 校验、retention、end-to-end 集成。

**改了逻辑就补测试。** 已经出现过「改了 4 处逻辑只有 1 处有覆盖」的情况，其中推送计数那处的 bug 正是因为 `count_briefing_items` 原本零测试才漏到线上。

**测试里用固定日期 fixture 时必须冻结时间**（`conftest.frozen_now`）。已有两个测试因为按 `datetime.now()` 算 retention 窗口、fixture 日期又是硬编码，随真实日期推移必然失败。

---

## Prompt 文件定位

- `.kiro/briefings/prompts/_shared.md` — 共享 Phase 框架
- `.kiro/briefings/prompts/curate.{topic}.md` — 各主题差异化
- 修改模板 / 风格 / 搜索词 → 改 prompt md，不改 hook json
- 修改源 / 规则 / 阈值 → 改 `.kiro/briefings/config.json`
- 修改代码逻辑 → 改 `scripts/briefing_tools/*.py`，跑测试
- hook json 保持极薄（10 行），只负责"读 prompt + 触发 subagent"
