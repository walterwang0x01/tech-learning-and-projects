# 框架面试题 React / Vue
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. React 面试题

### 虚拟 DOM 与 Diff 算法

```
虚拟 DOM：用 JS 对象描述 DOM 结构，减少直接操作真实 DOM

Diff 策略（O(n)）：
1. 同层比较，不跨层级
2. 不同类型的元素 → 销毁重建
3. 通过 key 标识同一元素（列表优化）

React Fiber：
- 将渲染工作拆分为多个小任务
- 可中断、可恢复、可设优先级
- 实现时间切片（Time Slicing）
- 支持并发模式（Concurrent Mode）
```

### Hooks 原理

```
- Hooks 依赖调用顺序（链表结构）
- 不能在条件语句中使用 Hook（破坏顺序）
- useState 通过闭包保存状态
- useEffect 在 commit 阶段异步执行
- useLayoutEffect 在 DOM 更新后同步执行
```

### 常见问题

```
Q: React 中 key 的作用？
A: 帮助 Diff 算法识别列表中哪些元素变化了，避免不必要的销毁重建。
   不要用 index 作为 key（列表顺序变化时会出问题）。

Q: setState 是同步还是异步？
A: React 18 中，所有 setState 都是批量异步更新（自动批处理）。
   如果需要同步获取更新后的值，使用 flushSync。

Q: useEffect 和 useLayoutEffect 的区别？
A: useEffect 异步执行，不阻塞渲染；
   useLayoutEffect 同步执行，在 DOM 更新后、浏览器绘制前执行。
   需要读取 DOM 布局信息时用 useLayoutEffect。

Q: React.memo、useMemo、useCallback 的区别？
A: React.memo — 组件级别，浅比较 props
   useMemo — 缓存计算结果
   useCallback — 缓存函数引用
```

## 2. Vue 面试题

### 响应式原理

```
Vue 2：Object.defineProperty
  - 劫持对象属性的 getter/setter
  - 缺点：无法检测属性新增/删除、数组索引变化

Vue 3：Proxy
  - 代理整个对象
  - 支持属性新增/删除、数组操作
  - 惰性响应式（访问时才递归代理）

依赖收集：
  - 读取数据时（getter）→ track 收集依赖
  - 修改数据时（setter）→ trigger 触发更新
```

### Diff 算法

```
Vue 3 Diff（双端 + 最长递增子序列）：
1. 从头部开始比较相同节点
2. 从尾部开始比较相同节点
3. 处理新增节点
4. 处理删除节点
5. 处理乱序节点（最长递增子序列优化移动次数）
```

### 常见问题

```
Q: computed 和 watch 的区别？
A: computed — 有缓存，依赖不变不重新计算，适合派生数据
   watch — 无缓存，适合执行副作用（API 调用、DOM 操作）

Q: v-if 和 v-show 的区别？
A: v-if — 条件渲染，切换时销毁/重建 DOM
   v-show — display 切换，DOM 始终存在
   频繁切换用 v-show，条件很少变化用 v-if

Q: nextTick 的原理？
A: Vue 异步更新 DOM，nextTick 在 DOM 更新后执行回调。
   内部使用 Promise.then（微任务）实现。

Q: Composition API vs Options API？
A: Composition API 更好的逻辑复用（composables）、更好的 TypeScript 支持、
   更灵活的代码组织。Options API 更直观，适合简单组件。
```

## 3. 通用框架问题

```
Q: 虚拟 DOM 一定比直接操作 DOM 快吗？
A: 不一定。虚拟 DOM 的优势是：
   1. 批量更新，减少 DOM 操作次数
   2. 跨平台（SSR、Native）
   3. 声明式编程，开发体验好
   对于简单的单次 DOM 操作，直接操作更快。

Q: SSR 的优缺点？
A: 优点：首屏快、SEO 好
   缺点：服务器压力大、开发复杂度高、部分浏览器 API 不可用

Q: 如何选择 React 还是 Vue？
A: React — 大型项目、灵活度高、生态丰富、函数式编程
   Vue — 上手快、模板语法直观、官方工具链完善、渐进式
```

## 4. 2026 年框架面试新热点

> 🔄 更新于 2026-05-02

<!-- version-check: React 19.2.4, Vue 3.6 Vapor Mode, React Router 7.6.x, checked 2026-05-20 -->

### React 19 与 React Compiler

