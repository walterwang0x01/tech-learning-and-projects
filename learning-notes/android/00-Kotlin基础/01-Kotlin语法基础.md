# Kotlin 语法基础
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 变量与类型

```kotlin
val constant = 10       // 不可变（推荐）
var variable = 20       // 可变

// 类型声明
val name: String = "张三"
val age: Int = 25
val height: Double = 1.75
val isActive: Boolean = true

// 类型推断
val message = "Hello"   // 自动推断为 String
val count = 42          // 自动推断为 Int

// 字符串模板
val greeting = "Hello, $name"
val info = "Name: ${user.name}, Age: ${user.age}"

// 多行字符串
val json = """
    {
        "name": "$name",
        "age": $age
    }
""".trimIndent()
```

## 2. 空安全

```kotlin
var nickname: String? = null  // 可空类型

// 安全调用
val length = nickname?.length  // Int?

// Elvis 运算符
val displayName = nickname ?: "匿名"

// 安全调用链
val city = user?.address?.city ?: "未知"

// let 作用域函数
nickname?.let { name ->
    println("昵称: $name")
}

// 非空断言（谨慎使用）
val forcedName = nickname!!  // 如果为 null 抛出 NPE

// 安全类型转换
val str = value as? String  // 失败返回 null
```

## 3. 集合

```kotlin
// 不可变集合
val fruits = listOf("苹果", "香蕉", "橙子")
val scores = mapOf("张三" to 90, "李四" to 85)
val tags = setOf("Kotlin", "Android")

// 可变集合
val mutableFruits = mutableListOf("苹果", "香蕉")
mutableFruits.add("橙子")
mutableFruits.removeAt(0)

val mutableScores = mutableMapOf("张三" to 90)
mutableScores["李四"] = 85

// 集合操作
val numbers = listOf(1, 2, 3, 4, 5)
val doubled = numbers.map { it * 2 }              // [2, 4, 6, 8, 10]
val evens = numbers.filter { it % 2 == 0 }        // [2, 4]
val sum = numbers.reduce { acc, n -> acc + n }     // 15
val total = numbers.fold(0) { acc, n -> acc + n }  // 15
val names = users.mapNotNull { it.name }           // 过滤 null
val allTags = users.flatMap { it.tags }            // 展平
val grouped = users.groupBy { it.department }      // 分组
val first = numbers.firstOrNull { it > 3 }        // 4
val any = numbers.any { it > 4 }                   // true
val all = numbers.all { it > 0 }                   // true
```

## 4. 控制流

```kotlin
// if 表达式（有返回值）
val max = if (a > b) a else b

// when 表达式（替代 switch）
val result = when (score) {
    in 90..100 -> "优秀"
    in 60..89 -> "及格"
    else -> "不及格"
}

// when 无参数
when {
    user.isAdmin -> handleAdmin()
    user.isActive -> handleActive()
    else -> handleDefault()
}

// for 循环
for (i in 0 until 5) { }          // 0,1,2,3,4
for (i in 5 downTo 1) { }         // 5,4,3,2,1
for (i in 0..10 step 2) { }       // 0,2,4,6,8,10
for ((index, value) in list.withIndex()) { }
for ((key, value) in map) { }

// 区间
val range = 1..10          // 闭区间
val until = 1 until 10     // 半开区间
```

## 5. 函数

```kotlin
// 基本函数
fun greet(name: String, greeting: String = "Hello"): String {
    return "$greeting, $name"
}

// 单表达式函数
fun add(a: Int, b: Int) = a + b

// 命名参数
greet(name = "张三", greeting = "Hi")

// 可变参数
fun sum(vararg numbers: Int): Int = numbers.sum()

// 扩展函数
fun String.isEmail(): Boolean = contains("@") && contains(".")
"test@example.com".isEmail()  // true

// 中缀函数
infix fun Int.times(str: String) = str.repeat(this)
val result = 3 times "abc"  // "abcabcabc"

// 高阶函数
fun <T> List<T>.customFilter(predicate: (T) -> Boolean): List<T> {
    val result = mutableListOf<T>()
    for (item in this) {
        if (predicate(item)) result.add(item)
    }
    return result
}
```

## 6. 数据类与密封类

