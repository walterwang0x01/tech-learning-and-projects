# Claude Code 架构深度解析
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang
> 基于 2026-03-31 npm source map 泄露事件的架构分析

## 1. 事件背景

2026 年 3 月 31 日，安全研究员 Chaofan Shou 发现 Claude Code 的 npm 包（`@anthropic-ai/claude-code` v2.1.88）中包含了一个 57MB 的 `.map` 源映射文件，指向 Anthropic R2 存储桶中未混淆的 TypeScript 源码。这次泄露暴露了约 1,900 个文件、512,000+ 行代码，完整揭示了当前最先进的 AI 编码 Agent 的内部架构。

Anthropic 官方确认这是"发布打包流程中的人为错误，不涉及客户数据或凭证泄露"。

**对开发者的价值：** 这是迄今为止对生产级 Agentic 系统最完整的架构参考，揭示了工具系统、权限模型、多 Agent 编排、记忆管理、上下文压缩等核心设计模式。

## 2. 技术栈

| 类别 | 技术 |
|------|------|
| 运行时 | Bun |
| 语言 | TypeScript（strict 模式） |
| 终端 UI | React + Ink |
| CLI 解析 | Commander.js（extra-typings） |
| Schema 验证 | Zod v4 |
| 代码搜索 | ripgrep |
| 协议 | MCP SDK、LSP |
| API | Anthropic SDK |
| 遥测 | OpenTelemetry + gRPC |
| 特性开关 | GrowthBook |
| 认证 | OAuth 2.0、JWT、macOS Keychain |

**关键选型洞察：**
- 选择 Bun 而非 Node.js，利用其原生 TypeScript 支持和更快的启动速度
- 用 React + Ink 构建终端 UI，实现组件化的终端界面（这是非常前沿的做法）
- Zod v4 做运行时 Schema 验证，确保工具输入输出的类型安全

## 3. 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                     Claude Code 架构全景                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  入口层    main.tsx（Commander.js CLI + React/Ink 渲染器）        │
│           ─────────────────────────────────────                  │
│  命令层    commands/（50+ 斜杠命令）                              │
│           ─────────────────────────────────────                  │
│  引擎层    QueryEngine.ts（46K行，LLM调用核心）                   │
│           ─────────────────────────────────────                  │
│  工具层    tools/（40+ 工具，每个自包含模块）                      │
│           ─────────────────────────────────────                  │
│  权限层    hooks/toolPermission/（5级权限系统）                    │
│           ─────────────────────────────────────                  │
│  协调层    coordinator/（多Agent编排）                             │
│           ─────────────────────────────────────                  │
│  服务层    services/（API、MCP、OAuth、LSP、分析）                 │
│           ─────────────────────────────────────                  │
│  桥接层    bridge/（IDE双向通信：VS Code、JetBrains）              │
│           ─────────────────────────────────────                  │
│  状态层    state/ + memdir/（持久化记忆目录）                      │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```


## 4. 工具系统（40+ 工具）

每个工具是一个自包含模块，定义输入 Schema、权限模型和执行逻辑。这是 Agent 能力的核心。

### 核心工具清单

| 工具 | 功能 | 设计要点 |
|------|------|---------|
| BashTool | Shell 命令执行 | 沙箱隔离，命令白名单/黑名单 |
| FileReadTool | 文件读取（图片/PDF/Notebook） | 支持多格式，自动编码检测 |
| FileWriteTool | 文件创建/覆盖 | 写前权限检查，原子写入 |
| FileEditTool | 部分文件修改（字符串替换） | 精确匹配，避免全文重写 |
| GlobTool | 文件模式匹配搜索 | 快速文件发现 |
| GrepTool | ripgrep 内容搜索 | 比原生 grep 快 10x+ |
| WebFetchTool | URL 内容获取 | 超时控制，内容截断 |
| WebSearchTool | 网络搜索 | 搜索结果结构化 |
| AgentTool | 子 Agent 生成 | 多 Agent 并行的核心 |
| SkillTool | Skill 执行 | 可复用工作流 |
| MCPTool | MCP Server 工具调用 | 动态工具发现 |
| LSPTool | 语言服务器协议集成 | 代码智能（跳转/补全/诊断） |
| NotebookEditTool | Jupyter Notebook 编辑 | Cell 级别操作 |
| TaskCreateTool | 任务创建 | 持久化任务图 |
| SendMessageTool | Agent 间消息传递 | 基于文件的消息队列 |
| TeamCreateTool | 团队 Agent 管理 | 创建/删除团队成员 |
| EnterPlanModeTool | 进入规划模式 | 只规划不执行 |
| EnterWorktreeTool | Git Worktree 隔离 | 每个 Agent 独立工作树 |
| ToolSearchTool | 延迟工具发现 | 按需加载工具定义 |
| CronCreateTool | 定时触发器 | 后台定时任务 |
| SleepTool | 主动模式等待 | Proactive Agent 用 |
| SyntheticOutputTool | 结构化输出生成 | 强制输出格式 |

### 工具设计模式

```typescript
// 每个工具的标准结构（简化示意）
interface Tool {
  name: string;
  description: string;
  inputSchema: ZodSchema;       // Zod v4 输入验证
  permissionModel: PermissionModel; // 权限模型
  execute(input: Input): Promise<Output>;
  
