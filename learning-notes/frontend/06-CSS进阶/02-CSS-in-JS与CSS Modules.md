# CSS-in-JS 与 CSS Modules
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. CSS Modules

```css
/* Button.module.css */
.button { padding: 8px 16px; border-radius: 4px; }
.primary { background: #3498db; color: white; }
.large { font-size: 18px; padding: 12px 24px; }
```

```jsx
import styles from './Button.module.css';

function Button({ variant, size, children }) {
  return (
    <button className={`${styles.button} ${styles[variant]} ${styles[size]}`}>
      {children}
    </button>
  );
}
```

## 2. styled-components

```jsx
import styled from 'styled-components';

const Button = styled.button`
  padding: ${props => props.$size === 'lg' ? '12px 24px' : '8px 16px'};
  background: ${props => props.$variant === 'primary' ? '#3498db' : '#eee'};
  color: ${props => props.$variant === 'primary' ? 'white' : '#333'};
  border: none;
  border-radius: 4px;
  cursor: pointer;

  &:hover { opacity: 0.9; }

  @media (max-width: 768px) {
    width: 100%;
  }
`;

// 继承样式
const PrimaryButton = styled(Button)`
  background: #3498db;
  color: white;
`;

// 主题
import { ThemeProvider } from 'styled-components';
const theme = { colors: { primary: '#3498db' }, spacing: { md: '16px' } };
<ThemeProvider theme={theme}><App /></ThemeProvider>
```

## 3. 方案对比

| 方案 | 运行时开销 | 类型安全 | 适用场景 |
|------|-----------|---------|---------|
| CSS Modules | 无 | 一般 | 通用 |
| styled-components | 有 | 好 | React 项目 |
| Tailwind CSS | 无 | 无 | 快速开发 |
| vanilla-extract | 无 | 好 | 零运行时需求 |

## 4. 2026 年零运行时 CSS-in-JS 趋势

<!-- version-check: StyleX 0.17.1, Panda CSS 0.53.x, styled-components maintenance mode, checked 2026-05-04 -->

> 🔄 更新于 2026-05-04

2026 年 CSS-in-JS 生态发生了根本性转变：**运行时 CSS-in-JS 正在被零运行时方案取代**。React Server Components 的普及和 Core Web Vitals 的严格要求，使得运行时样式注入的性能开销不再可接受。

### 4.1 styled-components 进入维护模式

styled-components 不再积极开发新功能，主要原因：

- RSC 不兼容：运行时 CSS-in-JS 依赖 `useContext`，无法在 Server Components 中使用
- 性能开销：每次渲染都需要序列化样式、计算哈希、注入 `<style>` 标签
- 包体积：styled-components + Emotion 约 12-15KB gzipped

**迁移建议**：新项目不应选择 styled-components，现有项目可逐步迁移到零运行时方案。

来源：[Why Migrating Away from Styled-Components](https://www.gperrucci.com/blog/react/why-migrating-design-systems-away-from-styled-components)

### 4.2 StyleX — Meta 的编译时 CSS-in-JS

StyleX 是 Meta 内部使用的样式方案（驱动 Facebook、Instagram、WhatsApp Web），2023 年开源，2026 年成为零运行时 CSS-in-JS 的标杆。

```javascript
import * as stylex from '@stylexjs/stylex';

// 编译时提取为原子 CSS，零运行时开销
const styles = stylex.create({
  button: {
    padding: '8px 16px',
    borderRadius: 4,
    cursor: 'pointer',
  },
  primary: {
    backgroundColor: '#3498db',
    color: 'white',
  },
});

// 使用
function Button({ variant, children }) {
  return (
    <button {...stylex.props(styles.button, variant === 'primary' && styles.primary)}>
      {children}
    </button>
  );
}
```

**核心优势**：
- 编译时提取原子 CSS，CSS 体积随项目增长趋于平稳
- 确定性样式合并（"最后应用的样式总是赢"）
- 完整 TypeScript 类型安全
- 支持 Next.js / Vite / Webpack / Rspack

来源：[StyleX 官方文档](https://stylexjs.com/docs/learn)

### 4.3 Panda CSS — Chakra UI 团队的零运行时方案

```javascript
import { css } from '../styled-system/css';

// 类似 Tailwind 的 Token 系统 + 类似 styled-components 的 API
function Button({ children }) {
  return (
    <button className={css({
      padding: '8px 16px',
      bg: 'blue.500',      // Design Token
      color: 'white',
      borderRadius: 'md',
      _hover: { bg: 'blue.600' },  // 伪类
      md: { padding: '12px 24px' }, // 响应式
    })}>
      {children}
    </button>
  );
}
```

**核心优势**：
- 编译时生成原子 CSS（通过 CLI 或 PostCSS）
- Design Token 系统（类似 Tailwind 的 `bg-blue-500` 但用 JS 对象语法）
- 支持 Recipes（类似 CVA 的变体模式）
- 框架无关（React / Vue / Solid / Svelte）

来源：[Panda CSS 官方文档](https://panda-css.com/)

### 4.4 2026 年 CSS 样式方案选型表

| 方案 | 运行时 | RSC 兼容 | 类型安全 | 适用场景 | 推荐度 |
| ---- | ------ | -------- | -------- | -------- | ------ |
| **Tailwind CSS v4** | 零 | ✅ | 一般 | 快速开发、工具类优先 | ⭐⭐⭐⭐⭐ |
| **CSS Modules** | 零 | ✅ | 一般 | 通用、简单项目 | ⭐⭐⭐⭐ |
| **StyleX** | 零 | ✅ | 好 | 大型应用、设计系统 | ⭐⭐⭐⭐ |
| **Panda CSS** | 零 | ✅ | 好 | Token 驱动、跨框架 | ⭐⭐⭐⭐ |
| **vanilla-extract** | 零 | ✅ | 好 | TypeScript 优先 | ⭐⭐⭐⭐ |
| styled-components | 有 | ❌ | 好 | 仅维护旧项目 | ⭐⭐ |
| Emotion | 有 | ❌ | 好 | 仅维护旧项目 | ⭐⭐ |

**2026 年选型建议**：
- 新项目首选 **Tailwind CSS v4**（最大生态）或 **CSS Modules**（最简单）
- 大型设计系统选 **StyleX**（Meta 验证）或 **Panda CSS**（Token 系统）
- 现有 styled-components 项目逐步迁移到零运行时方案

来源：[Zero-Runtime CSS-in-JS: The Final Boss of Styling in 2026](https://blog.weskill.org/2026/04/zero-runtime-css-in-js-final-boss-of.html)
