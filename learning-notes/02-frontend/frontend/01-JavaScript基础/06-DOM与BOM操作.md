# DOM 与 BOM 操作
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. DOM 查询

```javascript
// 推荐
document.getElementById('id');
document.querySelector('.class');       // 返回第一个匹配
document.querySelectorAll('.class');    // 返回 NodeList

// 其他
document.getElementsByClassName('class'); // HTMLCollection（实时）
document.getElementsByTagName('div');
element.closest('.parent');              // 向上查找最近匹配的祖先
element.matches('.selector');            // 是否匹配选择器
```

## 2. DOM 操作

```javascript
// 创建
const div = document.createElement('div');
const text = document.createTextNode('hello');
const fragment = document.createDocumentFragment(); // 文档片段（批量操作）

// 插入
parent.appendChild(child);
parent.insertBefore(newNode, referenceNode);
parent.append(node1, node2, 'text');     // 可插入多个
parent.prepend(node);                     // 插入到开头
element.before(node);                     // 插入到元素前
element.after(node);                      // 插入到元素后

// 替换与删除
parent.replaceChild(newChild, oldChild);
element.replaceWith(newElement);
parent.removeChild(child);
element.remove();

// 克隆
const clone = element.cloneNode(true); // true = 深克隆

// 属性操作
element.setAttribute('data-id', '123');
element.getAttribute('data-id');
element.removeAttribute('data-id');
element.dataset.id;                    // data-* 属性
element.classList.add('active');
element.classList.remove('active');
element.classList.toggle('active');
element.classList.contains('active');

// 样式操作
element.style.color = 'red';
element.style.cssText = 'color: red; font-size: 16px;';
getComputedStyle(element).color;       // 获取计算后的样式

// 内容操作
element.innerHTML = '<p>HTML内容</p>';
element.textContent = '纯文本内容';
element.innerText = '可见文本';        // 受CSS影响
```

## 3. 事件模型

```javascript
// 事件流：捕获阶段 → 目标阶段 → 冒泡阶段

// 添加事件监听
element.addEventListener('click', handler, {
  capture: false,  // 是否在捕获阶段触发
  once: true,      // 只触发一次
  passive: true,   // 不会调用 preventDefault（提升滚动性能）
});

// 移除事件监听
element.removeEventListener('click', handler);

// 事件对象
element.addEventListener('click', (e) => {
  e.target;           // 触发事件的元素
  e.currentTarget;    // 绑定事件的元素
  e.preventDefault();  // 阻止默认行为
  e.stopPropagation(); // 阻止冒泡
  e.type;             // 事件类型
});

// 事件委托（利用冒泡，减少事件绑定）
document.getElementById('list').addEventListener('click', (e) => {
  if (e.target.matches('li')) {
    console.log('点击了:', e.target.textContent);
  }
});
```

## 4. Observer API

```javascript
// IntersectionObserver（元素可见性，懒加载/无限滚动）
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.src = entry.target.dataset.src; // 懒加载
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.1 });
document.querySelectorAll('img[data-src]').forEach(img => observer.observe(img));

// MutationObserver（DOM变化监听）
const mutationObserver = new MutationObserver((mutations) => {
  mutations.forEach(m => console.log('DOM变化:', m.type));
});
mutationObserver.observe(element, { childList: true, subtree: true, attributes: true });

// ResizeObserver（元素尺寸变化）
const resizeObserver = new ResizeObserver((entries) => {
  entries.forEach(entry => {
    console.log('新尺寸:', entry.contentRect.width, entry.contentRect.height);
  });
});
resizeObserver.observe(element);
```

## 5. BOM 对象

```javascript
// window
window.innerWidth;   // 视口宽度
window.innerHeight;  // 视口高度
window.scrollTo({ top: 0, behavior: 'smooth' });
window.open(url);

// location
location.href;       // 完整URL
location.pathname;   // 路径
location.search;     // 查询参数
location.hash;       // 哈希值
location.reload();   // 刷新

// history
history.pushState(state, '', '/new-url');
history.replaceState(state, '', '/new-url');
history.back();
history.forward();
window.addEventListener('popstate', (e) => { /* 路由变化 */ });

// navigator
navigator.userAgent;
navigator.language;
navigator.clipboard.writeText('复制内容');
```


