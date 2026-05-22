# Kotlin 语言面试题
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. val vs var

```kotlin
// val：只读引用（类似 Java final），引用不可变但对象内容可变
val list = mutableListOf(1, 2, 3)
list.add(4)        // ✅ 对象内容可变
// list = listOf()  // ❌ 引用不可变

// var：可变引用
var name = "张三"
name = "李四"  // ✅

// const val：编译时常量（仅基本类型和 String）
companion object {
    const val MAX_COUNT = 100  // 编译时内联
    val PATTERN = Regex("\\d+")  // 运行时初始化
}
```

## 2. data class

```kotlin
// 自动生成: equals(), hashCode(), toString(), copy(), componentN()
data class User(val name: String, val age: Int)

val u1 = User("张三", 25)
val u2 = u1.copy(age = 26)           // 浅拷贝
val (name, age) = u1                  // 解构
println(u1 == u2)                     // false（结构相等）
println(u1 === u2)                    // false（引用不等）

// 注意：只有主构造函数中的属性参与 equals/hashCode
data class Item(val id: Int, val name: String) {
    var description: String = ""  // 不参与 equals/hashCode
}
```

## 3. sealed class vs enum

```kotlin
// sealed class：限制继承，子类可以有不同属性
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String, val code: Int) : Result<Nothing>()
    data object Loading : Result<Nothing>()
}

// enum：固定实例，所有实例结构相同
enum class Direction { NORTH, SOUTH, EAST, WEST }

// sealed interface（Kotlin 1.5+）
sealed interface UiEvent {
    data class ShowSnackbar(val msg: String) : UiEvent
    data object NavigateBack : UiEvent
}

// when 表达式编译器检查完整性
fun handle(result: Result<String>) = when (result) {
    is Result.Success -> result.data
    is Result.Error -> result.message
    is Result.Loading -> "加载中"
    // 不需要 else，编译器知道所有子类
}
```

## 4. 协程 vs 线程

```kotlin
// 线程：OS 级别，创建开销大（~1MB 栈），数量有限
// 协程：用户级别，轻量（~几KB），可创建数十万个

// 线程切换由 OS 调度，协程切换由程序控制
// 协程可以挂起而不阻塞线程

suspend fun fetchData(): String {
    return withContext(Dispatchers.IO) {
        // 挂起当前协程，释放线程给其他协程使用
        api.getData()
    }
}

// 结构化并发：父协程取消时子协程自动取消
viewModelScope.launch {
    val a = async { fetchA() }
    val b = async { fetchB() }
    // viewModelScope 取消时，a 和 b 自动取消
    process(a.await(), b.await())
}
```

## 5. Flow vs LiveData

```kotlin
// LiveData：
// - 生命周期感知，自动取消订阅
// - 只在主线程观察
// - 无操作符链
// - 适合简单 UI 状态

// Flow：
// - 协程原生，丰富操作符
// - 可在任意线程
// - 冷流（collect 时才执行）
// - 适合复杂数据流

// StateFlow 替代 LiveData
class ViewModel : ViewModel() {
    // LiveData 方式
    private val _data = MutableLiveData<String>()
    val data: LiveData<String> = _data

    // StateFlow 方式（推荐）
    private val _state = MutableStateFlow("")
    val state: StateFlow<String> = _state.asStateFlow()
}

// 收集 Flow 需要生命周期感知
viewLifecycleOwner.lifecycleScope.launch {
    repeatOnLifecycle(Lifecycle.State.STARTED) {
        viewModel.state.collect { updateUI(it) }
    }
}

// Compose 中直接使用
val state by viewModel.state.collectAsStateWithLifecycle()
```

## 6. 扩展函数 vs 继承

```kotlin
// 扩展函数：不修改原类，编译时静态解析
fun String.isValidEmail(): Boolean = Regex("^[\\w.-]+@[\\w.-]+\\.\\w+$").matches(this)
"test@example.com".isValidEmail()  // true

// 注意：扩展函数是静态分发，不支持多态
open class Base
class Derived : Base()

fun Base.greet() = "Base"
fun Derived.greet() = "Derived"

val obj: Base = Derived()
println(obj.greet())  // "Base"（静态类型决定）

// 继承：运行时多态
open class Base { open fun greet() = "Base" }
class Derived : Base() { override fun greet() = "Derived" }
val obj: Base = Derived()
println(obj.greet())  // "Derived"（动态分发）
```

## 7. 内联函数

```kotlin
// inline：函数体在调用处展开，避免 lambda 对象创建
inline fun <T> measureTime(block: () -> T): Pair<T, Long> {
    val start = System.nanoTime()
    val result = block()
    return result to (System.nanoTime() - start)
}

// reified：内联函数中获取泛型类型
inline fun <reified T> Gson.fromJson(json: String): T =
    fromJson(json, T::class.java)

// 使用
val user = gson.fromJson<User>(jsonStr)  // 无需传 Class
```

> 🔄 更新于 2026-05-02

<!-- version-check: Kotlin 2.3.20, Compose 1.11, Android 16 API 36, checked 2026-05-02 -->

