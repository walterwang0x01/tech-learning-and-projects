# 技术学习笔记
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> 本文件夹包含从 private-notes 中提取的技术学习内容，已移除所有敏感信息。

## 📚 内容说明

这些笔记是从个人学习过程中整理的技术内容，包括：

- ✅ 技术概念和原理
- ✅ 最佳实践和设计模式
- ✅ 代码示例和实现
- ✅ 学习路径和总结

**注意**：所有内容已移除：
- ❌ 项目机密信息
- ❌ 密码、Token、密钥
- ❌ 个人隐私信息
- ❌ 公司内部文档

## 📁 目录结构

```
learning-notes/
├── 00-ai/                         # AI 技术（Agent + 机器学习 + 大模型）
│   ├── ai-agent/                  # AI Agent 技术栈（24个分类，100+篇）
│   ├── machine-learning/          # 经典机器学习 + 深度学习原理（8个子目录）
│   └── llm/                       # 大语言模型原理与工程（6个子目录）
│
├── 01-languages/                  # 编程语言
│   ├── python/                    # Python 全栈（16个子目录）
│   ├── java/                      # Java 后端（12个子目录）
│   ├── go/                        # Go 云原生（6个子目录）
│   └── rust/                      # Rust 系统编程
│
├── 02-frontend/                   # 前端技术
│   └── frontend/                  # 前端全栈（16个子目录）
│
├── 03-mobile/                     # 移动开发
│   ├── ios/                       # iOS / Swift / SwiftUI（11个子目录）
│   └── android/                   # Android / Kotlin / Compose（11个子目录）
│
├── 04-backend-infra/              # 后端 & 基础设施
│   ├── architecture/              # 架构设计（事件驱动、微服务、DDD、CQRS）
│   ├── databases/                 # 数据库（PostgreSQL、向量搜索、ClickHouse）
│   ├── data-engineering/          # 数据工程（Airflow、dbt、Iceberg、Flink）
│   ├── observability-sre/         # 可观测性 & SRE（OTel、Prometheus、SLO）
│   ├── platform-engineering/      # 平台工程（GitOps、IaC、CI/CD、FinOps）
│   └── security/                  # 安全（OWASP、零信任、容器安全、Secrets）
│
├── _briefings/                    # 每日技术资讯简报（AI Agent / 国内 / 国际）
│
├── README.md                      # 本文件
├── 00-ai/ai-roadmap.md                  # AI 知识体系审计与学习路线
└── 00-ai/ai-learning-progress.md        # AI 学习进度跟踪
```

详细子目录见各分组内的 README.md：
- [AI 技术](00-ai/04-ai-agent/README.md) | [机器学习](00-ai/01-machine-learning/README.md) | [大模型](00-ai/02-llm/README.md)
- [Python](01-languages/python/README.md) | [Java](01-languages/java/README.md) | [Go](01-languages/go/README.md) | [Rust](01-languages/rust/README.md)
- [前端](02-frontend/frontend/README.md)
- [iOS](03-mobile/ios/README.md) | [Android](03-mobile/android/README.md)
- [数据库](04-backend-infra/databases/README.md) | [可观测性](04-backend-infra/observability-sre/README.md) | [平台工程](04-backend-infra/platform-engineering/README.md) | [安全](04-backend-infra/security/README.md)

## 🎯 内容分类

### 前端技术栈

**00-HTML与CSS基础**
- **HTML5语义化与新特性**：语义化标签、表单新特性、多媒体、Canvas、Web Storage、Web Workers、无障碍访问
- **CSS3核心特性**：选择器、盒模型、BFC、层叠上下文、定位方案、CSS变量、CSS函数、居中方案
- **Flex与Grid布局**：Flex容器与项目属性、Grid网格布局、区域命名、常见布局方案
- **响应式设计与媒体查询**：媒体查询、断点设计、移动优先、响应式单位、容器查询

**01-JavaScript基础**
- **数据类型与变量**：基本类型与引用类型、类型判断、类型转换、var/let/const、深拷贝与浅拷贝
- **函数与作用域**：函数声明与表达式、闭包、this指向、call/apply/bind
- **原型链与继承**：原型对象、原型链、继承方式、ES6 class、instanceof原理
- **异步编程与Promise**：事件循环、Promise、async/await、并发控制
- **ES6+新特性**：解构赋值、Map/Set、Proxy/Reflect、Symbol、Iterator、模块化
- **DOM与BOM操作**：DOM查询与操作、事件模型、Observer API、BOM对象

**02-TypeScript**
- **基础入门**：基础类型、接口、类型别名、联合类型、函数类型、类、类型守卫
- **高级类型**：泛型、条件类型、映射类型、工具类型、模板字面量类型、类型体操
- **工程化实践**：tsconfig配置、声明文件、与React/Vue集成

