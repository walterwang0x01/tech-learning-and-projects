# Agent 可扩展性设计
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang
> 基于 Claude Code 源码分析，提炼 Agent 系统的可扩展性设计模式
> 关联：`17-Coding Agent/02-Claude Code架构深度解析.md`

## 1. 可扩展性设计全景

Agent 系统如果只能做"出厂预设"的事情，价值天花板就是开发者的想象力。Claude Code 源码揭示了四层扩展体系：

```text
Layer 1: Skills（技能）    — Markdown 文件即技能，最轻量
Layer 2: Plugins（插件）   — 命令 + 技能的打包集合
Layer 3: Hooks（钩子）     — 25+ 生命周期事件，5 种动作
Layer 4: MCP（协议）       — 标准化外部工具接入
辅助：Workflow Scripts / Bridge / ToolSearchTool
```

| 维度 | Skills | Plugins | Hooks | MCP |
| ---- | ------ | ------- | ----- | --- |
| 复杂度 | 低 | 中 | 中 | 高 |
| 能力 | 提示词注入 | 命令+技能 | 流程拦截 | 外部工具 |
| 开销 | 几乎为零 | 低 | 取决于动作 | 进程间通信 |
| 场景 | 可复用工作流 | 功能模块化 | CI/CD 集成 | 外部服务 |

---

## 2. 技能系统（Skills）

### 四层来源（后加载覆盖先加载）

```typescript
const allSkills = [
  ...bundledSkills,           // 1. 内置打包（随 CLI 发布）
  ...builtinPluginSkills,     // 2. 内置插件提供
  ...skillDirCommands,        // 3. 用户 .claude/skills/ 目录
  ...pluginSkills,            // 4. 第三方插件注册
]
```

### 技能文件格式

```markdown
---
name: create-react-component
description: 创建标准 React 组件（类型定义+样式+测试）
whenToUse: 当用户要求创建新的 React 组件时
arguments:
  - name: componentName
    description: 组件名称（PascalCase）
    required: true
  - name: withTests
    description: 是否生成测试文件
    default: "true"
---

创建 `{{componentName}}` 组件：
1. `src/components/{{componentName}}/{{componentName}}.tsx`
2. `src/components/{{componentName}}/index.ts`

{{#if withTests}}
3. `{{componentName}}.test.tsx`（React Testing Library）
{{/if}}

验证：
` ` `bash
npx tsc --noEmit && npm test -- --related src/components/{{componentName}}
` ` `
```

### 关键机制

- **动态发现** — `activateConditionalSkillsForPaths()` 在文件操作后自动发现相关技能
- **Token 估算** — 只基于 Frontmatter（名称+描述+whenToUse），不加载完整内容
- **参数替换** — `substituteArguments(content, args)` 将 `{{arg}}` 替换为实际值
- **Shell 执行** — `executeShellCommandsInPrompt()` 执行技能中的 bash 代码块

---

## 3. 插件架构（Plugins）

插件是命令（Commands）+ 技能（Skills）的打包集合，通过 Manifest 声明能力：

```json
{
  "name": "my-agent-plugin",
  "version": "1.0.0",
  "commands": [
    { "name": "deploy", "description": "部署到指定环境", "handler": "./commands/deploy.js" },
    { "name": "db-migrate", "description": "数据库迁移", "handler": "./commands/migrate.js" }
  ],
  "skills": [
    { "path": "./skills/api-endpoint.md", "name": "create-api-endpoint" }
  ],
  "config": {
    "requiredEnvVars": ["DEPLOY_TOKEN"],
    "permissions": ["bash", "fileWrite"]
  }
}
```

内置插件随 CLI 发布，第三方插件通过配置注册。插件的技能合并到全局技能池第 4 层。

---

## 4. Hook 生命周期系统

### 25+ 生命周期事件

```text
SessionStart → UserPromptSubmit → PreToolUse → ToolExecution → PostToolUse → ...
→ PreCompact → AgentResponse → SessionEnd
+ FileCreated / FileEdited / FileDeleted / ErrorOccurred / CostThresholdReached
```

### 5 种动作类型

1. **Shell Command** — lint、test、format、deploy
2. **LLM Context Injection** — 向对话注入额外指令
3. **Agent Verification Loop** — 独立 Agent 验证操作安全性
4. **Webhook** — 通知 Slack、PagerDuty 等外部系统
5. **JavaScript Function** — 执行任意 JS 逻辑

### 实战示例

**自动 Lint（写入后自动格式化）：**

```json
{
  "name": "Auto Lint on Write",
  "when": { "type": "postToolUse", "toolTypes": ["write"] },
  "then": { "type": "runCommand", "command": "npx eslint --fix ${file}", "timeout": 30000 }
}
```

**自动测试（编辑后运行相关测试）：**

