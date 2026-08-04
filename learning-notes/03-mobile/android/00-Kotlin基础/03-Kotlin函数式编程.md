# Kotlin 函数式编程
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 高阶函数与 Lambda

```kotlin
// 高阶函数（函数作为参数或返回值）
fun <T> List<T>.customFilter(predicate: (T) -> Boolean): List<T> {
    return filter(predicate)
}

// Lambda 表达式
val sum = { a: Int, b: Int -> a + b }
val greet: (String) -> String = { name -> "Hello, $name" }

// 尾随 Lambda
listOf(1, 2, 3).map { it * 2 }
listOf(1, 2, 3).fold(0) { acc, n -> acc + n }

// 函数引用
fun isEven(n: Int) = n % 2 == 0
listOf(1, 2, 3, 4).filter(::isEven)

// 返回函数
fun multiplier(factor: Int): (Int) -> Int = { it * factor }
val double = multiplier(2)
double(5)  // 10
```

## 2. 内联函数

```kotlin
// inline：Lambda 编译时内联，避免对象创建开销
inline fun <T> measureTime(block: () -> T): Pair<T, Long> {
    val start = System.currentTimeMillis()
    val result = block()
    val time = System.currentTimeMillis() - start
    return result to time
}

// noinline：不内联某个 Lambda 参数
inline fun doSomething(inlined: () -> Unit, noinline stored: () -> Unit) {
    inlined()
    callback = stored  // noinline 的可以存储
}

// crossinline：禁止非局部返回
inline fun runOnUiThread(crossinline action: () -> Unit) {
    handler.post { action() }
}

// reified：泛型类型实化
inline fun <reified T> Gson.fromJson(json: String): T {
    return fromJson(json, T::class.java)
}
val user = gson.fromJson<User>(jsonString)
```

## 3. 序列（Sequence）

```kotlin
// 惰性求值（大数据集时性能更好）
val result = (1..1_000_000)
    .asSequence()
    .filter { it % 2 == 0 }
    .map { it * it }
    .take(10)
    .toList()

// 生成序列
val fibonacci = generateSequence(Pair(0, 1)) { Pair(it.second, it.first + it.second) }
    .map { it.first }
    .take(10)
    .toList()  // [0, 1, 1, 2, 3, 5, 8, 13, 21, 34]

// sequence builder
val customSequence = sequence {
    yield(1)
    yieldAll(listOf(2, 3))
    yieldAll(generateSequence(4) { it + 1 })
}
```

## 4. 集合操作符

```kotlin
data class User(val name: String, val age: Int, val department: String)

val users = listOf(
    User("张三", 25, "开发"),
    User("李四", 30, "设计"),
    User("王五", 28, "开发"),
)

// 转换
users.map { it.name }                    // [张三, 李四, 王五]
users.flatMap { it.name.toList() }       // 展平
users.associate { it.name to it.age }    // Map

// 过滤
users.filter { it.age > 25 }
users.filterNot { it.department == "设计" }
users.partition { it.age > 25 }          // Pair<匹配, 不匹配>

// 分组与聚合
users.groupBy { it.department }          // Map<String, List<User>>
users.maxByOrNull { it.age }
users.minByOrNull { it.age }
users.sortedByDescending { it.age }
users.distinctBy { it.department }

// 判断
users.any { it.age > 25 }               // true
users.all { it.age > 20 }               // true
users.none { it.age > 50 }              // true
users.count { it.department == "开发" }   // 2
```
