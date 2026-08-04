# 异步编程与 Promise
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 事件循环（Event Loop）

```
┌───────────────────────┐
│      调用栈 (Call Stack)  │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│    微任务队列 (Microtask)  │  ← Promise.then, queueMicrotask, MutationObserver
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│    宏任务队列 (Macrotask)  │  ← setTimeout, setInterval, I/O, UI渲染
└───────────────────────┘

执行顺序：同步代码 → 微任务 → 宏任务（循环）
```

```javascript
console.log('1');                    // 同步
setTimeout(() => console.log('2'), 0); // 宏任务
Promise.resolve().then(() => console.log('3')); // 微任务
console.log('4');                    // 同步
// 输出：1, 4, 3, 2
```

## 2. Promise

### 2.1 基本用法

```javascript
const promise = new Promise((resolve, reject) => {
  // 异步操作
  setTimeout(() => {
    const success = true;
    if (success) {
      resolve('成功数据');
    } else {
      reject(new Error('失败原因'));
    }
  }, 1000);
});

promise
  .then(data => console.log(data))
  .catch(err => console.error(err))
  .finally(() => console.log('完成'));
```

### 2.2 链式调用

```javascript
fetch('/api/user')
  .then(res => res.json())
  .then(user => fetch(`/api/posts?userId=${user.id}`))
  .then(res => res.json())
  .then(posts => console.log(posts))
  .catch(err => console.error(err));
```

### 2.3 静态方法

```javascript
// Promise.all：全部成功才成功，一个失败就失败
const results = await Promise.all([
  fetch('/api/users'),
  fetch('/api/posts'),
  fetch('/api/comments'),
]);

// Promise.allSettled：等待全部完成，不管成功失败
const results = await Promise.allSettled([p1, p2, p3]);
// [{ status: 'fulfilled', value: ... }, { status: 'rejected', reason: ... }]

// Promise.race：返回最先完成的（成功或失败）
const result = await Promise.race([fetchData(), timeout(5000)]);

// Promise.any：返回最先成功的，全部失败才失败
const result = await Promise.any([source1(), source2(), source3()]);
```

## 3. async / await

```javascript
// async 函数返回 Promise
async function fetchUser(id) {
  try {
    const res = await fetch(`/api/users/${id}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const user = await res.json();
    return user;
  } catch (err) {
    console.error('获取用户失败:', err);
    throw err;
  }
}

// 并发请求
async function fetchAll() {
  const [users, posts] = await Promise.all([
    fetch('/api/users').then(r => r.json()),
    fetch('/api/posts').then(r => r.json()),
  ]);
  return { users, posts };
}

// 顺序执行
async function sequential(urls) {
  const results = [];
  for (const url of urls) {
    const res = await fetch(url);
    results.push(await res.json());
  }
  return results;
}

// 控制并发数
async function concurrentLimit(tasks, limit) {
  const results = [];
  const executing = new Set();

  for (const task of tasks) {
    const p = task().then(result => {
      executing.delete(p);
      return result;
    });
    executing.add(p);
    results.push(p);

    if (executing.size >= limit) {
      await Promise.race(executing);
    }
  }
  return Promise.all(results);
}
```

## 4. 手写 Promise（简化版）

```javascript
class MyPromise {
  constructor(executor) {
    this.state = 'pending';
    this.value = undefined;
    this.callbacks = [];

    const resolve = (value) => {
      if (this.state !== 'pending') return;
      this.state = 'fulfilled';
      this.value = value;
      this.callbacks.forEach(cb => cb.onFulfilled(value));
    };

    const reject = (reason) => {
      if (this.state !== 'pending') return;
      this.state = 'rejected';
      this.value = reason;
      this.callbacks.forEach(cb => cb.onRejected(reason));
    };

    try { executor(resolve, reject); }
    catch (err) { reject(err); }
  }

  then(onFulfilled, onRejected) {
    return new MyPromise((resolve, reject) => {
      const handle = (callback, fallback) => {
        try {
          const fn = typeof callback === 'function' ? callback : fallback;
          resolve(fn(this.value));
        } catch (err) { reject(err); }
      };

      if (this.state === 'fulfilled') {
        queueMicrotask(() => handle(onFulfilled, v => v));
      } else if (this.state === 'rejected') {
        queueMicrotask(() => handle(onRejected, e => { throw e; }));
      } else {
        this.callbacks.push({
          onFulfilled: () => handle(onFulfilled, v => v),
          onRejected: () => handle(onRejected, e => { throw e; }),
        });
      }
    });
  }

