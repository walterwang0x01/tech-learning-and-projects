# 前端技术学习笔记
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> 本目录包含前端技术栈的学习笔记，按类别组织

## 📁 目录结构

```
frontend/
├── 00-HTML与CSS基础/        # HTML5 与 CSS3 基础
│   ├── HTML5语义化与新特性.md
│   ├── CSS3核心特性.md
│   ├── Flex与Grid布局.md
│   └── 响应式设计与媒体查询.md
│
├── 01-JavaScript基础/       # JavaScript 语言基础
│   ├── JavaScript数据类型与变量.md
│   ├── 函数与作用域.md
│   ├── 原型链与继承.md
│   ├── 异步编程与Promise.md
│   ├── ES6+新特性.md
│   └── DOM与BOM操作.md
│
├── 02-TypeScript/           # TypeScript 类型系统
│   ├── TypeScript基础入门.md
│   ├── TypeScript高级类型.md
│   └── TypeScript工程化实践.md
│
├── 03-React/                # React 生态
│   ├── React基础与JSX.md
│   ├── React Hooks深入.md
│   ├── React状态管理.md
│   ├── React Router路由.md
│   └── React性能优化.md
│
├── 04-Vue/                  # Vue 生态
│   ├── Vue3基础与组合式API.md
│   ├── Vue Router与Pinia.md
│   ├── Vue3高级特性.md
│   └── Vue生态工具库.md
│
├── 05-工程化与构建/          # 前端工程化
│   ├── Webpack核心概念.md
│   ├── Vite现代构建工具.md
│   ├── 包管理器npm-yarn-pnpm.md
│   ├── ESLint与Prettier代码规范.md
│   └── Monorepo与Turborepo.md
│
├── 06-CSS进阶/              # CSS 进阶方案
│   ├── CSS预处理器Sass-Less.md
│   ├── CSS-in-JS与CSS Modules.md
│   ├── Tailwind CSS实用优先.md
│   └── CSS动画与过渡.md
│
├── 07-Node.js/              # Node.js 服务端
│   ├── Node.js基础与模块系统.md
│   ├── Express与Koa框架.md
│   ├── Node.js数据库操作.md
│   └── Node.js性能优化.md
│
├── 08-测试/                 # 前端测试
│   ├── Jest单元测试.md
│   ├── React-Vue组件测试.md
│   ├── E2E测试Cypress-Playwright.md
│   └── 测试策略与最佳实践.md
│
├── 09-浏览器与网络/         # 浏览器原理与网络
│   ├── 浏览器渲染原理.md
│   ├── HTTP协议与缓存策略.md
│   ├── Web安全XSS-CSRF.md
│   └── 浏览器存储方案.md
│
├── 10-性能优化/             # 前端性能优化
│   ├── 性能指标与度量.md
│   ├── 加载性能优化.md
│   ├── 运行时性能优化.md
│   └── 图片与资源优化.md
│
├── 11-跨平台开发/           # 跨平台方案
│   ├── React Native移动开发.md
│   ├── Electron桌面应用.md
│   ├── 微信小程序开发.md
│   └── Flutter与Dart基础.md
│
├── 12-可视化与图形/         # 数据可视化
│   ├── Canvas与SVG基础.md
│   ├── ECharts数据可视化.md
│   ├── D3.js数据驱动文档.md
│   └── Three.js 3D图形.md
│
├── 13-微前端与架构/         # 前端架构
│   ├── 微前端架构方案.md
│   ├── 前端设计模式.md
│   └── 大型项目架构实践.md
│
├── 14-DevOps与部署/         # 部署与运维
│   ├── CI-CD与自动化部署.md
│   ├── Nginx前端部署配置.md
│   ├── Docker容器化前端.md
│   └── CDN与静态资源管理.md
│
├── 15-面试准备/             # 面试题整理
│   ├── JavaScript高频面试题.md
│   ├── 框架面试题React-Vue.md
│   └── 前端综合面试题.md
│
└── README.md                # 本文件
```

## 📚 内容说明

### HTML 与 CSS 基础

- **HTML5语义化与新特性**：语义化标签（header、nav、main、article、section、aside、footer）、表单新特性、多媒体标签（audio、video）、Canvas、Web Storage、Web Workers、Geolocation
- **CSS3核心特性**：选择器（属性选择器、伪类、伪元素）、盒模型（content-box、border-box）、BFC、层叠上下文、定位方案、浮动与清除
- **Flex与Grid布局**：Flex容器与项目属性、主轴与交叉轴、Grid网格布局、grid-template、gap、区域命名、响应式网格
- **响应式设计与媒体查询**：媒体查询语法、断点设计、移动优先策略、rem/em/vw/vh单位、视口设置、响应式图片

