# React Hooks 深入
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. useState

```jsx
// 基本用法
const [count, setCount] = useState(0);

// 函数式更新（基于前一个状态）
setCount(prev => prev + 1);

// 惰性初始化（复杂计算只在首次渲染执行）
const [state, setState] = useState(() => {
  return expensiveComputation();
});

// 对象状态（需要展开合并）
const [form, setForm] = useState({ name: '', email: '' });
setForm(prev => ({ ...prev, name: '张三' }));
```

## 2. useEffect

```jsx
// 每次渲染后执行
useEffect(() => { console.log('rendered'); });

// 仅挂载时执行
useEffect(() => { fetchData(); }, []);

// 依赖变化时执行
useEffect(() => {
  const results = search(query);
  setResults(results);
}, [query]);

// 清理副作用
useEffect(() => {
  const timer = setInterval(() => tick(), 1000);
  return () => clearInterval(timer); // 清理
}, []);

// 请求数据模式
useEffect(() => {
  let cancelled = false;
  async function fetchData() {
    const res = await fetch(`/api/users/${id}`);
    const data = await res.json();
    if (!cancelled) setUser(data);
  }
  fetchData();
  return () => { cancelled = true; }; // 防止竞态
}, [id]);
```

## 3. useContext

```jsx
const ThemeContext = createContext({ theme: 'light', toggle: () => {} });

function ThemeProvider({ children }) {
  const [theme, setTheme] = useState('light');
  const toggle = () => setTheme(t => t === 'light' ? 'dark' : 'light');
  return (
    <ThemeContext.Provider value={{ theme, toggle }}>
      {children}
    </ThemeContext.Provider>
  );
}

// 自定义 Hook 封装
function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) throw new Error('useTheme must be used within ThemeProvider');
  return context;
}
```

## 4. useReducer

```jsx
const initialState = { count: 0, step: 1 };

function reducer(state, action) {
  switch (action.type) {
    case 'increment': return { ...state, count: state.count + state.step };
    case 'decrement': return { ...state, count: state.count - state.step };
    case 'setStep':   return { ...state, step: action.payload };
    case 'reset':     return initialState;
    default: throw new Error(`Unknown action: ${action.type}`);
  }
}

function Counter() {
  const [state, dispatch] = useReducer(reducer, initialState);
  return (
    <div>
      <p>Count: {state.count}</p>
      <button onClick={() => dispatch({ type: 'increment' })}>+</button>
      <button onClick={() => dispatch({ type: 'decrement' })}>-</button>
      <button onClick={() => dispatch({ type: 'reset' })}>重置</button>
    </div>
  );
}
```

## 5. useMemo / useCallback

```jsx
// useMemo：缓存计算结果
const expensiveResult = useMemo(() => {
  return items.filter(item => item.active).sort((a, b) => a.name.localeCompare(b.name));
}, [items]);

// useCallback：缓存函数引用（配合 React.memo 使用）
const handleClick = useCallback((id) => {
  setSelectedId(id);
}, []);

// React.memo：浅比较 props，避免不必要的重渲染
const MemoChild = React.memo(function Child({ onClick, data }) {
  return <div onClick={onClick}>{data.name}</div>;
});
```

## 6. useRef

```jsx
// DOM 引用
const inputRef = useRef(null);
const focusInput = () => inputRef.current?.focus();
<input ref={inputRef} />

// 保存可变值（不触发重渲染）
const timerRef = useRef(null);
useEffect(() => {
  timerRef.current = setInterval(() => tick(), 1000);
  return () => clearInterval(timerRef.current);
}, []);

// 保存前一个值
function usePrevious(value) {
  const ref = useRef();
  useEffect(() => { ref.current = value; });
  return ref.current;
}
```

## 7. React 19 新增 Hooks

> 🔄 更新于 2026-07-08

<!-- version-check: React 19.2.7 (2026-06-01 FormData fix), checked 2026-07-08 -->
<!-- 修复于 2026-07-08: 19.2.6 → 19.2.7（19.2.6 CVE-2026-23870 DoS 修复引入 Server Actions FormData 丢失回归，19.2.7 修复） -->

React 19（2024-12 稳定版，当前最新补丁 **19.2.7**，2026-06-01）引入了多个面向异步和表单场景的新 Hook，配合 React Compiler 实现自动记忆化优化。

