# 包管理器 npm / yarn / pnpm
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. npm

```bash
# 初始化
npm init -y

# 安装依赖
npm install lodash              # 生产依赖
npm install -D typescript       # 开发依赖
npm install -g create-react-app # 全局安装

# 常用命令
npm run dev          # 运行脚本
npm update           # 更新依赖
npm outdated         # 查看过期依赖
npm list --depth=0   # 查看已安装依赖
npm cache clean --force # 清理缓存

# npx（执行本地或远程包）
npx create-react-app my-app
npx tsc --init
```

### package.json 关键字段

```json
{
  "name": "my-app",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "lint": "eslint src --ext .ts,.tsx",
    "test": "vitest run"
  },
  "dependencies": {},
  "devDependencies": {},
  "engines": { "node": ">=18" }
}
```

### 语义化版本

```
^1.2.3  → >=1.2.3 <2.0.0（兼容补丁和次版本更新）
~1.2.3  → >=1.2.3 <1.3.0（仅兼容补丁更新）
1.2.3   → 精确版本
>=1.2.3 → 大于等于
*       → 任意版本
```

## 2. pnpm（推荐）

> 🔄 更新于 2026-05-13

<!-- version-check: pnpm 11.x (stable), checked 2026-05-13 -->

**pnpm 11**（2026-05 发布）：ESM-only 分发、SQLite 存储索引替代 JSON-per-package、全局安装隔离、更严格的供应链安全默认值。

```bash
# 安装
npm install -g pnpm

# 基本命令
pnpm install          # 安装所有依赖
pnpm add lodash       # 添加依赖
pnpm add -D typescript
pnpm remove lodash    # 移除依赖
pnpm run dev
pnpm dlx create-react-app my-app  # 类似 npx

# 优势：
# 1. 硬链接 + 内容寻址存储，节省磁盘空间
# 2. 非扁平化 node_modules，避免幽灵依赖
# 3. 安装速度快
```

### pnpm workspace（Monorepo）

```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

```bash
# workspace 命令
pnpm --filter @my/web add lodash     # 给特定包添加依赖
pnpm --filter @my/web run build      # 运行特定包的脚本
pnpm -r run build                    # 所有包执行 build
```

## 3. yarn

```bash
yarn init -y
yarn add lodash
yarn add -D typescript
yarn remove lodash
yarn run dev

# Yarn Berry (v2+)
yarn set version berry
yarn dlx create-react-app my-app
```

## 4. 对比

| 特性 | npm | yarn | pnpm | Bun（1.3+） |
|------|-----|------|------|-------------|
| 磁盘空间 | 大 | 大 | 小（硬链接） | 中（内容寻址） |
| 安装速度 | 中 | 快 | 最快 | 最快级（与 pnpm 接近或更快） |
| 幽灵依赖 | 有 | 有 | 无 | 无（isolated installs） |
| Monorepo | workspaces | workspaces | workspace | workspace + catalogs |
| Lock 文件 | package-lock.json | yarn.lock | pnpm-lock.yaml | bun.lock |
| 角色范围 | 仅包管理 | 仅包管理 | 仅包管理 | 包管理 + Runtime + bundler + test |

## 5. Bun 1.3：Runtime + 包管理 + 全栈工具链

> 🔄 更新于 2026-05-18

<!-- version-check: Bun 1.3.14 (last Zig version), Rust rewrite merged 2026-05-14, checked 2026-05-20 -->

[Bun](https://bun.com/) 自 1.0（2025-09）起进入主流视野，2025-10 发布的 1.3 是把它从"快的 Node 替代"推到"全栈一体化运行时"的关键版本。**Bun 同时是 Runtime、包管理器、bundler、test runner、TypeScript 编译器和 SQL/Redis 客户端**。

### 5.1 1.3 关键能力

| 能力 | 说明 |
| ---- | ---- |
| 内置 SQL 客户端 | `Bun.SQL` 统一 API，支持 MySQL / PostgreSQL / SQLite，无需第三方驱动 |
| 内置 Redis 客户端 | 据 Bun 团队基准比 ioredis 快约 7.9x |
| 零配置全栈 dev | `bun dev` 直接跑 HTML 入口，自动转译 JS / TS / CSS / React，HMR 内置 |
| Workspace 增强 | Isolated installs、catalogs、minimumRelease，向 pnpm 看齐 |
| `bun install` | 流式写入 tarball（17x 更省内存），5.5x 更快 gzip（zlib-ng） |
| `bun test` | `--parallel` / `--isolate` / `--shard` / `--changed`，在文件间清理 microtask、socket、timer，干净 VM 全局对象 |

来源：[Bun 1.3 Blog](https://bun.com/1.3)、[Bun 1.3.13 Release Notes](https://bun.com/blog/bun-v1.3.13)、[InfoQ: Bun 1.3 Database Clients](https://www.infoq.com/news/2026/01/bun-v3-1-release/)

### 5.2 包管理常用命令

```bash
# 安装 Bun
curl -fsSL https://bun.com/install | bash