## 8. 2026 年面试新增热点

### 8.1 Kotlin 2.x 新特性面试题

```kotlin
// Q: K2 编译器是什么？有什么影响？
// A: K2 是 Kotlin 2.0 引入的全新编译器前端，Kotlin 2.3.20 默认启用。
// 编译速度显著提升，类型推断更准确，IDE 分析更快。
// 对开发者代码无 Breaking Change，但 Gradle 插件需要 2.0+ 版本。

// Q: when 表达式的守卫条件（Guard Conditions）是什么？
// A: Kotlin 2.1+ 新增，允许在 when 分支中添加额外的布尔条件
fun classify(value: Any) = when (value) {
    is Int if value > 0 -> "正整数"
    is Int -> "非正整数"
    is String if value.isNotEmpty() -> "非空字符串"
    else -> "其他"
}

// Q: name-based 解构声明是什么？
// A: Kotlin 2.3.20 新增，解构声明不再依赖位置顺序，而是按名称匹配
data class User(val name: String, val age: Int, val email: String)
// 传统方式（位置依赖）
val (name, age, email) = user
// name-based（Kotlin 2.3.20+，按名称匹配，顺序无关）
val (email, name) = user  // 只取需要的字段

// Q: 显式 backing fields 是什么？
// A: Kotlin 2.0+ 新增，允许属性的 backing field 有不同的类型
class Counter {
    val count: Int
        field = 0  // backing field 显式声明
        get() = field
    
    fun increment() { field++ }
}
```

### 8.2 Compose 2026 面试题

```kotlin
// Q: Strong Skipping Mode 是什么？
// A: Compose 编译器优化，默认启用（Compose 1.10+）。
// 即使参数不稳定（unstable），只要值没变就跳过重组。
// 减少了手动标注 @Stable/@Immutable 的需求。

// Q: collectAsStateWithLifecycle 和 collectAsState 的区别？
// A: collectAsStateWithLifecycle 是生命周期感知的：
// - App 进入后台时自动停止收集 → 节省资源
// - App 回到前台时自动恢复收集
// - 2026 年是标准推荐，替代 collectAsState
val state by viewModel.uiState.collectAsStateWithLifecycle()

// Q: Compose 1.11（2026-04）有什么新特性？
// A: 核心变化：
// 1. 测试 API v2 成为默认（StandardTestDispatcher 替代 UnconfinedTestDispatcher）
// 2. SharedElement 调试工具（LookaheadAnimationVisualDebugging）
// 3. Trackpad 事件改进（PointerType.Mouse 替代 PointerType.Touch）
// 4. Material3 1.5 稳定版

// Q: Navigation 3 和 Navigation Compose 2.x 的区别？
// A: Navigation 3 是全新 Compose-first 设计（1.1.1 稳定版）：
// - 开发者完全控制 back stack（不再是框架管理）
// - 使用 @Serializable 数据类定义路由（类型安全）
// - 支持 Compose Multiplatform
// Navigation 2.x 仍然维护（2.9.8），但新项目推荐 Navigation 3

// Q: Vkompose 是什么？为什么重要？
// A: VK.com 开源的 Compose 性能工具套件，包含：
// - IntelliJ 插件：高亮不稳定参数
// - Gradle 插件：编译时检测重组问题
// - Detekt 规则：阻止性能问题进入代码库
// 2026 年 Compose 性能优化的最佳实践工具
```

### 8.3 Android 16 面试题

```kotlin
// Q: Android 16 的 Minor SDK Version 是什么？
// A: Android 16 QPR2 首次引入 Minor SDK Version 机制：
// - 允许在年度大版本之外发布新 API
// - Minor 版本只包含增量 API，不引入 targetSdkVersion 行为变更
// - 减少开发者回归测试负担
// 检查方式：Build.VERSION.SDK_INT_MINOR

// Q: Android 16 对 App 方向和宽高比有什么变化？
// A: Android 16（API 36）强制所有 App 支持自适应布局：
// - 系统可覆盖 App 的屏幕方向、宽高比、可调整大小限制
// - 折叠屏和大屏设备上，App 不能再锁定竖屏
// - 开发者需要测试多窗口和不同屏幕尺寸

// Q: AGP 9.0 有什么重大变化？
// A: Android Gradle Plugin 9.0（2026-01）：
// - 要求 Gradle 9+、Kotlin 2.0+
// - Compose Compiler 不再需要单独配置（内置于 Kotlin 编译器）
// - compileSdk/targetSdk 推荐 36
// - JDK 要求从 17 升级到 21
```

### 8.4 KotlinConf 2026 与 Kotlin 2.4 面试题

<!-- version-check: Kotlin 2.4.0-RC (KotlinConf 2026, May 20-22 Munich), context parameters stable, explicit backing fields stable, Kotlin VS Code support, checked 2026-05-22 -->

> 🔄 更新于 2026-05-22

