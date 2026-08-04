# Android 技术学习笔记
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> 本目录包含 Android 技术栈的学习笔记，按类别组织

## 📁 目录结构

```
android/
├── 00-Kotlin基础/              # Kotlin 语言基础
│   ├── Kotlin语法基础.md
│   ├── Kotlin面向对象编程.md
│   ├── Kotlin函数式编程.md
│   ├── Kotlin协程与异步.md
│   └── Kotlin与Java互操作.md
│
├── 01-Jetpack Compose/         # Compose 声明式UI
│   ├── Compose基础与布局.md
│   ├── Compose状态管理.md
│   ├── Compose导航与路由.md
│   └── Compose动画与手势.md
│
├── 02-传统View体系/             # XML布局与View
│   ├── View与ViewGroup基础.md
│   ├── RecyclerView深入.md
│   ├── ConstraintLayout布局.md
│   └── 自定义View与绘制.md
│
├── 03-Jetpack组件/              # Android Jetpack
│   ├── ViewModel与LiveData.md
│   ├── Room数据库.md
│   ├── Navigation组件.md
│   ├── WorkManager后台任务.md
│   └── DataStore数据存储.md
│
├── 04-网络编程/                  # 网络请求
│   ├── Retrofit与OkHttp.md
│   ├── Kotlin序列化与JSON.md
│   ├── WebSocket与gRPC.md
│   └── 网络缓存与离线策略.md
│
├── 05-架构模式/                  # 架构设计
│   ├── MVVM与MVI架构.md
│   ├── Clean Architecture实践.md
│   ├── 依赖注入Hilt-Koin.md
│   └── 模块化与组件化.md
│
├── 06-系统能力/                  # Android 系统
│   ├── Activity与Fragment生命周期.md
│   ├── Service与广播接收器.md
│   ├── ContentProvider与权限.md
│   ├── 通知与前台服务.md
│   └── 多媒体与相机.md
│
├── 07-性能优化/                  # 性能调优
│   ├── 内存优化与LeakCanary.md
│   ├── 启动优化与ANR分析.md
│   ├── 布局优化与渲染性能.md
│   └── 包体积与电量优化.md
│
├── 08-工程化/                    # 工程化实践
│   ├── Gradle构建系统.md
│   ├── 多渠道打包与签名.md
│   ├── 单元测试与UI测试.md
│   └── CI-CD与自动化发布.md
│
├── 09-跨平台/                    # 跨平台方案
│   ├── Flutter Android集成.md
│   ├── KMM跨平台开发.md
│   └── Compose与View混合开发.md
│
├── 10-面试准备/                  # 面试题整理
│   ├── Kotlin语言面试题.md
│   ├── Android系统与组件面试题.md
│   └── 架构与性能面试题.md
│
└── README.md                    # 本文件
```

## 📚 内容说明

### Kotlin 基础

- **Kotlin语法基础**：变量（val/var）、基本类型、空安全（?/?./!!/?:）、控制流（when/if/for）、集合操作（List/Map/Set）、字符串模板、区间（Range）、解构声明
- **Kotlin面向对象编程**：类与对象、数据类（data class）、密封类（sealed class）、枚举类、伴生对象（companion object）、继承与接口、属性委托（by lazy/observable）、扩展函数与属性
- **Kotlin函数式编程**：高阶函数、Lambda表达式、内联函数（inline/noinline/crossinline）、作用域函数（let/run/with/apply/also）、序列（Sequence）、集合操作符（map/filter/flatMap/groupBy/fold）
- **Kotlin协程与异步**：协程基础（launch/async/runBlocking）、CoroutineScope与CoroutineContext、Dispatcher（Main/IO/Default）、Flow（冷流/热流/StateFlow/SharedFlow）、Channel、异常处理、结构化并发
- **Kotlin与Java互操作**：Java调用Kotlin（@JvmStatic/@JvmField/@JvmOverloads）、Kotlin调用Java、SAM转换、平台类型、注解互操作

### Jetpack Compose

