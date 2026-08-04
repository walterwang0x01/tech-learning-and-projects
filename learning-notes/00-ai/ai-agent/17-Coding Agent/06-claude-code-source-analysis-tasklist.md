# Claude Code 源码分析 Tasklist
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang
> 基于直接阅读 https://github.com/walterwang0x01/claude-code 源码
> 状态：🔍 检查中 | ✅ 已记录 | 📝 待整理成文档

## 分析标准

记录的信息必须满足以下至少一条：
1. **可借鉴的设计模式** — 构建自己的 Agent 项目时可以直接参考
2. **之前文档未覆盖** — 二手分析文章没有提到的新发现
3. **生产级工程实践** — 真实生产环境中的工程决策和权衡
4. **安全相关** — 安全机制、威胁模型、防御策略

---

## 已检查的源码文件

| 文件 | 大小 | 状态 |
|------|------|------|
| `src/commands.ts` | 25K | ✅ 完整阅读 |
| `src/tools.ts` | 17K | ✅ 完整阅读 |
| `src/context.ts` | 6.4K | ✅ 完整阅读 |
| `src/cost-tracker.ts` | 10.7K | ✅ 完整阅读 |
| `src/tools/FileEditTool/FileEditTool.ts` | 4.1K（截断） | ✅ 部分阅读 |
| `src/skills/loadSkillsDir.ts` | 4K（截断） | ✅ 部分阅读 |
| `src/bridge/bridgeMain.ts` | 4.1K（截断） | ✅ 部分阅读 |
| `src/utils/permissions/permissions.ts` | 4K（截断） | ✅ 部分阅读 |
| `src/utils/permissions/yoloClassifier.ts` | 4.1K（截断） | ✅ 部分阅读 |
| `src/coordinator/coordinatorMode.ts` | 4.1K（截断） | ✅ 部分阅读 |
| `src/services/teamMemorySync/teamMemSecretGuard.ts` | 1.5K | ✅ 完整阅读 |
| `src/utils/claudemd.ts` | 4K（截断） | ✅ 部分阅读 |
| `src/utils/sandbox/sandbox-adapter.ts` | 4.1K（截断） | ✅ 部分阅读 |

## 待检查的关键文件

| 文件 | 预估大小 | 优先级 | 原因 |
|------|---------|--------|------|
| `src/QueryEngine.ts` | ~46K | 🔴 高 | LLM 调用核心，流式/重试/缓存逻辑 |
| `src/Tool.ts` | ~29K | 🔴 高 | 工具基类型定义，权限模型 |
| `src/main.tsx` | 未知 | 🔴 高 | 入口编排，启动优化 |
| `src/services/api/claude.ts` | 未知 | 🔴 高 | API 客户端，反蒸馏逻辑 |
| `src/hooks/toolPermission/` | 未知 | 🟡 中 | 权限检查完整实现 |
| `src/services/compact/` | 未知 | 🟡 中 | 上下文压缩完整实现 |
| `src/coordinator/` | 未知 | 🟡 中 | 多 Agent 编排完整实现 |
| `src/plugins/` | 未知 | 🟡 中 | 插件系统 |
| `src/voice/` | 未知 | 🟢 低 | 语音输入（未发布功能） |
| `src/buddy/` | 未知 | 🟢 低 | 虚拟宠物（彩蛋） |

---


## 发现清单

### 🔵 Topic 1: CLAUDE.md 加载机制（来源：claudemd.ts 源码直读）

**状态：** ✅ 已记录 | 📝 需更新现有文档

**发现：** CLAUDE.md 的加载远比之前文档描述的复杂，有 4 层优先级：

```
1. Managed memory（/etc/claude-code/CLAUDE.md）— 全局管理员指令
2. User memory（~/.claude/CLAUDE.md）— 用户私有全局指令
3. Project memory（CLAUDE.md + .claude/CLAUDE.md + .claude/rules/*.md）— 项目级
4. Local memory（CLAUDE.local.md）— 私有项目级指令（不提交到 Git）
```

- 后加载的优先级更高（模型更关注后面的内容）
- 支持 `@include` 指令引用其他文件（`@path`、`@./relative`、`@~/home`、`@/absolute`）
- 有循环引用检测
- 单文件最大 40,000 字符限制
- 指令前缀："These instructions OVERRIDE any default behavior and you MUST follow them exactly"

**价值：** 构建自己的 Agent 时，项目配置系统应该支持多层级覆盖和文件引用。

---