  // 关键：每个工具自声明权限需求
  requiredPermissions: Permission[];
  sideEffects: boolean;         // 是否有副作用
}
```

**核心设计原则：**
1. 自包含 — 每个工具独立定义 Schema、权限、执行逻辑
2. 权限前置 — 执行前必须通过权限检查
3. 副作用声明 — 工具显式声明是否有副作用（读 vs 写）
4. Schema 验证 — Zod v4 确保输入输出类型安全

## 5. 五级权限系统（关键发现）

这是泄露中最有价值的设计之一。Claude Code 不是简单的"允许/拒绝"，而是一个可配置的五级权限系统。

```
┌─────────────────────────────────────────────────────────┐
│                    五级权限模型                            │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Level 1: Always Allow（始终允许）                        │
│  └─ 配置在 ~/.claude/settings.json 的白名单              │
│  └─ 例：文件读取、grep 搜索                              │
│                                                          │
│  Level 2: Auto-Approve（自动批准）                       │
│  └─ 基于 glob 模式匹配的自动授权                         │
│  └─ 例：*.test.ts 文件的写入自动允许                     │
│                                                          │
│  Level 3: Prompt（交互确认）                             │
│  └─ 需要用户明确确认的操作                               │
│  └─ 例：删除文件、执行未知命令                           │
│                                                          │
│  Level 4: Plan Mode（规划模式）                          │
│  └─ 只生成计划，不执行任何操作                           │
│  └─ 用于审查 Agent 的决策逻辑                            │
│                                                          │
│  Level 5: Never Allow（始终拒绝）                        │
│  └─ 黑名单操作，无论如何不允许                           │
│  └─ 例：rm -rf /、访问 ~/.ssh/                          │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

**配置示例：**

```json
// ~/.claude/settings.json
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

**对我们的启示：** 当你点击"允许"时，说明你的权限配置不够完善。生产环境应该预配置好权限规则，让 Agent 在安全边界内自主运行。

## 6. CLAUDE.md 每轮加载机制（关键发现）

泄露源码揭示了一个被严重低估的特性：**CLAUDE.md 在每一轮对话中都会被重新加载**。

```
用户输入 → 加载 CLAUDE.md → 注入系统提示 → LLM 推理 → 工具调用 → 返回结果
              ↑                                                    │
              └────────────────────────────────────────────────────┘
                              下一轮继续加载
```

**这意味着：**
1. CLAUDE.md 是最高杠杆的配置文件 — 它影响 Agent 的每一次决策
2. 可以动态修改 — 在会话中途修改 CLAUDE.md，下一轮立即生效
3. 层级加载 — 项目根目录 + 子目录的 CLAUDE.md 会合并

**最佳实践：**

```markdown
# CLAUDE.md — 高杠杆配置示例

## 项目上下文
- 这是一个 Python 3.12 + FastAPI 项目
- 数据库：PostgreSQL + SQLAlchemy
- 测试：pytest，覆盖率要求 > 80%

## 编码规范（每轮都会执行）
- 所有函数必须有类型注解
- 使用 ruff format 格式化
- 错误处理使用自定义异常类（见 src/exceptions.py）
- API 响应统一使用 ResponseModel

## 禁止操作
- 不要修改 alembic/versions/ 中的已有迁移
- 不要直接操作数据库，必须通过 ORM
- 不要在代码中硬编码密钥

## 测试要求
- 每个新功能必须有对应测试
- 修改代码后运行 pytest -xvs 验证
```

## 7. 上下文压缩策略（5 种）

长会话是 LLM Agent 的核心挑战。Claude Code 实现了 5 种压缩策略：

| 策略 | 触发条件 | 机制 | 保留内容 |
|------|---------|------|---------|
| Microcompact | 基于时间 | 清除旧的工具调用结果 | 保留决策，丢弃细节 |
| Context Collapse | 上下文过长 | 摘要压缩对话片段 | 关键决策和结论 |
| Session Memory | 主动触发 | 提取关键上下文到文件 | 持久化到 memdir/ |
| Full Compact | /compact 命令 | 摘要整个对话历史 | 全局摘要 |
| PTL Truncation | 最后手段 | 丢弃最早的消息组 | 保留最近上下文 |

```
上下文窗口使用率
100% ┤                          ╭─── PTL Truncation（最后手段）
 90% ┤                     ╭────╯
 80% ┤                ╭────╯ ← Full Compact 触发线
 70% ┤           ╭────╯
 60% ┤      ╭────╯ ← Context Collapse 触发线
 50% ┤ ╭────╯
 40% ┤─╯ ← Microcompact 持续运行
     └──────────────────────────────────────→ 对话轮次
