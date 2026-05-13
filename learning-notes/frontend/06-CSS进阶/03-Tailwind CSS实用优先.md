# Tailwind CSS 实用优先
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 核心理念

<!-- version-check: Tailwind CSS 4.2.x, checked 2026-05-13 -->
<!-- 修复于 2026-05-13: 4.2.0 → 4.2.x（4.2.2 已发布） -->

- 工具类优先（Utility-First）：直接在 HTML 中使用预定义的工具类
- JIT 模式：按需生成 CSS，构建产物极小
- 高度可定制：通过配置文件自定义设计系统

> 🔄 更新于 2026-04-18

**Tailwind CSS v4**（2025-01 发布）是一次完全重写：
- **Rust 引擎（Oxide）**：全量构建 < 100ms，增量构建微秒级，比 v3 快 5x~100x
- **CSS-first 配置**：`tailwind.config.js` 被 CSS 中的 `@theme` 指令替代
- **原生 CSS 特性**：使用 Cascade Layers、注册自定义属性、`color-mix()` 等现代 CSS
- **容器查询**：原生支持 `@container` 查询

**Tailwind CSS v4.2**（2026-02-18）：
- 新增 `@tailwindcss/webpack` 插件（webpack 项目无需手动配置 PostCSS）
- 4 个新色板：mauve、olive、mist、taupe
- 逻辑属性扩展：`pbs-*`、`pbe-*`、`mbs-*`、`mbe-*` 等 block 方向工具类
- 重编译性能提升 3.8x（[Tim Neutkens 测试](https://infoq.com/news/2026/04/tailwind-css-4-2-webpack)）

来源：[Tailwind CSS v4 文档](https://tailwindcss.com/docs)、[InfoQ: Tailwind CSS 4.2](https://infoq.com/news/2026/04/tailwind-css-4-2-webpack)

## 2. 安装与配置

> 🔄 更新于 2026-04-18：v4 采用 CSS-first 配置，`tailwind.config.js` 不再是必需的。

**v4 CSS-first 配置（推荐）**：

```css
/* app.css — v4 使用 @theme 指令直接在 CSS 中定义主题 */
@import "tailwindcss";

@theme {
  --color-primary-50: #eff6ff;
  --color-primary-500: #3b82f6;
  --color-primary-900: #1e3a5f;
  --spacing-128: 32rem;
  --font-sans: 'Inter', sans-serif;
}
```

**v3 JS 配置（仍兼容，但不推荐新项目使用）**：

```javascript
// tailwind.config.js（v3 风格）
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx,vue}'],
  darkMode: 'class', // 'media' | 'class'
  theme: {
    extend: {
      colors: {
        primary: { 50: '#eff6ff', 500: '#3b82f6', 900: '#1e3a5f' },
      },
      spacing: { '128': '32rem' },
      fontFamily: { sans: ['Inter', 'sans-serif'] },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
};
```

## 3. 常用工具类

```html
<!-- 布局 -->
<div class="flex items-center justify-between gap-4">
<div class="grid grid-cols-3 gap-6">
<div class="container mx-auto px-4">

<!-- 间距 -->
<div class="p-4 px-6 py-2 m-4 mt-8 space-y-4">

<!-- 尺寸 -->
<div class="w-full h-screen max-w-lg min-h-[200px]">

<!-- 文字 -->
<p class="text-lg font-bold text-gray-700 leading-relaxed tracking-wide">
<p class="text-center truncate line-clamp-3">

<!-- 背景与边框 -->
<div class="bg-blue-500 bg-opacity-50 rounded-lg border border-gray-200 shadow-md">

<!-- 响应式 -->
<div class="text-sm md:text-base lg:text-lg">
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3">

<!-- 暗色模式 -->
<div class="bg-white dark:bg-gray-800 text-black dark:text-white">

<!-- 状态 -->
<button class="bg-blue-500 hover:bg-blue-600 active:bg-blue-700
               focus:outline-none focus:ring-2 focus:ring-blue-500
               disabled:opacity-50 disabled:cursor-not-allowed">

<!-- 过渡动画 -->
<div class="transition-all duration-300 ease-in-out hover:scale-105">

<!-- 组合示例：卡片 -->
<div class="rounded-xl bg-white p-6 shadow-lg ring-1 ring-gray-200
            hover:shadow-xl transition-shadow duration-300">
  <h3 class="text-xl font-semibold text-gray-900">标题</h3>
  <p class="mt-2 text-gray-600 line-clamp-2">描述内容</p>
</div>
```

## 4. 组件抽象

```css
/* 使用 @apply 抽取重复样式 */
@layer components {
  .btn {
    @apply px-4 py-2 rounded-lg font-medium transition-colors;
  }
  .btn-primary {
    @apply btn bg-blue-500 text-white hover:bg-blue-600;
  }
  .input {
    @apply w-full rounded-lg border border-gray-300 px-3 py-2
           focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500;
  }
}
```

## 5. 与框架集成

```jsx
// React + clsx/cn 条件类名
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs) { return twMerge(clsx(inputs)); }

function Button({ variant = 'primary', size = 'md', className, ...props }) {
  return (
    <button
      className={cn(
        'rounded-lg font-medium transition-colors',
        variant === 'primary' && 'bg-blue-500 text-white hover:bg-blue-600',
        variant === 'secondary' && 'bg-gray-200 text-gray-800 hover:bg-gray-300',
        size === 'sm' && 'px-3 py-1.5 text-sm',
        size === 'md' && 'px-4 py-2',
        size === 'lg' && 'px-6 py-3 text-lg',
        className,
      )}
      {...props}
    />
  );
}
```
## 🎬 推荐视频资源

- [Traversy Media - Tailwind CSS Crash Course](https://www.youtube.com/watch?v=dFgzHOX84xQ) — Tailwind速成
- [Fireship - Tailwind in 100 Seconds](https://www.youtube.com/watch?v=mr15Xzb1Ook) — Tailwind快速了解
