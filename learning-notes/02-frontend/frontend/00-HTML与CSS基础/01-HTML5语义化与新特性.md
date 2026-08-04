# HTML5 语义化与新特性
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. HTML5 语义化标签

### 1.1 为什么需要语义化

- 提高代码可读性和可维护性
- 有利于 SEO（搜索引擎优化）
- 方便屏幕阅读器等辅助设备解析（无障碍访问）
- 便于团队协作开发

### 1.2 常用语义化标签

```html
<header>  <!-- 页面或区块的头部 -->
<nav>     <!-- 导航链接区域 -->
<main>    <!-- 页面主要内容（唯一） -->
<article> <!-- 独立的内容块（文章、帖子） -->
<section> <!-- 文档中的一个区域 -->
<aside>   <!-- 侧边栏或附属内容 -->
<footer>  <!-- 页面或区块的底部 -->
<figure>  <!-- 独立的流内容（图片、图表） -->
<figcaption> <!-- figure 的标题 -->
<details> <!-- 可展开/折叠的详情 -->
<summary> <!-- details 的摘要标题 -->
<mark>    <!-- 高亮文本 -->
<time>    <!-- 日期/时间 -->
```

### 1.3 页面结构示例

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>语义化页面</title>
</head>
<body>
  <header>
    <h1>网站标题</h1>
    <nav>
      <ul>
        <li><a href="/">首页</a></li>
        <li><a href="/about">关于</a></li>
      </ul>
    </nav>
  </header>

  <main>
    <article>
      <h2>文章标题</h2>
      <time datetime="2024-01-01">2024年1月1日</time>
      <p>文章内容...</p>
      <figure>
        <img src="image.jpg" alt="描述">
        <figcaption>图片说明</figcaption>
      </figure>
    </article>

    <aside>
      <h3>相关推荐</h3>
      <ul>
        <li><a href="#">推荐文章1</a></li>
      </ul>
    </aside>
  </main>

  <footer>
    <p>&copy; 2024 版权所有</p>
  </footer>
</body>
</html>
```

## 2. HTML5 表单新特性

### 2.1 新增 input 类型

```html
<input type="email" placeholder="邮箱">
<input type="url" placeholder="网址">
<input type="tel" placeholder="电话">
<input type="number" min="0" max="100" step="1">
<input type="range" min="0" max="100">
<input type="date">
<input type="time">
<input type="datetime-local">
<input type="month">
<input type="week">
<input type="color">
<input type="search" placeholder="搜索">
```

### 2.2 表单属性

```html
<!-- 必填 -->
<input type="text" required>

<!-- 正则验证 -->
<input type="text" pattern="[A-Za-z]{3,}">

<!-- 自动聚焦 -->
<input type="text" autofocus>

<!-- 自动完成 -->
<input type="text" autocomplete="on">

<!-- 占位符 -->
<input type="text" placeholder="请输入内容">

<!-- 数据列表 -->
<input list="browsers">
<datalist id="browsers">
  <option value="Chrome">
  <option value="Firefox">
  <option value="Safari">
</datalist>
```

## 3. 多媒体标签

### 3.1 音频 audio

```html
<audio controls autoplay loop muted preload="auto">
  <source src="audio.mp3" type="audio/mpeg">
  <source src="audio.ogg" type="audio/ogg">
  您的浏览器不支持 audio 标签
</audio>
```

### 3.2 视频 video

```html
<video controls width="640" height="360" poster="cover.jpg">
  <source src="video.mp4" type="video/mp4">
  <source src="video.webm" type="video/webm">
  <track src="subtitles.vtt" kind="subtitles" srclang="zh" label="中文">
  您的浏览器不支持 video 标签
</video>
```

## 4. Canvas 画布

```html
<canvas id="myCanvas" width="400" height="300"></canvas>

<script>
const canvas = document.getElementById('myCanvas');
const ctx = canvas.getContext('2d');

// 绘制矩形
ctx.fillStyle = '#3498db';
ctx.fillRect(10, 10, 150, 100);