# 项目初始化
bun init

# 依赖管理（API 与 npm/pnpm 接近）
bun install                  # 等价于 npm install
bun add lodash               # 添加依赖
bun add -d typescript        # devDependency
bun add -g create-react-app  # 全局
bun remove lodash

# 运行脚本与可执行文件
bun run dev                  # 跑 package.json scripts
bun x create-react-app my-app  # 等价于 npx
bun --filter @my/web run build  # 类似 pnpm --filter
```

### 5.3 内置 SQL / Redis 客户端示例

```ts
// PostgreSQL（不需要 pg 驱动）
import { SQL } from "bun";

const sql = new SQL("postgres://user:pass@localhost/app");
const users = await sql`select * from users where id = ${userId}`;

// MySQL（同一 API，只换连接串）
const mysql = new SQL("mysql://user:pass@localhost/app");

// 内置 Redis
import { redis } from "bun";

await redis.set("session:42", JSON.stringify({ uid: 42 }));
const s = await redis.get("session:42");
```

### 5.4 与 Node.js + pnpm 的取舍

| 场景 | 推荐 |
| ---- | ---- |
| 生产长期运行的企业应用 | Node.js 24 LTS + pnpm 11（生态最稳） |
| 个人项目 / Side project / Edge 部署 | Bun 1.3 单工具搞定全栈 |
| 极端 IO 密集型脚本（流式 tar、爬虫） | Bun（内存与 IO 优势明显） |
| 严格依赖 Node 原生 API 兼容性 | Node.js（Bun 仍在补齐 Node 兼容层） |
| Monorepo 多包工作流 | pnpm 11（catalogs 体验更成熟） |

> 🔄 更新于 2026-05-20

**Bun Rust 重写已正式合并**（2026-05-14）：Bun 创始人 Jarred Sumner 使用 Claude 将约 96 万行 Zig 代码移植为 Rust，5 月 14 日合并到主分支（2188 个文件变更，100 万+ 行重写）。v1.3.14 是最后一个 Zig 版本。Rust 重写通过了 Bun 99.8% 的测试套件，修复了部分内存泄漏，二进制体积缩小 3-8 MB。这标志着 Bun 从 Zig 时代进入 Rust 时代，是 JavaScript 运行时历史上最大规模的 AI 辅助代码迁移。来源：[The Register](https://theregister.com/devops/2026/05/14/anthropics-bun-rust-rewrite-merged-at-speed-of-ai/5240381)、[Heise](https://www.heise.de/en/news/AI-Porting-Claude-Rewrites-Bun-Codebase-in-Rust-11294318.html)

### 5.5 在已有项目里只把 Bun 当包管理器

如果暂时不想替换 Runtime，可以仅用 Bun 做安装加速：

```bash
# 在 Node 项目里仅用 Bun 安装依赖（生成 bun.lock）
bun install

# CI 中保留 npm/pnpm lock 也可以共存：用环境变量切换
BUN_INSTALL_LOCKFILE_PATH=bun.lock bun install
```

注意：`bun.lock` 与 `package-lock.json` / `pnpm-lock.yaml` 不通用，混用会导致依赖解析不一致，团队内需统一选一个。

