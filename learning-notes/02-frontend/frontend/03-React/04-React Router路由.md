# React Router 路由
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 基本配置（v6）

> 🔄 更新于 2026-04-18：React Router v7（当前 v7.16.0）已将 `react-router-dom` 合并到 `react-router` 单一包中，v6 API 仍可用但建议迁移。详见下方第 6 节。

<!-- version-check: React Router 7.16.0, checked 2026-05-31 -->
<!-- 修复于 2026-05-31: 7.14.0 → 7.16.0（npm registry 实测 latest） -->

```jsx
import { BrowserRouter, Routes, Route, Link, NavLink, Outlet } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">首页</Link>
        <NavLink to="/about" className={({ isActive }) => isActive ? 'active' : ''}>
          关于
        </NavLink>
      </nav>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Home />} />
          <Route path="about" element={<About />} />
          <Route path="users" element={<Users />}>
            <Route path=":userId" element={<UserDetail />} />
          </Route>
          <Route path="*" element={<NotFound />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

function Layout() {
  return (
    <div>
      <header>Header</header>
      <main><Outlet /></main> {/* 子路由渲染位置 */}
      <footer>Footer</footer>
    </div>
  );
}
```

## 2. 路由 Hooks

```jsx
import { useParams, useSearchParams, useNavigate, useLocation } from 'react-router-dom';

function UserDetail() {
  const { userId } = useParams();           // 路径参数
  const [searchParams, setSearchParams] = useSearchParams(); // 查询参数
  const navigate = useNavigate();            // 编程式导航
  const location = useLocation();            // 当前位置信息

  const tab = searchParams.get('tab') || 'profile';

  return (
    <div>
      <h1>用户 {userId}</h1>
      <button onClick={() => navigate(-1)}>返回</button>
      <button onClick={() => navigate('/users', { replace: true })}>
        回到列表
      </button>
    </div>
  );
}
```

## 3. 路由守卫

```jsx
function ProtectedRoute({ children }) {
  const { user } = useAuth();
  const location = useLocation();

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }
  return children;
}

// 使用
<Route path="/dashboard" element={
  <ProtectedRoute>
    <Dashboard />
  </ProtectedRoute>
} />
```

## 4. 路由懒加载

```jsx
import { lazy, Suspense } from 'react';

const Dashboard = lazy(() => import('./pages/Dashboard'));
const Settings = lazy(() => import('./pages/Settings'));

function App() {
  return (
    <Suspense fallback={<div>加载中...</div>}>
      <Routes>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Suspense>
  );
}
```

## 5. 数据加载（loader）

```jsx
import { createBrowserRouter, RouterProvider, useLoaderData } from 'react-router-dom';

const router = createBrowserRouter([
  {
    path: '/users/:id',
    element: <UserDetail />,
    loader: async ({ params }) => {
      const res = await fetch(`/api/users/${params.id}`);
      if (!res.ok) throw new Response('Not Found', { status: 404 });
      return res.json();
    },
    errorElement: <ErrorPage />,
  },
]);

function UserDetail() {
  const user = useLoaderData();
  return <h1>{user.name}</h1>;
}

function App() {
  return <RouterProvider router={router} />;
}
```

## 6. React Router v7（2026 最新）

> 🔄 更新于 2026-04-18

<!-- version-check: React Router 7.16.0, checked 2026-05-31 -->

React Router v7 是一次重大升级，从路由库演进为全栈框架，支持 SSR、数据加载、RSC 等能力。核心变化：

- **统一包名**：推荐统一使用 `react-router` 单一包；`react-router-dom` 在 v7 中**仍作为 `react-router` 的 re-export 发布**（平滑 v6 升级路径），旧导入仍可用，但新项目建议直接用 `react-router` <!-- 修复于 2026-05-31: 原文"react-router-dom 已废弃"措辞失实，官方文档明确 v7 仍发布该包作为 re-export，并未废弃 -->
- **Framework Mode**：内置 SSR、代码分割、数据预加载，可替代 Next.js/Remix
- **Vite 8 支持**：v7.14.0 新增 Vite 8 集成
- **RSC 支持**：实验性 React Server Components 框架模式

```jsx
// v7 安装：npm install react-router（不再需要 react-router-dom）
import { createBrowserRouter, RouterProvider, useLoaderData, Outlet } from 'react-router';

// v7 路由配置（与 v6 data router 兼容）
const router = createBrowserRouter([
  {
    path: '/',
    element: <Layout />,
    children: [
      { index: true, element: <Home /> },
      {
        path: 'users/:id',
        element: <UserDetail />,
        loader: async ({ params }) => {
          const res = await fetch(`/api/users/${params.id}`);
          return res.json();
        },
      },
    ],
  },
]);

function App() {
  return <RouterProvider router={router} />;
}
```

**从 v6 迁移到 v7 的关键变化**：

| 变化项 | v6 | v7 |
|--------|----|----|
| 包名 | `react-router-dom` | `react-router` |
| SSR | 需要 Next.js/Remix | 内置 Framework Mode |
| 数据加载 | `loader` + `useLoaderData` | 保持兼容，新增中间件支持 |
| 代码分割 | 手动 `lazy()` | 框架模式自动处理 |

来源：[React Router 官方文档](https://reactrouter.com/)、[releasebot.io](https://releasebot.io/updates/remix/react-router)
