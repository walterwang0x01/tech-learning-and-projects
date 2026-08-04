# Kotlin 与 Java 互操作
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Java 调用 Kotlin

```kotlin
// @JvmStatic — 生成静态方法
class UserUtils {
    companion object {
        @JvmStatic
        fun create(name: String) = User(name)
    }
}
// Java: UserUtils.create("张三")

// @JvmField — 暴露为字段（不生成 getter/setter）
class Config {
    @JvmField val MAX_RETRY = 3
}

// @JvmOverloads — 生成重载方法
@JvmOverloads
fun greet(name: String, greeting: String = "Hello") = "$greeting, $name"
// Java: greet("张三") 和 greet("张三", "Hi") 都可用

// @JvmName — 自定义 JVM 名称
@file:JvmName("StringUtils")
fun String.isEmail(): Boolean = contains("@")
// Java: StringUtils.isEmail(str)

// @Throws — 声明受检异常
@Throws(IOException::class)
fun readFile(path: String): String { /* ... */ }
```

## 2. Kotlin 调用 Java

```kotlin
// 平台类型（Java 返回值可能为 null）
val list: MutableList<String> = ArrayList()  // Java ArrayList
val size: Int = list.size  // 平台类型，可能 NPE

// SAM 转换（Java 单抽象方法接口 → Lambda）
button.setOnClickListener { view ->
    // Java: new View.OnClickListener() { void onClick(View v) { } }
}

executor.submit { println("Running in thread pool") }

// Java Stream → Kotlin
javaList.stream()
    .filter { it.isNotEmpty() }
    .map { it.uppercase() }
    .collect(Collectors.toList())

// 或直接用 Kotlin 集合操作
javaList.filter { it.isNotEmpty() }.map { it.uppercase() }
```

## 3. 互操作注意事项

```kotlin
// 1. Kotlin 的 null 安全 vs Java 的可空性
// Java 返回值在 Kotlin 中是平台类型（T!），需要自行判断

// 2. Kotlin 的 data class 在 Java 中
// 自动生成 getXxx()/setXxx()、equals()、hashCode()、toString()、copy()

// 3. Kotlin 的 companion object 在 Java 中
// 通过 Companion 访问：User.Companion.create("张三")
// 加 @JvmStatic 后：User.create("张三")

// 4. Kotlin 的扩展函数在 Java 中
// 编译为静态方法：StringExtKt.isEmail(str)
```
