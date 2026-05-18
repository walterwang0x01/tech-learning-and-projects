# TypeScript 工程化实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. tsconfig.json 配置

<!-- version-check: TypeScript 5.9 stable, TypeScript 7.0 Beta (2026-04), checked 2026-05-18 -->

> 🔄 更新于 2026-05-18：TypeScript 7.0 Beta 已正式发布（2026 年 4 月），编译器使用 Go 重写（Project Corsa），构建速度比 TypeScript 6.0 快约 10 倍。Beta 阶段建议与 5.9 并行使用，正式生产仍以 5.9 为主。TypeScript 5.9（2025-07 发布）继续作为稳定线维护，`--strictInference` 在 `--strict` 下默认启用、`tsc --init` 生成精简 tsconfig、支持 `import defer`。

来源：[Announcing TypeScript 7.0 Beta](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0-beta/) | [TypeScript 5.9 文档](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-5-9.html)

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
- 设计上与 TypeScript 6 并行运行：`tsgo` 二进制独立分发，`@typescript/native-preview` npm 包可作为预览
- TypeScript 6（即原 5.9 后续版本）在生态完成迁移前继续作为稳定线维护
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
    "type-check": "tsc --noEmit",                   // TS 5.9 稳定路径
    "type-check:fast": "tsgo --noEmit",             // TS 7.0 Beta 加速
    "build": "tsc -p tsconfig.build.json",          // 生产构建仍用 5.9
    "ci:check": "tsgo --noEmit && tsc --noEmit"    // 双校验，确认行为一致
  }
}
```

### 5.4 迁移注意事项

```
迁移建议（2026-Q2）
├── 本地 type-check 可切换 tsgo，CI 双跑校验
├── tsc-watch / IDE Language Server 仍以 5.9 为准
├── 自定义 transformer / ts-patch 等深度集成尚未适配 Go 版
└── 等待 7.0 RC 后再考虑生产构建迁移
```

> ⚠️ 待确认：vue-tsc、ts-jest、ts-node 等深度依赖 TypeScript API 的工具对 tsgo 的兼容情况随版本快速变化，请在升级前查阅各工具的 TS 7 issue。