## 6. 2026 Web Platform 新 API

<!-- version-check: Interop 2026, Navigation API Baseline, Popover API, View Transitions, checked 2026-05-05 -->

> 🔄 更新于 2026-05-05

### 6.1 Navigation API（Baseline Newly Available 2026）

Navigation API 是 `history.pushState()` 和 `popstate` 的现代替代方案，提供更清晰的导航拦截和控制能力。2026 年初已在所有主流浏览器中可用（全球覆盖率 ~88%）。

```javascript
// 拦截导航事件（替代 popstate + pushState）
navigation.addEventListener('navigate', (event) => {
  // 只处理同源导航
  if (!event.canIntercept) return;

  const url = new URL(event.destination.url);

  event.intercept({
    // 预提交处理器：在 DOM 更新前加载关键资源
    async precommitHandler() {
      await loadCriticalCSS(url.pathname);
    },
    // 主处理器：渲染新页面
    async handler() {
      const content = await fetchPage(url.pathname);
      document.querySelector('#app').innerHTML = content;
    }
  });
});

// 编程式导航（替代 history.pushState）
navigation.navigate('/dashboard', {
  state: { tab: 'overview' },
  info: { source: 'sidebar-click' }  // 传递给 navigate 事件的额外信息
});

// 遍历历史条目（比 history 更安全，只暴露同源条目）
for (const entry of navigation.entries()) {
  console.log(entry.url, entry.getState());
}

// 监听当前条目变化
navigation.addEventListener('currententrychange', (event) => {
  // 更新 UI 状态
  updateBreadcrumb(navigation.currentEntry.url);
});
```

