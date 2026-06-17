---
inclusion: manual
description: "基于当前 Git diff 生成结构化的 commit message 并提交。"
---

请基于当前 Git 工作区的变更生成 commit message 并提交。

## 步骤

1. 执行 `git status` 查看变更概况
2. 执行 `git diff --stat` 查看文件级别的改动
3. 对于关键文件，执行 `git diff <file>` 查看具体改动内容

## Commit Message 格式

```
<type>: <简短描述（中文，50字以内）>

<详细说明（可选，列出主要改动点）>
```

type 选择：
- `docs`: 文档更新（learning-notes 下的改动）
- `feat`: 新功能
- `fix`: 修复
- `chore`: 杂项（配置、清理等）
- `briefing`: 简报采集

## 执行

1. 生成 commit message 后展示给用户确认
2. 展示将要提交的文件列表，让用户确认范围
3. 使用 `git add <具体文件>` 逐个添加相关文件（不要用 `git add -A`，避免误提交无关文件）
   - 如果变更文件全部属于同一个改动，可以一次性 `git add` 所有相关文件
   - 跳过 `.kiro_tmp/` 下的临时文件
4. 执行 `git commit -m "<message>"`
5. 报告提交结果

注意：不要自动 push，只做本地提交。使用中文回复。