```

**对我们的启示：** 不要等到 Agent 开始"忘事"才压缩。主动使用 `/compact` 命令，或在 CLAUDE.md 中设置关键上下文，确保每轮都能读到。

## 8. 多 Agent 编排（Swarm 模式）

泄露揭示了 Claude Code 的多 Agent 系统是基于**文件系统的消息传递**，而非数据库或消息队列。

```
┌─────────────────────────────────────────────────┐
│              Lead Agent（主 Agent）               │
│  ├─ 任务分解                                     │
│  ├─ 子 Agent 生成（AgentTool）                   │
│  ├─ 结果聚合                                     │
│  └─ 冲突解决                                     │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ Agent A  │  │ Agent B  │  │ Agent C  │      │
│  │ 前端重构  │  │ API修改   │  │ 测试编写  │      │
│  │ Worktree │  │ Worktree │  │ Worktree │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│       │              │              │            │
│       └──────────────┴──────────────┘            │
│              共享 Prompt Cache                    │
│              文件系统消息传递                      │
│              JSON 任务图                          │
└─────────────────────────────────────────────────┘
```

**关键设计决策：**

1. **Prompt Cache 共享** — 子 Agent fork 时创建父上下文的字节级副本，共享 Prompt Cache。这意味着并行 Agent 几乎不增加额外成本（这是最"mind-blowing"的发现）
2. **Git Worktree 隔离** — 每个子 Agent 在独立的 Git Worktree 中工作，避免文件冲突
3. **文件系统通信** — Agent 间通过写入对方的 inbox 文件通信，任务是磁盘上的 JSON 文件
4. **无数据库/无消息队列** — 整个多 Agent 系统基于文件系统，极简但有效

**为什么选择文件系统而非数据库？**
- 零依赖：不需要安装 Redis/PostgreSQL
- 可调试：直接 `cat` 查看 Agent 状态
- 可恢复：任务图持久化在磁盘，会话重启后可恢复
- 简单：JSON 文件比 IPC/RPC 简单得多

## 9. Hook 系统（25+ 生命周期事件）

泄露揭示了一个强大的 Hook 系统，这是 Claude Code 真正的扩展 API。

```
Agent 生命周期
│
├─ SessionStart          ← 会话开始
├─ UserPromptSubmit      ← 用户提交提示
│   ├─ PreToolUse        ← 工具调用前（可拦截）
│   ├─ ToolExecution     ← 工具执行中
│   ├─ PostToolUse       ← 工具调用后
│   └─ ... (循环)
├─ AgentResponse         ← Agent 响应
├─ SessionEnd            ← 会话结束
│
Hook 可触发的动作：
├─ 运行 Shell 命令
├─ 注入 LLM 上下文
├─ 运行完整 Agent 验证循环
├─ 调用 Webhook
└─ 运行 JavaScript 函数
```

**生产级 Hook 示例：**

```json
// .claude/hooks/pre-write-lint.json
{
  "name": "Pre-Write Lint",
  "version": "1.0.0",
  "when": {
    "type": "preToolUse",
    "toolTypes": ["write"]
  },
  "then": {
    "type": "runCommand",
    "command": "npx eslint --fix ${file}"
  }
}

// .claude/hooks/post-edit-test.json
{
  "name": "Post-Edit Test",
  "version": "1.0.0",
  "when": {
    "type": "postToolUse",
    "toolTypes": ["write"]
  },
  "then": {
    "type": "runCommand",
    "command": "npm test -- --related ${file}"
  }
}
```

## 10. 反蒸馏机制（Anti-Distillation）

泄露揭示了 Anthropic 防止竞争对手通过录制 API 流量来训练模型的两层防御：

### 第一层：假工具注入（Fake Tools）

```typescript
// claude.ts (line 301-313)
// 当 ANTI_DISTILLATION_CC 启用时，API 请求中包含：
anti_distillation: ['fake_tools']
// 服务端会静默注入虚假工具定义到系统提示中
```

触发条件（四个条件同时满足）：
1. `ANTI_DISTILLATION_CC` 编译时 Flag 启用
2. CLI 入口点（非 SDK）
3. 使用第一方 API Provider
4. GrowthBook 远程开关 `tengu_anti_distill_fake_tool_injection` 为 true

**原理：** 如果有人录制 Claude Code 的 API 流量来训练竞争模型，假工具定义会污染训练数据。不是防止复制，而是让你复制到错误的东西。

### 第二层：连接器文本摘要（Connector-Text Summarization）

```typescript
// betas.ts (lines 279-298)
// 服务端缓冲助手在工具调用之间的文本，生成摘要并附带加密签名
// 后续轮次可通过签名恢复原文
// 录制 API 流量的人只能获得摘要，而非完整推理链
```

**对我们的启示：** 在 AI 产品中，技术防护（假数据注入）+ 法律手段是保护知识产权的组合拳。但正如分析者指出的，"认真做蒸馏的人大约一小时就能找到绕过方法"，真正的保护可能还是法律层面。

## 11. 原生客户端认证（Native Client Attestation）

这是 Anthropic 阻止第三方工具使用 Claude Code 内部 API 的技术手段：

```typescript
// system.ts (lines 59-95)
// API 请求中包含 cch=00000 占位符
// 在请求离开进程前，Bun 的原生 HTTP 栈（Zig 编写）
// 将这 5 个零替换为计算出的哈希值
// 服务端验证哈希以确认请求来自真正的 Claude Code 二进制文件
```

**设计细节：**
- 占位符与替换值长度相同，不改变 Content-Length 头
- 计算发生在 JavaScript 运行时之下（Zig 层），JS 层不可见
- 本质上是 API 调用的 DRM，在 HTTP 传输层实现

**这解释了为什么 OpenCode 社区被迫使用 session-stitching hack** — Anthropic 不仅法律上要求第三方工具不使用其 API，二进制文件本身也在加密证明自己是正版客户端。

## 12. Prompt Cache 经济学（成本驱动架构）

泄露揭示了 Prompt Cache 如何深刻影响整个架构设计：

### 缓存命中 vs 未命中的成本差异

以 Claude Opus 4.6 为例：
- 标准输入：$5 / 百万 Token
- 缓存命中：$0.5 / 百万 Token（**90% 折扣**）
- 每次缓存未命中，成本增加 10 倍

### 14 种缓存失效向量

```typescript
// promptCacheBreakDetection.ts
// 追踪 14 种可能导致 Prompt Cache 失效的情况
// 包括：模式切换、上下文变更、系统提示修改等