> 来源：[web.dev - Navigation API Baseline](https://web.dev/blog/baseline-navigation-api)、[MDN Navigation API](https://developer.mozilla.org/docs/Web/API/Navigation_API)

### 6.2 Popover API（Baseline Widely Available 2025）

原生弹出层 API，浏览器内置顶层渲染、键盘交互、Escape 关闭和无障碍支持，无需 JavaScript 库。

```html
<!-- 基础用法：纯 HTML，零 JS -->
<button popovertarget="menu">打开菜单</button>
<div id="menu" popover>
  <p>这是一个弹出菜单</p>
</div>

<!-- popover="hint"：不会关闭其他 auto 弹出层，适合 tooltip -->
<span popovertarget="tip" popovertargetaction="hover">悬停查看</span>
<div id="tip" popover="hint">这是提示信息</div>

<!-- closedby 属性：控制关闭方式（Interop 2026 焦点） -->
<dialog closedby="any">
  <!-- 点击外部或按 Escape 都可关闭 -->
  <p>对话框内容</p>
</dialog>
```

```javascript
// JavaScript 控制
const popover = document.getElementById('menu');
popover.showPopover();   // 显示
popover.hidePopover();   // 隐藏
popover.togglePopover(); // 切换

// 监听显示/隐藏事件
popover.addEventListener('toggle', (event) => {
  console.log(event.newState); // 'open' 或 'closed'
});
```

```css
/* :open 伪类：匹配打开状态的元素（Interop 2026 焦点） */
dialog:open {
  animation: slideIn 0.3s ease;
}

/* ::backdrop 伪元素：弹出层背景遮罩 */
[popover]::backdrop {
  background: rgba(0, 0, 0, 0.3);
}
```

> 来源：[MDN Popover API](https://developer.mozilla.org/docs/Web/API/Popover_API)、[Smashing Magazine](https://next.smashingmagazine.com/2026/03/getting-started-popover-api/)

### 6.3 View Transitions API

原生页面过渡动画，浏览器自动处理新旧 DOM 状态之间的动画，无需动画库。

```javascript
// 同文档视图过渡（Baseline Newly Available 2025）
document.startViewTransition(async () => {
  // 更新 DOM
  const data = await fetchNewContent();
  document.querySelector('#content').innerHTML = data;
});

// 为特定元素命名过渡（实现共享元素动画）
// HTML: <img style="view-transition-name: hero-image" />
```

```css
/* 自定义过渡动画 */
::view-transition-old(root) {
  animation: fade-out 0.3s ease;
}
::view-transition-new(root) {
  animation: fade-in 0.3s ease;
}

/* 跨文档视图过渡（Interop 2026 焦点）— 零 JS */
@view-transition {
  navigation: auto;  /* 页面间导航自动触发过渡 */
}

/* 按过渡类型应用不同动画 */
:active-view-transition-type(slide-left) {
  &::view-transition-old(root) {
    animation: slide-out-left 0.3s;
  }
  &::view-transition-new(root) {
    animation: slide-in-right 0.3s;
  }
}
```

> 来源：[web.dev Interop 2026](https://web.dev/blog/interop-2026)、[trevorlasn.com](https://trevorlasn.com/blog/view-transitions-api)

### 6.4 Scroll-driven Animations（Interop 2026）

纯 CSS 实现滚动驱动动画，无需 JavaScript 监听 scroll 事件。

```css
/* 元素进入视口时淡入 */
.reveal {
  animation: fade-in linear forwards;
  animation-timeline: view();           /* 绑定到元素可见性 */
  animation-range: entry 0% entry 100%; /* 进入视口时触发 */
}

@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 滚动进度条 */
.progress-bar {
  animation: grow-width linear;
  animation-timeline: scroll();  /* 绑定到滚动容器 */
}

@keyframes grow-width {
  from { width: 0%; }
  to { width: 100%; }
}
```

### 6.5 HTML Invoker Commands（Baseline 2026-01）

声明式按钮命令，无需 JavaScript 即可控制 `<dialog>`、`<details>`、`<popover>` 等元素。

```html
<!-- commandfor + command 属性（替代 popovertarget 的通用方案） -->
<button commandfor="my-dialog" command="show-modal">打开对话框</button>
<dialog id="my-dialog">
  <p>对话框内容</p>
  <button commandfor="my-dialog" command="close">关闭</button>
</dialog>

<!-- 控制 details 展开/折叠 -->
<button commandfor="faq" command="toggle">展开/折叠</button>
<details id="faq">
  <summary>常见问题</summary>
  <p>答案内容...</p>
</details>
```

> 来源：[InfoQ - HTML Invoker Commands Baseline](https://infoq.com/news/2026/01/html-invoker-commands)

### 6.6 Interop 2026 其他重要 API

| API | 说明 | 状态 |
| --- | ---- | ---- |
| `IndexedDB.getAllRecords()` | 批量读取记录，支持反向排序 | Interop 2026 焦点 |
| `WebTransport` | HTTP/3 低延迟双向通信，替代 WebSocket | Interop 2026 焦点 |
| `CSS contrast-color()` | 浏览器自动选择高对比度前景色 | Safari/Firefox 已支持 |
| `CSS shape()` | 路径命令创建复杂裁剪形状，支持百分比坐标 | Safari 18.4 已支持 |
| `Scoped Custom Element Registries` | 同名自定义元素共存，解决 Web Components 冲突 | Safari 26.0 首发 |
| Media 伪类 | `:playing`/`:paused`/`:buffering`/`:muted` 等 | Safari 多年前已支持 |
| `CSS attr()` 高级版 | 任意属性读取 HTML 属性值，支持类型转换 | Interop 2026 焦点 |
| Soft Navigations API | SPA 软导航性能指标追踪 | Chrome 147 Origin Trial |

> 来源：[Interop 2026 Dashboard](https://wpt.fyi/interop-2026)、[webkit.org](https://webkit.org/blog/17818/announcing-interop-2026/)
