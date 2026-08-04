# React 基础与 JSX
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. JSX 语法

```jsx
// JSX 是 JavaScript 的语法扩展，编译为 React.createElement 调用
const element = <h1 className="title">Hello, React</h1>;

// 表达式嵌入
const name = '张三';
const greeting = <p>Hello, {name}</p>;

// 条件渲染
const App = ({ isLoggedIn }) => (
  <div>
    {isLoggedIn ? <Dashboard /> : <Login />}
    {isLoggedIn && <UserMenu />}
  </div>
);

// 列表渲染
const List = ({ items }) => (
  <ul>
    {items.map(item => (
      <li key={item.id}>{item.name}</li>
    ))}
  </ul>
);

// 样式
const style = { color: 'red', fontSize: '16px' };
<div style={style} className="container">内容</div>
```

## 2. 函数组件

```jsx
// 基本组件
function Welcome({ name, age = 18 }) {
  return <h1>Hello, {name} ({age})</h1>;
}

// 箭头函数组件
const Card = ({ title, children }) => (
  <div className="card">
    <h2>{title}</h2>
    <div className="card-body">{children}</div>
  </div>
);

// 使用
<Welcome name="张三" age={25} />
<Card title="标题">
  <p>卡片内容</p>
</Card>
```

## 3. State 与事件

```jsx
import { useState } from 'react';

function Counter() {
  const [count, setCount] = useState(0);

  // 事件处理
  const increment = () => setCount(prev => prev + 1);

  // 表单处理
  const [name, setName] = useState('');
  const handleChange = (e) => setName(e.target.value);
  const handleSubmit = (e) => {
    e.preventDefault();
    console.log('提交:', name);
  };

  return (
    <div>
      <p>Count: {count}</p>
      <button onClick={increment}>+1</button>

      <form onSubmit={handleSubmit}>
        <input value={name} onChange={handleChange} />
        <button type="submit">提交</button>
      </form>
    </div>
  );
}
```

## 4. 受控与非受控组件

```jsx
// 受控组件（React 管理状态，推荐）
function ControlledInput() {
  const [value, setValue] = useState('');
  return <input value={value} onChange={e => setValue(e.target.value)} />;
}

// 非受控组件（DOM 管理状态，用 ref 获取值）
function UncontrolledInput() {
  const inputRef = useRef(null);
  const handleSubmit = () => {
    console.log(inputRef.current.value);
  };
  return <input ref={inputRef} defaultValue="默认值" />;
}
```

## 5. 组件通信

```jsx
// 父 → 子：Props
<Child name="张三" onUpdate={handleUpdate} />

// 子 → 父：回调函数
function Child({ onUpdate }) {
  return <button onClick={() => onUpdate('新数据')}>更新</button>;
}

// 跨层级：Context
const ThemeContext = React.createContext('light');

function App() {
  return (
    <ThemeContext.Provider value="dark">
      <DeepChild />
    </ThemeContext.Provider>
  );
}

function DeepChild() {
  const theme = useContext(ThemeContext);
  return <div>当前主题: {theme}</div>;
}
```

## 6. 生命周期（Hooks 对应）

```jsx
import { useState, useEffect, useRef } from 'react';

function LifecycleDemo() {
  const [data, setData] = useState(null);
  const mountedRef = useRef(false);

  // componentDidMount（空依赖数组）
  useEffect(() => {
    fetchData().then(setData);

    // componentWillUnmount（返回清理函数）
    return () => {
      console.log('组件卸载，清理副作用');
    };
  }, []);

  // componentDidUpdate（指定依赖）
  useEffect(() => {
    if (mountedRef.current) {
      console.log('data 更新了:', data);
    }
    mountedRef.current = true;
  }, [data]);

  return <div>{data ? JSON.stringify(data) : '加载中...'}</div>;
}
```
## 🎬 推荐视频资源

- [freeCodeCamp - React Full Course](https://www.youtube.com/watch?v=bMknfKXIFA8) — React完整课程（12小时）
- [Traversy Media - React Crash Course](https://www.youtube.com/watch?v=LDB4uaJ87e0) — React速成
- [Fireship - React in 100 Seconds](https://www.youtube.com/watch?v=Tn6-PIqc4UM) — React快速了解
### 📺 B站（Bilibili）
- [尚硅谷 - React18教程](https://www.bilibili.com/video/BV1ZB4y1Z7o8) — React18完整中文教程
- [黑马程序员 - React教程](https://www.bilibili.com/video/BV1Z44y1K7Fj) — React项目实战

### 🌐 其他平台
- [React官方中文文档](https://zh-hans.react.dev/) — 官方中文文档（2023新版）
