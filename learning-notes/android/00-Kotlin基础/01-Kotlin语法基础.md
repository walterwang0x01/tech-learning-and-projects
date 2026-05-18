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

<!-- version-check: Kotlin 2.3.21 stable, 2.4.0-Beta2 EAP, checked 2026-05-18 -->

> 🔄 更新于 2026-04-21（2026-05-18 增补 2.3.21 + 2.4 EAP）

Kotlin 2.0 于 2024 年发布，引入了全新的 **K2 编译器**，当前最新稳定版为 **Kotlin 2.3.21**（2026-04-23），下一代 **2.4.0-Beta2** 已进入 EAP 阶段。

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
| 尝鲜 / 提前适配 | Kotlin 2.4.0-Beta2 | 仅用于实验项目，正式版预计随 KotlinConf 2026 发布 |

> 来源：[Kotlin 2.3.0 Released](https://blog.jetbrains.com/kotlin/2025/12/kotlin-2-3-0-released/)、[What's new in Kotlin 2.3.20](https://kotlinlang.org/docs/whatsnew2320.html)

### Kotlin 2.3.21（2026-04-23 当前稳定版）

> 🔄 更新于 2026-05-18

<!-- version-check: Kotlin 2.3.21 stable, 2.4.0-Beta2 EAP, KotlinConf 2026 May 20-22 Munich, checked 2026-05-18 -->

Kotlin 2.3.21 是 2.3.x 分支的补丁版本（2026-04-23 发布），主要内容是工具链 / IDE 支持的稳定性修复，不引入语法变化。Android 项目可直接从 2.3.20 升级，无 Breaking Change。来源：[Kotlin Documentation FAQ](https://kotlinlang.org/docs/faq.html)

### Kotlin 2.4.0-Beta2（2026-04 EAP）

Kotlin 2.4 进入 Beta2 阶段，预计在 KotlinConf 2026（2026-05-20 至 22，慕尼黑）期间释出更多发布信号。来源：[Kodee's Kotlin Roundup — May 2026](https://blog.jetbrains.com/kotlin/2026/05/kodees-kotlin-roundup-golden-kodee-finalists-kotlin-2-4-0-beta2-and-new-learning-resources/)、[What's new in Kotlin 2.4.0-Beta2](https://kotlinlang.org/docs/whatsnew-eap.html)

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
- 库作者：可以用 2.4.0-Beta2 提前测试 binary compatibility，但发布版仍以 2.3.x 编译
- KMP 项目：升级 2.4 前先确认 Compose Multiplatform 的兼容版本（CMP 1.11.0 当前对齐 Kotlin 2.3.x）