```kotlin
// 数据类（自动生成 equals/hashCode/toString/copy/componentN）
data class User(
    val id: Int,
    val name: String,
    val email: String,
)

val user = User(1, "张三", "test@example.com")
val copy = user.copy(name = "李四")
val (id, name, email) = user  // 解构

// 密封类（限制继承）
sealed class Result<out T> {
    data class Success<T>(val data: T) : Result<T>()
    data class Error(val message: String, val cause: Throwable? = null) : Result<Nothing>()
    data object Loading : Result<Nothing>()
}

// 配合 when 使用（编译器检查完整性）
fun handleResult(result: Result<User>) = when (result) {
    is Result.Success -> showUser(result.data)
    is Result.Error -> showError(result.message)
    is Result.Loading -> showLoading()
}

// 枚举类
enum class Status(val code: Int) {
    ACTIVE(1), INACTIVE(0), DELETED(-1);
}
```

## 7. 作用域函数

```kotlin
// let：非空执行，转换
val length = name?.let { it.length } ?: 0

// run：对象配置 + 计算结果
val result = user.run {
    "$name ($email)"
}

// with：对同一对象多次操作
with(user) {
    println(name)
    println(email)
}

// apply：对象配置（返回对象本身）
val user = User().apply {
    name = "张三"
    email = "test@example.com"
}

// also：附加操作（返回对象本身）
val user = createUser().also {
    logger.info("Created user: ${it.name}")
}
```
## 🎬 推荐视频资源

