# React 状态管理
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Context API

```jsx
// 适合低频更新的全局状态（主题、语言、用户信息）
const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const login = async (credentials) => { /* ... */ };
  const logout = () => setUser(null);
  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

const useAuth = () => useContext(AuthContext);
```

## 2. Redux Toolkit

```javascript
// store.js
import { configureStore } from '@reduxjs/toolkit';
import counterReducer from './counterSlice';

export const store = configureStore({
  reducer: { counter: counterReducer },
});

// counterSlice.js
import { createSlice, createAsyncThunk } from '@reduxjs/toolkit';

export const fetchCount = createAsyncThunk('counter/fetch', async (amount) => {
  const res = await fetch(`/api/count?amount=${amount}`);
  return res.json();
});

const counterSlice = createSlice({
  name: 'counter',
  initialState: { value: 0, status: 'idle' },
  reducers: {
    increment: (state) => { state.value += 1; }, // Immer 允许直接修改
    decrement: (state) => { state.value -= 1; },
    incrementByAmount: (state, action) => { state.value += action.payload; },
  },
  extraReducers: (builder) => {
    builder
      .addCase(fetchCount.pending, (state) => { state.status = 'loading'; })
      .addCase(fetchCount.fulfilled, (state, action) => {
        state.status = 'idle';
        state.value = action.payload;
      });
  },
});

export const { increment, decrement } = counterSlice.actions;
export default counterSlice.reducer;

// 组件中使用
import { useSelector, useDispatch } from 'react-redux';
function Counter() {
  const count = useSelector(state => state.counter.value);
  const dispatch = useDispatch();
  return <button onClick={() => dispatch(increment())}>{count}</button>;
}
```

## 3. Zustand（轻量推荐）

```javascript
import { create } from 'zustand';
import { devtools, persist } from 'zustand/middleware';

const useStore = create(
  devtools(
    persist(
      (set, get) => ({
        count: 0,
        increment: () => set(state => ({ count: state.count + 1 })),
        decrement: () => set(state => ({ count: state.count - 1 })),
        reset: () => set({ count: 0 }),
        // 异步操作
        fetchCount: async () => {
          const res = await fetch('/api/count');
          const data = await res.json();
          set({ count: data.count });
        },
      }),
      { name: 'counter-storage' } // localStorage 持久化
    )
  )
);

// 组件中使用（自动订阅，精确更新）
function Counter() {
  const count = useStore(state => state.count);
  const increment = useStore(state => state.increment);
  return <button onClick={increment}>{count}</button>;
}
```

## 4. TanStack Query（服务端状态）

```jsx
import { useQuery, useMutation, useQueryClient, QueryClient, QueryClientProvider } from '@tanstack/react-query';

const queryClient = new QueryClient();

// 查询
function UserList() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['users'],
    queryFn: () => fetch('/api/users').then(r => r.json()),
    staleTime: 5 * 60 * 1000,  // 5分钟内不重新请求
    gcTime: 10 * 60 * 1000,    // 缓存保留10分钟
  });

  if (isLoading) return <div>加载中...</div>;
  if (error) return <div>错误: {error.message}</div>;
  return <ul>{data.map(u => <li key={u.id}>{u.name}</li>)}</ul>;
}

// 变更
function CreateUser() {
  const queryClient = useQueryClient();
  const mutation = useMutation({
    mutationFn: (newUser) => fetch('/api/users', {
      method: 'POST',
      body: JSON.stringify(newUser),
    }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] }); // 刷新列表
    },
  });

  return <button onClick={() => mutation.mutate({ name: '新用户' })}>创建</button>;
}
```

## 5. 状态管理选型

| 方案 | 适用场景 | 复杂度 |
|------|---------|--------|
| useState | 组件内部状态 | 低 |
| Context | 低频全局状态（主题、认证） | 低 |
| Zustand | 中小型应用全局状态 | 低 |
| Redux Toolkit | 大型应用、复杂状态逻辑 | 中 |
| TanStack Query | 服务端状态（API数据缓存） | 中 |
| Jotai | 原子化状态管理 | 低 |

## 6. 2026 年状态管理生态更新

> 🔄 更新于 2026-05-03

<!-- version-check: Zustand 5.0.14, Redux Toolkit 2.12.0, TanStack Query 5.101.2, Jotai 2.20.1, checked 2026-07-08 -->
<!-- 修复于 2026-05-31: 版本号按 npm registry 实测刷新（Zustand 5.0.3→5.0.14、RTK 2.9.x→2.12.x、Jotai 2.12.x→2.20.x）；TanStack AI 归属修正 -->

### 6.1 Zustand 5.x（当前稳定版 5.0.14）

