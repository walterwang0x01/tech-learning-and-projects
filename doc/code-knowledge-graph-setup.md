# 代码知识图谱工具安装指南

> 给 AI 编程工具（Kiro / Claude Code / Cursor 等）装上"代码记忆"——让 agent 不再靠 grep 逐文件扫描，而是一次查询就拿到完整的调用链、依赖关系、影响半径。

## 为什么需要这个

AI agent 探索代码时，默认行为是反复 grep/read 文件来拼凑上下文。一个 900 文件的项目，agent 可能要 20+ 次工具调用才搞明白一个函数的调用关系。

代码知识图谱**预先索引**整个代码库的结构（符号、调用、导入、继承），agent 一次 MCP 工具调用就拿到答案。实测效果：

- token 消耗降低 ~47%
- 工具调用次数减少 ~58%
- 响应速度提升 ~22%

## 我们用了两个工具（互补，不冲突）

| | CodeGraph | GitNexus |
|---|---|---|
| **定位** | 快速实时索引 | 深度架构分析 |
| **核心能力** | 符号搜索、调用图、自动 watch | 执行流追踪、社区聚类、影响半径、Cypher 查询 |
| **更新策略** | 文件改动后 2 秒自动更新 | 手动 `gitnexus analyze` |
| **适用场景** | 日常编码：快速查"谁调用了这个函数" | 架构决策：改大模块前看影响范围 |
| **协议** | MIT | PolyForm Noncommercial（非商业免费） |
| **存储** | SQLite（轻） | LadybugDB 图数据库（重） |

**日常 90% 用 CodeGraph（快、自动），做架构分析时用 GitNexus（深、全）。**

---

## 安装步骤

### 前置条件

- macOS / Linux
- Node.js 20+（`node --version` 检查）
- Kiro IDE（或其他支持 MCP 的 AI 工具）

### 1. 安装 CodeGraph

```bash
# 方式 A：npm（推荐，国内网络稳定）
npm install -g @colbymchenry/codegraph

# 方式 B：官方安装脚本（需要能直连 GitHub）
curl -fsSL https://raw.githubusercontent.com/colbymchenry/codegraph/main/install.sh | sh
```

验证：

```bash
codegraph version
# 应输出版本号，如 1.0.1
```

### 2. 安装 GitNexus

```bash
npm install -g gitnexus
```

> ⚠️ 安装较慢（5-7 分钟），因为要编译 tree-sitter native bindings 和 LadybugDB。耐心等待。
>
> 如果 npm 11 报错 `Cannot destructure property 'package'`，换用：
> ```bash
> pnpm --allow-build=@ladybugdb/core --allow-build=gitnexus --allow-build=tree-sitter dlx gitnexus@latest analyze
> ```

验证：

```bash
gitnexus --version
# 应输出版本号，如 1.6.7
```

### 3. 配置 Kiro MCP

#### 方式 A：自动配置（推荐）

```bash
# CodeGraph 自动写入 ~/.kiro/settings/mcp.json
codegraph install --target=kiro --location=global --yes

# GitNexus 自动配置（检测已安装的 IDE）
gitnexus setup
```

#### 方式 B：手动配置

编辑 `~/.kiro/settings/mcp.json`（全局生效）或 `项目/.kiro/settings/mcp.json`（仅该项目）：

```json
{
  "mcpServers": {
    "codegraph": {
      "type": "stdio",
      "command": "codegraph",
      "args": ["serve", "--mcp"]
    },
    "gitnexus": {
      "command": "gitnexus",
      "args": ["mcp"]
    }
  }
}
```

### 4. 索引你的项目

```bash
cd /path/to/your/project

# CodeGraph：秒级完成，之后自动 watch
codegraph init

# GitNexus：几十秒，含聚类和流追踪
gitnexus analyze --skip-skills --skip-agents-md
```

> `--skip-skills --skip-agents-md` 避免 GitNexus 在项目根目录生成 AGENTS.md 等文件。

### 5. 重启 Kiro

重启后在 Kiro 侧边栏 → MCP Servers 面板检查：

- **codegraph** — 绿灯 ✅
- **gitnexus** — 绿灯 ✅

---

## 日常使用

### 无需任何操作

装完后正常跟 Kiro 聊代码就行。当你问结构性问题时，Kiro 会自动选用图谱工具。

### CodeGraph 自动更新

你改了文件 → FSEvents 监听 → 2 秒后索引自动刷新。不需要手动操作。

查看状态：

```bash
cd /path/to/project
codegraph status
```

### GitNexus 手动更新

代码改动较大后（比如 merge 了大 PR），手动刷新：

```bash
cd /path/to/project
gitnexus analyze
```

