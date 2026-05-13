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

| 特性 | npm | yarn | pnpm |
|------|-----|------|------|
| 磁盘空间 | 大 | 大 | 小（硬链接） |
| 安装速度 | 中 | 快 | 最快 |
| 幽灵依赖 | 有 | 有 | 无 |
| Monorepo | workspaces | workspaces | workspace |
| Lock 文件 | package-lock.json | yarn.lock | pnpm-lock.yaml |
