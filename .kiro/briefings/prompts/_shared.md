# 简报执行框架（共享）

> 本文件定义三个简报 hook 共享的 Phase 流程。
> 三个 `curate.{topic}.md` 仅关注「主题差异化」部分：web search 关键词、写作模板、风格约束。

---

## 工作目录

`/Users/administrator/PycharmProjects/tech-learning-and-projects/`
所有相对路径以此为基准。通用规则见 `.kiro/steering/briefing-rules.md`（命中 `learning-notes/briefings/**` 自动加载）。

---

## Phase 0: 幂等性检查

⚠️ **所有检查和操作必须在工作目录 `/Users/administrator/PycharmProjects/tech-learning-and-projects/` 下执行。**
多 workspace 环境中严禁在 agenzo 或其他项目目录下做文件存在性检查。

1. 今天日期已由工作区注入，动态计算年（YYYY）/ 月（MM）
2. 在 **tech-learning-and-projects** 项目下检查 `learning-notes/briefings/{topic}/YYYY/MM/YYYY-MM-DD.md`：
   - 已存在 → 告知用户「✅ {主题} 今日已完成，跳过」并结束
   - 不存在 → 继续
3. 三个主题都已存在 → 输出汇总后终止，**不执行 run-all 或任何后续步骤**

---

## Phase 1: 读取候选集

由 `scripts/briefing-tools.py` 的流水线预先产出（全部已完成确定性抓取、打标、评分、跨天/跨主题去重）。

### 1a. 确认流水线已跑

```bash
# 如果 .kiro_tmp/briefings/runs/YYYY-MM-DD/candidates.{topic}.jsonl 不存在则触发流水线
python3 scripts/briefing-tools.py run-all
```

`run-all` 串行跑：ingest → classify → candidates，产出：
- `pool.jsonl`：原始采集池（含 RSS + follow-builders + **supplement** 补充源）
- `classified.jsonl`：带 tags 和 score
- `candidates.{topic}.jsonl`：本主题已过滤候选集

**supplement 补充层**（`config.json` → `supplement_sources`）：B站搜索、V2EX 等无 Cookie 社区源，确定性并入 pool。本机若安装 Agent-Reach 的 `bili-cli` 会自动优先 CLI。curate 阶段无需再单独搜这些平台。

### 1b. 读取本主题候选集

```bash
cat .kiro_tmp/briefings/runs/YYYY-MM-DD/candidates.{topic}.jsonl
```

每条 JSONL 格式：
```json
{"title":"...","url":"...","published":"...","description":"...","source":"...","tags":["..."],"score":{"freshness":5,"primacy":4,"relevance":5,"utility":4,"total":18}}
```

---

## Phase 2: Web Search 补充

候选集来自 RSS + HN API（确定性数据）。Web search 补充长尾官方博客、论文、行业动态。
主题差异化关键词见各自的 `curate.{topic}.md`。

**搜索规则：**
- 禁止硬编码年月：用当前日期动态生成（如 "2026 May"）
- 每次搜索结果与候选集合并，title/url 去重后一起参与后续步骤

---

## Phase 3: 精选

从「候选集 + web search 结果」中挑选要收录到简报的条目。

**筛选原则：**
- 优先 score.total ≥ 15 的 RSS 候选（已经过确定性打分）
- Web search 结果按自己判断（可参考评分维度：时效 / 一手 / 相关 / 实用）
- 总收录量：头条 1-2 条 + 快讯 5-8 条 + 表格区 3-6 条
- 综述 / 对比 / 选型类文章除非有独特洞察否则排除
- 纯营销 / PR 稿排除

**注意：评分仅用于内部筛选，不出现在最终简报中。**

---

## Phase 4: 生成简报

严格使用各自 `curate.{topic}.md` 的 **写作模板** 和 **写作原则**。

**共同原则：**
- 像一个懂行的朋友在跟你聊天，不是填表
- 每条新闻的价值判断融入叙述，不单独列字段
- 不暴露采集流程（不写「采集统计」「评分明细」「标签」）
- 不写泛泛的行动建议，有具体可执行动作时自然融入正文最后一句
- 所有内容使用中文，技术术语可用英文
- 关注 Walter 的技术栈偏好：LangGraph、MCP、CrewAI、Python、TypeScript

**事实与推断必须分开写（硬约束）：**

只把来源里**明确写了**的内容当事实陈述。从名称、缩写、惯例推测出来的含义属于推断，必须带上不确定语气，或干脆不写。