- **Compose基础与布局**：@Composable函数、Text/Image/Button/Icon基础组件、Column/Row/Box布局、LazyColumn/LazyRow列表、Modifier修饰符链、Scaffold脚手架、Material3组件
- **Compose状态管理**：remember/mutableStateOf、rememberSaveable、State hoisting、derivedStateOf、snapshotFlow、collectAsState、Side Effects（LaunchedEffect/DisposableEffect/SideEffect）
- **Compose导航与路由**：Navigation Compose、NavHost/NavController、参数传递、深度链接、嵌套导航、底部导航栏、类型安全路由（Kotlin Serialization）
- **Compose动画与手势**：animateXxxAsState、AnimatedVisibility、AnimatedContent、Crossfade、updateTransition、InfiniteTransition、手势检测（detectTapGestures/detectDragGestures）、Swipeable

### 传统 View 体系

- **View与ViewGroup基础**：View绘制流程（measure/layout/draw）、事件分发机制（dispatchTouchEvent/onInterceptTouchEvent/onTouchEvent）、常用布局（LinearLayout/FrameLayout/RelativeLayout）
- **RecyclerView深入**：Adapter与ViewHolder、LayoutManager（Linear/Grid/StaggeredGrid）、ItemDecoration、ItemAnimator、DiffUtil、ConcatAdapter、Paging3分页加载
- **ConstraintLayout布局**：约束关系、Chain链、Guideline辅助线、Barrier屏障、Group分组、MotionLayout动画
- **自定义View与绘制**：Canvas绑制（drawRect/drawCircle/drawPath/drawText）、Paint画笔、Path路径、自定义属性（attrs.xml）、onMeasure/onLayout/onDraw、硬件加速

### Jetpack 组件

- **ViewModel与LiveData**：ViewModel生命周期、SavedStateHandle、LiveData观察者模式、MutableLiveData、Transformations（map/switchMap）、MediatorLiveData、StateFlow替代方案
- **Room数据库**：@Entity/@Dao/@Database注解、CRUD操作、关系映射（@Relation）、类型转换器、数据库迁移、Flow/LiveData查询、预填充数据
- **Navigation组件**：NavGraph导航图、Safe Args参数传递、Deep Link、嵌套导航、条件导航、NavigationUI与Toolbar/BottomNav集成
- **WorkManager后台任务**：OneTimeWorkRequest/PeriodicWorkRequest、约束条件（网络/电量/存储）、链式任务、输入输出数据、任务观察、加急任务
- **DataStore数据存储**：Preferences DataStore（键值对）、Proto DataStore（类型安全）、数据迁移（SharedPreferences → DataStore）、Flow集成

### 网络编程

- **Retrofit与OkHttp**：Retrofit接口定义、注解（@GET/@POST/@Path/@Query/@Body）、Converter（Gson/Moshi/Kotlin Serialization）、OkHttp拦截器（日志/认证/缓存）、连接池、超时配置
- **Kotlin序列化与JSON**：kotlinx.serialization（@Serializable、Json配置）、Gson、Moshi（@JsonClass、自定义Adapter）、Codegen vs Reflection
- **WebSocket与gRPC**：OkHttp WebSocket、Scarlet库、gRPC-Kotlin（Protobuf定义、Stub生成、流式通信）
- **网络缓存与离线策略**：OkHttp缓存、Room离线缓存、NetworkBoundResource模式、离线优先策略、数据同步

### 架构模式

- **MVVM与MVI架构**：MVVM（ViewModel + LiveData/StateFlow + Repository）、MVI（单向数据流、Intent → Model → View）、UiState模式、事件处理（SingleEvent/Channel）
- **Clean Architecture实践**：分层（Presentation/Domain/Data）、Use Case、Repository接口与实现、实体映射、依赖规则
- **依赖注入Hilt-Koin**：Hilt（@HiltAndroidApp/@AndroidEntryPoint/@Inject/@Module/@Provides/@Singleton）、Koin（module/single/factory/viewModel）、作用域管理
- **模块化与组件化**：feature模块拆分、api/impl分离、模块间通信（Navigation/接口暴露）、动态Feature Module、Gradle Convention Plugins

### 系统能力

- **Activity与Fragment生命周期**：Activity生命周期（onCreate→onStart→onResume→onPause→onStop→onDestroy）、Fragment生命周期、配置变更处理、进程死亡恢复、Result API
- **Service与广播接收器**：Started Service/Bound Service、前台服务、JobIntentService、BroadcastReceiver（静态/动态注册）、LocalBroadcastManager
- **ContentProvider与权限**：ContentProvider数据共享、ContentResolver查询、运行时权限请求、权限最佳实践、FileProvider文件共享
- **通知与前台服务**：NotificationChannel、NotificationCompat.Builder、通知样式（BigText/BigPicture/Inbox/Messaging）、前台服务通知、通知权限（Android 13+）
- **多媒体与相机**：CameraX（Preview/ImageCapture/VideoCapture/ImageAnalysis）、MediaPlayer/ExoPlayer、图片加载（Coil/Glide）、图片选择器（Photo Picker）

