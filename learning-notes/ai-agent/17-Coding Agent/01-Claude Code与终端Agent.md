# Claude Code 与终端 Agent
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Claude Code 概述

Claude Code 是 Anthropic 推出的终端原生 Agentic 编码工具。直接在终端中运行，能理解整个代码库、编辑文件、执行命令、操作 Git，无需离开命令行。

```
┌──────────────── Claude Code ────────────────┐
│                                              │
│  终端界面                                     │
│  ├─ 自然语言交互                              │
│  ├─ 代码库全局理解                            │
│  └─ 多文件编辑                                │
│                                              │
│  核心能力                                     │
│  ├─ 读取/搜索代码    ├─ 执行 Shell 命令       │
│  ├─ 编辑/创建文件    ├─ Git 工作流            │
│  ├─ MCP 工具扩展     └─ 多 Agent 并行         │
│                                              │
└──────────────────────────────────────────────┘
```

## 2. 基本使用

```bash
# 安装
npm install -g @anthropic-ai/claude-code

# 在项目目录启动
cd my-project
claude

# 直接传入任务（非交互模式）
claude "解释这个项目的架构"
claude "修复 src/auth.ts 中的登录 bug"
claude "为 UserService 类添加单元测试"

# 管道模式（用于 CI/CD）
echo "检查代码中的安全漏洞" | claude --pipe
```

## 3. 常用命令与模式

```bash
# 交互模式中的命令
> /help              # 查看帮助
> /compact            # 压缩上下文
> /clear              # 清除对话历史
> /model              # 切换模型
> /mcp                # 管理 MCP 工具
> /cost               # 查看 Token 用量

# 常见使用模式
> 阅读 src/ 目录，解释项目架构
> 找到所有使用 deprecated API 的地方并更新
> 创建一个 PR，修复 issue #42
> 运行测试，修复失败的用例
> 重构 database 模块，使用连接池
```

## 4. CLAUDE.md 项目配置

```markdown
# CLAUDE.md（放在项目根目录）

## 项目概述
这是一个 Python FastAPI 后端服务，使用 PostgreSQL 数据库。

## 技术栈
- Python 3.12 + FastAPI
- SQLAlchemy ORM
- Alembic 数据库迁移
- pytest 测试框架

## 代码规范
- 使用 ruff 格式化代码
- 类型注解必须完整
- 每个公共函数需要 docstring
- 测试文件放在 tests/ 对应目录

## 常用命令
- 运行测试: pytest -xvs
- 格式化: ruff format .
- 类型检查: mypy src/
- 数据库迁移: alembic upgrade head

## 注意事项
- 不要修改 alembic/versions/ 中的已有迁移文件
- API 路由定义在 src/routes/ 目录
- 环境变量通过 .env 文件管理
```

## 5. MCP 工具扩展

```json
// ~/.claude/mcp.json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": { "GITHUB_TOKEN": "ghp_xxx" }
    },
    "postgres": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-postgres"],
      "env": { "DATABASE_URL": "postgresql://..." }
    },
    "jira": {
      "command": "npx",
      "args": ["-y", "mcp-server-jira"],
      "env": { "JIRA_URL": "https://xxx.atlassian.net" }
    }
  }
}
```

## 6. 多 Agent 并行（Claude Code 5）

```bash
# Claude Code 支持并行 Agent 执行
# 主 Agent 可以 spawn 子 Agent 并行处理不同文件/任务

> 重构整个项目的错误处理：
>   1. 统一异常类定义
>   2. 更新所有路由的错误处理
>   3. 添加全局异常处理中间件
>   4. 更新对应的测试

# Claude Code 会自动并行处理多个文件的修改
# 子 Agent 各自负责不同模块，最后合并结果
```

## 7. Git 工作流集成

