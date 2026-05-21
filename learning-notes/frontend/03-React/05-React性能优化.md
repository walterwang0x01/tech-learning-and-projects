# React 性能优化
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. React.memo

```jsx
// 浅比较 props，props 不变则跳过重渲染
const ExpensiveList = React.memo(function List({ items, onSelect }) {
  return (
    <ul>
      {items.map(item => (
        <li key={item.id} onClick={() => onSelect(item.id)}>{item.name}</li>
      ))}
    </ul>
  );
});

// 自定义比较函数
const MemoComponent = React.memo(Component, (prevProps, nextProps) => {
  return prevProps.id === nextProps.id; // 返回 true 跳过渲染
});
```

## 2. useMemo / useCallback

```jsx
function SearchResults({ query, items }) {
  // 缓存计算结果
  const filtered = useMemo(() =>
    items.filter(item => item.name.includes(query)),
    [query, items]
  );

  // 缓存回调函数（传给子组件时避免子组件重渲染）
  const handleSelect = useCallback((id) => {
    setSelectedId(id);
  }, []);

  return <ExpensiveList items={filtered} onSelect={handleSelect} />;
}
```

## 3. 代码分割

```jsx
// React.lazy + Suspense
const HeavyComponent = lazy(() => import('./HeavyComponent'));

function App() {
  return (
    <Suspense fallback={<Skeleton />}>
      <HeavyComponent />
    </Suspense>
  );
}

// 路由级别分割
const routes = [
  { path: '/', element: lazy(() => import('./pages/Home')) },
  { path: '/dashboard', element: lazy(() => import('./pages/Dashboard')) },
];
```

## 4. 虚拟列表

```jsx
// 使用 react-virtuoso 或 @tanstack/react-virtual
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }) {
  const parentRef = useRef(null);
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 50,
  });

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: `${virtualizer.getTotalSize()}px`, position: 'relative' }}>
        {virtualizer.getVirtualItems().map(virtualRow => (
          <div
            key={virtualRow.key}
            style={{
              position: 'absolute',
              top: 0,
              transform: `translateY(${virtualRow.start}px)`,
              height: `${virtualRow.size}px`,
            }}
          >
            {items[virtualRow.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

## 5. 并发特性（React 18+）

```jsx
import { useTransition, useDeferredValue } from 'react';

// useTransition：标记低优先级更新
function SearchPage() {
  const [query, setQuery] = useState('');
  const [isPending, startTransition] = useTransition();

  const handleChange = (e) => {
    setQuery(e.target.value);           // 高优先级：更新输入框
    startTransition(() => {
      setSearchResults(search(e.target.value)); // 低优先级：更新搜索结果
    });
  };

  return (
    <div>
      <input value={query} onChange={handleChange} />
      {isPending ? <Spinner /> : <Results />}
    </div>
  );
}

// useDeferredValue：延迟更新值
function FilteredList({ query }) {
  const deferredQuery = useDeferredValue(query);
  const isStale = query !== deferredQuery;

  const filtered = useMemo(() =>
    heavyFilter(items, deferredQuery),
    [deferredQuery]
  );

  return (
    <div style={{ opacity: isStale ? 0.5 : 1 }}>
      <List items={filtered} />
    </div>
  );
}
```

## 6. 性能分析

```jsx
// React DevTools Profiler
// 1. 打开 React DevTools → Profiler 标签
// 2. 点击录制 → 操作页面 → 停止录制
// 3. 查看火焰图，找到耗时组件

// Profiler 组件（代码中测量）
<Profiler id="Navigation" onRender={(id, phase, actualDuration) => {
  console.log(`${id} ${phase}: ${actualDuration}ms`);
}}>
  <Navigation />
</Profiler>

// 常见优化清单：
// ✅ 避免在渲染中创建新对象/数组/函数
// ✅ 使用 key 帮助 React 识别列表项
// ✅ 将频繁变化的状态下移到子组件
// ✅ 使用 React.memo 包裹纯展示组件
// ✅ 大列表使用虚拟滚动
// ✅ 路由级别代码分割
```

## 7. Next.js 16.2 性能改进（2026-03）

> 🔄 更新于 2026-04-22

<!-- version-check: Next.js 16.2.5 (May 2026 security release), checked 2026-05-21 -->

Next.js 16.2 带来了显著的性能提升，对 React 应用的渲染和开发体验有直接影响。来源：[Next.js 16.2 Blog](https://nextjs.org/blog/next-16-2)

### 关键性能数据

| 指标 | 改进幅度 | 说明 |
|------|---------|------|
| `next dev` 启动 | ~400% 更快 | 相比 16.1，默认应用启动快 87% |
| Server Components 渲染 | ~50% 更快 | RSC payload 反序列化优化 350% |
| ImageResponse | 2-20x 更快 | 基础图片 2x，复杂图片 20x |

### RSC 反序列化优化原理

React 团队贡献了一个关键优化：将 `JSON.parse` 的 reviver 回调（每个键值对都跨 C++/JS 边界）替换为两步法——先纯 `JSON.parse()`，再用纯 JS 递归遍历。消除了 V8 边界跨越开销。

### 其他改进

- **Server Function 日志**：开发终端显示函数名、参数、执行时间、文件位置
- **Hydration Diff 指示器**：错误叠加层清晰标注 `+ Client` / `- Server` 差异
- **`--inspect` for `next start`**：生产服务器支持 Node.js 调试器
- **AI 改进**：`create-next-app` 内置 `AGENTS.md`、浏览器日志转发、`next-browser`（实验性）
- **View Transitions**：`<Link>` 组件支持 `transitionTypes` prop

> 🔄 更新于 2026-05-21

### ⚠️ Next.js 16.2.5 安全更新（2026-05-07）

Next.js May 2026 安全发布修复了 13 个安全公告（含 React RSC 上游 CVE-2025-55182 RCE 漏洞）。所有使用 App Router 的生产应用必须立即升级到 **16.2.5**（或 15.5.16）。

详见 → [Web 安全文档](../09-浏览器与网络/04-Web安全XSS-CSRF.md) 第 5 节

来源：[Vercel Changelog](https://vercel.com/changelog/next-js-may-2026-security-release)