### JavaScript 基础

- **JavaScript数据类型与变量**：基本类型与引用类型、类型判断（typeof、instanceof、Object.prototype.toString）、类型转换、变量声明（var、let、const）、暂时性死区
- **函数与作用域**：函数声明与表达式、箭头函数、闭包、执行上下文、作用域链、this指向、call/apply/bind
- **原型链与继承**：原型对象、原型链、构造函数、new操作符、class语法、继承方式（原型链继承、组合继承、寄生组合继承）
- **异步编程与Promise**：回调函数、Promise（then/catch/finally、all/race/allSettled/any）、async/await、事件循环（宏任务、微任务）、Generator
- **ES6+新特性**：解构赋值、模板字符串、Symbol、Iterator、Map/Set/WeakMap/WeakSet、Proxy/Reflect、模块化（import/export）、可选链、空值合并
- **DOM与BOM操作**：DOM查询与操作、事件模型（捕获、冒泡、委托）、MutationObserver、IntersectionObserver、ResizeObserver、BOM对象（window、location、history、navigator）

### TypeScript

- **TypeScript基础入门**：基础类型、接口（interface）、类型别名（type）、联合类型、交叉类型、字面量类型、枚举、函数类型、类与修饰符
- **TypeScript高级类型**：泛型（泛型函数、泛型类、泛型约束）、条件类型、映射类型、模板字面量类型、infer关键字、工具类型（Partial、Required、Pick、Omit、Record、Exclude、Extract、ReturnType）、类型体操
- **TypeScript工程化实践**：tsconfig配置、声明文件（.d.ts）、模块解析、与React/Vue集成、严格模式、类型守卫、装饰器

### React 生态

- **React基础与JSX**：JSX语法、组件（函数组件、类组件）、Props与State、条件渲染、列表渲染、事件处理、受控与非受控组件、Refs
- **React Hooks深入**：useState、useEffect、useContext、useReducer、useMemo、useCallback、useRef、useId、自定义Hook、Hook规则与原理
- **React状态管理**：Context API、Redux Toolkit（createSlice、createAsyncThunk）、Zustand、Jotai、React Query/TanStack Query（数据获取与缓存）、状态管理选型
- **React Router路由**：路由配置、嵌套路由、动态路由、路由守卫、数据加载（loader）、React Router v6新特性
- **React性能优化**：React.memo、useMemo/useCallback、代码分割（React.lazy、Suspense）、虚拟列表、并发特性（useTransition、useDeferredValue）、React DevTools Profiler

### Vue 生态

- **Vue3基础与组合式API**：模板语法、响应式原理（ref、reactive、computed、watch）、组件通信（props、emit、provide/inject）、生命周期、组合式API（setup、composables）
- **Vue Router与Pinia**：路由配置、导航守卫、动态路由、路由懒加载、Pinia状态管理（defineStore、storeToRefs）、Pinia插件
- **Vue3高级特性**：Teleport、Suspense、自定义指令、插件开发、渲染函数与JSX、Transition动画、KeepAlive、异步组件
- **Vue生态工具库**：Nuxt3（SSR/SSG）、VueUse工具集、Element Plus/Ant Design Vue、Vitest测试、unplugin自动导入

### 工程化与构建

- **Webpack核心概念**：Entry/Output、Loader（babel-loader、css-loader、file-loader）、Plugin（HtmlWebpackPlugin、MiniCssExtractPlugin）、代码分割、Tree Shaking、HMR热更新、优化配置
- **Vite现代构建工具**：ESM原生模块、依赖预构建、HMR、插件系统、Rollup打包、环境变量、SSR支持、性能对比
- **包管理器npm-yarn-pnpm**：npm（package.json、scripts、语义化版本）、yarn（workspaces、PnP）、pnpm（硬链接、内容寻址存储、workspace）、lock文件、依赖管理策略
- **ESLint与Prettier代码规范**：ESLint配置与规则、Prettier格式化、EditorConfig、Husky + lint-staged、commitlint提交规范、Stylelint CSS检查
- **Monorepo与Turborepo**：Monorepo概念与优势、pnpm workspace、Turborepo任务编排与缓存、Nx构建系统、Lerna、共享配置与依赖

### CSS 进阶

