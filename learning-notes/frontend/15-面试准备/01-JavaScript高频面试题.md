# JavaScript 高频面试题
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 数据类型

```javascript
// typeof null === 'object' 的原因？
// 历史遗留 bug，JS 最初用 32 位表示值，低 3 位表示类型，000 表示对象，null 全为 0

// [] == false 为什么是 true？
// [] → '' → 0, false → 0, 0 == 0 → true

// 0.1 + 0.2 !== 0.3 的原因？
// IEEE 754 浮点数精度问题
// 解决：Math.abs(0.1 + 0.2 - 0.3) < Number.EPSILON
```

## 2. 手写题

```javascript
// 防抖
function debounce(fn, delay) {
  let timer;
  return function(...args) {
    clearTimeout(timer);
    timer = setTimeout(() => fn.apply(this, args), delay);
  };
}

// 节流
function throttle(fn, interval) {
  let lastTime = 0;
  return function(...args) {
    const now = Date.now();
    if (now - lastTime >= interval) {
      lastTime = now;
      fn.apply(this, args);
    }
  };
}

// 深拷贝
function deepClone(obj, map = new WeakMap()) {
  if (obj === null || typeof obj !== 'object') return obj;
  if (obj instanceof Date) return new Date(obj);
  if (obj instanceof RegExp) return new RegExp(obj);
  if (map.has(obj)) return map.get(obj);
  const clone = Array.isArray(obj) ? [] : {};
  map.set(obj, clone);
  for (const key of Object.keys(obj)) {
    clone[key] = deepClone(obj[key], map);
  }
  return clone;
}

// Promise.all
function promiseAll(promises) {
  return new Promise((resolve, reject) => {
    const results = [];
    let count = 0;
    promises.forEach((p, i) => {
      Promise.resolve(p).then(
        (value) => {
          results[i] = value;
          if (++count === promises.length) resolve(results);
        },
        reject
      );
    });
  });
}

// 柯里化
function curry(fn) {
  return function curried(...args) {
    if (args.length >= fn.length) return fn.apply(this, args);
    return (...moreArgs) => curried(...args, ...moreArgs);
  };
}

// 发布订阅
class EventEmitter {
  constructor() { this.events = {}; }
  on(event, fn) {
    (this.events[event] ||= []).push(fn);
    return this;
  }
  off(event, fn) {
    this.events[event] = this.events[event]?.filter(f => f !== fn);
    return this;
  }
  emit(event, ...args) {
    this.events[event]?.forEach(fn => fn(...args));
    return this;
  }
  once(event, fn) {
    const wrapper = (...args) => { fn(...args); this.off(event, wrapper); };
    return this.on(event, wrapper);
  }
}

// new 操作符
function myNew(Constructor, ...args) {
  const obj = Object.create(Constructor.prototype);
  const result = Constructor.apply(obj, args);
  return result instanceof Object ? result : obj;
}

// instanceof
function myInstanceof(obj, Constructor) {
  let proto = Object.getPrototypeOf(obj);
  while (proto) {
    if (proto === Constructor.prototype) return true;
    proto = Object.getPrototypeOf(proto);
  }
  return false;
}

// 数组扁平化
function flatten(arr, depth = Infinity) {
  return depth > 0
    ? arr.reduce((acc, val) =>
        acc.concat(Array.isArray(val) ? flatten(val, depth - 1) : val), [])
    : arr.slice();
}
// 或 arr.flat(Infinity)

// 数组去重
const unique = (arr) => [...new Set(arr)];
```

## 3. 闭包与作用域

```javascript
// 经典题
for (var i = 0; i < 5; i++) {
  setTimeout(() => console.log(i), 0);
}
// 输出：5 5 5 5 5
// 解决：let / IIFE / setTimeout 第三个参数

// 事件循环
console.log('1');
setTimeout(() => console.log('2'), 0);
Promise.resolve().then(() => console.log('3'));
Promise.resolve().then(() => {
  console.log('4');
  setTimeout(() => console.log('5'), 0);
});
console.log('6');
// 输出：1 6 3 4 2 5
```


## 4. 2026 年 JavaScript 面试新增热点

> 🔄 更新于 2026-05-02