```
Q: React 19 有哪些重要的新 Hook？
A: 四个新 Hook：
   1. use() — 在组件中读取 Promise 或 Context，替代 useEffect 数据获取
   2. useActionState — 管理表单提交状态（pending/error/result）
   3. useFormStatus — 获取父级 <form> 的提交状态（pending/data/method）
   4. useOptimistic — 乐观更新 UI，提交失败自动回滚

Q: React Compiler 是什么？它如何影响性能优化？
A: React Compiler 在编译时自动分析组件依赖关系，
   自动插入 useMemo/useCallback 等记忆化优化。
   影响：
   - 不再需要手动写 useMemo/useCallback/React.memo
   - 编译器比人更精确地判断哪些值需要缓存
   - 不改变代码行为，只优化性能
   - 需要组件是纯函数（无副作用）

Q: React Server Components（RSC）是什么？什么时候用？
A: RSC 是只在服务端执行的组件，代码不会发送到浏览器。
   适用场景：
   - 数据获取密集的页面（直接访问数据库/API）
   - 减少客户端 JS 体积（大型依赖留在服务端）
   - SEO 关键页面
   不适用：
   - 需要浏览器 API（事件、状态、Effect）
   - 高交互性组件
   关键概念：'use client' 指令标记客户端边界。

Q: React 19 的自动批处理和 React 18 有什么区别？
A: React 18 引入了自动批处理（所有 setState 都批量更新）。
   React 19 进一步优化：
   - Actions 概念：async 函数中的状态更新也自动批处理
   - Transitions 更智能：可中断的低优先级更新
   - 表单场景：useActionState 自动处理 pending 状态
```

### Vue 3.6 Vapor Mode

```
Q: Vue 3.6 Vapor Mode 是什么？
A: Vapor Mode 是 Vue 3.6 引入的新编译策略（2025-12 进入 beta，截至 2026-05 仍在 beta）：
   <!-- 修复于 2026-05-19: 标注 beta 状态，避免读者误以为已稳定 -->
   - 跳过虚拟 DOM，直接编译为原生 DOM 操作
   - 性能接近 Solid.js 和 Svelte 5
   - 组件级别 opt-in（不是全局开关）
   - 不改变开发者写法，编译器自动处理
   - 适合性能敏感的组件（大列表、动画密集）
   - 生产使用建议等待稳定版

Q: Vue 3 的 alien-signals 响应式引擎是什么？
A: Vue 3.6 底层响应式系统从 @vue/reactivity 重构为
   alien-signals 引擎，核心改进：
   - 更快的依赖追踪（基于版本号而非 Set）
   - 更低的内存占用
   - 更精确的更新粒度
   对开发者透明，API 不变。

Q: @Observable（Vue）和 Composition API 的关系？
A: 这是 iOS 的概念。Vue 中对应的是：
   - Options API → Composition API 的演进
   - ref/reactive → 响应式基础
   - composables → 逻辑复用（替代 mixins）
   2026 年新项目推荐 Composition API + <script setup>。
```

### 2026 年框架面试高频新题

```
Q: React Router v7 和 v6 有什么区别？
A: v7（2024-11 GA，当前 7.6.x）从路由库变为全栈框架：
   <!-- 修复于 2026-05-20: 7.9.x → 7.6.x（npm 确认） -->
   - 统一包名（react-router 主包，react-router-dom 仅做转发）
   - Framework Mode：内置 SSR/RSC 支持（吸收了 Remix）
   - 三种使用模式：Declarative / Data / Framework
   - 从 v6 升级是非破坏性的（启用所有 future flags 后）
   - Vite 8 原生支持

Q: Nuxt 4 和 Nuxt 3 的主要区别？
A: Nuxt 4 稳定版（v4.4.3，2026-05）：
   <!-- 修复于 2026-05-19: 4.4.2 → 4.4.3，与 04-Vue 文档保持一致 -->
   - Vue Router 5 集成（4.4 升级，移除 unplugin-vue-router 依赖）
   - 更好的 TypeScript 支持
   - Nuxt 3 将于 2026-07-31 EOL
   - 新项目应直接使用 Nuxt 4

Q: 2026 年状态管理怎么选？
A: React：
   - 简单场景：useState + Context
   - 中等复杂度：Zustand（轻量、无 Provider）
   - 服务端状态：TanStack Query
   - 大型应用：Redux Toolkit（仍然可靠）
   Vue：
   - Pinia（官方推荐，替代 Vuex）
   - 简单场景：composables + ref

Q: 什么是 React Compiler 的 "纯函数" 要求？
A: React Compiler 要求组件和 Hook 是纯函数：
   - 相同输入产生相同输出
   - 渲染期间不修改外部变量
   - 不在渲染期间读取可变的外部状态
   违反纯函数规则的代码，Compiler 会跳过优化。
```

> 来源：[React Interview Playbook 2026](https://bigdevsoon.me/guides/react-interview-playbook/)、[Vue 3.6 Vapor Mode](https://vueschool.io/articles/news/vn-talk-evan-you-preview-of-vue-3-6-vapor-mode/)
