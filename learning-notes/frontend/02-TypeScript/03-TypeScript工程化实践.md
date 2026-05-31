# TypeScript 工程化实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. tsconfig.json 配置

<!-- version-check: TypeScript 6.0 stable (last JS-based, 2026-03), TypeScript 7.0 Beta (Go rewrite, 2026-04), checked 2026-05-31 -->

> 🔄 更新于 2026-05-31：当前稳定线是 **TypeScript 6.0**（2026-03 正式发布）。官方明确 6.0 是**最后一个基于 JavaScript 代码库**的版本，由 5.9（2025-08 发布，引入 `import defer`、`tsc --init` 精简 tsconfig）演进而来。TypeScript 7.0 Beta（2026-04 发布）将编译器用 Go 重写（Project Corsa），构建速度比 6.0 快约 10 倍，与 6.0 **并行开发**——生态完成迁移前 6.x 仍是生产稳定线，7.0 作为预览加速本地类型检查。
> <!-- 修复于 2026-05-31: 原文称"以 5.9 为稳定线"，与本文第 5.1 节"与 TypeScript 6 并行"自相矛盾，且与官方不符（6.0 已于 2026-03 发布、是最后一个 JS 版本）。统一更正为 6.0 为稳定线 -->
> ⚠️ 待确认：`--strictInference` 是否为 5.9/6.0 官方默认启用项（官方 5.9 release notes 未明确列出，仅二手博客提及，故从正文移除）。

来源：[Announcing TypeScript 7.0 Beta](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0-beta/) | [TypeScript Dev Blog（6.0 是最后一个 JS 版本）](https://devblogs.microsoft.com/typescript/) | [TypeScript 5.9 文档](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html)

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


## 5. TypeScript 7.0 Beta（Project Corsa）

> 🔄 更新于 2026-05-18

<!-- version-check: TypeScript 7.0 Beta (2026-04), tsgo / @typescript/native-preview, checked 2026-05-18 -->

TypeScript 7.0 Beta 于 2026 年 4 月发布，是 TypeScript 自创建以来最大的架构变更：编译器从 TypeScript/JavaScript 自举完整迁移为 Go 实现，并引入共享内存并行。来源：[Announcing TypeScript 7.0 Beta](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0-beta/)、[TypeScript 7 Project Corsa](https://www.alexcloudstar.com/blog/typescript-7-project-corsa-go-compiler-2026)

### 5.1 性能与定位

- 构建速度相对 TypeScript 6.0 提升约 10 倍（来源数据由 Microsoft 公开）
- 设计上与 TypeScript 6.0 并行运行：`tsgo` 二进制独立分发，`@typescript/native-preview` npm 包可作为预览
- TypeScript 6.0（最后一个基于 JavaScript 代码库的版本，由 5.9 演进）在生态完成迁移前继续作为稳定线维护
- RC 里程碑见 [microsoft/typescript-go Milestone 1](https://github.com/microsoft/typescript-go/milestone/1)

### 5.2 安装预览版

```bash
# 安装预览版（不会替换现有 tsc）
npm i -D @typescript/native-preview

# 使用 tsgo 二进制
npx tsgo --version
npx tsgo --noEmit          # 类型检查
npx tsgo -p tsconfig.json  # 按配置构建
```

### 5.3 与现有项目并存

```jsonc
// package.json — 同时保留 tsc 和 tsgo 脚本
{
  "scripts": {
    "type-check": "tsc --noEmit",                   // TS 6.0 稳定路径
    "type-check:fast": "tsgo --noEmit",             // TS 7.0 Beta 加速
    "build": "tsc -p tsconfig.build.json",          // 生产构建仍用 6.0
    "ci:check": "tsgo --noEmit && tsc --noEmit"    // 双校验，确认行为一致
  }
}
```

### 5.4 迁移注意事项

```
迁移建议（2026-Q2）
├── 本地 type-check 可切换 tsgo，CI 双跑校验
├── tsc-watch / IDE Language Server 仍以 6.0 为准
├── 自定义 transformer / ts-patch 等深度集成尚未适配 Go 版
└── 等待 7.0 RC 后再考虑生产构建迁移
```

> ⚠️ 待确认：vue-tsc、ts-jest、ts-node 等深度依赖 TypeScript API 的工具对 tsgo 的兼容情况随版本快速变化，请在升级前查阅各工具的 TS 7 issue。