```markdown
❌ 同时开源了 MoonEP（专家并行通信）、FlashKDA（注意力算子实现）和 AgentEnv（Agent 训练环境）
   ——官方只公布了名称，三个解释全是猜的，但读者会当成事实

✅ 同时开源了 MoonEP、FlashKDA 和 AgentEnv。官方公告只给了名称没有展开，
   从命名推测分别对应专家并行、KDA 算子实现和 Agent 训练环境，具体边界要等技术报告细读
```

- 多个来源数字冲突时，以官方 / 一手来源为准，并在正文写清口径（例：「数百 GB 到 1.4TB，取决于量化方案」而不是挑一个数字）
- 单一来源的关键结论（尤其是融资额、罚款、benchmark 分数）附上该来源链接，不要写成公认事实
- arXiv 条目注意 ID 前缀就是提交年月（`2601.x` = 2026 年 1 月）。老论文修订后会被 RSS 重新推送，**不要把它描述成新研究**
- 立场性内容、无独立来源佐证的爆料，宁可不收

**文件格式硬约束（违反会被 validate 拒绝）：**
- ❌ **不要加 YAML frontmatter**（不要写 `---\ntitle: ...\n---`）
- ✅ **第一行必须是** `# {标题}`，紧接着第二行 `> Author: Walter Wang`
- 后续章节用 `## 📌 头条` / `## ⚡ 快讯` 等 H2，每个具体条目用 `### {标题}` H3
- 每条至少包含一个外链（markdown 链接形式）

### 共用结构模板（所有主题必须遵守）

每个主题的简报都必须包含以下章节，**顺序固定**：

```markdown
# {主题图标} {主题名}简报 — YYYY-MM-DD

> Author: Walter Wang
> 每日精选 ... 5 分钟读完。

## 📌 头条

### 头条 1 标题（≤ 30 字）

3-5 句自然语言：发生了什么 → 为什么重要 → 对你意味着什么。

→ [原文](url) / [其他链接](url)

---

### 头条 2 标题

3-5 句自然语言。

→ [原文](url)

---

## ⚡ 快讯

- **主体名**：一句话说清楚 → [链接](url)
- **主体名**：一句话说清楚 → [链接](url)
- ...（5-8 条）

## {主题特有的中间章节，详见各 curate.{topic}.md}

## 📈 趋势

- 🆕 / 🔺 / 🔻 趋势名 — 一句话解释（3-4 条）
```

**头条规则（最常踩的雷，硬约束）：**
- 头条数量：1-2 条，**最多 2 条**
- **每条头条之后都必须有 `---` 分隔线**，包括最后一条与下一节之间
- 头条 H3 标题 ≤ 30 字，禁止用「## 头条 1」「## 头条 2」这种带序号的 H2 拆分

**快讯规则：**
- 最少 3 条（少于 3 条 validate 会拒）
- 每条用 `- **主体名**：` 开头，必须带链接

**表格规则：**
- 同一表格列数必须一致（| 数量相同）

---

## Phase 5: 写入 + 登记 + 分发

### ⚠️ 命令签名速查（错一字就报参数错误）

| 命令 | 正确签名 | ❌ 常见错写 |
|------|----------|-------------|
| `validate` | `validate <md_path>` （位置参数，不接受 `--topic` / `--date`） | `validate --topic xxx --date YYYY-MM-DD` |
| `register` | `register --topic {topic}` （`--date` 可选，默认今天） | `register --topic xxx --date YYYY-MM-DD` 也能跑通，但额外参数没必要 |
| `index` | `index --topic {topic}` 或 `--topic all` | — |
| `notify` | `notify --topic {topic}` | — |
| `compare-skeleton` | `compare-skeleton --topic {topic} <md_path>` | — |
| `render` | `render --json <draft_json_path>` | — |

报错时立刻 `python3 scripts/briefing-tools.py {子命令} --help` 自查，不要瞎试。

**两条等价路径，二选一：**

### 路径 A（推荐，结构化产出）

把精选结果写成 BriefingDoc JSON（schema 见 `scripts/briefing_tools/doc_schema.py`），由脚本渲染：

```bash
# 1. 写 JSON 到临时文件，例如 .kiro_tmp/briefings/runs/YYYY-MM-DD/draft.{topic}.json
# 2. render 命令自动产出 md + 跑 validate + 跑 skeleton 对比 + 查 URL 复用
python3 scripts/briefing-tools.py render --json .kiro_tmp/briefings/runs/YYYY-MM-DD/draft.{topic}.json
```

