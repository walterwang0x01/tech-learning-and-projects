# TypeScript 工程化实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. tsconfig.json 配置

<!-- version-check: TypeScript 6.0.3 stable (last JS-based, 2026-03), TypeScript 7.0 RC 7.0.1-rc (Go rewrite, 2026-06-18), checked 2026-07-08 -->

> 🔄 更新于 2026-07-08：**TypeScript 7.0 RC**（`7.0.1-rc`，2026-06-18）已发布，可通过 `npm install -D typescript@rc` 安装，`npx tsc --version` 即报告 Go 原生编译器。官方预计 **GA 稳定版在 RC 后约一个月内**发布；稳定版 **programmatic API 推迟到 7.1**，typescript-eslint 等深度依赖 TS API 的工具仍应通过 `@typescript/typescript6` 与 7.0 并行运行。当前生产稳定线仍是 **TypeScript 6.0**（2026-03，最后一个 JS 代码库版本）。
>
> 🔄 更新于 2026-05-31：TypeScript 7.0 Beta（2026-04）将编译器用 Go 重写（Project Corsa），构建速度比 6.0 快约 10 倍，与 6.0 **并行开发**——生态完成迁移前 6.x 仍是生产稳定线，7.0 作为预览加速本地类型检查。
> <!-- 修复于 2026-05-31: 原文称"以 5.9 为稳定线"，与本文第 5.1 节"与 TypeScript 6 并行"自相矛盾，且与官方不符（6.0 已于 2026-03 发布、是最后一个 JS 版本）。统一更正为 6.0 为稳定线 -->
> ⚠️ 待确认：`--strictInference` 是否为 5.9/6.0 官方默认启用项（官方 5.9 release notes 未明确列出，仅二手博客提及，故从正文移除）。

来源：[Announcing TypeScript 7.0 RC](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0-rc/) | [Announcing TypeScript 7.0 Beta](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0-beta/) | [TypeScript Dev Blog（6.0 是最后一个 JS 版本）](https://devblogs.microsoft.com/typescript/)

```jsonc
{
  "compilerOptions": {
    // 目标与模块
    "target": "ES2020",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],

    // 严格模式（推荐全部开启）
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,

    // 路径与输出
    "baseUrl": ".",
    "paths": {
      "@/*": ["src/*"],
      "@components/*": ["src/components/*"]
    },
    "outDir": "dist",
    "rootDir": "src",

    // JSX（React项目）
    "jsx": "react-jsx",

    // 互操作
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "resolveJsonModule": true,
    "isolatedModules": true,

    // 声明文件
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,

    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

## 2. 声明文件

```typescript
// types/global.d.ts — 全局类型声明
declare global {
  interface Window {
    __APP_CONFIG__: {
      apiUrl: string;
      env: 'development' | 'production';
    };
  }
}

// 模块声明（为无类型的库添加类型）
declare module '*.css' {
  const classes: { [key: string]: string };
  export default classes;
}

declare module '*.svg' {
  const content: string;
  export default content;
}

declare module 'some-untyped-lib' {
  export function doSomething(input: string): number;
}
```

## 3. 与 React 集成

```typescript
// 组件 Props 类型
interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  disabled?: boolean;
  onClick?: (e: React.MouseEvent<HTMLButtonElement>) => void;
  children: React.ReactNode;
}

const Button: React.FC<ButtonProps> = ({ variant = 'primary', children, ...props }) => {
  return <button className={variant} {...props}>{children}</button>;
};

// 事件类型
const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {};
const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {};

// Ref 类型
const inputRef = useRef<HTMLInputElement>(null);

// 泛型组件
interface ListProps<T> {
  items: T[];
  renderItem: (item: T) => React.ReactNode;
}

function List<T>({ items, renderItem }: ListProps<T>) {
  return <ul>{items.map(renderItem)}</ul>;
}
```

## 4. 与 Vue 集成

```typescript
// defineComponent + TypeScript
<script setup lang="ts">
import { ref, computed } from 'vue';

interface User {
  id: number;
  name: string;
}

const props = defineProps<{
  title: string;
  users: User[];
  count?: number;
}>();