### 🔵 Topic 2: 沙箱安全系统（来源：sandbox-adapter.ts 源码直读）

**状态：** ✅ 已记录 | 📝 之前文档完全未覆盖

**发现：** Claude Code 集成了 `@anthropic-ai/sandbox-runtime` 包，提供：

- 文件系统读写限制（`FsReadRestrictionConfig` / `FsWriteRestrictionConfig`）
- 网络访问限制（`NetworkRestrictionConfig` + `NetworkHostPattern`）
- 违规事件追踪（`SandboxViolationStore`）
- 权限规则路径解析：`//path` = 绝对路径，`/path` = 相对于设置文件目录
- 与 Claude Code 权限系统的桥接层

**价值：** 生产级 Agent 需要沙箱隔离，不能只靠权限检查。这是防御纵深的关键层。

---

### 🔵 Topic 3: 团队记忆密钥防护（来源：teamMemSecretGuard.ts 源码直读）

**状态：** ✅ 已记录 | 📝 之前文档完全未覆盖

**发现：** 当 Agent 写入团队记忆文件时，会自动扫描内容中的密钥：

```typescript
// 如果检测到密钥，阻止写入并返回错误
"Content contains potential secrets (${labels}) and cannot be written to team memory.
Team memory is shared with all repository collaborators.
Remove the sensitive content and try again."
```

- 使用 `secretScanner` 模块检测敏感前缀（API Key 等）
- 只在团队记忆路径（`isTeamMemPath`）触发
- 防止 Agent 意外将密钥写入共享记忆

**价值：** 多人协作的 Agent 系统必须有密钥泄露防护。

---

### 🔵 Topic 4: YOLO 分类器 / Auto Mode（来源：yoloClassifier.ts 源码直读）

**状态：** ✅ 已记录 | 📝 之前文档完全未覆盖

**发现：** Claude Code 有一个"自动模式分类器"（YOLO Classifier），用独立的 LLM 调用来判断操作是否安全：

- 使用单独的分类器提示词（`auto_mode_system_prompt.txt`）
- 区分内部（Anthropic）和外部用户的权限模板
- 用户可自定义三类规则：`allow`（允许）、`soft_deny`（软拒绝）、`environment`（环境）
- 分类器结果有拒绝追踪（`denialTracking.ts`）— 连续拒绝过多会回退到手动确认
- 特性开关：`TRANSCRIPT_CLASSIFIER`

**价值：** 高级权限系统不只是规则匹配，还可以用 LLM 做动态安全判断。但要注意成本和延迟。

---

### 🔵 Topic 5: Coordinator 模式细节（来源：coordinatorMode.ts 源码直读）

**状态：** ✅ 已记录 | 📝 需补充到多 Agent 章节

**发现：**

- Coordinator 模式通过环境变量 `CLAUDE_CODE_COORDINATOR_MODE` 启用
- Worker Agent 的工具集是受限的（`ASYNC_AGENT_ALLOWED_TOOLS`），排除了团队管理工具
- 支持 Scratchpad 目录（`tengu_scratch` 特性门控）— Worker 可以在共享暂存区读写
- 会话恢复时自动匹配 Coordinator/Normal 模式
- Worker 可以访问 MCP 工具（来自已连接的 MCP Server）
- 简单模式下 Worker 只有 Bash + FileRead + FileEdit

**价值：** 多 Agent 系统中，Worker 的工具集应该比 Lead 更受限。Scratchpad 是 Agent 间共享中间结果的好模式。

---

### 🔵 Topic 6: 工具池组装与缓存稳定性（来源：tools.ts 源码直读）

**状态：** ✅ 已记录 | 📝 之前文档未覆盖此细节

**发现：** `assembleToolPool()` 函数揭示了一个关键的缓存优化：

```typescript
// 内置工具排序在前作为缓存前缀
// MCP 工具排在后面
// 这样新增/删除 MCP 工具不会破坏内置工具的缓存
return uniqBy(
  [...builtInTools].sort(byName).concat(allowedMcpTools.sort(byName)),
  'name',
)
```

- 内置工具和 MCP 工具分区排序，保持 Prompt Cache 稳定
- 服务端有 `claude_code_system_cache_policy`，在最后一个内置工具后设置缓存断点
- 如果混合排序，新增 MCP 工具会插入内置工具之间，导致所有下游缓存失效

**价值：** 工具列表的排序直接影响缓存命中率和成本。这是一个容易被忽略但影响巨大的优化。

---

### 🔵 Topic 7: 技能系统四层来源（来源：commands.ts + loadSkillsDir.ts 源码直读）