// 绘制圆形
ctx.beginPath();
ctx.arc(250, 60, 50, 0, Math.PI * 2);
ctx.fillStyle = '#e74c3c';
ctx.fill();

// 绘制文本
ctx.font = '20px Arial';
ctx.fillStyle = '#333';
ctx.fillText('Hello Canvas', 100, 200);

// 绘制线条
ctx.beginPath();
ctx.moveTo(10, 250);
ctx.lineTo(390, 250);
ctx.strokeStyle = '#2ecc71';
ctx.lineWidth = 2;
ctx.stroke();
</script>
```

## 5. Web Storage

### 5.1 localStorage

```javascript
// 存储数据（持久化，关闭浏览器不丢失）
localStorage.setItem('username', 'zhangsan');
localStorage.setItem('user', JSON.stringify({ name: '张三', age: 25 }));

// 读取数据
const username = localStorage.getItem('username');
const user = JSON.parse(localStorage.getItem('user'));

// 删除数据
localStorage.removeItem('username');

// 清空所有数据
localStorage.clear();
```

### 5.2 sessionStorage

```javascript
// 存储数据（会话级别，关闭标签页丢失）
sessionStorage.setItem('token', 'abc123');

// 读取数据
const token = sessionStorage.getItem('token');

// 删除数据
sessionStorage.removeItem('token');
```

## 6. 其他 HTML5 API

### 6.1 Geolocation 地理定位

```javascript
navigator.geolocation.getCurrentPosition(
  (position) => {
    console.log('纬度:', position.coords.latitude);
    console.log('经度:', position.coords.longitude);
  },
  (error) => {
    console.error('定位失败:', error.message);
  }
);
```

### 6.2 Web Workers

```javascript
// main.js
const worker = new Worker('worker.js');
worker.postMessage({ data: [1, 2, 3, 4, 5] });
worker.onmessage = (e) => {
  console.log('计算结果:', e.data);
};

// worker.js
self.onmessage = (e) => {
  const result = e.data.data.reduce((sum, n) => sum + n, 0);
  self.postMessage(result);
};
```

### 6.3 Drag and Drop

```html
<div id="drag" draggable="true">拖拽我</div>
<div id="drop">放置区域</div>

<script>
const drag = document.getElementById('drag');
const drop = document.getElementById('drop');

drag.addEventListener('dragstart', (e) => {
  e.dataTransfer.setData('text/plain', e.target.id);
});

drop.addEventListener('dragover', (e) => {
  e.preventDefault(); // 允许放置
});

drop.addEventListener('drop', (e) => {
  e.preventDefault();
  const id = e.dataTransfer.getData('text/plain');
  drop.appendChild(document.getElementById(id));
});
</script>
```

## 7. 无障碍访问（a11y）

### 7.1 ARIA 属性

```html
<!-- 角色 -->
<div role="navigation">导航区域</div>
<div role="alert">警告信息</div>

<!-- 状态 -->
<button aria-expanded="false">展开菜单</button>
<input aria-invalid="true" aria-describedby="error-msg">
<span id="error-msg">请输入有效的邮箱</span>

<!-- 标签 -->
<button aria-label="关闭对话框">×</button>
<div aria-live="polite">动态更新的内容</div>
```

## 8. Meta 标签最佳实践

```html
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="description" content="页面描述，用于SEO">
  <meta name="keywords" content="关键词1,关键词2">
  <meta name="author" content="作者">
  <meta http-equiv="X-UA-Compatible" content="IE=edge">
  <meta name="theme-color" content="#3498db">

  <!-- Open Graph（社交分享） -->
  <meta property="og:title" content="页面标题">
  <meta property="og:description" content="页面描述">
  <meta property="og:image" content="https://example.com/image.jpg">
  <meta property="og:url" content="https://example.com">
</head>
```
## 🎬 推荐视频资源

- [freeCodeCamp - HTML Full Course](https://www.youtube.com/watch?v=kUMe1FH4CHE) — HTML完整课程
- [Kevin Powell - HTML & CSS](https://www.youtube.com/@KevinPowell) — CSS大师Kevin Powell频道