```kotlin
// Q: Kotlin 2.4 的 stable 时间线是什么？
// A: KotlinConf 2026（5-20 至 5-22，慕尼黑）发布 Kotlin 2.4.0-RC：
// - GA 时间窗：2026 年 6-7 月
// - Tooling release 2.4.20：2026-09
// - 同时发布 18 个月安全补丁政策（标准库进入 LTS 模式）
// - 来源：https://blog.jetbrains.com/kotlin/2026/05/kotlinconf26-keynote-highlights/

// Q: Kotlin 2.4 中 context parameters 稳定意味着什么？
// A: context parameters（曾叫 context receivers）从实验阶段升级为稳定特性：
// - 解决"隐式上下文"传递问题，比 receiver 更轻量
// - 适合 Logger、Transaction、CoroutineScope 等横切关注点

// 旧方式（每个函数都要传 logger）：
fun process(input: String, logger: Logger) {
    logger.info("processing $input")
}

// Kotlin 2.4 stable 写法：
context(logger: Logger)
fun process(input: String) {
    logger.info("processing $input")  // 直接访问 context 中的 logger
}

// 调用方
context(myLogger) {
    process("hello")
}

// Q: Kotlin 2.4 的 explicit backing fields 怎么用？
// A: 解决"对外只读、对内可变"场景，无需手动写 _state / state pair
class ViewModel {
    val items: List<String>
        field = mutableListOf<String>()  // 内部可变
    
    fun addItem(item: String) {
        items.field.add(item)  // 通过 field 访问可变版本
    }
}
// 替代了之前 _items + items 双属性的写法

// Q: KMP 默认项目结构变化是什么？
// A: 配合 AGP 9.0，KMP 默认项目结构调整：
// - shared/src/commonMain/kotlin/ 中存放跨平台代码
// - shared/src/androidMain/、iosMain/、jsMain/ 中存放平台特定代码
// - 模块职责更清晰，与其他构建系统约定对齐
// - 新建项目自动遵循新结构
// - 来源：https://blog.jetbrains.com/kotlin/2026/05/new-kmp-default-structure/

// Q: Kotlin VS Code 官方支持是什么？
// A: KotlinConf 2026 期间，JetBrains 发布 VS Code 官方 Kotlin 扩展（Alpha）：
// - 核心编辑器支持：补全、诊断、导航、quick fix、格式化、项目导入
// - LSP 协议实现，理论上其他支持 LSP 的编辑器（Neovim、Helix）也可用
// - 不替代 IntelliJ IDEA，定位是"轻量编辑场景"
// - 来源：https://blog.jetbrains.com/kotlin/2026/05/official-kotlin-support-for-visual-studio-code-is-now-available-in-alpha/

// Q: 为什么 Kotlin 标准库要引入 18 个月安全支持政策？
// A: 标准库面临的供应链安全压力越来越大：
// - 安全补丁会向旧 release line 回溯（active release lines）
// - 18 个月覆盖企业项目的常见升级周期
// - 配合 deprecation cycle，让升级路径更稳
// - 来源：https://blog.jetbrains.com/kotlin/2026/05/security-support-policy-for-the-kotlin-standard-library/
```

### 8.5 Compose Multiplatform 1.11 与 Hilt 1.4 面试题

<!-- version-check: Compose Multiplatform 1.11.0 (2026-05), Hilt 1.4.0-beta01 (2026-04-22), checked 2026-05-22 -->

```kotlin
// Q: Compose Multiplatform 1.11 在 iOS 端有什么关键改进？
// A: 实验性的 native text input（基于 UIView）：
// - caret 移动更精准（接近原生 UIKit 体验）
// - 原生手势 + selection handles
// - 系统右键菜单：Autofill、Translate、Search
// - 现有 Compose 文本输入仍然是稳定跨平台默认，新方案是 opt-in
// - 解决 KMP 在 iOS 上"手感不够原生"的长期痛点
// - 来源：https://blog.jetbrains.com/kotlin/2026/05/compose-multiplatform-1-11-0/

// Q: Hilt 1.4.0-beta01（2026-04-22）的 rememberHiltViewModelFactory 怎么用？
// A: 简化了 Compose 中 Hilt ViewModel 的获取流程：
// - 移除 ViewModelStoreOwner 参数，API 更简洁
// - 通过 delegateFactory 提供自定义工厂逻辑
// - 适合 rememberViewModelStoreOwner 提供默认工厂的场景

@Composable
fun MyScreen() {
    val viewModel: MyViewModel = viewModel(
        factory = rememberHiltViewModelFactory()
    )
    // ...
}

// Q: 2026 年 Android 项目应该选 Hilt 还是 Koin？
// A: 决策树：
// - 纯 Android 项目 + 团队偏好编译时安全 → Hilt 1.4.0
// - KMP 项目（Android + iOS 共享 DI） → Koin 4.1（Hilt 不支持 KMP）
// - 已有 Now in Android 模板 → Hilt（官方模板沿用）
// - 偏好运行时灵活性、热重载快 → Koin
// 来源：https://insert-koin.io/docs/reference/koin-android/hilt-migration
```