- **CSS预处理器Sass-Less**：Sass（变量、嵌套、混入、继承、函数、模块化）、Less（变量、混入、运算）、PostCSS（Autoprefixer、postcss-preset-env）
- **CSS-in-JS与CSS Modules**：CSS Modules（局部作用域、组合）、styled-components、Emotion、vanilla-extract、零运行时方案、CSS作用域方案对比
- **Tailwind CSS实用优先**：工具类优先理念、配置定制（theme、extend）、响应式设计、暗色模式、JIT模式、组件抽象、与框架集成
- **CSS动画与过渡**：transition过渡、animation关键帧、transform变换、GPU加速、requestAnimationFrame、Web Animations API、FLIP动画技术、Framer Motion/GSAP

### Node.js

- **Node.js基础与模块系统**：事件循环、模块系统（CommonJS、ESM）、Buffer与Stream、文件系统（fs）、path模块、child_process、cluster集群
- **Express与Koa框架**：Express（路由、中间件、错误处理、模板引擎）、Koa（洋葱模型、Context、中间件编写）、NestJS（模块、控制器、服务、依赖注入）
- **Node.js数据库操作**：MySQL（mysql2、连接池）、MongoDB（Mongoose、聚合）、Redis（ioredis）、Prisma ORM、TypeORM、数据库迁移
- **Node.js性能优化**：内存泄漏排查、CPU密集型任务处理（Worker Threads）、Stream流式处理、连接池优化、PM2进程管理、日志管理（winston、pino）

### 前端测试

- **Jest单元测试**：测试基础（describe、it、expect）、匹配器、Mock函数、异步测试、快照测试、覆盖率报告、Vitest对比
- **React-Vue组件测试**：React Testing Library（render、screen、userEvent、waitFor）、Vue Test Utils（mount、shallowMount）、组件交互测试、Hook测试
- **E2E测试Cypress-Playwright**：Cypress（选择器、断言、网络拦截、自定义命令）、Playwright（多浏览器、自动等待、截图对比、API测试）、测试录制
- **测试策略与最佳实践**：测试金字塔、TDD/BDD、测试覆盖率策略、Mock策略、CI集成测试、可视化回归测试

### 浏览器与网络

- **浏览器渲染原理**：DOM树构建、CSSOM、渲染树、布局（Layout/Reflow）、绘制（Paint）、合成（Composite）、关键渲染路径、重排与重绘优化
- **HTTP协议与缓存策略**：HTTP/1.1、HTTP/2（多路复用、头部压缩、服务器推送）、HTTP/3（QUIC）、HTTPS/TLS、强缓存（Cache-Control、Expires）、协商缓存（ETag、Last-Modified）、Service Worker缓存
- **Web安全XSS-CSRF**：XSS（存储型、反射型、DOM型、防御策略CSP）、CSRF（Token、SameSite Cookie）、点击劫持、CORS跨域、Content Security Policy、HTTPS、子资源完整性（SRI）
- **浏览器存储方案**：Cookie（属性、安全性）、localStorage/sessionStorage、IndexedDB、Cache API、Web SQL（已废弃）、存储容量与限制、存储方案选型

### 性能优化

- **性能指标与度量**：Core Web Vitals（LCP、FID/INP、CLS）、FCP、TTFB、TTI、Lighthouse、Performance API、Web Vitals库、性能监控平台
- **加载性能优化**：代码分割与懒加载、Tree Shaking、资源压缩（Gzip/Brotli）、预加载（preload/prefetch/preconnect）、SSR/SSG、骨架屏、关键CSS内联
- **运行时性能优化**：虚拟列表（react-virtualized/vue-virtual-scroller）、防抖节流、Web Worker、requestAnimationFrame、避免强制同步布局、内存泄漏排查
- **图片与资源优化**：图片格式选择（WebP、AVIF）、响应式图片（srcset、picture）、图片懒加载、SVG优化、字体优化（font-display、子集化）、资源CDN

### 跨平台开发

- **React Native移动开发**：环境搭建、核心组件（View、Text、Image、ScrollView、FlatList）、样式系统、导航（React Navigation）、原生模块、Expo、性能优化
- **Electron桌面应用**：主进程与渲染进程、IPC通信、窗口管理、菜单与托盘、自动更新、打包发布（electron-builder）、安全最佳实践
- **微信小程序开发**：项目结构、WXML/WXSS、组件与API、生命周期、数据绑定、网络请求、分包加载、Taro/uni-app跨端框架
- **Flutter与Dart基础**：Dart语法、Widget体系（StatelessWidget、StatefulWidget）、布局系统、路由导航、状态管理（Provider、Riverpod、Bloc）、平台通道

### 数据可视化与图形

