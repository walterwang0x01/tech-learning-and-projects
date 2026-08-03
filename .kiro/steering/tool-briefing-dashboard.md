---
inclusion: manual
description: "调用脚本生成简报状态面板，补充文档维护状态。"
---

请生成一份 Hook 运行状态总览。

## 1. 简报采集状态（脚本生成）

执行以下命令获取精确的采集状态：
```bash
python3 scripts/briefing-tools.py status
```

将输出直接展示给用户。

## 2. 文档维护状态

读取以下文件（如果存在）：

- `learning-notes/.audit-progress.md` — 提取上次审查的技术栈、日期
- `learning-notes/.update-log.md` — 提取上次知识追踪的技术栈和日期

输出表格：
| 项目 | 上次执行 | 覆盖技术栈 | 下次建议 |
| --- | --- | --- | --- |

## 3. 错误日志与采集源健康检查

检查 `learning-notes/briefings/.errors.log`，如果有则：
1. 展示最近 10 行
2. **连续失败源检测**：统计最近 7 天内同一 URL 出现 `HTTP GET 失败` 的次数。如果同一源连续 3 天以上失败，高亮警告：
   - `🚨 {源名称} 已连续 {N} 天失败，建议检查 scripts/briefing-tools.py 中的 RSS_SOURCES 配置是否需要更新`

## 4. 建议

根据状态给出今天建议执行哪些 hook。使用中文回复，保持简洁。
