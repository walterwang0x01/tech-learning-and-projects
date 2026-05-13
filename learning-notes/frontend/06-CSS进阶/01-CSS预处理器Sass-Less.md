# CSS 预处理器 Sass / Less
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Sass/SCSS

<!-- version-check: Dart Sass (sass npm), PostCSS 8.x, checked 2026-05-13 -->

```scss
// 变量
$primary: #3498db;
$spacing: 8px;
$font-stack: 'Inter', sans-serif;

// 嵌套
.nav {
  background: $primary;
  &__item { padding: $spacing * 2; }
  &--active { font-weight: bold; }
  &:hover { opacity: 0.9; }
}

// 混入（Mixin）
@mixin flex-center($direction: row) {
  display: flex;
  justify-content: center;
  align-items: center;
  flex-direction: $direction;
}
.container { @include flex-center(column); }

// 继承
%button-base {
  padding: 8px 16px;
  border-radius: 4px;
  cursor: pointer;
}
.btn-primary { @extend %button-base; background: $primary; }
.btn-danger  { @extend %button-base; background: red; }

// 函数
@function rem($px) { @return $px / 16 * 1rem; }
.title { font-size: rem(24); }

// 条件与循环
@each $name, $color in (primary: #3498db, danger: #e74c3c, success: #2ecc71) {
  .text-#{$name} { color: $color; }
  .bg-#{$name} { background: $color; }
}

// 模块化
@use 'variables' as vars;
@use 'mixins';
.title { color: vars.$primary; @include mixins.flex-center; }
```

## 2. Less

```less
// 变量
@primary: #3498db;
@spacing: 8px;

// 混入
.flex-center() {
  display: flex;
  justify-content: center;
  align-items: center;
}
.container { .flex-center(); }

// 运算
.box { width: 100% - 200px; padding: @spacing * 2; }
```

## 3. PostCSS

```javascript
// postcss.config.js
export default {
  plugins: {
    'postcss-preset-env': { stage: 2 },  // 使用现代CSS特性
    autoprefixer: {},                      // 自动添加浏览器前缀
    cssnano: {},                           // CSS压缩（生产环境）
  },
};
```
