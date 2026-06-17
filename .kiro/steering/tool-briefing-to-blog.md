---
inclusion: manual
description: "从本周简报中提取热点话题，在博客站点生成 Markdown 草稿。"
---

请从本周的简报中提取最有价值的话题，在博客站点生成一篇 Markdown 草稿。

## 重要：博客已迁移到 Astro + Markdown 架构

- 博客站点路径：`📝 博客站点/astro-site/src/content/blog/`
- 不要再修改 `📝 博客站点/index.html`
- 新文章文件名用 slug，如 `my-new-article.md`

## Phase 1: 收集本周简报

1. 计算本周的日期范围（周一到今天）
2. 读取 `learning-notes/briefings/` 下三个主题目录中本周的所有简报文件
3. 如果本周简报不足 3 篇，扩展到最近 7 天

## Phase 2: 提取热点

从所有简报中提取：
- 评分最高的 3-5 条新闻
- 跨多个简报出现的共同趋势
- 有深度分析价值的技术话题

列出候选话题，选择最适合写博客的 1 个（优先选：技术深度、开发者实用价值、时效性强）。

## Phase 3: 生成博客文章

先 `ls 📝 博客站点/astro-site/src/content/blog/` 确认 slug 不重复。

生成 Markdown 文件，路径 `📝 博客站点/astro-site/src/content/blog/<slug>.md`，格式：

```markdown
---
title: "中文吸引人的标题"
date: YYYY-MM-DD
tags: ["标签1", "标签2"]
excerpt: "1-2 句话摘要，≤400 字符"
vip: false
draft: false
---

## 二级标题

正文 Markdown，1500-2000 字...
```

要求：
- 基于简报中的真实信息，引用原始来源
- 有技术深度，不泛泛而谈
- 包含代码示例或架构图（如适用）
- 结尾有「行动建议」或「延伸阅读」

## Phase 4: 输出

1. 展示选题理由和文章预览
2. 询问用户是否要写入博客站点（注意询问用户以确认）
3. 用户确认后写入 Markdown 文件，并告知：
   - 本地预览：`cd 📝 博客站点/astro-site && npm run dev`
   - 发布：在博客站点工作区 commit + push 到 main，1-2 分钟后自动上线

使用中文回复。