<!-- version-check: ES2025/2026, TypeScript 5.9, Node.js 24 LTS, checked 2026-05-02 -->

### ES2025/2026 新特性

```javascript
// Q: Set 的新方法有哪些？（ES2025）
// A: Set 终于有了集合运算方法：
const a = new Set([1, 2, 3]);
const b = new Set([2, 3, 4]);

a.union(b);           // Set {1, 2, 3, 4} — 并集
a.intersection(b);    // Set {2, 3} — 交集
a.difference(b);      // Set {1} — 差集
a.symmetricDifference(b); // Set {1, 4} — 对称差集
a.isSubsetOf(b);      // false — 子集判断
a.isSupersetOf(b);    // false — 超集判断

// Q: Promise.withResolvers() 是什么？（ES2025）
// A: 将 resolve/reject 从 Promise 构造函数中提取出来
const { promise, resolve, reject } = Promise.withResolvers();
// 等价于：
// let resolve, reject;
// const promise = new Promise((res, rej) => { resolve = res; reject = rej; });
// 适用场景：需要在 Promise 外部控制 resolve/reject

// Q: structuredClone 和 JSON.parse(JSON.stringify()) 的区别？
// A: structuredClone 是原生深拷贝 API：
const obj = { date: new Date(), regex: /test/i, map: new Map() };
const clone = structuredClone(obj);
// ✅ 保留 Date、RegExp、Map、Set、ArrayBuffer 等类型
// ✅ 处理循环引用
// ❌ 不能克隆函数、DOM 节点、Symbol
// JSON 方式会丢失 Date（变字符串）、RegExp、Map 等

// Q: Iterator Helpers 是什么？（ES2025）
// A: 为迭代器添加了 map/filter/take 等链式方法：
function* naturals() {
  let n = 1;
  while (true) yield n++;
}
const result = naturals()
  .filter(n => n % 2 === 0)  // 偶数
  .map(n => n * n)            // 平方
  .take(5)                    // 取前 5 个
  .toArray();                 // [4, 16, 36, 64, 100]
// 惰性求值，不会创建中间数组
```

### TypeScript 面试题

```
Q: TypeScript 5.9 的 --strictInference 是什么？
A: 更严格的类型推断模式，减少隐式 any 的场景。
   例如：泛型函数参数推断更精确，
   减少需要手动标注类型的情况。

Q: TypeScript 7.0 Go 编译器对开发者有什么影响？
A: 预计构建速度提升 10x，但：
   - API 兼容，不需要改代码
   - .d.ts 声明文件格式不变
   - tsconfig.json 配置不变
   - 主要影响 CI/CD 构建时间和 IDE 响应速度
   当前稳定版 5.9，7.0 预计 2026 年底。

Q: satisfies 关键字的作用？
A: 验证表达式是否满足某个类型，但保留推断的更窄类型：
   type Colors = Record<string, string | string[]>;
   const palette = {
     red: '#ff0000',
     green: ['#00ff00', '#008000'],
   } satisfies Colors;
   // palette.red 的类型是 string（不是 string | string[]）
   // 既有类型检查，又保留精确类型
```

### Node.js 面试题

```
Q: Node.js 24 LTS 有哪些重要变化？
A: 代号 Krypton（2025-04 发布，2025-10 进入 LTS）：
   <!-- 修复于 2026-05-19: 修正"安装速度提升 65%"为官方说法（官方未公布具体百分比） -->
   - V8 13.6（更快的 JS 执行）
   - npm 11（性能、安全和现代 JS 包兼容性改进）
   - Undici 7（内置 HTTP 客户端）
   - Windows 平台从 MSVC 切换到 ClangCL
   - 支持至 2028-04
   - require(esm) 默认启用

Q: Node.js 的 ESM 和 CJS 互操作现状？
A: Node.js 24 中：
   - require() 可以加载 ESM 模块（默认启用）
   - import 可以加载 CJS 模块（一直支持）
   - 新项目推荐 ESM（"type": "module"）
   - package.json 的 exports 字段控制双格式发布
```

> 来源：[ES2025 Features](https://tc39.es/ecma262/)、[TypeScript 5.9 Release](https://devblogs.microsoft.com/typescript/)