### Web UI 可视化（GitNexus）

想看代码关系图：

```bash
gitnexus serve
# 浏览器打开 https://gitnexus.vercel.app
# 它会自动连接本地 server，显示所有已索引仓库
```

---

## 能力速查

### CodeGraph 工具（Kiro 自动调用）

| 工具 | 用途 | 示例问题 |
|---|---|---|
| `codegraph_explore` | 一次回答"怎么工作的" | "SceneRouter 怎么路由到各场景的？" |
| `codegraph_search` | 按名字找符号 | "找一下 StatelessIntentRecognizer" |
| `codegraph_callers` | 谁调用了某函数 | "哪些地方调用了 validate_payment？" |
| `codegraph_node` | 一个符号的完整上下文 | "给我看 OrderService 的源码和调用关系" |

### GitNexus 工具（Kiro 自动调用）

| 工具 | 用途 | 示例问题 |
|---|---|---|
| `query` | 按概念搜执行流 | "认证中间件相关的调用链" |
| `context` | 360° 符号视图 | "validateUser 的所有调用者和被调用者" |
| `impact` | 影响半径分析 | "改 UserService 会影响什么？" |
| `detect_changes` | git diff 影响分析 | "我这次改动会破坏哪些流程？" |
| `cypher` | 原始图查询 | 自定义 Cypher 查关系 |

### CLI 常用命令

```bash
# === CodeGraph ===
codegraph init              # 索引当前项目（首次）
codegraph status            # 查看索引状态
codegraph query "函数名"     # CLI 搜索符号
codegraph explore "概念"    # CLI 探索代码
codegraph callers "函数名"  # 查调用者
codegraph impact "符号名"   # 影响分析
codegraph telemetry off     # 关闭匿名统计（可选）

# === GitNexus ===
gitnexus analyze            # 索引/更新当前项目
gitnexus status             # 查看索引状态
gitnexus list               # 列出所有已索引仓库
gitnexus serve              # 启动本地 server（Web UI 用）
gitnexus clean              # 删除当前项目索引
```

---

## 多仓库场景

我们有多个仓库需要索引。每个仓库分别 init：

```bash
# 批量索引
for dir in agenzo agenzo-platform kiro-conduit lark-kiro-bridge ledger-service; do
  cd /Users/administrator/PycharmProjects/$dir
  codegraph init
  gitnexus analyze --skip-skills --skip-agents-md
done
```

GitNexus 支持跨仓库关联（repository groups）：

```bash
# 创建仓库组
gitnexus group create agenzo-ecosystem

# 添加成员
gitnexus group add agenzo-ecosystem platform agenzo-platform
gitnexus group add agenzo-ecosystem orchestrator agenzo-agent-orchestrator
gitnexus group add agenzo-ecosystem ledger ledger-service

# 同步契约（提取 HTTP 契约并跨仓匹配）
gitnexus group sync agenzo-ecosystem
```

---

## 卸载

```bash
# CodeGraph
codegraph uninstall          # 移除 MCP 配置
npm uninstall -g @colbymchenry/codegraph
# 各项目的 .codegraph/ 目录需手动删除

# GitNexus
gitnexus uninstall --force   # 移除 MCP/skills/hooks 配置
npm uninstall -g gitnexus
# 各项目的 .gitnexus/ 目录需手动删除
```

---

## FAQ

**Q: 两个工具会冲突吗？**

不会。它们通过不同的 MCP server 暴露不同的工具名，Kiro 按需选用。

**Q: 对性能有影响吗？**

CodeGraph 的 auto-sync 后台 watch 进程内存占用极低（~20MB）。GitNexus 不常驻后台，只在 Kiro 需要时通过 MCP 启动。

**Q: 支持哪些语言？**

两者都覆盖：Python / TypeScript / JavaScript / Vue / Go / Rust / Java / C# / PHP / Ruby / Swift / Kotlin 等 20+ 语言。

**Q: 项目很小（几十个文件）有必要装吗？**

CodeGraph 对小项目收益有限（Kiro 自己 grep 就够快）。GitNexus 的聚类/流追踪对理解不熟悉的项目结构仍有帮助。

**Q: GitNexus 的 PolyForm Noncommercial 协议怎么理解？**

开发、学习、内部工具优化等非直接商业用途没问题。如果要把 GitNexus 作为商业产品的一部分提供给客户，需要联系 akonlabs.com 购买商业 license。

---

## 参考链接

- CodeGraph：https://github.com/colbymchenry/codegraph
- GitNexus：https://github.com/abhigyanpatwari/GitNexus
- Kiro MCP 配置文档：https://kiro.dev/docs/mcp/configuration/