### ⚠️ 必须处理 render 的「URL 复用」警告

render 结尾会检查你用的链接是否此前已被收录，命中就打印 `⚠️ N 条 URL 此前已收录`。
**这不是可以忽略的提示**——候选集已经做过跨天与跨主题去重，但你 web search 补充进来的
链接从未进过候选集，是唯一能漏进重复内容的口子。

逐条判断，二选一，不要放着不管：

- **有实质新进展** → 保留，但正文必须写出新增的是什么（原文更新了、事件有后续、
  你的切入角度不同）。不要把昨天讲过的事换个说法再讲一遍。
- **只是同一件事换个说法** → 换掉这条，重新选来源或直接弃收该条目。

判断完改 JSON 重跑 render。**特别注意 `[跨天]` 命中同一主题的情况**：这往往说明你把
一篇旧文当成了今天的新闻，先核对原文发布日期再决定。

JSON 结构：
```json
{
  "topic": "ai-agent",
  "date": "2026-05-19",
  "h1": "AI Agent 简报 — 2026-05-19",
  "subtitle": "每日精选 ... 5 分钟读完。",
  "headlines": [
    {"title": "...", "body": "...", "links": [{"label": "原文", "url": "..."}]},
    {"title": "...", "body": "...", "links": [...]}
  ],
  "briefs": [
    {"subject": "...", "text": "...", "links": [...]},
    ...（≥ 3 条）
  ],
  "extra_sections": [
    {"title": "📦 项目 & 论文", "columns": ["项目","描述","链接"],
     "rows": [{"cells":["...","..."], "link": {"label":"→","url":"..."}}]}
  ],
  "trends": [
    {"icon": "🆕", "text": "..."},
    {"icon": "🔺", "text": "..."}
  ],
  "optional_sections": [
    {"type": "markdown", "content": "**论文标题** — 一句话贡献。→ [arXiv](url)"}
  ]
}
```

`optional_sections` 用于表格区之后的自由块（如论文段落），`render` 会自动渲染。

### 路径 B（手写 markdown，仅用于路径 A 不可用时）

```bash
# 1. fs_write 到 learning-notes/briefings/{topic}/YYYY/MM/YYYY-MM-DD.md

# 2. 严格校验（缺 H1 / 头条少 --- / 快讯不足都会 fail）
python3 scripts/briefing-tools.py validate learning-notes/briefings/{topic}/YYYY/MM/YYYY-MM-DD.md

# 3. 跟金标准 fixture 对比章节骨架
python3 scripts/briefing-tools.py compare-skeleton --topic {topic} learning-notes/briefings/{topic}/YYYY/MM/YYYY-MM-DD.md
```

### 两条路径汇合处

```bash
# 4. 通过校验后再登记 URL 到 published-index（hash 漂移自动告警）
python3 scripts/briefing-tools.py register --topic {topic}

# 5. 同步 README 索引 + Bark 推送由 orchestrator 统一执行（见下方「收尾」）
#    subagent 不要各自跑 index / notify，避免重复推送
```

**单主题 hook** 可自己跑完整收尾；**一键采集全部简报** 由主线程最后统一：

```bash
python3 scripts/briefing-tools.py finalize --topic all
# 等价于 register(all) + index --topic all + notify --topic all + status
```

**顺序重要**：validate / compare-skeleton 先于 register。前置校验让 subagent 在失败时直接停手而不是污染索引。

**事后改 md 不是禁区**：register 之后仍然可以修正内容。改完按这个顺序收尾即可，成本很低：

```bash
python3 scripts/briefing-tools.py validate learning-notes/briefings/{topic}/YYYY/MM/YYYY-MM-DD.md
python3 scripts/briefing-tools.py doctor --fix   # 自动为 hash_drift / missing 重跑 register
```

`register` 报的 file_hash 告警只是提示同步 README，**不是错误、不会阻塞、也不需要人工介入**。
⚠️ 因此：发现自己写错了事实就直接改，**不要因为「已经 register 过」而把已知错误留在正文里**。

---

## 周报（仅周日执行）

如果今天是周日，额外生成 `YYYY-WXX-weekly.md`，包含：
- 本周 Top 5 / 趋势总结 / 论文精选 / 下周预测
- 文件名使用 ISO 周号（Python: `datetime.now().isocalendar()`）

---

## 返回给用户

简短 3-5 行摘要：
- 收录条目数
- 最值得关注的 1-2 条
- 是否生成了周报
- 是否有异常
