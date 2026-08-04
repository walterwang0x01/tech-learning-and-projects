# Flex 与 Grid 布局
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Flex 弹性布局

### 1.1 基本概念

- 主轴（Main Axis）：默认水平方向
- 交叉轴（Cross Axis）：默认垂直方向
- Flex 容器（Container）：设置 `display: flex` 的元素
- Flex 项目（Item）：容器的直接子元素

### 1.2 容器属性

```css
.container {
  display: flex; /* 或 inline-flex */

  /* 主轴方向 */
  flex-direction: row | row-reverse | column | column-reverse;

  /* 换行 */
  flex-wrap: nowrap | wrap | wrap-reverse;

  /* 简写 */
  flex-flow: row wrap;

  /* 主轴对齐 */
  justify-content: flex-start | flex-end | center
                 | space-between | space-around | space-evenly;

  /* 交叉轴对齐（单行） */
  align-items: stretch | flex-start | flex-end | center | baseline;

  /* 交叉轴对齐（多行） */
  align-content: stretch | flex-start | flex-end | center
               | space-between | space-around;

  /* 间距（现代浏览器） */
  gap: 16px;
  row-gap: 16px;
  column-gap: 16px;
}
```

### 1.3 项目属性

```css
.item {
  /* 排列顺序（默认0，越小越靠前） */
  order: 0;

  /* 放大比例（默认0，不放大） */
  flex-grow: 1;

  /* 缩小比例（默认1，空间不足时缩小） */
  flex-shrink: 0;

  /* 初始大小 */
  flex-basis: 200px | auto;

  /* 简写：flex-grow flex-shrink flex-basis */
  flex: 1;          /* 等价于 1 1 0% */
  flex: auto;       /* 等价于 1 1 auto */
  flex: none;       /* 等价于 0 0 auto */
  flex: 0 0 200px;  /* 固定宽度，不伸缩 */

  /* 单独对齐（覆盖 align-items） */
  align-self: auto | flex-start | flex-end | center | stretch;
}
```

### 1.4 常见布局

```css
/* 导航栏：logo左侧，菜单右侧 */
.navbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 等分布局 */
.equal-cols {
  display: flex;
}
.equal-cols > * {
  flex: 1;
}

/* 圣杯布局 */
.holy-grail {
  display: flex;
  min-height: 100vh;
  flex-direction: column;
}
.holy-grail main { flex: 1; display: flex; }
.holy-grail .content { flex: 1; }
.holy-grail .sidebar { flex: 0 0 200px; }

/* 底部固定 */
.page {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}
.page main { flex: 1; }
```

## 2. Grid 网格布局

### 2.1 容器属性

```css
.grid-container {
  display: grid; /* 或 inline-grid */

  /* 定义列 */
  grid-template-columns: 200px 1fr 200px;
  grid-template-columns: repeat(3, 1fr);
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));

  /* 定义行 */
  grid-template-rows: 60px 1fr 40px;
  grid-template-rows: repeat(3, 100px);

  /* 间距 */
  gap: 16px;
  row-gap: 16px;
  column-gap: 16px;

  /* 隐式网格行高 */
  grid-auto-rows: minmax(100px, auto);

  /* 区域命名 */
  grid-template-areas:
    "header header header"
    "sidebar content aside"
    "footer footer footer";

  /* 对齐 */
  justify-items: start | end | center | stretch;
  align-items: start | end | center | stretch;
  place-items: center; /* 简写 */

  justify-content: start | end | center | space-between | space-around;
  align-content: start | end | center | space-between | space-around;
  place-content: center; /* 简写 */
}
```

### 2.2 项目属性

```css
.grid-item {
  /* 指定位置 */
  grid-column: 1 / 3;      /* 从第1列线到第3列线 */
  grid-column: 1 / span 2; /* 从第1列线跨2列 */
  grid-row: 1 / 2;

  /* 简写 */
  grid-area: 1 / 1 / 3 / 3; /* row-start / col-start / row-end / col-end */

  /* 使用区域名称 */
  grid-area: header;

  /* 单独对齐 */
  justify-self: start | end | center | stretch;
  align-self: start | end | center | stretch;
  place-self: center;
}
```

### 2.3 常见布局

```css
/* 经典三栏布局 */
.layout {
  display: grid;
  grid-template-columns: 200px 1fr 200px;
  grid-template-rows: 60px 1fr 40px;
  grid-template-areas:
    "header header header"
    "left   main   right"
    "footer footer footer";
  min-height: 100vh;
}
.header { grid-area: header; }
.left   { grid-area: left; }
.main   { grid-area: main; }
.right  { grid-area: right; }
.footer { grid-area: footer; }

/* 响应式卡片网格 */
.card-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 24px;
}

/* 瀑布流（简易） */
.masonry {
  columns: 3;
  column-gap: 16px;
}
.masonry-item {
  break-inside: avoid;
  margin-bottom: 16px;
}
```

## 3. Flex vs Grid 选型

| 场景 | 推荐 | 原因 |
|------|------|------|
| 一维布局（行或列） | Flex | Flex 更简单直观 |
| 二维布局（行和列） | Grid | Grid 天然支持二维 |
| 导航栏、工具栏 | Flex | 单行排列 |
| 页面整体布局 | Grid | 区域划分更清晰 |
| 卡片列表 | Grid | auto-fill 自适应 |
| 居中对齐 | 都可以 | Grid 的 place-items 更简洁 |
| 不确定子元素数量 | Flex | 更灵活 |
## 🎬 推荐视频资源

- [Kevin Powell - Flexbox Tutorial](https://www.youtube.com/watch?v=u044iM9xsWU) — Flexbox完整教程
- [Kevin Powell - CSS Grid Tutorial](https://www.youtube.com/watch?v=rg7Fvvl3taU) — CSS Grid完整教程
- [Fireship - CSS Flexbox in 100 Seconds](https://www.youtube.com/watch?v=K74l26pE4YA) — Flexbox快速了解
### 📺 B站（Bilibili）
- [黑马程序员 - CSS布局教程](https://www.bilibili.com/video/BV1p84y1P7Z5) — Flex/Grid完整教程

### 🌐 其他平台
- [Flexbox Froggy](https://flexboxfroggy.com/#zh-cn) — Flexbox游戏化学习（中文）
- [Grid Garden](https://cssgridgarden.com/#zh-cn) — CSS Grid游戏化学习（中文）