- **Canvas与SVG基础**：Canvas 2D API（绑定、路径、文本、图像）、SVG基础（基本图形、路径、滤镜、动画）、Canvas vs SVG选型
- **ECharts数据可视化**：图表类型（折线图、柱状图、饼图、散点图、地图）、配置项、交互事件、数据更新、主题定制、大数据量优化
- **D3.js数据驱动文档**：选择集、数据绑定（enter/update/exit）、比例尺、坐标轴、过渡动画、力导向图、地理投影、可复用组件
- **Three.js 3D图形**：场景（Scene）、相机（Camera）、渲染器（Renderer）、几何体与材质、光照、纹理、动画循环、模型加载（GLTF）、后期处理

### 微前端与架构

- **微前端架构方案**：qiankun（基于single-spa）、Module Federation（Webpack5）、micro-app、无界（wujie）、应用通信、样式隔离、JS沙箱
- **前端设计模式**：观察者/发布订阅模式、策略模式、代理模式、装饰器模式、单例模式、工厂模式、MVC/MVP/MVVM、组件设计模式（HOC、Render Props、Hooks）
- **大型项目架构实践**：目录结构设计、分层架构、状态管理策略、API层封装、错误处理体系、权限控制、国际化（i18n）、主题切换

### DevOps 与部署

- **CI-CD与自动化部署**：GitHub Actions（工作流配置、矩阵构建、缓存）、GitLab CI、Jenkins、自动化测试、自动化发布、版本管理（Changesets）
- **Nginx前端部署配置**：静态资源服务、SPA路由配置（try_files）、反向代理、Gzip压缩、缓存配置、HTTPS配置、负载均衡
- **Docker容器化前端**：Dockerfile编写（多阶段构建）、Docker Compose、镜像优化、环境变量注入、健康检查、CI/CD集成
- **CDN与静态资源管理**：CDN原理与选型、资源哈希与缓存策略、域名分片、资源预热、回源策略、多环境资源管理

### 面试准备

- **JavaScript高频面试题**：数据类型、闭包、原型链、事件循环、Promise、深拷贝、手写题（防抖节流、Promise.all、柯里化、发布订阅、new操作符）
- **框架面试题React-Vue**：React（虚拟DOM、Diff算法、Fiber架构、Hooks原理、状态管理对比）、Vue（响应式原理、Diff算法、Composition API、nextTick、虚拟DOM）
- **前端综合面试题**：性能优化、浏览器原理、网络协议、安全、工程化、设计模式、算法题、系统设计题

## 🎯 学习路径建议

### 基础阶段
1. **HTML与CSS**：语义化标签 → CSS盒模型 → Flex/Grid布局 → 响应式设计
2. **JavaScript**：数据类型 → 函数与作用域 → 原型链 → 异步编程 → ES6+新特性 → DOM操作
3. **TypeScript**：基础类型 → 高级类型 → 工程化实践

### 框架阶段
4. **React 或 Vue**：选择一个深入学习，掌握核心概念、状态管理、路由
5. **CSS进阶**：预处理器 → CSS方案选型 → Tailwind CSS → 动画
6. **工程化**：Webpack/Vite → 包管理 → 代码规范 → Monorepo

### 进阶阶段
7. **Node.js**：基础模块 → Web框架 → 数据库操作 → 性能优化
8. **测试**：单元测试 → 组件测试 → E2E测试
9. **浏览器与网络**：渲染原理 → HTTP协议 → Web安全 → 存储方案
10. **性能优化**：性能指标 → 加载优化 → 运行时优化 → 资源优化

### 高级阶段
11. **跨平台**：React Native / Electron / 小程序 / Flutter
12. **可视化**：Canvas/SVG → ECharts → D3.js → Three.js
13. **架构**：微前端 → 设计模式 → 大型项目架构
14. **DevOps**：CI/CD → Nginx → Docker → CDN
15. **面试准备**：JS面试题 → 框架面试题 → 综合面试题

## 📖 使用说明

- 所有笔记从个人学习过程中整理，已移除敏感信息
- 包含代码示例和最佳实践
- 适合系统学习和面试准备

## 🔗 相关资源

- [MDN Web Docs](https://developer.mozilla.org/zh-CN/)
- [React 官方文档](https://react.dev/)
- [Vue 官方文档](https://cn.vuejs.org/)
- [TypeScript 官方文档](https://www.typescriptlang.org/)
- [Vite 官方文档](https://cn.vitejs.dev/)
- [Node.js 官方文档](https://nodejs.org/zh-cn/docs/)
