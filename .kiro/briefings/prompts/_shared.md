# 简报执行框架（共享）

> 本文件定义三个简报 hook 共享的 Phase 流程。
> 三个 `curate.{topic}.md` 仅关注「主题差异化」部分：web search 关键词、写作模板、风格约束。

---

## 工作目录

`/Users/administrator/PycharmProjects/tech-learning-and-projects/`
所有相对路径以此为基准。通用规则见 `.kiro/steering/briefing-rules.md`（命中 `learning-notes/briefings/**` 自动加载）。

---

## Phase 0: 幂等性检查

1. 今天日期已由工作区注入，动态计算年（YYYY）/ 月（MM）
2. 检查 `learning-notes/briefings/{topic}/YYYY/MM/YYYY-MM-DD.md`：
   - 已存在 → 告知用户「今日已完成」并结束
   - 不存在 → 继续

---

## Phase 1: 读取候选集

由 `scripts/briefing-tools.py` 的流水线预先产出（全部已完成确定性抓取、打标、评分、跨天/跨主题去重）。

### 1a. 确认流水线已跑

```bash
# 如果 .kiro_tmp/briefings/runs/YYYY-MM-DD/candidates.{topic}.jsonl 不存在则触发流水线
python3 scripts/briefing-tools.py run-all
```

`run-all` 串行跑：ingest → classify → candidates，产出：
- `pool.jsonl`：原始采集池
- `classified.jsonl`：带 tags 和 score
- `candidates.{topic}.jsonl`：本主题已过滤候选集

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

---

## Phase 5: 写入 + 登记 + 分发

```bash
# 1. 写入 md 文件
# 工具：fs_write 到 learning-notes/briefings/{topic}/YYYY/MM/YYYY-MM-DD.md

# 2. 事务性校验（缺 H1 / 没有 ### 标题 / 没有外链都会 fail 并退出 1）
python3 scripts/briefing-tools.py validate learning-notes/briefings/{topic}/YYYY/MM/YYYY-MM-DD.md

# 3. 通过校验后再登记 URL 到 published-index
python3 scripts/briefing-tools.py register --topic {topic}

# 4. 同步 README 索引
python3 scripts/briefing-tools.py index --topic {topic}

# 5. 推送 Bark 通知
python3 scripts/briefing-tools.py notify --topic {topic}
```

**顺序重要**：validate 先于 register。register 内部会再次校验，但前置校验能让 subagent 在失败时直接停手而不是污染索引。

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