- [freeCodeCamp - Kotlin Full Course](https://www.youtube.com/watch?v=EExSSotojVI) — Kotlin完整课程
- [Philipp Lackner - Kotlin Tutorial](https://www.youtube.com/watch?v=5flXf8nuq60) — Kotlin入门教程
- [JetBrains - Kotlin by JetBrains](https://www.youtube.com/watch?v=F9UC9DY-vIU) — 官方Kotlin教程
### 📺 B站（Bilibili）
- [黑马程序员 - Kotlin教程](https://www.bilibili.com/video/BV1wf4y1s7TG) — Kotlin完整中文教程

### 🌐 其他平台
- [Kotlin官方中文文档](https://book.kotlincn.net/) — 官方中文文档
- [Kotlin Koans](https://play.kotlinlang.org/koans/) — 官方交互式练习


## 8. Kotlin 2.x 新特性

<!-- version-check: Kotlin 2.3.21 stable, 2.4.0-RC2 (2026-05-27) prerelease, checked 2026-05-31 -->

> 🔄 更新于 2026-04-21（2026-05-31 校准 2.4 状态：已到 RC2）

Kotlin 2.0 于 2024 年发布，引入了全新的 **K2 编译器**，当前最新稳定版为 **Kotlin 2.3.21**（2026-04-23），下一代 **2.4.0** 已进入 RC 阶段（2026-05-27 发布 2.4.0-RC2），GA 临近。

<!-- 修复于 2026-05-31: 原文称"2.4.0-Beta2 已进入 EAP"，经 GitHub Releases 实测 Kotlin 已发布 2.4.0-RC（2026-05-13）、2.4.0-RC2（2026-05-27），早已超出 Beta 阶段，校准为 RC -->


### K2 编译器

K2 编译器是 Kotlin 前端的完全重写，带来显著的编译速度提升和更好的类型推断：

```kotlin
// K2 编译器改进了智能类型转换
fun process(value: Any) {
    if (value is String && value.length > 0) {
        // K2 在更多场景下自动推断类型，无需显式转换
        println(value.uppercase())
    }
}
```

### Kotlin 2.1+ 新语法

```kotlin
// Guard conditions in when（when 中的守卫条件）
fun classify(value: Any) = when (value) {
    is String if value.isNotEmpty() -> "非空字符串"
    is Int if value > 0 -> "正整数"
    else -> "其他"
}

// 多美元符号字符串插值（减少转义）
val regex = $"\\d{3}-\\d{4}"  // 不需要额外转义 $
```

### Kotlin 2.3 新特性（2025-12-16 发布）

```kotlin
// 未使用返回值检查器（实验性）
// 编译器会警告未使用的函数返回值
val list = mutableListOf(1, 2, 3)
list.sorted()  // ⚠️ 警告：sorted() 返回新列表，原列表未改变

// 显式 backing fields（实验性）
class User {
    val name: String
        field = "默认名称"  // 显式声明 backing field
        get() = field.uppercase()
}

// name-based 解构声明（Kotlin 2.3.20）
data class Point(val x: Int, val y: Int)
val point = Point(1, 2)
val (y, x) = point  // 按名称匹配，而非位置
```

### 版本选择建议（2026）

| 场景 | 推荐版本 | 说明 |
|------|----------|------|
| 新项目 | Kotlin 2.3.21 | 最新稳定版，K2 编译器默认启用 |
| 现有项目升级 | Kotlin 2.1.x+ | 先迁移到 2.1，再逐步升级 |
| KMP 跨平台 | Kotlin 2.3.21 | KMP 在 2.x 中显著改进 |
| 尝鲜 / 提前适配 | Kotlin 2.4.0-RC2 | 仅用于实验项目，GA 临近（KotlinConf 2026 后释出 RC，正式版预计 2026-06） |

> 来源：[Kotlin 2.3.0 Released](https://blog.jetbrains.com/kotlin/2025/12/kotlin-2-3-0-released/)、[What's new in Kotlin 2.3.20](https://kotlinlang.org/docs/whatsnew2320.html)

### Kotlin 2.3.21（2026-04-23 当前稳定版）

> 🔄 更新于 2026-05-18

<!-- version-check: Kotlin 2.3.21 stable, 2.4.0-RC2 prerelease, KotlinConf 2026 May 20-22 Munich, checked 2026-05-31 -->

Kotlin 2.3.21 是 2.3.x 分支的补丁版本（2026-04-23 发布），主要内容是工具链 / IDE 支持的稳定性修复，不引入语法变化。Android 项目可直接从 2.3.20 升级，无 Breaking Change。来源：[Kotlin Documentation FAQ](https://kotlinlang.org/docs/faq.html)

### Kotlin 2.4.0-RC2（2026-05 RC 阶段）

Kotlin 2.4 已进入 RC2 阶段（2026-05-27 发布），在 KotlinConf 2026（2026-05-20 至 22，慕尼黑）期间释出了 RC，GA 临近。来源：[Kodee's Kotlin Roundup — May 2026](https://blog.jetbrains.com/kotlin/2026/05/kodees-kotlin-roundup-golden-kodee-finalists-kotlin-2-4-0-beta2-and-new-learning-resources/)、[Kotlin GitHub Releases](https://github.com/JetBrains/kotlin/releases)

```kotlin
// 2.4 EAP：上下文参数（context parameters）实验性增强
// 用于替代 receiver lambda 中冗长的 this 链
context(_: Logger)
fun process(value: String) {
    log("处理 $value")  // 自动从 context 中解析 Logger
}

// 2.4 EAP：Kotlin/Wasm GC 体积进一步减小
// Kotlin/Native 在 iOS arm64 上的二进制体积也有持续优化
```

**升级建议**：

- 生产项目：**继续使用 2.3.21**，等 2.4 GA 稳定一段时间后再上
- 库作者：可以用 2.4.0-RC2 提前测试 binary compatibility，但发布版仍以 2.3.x 编译
- KMP 项目：升级 2.4 前先确认 Compose Multiplatform 的兼容版本（CMP 1.11.0 当前对齐 Kotlin 2.3.x）

### Kotlin 2.4.0-RC2 详细稳定特性

> 🔄 更新于 2026-05-20（2026-05-31 校准：Beta2 → RC2）

<!-- version-check: Kotlin 2.4.0-RC2 stable features list, KotlinConf 2026 keynote May 20-22, checked 2026-05-31 -->

Kotlin 2.4.0-RC2 已经把多个之前的 Experimental 特性升级为 **Stable**，使得 2.4 GA 后这些特性可以直接在生产项目中使用而无需 opt-in 注解。来源：[What's new in Kotlin 2.4.0-RC](https://kotlinlang.org/docs/whatsnew-eap.html)

**1. Stable context parameters**：从 2.2 引入的 Beta 特性正式稳定

```kotlin
// 2.4 Stable：context parameters 取代旧的 context receivers
// 可以在被调用函数内通过名字访问上下文实例
context(logger: Logger, db: Database)
fun saveUser(user: User) {
    logger.info("保存用户 ${user.id}")
    db.insert(user)
}

// 调用方使用 with(logger) { with(db) { saveUser(user) } } 自动注入
```

**2. Stable explicit backing fields**：之前需要 `@OptIn` 现在直接用

```kotlin
class Repository {
    // 公开 List<User>，但内部用 MutableList 维护
    val users: List<User>
        field = mutableListOf<User>()  // backing field 类型不同于属性类型

    fun add(user: User) {
        users.field.add(user)  // 内部仍可调用 mutable API
    }
}
```

**3. Stable UUIDs in Standard Library**：`kotlin.uuid.Uuid` 进入 stdlib stable

```kotlin
import kotlin.uuid.Uuid

val id = Uuid.random()           // 生成 v4 UUID
val parsed = Uuid.parse("...")   // 安全解析
```

**4. Kotlin/JVM 支持 Java 26**：可以把 `jvmTarget` 设为 26，annotations in metadata 默认启用（Kotlin 反射可见 Java 注解）

**5. Kotlin/Native CMS GC 成为默认**：替代之前的 stop-the-world GC，iOS App 在 Kotlin Multiplatform 共享代码段的 GC 暂停时间显著降低

**6. Kotlin/Wasm 增量编译默认启用**：Wasm 项目重编译时间显著缩短，Component Model 支持是 WebAssembly 跨语言互操作的关键基础

**7. Gradle 9.4.1 兼容**：必须使用 Gradle 9.4.1+ 才能用 2.4.0-RC2 的部分 KMP 能力

### KotlinConf 2026 速览（2026-05-20 至 05-22 慕尼黑）

> 🔄 更新于 2026-05-20

KotlinConf 2026 是 Kotlin 2.4 的发布舞台，超过 2,000 名 Kotlin 开发者到现场，全球同步直播在 [Kotlin YouTube 频道](https://www.youtube.com/@Kotlin)。Day 1 keynote 由 JetBrains Kotlin 团队主讲，Day 2 keynote 由前 Engineering VP Lena Reinhard 演讲 *We Were Meant to Be*（聚焦 AI 时代的工程团队领导力）。来源：[KotlinConf 2026 官网](https://www.kotlinconf.com/)、[KotlinConf 2026 Speakers](https://kotlinconf.com/speakers)

**值得关注的方向（基于公开 schedule）**：

1. **Kotlin Multiplatform 落地实战**：Jetpack Compose Multiplatform 1.11.0（2026-05-15 已发布）+ iOS 原生文本输入 opt-in，是把 KMP 在 iOS 端体验逼近 SwiftUI 的关键拼图
2. **Koog——JetBrains 的 AI Agent 框架**：原生 Kotlin DSL，在 KotlinConf 全天 Workshop 中专题介绍。是 Kotlin 进入 AI Agent 生态的官方信号
3. **Kotlin 2.4 路线图**：2.4 已于 KotlinConf 期间进入 RC（2026-05-13 RC、2026-05-27 RC2），GA 时间窗预计在 RC 之后数周内（约 2026-06）<!-- 修复于 2026-05-31: 原文称"GA 预计 KotlinConf 后 4-6 周"，实测 2.4 已发布 RC/RC2，校准为 RC 已出、GA 临近 -->

**升级时间窗建议**：

| 当前版本 | 建议路径 |
|----------|----------|
| 1.9.x | 先升 2.0 / 2.1 适配 K2，再升 2.3.21 |
| 2.0 / 2.1 / 2.2 | 直接升 2.3.21（无 Breaking） |
| 2.3.x | 持续保持 2.3.21，等 2.4 GA + Compose 1.12 BOM 同步发布后再升 |
| 实验项目 | 可以用 2.4.0-RC2，提前体验 stable context parameters / UUID / Java 26 |

> 更新于 2026-07-09

### Kotlin 2.4.0 GA 正式版（2026-06-03）

**Kotlin 2.4.0** 已 GA，与 RC 相比无意外 Breaking，但需注意：

| 变化 | 影响 |
| ---- | ---- |
| **`-language-version=1.9` 移除** | K1 编译器不可再选；必须 K2 |
| **AGP 最低 8.5.2** | Android 项目需同步升级 Gradle Plugin |
| **Context parameters 稳定** | Clean Architecture 依赖注入语法更简洁 |
| **UUID API 稳定** | 标准库原生 UUID，减少 java.util 依赖 |
| **Java 26 字节码** | `jvmTarget = 26`，annotations in metadata 默认开 |
| **Gradle 9.5.0 兼容** | 构建脚本需验证插件矩阵 |

```kotlin
// build.gradle.kts
plugins {
    id("com.android.application") version "8.5.2"
    kotlin("android") version "2.4.0"
}
// 检查并删除：languageVersion.set(KotlinVersion.KOTLIN_1_9)
```

**Android 17 + Kotlin 2.4 联调清单**：Compose Compiler 版本对齐、KSP/kapt 升级、移除 `kotlin.io.readLine()`（改用 `readln()`/`readlnOrNull()`）。

> 来源：[Kotlin 2.4.0 发布公告](https://blog.jetbrains.com/kotlin/2026/06/kotlin-2-4-0-released/)、[GitHub Release v2.4.0](https://github.com/JetBrains/kotlin/releases/tag/v2.4.0)、[Kotlin 2.4.0 兼容指南](https://medium.com/@AlexanderObregon/what-to-know-about-the-kotlin-2-4-0-release-ec2f3a5a8d3e)