```bash
# Claude Code 原生支持 Git 操作
> 创建一个新分支 feature/user-auth，实现用户认证模块
> 查看最近的 commit，解释每个变更的目的
> 帮我写一个好的 commit message 并提交
> 创建 PR，标题和描述要清晰

# 代码审查
> 审查 PR #15 的代码变更，给出改进建议
```

## 8. 2026 版本演进

> 🔄 更新于 2026-05-12

<!-- version-check: Claude Code 2.1.139, Code with Claude SF (2026-05-06), checked 2026-05-20 -->

Claude Code 在 2026 年 3-4 月进入了史上最密集的迭代周期，从 v2.1.69 到 v2.1.101，5 周内发布了 30+ 个版本。

```
版本演进（2026 年 3-4 月关键里程碑）：

v2.1.83-85（Week 13，3/23-27）：
├─ Auto Mode（研究预览）：分类器自动处理权限提示
│  → 安全操作自动放行，高风险操作自动拦截
│  → 介于全部批准和 --dangerously-skip-permissions 之间
├─ Computer Use（桌面应用）：Claude 可操作 GUI 应用
├─ PR Auto-fix（Web 端）：自动修复 PR 问题
├─ 对话搜索：/ 键搜索历史对话
└─ 条件 Hook：if 条件触发的 Hook

v2.1.86-91（Week 14，3/30-4/3）：
├─ Computer Use（CLI 研究预览）：终端中操作原生应用
│  → 打开 GUI 应用、点击 UI、验证变更
│  → 适合只有 GUI 才能验证的场景
├─ /powerup 交互式教程
├─ MCP 结果大小上限提升至 500K（per-tool 可配置）
└─ 插件可执行文件加入 Bash 工具 PATH

v2.1.92-101（Week 15，4/6-10）：
├─ Ultraplan（早期预览）：云端规划 + 本地执行
│  → CLI 起草计划 → Web 编辑器审查/评论 → 远程或本地执行
│  → 首次运行自动创建云环境
├─ Monitor 工具：后台事件流注入对话
│  → Claude 可以 tail 日志并实时响应
├─ /loop 自动节奏（省略间隔时自动调节）
├─ /team-onboarding 团队入职指南打包
├─ /autofix-pr 终端启动 PR 自动修复
├─ Vertex AI 设置向导
├─ Bash 和沙箱安全增强
└─ 企业级改进：OS CA 证书信任、TLS 代理支持
```

**Claude Managed Agents**（公开 Beta）：Anthropic 推出完全托管的 Agent 运行时，提供安全沙箱、内置工具和 SSE 流式输出。通过 API 创建 Agent、配置容器、运行会话。

**v2.1.105-123（2026 年 4-5 月）— Plugin 生态与新命令**：

```
v2.1.105-114（4 月中旬）：
├─ Plugin 系统正式发布：自定义 skills/agents/hooks/MCP/LSP/monitors
│  → 单命令安装：claude plugin add <name>
│  → 组件类型：slash commands、sub-agents、hooks、MCP servers
├─ Plugin Marketplace：集中式目录，版本追踪，自动更新
│  → 支持 git 仓库、本地路径等多种来源
├─ Cowork Plugins：Claude.com 桌面端也支持 Plugin
└─ Agent SDK：开发者可构建自己的 Agent 循环

v2.1.116-123（5 月初）：
├─ /loop 命令：定时自动执行任务（省略间隔时自动调节节奏）
├─ /ultrareview：云端多 Agent 代码审查
├─ /caveman：超压缩 Skill（极限上下文节省）
├─ /focus、/recap、/release-notes：上下文管理命令
├─ /radio：社区分享的实验性命令
├─ MCP 安全加固：更严格的工具权限和沙箱隔离
├─ Channels 系统：多渠道输出（终端、Web、Slack）
└─ 性能改进：上下文窗口利用率优化
```

