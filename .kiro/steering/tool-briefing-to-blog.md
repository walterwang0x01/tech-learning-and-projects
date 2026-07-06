---
inclusion: manual
description: "从本周简报提取热点，自动生成博客 Markdown 草稿（draft: true）。"
---

请从本周简报提取最有价值的话题，在博客站点生成 Markdown 草稿。

## 博客路径

`/Users/administrator/PycharmProjects/portfolio/astro-site/src/content/blog/<slug>.md`

## Phase 1-2: 收集简报 + 选题

周一到今天；不足 3 篇扩展到 7 天。选 1 个最适合写博客的话题，先 `ls` 确认 slug 不重复。

## Phase 3: 生成并写入

**默认直接写入**，`draft: true`：

```markdown
---
title: "..."
date: YYYY-MM-DD
tags: ["..."]
excerpt: "..."
emoji: "..."
vip: false
draft: true
---
```

正文 1500-2000 字，基于简报真实信息。

## Phase 4: 校验

```bash
cd /Users/administrator/PycharmProjects/portfolio/astro-site && npm run build
```

告知路径、预览命令、发布方式（改 draft: false 后 push）。