**03-React**
- **基础与JSX**：JSX语法、组件、Props与State、条件渲染、列表渲染、组件通信
- **Hooks深入**：useState、useEffect、useContext、useReducer、useMemo/useCallback、自定义Hook
- **状态管理**：Context API、Redux Toolkit、Zustand、TanStack Query
- **Router路由**：路由配置、嵌套路由、路由守卫、数据加载
- **性能优化**：React.memo、代码分割、虚拟列表、并发特性

**04-Vue**
- **Vue3基础与组合式API**：模板语法、响应式（ref/reactive/computed/watch）、组件通信、Composables
- **Vue Router与Pinia**：路由配置、导航守卫、Pinia状态管理、持久化
- **Vue3高级特性**：Teleport、Suspense、自定义指令、Transition、KeepAlive、插件开发
- **Vue生态工具库**：Nuxt3、VueUse、Element Plus、Vitest、unplugin自动导入

**05-工程化与构建**
- **Webpack核心概念**：Entry/Output、Loader、Plugin、代码分割、Tree Shaking、HMR
- **Vite现代构建工具**：ESM原生模块、依赖预构建、插件系统、环境变量、SSR
- **包管理器**：npm、yarn、pnpm（硬链接、workspace）
- **代码规范**：ESLint、Prettier、Husky + lint-staged、commitlint
- **Monorepo**：pnpm workspace、Turborepo任务编排与缓存

**06-CSS进阶**
- **CSS预处理器**：Sass（变量、嵌套、混入、模块化）、Less、PostCSS
- **CSS-in-JS与CSS Modules**：CSS Modules、styled-components、方案对比
- **Tailwind CSS**：工具类优先、配置定制、响应式、暗色模式、组件抽象
- **CSS动画与过渡**：transition、animation、GPU加速、FLIP技术、Web Animations API

**07-Node.js**
- **基础与模块系统**：事件循环、CommonJS/ESM、Buffer/Stream、核心模块
- **Express与Koa框架**：路由、中间件、错误处理、NestJS简介
- **数据库操作**：Prisma ORM、Mongoose、ioredis
- **性能优化**：内存泄漏排查、Worker Threads、Stream、PM2

**08-测试**
- **Jest单元测试**：匹配器、Mock函数、异步测试、Vitest
- **组件测试**：React Testing Library、Vue Test Utils、Hook测试
- **E2E测试**：Playwright、Cypress、API拦截
- **测试策略**：测试金字塔、TDD/BDD、Mock策略、MSW

**09-浏览器与网络**
- **浏览器渲染原理**：关键渲染路径、重排与重绘、优化策略、资源加载
- **HTTP协议与缓存**：HTTP/1.1/2/3、HTTPS、强缓存、协商缓存、Service Worker
- **Web安全**：XSS（存储型/反射型/DOM型）、CSRF、CSP、CORS、安全响应头
- **浏览器存储**：Cookie、localStorage/sessionStorage、IndexedDB、Cache API

**10-性能优化**
- **性能指标**：Core Web Vitals（LCP/INP/CLS）、Lighthouse、Performance API
- **加载优化**：代码分割、Tree Shaking、压缩、预加载、SSR/SSG、骨架屏
- **运行时优化**：防抖节流、虚拟列表、Web Worker、内存泄漏排查
- **资源优化**：图片格式（WebP/AVIF）、响应式图片、字体优化、SVG优化

**11-跨平台开发**
- **React Native**：核心组件、样式系统、React Navigation、Expo
- **Electron**：主进程与渲染进程、IPC通信、打包发布
- **微信小程序**：WXML/WXSS、生命周期、Taro/uni-app跨端框架
- **Flutter与Dart**：Dart语法、Widget体系、布局系统、状态管理

**12-可视化与图形**
- **Canvas与SVG**：Canvas 2D API、SVG基础、选型对比
- **ECharts**：图表类型、配置项、React/Vue集成、大数据量优化
- **D3.js**：选择集、数据绑定、比例尺、坐标轴、过渡动画
- **Three.js**：场景/相机/渲染器、几何体与材质、光照、动画、模型加载

**13-微前端与架构**
- **微前端方案**：qiankun、Module Federation、样式隔离、JS沙箱、应用通信
- **前端设计模式**：发布订阅、策略模式、单例模式、组件模式（HOC/Hooks/复合组件）
- **大型项目架构**：目录结构、API层封装、错误处理、权限控制、国际化

**14-DevOps与部署**
- **CI/CD**：GitHub Actions、Docker构建推送、Changesets版本管理
- **Nginx配置**：SPA部署、反向代理、Gzip、HTTPS、安全头
- **Docker容器化**：多阶段构建、Docker Compose、镜像优化
- **CDN**：缓存策略、资源哈希、多环境管理