const emit = defineEmits<{
  (e: 'update', id: number): void;
  (e: 'delete', id: number): void;
}>();

const search = ref<string>('');
const filteredUsers = computed<User[]>(() =>
  props.users.filter(u => u.name.includes(search.value))
);
</script>
```


## 5. TypeScript 7.0 RC（Project Corsa）

> 🔄 更新于 2026-07-08

<!-- version-check: TypeScript 7.0 RC 7.0.1-rc (2026-06-18), @typescript/typescript6 side-by-side, checked 2026-07-08 -->

TypeScript 7.0 RC 于 2026 年 6 月 18 日发布（feature-frozen），是 TypeScript 自创建以来最大的架构变更：编译器从 TypeScript/JavaScript 自举完整迁移为 Go 实现，并引入共享内存并行。RC 起 `tsc` 入口已收敛到标准 `typescript` 包（`typescript@rc`），不再仅限 `@typescript/native-preview` 的 `tsgo` 二进制。

来源：[Announcing TypeScript 7.0 RC](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0-rc/) · [InfoWorld 报道（2026-07-01）](https://www.infoworld.com/article/4191918/typescript-7-0-reaches-release-candidate-stage.html) · [TypeScript 7.0 Beta 公告](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0-beta/)

### 5.1 性能与定位

- 构建速度相对 TypeScript 6.0 提升约 10 倍（VS Code 1.5M 行：77.8s → 7.5s；Playwright 11.1s → 1.1s；内存约减半）
- 解析、类型检查、emit 多步骤并行化，大 monorepo 收益最明显
- TypeScript 6.0（最后一个基于 JavaScript 代码库的版本）在生态完成迁移前继续作为稳定线维护
- 稳定 programmatic API 推迟到 **7.1**；7.0 RC 窗口回归请提交 [microsoft/typescript-go](https://github.com/microsoft/typescript-go/issues)

### 5.2 安装 RC 版

```bash
# 推荐：RC 已收敛到标准 typescript 包
npm install -D typescript@rc
npx tsc --version          # Version 7.0.1-rc
npx tsc --noEmit           # 类型检查

# 旧预览路径（nightlies 仍可用，但 RC 后优先 typescript@rc）
npm i -D @typescript/native-preview
npx tsgo --noEmit
```

### 5.2.1 与 TypeScript 6.0 并行（typescript-eslint 等）

```bash
# 7.0 的 tsc 走 typescript@rc，工具链 API 仍用 6.0
npm install -D typescript@rc
npm install -D typescript@npm:@typescript/typescript6

# tsc     → TypeScript 7.0（Go 原生）
# tsc6    → TypeScript 6.0（供 typescript-eslint 等 peer 依赖）
```

来源：[Announcing TypeScript 7.0 RC — Running Side-by-Side](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0-rc/)

### 5.3 与现有项目并存

```jsonc
// package.json — 6.0 稳定构建 + 7.0 RC 加速校验
{
  "scripts": {
    "type-check": "tsc6 --noEmit",                  // TS 6.0（@typescript/typescript6）
    "type-check:fast": "tsc --noEmit",              // TS 7.0 RC（typescript@rc）
    "build": "tsc6 -p tsconfig.build.json",         // 生产构建仍用 6.0
    "ci:check": "tsc --noEmit && tsc6 --noEmit"     // 双校验，确认行为一致
  }
}
```

### 5.4 迁移注意事项

```
迁移建议（2026-Q3）
├── 未上 6.0 的项目先升到 6.0 并清理弃用项
├── 本地 / CI 可 `npm install -D typescript@rc` 跑 `tsc --noEmit` 做基准测试
├── typescript-eslint 等 API 依赖工具用 @typescript/typescript6 并行
├── IDE 可装 TypeScript Native Preview 扩展体验 LSP 加速
├── 自定义 transformer / ts-patch 等深度集成尚未适配 Go 版
└── 生产构建切换等 7.0 GA 公告 + 自有测试套件全绿后再执行
```

> ⚠️ 待确认：vue-tsc、ts-jest、ts-node 等深度依赖 TypeScript API 的工具对 tsgo 的兼容情况随版本快速变化，请在升级前查阅各工具的 TS 7 issue。