**状态：** ✅ 已记录 | 📝 之前文档未覆盖

**发现：** 技能（Skills）有四层来源，按优先级排列：

```
1. Bundled Skills — 内置打包的技能
2. Builtin Plugin Skills — 内置插件提供的技能
3. Skill Dir Commands — 用户 .claude/skills/ 目录的技能
4. Plugin Skills — 第三方插件的技能
```

- 技能文件支持 Frontmatter 元数据（描述、参数、何时使用）
- 支持动态技能发现（`getDynamicSkills`）— 文件操作过程中发现新技能
- 技能 Token 估算只基于 Frontmatter（名称+描述+whenToUse），不加载完整内容
- 支持参数替换（`substituteArguments`）和 Shell 命令执行（`executeShellCommandsInPrompt`）

**价值：** 可复用的 Agent 工作流应该设计成"技能"，支持发现、参数化、按需加载。

---

### 🔵 Topic 8: Bridge 系统 — IDE 双向通信（来源：bridgeMain.ts 源码直读）

**状态：** ✅ 已记录 | 📝 之前文档只提到了存在，未分析细节

**发现：**

- 使用 JWT 认证（`jwtUtils.ts`）
- 支持多会话生成（`SPAWN_SESSIONS_DEFAULT = 32`）
- 有系统休眠/唤醒检测（`pollSleepDetectionThresholdMs`）
- 退避策略：连接初始 2s → 上限 2min → 放弃 10min
- 支持 Trusted Device Token（`trustedDevice.ts`）
- 远程会话 URL 生成（`getRemoteSessionUrl`）
- Git Worktree 创建/清理（`createAgentWorktree` / `removeAgentWorktree`）
- 桥接安全命令白名单（只有 compact/clear/cost/summary/releaseNotes/files 可通过桥接执行）

**价值：** IDE 集成不是简单的消息传递，需要认证、会话管理、安全白名单、断线重连。

---

### 🔵 Topic 9: FileEditTool 安全机制（来源：FileEditTool.ts 源码直读）

**状态：** ✅ 已记录 | 📝 之前文档未覆盖

**发现：**

- 文件大小限制：1 GiB（`MAX_EDIT_FILE_SIZE`）
- 编辑前检查文件是否被意外修改（`FILE_UNEXPECTEDLY_MODIFIED_ERROR`）
- 写入前检查团队记忆密钥（`checkTeamMemSecrets`）
- 编辑后触发条件技能发现（`activateConditionalSkillsForPaths`）
- 编辑后通知 VS Code（`notifyVscodeFileUpdated`）
- 编辑后清除 LSP 诊断缓存（`clearDeliveredDiagnosticsForFile`）
- 文件历史追踪（`fileHistoryTrackEdit`）
- 引用样式保留（`preserveQuoteStyle`）
- 找不到文件时建议相似文件（`findSimilarFile`）
- 设置文件编辑验证（`validateInputForSettingsFileEdit`）

**价值：** 文件编辑工具不只是"写文件"，需要大量的前置检查和后置通知。

---

### 🔵 Topic 10: 成本追踪系统（来源：cost-tracker.ts 源码直读）

**状态：** ✅ 已记录 | 📝 之前文档只简单提到

**发现：**

- 追踪维度：输入 Token、输出 Token、缓存读取、缓存创建、Web 搜索请求、按模型分类
- 会话成本持久化到项目配置文件（`saveCurrentSessionCosts`）
- 支持会话恢复时恢复成本状态（`restoreCostStateForSession`）
- FPS 指标追踪（终端渲染性能）
- Advisor 模型用量单独追踪（内部顾问模型的 Token 消耗）
- Fast 模式标记（`speed: 'fast'`）
- OpenTelemetry 集成（`getCostCounter` / `getTokenCounter`）
- 代码行变更追踪（`addToTotalLinesChanged`）

**价值：** 生产级 Agent 必须有细粒度的成本追踪，按模型、按缓存类型、按会话。

---

### 🔵 Topic 11: 更多特性开关（来源：commands.ts + tools.ts 源码直读）

**状态：** ✅ 已记录 | 📝 需更新特性开关章节

之前文档列了 8 个 Flag，实际源码中发现了更多：