Zustand 5 于 2024-10 发布，是一次面向现代化的重构。51.6K+ GitHub Stars，约 40% 新项目采用。来源：[Announcing Zustand v5](https://pmnd.rs/blog/announcing-zustand-v5/)

**核心变化：**
- 最低 React 18（使用原生 `useSyncExternalStore`，移除 `use-sync-external-store` 依赖）
- 最低 TypeScript 4.5
- 包体积更小（移除 shim 后减少约 30%）
- `ExtractState` 类型工具（从 store 类型提取 state 类型）
- `createWithEqualityFn` 替代旧的 `create` + `equalityFn` 模式

```typescript
import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';

// Zustand 5 推荐模式：immer 中间件 + TypeScript
interface TodoStore {
  todos: { id: number; text: string; done: boolean }[];
  addTodo: (text: string) => void;
  toggleTodo: (id: number) => void;
}

const useTodoStore = create<TodoStore>()(
  immer((set) => ({
    todos: [],
    addTodo: (text) =>
      set((state) => {
        state.todos.push({ id: Date.now(), text, done: false });
      }),
    toggleTodo: (id) =>
      set((state) => {
        const todo = state.todos.find((t) => t.id === id);
        if (todo) todo.done = !todo.done;
      }),
  }))
);
```

### 6.2 Redux Toolkit 2.x（当前稳定版 2.12.x）

RTK 2.0 于 2023-11 发布，当前 2.12.x 持续迭代。在企业级项目中仍占主导地位。来源：[Redux Toolkit Releases](https://github.com/reduxjs/redux-toolkit/releases)

**RTK 2.x 关键变化：**
- ESM/CJS 双格式发布
- 移除 `createReducer`、`createSlice.extraReducers` 对象写法
- `combineSlices` API（动态注入 reducer，支持代码分割）
- `configureStore` 默认中间件更新

```typescript
import { combineSlices, configureStore } from '@reduxjs/toolkit';

// RTK 2.x 新增：combineSlices 支持动态注入
const rootReducer = combineSlices(counterSlice, todosSlice);

// 懒加载的 slice 可以后续注入
const injectedReducer = rootReducer.inject(lazySlice);
```

### 6.3 TanStack Query v5（当前 5.101.x）

TanStack Query v5 是服务端状态管理的事实标准，当前 @tanstack/react-query **5.101.2**。来源：[TanStack Query Releases](https://github.com/TanStack/query/releases)

**v5 关键改进：**
- 统一对象参数格式（移除所有重载）
- `gcTime` 替代 `cacheTime`
- 更好的 TypeScript 推断
- 支持 Angular、Svelte、Solid 等多框架

> **注意**：TanStack AI 是 TanStack 生态中**独立的库**（`@tanstack/ai`，提供 AI 聊天、AG-UI 协议、实时语音、客户端工具调用等），并非 TanStack Query v5 的内置特性，二者不要混淆。来源：[TanStack AI Blog](https://tanstack.com/blog) <!-- 修复于 2026-05-31: 原文将"TanStack AI 集成"误列为 Query v5 特性，实为独立库，已澄清归属 -->

### 6.4 Jotai 2.x（当前 2.20.x）

Jotai 是原子化状态管理方案，19K+ Stars。适合需要精确控制重渲染的场景。来源：[Jotai Documentation](https://jotai.org/docs)

```typescript
import { atom, useAtom } from 'jotai';

// 原子化：每个状态独立，组件只订阅需要的 atom
const countAtom = atom(0);
const doubleCountAtom = atom((get) => get(countAtom) * 2); // 派生 atom

function Counter() {
  const [count, setCount] = useAtom(countAtom);
  return <button onClick={() => setCount((c) => c + 1)}>{count}</button>;
}
```

### 6.5 2026 年状态管理选型建议

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 服务端状态（API 数据） | **TanStack Query** | 缓存、重试、乐观更新一站式解决 |
| 中小型客户端状态 | **Zustand 5** | 极简 API、零样板、40% 新项目采用 |
| 大型企业级应用 | **Redux Toolkit 2.x** | 成熟生态、DevTools、combineSlices 代码分割 |
| 精确重渲染控制 | **Jotai 2.x** | 原子化订阅、零 Provider、组合灵活 |
| 简单全局状态 | **React Context** | 内置方案、无额外依赖 |
| 表单状态 | **React Hook Form** | 非受控表单、性能优异 |

> **2026 年共识**：TanStack Query 处理服务端状态（约 80% 场景），Zustand/Jotai 处理客户端状态。手写 Redux 已降至约 10% 新项目，RTK 在企业级仍然常见。来源：[Nucamp State Management 2026](https://www.nucamp.co/blog/state-management-in-2026-redux-context-api-and-modern-patterns)

## 🎬 推荐视频资源

- [Jack Herrington - State Management](https://www.youtube.com/watch?v=zpUMRsAO6-Y) — React状态管理对比
- [Fireship - Redux in 100 Seconds](https://www.youtube.com/watch?v=_shA5Xwe8_4) — Redux快速了解
