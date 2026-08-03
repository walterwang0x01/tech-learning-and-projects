---
inclusion: manual
description: "按项目维度扫描简报，输出对每个项目有直接影响的条目和动作建议。增量扫描，自动维护游标。"
---

请执行简报扫描 → 项目化总结流程。

1. 读取执行框架 `.kiro/briefings/prompts/scan-for-projects.md`
2. 严格按 Phase 0-5 执行
3. 配置文件：`.kiro/briefings/scan-config.yaml`（项目清单、主题开关、增量游标）

关键约束：

- 主题开关由 yaml 控制，不要扫被关闭的主题
- 首次运行（last_scanned_date 为空）扫全部历史，之后增量
- 输出文件：`learning-notes/briefings/_summaries/YYYY-MM-DD_review.md`
- 完成后必须更新 yaml 中的 `last_scanned_date`