// "sticky latches" 机制：防止模式切换破坏已建立的缓存
// 一个函数被标注为 DANGEROUS_uncachedSystemPromptSection()
```

### cache_edits 机制（长会话不变慢的秘密）

```
传统做法：删除旧消息 → 缓存连续性断裂 → 整个历史重新处理 → 延迟飙升
Claude Code：标记旧消息为 "skip" → 模型不再看到 → 但缓存连续性不断裂
结果：数小时长会话，清除数百条旧消息后，下一轮响应速度几乎和第一轮一样快
```

### 25 万次浪费的 API 调用

```typescript
// autoCompact.ts (lines 68-70) 注释，日期 2026-03-10：
// "1,279 个会话有 50+ 次连续失败（最多 3,272 次），
//  全球每天浪费约 250,000 次 API 调用"
// 修复：MAX_CONSECUTIVE_AUTOCOMPACT_FAILURES = 3
// 三行代码，每天节省 25 万次 API 调用
```

**核心洞察：** 对 AI 产品来说，模型推理成本可能不是最贵的层面；失败的缓存管理才是。

## 13. Undercover 模式（隐身模式）

```typescript
// undercover.ts (~90 行)
// 在非内部仓库中使用时，剥离所有 Anthropic 内部痕迹
// 指示模型永远不要提及：
// - 内部代号（"Capybara"、"Tengu"）
// - 内部 Slack 频道
// - 仓库名称
// - "Claude Code" 本身

// line 15: "There is NO force-OFF. This guards against model codename leaks."
// 可以用 CLAUDE_CODE_UNDERCOVER=1 强制开启，但没有办法强制关闭
// 在外部构建中，整个函数被死代码消除为空返回
```

**争议点：** 这意味着 Anthropic 员工在开源项目中提交的 AI 生成代码，不会有任何 AI 编写的标识。隐藏内部代号是合理的，但让 AI 主动假装是人类写的代码，这是另一回事。

## 14. 用户情绪检测（Regex 方式）

```typescript
// userPromptKeywords.ts
// 用正则表达式检测用户挫败感：
/\b(wtf|wth|ffs|omfg|shit(ty|tiest)?|dumbass|horrible|awful|
piss(ed|ing)? off|piece of (shit|crap|junk)|what the (fuck|hell)|
fucking? (broken|useless|terrible|awful|horrible)|fuck you|
screw (this|you)|so frustrating|this sucks|damn it)\b/
```

**讽刺之处：** 一家 LLM 公司用正则表达式做情感分析。但也合理 — regex 比一次 LLM 推理调用快得多、便宜得多，只是用来检测用户是否在骂工具。

## 15. Bash 安全系统（23 项检查）

```typescript
// bashSecurity.ts
// 每个 Bash 命令经过 23 项编号安全检查：
// - 18 个被阻止的 Zsh 内置命令
// - 防御 Zsh 等号扩展（=curl 绕过 curl 的权限检查）
// - Unicode 零宽空格注入防御
// - IFS null-byte 注入防御
// - HackerOne 审查中发现的畸形 Token 绕过
```

**对我们的启示：** 这是目前已知最细致的 Zsh 威胁模型。如果你在构建允许 Agent 执行 Shell 命令的系统，这 23 项检查是一个很好的安全基线参考。

## 16. KAIROS 自主 Agent 系统（深度分析）

KAIROS 在源码中被引用超过 150 次，是一个完整的后台自主 Agent 系统：

### 注意力感知的自主性调节

```
用户在终端 → 协作模式（报告 + 征求意见）
用户切走窗口 → 自主模式（主动执行、直接提交）
用户切回终端 → 立即报告刚才做了什么