```json
{
  "name": "Auto Test Related",
  "when": { "type": "postToolUse", "toolTypes": ["write"], "filePattern": "src/**/*.ts" },
  "then": {
    "type": "runCommand",
    "command": "npm test -- --related ${file} --passWithNoTests",
    "onFailure": "injectContext",
    "failureMessage": "测试失败，请修复：\n${output}"
  }
}
```

**Slack 通知（会话结束时汇报）：**

```json
{
  "name": "Slack Session Summary",
  "when": { "type": "sessionEnd" },
  "then": {
    "type": "webhook",
    "url": "https://hooks.slack.com/services/T00/B00/xxx",
    "body": { "text": "🤖 会话结束 | 成本：$${totalCost} | 变更：${filesChanged} 个文件" }
  }
}
```

**安全审查（Bash 命令执行前验证）：**

```json
{
  "name": "Security Review on Bash",
  "when": { "type": "preToolUse", "toolTypes": ["bash"] },
  "then": {
    "type": "agentVerification",
    "prompt": "审查命令安全性：1)破坏性操作 2)敏感路径 3)注入风险。命令：${toolInput}",
    "onReject": "block"
  }
}
```

失败处理策略：`"warn"`（记录继续）、`"block"`（阻止操作）、`"injectContext"`（注入错误让 Agent 自修复）。


---

## 5. MCP 工具集成

### 工具池组装：缓存稳定性优化

源码中最精妙的设计之一 — 工具列表排序直接影响 Prompt Cache 命中率：

```typescript
// tools.ts — assembleToolPool()
// 内置工具排前面作为缓存前缀，MCP 工具排后面
return uniqBy(
  [...builtInTools].sort(byName)              // 稳定前缀
    .concat(allowedMcpTools.sort(byName)),     // 可变后缀
  'name',
)
// 服务端在最后一个内置工具后设置缓存断点
```

```text
❌ 混合排序：新增 mcp_api_call 插入内置工具之间 → 所有下游缓存失效 → 10x 成本
✅ 分区排序：新增 MCP 工具只影响后缀区域 → 内置工具缓存不受影响 → 省 90%
```

### MCP Skills 与资源工具

```typescript
// MCP_SKILLS 特性开关：从 MCP Server 加载 prompt-type 命令作为技能
if (feature('MCP_SKILLS')) {
  allSkills.push(...await loadMcpSkills(mcpServers))
}

// ListMcpResourcesTool — 列出 MCP Server 资源（类似 ls）
// ReadMcpResourceTool  — 读取 MCP 资源内容（类似 cat）
```

---

## 6. 工作流脚本系统

通过 `WORKFLOW_SCRIPTS` 特性开关控制，`WorkflowTool` 执行多步骤自动化流程：

```yaml
# .claude/workflows/pr-review.yml
name: PR Review Workflow
steps:
  - name: fetch-changes
    action: bash
    command: "git diff main...HEAD --name-only"
  - name: analyze
    action: skill
    skill: code-review
    arguments:
      files: "{{steps.fetch-changes.output}}"
  - name: test
    action: bash
    command: "npm test -- --coverage"
  - name: report
    action: skill
    skill: review-report
    arguments:
      analysis: "{{steps.analyze.output}}"
      testResults: "{{steps.test.output}}"
```

来源：Bundled Workflows（内置）+ User-defined（`.claude/workflows/` 目录）。

---

## 7. Bridge/IDE 双向通信

Bridge 是 Claude Code 与 IDE 之间的双向通信层，也是一个扩展点：

```typescript
// bridgeMain.ts 关键设计：
const config = {
  auth: 'JWT',                          // JWT 认证
  maxSessions: 32,                      // 最多 32 并发会话
  sleepDetection: 5000,                 // 系统休眠检测阈值 5s
  reconnect: { initial: 2000, max: 120000, giveUp: 600000 },  // 退避重连
  trustedDevice: true,                  // 设备信任 Token
}

// 安全命令白名单 — 只有这些命令可通过 Bridge 执行
const BRIDGE_SAFE_COMMANDS = ['compact', 'clear', 'cost', 'summary', 'releaseNotes', 'files']

// Git Worktree 集成 — 为子 Agent 创建隔离工作环境
await createAgentWorktree(sessionId, branchName)
await removeAgentWorktree(sessionId)  // 会话结束后清理
```

---

## 8. 动态工具发现（ToolSearchTool）

当工具池很大时，将所有定义放入系统提示消耗大量 Token。解决方案：

```text
工具数 ≤ 30：所有工具定义直接放入系统提示
工具数 > 30：只放核心工具 + ToolSearchTool（延迟加载）
```

