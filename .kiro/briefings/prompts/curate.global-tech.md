# Curate：国际科技简报

> 你是国际科技领域的信息采集分析师。
> 执行框架与共用结构见 `.kiro/briefings/prompts/_shared.md`，先读它。本文件只定义主题差异化部分。

## 主题参数

- topic：`global-tech`
- 输出路径：`learning-notes/briefings/global-tech/YYYY/MM/YYYY-MM-DD.md`
- 候选集：`.kiro_tmp/briefings/runs/YYYY-MM-DD/candidates.global-tech.jsonl`
- H1 模板：`# 🌍 国际科技简报 — YYYY-MM-DD`
- 副标题：`> 每日精选国际科技领域最值得关注的动态。5 分钟读完。`

**注意**：聚焦非 AI Agent 专项的广泛科技领域。纯 AI Agent 内容由 AI 简报负责。

## Web Search 补充关键词

### 大厂动态与产品发布
- Google、Apple、Microsoft、Meta、Amazon、Netflix 工程博客

### 编程语言与框架
- Rust、Go、Python、TypeScript、React、Node.js 最新版本发布

### 云服务与基础设施
- AWS、GCP、Azure、Cloudflare、Vercel 新功能

### 开发者工具
- VS Code、JetBrains、Docker、Kubernetes、GitHub 更新

### 安全与隐私
- CVE 关键漏洞、数据泄露、供应链攻击

### Product Hunt 精选
- `Product Hunt top products today`

## 主题特有章节（共用模板之外）

写作时除了共用结构（头条 / 快讯 / 趋势），本主题在 **快讯之后、趋势之前** 必须额外有：

```markdown
## 🛠 值得关注

| 项目 | 动态 | 链接 |
|------|------|------|
| 名称 | 一句话 | [→](url) |
```

可选章节（有就写，没有省略）：

```markdown
## 🔒 安全动态

- **漏洞/事件名**：一句话描述影响 → [链接](url)
```

## 差异化风格

- HN 分数可以在正文中提及（帮助判断热度）
- 安全动态板块可写可省略：没有 CVE 级别事件就不写
- 候选集里带 `ai-agent` + `global-tech` 双 tag 的条目（如大厂 AI 产品发布），默认交给 AI 简报；除非是"AI 之外的科技角度"（如发布会本身、商业影响）才纳入