规则：任何可能阻塞用户超过 15 秒的操作都会被延迟
```

**这解决了 AI 工具的核心矛盾：** 完全自主让人不安，完全被动又低效。KAIROS 的方案是让 AI 的主动性随用户注意力动态波动 — 你看着它就乖，你走了它就干活。

### autoDream 记忆蒸馏

```
触发条件：累积 5 个会话 或 每 24 小时
四步流程：
1. 扫描现有记忆 → 了解当前已知内容
2. 从对话日志提取新知识
3. 合并新旧知识 → 修正矛盾、去除重复
4. 精炼索引 → 删除过时条目
```

借鉴了认知科学中的记忆巩固理论 — 人类在睡眠中巩固白天的记忆，KAIROS 在用户离开时巩固项目上下文。

### KAIROS 完整子系统

- `/dream` Skill — 夜间记忆蒸馏
- 每日追加日志
- GitHub Webhook 订阅
- 后台守护进程
- Cron 定时刷新（每 5 分钟）

## 17. 终端渲染优化（游戏引擎技术）

```typescript
// ink/screen.ts + ink/optimizer.ts
// 借鉴游戏引擎的终端渲染技术：
// - Int32Array 支持的 ASCII 字符池
// - 位掩码编码的样式元数据
// - 补丁优化器：合并光标移动、取消 hide/show 对
// - 自驱逐的行宽缓存（源码声称 "~50x reduction in stringWidth calls"）
```

看似过度工程化，但考虑到 Token 是逐个流式输出的，终端渲染性能直接影响用户体验。

## 18. 代码质量的真实面貌

泄露也暴露了一些"不那么优雅"的代码：

- `print.ts` — 5,594 行，其中一个函数 3,167 行，12 层嵌套
- 使用 Axios 做 HTTP（讽刺的是 Axios 刚在 npm 上被投毒）
- 模型只占 1.6% 的代码量（~8,000 行），98.4% 是工程脚手架

**核心洞察：** 同一个 Claude 模型，在 Web 版和 Claude Code 中表现差异巨大，原因不在模型本身，而在于围绕模型构建的 512,000 行工程代码 — 仓库上下文加载、工具调度、缓存策略、子 Agent 协作。ML 研究员 Sebastian Raschka 指出，将同样的工程架构应用到 DeepSeek 或 Kimi 等模型上，可能获得类似的编程性能提升。

## 19. 泄露原因与供应链安全教训

```
根因链：
Anthropic 2025 年底收购 Bun
→ Claude Code 基于 Bun 构建
→ Bun 有一个已知 Bug（oven-sh/bun#28001，2026-03-11 提交）：
   生产模式下仍然提供 Source Map
→ .map 文件未被 .npmignore 排除
→ npm publish 时 57MB Source Map 被包含在包中
→ Source Map 指向 R2 存储桶中的未混淆源码
→ 512,000 行代码完全暴露

讽刺：Anthropic 自己的工具链暴露了自己产品的源码
Twitter 评论："意外把 Source Map 发到 npm 上，这种错误听起来不可能，
直到你想起代码库的很大一部分可能是被你正在发布的 AI 写的"
```

## 20. 特性开关系统（44 个 Flag，5 大类）

泄露揭示了 44 个特性开关，分为 5 大类：

### 按功能域分类

| 类别 | 数量 | 代表 Flag | 说明 |
|------|------|----------|------|
| 自主 Agent | 12 | KAIROS, PROACTIVE, DAEMON | 后台自主运行、注意力感知 |
| 反蒸馏与安全 | 8 | ANTI_DISTILLATION_CC, NATIVE_CLIENT_ATTESTATION | 假工具注入、客户端认证 |
| IDE 桥接 | 6 | BRIDGE_MODE | VS Code/JetBrains 双向通信 |
| 交互增强 | 10 | VOICE_MODE, BUDDY, VIM_MODE | 语音输入、虚拟宠物、Vim 模式 |
| Agent 编排 | 8 | AGENT_TRIGGERS, MONITOR_TOOL | 定时触发、监控工具 |

### 模型代号泄露

源码中出现了代号 **Capybara**（水豚），分为三个层级：
- Standard（标准版）
- Fast（快速版）
- Million-context（百万上下文窗口版）

社区广泛推测这是 Claude 5 系列的内部代号。

**实现方式（Bun 编译时消除）：**

```typescript
import { feature } from 'bun:bundle'

// 未启用的代码在构建时完全移除（Dead Code Elimination）
const voiceCommand = feature('VOICE_MODE')
  ? require('./commands/voice/index.js').default
  : null
```

**对我们的启示：** 特性开关是管理 Agent 功能演进的最佳实践。通过编译时消除，未启用的功能不会增加包体积。

## 11. 启动优化（并行预取）

Claude Code 的启动速度优化是一个值得学习的工程实践：

```typescript
// main.tsx — 在其他 import 之前作为副作用触发
startMdmRawRead()        // 预读 MDM 设置
startKeychainPrefetch()  // 预取密钥链
// API 预连接也在此并行启动