**15-面试准备**
- **JavaScript面试题**：数据类型、手写题（防抖节流、Promise.all、深拷贝、柯里化等）、闭包、事件循环
- **框架面试题**：React（虚拟DOM、Fiber、Hooks原理）、Vue（响应式原理、Diff算法）
- **综合面试题**：性能优化、浏览器原理、工程化、设计模式、算法题

### Java 技术栈

**00-Java基础**
- **Java语言特性**：Java新特性8-17（Lambda、Stream API等）
- **JVM**：JVM内存模型、垃圾回收算法、垃圾收集器、JVM调优
- **并发编程**：线程基础、线程同步、线程池、并发集合、原子类、CAS、锁机制
- **集合框架**：List、Set、Map、Queue等集合类的使用和原理
- **反射与注解**：反射机制、Class类、注解定义和使用
- **异常处理**：异常分类、try-catch-finally、自定义异常
- **泛型**：泛型类、泛型方法、类型通配符、类型擦除
- **枚举**：枚举定义、枚举方法、EnumSet、EnumMap
- **IO与NIO**：字节流、字符流、对象流、NIO Buffer、Channel、Selector
- **字符串**：String不可变性、字符串常量池、StringBuilder、StringBuffer
- **包装类**：包装类使用、自动装箱拆箱、缓存机制
- **内部类**：成员内部类、静态内部类、局部内部类、匿名内部类
- **正则表达式**：Pattern、Matcher、正则语法

**01-框架**
- **Spring 系列**：Spring 基础（IOC、DI、AOP）、Spring Boot、SpringMVC、Spring 高级特性
- **Spring Cloud**：微服务架构、服务发现、配置中心、网关等
- **微服务高级**：微服务保护（Sentinel）、分布式事务（Seata）
- **MyBatis Plus**：MyBatis 增强工具，简化开发
- **最佳实践**：统一异常处理、响应格式、全链路追踪、微服务架构模式

**02-中间件**
- **消息队列**：RabbitMQ（基础、高级篇）、Kafka 事件驱动架构
- **搜索引擎**：Elasticsearch（基础、进阶、高级）
- **Web 服务器**：Nginx（简介、常用配置）
- **缓存**：Caffeine 本地缓存、Redis 分布式缓存、多级缓存架构

**03-容器化**
- **Docker**：容器化部署、镜像构建、Docker Compose
- **Kubernetes**：容器编排、Pod、Service、Deployment 等核心概念（5天完整教程）

**04-设计模式**
- **设计模式**：23 种设计模式详解（创建型、结构型、行为型）

**05-网络编程**
- **Netty**：NIO 基础、入门、进阶、优化与源码分析
- **gRPC**：高性能 RPC 框架、Protobuf、HTTP/2

**06-构建工具**
- **Maven**：Maven 基础、Maven 高级（分模块、聚合、继承、私服）
- **Gradle**：Gradle 构建工具基础

**07-数据库**
- **MySQL**：MySQL 基础、MySQL 中级、MySQL 高级（索引、优化、锁等）

**08-部署与运维**
- **服务注册**：Nacos安装、集群搭建
- **消息队列**：RabbitMQ部署（单机、集群）
- **搜索引擎**：Elasticsearch安装
- **容器化**：Docker安装
- **微服务组件**：Sentinel规则持久化、Seata部署
- **缓存**：Redis集群、Canal、OpenResty

**09-源码分析**
- **Nacos源码分析**：服务注册发现、配置管理源码
- **Sentinel源码分析**：限流、熔断、降级源码

**10-工具与测试**
- **Jmeter**：性能测试工具快速入门

**11-面试准备**
- **微服务面试题**：Spring Cloud、Nacos、Sentinel等常见面试题

### Python 技术栈

**00-Python基础**
- **Python语言特性**：变量与数据类型、运算符、分支结构、循环结构
- **数据结构**：列表、元组、字典、集合、字符串的操作和方法
- **函数与面向对象**：函数定义、Lambda、装饰器、类与对象、继承与多态
- **高级特性**：异常处理、文件操作、正则表达式、生成器、迭代器、上下文管理器

**01-Web开发**
- **FastAPI**：现代 Web 框架、API 开发、异步支持
- **Django**：全栈 Web 框架、模型、视图、模板
- **Flask**：轻量级 Web 框架、路由、蓝图

**02-数据分析**
- **数据分析概述**：数据分析流程、工具库介绍
- **NumPy**：数组操作、数学运算、科学计算
- **Pandas**：DataFrame 操作、数据清洗、数据分析
- **数据可视化**：Matplotlib、Seaborn 等可视化库

**03-机器学习**
- **浅谈机器学习**：机器学习概述、算法分类、模型训练
- **RAG检索增强生成**：RAG 实现、向量化、检索策略

