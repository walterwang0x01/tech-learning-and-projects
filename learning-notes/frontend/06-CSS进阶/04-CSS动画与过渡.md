# CSS 动画与过渡
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. transition 过渡

```css
.button {
  background: #3498db;
  transform: translateY(0);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.button:hover {
  background: #2980b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}
```

## 2. animation 关键帧

```css
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes pulse {
  0%, 100% { transform: scale(1); }
  50%      { transform: scale(1.05); }
}

.fade-in {
  animation: fadeIn 0.5s ease-out forwards;
}

.spinner {
  animation: spin 1s linear infinite;
}

.pulse {
  animation: pulse 2s ease-in-out infinite;
}
```

## 3. GPU 加速

```css
/* 触发 GPU 加速的属性（合成层） */
.gpu-accelerated {
  transform: translateZ(0);    /* 或 translate3d(0,0,0) */
  will-change: transform;      /* 提前告知浏览器 */
  /* 优先使用 transform 和 opacity 做动画，避免触发重排 */
}

/* 性能好的动画属性：transform, opacity */
/* 性能差的动画属性：width, height, top, left, margin */
```

## 4. FLIP 动画技术

```javascript
// First: 记录初始位置
// Last: 记录最终位置
// Invert: 计算差值，用 transform 反转到初始位置
// Play: 移除 transform，让元素动画到最终位置

function flipAnimate(element) {
  const first = element.getBoundingClientRect();

  // 触发布局变化
  element.classList.toggle('expanded');

  const last = element.getBoundingClientRect();
  const deltaX = first.left - last.left;
  const deltaY = first.top - last.top;

  element.animate([
    { transform: `translate(${deltaX}px, ${deltaY}px)` },
    { transform: 'translate(0, 0)' },
  ], { duration: 300, easing: 'ease-out' });
}
```

## 5. Web Animations API

```javascript
const element = document.querySelector('.box');

const animation = element.animate([
  { transform: 'translateX(0)', opacity: 1 },
  { transform: 'translateX(300px)', opacity: 0.5 },
], {
  duration: 1000,
  easing: 'ease-in-out',
  iterations: Infinity,
  direction: 'alternate',
  fill: 'forwards',
});

animation.pause();
animation.play();
animation.reverse();
animation.cancel();
animation.finished.then(() => console.log('动画完成'));
```

## 6. 2026 年 CSS 动画新特性

<!-- version-check: @starting-style Baseline 2024-11, View Transitions API Baseline 2026, checked 2026-05-04 -->

> 🔄 更新于 2026-05-04

### 6.1 @starting-style 入场动画

纯 CSS 实现元素从 `display: none` 到可见的入场动画，不再需要 JavaScript：

```css
/* 对话框入场动画 */
dialog {
  opacity: 1;
  transform: translateY(0);
  transition: opacity 0.3s, transform 0.3s, display 0.3s allow-discrete;

  /* 定义初始状态（从 display:none 切换时的起始值） */
  @starting-style {
    opacity: 0;
    transform: translateY(-20px);
  }
}

/* Popover 入场动画 */
[popover]:popover-open {
  opacity: 1;
  scale: 1;
  transition: opacity 0.25s, scale 0.25s, display 0.25s allow-discrete;

  @starting-style {
    opacity: 0;
    scale: 0.9;
  }
}
```

**关键点**：`allow-discrete` 让 `display` 属性也能参与过渡，浏览器会在动画开始前应用 `@starting-style` 中的值。

来源：[MDN @starting-style](https://developer.mozilla.org/en-US/docs/Web/CSS/Reference/At-rules/@starting-style)

### 6.2 View Transitions API

页面间或状态间的平滑过渡动画，2026 年跨文档 View Transitions 已全浏览器支持（Interop 2026）：

```css
/* 同文档 View Transition */
::view-transition-old(root) {
  animation: fade-out 0.3s ease-out;
}
::view-transition-new(root) {
  animation: fade-in 0.3s ease-in;
}

/* 为特定元素命名过渡 */
.card {
  view-transition-name: card-hero;
}
```

```javascript
// 触发同文档 View Transition
document.startViewTransition(() => {
  // 更新 DOM
  updateContent();
});
```

```html
<!-- 跨文档 View Transition（MPA，无需 JS） -->
<head>
  <meta name="view-transition" content="same-origin" />
  <style>
    @view-transition { navigation: auto; }
  </style>
</head>
```

来源：[Interop 2026 View Transitions](https://webkit.org/blog/17818/announcing-interop-2026/)
