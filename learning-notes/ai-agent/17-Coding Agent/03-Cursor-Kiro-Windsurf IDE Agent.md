# Cursor / Kiro / Windsurf IDE Agent
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. IDE 集成 Coding Agent 概述

IDE Agent 将 AI 能力直接嵌入开发环境，提供代码补全、多文件编辑、对话式编程等能力。相比终端 Agent，IDE Agent 拥有更丰富的上下文（语法树、诊断信息、UI 交互）。

```
┌─────────────── IDE Agent 架构 ───────────────┐
│                                               │
│  ┌─────────┐  ┌──────────┐  ┌─────────────┐ │
│  │代码补全  │  │ 对话/Chat │  │ 多文件编辑   │ │
│  │Tab 补全  │  │ 上下文问答 │  │ Composer    │ │
│  └─────────┘  └──────────┘  └─────────────┘ │
│       ↕             ↕              ↕          │
│  ┌───────────────────────────────────────┐   │
│  │  代码索引 / 语法树 / 诊断 / Git 状态   │   │
│  └───────────────────────────────────────┘   │
│       ↕             ↕              ↕          │
│  ┌───────────────────────────────────────┐   │
│  │     LLM (Claude/GPT/Gemini/自选)      │   │
│  └───────────────────────────────────────┘   │
└──────────────────────────────────────────────┘
```

## 2. Cursor

AI-first 代码编辑器（基于 VS Code fork），以 Composer 多文件编辑和智能补全著称。

```
核心功能：
├─ Tab 补全：上下文感知的代码补全
├─ Chat：对话式编程，引用文件/符号
├─ Composer：多文件编辑，Agent 模式
├─ Cmd+K：内联代码生成/编辑
└─ @引用：@file @folder @web @docs @codebase
```

### .cursorrules 配置

```markdown
# .cursorrules（项目根目录）

You are an expert TypeScript developer.

## Code Style
- Use functional components with hooks
- Prefer named exports over default exports
- Use Zod for runtime validation
- Error handling: use Result pattern, avoid try-catch

## Project Structure
- src/routes/ - API route handlers
- src/services/ - Business logic
- src/models/ - Data models with Zod schemas
- src/utils/ - Shared utilities

## Testing
- Use Vitest for unit tests
- Test files: *.test.ts next to source files
- Mock external services, don't mock internal modules
```

## 3. Kiro

AWS 推出的 AI IDE，核心特色是 Specs 驱动开发和 Hooks 自动化。

```
核心功能：
├─ Specs：需求 → 设计 → 任务的结构化开发流程
├─ Hooks：文件变更/事件触发的自动化动作
├─ Steering：项目级 AI 行为配置
├─ MCP 集成：扩展工具能力
└─ Agent 模式：自主完成复杂任务
```

### Steering 文件

```markdown
# .kiro/steering/project.md
# inclusion: auto

## 项目概述
这是一个 Node.js 后端服务。

## 代码规范
- 使用 TypeScript strict 模式
- 所有函数必须有 JSDoc 注释
- 使用 ESM 模块系统

## 测试要求
- 每个 service 文件必须有对应测试
- 使用 Vitest 测试框架
```

### Hooks 自动化

```
Hooks 示例：
├─ 文件保存时自动运行 lint
├─ 创建新文件时自动生成测试模板
├─ 提交前自动检查类型错误
└─ Agent 完成任务后自动运行测试
```

## 4. Windsurf

Codeium 推出的 AI IDE，以 Cascade 流式编辑和深度上下文理解为特色。

```
核心功能：
├─ Cascade：多步骤 Agent 流，自动执行编辑链
├─ Flows：上下文感知的代码操作流
├─ Supercomplete：超级补全（预测下一步操作）
├─ 命令执行：内置终端命令执行
└─ 多模型：支持 GPT/Claude/Gemini
```

## 5. GitHub Copilot

GitHub 原生 AI 编程助手，集成于 VS Code / JetBrains / Neovim。

```
核心功能：
├─ 代码补全：行级/块级智能补全
├─ Copilot Chat：对话式编程
├─ Workspace Agent：@workspace 全项目理解
├─ Copilot Edits：多文件编辑模式
└─ CLI：终端命令建议
```

## 6. 2026 版本演进

> 🔄 更新于 2026-04-21

<!-- version-check: Cursor 3.0, Kiro GA, Claude Code Agent View (2026-05-06), checked 2026-05-21 -->

### Cursor 3（2026-04-02）

Cursor 3 是自编辑器发布以来最大的架构变更，从文件中心模型转向 Agent 中心工作区。年化收入突破 $20 亿，Agent 用户数量已是 Tab 自动补全用户的两倍。