> **⚠️ Server Actions + FormData 回归（2026-06）**：19.2.6 修复 CVE-2026-23870（DoS）时，Server Function 请求反序列化路径变更导致 `useActionState` 提交的 `FormData` 在服务端**静默为空**（`formData.get()` 返回 `null`，无报错）。**19.2.7 / 19.1.8 / 19.0.7** 已修复。若使用下方 `useActionState` 示例，请确保 `react` ≥ 19.2.7。排查：`console.log([...formData.entries()])`。
>
> 来源：[React 19.2.7 Release](https://github.com/facebook/react/releases/tag/v19.2.7) · [osbytes 分析](https://www.osbytes.io/blog/react-19-2-7-security-patch-dropped-server-action-formdata) · [Next.js #93754](https://github.com/vercel/next.js/issues/93754)

```jsx
// use() — 在渲染期间读取 Promise 或 Context（替代 useContext）
import { use, Suspense } from 'react';

// 读取 Promise（配合 Suspense 使用）
function UserProfile({ userPromise }) {
  const user = use(userPromise); // 渲染期间直接读取
  return <h1>{user.name}</h1>;
}

// 读取 Context（可在条件语句中使用，比 useContext 更灵活）
function ThemeButton() {
  if (someCondition) {
    const theme = use(ThemeContext); // useContext 不能在条件中使用，use 可以
    return <button className={theme}>按钮</button>;
  }
}

// useActionState — 管理表单 Action 的状态（替代手动 useState + loading）
import { useActionState } from 'react';

function LoginForm() {
  const [state, submitAction, isPending] = useActionState(
    async (previousState, formData) => {
      const email = formData.get('email');
      const result = await login(email, formData.get('password'));
      if (result.error) return { error: result.error };
      return { success: true };
    },
    { error: null } // 初始状态
  );

  return (
    <form action={submitAction}>
      <input name="email" type="email" />
      <input name="password" type="password" />
      <button disabled={isPending}>
        {isPending ? '登录中...' : '登录'}
      </button>
      {state.error && <p className="error">{state.error}</p>}
    </form>
  );
}

// useFormStatus — 获取父级 <form> 的提交状态
import { useFormStatus } from 'react-dom';

function SubmitButton() {
  const { pending, data, method } = useFormStatus();
  return (
    <button disabled={pending}>
      {pending ? '提交中...' : '提交'}
    </button>
  );
}

// useOptimistic — 乐观更新 UI
import { useOptimistic } from 'react';

function TodoList({ todos, addTodoAction }) {
  const [optimisticTodos, addOptimisticTodo] = useOptimistic(
    todos,
    (currentTodos, newTodo) => [...currentTodos, { ...newTodo, sending: true }]
  );

  async function handleSubmit(formData) {
    const title = formData.get('title');
    addOptimisticTodo({ title, id: Date.now() }); // 立即显示
    await addTodoAction(title); // 实际请求
  }

  return (
    <div>
      <form action={handleSubmit}>
        <input name="title" />
        <button>添加</button>
      </form>
      <ul>
        {optimisticTodos.map(todo => (
          <li key={todo.id} style={{ opacity: todo.sending ? 0.5 : 1 }}>
            {todo.title}
          </li>
        ))}
      </ul>
    </div>
  );
}
```

### React Compiler（自动记忆化）

React Compiler 在 React 19 中稳定，自动为组件添加 `useMemo`、`useCallback`、`React.memo` 等优化，开发者无需手动编写：

```jsx
// React 19 之前：手动优化
const MemoChild = React.memo(({ data }) => <div>{data.name}</div>);
const handleClick = useCallback(() => setCount(c => c + 1), []);
const filtered = useMemo(() => items.filter(i => i.active), [items]);

// React 19 + Compiler：自动优化，直接写即可
function Child({ data }) {
  return <div>{data.name}</div>; // Compiler 自动判断是否需要 memo
}
const handleClick = () => setCount(c => c + 1); // 自动缓存
const filtered = items.filter(i => i.active); // 自动 memo
```

## 8. 自定义 Hook

```jsx
// useLocalStorage
function useLocalStorage(key, initialValue) {
  const [value, setValue] = useState(() => {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : initialValue;
    } catch { return initialValue; }
  });

  useEffect(() => {
    localStorage.setItem(key, JSON.stringify(value));
  }, [key, value]);

  return [value, setValue];
}

// useDebounce
function useDebounce(value, delay = 300) {
  const [debouncedValue, setDebouncedValue] = useState(value);
  useEffect(() => {
    const timer = setTimeout(() => setDebouncedValue(value), delay);
    return () => clearTimeout(timer);
  }, [value, delay]);
  return debouncedValue;
}

// useFetch
function useFetch(url) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(url)
      .then(res => res.json())
      .then(data => { if (!cancelled) setData(data); })
      .catch(err => { if (!cancelled) setError(err); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [url]);

  return { data, loading, error };
}
```
## 🎬 推荐视频资源

- [Web Dev Simplified - React Hooks](https://www.youtube.com/watch?v=O6P86uwfdR0) — React Hooks完整教程
- [Jack Herrington - React Hooks](https://www.youtube.com/@jherr) — React高级技巧频道