来源：[Claude Code Docs - Changelog](https://code.claude.com/docs/en/changelog)、[Claude Code Plugins](https://www.anthropic.com/news/claude-code-plugins)（Content was rephrased for compliance with licensing restrictions）

## 9. 终端 Agent 对比

<!-- 修复于 2026-05-20: gpt-4o/o3 已退役 → GPT-5/Codex；Claude 模型更新为最新版本 -->
| 特性 | Claude Code | Aider | Codex CLI | Gemini CLI |
|------|------------|-------|-----------|------------|
| 开发商 | Anthropic | 开源 | OpenAI | Google |
| 模型 | Opus 4.7 / Sonnet 4.6 | 多模型 | GPT-5.2 / Codex | Gemini 3.1 Pro |
| 代码库理解 | 全局索引 | Git 感知 | 全局索引 | 全局索引 |
| 多文件编辑 | ✅ | ✅ | ✅ | ✅ |
| 命令执行 | ✅ | 有限 | ✅ 沙箱 | ✅ |
| MCP 支持 | ✅ | ❌ | ❌ | ✅ |
| 多 Agent | ✅ 并行 | ❌ | ❌ | ❌ |
| Git 集成 | ✅ 原生 | ✅ 原生 | ✅ | ✅ |
| 价格 | Claude API 计费 | 免费+API费 | OpenAI 计费 | Gemini 计费 |

<!-- 修复于 2026-05-20: 章节编号重复（两个 ## 9.），按位置重新编号为 10-12 -->
## 10. 权限配置（五级权限系统）

Claude Code 内部实现了五级权限模型，点击"允许"说明配置不够完善：

```json
// ~/.claude/settings.json — 预配置权限规则
{
  "permissions": {
    "allow": [
      "Read(**)",
      "Glob(**)",
      "Grep(**)",
      "Bash(npm test*)",
      "Bash(git *)",
      "Write(src/**/*.test.ts)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Read(~/.ssh/**)",
      "Write(.env*)"
    ]
  }
}
```

## 11. 上下文管理（5 种压缩策略）

Claude Code 内部有 5 种上下文压缩策略，从轻到重：
1. Microcompact — 基于时间清除旧工具结果
2. Context Collapse — 摘要压缩对话片段
3. Session Memory — 提取关键上下文到文件
4. Full Compact — `/compact` 命令，摘要整个历史
5. PTL Truncation — 最后手段，丢弃最早消息

**关键：** CLAUDE.md 在每一轮对话中都会重新加载，所以把最重要的上下文放在 CLAUDE.md 中，而不是依赖对话历史。

## 12. 最佳实践

```
1. CLAUDE.md 是最高杠杆 — 每轮都会加载，放入项目规范和关键上下文
2. 预配置权限 — 用 settings.json 配置 allow/deny，减少交互确认
3. 主动压缩 — 长会话用 /compact，不要等 Agent 开始"忘事"
4. 任务粒度 — 一次一个明确任务，避免模糊指令
5. 验证习惯 — 让 Claude Code 运行测试验证修改
6. Git Worktree — 多 Agent 并行时利用 Worktree 隔离
7. Hook 扩展 — 用 Hook 系统自动化 lint/test/通知
8. MCP 扩展 — 为常用服务配置 MCP Server
```

> 📖 深度架构分析见 → `Claude Code架构深度解析.md`（本目录）
## 🎬 推荐视频资源

### 🌐 YouTube
- [Anthropic - Claude Code Demo](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude Code官方演示
- [Frontend Masters - Claude Code Tutorial](https://frontendmasters.com/courses/pro-ai/) — Claude Code专业教程
- [Fireship - Claude Code Review](https://www.youtube.com/watch?v=DHjqpvDnNGE) — Claude Code快速评测

### 📺 B站
- [Claude Code使用教程](https://www.bilibili.com/video/BV1Bm421N7BH) — Claude Code中文教程

### 📖 官方文档
- [Claude Code Docs](https://docs.anthropic.com/en/docs/claude-code) — Anthropic官方文档