### 性能优化

- **内存优化与LeakCanary**：内存泄漏常见场景（静态引用/Handler/匿名内部类/单例）、LeakCanary集成与分析、Profiler内存分析、Bitmap优化、大对象管理
- **启动优化与ANR分析**：冷启动/温启动/热启动、App Startup库、启动任务编排、Baseline Profiles、ANR原因分析（主线程阻塞/死锁/广播超时）、StrictMode
- **布局优化与渲染性能**：布局层级优化（merge/include/ViewStub）、过度绘制检测、GPU渲染分析、Compose重组优化（Stability/Skippable）、Layout Inspector
- **包体积与电量优化**：ProGuard/R8代码混淆与压缩、资源压缩、App Bundle、动态Feature、电量优化（Doze模式/App Standby/Battery Historian）

### 工程化

- **Gradle构建系统**：build.gradle.kts配置、依赖管理（Version Catalog）、Build Variants（productFlavors/buildTypes）、自定义Task、Gradle Plugin、构建缓存与加速
- **多渠道打包与签名**：签名配置（keystore）、多渠道打包方案（productFlavors/Walle）、V1/V2/V3签名、App Bundle与APK
- **单元测试与UI测试**：JUnit5、MockK/Mockito、Turbine（Flow测试）、Robolectric、Espresso UI测试、Compose Testing（ComposeTestRule）、截图测试
- **CI-CD与自动化发布**：GitHub Actions Android构建、Fastlane（supply/screengrab）、Firebase App Distribution、Google Play Console API、版本管理

### 跨平台

- **Flutter Android集成**：Flutter Module嵌入、MethodChannel/EventChannel通信、混合导航、PlatformView
- **KMM跨平台开发**：Kotlin Multiplatform Mobile、共享业务逻辑、expect/actual机制、Ktor网络请求、SQLDelight数据库
- **Compose与View混合开发**：ComposeView嵌入XML、AndroidView嵌入Compose、渐进式迁移策略、互操作最佳实践

### 面试准备

- **Kotlin语言面试题**：val vs var、data class原理、sealed class用途、协程vs线程、Flow vs LiveData、内联函数原理、委托属性
- **Android系统与组件面试题**：Activity启动模式、Fragment通信方式、Handler消息机制、Binder IPC原理、View绘制流程、事件分发机制、进程保活
- **架构与性能面试题**：MVVM vs MVI、Hilt vs Koin、内存泄漏排查、启动优化方案、Compose重组原理、RecyclerView缓存机制

## 🎯 学习路径建议

### 基础阶段
1. **Kotlin语言**：语法基础 → 面向对象 → 函数式编程 → 协程
2. **Jetpack Compose**：基础组件 → 布局 → 状态管理 → 导航 → 动画
3. **传统View体系**（了解）：View基础 → RecyclerView → ConstraintLayout

### 进阶阶段
4. **Jetpack组件**：ViewModel → Room → Navigation → WorkManager → DataStore
5. **网络编程**：Retrofit/OkHttp → JSON序列化 → 缓存策略
6. **架构模式**：MVVM/MVI → Clean Architecture → 依赖注入

### 高级阶段
7. **系统能力**：四大组件 → 通知 → 多媒体 → 权限
8. **性能优化**：内存优化 → 启动优化 → 布局优化 → 包体积优化
9. **工程化**：Gradle → 测试 → CI/CD → 自动化发布
10. **面试准备**：Kotlin面试题 → Android系统面试题 → 架构面试题

## 📖 使用说明

- 所有笔记从个人学习过程中整理，已移除敏感信息
- 包含代码示例和最佳实践
- 适合系统学习和面试准备

## 🔗 相关资源

- [Android Developer 官方文档](https://developer.android.com/)
- [Kotlin 官方文档](https://kotlinlang.org/docs/home.html)
- [Jetpack Compose 文档](https://developer.android.com/jetpack/compose)
- [Android Architecture Guide](https://developer.android.com/topic/architecture)