// 重模块延迟加载
// OpenTelemetry、gRPC、分析等模块通过 dynamic import() 按需加载
```

**优化策略：**
1. 并行预取 — MDM 设置、密钥链读取、API 预连接同时进行
2. 延迟加载 — 重模块（遥测、gRPC、分析）按需 `import()`
3. 特性开关 — 未启用功能在编译时完全移除

## 12. 服务层架构

| 服务 | 职责 |
|------|------|
| api/ | Anthropic API 客户端、文件 API、引导程序 |
| mcp/ | MCP Server 连接和管理 |
| oauth/ | OAuth 2.0 认证流程 |
| lsp/ | 语言服务器协议管理器 |
| analytics/ | GrowthBook 特性开关和分析 |
| plugins/ | 插件加载器 |
| compact/ | 对话上下文压缩 |
| policyLimits/ | 组织策略限制 |
| extractMemories/ | 自动记忆提取 |
| tokenEstimation.ts | Token 计数估算 |
| teamMemorySync/ | 团队记忆同步 |

## 13. 对 Agent 开发者的核心启示

### 可直接借鉴的设计模式

```
1. 工具自包含模式
   每个工具独立定义 Schema + 权限 + 执行逻辑
   → 适用于任何 Agent 框架的工具设计

2. 五级权限模型
   Always Allow → Auto-Approve → Prompt → Plan → Never Allow
   → 比简单的 allow/deny 更适合生产环境

3. CLAUDE.md 每轮注入
   项目配置在每轮对话中重新加载
   → 最高杠杆的 Agent 行为控制手段

4. Prompt Cache 共享 + cache_edits
   子 Agent 共享父上下文缓存 + 标记删除而非真删除
   → 多 Agent 并行成本优化 + 长会话不变慢的秘密

5. 文件系统通信
   Agent 间通过 JSON 文件通信
   → 零依赖、可调试、可恢复

6. 五种上下文压缩
   从微压缩到全量截断的渐进策略
   → 长会话 Agent 的必备能力

7. Hook 生命周期
   25+ 事件点，5 种动作类型
   → Agent 可扩展性的核心

8. 特性开关 + 编译时消除
   未启用功能零成本
   → Agent 功能演进的最佳实践

9. 反蒸馏机制
   假工具注入 + 连接器文本摘要
   → AI 产品知识产权保护的新范式

10. 注意力感知自主性（KAIROS）
    根据用户是否在看终端动态调整 Agent 主动性
    → 解决"全自主 vs 全被动"的核心矛盾

11. 23 项 Bash 安全检查
    Zsh 内置命令阻止、零宽空格注入防御等
    → Agent 执行 Shell 命令的安全基线

12. 缓存经济学驱动架构
    14 种缓存失效向量追踪、sticky latches
    → 缓存未命中成本 10x，架构设计必须以缓存为中心
```

### 安全教训

```
1. Source Map 泄露
   → 生产构建必须排除 .map 文件
   → npm publish 前检查包内容（npm pack --dry-run）
   → 注意构建工具的默认行为（Bun 默认生成 Source Map）

2. 供应链安全
   → CI/CD 中加入包内容审计步骤
   → 使用 .npmignore 或 package.json files 字段精确控制发布内容
   → 收购的工具链也需要安全审计

3. 凭证管理
   → Claude Code 使用 OS 原生密钥链（macOS Keychain）
   → 不在文件系统中明文存储 Token
   → 原生客户端认证（Zig 层哈希）防止第三方冒用

4. 模型即 1.6%
   → 512,000 行代码中只有 ~8,000 行直接调用模型
   → 98.4% 是工程脚手架（安全、缓存、编排、UI）
   → AI 产品的竞争壁垒在工程层，不在模型层