  catch(onRejected) { return this.then(null, onRejected); }
}
```
## 5. ES2025/ES2026 异步编程新特性

> 🔄 更新于 2026-05-04

<!-- version-check: ES2025 Promise.withResolvers, ES2026 using/await using, checked 2026-05-04 -->

### 5.1 Promise.withResolvers()（ES2025）

将 Promise 的 resolve/reject 从构造函数中提取出来，适合需要在外部控制 Promise 的场景。

浏览器支持：~91%（Chrome 119+、Firefox 121+、Safari 17.2+）。

```javascript
// 传统写法：resolve/reject 被锁在构造函数内
let resolve, reject;
const promise = new Promise((res, rej) => {
  resolve = res;
  reject = rej;
});

// ES2025 写法：一行搞定
const { promise, resolve, reject } = Promise.withResolvers();

// 实际场景：事件驱动的异步操作
function waitForEvent(target, eventName) {
  const { promise, resolve } = Promise.withResolvers();
  target.addEventListener(eventName, resolve, { once: true });
  return promise;
}

// 实际场景：超时控制
function withTimeout(asyncFn, ms) {
  const { promise, resolve, reject } = Promise.withResolvers();
  asyncFn().then(resolve, reject);
  setTimeout(() => reject(new Error(`超时 ${ms}ms`)), ms);
  return promise;
}
```

### 5.2 显式资源管理 using / await using（ES2026）

类似 Python 的 `with` 或 C# 的 `using`，确保资源在作用域退出时自动清理。

浏览器支持：Chrome 134+、Node.js 24+（V8 13.6）。来源：[V8 Explicit Resource Management](https://v8.dev/features/explicit-resource-management)

```javascript
// 定义可释放资源：实现 Symbol.dispose
class FileHandle {
  #handle;
  constructor(path) {
    this.#handle = openFile(path);
    console.log(`打开文件: ${path}`);
  }
  read() { return readFrom(this.#handle); }
  // 同步释放
  [Symbol.dispose]() {
    closeFile(this.#handle);
    console.log('文件已关闭');
  }
}

// using 声明：作用域退出时自动调用 Symbol.dispose
{
  using file = new FileHandle('/data/config.json');
  const data = file.read();
  // 即使抛出异常，file 也会被自动关闭
} // ← 这里自动调用 file[Symbol.dispose]()

// await using：异步资源释放
class DbConnection {
  static async connect(url) {
    const conn = new DbConnection();
    await conn.#init(url);
    return conn;
  }
  // 异步释放
  async [Symbol.asyncDispose]() {
    await this.#pool.end();
    console.log('数据库连接已释放');
  }
}

async function queryUsers() {
  await using db = await DbConnection.connect(DB_URL);
  return await db.query('SELECT * FROM users');
} // ← 自动 await db[Symbol.asyncDispose]()

// DisposableStack：聚合多个资源
{
  using stack = new DisposableStack();
  const file = stack.use(new FileHandle('/tmp/a.txt'));
  const lock = stack.use(acquireLock('resource-1'));
  stack.defer(() => console.log('额外清理'));
  // 退出时按 LIFO 顺序释放所有资源
}
```

### 5.3 Temporal API（ES2026，Stage 4）

替代 `Date` 对象的全新日期时间 API，2026-03 达到 TC39 Stage 4，正式进入 ES2026 规范。来源：[Temporal API Blog](https://jadjoubran.io/blog/javascript-temporal-api)

```javascript
// 当前时刻（带时区）
const now = Temporal.Now.zonedDateTimeISO();
// 2026-05-04T14:30:00+08:00[Asia/Shanghai]

// 纯日期（无时间、无时区）
const birthday = Temporal.PlainDate.from('1990-06-15');
const nextBirthday = birthday.with({ year: 2026 });

// 纯时间
const meeting = Temporal.PlainTime.from('14:30');

// 日期时间计算（不可变，返回新对象）
const deadline = Temporal.PlainDate.from('2026-05-04');
const extended = deadline.add({ days: 30 });
// 2026-06-03

// 时区转换
const tokyoTime = Temporal.Now.zonedDateTimeISO('Asia/Tokyo');
const nyTime = tokyoTime.withTimeZone('America/New_York');

// 两个日期之间的差值
const start = Temporal.PlainDate.from('2026-01-01');
const end = Temporal.PlainDate.from('2026-05-04');
const diff = start.until(end);
// P4M3D（4个月3天）
console.log(diff.months); // 4
console.log(diff.days);   // 3

// 比较
Temporal.PlainDate.compare(start, end); // -1（start 更早）
```

## 🎬 推荐视频资源

- [Fireship - Async Await in 100 Seconds](https://www.youtube.com/watch?v=vn3tm0quoqE) — 异步编程快速了解
- [Traversy Media - Async JS Crash Course](https://www.youtube.com/watch?v=PoRJizFvM7s) — 异步JS速成
- [The Net Ninja - Async JavaScript](https://www.youtube.com/playlist?list=PL4cUxeGkcC9jx2TTZk3IGWKSbtugYdrlu) — 异步JS系列教程