**04-并发编程**
- **Python并发编程**：多线程、多进程、异步编程（asyncio）

**05-网络编程**
- **Python网络编程**：Socket 编程、HTTP 客户端、WebSocket

**06-爬虫**
- **Python爬虫**：requests、BeautifulSoup、Scrapy、Selenium

**07-数据库操作**
- **Python数据库操作**：SQLAlchemy ORM、MongoDB、Redis

**08-测试**
- **Python测试**：unittest、pytest、Mock、测试覆盖率

**09-工具与规范**
- **Python工具与规范**：虚拟环境、包管理、代码规范（PEP 8）、类型检查

**10-设计模式**
- **Python设计模式**：创建型、结构型、行为型设计模式

**11-部署与运维**
- **Python部署与运维**：Gunicorn/uWSGI 部署、Nginx 配置、Docker 部署

**12-性能优化**
- **Python性能优化**：算法优化、代码优化、内存优化、性能分析

**13-安全编程**
- **Python安全编程**：输入验证、认证授权、数据加密、安全配置

**14-算法与数据结构**
- **Python算法与数据结构**：数据结构实现、排序算法、搜索算法、动态规划

**15-消息队列**
- **Python消息队列**：RabbitMQ、Kafka、Redis 队列、Celery

### 架构设计

- **事件驱动架构**：EDA 模式、Kafka/RabbitMQ/Redis Streams/Pulsar 对比
- **微服务架构模式**：服务拆分、通信、服务发现、断路器、Saga
- **DDD领域驱动设计**：聚合根、领域事件、限界上下文、战略/战术设计
- **CQRS与事件溯源**：命令查询分离、事件存储、最终一致性
- **系统设计核心概念**：CAP 定理、缓存策略、限流、分库分表

### 机器学习与深度学习原理

> 详细索引 → [machine-learning/README.md](00-ai/01-machine-learning/README.md)

- **机器学习基础**：学习范式、经验风险与结构风险、泛化误差、归纳偏置、数据泄露、交叉验证
- **经典算法**：线性/逻辑回归推导、决策树、集成学习（RF/GBDT/XGBoost/LightGBM）、SVM 与核方法、朴素贝叶斯、聚类、降维
- **特征工程**：缺失值、类别编码与泄露、数值变换、特征交叉、特征选择、特征漂移
- **神经网络原理**：感知机与 MLP、反向传播推导、梯度下降与优化器（含 Adam/AdamW 差异）、激活函数、损失函数
- **训练工程**：过拟合与偏差方差（含双下降）、正则化、归一化（BN/LN/RMSNorm、Pre-LN vs Post-LN）、学习率调度与混合精度
- **CNN与视觉**：卷积原理、经典网络演进（ResNet 残差机制）、ViT 与视觉 Transformer
- **RNN与序列**：RNN/LSTM/GRU、BPTT 梯度问题、seq2seq 与注意力起源
- **强化学习基础**：MDP 与价值函数、策略梯度与 PPO（为读懂 RLHF 服务）

### 大模型原理与工程

> 详细索引 → [llm/README.md](00-ai/02-llm/README.md)

- **Transformer原理**：注意力机制推导（含 sqrt(d_k) 方差分析）、位置编码（正弦式/RoPE/ALiBi）、架构组件与训练稳定性
- **分词与表示**：BPE/WordPiece/Unigram/SentencePiece、词向量演进（word2vec/GloVe/FastText）
- **预训练范式**：BERT 与自编码路线、GPT 与自回归路线、MoE 混合专家
- **微调与对齐**：三阶段范式与数据构造、PEFT（LoRA/QLoRA/Adapter）、RLHF 全链路、DPO 与免 RL 对齐
- **推理优化**：KV Cache 与显存分析、量化（GPTQ/AWQ/离群值问题）、蒸馏与剪枝、投机解码与推理引擎
- **多模态**：CLIP 与对比学习、扩散模型原理、VLM 架构、语音与视频模型

## 📖 如何使用

1. **按需阅读**：根据技术栈选择相关内容
2. **实践应用**：结合项目实践应用所学
3. **持续更新**：根据学习进度更新内容

> **AI 方向学习路线**：应用层（`ai-agent/`）与原理层（`machine-learning/`、`llm/`）分工与推荐阅读顺序，
> 详见 → [AI 知识体系审计与学习路线](00-ai/ai-roadmap.md)

## 🔄 更新说明

这些笔记会持续更新，添加新的学习内容和实践经验。

## 📝 注意事项

- 这些是个人学习笔记，仅供参考
- 部分内容可能不够深入，建议结合官方文档学习
- 代码示例仅作参考，实际使用时需要根据场景调整

---

**提示**：如果想查看原始学习笔记（包含更多内容），请查看 `private-notes` 文件夹（本地，不上传到 GitHub）。