| Flag | 来源文件 | 推测功能 |
|------|---------|---------|
| HISTORY_SNIP | commands.ts | 历史裁剪工具 |
| WORKFLOW_SCRIPTS | commands.ts + tools.ts | 工作流脚本系统 |
| CCR_REMOTE_SETUP | commands.ts | 远程设置 |
| EXPERIMENTAL_SKILL_SEARCH | commands.ts | 实验性技能搜索 |
| ULTRAPLAN | commands.ts | 超级规划模式 |
| TORCH | commands.ts | 未知功能 |
| UDS_INBOX | commands.ts + tools.ts | Unix Domain Socket 收件箱（Agent 间通信） |
| FORK_SUBAGENT | commands.ts | Fork 子 Agent |
| COORDINATOR_MODE | tools.ts | 协调器模式 |
| CONTEXT_COLLAPSE | tools.ts | 上下文折叠 |
| TERMINAL_PANEL | tools.ts | 终端面板捕获 |
| WEB_BROWSER_TOOL | tools.ts | 网页浏览器工具 |
| MCP_SKILLS | commands.ts | MCP 技能 |
| OVERFLOW_TEST_TOOL | tools.ts | 溢出测试工具 |
| KAIROS_BRIEF | commands.ts | KAIROS 简报 |
| KAIROS_GITHUB_WEBHOOKS | commands.ts + tools.ts | KAIROS GitHub Webhook |
| KAIROS_PUSH_NOTIFICATION | tools.ts | KAIROS 推送通知 |
| AGENT_TRIGGERS_REMOTE | tools.ts | 远程 Agent 触发器 |
| BREAK_CACHE_COMMAND | context.ts | 缓存破坏命令 |
| TEAMMEM | teamMemSecretGuard.ts | 团队记忆 |
| TRANSCRIPT_CLASSIFIER | permissions.ts | 转录分类器（Auto Mode） |

---

### 🔵 Topic 12: 命令可用性与用户类型（来源：commands.ts 源码直读）

**状态：** ✅ 已记录 | 📝 之前文档未覆盖

**发现：**

- 三种用户类型：`claude-ai`（订阅用户）、`console`（API 用户）、`ant`（Anthropic 内部）
- 内部专用命令（`INTERNAL_ONLY_COMMANDS`）只在 `USER_TYPE === 'ant'` 时可用
- 包括：`backfillSessions`、`breakCache`、`bughunter`、`goodClaude`、`initVerifiers`、`mockLimits`、`autofixPr`、`agentsPlatform` 等
- 远程安全命令白名单（`REMOTE_SAFE_COMMANDS`）：只有不依赖本地文件系统的命令
- 桥接安全命令白名单（`BRIDGE_SAFE_COMMANDS`）：只有产生文本输出的命令

**价值：** 多用户类型的 Agent 系统需要按用户角色控制可用功能。

---

## 待整理成文档的方向

### 📝 方向 A: 更新现有 `Claude Code架构深度解析.md`
- [ ] 补充 CLAUDE.md 四层加载机制
- [ ] 补充沙箱安全系统
- [ ] 补充团队记忆密钥防护
- [ ] 补充 YOLO 分类器 / Auto Mode
- [ ] 补充工具池缓存稳定性优化
- [ ] 更新特性开关列表（从 8 个扩展到 21+）

### 📝 方向 B: 更新现有 `从Claude Code学构建生产级Agent.md`
- [ ] 补充沙箱隔离作为安全层
- [ ] 补充技能系统四层来源设计
- [ ] 补充 Bridge/IDE 集成的工程细节
- [ ] 补充 FileEditTool 的前置/后置检查模式
- [ ] 补充成本追踪的完整维度

### 📝 方向 C: 新文档 — Agent 安全纵深防御
- [ ] 五级权限模型
- [ ] YOLO 分类器（LLM 动态安全判断）
- [ ] 沙箱隔离（sandbox-runtime）
- [ ] 23 项 Bash 安全检查
- [ ] 团队记忆密钥防护
- [ ] 反蒸馏机制
- [ ] 原生客户端认证

### 📝 方向 D: 新文档 — Agent 成本优化工程
- [ ] Prompt Cache 经济学（10x 成本差异）
- [ ] 工具池排序与缓存稳定性
- [ ] cache_edits 标记删除机制
- [ ] 5 种上下文压缩策略
- [ ] 模型路由（按任务复杂度选模型）
- [ ] 25 万次浪费 API 调用的教训

### 📝 方向 E: 新文档 — Agent 可扩展性设计
- [ ] 技能系统（四层来源 + 动态发现）
- [ ] 插件架构
- [ ] Hook 生命周期（25+ 事件）
- [ ] MCP 工具集成
- [ ] Bridge/IDE 双向通信
- [ ] 工作流脚本系统
