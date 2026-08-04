# ESLint 与 Prettier 代码规范
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. ESLint 配置

```javascript
// eslint.config.js（Flat Config，ESLint 9+）
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';

export default [
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    files: ['**/*.{ts,tsx}'],
    plugins: { react, 'react-hooks': reactHooks },
    rules: {
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-console': ['warn', { allow: ['warn', 'error'] }],
    },
  },
  { ignores: ['dist/', 'node_modules/'] },
];
```

## 2. Prettier 配置

```json
// .prettierrc
{
  "semi": true,
  "singleQuote": true,
  "tabWidth": 2,
  "trailingComma": "all",
  "printWidth": 100,
  "bracketSpacing": true,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

## 3. Husky + lint-staged

```bash
# 安装
pnpm add -D husky lint-staged

# 初始化 husky
npx husky init
```

```json
// package.json
{
  "lint-staged": {
    "*.{ts,tsx,js,jsx}": ["eslint --fix", "prettier --write"],
    "*.{css,scss,md,json}": ["prettier --write"]
  }
}
```

```bash
# .husky/pre-commit
npx lint-staged
```

## 4. commitlint

```bash
pnpm add -D @commitlint/cli @commitlint/config-conventional
```

```javascript
// commitlint.config.js
export default {
  extends: ['@commitlint/config-conventional'],
  // feat: 新功能 | fix: 修复 | docs: 文档 | style: 格式
  // refactor: 重构 | test: 测试 | chore: 构建/工具
};
```

```bash
# .husky/commit-msg
npx --no -- commitlint --edit $1
```

## 5. ESLint 10 与 Flat Config 时代（2026）

> 🔄 更新于 2026-04-22

<!-- version-check: ESLint 10.0.0, checked 2026-04-22 -->

ESLint 10.0.0（2026-02）完全移除了 `.eslintrc` 配置系统，强制使用 `eslint.config.js`（Flat Config）。这是 ESLint 历史上最大的配置系统变更。来源：[ESLint Blog](https://eslint.org/blog/)

### 5.1 关键变化

| 变化 | ESLint 9.x | ESLint 10.x |
|------|-----------|-------------|
| 配置文件 | `.eslintrc` 和 `eslint.config.js` 并存 | 仅 `eslint.config.js` |
| Node.js 要求 | ≥ 18.18.0 | ≥ 20.19.0 |
| 旧配置兼容 | `@eslint/eslintrc` 兼容层 | 移除兼容层 |
| 插件加载 | `extends` 字符串 | 直接 import |

### 5.2 Flat Config 完整示例（React + TypeScript）

```javascript
// eslint.config.js — ESLint 10 标准配置
import js from '@eslint/js';
import tseslint from 'typescript-eslint';
import reactPlugin from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import prettier from 'eslint-config-prettier';

export default tseslint.config(
  // 全局忽略
  { ignores: ['dist/', 'node_modules/', '.next/', 'coverage/'] },

  // 基础推荐规则
  js.configs.recommended,
  ...tseslint.configs.recommendedTypeChecked,

  // TypeScript 项目配置
  {
    languageOptions: {
      parserOptions: {
        projectService: true,  // ESLint 10 推荐的类型检查方式
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },

  // React 配置
  {
    files: ['**/*.{tsx,jsx}'],
    plugins: {
      react: reactPlugin,
      'react-hooks': reactHooks,
    },
    rules: {
      ...reactPlugin.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      'react/react-in-jsx-scope': 'off',  // React 17+ 不需要
      'react/prop-types': 'off',          // TypeScript 替代
    },
    settings: { react: { version: 'detect' } },
  },

  // 自定义规则
  {
    files: ['**/*.{ts,tsx}'],
    rules: {
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'no-console': ['warn', { allow: ['warn', 'error'] }],
    },
  },

  // Prettier 兼容（必须放最后）
  prettier,
);
```

### 5.3 从 `.eslintrc` 迁移

```bash
# 使用官方迁移工具
npx @eslint/migrate-config .eslintrc.json

# 或手动迁移核心步骤：
# 1. 删除 .eslintrc.* 文件
# 2. 创建 eslint.config.js
# 3. 将 extends 字符串改为 import
# 4. 将 plugins 字符串改为 import
# 5. 将 env 改为 languageOptions.globals
```

### 5.4 Biome 替代方案

2026 年 [Biome](https://biomejs.dev/) 作为 ESLint + Prettier 的一体化替代方案持续增长，单工具覆盖 lint + format，速度提升 10-100x。适合新项目评估，但 ESLint 生态（插件、规则）仍然更丰富。

### 5.5 2026 年推荐工具链

```
前端代码质量工具链（2026）：
├── ESLint 10 + Flat Config — lint（标准选择）
├── Prettier — format（与 ESLint 互补）
├── Husky + lint-staged — Git hooks
├── commitlint — 提交信息规范
└── 可选：Biome — 一体化替代（新项目可评估）
```
