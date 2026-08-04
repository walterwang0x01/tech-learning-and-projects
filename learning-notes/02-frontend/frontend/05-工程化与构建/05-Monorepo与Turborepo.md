# Monorepo 与 Turborepo
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Monorepo 概念

- 单一仓库管理多个项目/包
- 优势：代码共享、统一版本管理、原子提交、统一CI/CD
- 工具：pnpm workspace、Turborepo、Nx、Lerna

## 2. pnpm workspace 基础

```yaml
# pnpm-workspace.yaml
packages:
  - 'packages/*'
  - 'apps/*'
```

```
monorepo/
├── apps/
│   ├── web/          # 前端应用
│   └── admin/        # 管理后台
├── packages/
│   ├── ui/           # 共享UI组件库
│   ├── utils/        # 工具函数
│   └── config/       # 共享配置
├── pnpm-workspace.yaml
├── package.json
└── turbo.json
```

```json
// packages/ui/package.json
{ "name": "@my/ui", "version": "1.0.0" }

// apps/web/package.json
{
  "name": "@my/web",
  "dependencies": {
    "@my/ui": "workspace:*",
    "@my/utils": "workspace:*"
  }
}
```

## 3. Turborepo

```json
// turbo.json
{
  "$schema": "https://turborepo.com/schema.json",
  "tasks": {
    "build": {
      "dependsOn": ["^build"],
      "outputs": ["dist/**", ".next/**"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "lint": {},
    "test": {
      "dependsOn": ["build"]
    }
  }
}
```

```bash
# 运行所有包的 build
turbo run build

# 只运行特定包
turbo run build --filter=@my/web

# 并行运行 dev
turbo run dev

# 远程缓存（团队共享构建缓存）
npx turbo login
npx turbo link
```

## 4. 共享配置

```javascript
// packages/config/eslint.js
export default [
  // 共享的 ESLint 配置
];

// packages/config/tsconfig.base.json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2020",
    "module": "ESNext"
  }
}

// apps/web/tsconfig.json
{
  "extends": "@my/config/tsconfig.base.json",
  "compilerOptions": { "jsx": "react-jsx" }
}
```