```
Cursor 3 核心变化：
├─ Agents Window：独立的 Agent 工作区
│  ├─ 多 Agent 并行运行（本地/Worktree/云端/SSH）
│  ├─ 不中断主编码会话
│  └─ 云端-本地 Agent 无缝切换
├─ Design Mode：可视化设计模式
│  ├─ 交互式 Canvas（仪表盘、自定义界面）
│  ├─ 内置组件：表格、框图、图表
│  └─ 与 Diff 和 Todo 列表集成
├─ Best-of-N 模型对比：原生多模型对比
├─ 有状态续传：服务端缓存上下文
│  ├─ 客户端发送数据减少 80%+
│  └─ 执行时间提升 15-29%
└─ 界面完全重构（非增量更新）
```

### Kiro GA（2025-07 正式发布）

<!-- 修复于 2026-05-21: 定价更新为 $20/月 Pro，补充新定价结构 -->
Kiro 已从 Preview 阶段进入正式发布。2026 年定价调整为统一 credit 池模式：Free（50 credits）、Pro（$20/月，1000 credits）、Pro+（$40/月，2000 credits）、Power（$200/月，10000 credits）。

### Windsurf 被 Cognition 收购（2025-07）

<!-- 修复于 2026-05-21: 收购时间从 2025-12 修正为 2025-07，金额从 $2.5 亿修正为实际情况 -->
2025 年 7 月，在 OpenAI 的 $30 亿收购交易排他期到期后，Google 以 $24 亿"反向收购"挖走了 Windsurf 创始人和核心研究团队，Cognition 随后收购了 Windsurf 剩余资产（产品、代码库、用户）。截至 2026-05，两个产品仍独立运营，但合并后有望提供从 IDE 辅助到自主执行的完整 AI 开发工作流。

来源：[Cursor 3.0 Changelog](https://cursor.com/changelog/3-0)（Content was rephrased for compliance with licensing restrictions）
来源：[InfoQ: Cursor 3 Agent-First Interface](https://www.infoq.com/news/2026/04/cursor-3-agent-first-interface/)（Content was rephrased for compliance with licensing restrictions）

## 7. 综合对比

| 特性 | Cursor | Kiro | Windsurf | GitHub Copilot |
|------|--------|------|----------|----------------|
| 基础 | 自研界面（v3） | VS Code fork | VS Code fork（Cognition 旗下） | VS Code 插件 |
| 核心模式 | Agents Window | Specs 驱动 | Cascade 流 | Copilot Edits |
| 多文件编辑 | ✅ 强 | ✅ | ✅ | ✅ |
| 项目配置 | .cursorrules | Steering/Hooks | Cascade Rules | .github/copilot |
| 模型支持 | Claude/GPT/自选 | Claude/多模型 | GPT/Claude/Gemini | GPT/Claude |
| MCP 支持 | ✅ | ✅ 原生 | ✅ | ✅ |
| 结构化开发 | ❌ | ✅ Specs | ❌ | ❌ |
| 自动化 | Design Mode | ✅ Hooks | 有限 | 有限 |
| 多 Agent 并行 | ✅ Agents Window | ❌ | ❌ | ❌ |
| 免费版 | 有限额度 | 免费额度 | 有限额度 | 免费额度 |
| Pro 价格 | $20/月 | $20/月 | $15/月 | $10/月 |
| 特色优势 | Agent 编排中心 | 规范化开发流程 | 自主执行+IDE | 生态集成最广 |

## 8. IDE Agent vs 终端 Agent

```
IDE Agent 优势：
  ✅ 可视化 diff，直观审查变更
  ✅ 语法高亮、诊断信息、自动补全
  ✅ 文件树、符号导航等 IDE 能力
  ✅ 适合日常开发、代码审查

终端 Agent 优势：
  ✅ 无 GUI 依赖，可在服务器/CI 中运行
  ✅ 管道组合，与 Shell 工具链集成
  ✅ 适合批量操作、自动化脚本
  ✅ SSH 远程开发友好

推荐：日常开发用 IDE Agent，自动化/CI 用终端 Agent
```

## 9. 选型建议

```
追求补全体验和灵活性     → Cursor
需要规范化开发流程       → Kiro
喜欢流式编辑体验        → Windsurf
已有 GitHub 生态        → GitHub Copilot
团队统一工具            → GitHub Copilot（覆盖面最广）
```
## 🎬 推荐视频资源

### 🌐 YouTube
- [Fireship - Cursor AI Review](https://www.youtube.com/watch?v=DHjqpvDnNGE) — Cursor AI评测
- [Frontend Masters - Cursor & Claude Code](https://frontendmasters.com/courses/pro-ai/) — IDE Agent专业教程
- [Traversy Media - Cursor Tutorial](https://www.youtube.com/watch?v=LDB4uaJ87e0) — Cursor使用教程

### 📺 B站
- [Cursor AI编程助手教程](https://www.bilibili.com/video/BV1Bm421N7BH) — Cursor中文教程
- [Kiro IDE使用体验](https://www.bilibili.com/video/BV1dH4y1P7FY) — Kiro中文评测