```typescript
// ToolSearchTool — "搜索工具的工具"
{
  name: "ToolSearch",
  description: "搜索可用工具。不确定用哪个工具时使用。",
  execute: async ({ query }) => {
    const matches = searchTools(query, allRegisteredTools)
    return matches.map(t => ({ name: t.name, description: t.description }))
    // 只返回摘要，Agent 决定使用后才加载完整 Schema
  }
}

// 乐观检查：Agent 请求未加载工具时，先 O(1) 查注册表
function optimisticToolCheck(name: string): Tool | null {
  return toolRegistry.get(name) ?? null  // 存在则直接加载，否则触发搜索
}
```


---

## 9. 设计你自己的 Agent 扩展系统

### 核心接口设计

```typescript
// 统一扩展注册中心
interface ExtensionRegistry {
  registerSkill(skill: SkillDefinition): void
  registerPlugin(plugin: PluginManifest): void
  registerHook(hook: HookDefinition): void
  registerMcpServer(server: McpServerConfig): void
}

// Hook 事件分发器
class HookDispatcher {
  private hooks: Map<string, HookDefinition[]> = new Map()

  register(hook: HookDefinition): void {
    const list = this.hooks.get(hook.when.type) || []
    list.push(hook)
    list.sort((a, b) => (a.priority || 0) - (b.priority || 0))
    this.hooks.set(hook.when.type, list)
  }

  async dispatch(event: string, ctx: HookContext): Promise<void> {
    for (const hook of this.hooks.get(event) || []) {
      if (this.matches(hook, ctx)) await executeHook(hook, ctx)
    }
  }

  private matches(hook: HookDefinition, ctx: HookContext): boolean {
    if (hook.when.toolTypes && !hook.when.toolTypes.includes(ctx.toolType)) return false
    if (hook.when.filePattern && !minimatch(ctx.filePath, hook.when.filePattern)) return false
    return true
  }
}

// 工具池组装（缓存稳定性）
function assembleToolPool(builtIn: Tool[], mcp: Tool[], plugin: Tool[]): Tool[] {
  const stablePrefix = [...builtIn].sort(byName)
  const dynamicSuffix = [...mcp, ...plugin].sort(byName)
  return uniqBy(stablePrefix.concat(dynamicSuffix), 'name')
}
```

### 扩展加载流程

```text
Agent 启动
├─ 1. 加载内置技能 → 2. 加载内置插件（命令+技能）
├─ 3. 扫描用户技能目录 → 4. 加载第三方插件
├─ 5. 连接 MCP Servers（获取工具+技能）
├─ 6. 加载 Hook 配置 → 7. 加载工作流定义
├─ 8. 组装工具池（分区排序，内置前缀 + MCP/插件后缀）
├─ 9. 工具数 > 阈值 → 启用 ToolSearchTool
└─ 10. 初始化 Bridge（IDE 模式）
```

---

## 10. 扩展系统设计检查清单

- [ ] **技能**：多层来源 + Frontmatter 元数据 + 参数替换 + 动态发现 + Token 估算只基于元数据
- [ ] **插件**：标准 Manifest + 错误隔离 + 权限声明
- [ ] **Hook**：完整生命周期 + 5 种动作 + 工具/文件过滤 + 失败策略 + 超时 + 优先级
- [ ] **MCP**：分区排序保缓存 + 命名空间前缀 + 资源访问 + MCP 技能
- [ ] **工具管理**：延迟加载（ToolSearchTool）+ 乐观查找 + Schema 验证 + 权限自声明
- [ ] **Bridge**：JWT 认证 + 命令白名单 + 退避重连 + 多会话 + 休眠检测
- [ ] **安全**：第三方沙箱隔离 + 不可绕过权限 + Shell 超时和资源限制

---

## 🎬 推荐视频资源

### 🌐 YouTube

- [Anthropic - Tool Use with Claude](https://www.youtube.com/watch?v=kSHiV0XKHSA) — Claude 工具使用官方教程
- [Anthropic - Building Effective Agents](https://www.youtube.com/watch?v=a_bCEBNtz_4) — 构建高效 Agent 官方指南
- [Matthew Berman - Claude Code Leak Analysis](https://www.youtube.com/watch?v=hkhDdcM5V94) — Claude Code 泄露深度分析
- [AI Jason - MCP Explained](https://www.youtube.com/watch?v=oS4aSv08FJg) — MCP 协议详解

### 📺 B站

- [Claude Code 源码泄露分析](https://www.bilibili.com/video/BV1Bm421N7BH) — 中文架构分析

### 📖 参考资料

- [Model Context Protocol Specification](https://modelcontextprotocol.io/) — MCP 协议规范
- [Claude Code Hooks Documentation](https://docs.anthropic.com/en/docs/claude-code/hooks) — 官方 Hook 文档
- [PromptLayer - Claude Code Agent Loop](https://blog.promptlayer.com/claude-code-behind-the-scenes-of-the-master-agent-loop/) — Agent 主循环解析
- [alex000kim - Claude Code Source Analysis](https://alex000kim.com/posts/2026-03-31-claude-code-source-leak/) — 源码分析
