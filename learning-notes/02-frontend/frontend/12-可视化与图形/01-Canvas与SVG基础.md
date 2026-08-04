# Canvas 与 SVG 基础
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Canvas 2D

```javascript
const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');

// 矩形
ctx.fillStyle = '#3498db';
ctx.fillRect(10, 10, 200, 100);
ctx.strokeStyle = '#e74c3c';
ctx.strokeRect(10, 10, 200, 100);

// 路径
ctx.beginPath();
ctx.moveTo(50, 50);
ctx.lineTo(200, 50);
ctx.lineTo(200, 200);
ctx.closePath();
ctx.fill();

// 圆弧
ctx.beginPath();
ctx.arc(150, 150, 50, 0, Math.PI * 2);
ctx.fill();

// 文本
ctx.font = '20px Arial';
ctx.fillText('Hello Canvas', 50, 50);

// 图像
const img = new Image();
img.onload = () => ctx.drawImage(img, 0, 0, 200, 150);
img.src = 'image.jpg';

// 渐变
const gradient = ctx.createLinearGradient(0, 0, 200, 0);
gradient.addColorStop(0, '#3498db');
gradient.addColorStop(1, '#2ecc71');
ctx.fillStyle = gradient;
ctx.fillRect(0, 0, 200, 100);
```

## 2. SVG 基础

```html
<svg width="400" height="300" viewBox="0 0 400 300">
  <!-- 矩形 -->
  <rect x="10" y="10" width="200" height="100" rx="8"
        fill="#3498db" stroke="#2980b9" stroke-width="2" />

  <!-- 圆形 -->
  <circle cx="300" cy="60" r="50" fill="#e74c3c" opacity="0.8" />

  <!-- 线条 -->
  <line x1="10" y1="200" x2="390" y2="200" stroke="#333" stroke-width="2" />

  <!-- 路径 -->
  <path d="M 10 250 Q 200 150 390 250" fill="none" stroke="#2ecc71" stroke-width="3" />

  <!-- 文本 -->
  <text x="200" y="280" text-anchor="middle" font-size="16" fill="#333">SVG Text</text>

  <!-- 组 -->
  <g transform="translate(50, 50)" opacity="0.9">
    <rect width="100" height="60" fill="#9b59b6" />
    <text x="50" y="35" text-anchor="middle" fill="white">Group</text>
  </g>
</svg>
```

## 3. Canvas vs SVG

| 特性 | Canvas | SVG |
|------|--------|-----|
| 渲染方式 | 位图（像素） | 矢量（DOM） |
| 性能 | 大量元素时更好 | 少量元素时更好 |
| 事件处理 | 需手动计算 | 原生 DOM 事件 |
| 缩放 | 会模糊 | 无损缩放 |
| 适用场景 | 游戏、粒子、图表 | 图标、图表、地图 |
| SEO | 不支持 | 支持 |