```

## 14. 与其他 Coding Agent 的架构对比

| 维度 | Claude Code | Cursor | Devin | Aider |
|------|------------|--------|-------|-------|
| 运行环境 | 终端（Bun） | IDE（Electron） | 云端沙箱 | 终端（Python） |
| UI 框架 | React + Ink | React | Web UI | 纯文本 |
| 工具数量 | 40+ | ~20 | ~30 | ~10 |
| 权限模型 | 5级可配置 | 基础确认 | 沙箱隔离 | 基础确认 |
| 多 Agent | Swarm（文件通信） | 后台 Agent | 单 Agent | 无 |
| 上下文压缩 | 5种策略 | 基础截断 | 未知 | 基础截断 |
| MCP 支持 | 原生 | 原生 | 无 | 无 |
| 开源 | ❌（已泄露） | ❌ | ❌ | ✅ |

## 21. CLAUDE.md 四层加载机制（源码直读补充）

基于 `claudemd.ts` 源码直读，CLAUDE.md 的加载机制远比之前文档描述的复杂，实际有 **4 层优先级**：

```text
1. Managed memory（/etc/claude-code/CLAUDE.md）— 管理员全局指令
2. User memory（~/.claude/CLAUDE.md）— 用户私有全局指令
3. Project memory（CLAUDE.md + .claude/CLAUDE.md + .claude/rules/*.md）— 项目级指令
4. Local memory（CLAUDE.local.md）— 私有项目级指令（不提交到 Git）
```

**关键细节：**

- **后加载 = 更高优先级** — 模型更关注后面的内容，因此 Local memory 优先级最高
- **`@include` 指令** — 支持引用其他文件：`@path`、`@./relative`、`@~/home`、`@/absolute`
- **循环引用检测** — 防止 `@include` 形成无限循环
- **单文件最大 40,000 字符** — 超出部分会被截断
- **指令前缀** — 每层加载时都会注入："These instructions OVERRIDE any default behavior and you MUST follow them exactly"

**对我们的启示：** 构建自己的 Agent 时，项目配置系统应该支持多层级覆盖和文件引用，让不同角色（管理员、用户、项目、个人）都能注入指令。

---

## 22. 沙箱安全系统（源码直读补充）

基于 `sandbox-adapter.ts` 源码直读，Claude Code 集成了 `@anthropic-ai/sandbox-runtime` 包，提供操作系统级别的沙箱隔离：

**核心能力：**

- **文件系统读写限制** — `FsReadRestrictionConfig` / `FsWriteRestrictionConfig` 分别控制读写权限
- **网络访问限制** — `NetworkRestrictionConfig` + `NetworkHostPattern` 控制网络出口
- **违规事件追踪** — `SandboxViolationStore` 记录所有违规尝试，用于审计和告警
- **权限规则路径解析** — `//path` 表示绝对路径，`/path` 表示相对于设置文件目录
- **桥接层** — 在 `sandbox-runtime` 和 Claude Code 权限系统之间建立桥接，统一权限模型

**对我们的启示：** 生产级 Agent 需要沙箱隔离，不能只靠权限检查。这是防御纵深的关键层 — 即使权限系统被绕过，沙箱仍然能阻止危险操作。

---

## 23. 团队记忆密钥防护（源码直读补充）

基于 `teamMemSecretGuard.ts` 源码直读，当 Agent 写入团队记忆文件时，会自动扫描内容中的密钥：

```typescript
// 如果检测到密钥，阻止写入并返回错误
"Content contains potential secrets (${labels}) and cannot be written to team memory.
Team memory is shared with all repository collaborators.
Remove the sensitive content and try again."
```

**工作机制：**

- 使用 `secretScanner` 模块自动检测敏感前缀（API Key、Token 等）
- **只在团队记忆路径触发** — 通过 `isTeamMemPath` 判断，个人记忆不受限制
- 检测到密钥时**直接阻止写入**并返回错误信息
- 防止 Agent 意外将 API 密钥、Token 等敏感信息写入共享记忆

**对我们的启示：** 多人协作的 Agent 系统必须有密钥泄露防护。Agent 可能在执行任务过程中接触到密钥，如果没有写入拦截，这些密钥可能被持久化到共享存储中。

---

## 24. YOLO 分类器 / Auto Mode（源码直读补充）

基于 `yoloClassifier.ts` 源码直读，Claude Code 有一个"自动模式分类器"（YOLO Classifier），用**独立的 LLM 调用**来判断操作是否安全：

**核心机制：**

- **独立分类器提示词** — 使用 `auto_mode_system_prompt.txt`，与主对话分离
- **区分用户类型** — 内部（Anthropic）和外部用户使用不同的权限模板
- **三类自定义规则** — 用户可配置：
  - `allow` — 允许执行
  - `soft_deny` — 软拒绝（分类器可覆盖）
  - `environment` — 环境相关规则
- **拒绝追踪** — `denialTracking.ts` 记录连续拒绝次数，过多连续拒绝会回退到手动确认模式
- **特性开关** — 通过 `TRANSCRIPT_CLASSIFIER` 控制启用/禁用

**对我们的启示：** 高级权限系统不只是规则匹配，还可以用 LLM 做动态安全判断。但要注意额外的成本和延迟 — 每次操作都多一次 LLM 调用。

---

## 25. 工具池缓存稳定性优化（源码直读补充）

基于 `tools.ts` 源码直读，`assembleToolPool()` 函数揭示了一个关键的 Prompt Cache 优化策略：

```typescript
// 内置工具排序在前作为缓存前缀
// MCP 工具排在后面
// 这样新增/删除 MCP 工具不会破坏内置工具的缓存
return uniqBy(
  [...builtInTools].sort(byName).concat(allowedMcpTools.sort(byName)),
  'name',
)
```

**设计原理：**

- **内置工具和 MCP 工具分区排序** — 内置工具作为连续前缀，MCP 工具追加在后
- **服务端缓存断点** — `claude_code_system_cache_policy` 在最后一个内置工具后设置缓存断点
- **缓存稳定性保证** — 如果混合排序，新增 MCP 工具会插入内置工具之间，导致所有下游缓存键失效
- **成本影响** — 工具列表的排序直接影响缓存命中率，缓存未命中意味着 10 倍的成本差异

**对我们的启示：** 工具列表的排序看似无关紧要，实际上直接影响 Prompt Cache 命中率和运行成本。这是一个容易被忽略但影响巨大的优化点。

---

## 26. 完整特性开关列表（源码直读更新）

基于对 `commands.ts`、`tools.ts`、`context.ts`、`permissions.ts`、`teamMemSecretGuard.ts` 等源码的直读，实际发现了 **21+ 个特性开关**，远超之前文档记录的 8 个：

| Flag | 来源文件 | 推测功能 |
|------|---------|---------|
| `HISTORY_SNIP` | commands.ts | 历史裁剪工具 |
| `WORKFLOW_SCRIPTS` | commands.ts + tools.ts | 工作流脚本系统 |
| `CCR_REMOTE_SETUP` | commands.ts | 远程设置 |
| `EXPERIMENTAL_SKILL_SEARCH` | commands.ts | 实验性技能搜索 |
| `ULTRAPLAN` | commands.ts | 超级规划模式 |
| `TORCH` | commands.ts | 未知功能 |
| `UDS_INBOX` | commands.ts + tools.ts | Unix Domain Socket 收件箱（Agent 间通信） |
| `FORK_SUBAGENT` | commands.ts | Fork 子 Agent |
| `COORDINATOR_MODE` | tools.ts | 协调器模式 |
| `CONTEXT_COLLAPSE` | tools.ts | 上下文折叠 |
| `TERMINAL_PANEL` | tools.ts | 终端面板捕获 |
| `WEB_BROWSER_TOOL` | tools.ts | 网页浏览器工具 |
| `MCP_SKILLS` | commands.ts | MCP 技能 |
| `OVERFLOW_TEST_TOOL` | tools.ts | 溢出测试工具 |
| `KAIROS_BRIEF` | commands.ts | KAIROS 简报 |
| `KAIROS_GITHUB_WEBHOOKS` | commands.ts + tools.ts | KAIROS GitHub Webhook |
| `KAIROS_PUSH_NOTIFICATION` | tools.ts | KAIROS 推送通知 |
| `AGENT_TRIGGERS_REMOTE` | tools.ts | 远程 Agent 触发器 |
| `BREAK_CACHE_COMMAND` | context.ts | 缓存破坏命令 |
| `TEAMMEM` | teamMemSecretGuard.ts | 团队记忆 |
| `TRANSCRIPT_CLASSIFIER` | permissions.ts | 转录分类器（Auto Mode） |

**值得关注的新发现：**

- `UDS_INBOX` — 使用 Unix Domain Socket 实现 Agent 间通信，比文件系统消息传递更高效
- `FORK_SUBAGENT` — 支持 Fork 方式创建子 Agent，可能共享父进程的上下文
- `CONTEXT_COLLAPSE` — 上下文折叠，可能是新的上下文压缩策略
- `WEB_BROWSER_TOOL` — 网页浏览器工具，扩展 Agent 的信息获取能力
- `WORKFLOW_SCRIPTS` — 工作流脚本系统，允许用户定义可复用的自动化流程

**对我们的启示：** 特性开关是管理 Agent 功能演进的最佳实践。通过 GrowthBook 等特性开关平台，可以实现灰度发布、A/B 测试和快速回滚。

---

## 🎬 推荐视频资源

### 🌐 YouTube
- [Matthew Berman - Claude Code Leak Analysis](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude Code 泄露深度分析
- [Anthropic - How We Built Multi-Agent Research](https://www.anthropic.com/engineering/multi-agent-research-system) — Anthropic 官方多 Agent 架构文章
- [PromptLayer - Claude Code Agent Loop](https://blog.promptlayer.com/claude-code-behind-the-scenes-of-the-master-agent-loop/) — Agent 主循环深度解析

### 📺 B站
- [Claude Code 源码泄露分析](https://www.bilibili.com/video/BV1Bm421N7BH) — 中文架构分析

### 📖 参考资料
- [alex000kim - Fake Tools, Frustration Regexes, Undercover Mode](https://alex000kim.com/posts/2026-03-31-claude-code-source-leak/) — 最详细的源码分析（本文主要参考）
- [Odaily - 500,000 行 Claude Code 泄露完整分析](https://www.odaily.news/en/post/5210047) — 中文深度分析
- [Claude Code Leak: What Developers Can Learn](https://www.startuphub.ai/ai-news/artificial-intelligence/2026/claude-code-leak-what-developers-can-learn) — 开发者视角分析
- [Ars Technica - Claude Code Source Leak](https://arstechnica.com/ai/2026/03/entire-claude-code-cli-source-code-leaks-thanks-to-exposed-map-file/) — 事件报道
- [The Hacker News - Claude Code Leaked via npm](https://thehackernews.com/2026/04/claude-code-tleaked-via-npm-packaging.html) — 安全视角报道
- [CTOL - 512,000-Line Agent Blueprint](https://www.ctol.digital/news/claude-code-cli-source-map-leak-anthropic-512000-line-agent-blueprint/) — 架构蓝图分析
- [Claude Code Camp - Agent Teams Under the Hood](https://www.claudecodecamp.com/p/claude-code-agent-teams-how-they-work-under-the-hood) — 多 Agent 系统内部机制
- [GitHub Archive](https://github.com/walterwang0x01/claude-code) — 源码存档（教育研究用途）
