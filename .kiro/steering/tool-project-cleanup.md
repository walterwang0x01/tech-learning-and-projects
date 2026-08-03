---
inclusion: manual
description: "扫描产出物目录，检查索引一致性，标记可归档内容，清理孤儿文件。"
---

你是一个项目目录整理助手。请对 learning-notes/ 下的产出物进行全面扫描和整理建议。

## 1. 简报目录扫描

先执行脚本获取精确状态：
```bash
python3 scripts/briefing-tools.py status --json
```

然后扫描 `learning-notes/briefings/` 下三个主题目录：

- 统计文件总数、本月文件数、本周文件数
- 找出最早和最近的文件日期
- 标记超过 30 天的文件为「可归档」
- 检查是否有非标准命名的文件（应为 YYYY-MM-DD.md 或 YYYY-WXX-weekly.md）

## 2. README 索引一致性修复

执行脚本自动同步所有索引：
```bash
python3 scripts/briefing-tools.py index --topic all
```

## 3. 孤儿文件检查

扫描 `learning-notes/` 下所有子目录：

- 空目录（没有任何文件）
- 孤立的 .md 文件（不在任何技术栈目录结构中）
- 临时文件（如 .DS_Store、*.tmp、*~）

对于 .DS_Store 文件，直接删除。其他孤儿文件只报告不删除。

## 4. 进度文件健康检查

检查以下状态文件是否存在且格式正确：

- `learning-notes/.audit-progress.md`
- `learning-notes/.update-log.md`
- `learning-notes/briefings/.errors.log`
- `learning-notes/briefings/.dedup-index.json`（去重索引）

如果错误日志超过 100 行，建议截断保留最近 50 行。
如果去重索引超过 30 天的条目过多，执行清理。

## 5. 输出整理报告

```
## 🧹 项目目录整理报告 — YYYY-MM-DD

### 📊 简报统计
| 主题 | 总文件数 | 本月 | 本周 | 最早 | 可归档 |
|------|----------|------|------|------|--------|

### 🔗 索引修复
- 已通过脚本自动同步所有索引 ✅

### 🗑 清理结果
- 删除 .DS_Store X 个
- 发现空目录 X 个
- 发现孤儿文件 X 个

### 📋 归档建议

### 💡 其他建议
```

## 规则
- 只修复 README.md 索引和删除 .DS_Store，其他操作只建议不执行
- 使用中文回复
- 保持报告简洁
