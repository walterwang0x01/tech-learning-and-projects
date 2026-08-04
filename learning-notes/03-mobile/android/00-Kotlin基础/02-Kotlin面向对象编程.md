# Kotlin 面向对象编程
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 类与对象

```kotlin
// 主构造函数
class User(val id: Int, var name: String, val email: String) {
    // 次构造函数
    constructor(name: String) : this(0, name, "")

    // 初始化块
    init { require(name.isNotBlank()) { "Name cannot be blank" } }

    // 方法
    fun displayName() = "[$id] $name"

    override fun toString() = "User(id=$id, name=$name)"
}

// 对象声明（单例）
object DatabaseManager {
    fun getConnection(): Connection { /* ... */ }
}

// 伴生对象（类似 Java static）
class User(val name: String) {
    companion object {
        const val MAX_NAME_LENGTH = 50
        fun create(name: String) = User(name)
    }
}
val user = User.create("张三")
```

## 2. 继承与接口

```kotlin
// 类默认 final，需要 open 才能继承
open class Animal(val name: String) {
    open fun speak(): String = "$name makes a sound"
}

class Dog(name: String, val breed: String) : Animal(name) {
    override fun speak() = "$name barks"
}

// 接口
interface Clickable {
    fun click()
    fun showOff() = println("I'm clickable!")  // 默认实现
}

interface Focusable {
    fun showOff() = println("I'm focusable!")
}

class Button : Clickable, Focusable {
    override fun click() { println("Button clicked") }
    override fun showOff() {
        super<Clickable>.showOff()  // 指定调用哪个默认实现
    }
}

// 抽象类
abstract class Shape {
    abstract fun area(): Double
    fun describe() = "Area: ${area()}"
}
```

## 3. 属性委托

```kotlin
// lazy（延迟初始化）
val heavyObject: HeavyObject by lazy {
    HeavyObject()  // 首次访问时才创建
}

// observable（属性变化监听）
var name: String by Delegates.observable("初始值") { _, old, new ->
    println("$old → $new")
}

// 自定义委托
class SharedPreferencesDelegate(private val key: String, private val default: String) {
    operator fun getValue(thisRef: Any?, property: KProperty<*>): String {
        return prefs.getString(key, default) ?: default
    }
    operator fun setValue(thisRef: Any?, property: KProperty<*>, value: String) {
        prefs.edit().putString(key, value).apply()
    }
}

var username: String by SharedPreferencesDelegate("username", "")
```

## 4. 扩展函数与属性

```kotlin
// 扩展函数
fun String.isEmail(): Boolean = matches(Regex("[^@]+@[^@]+\\.[^@]+"))
"test@example.com".isEmail()  // true

// 扩展属性
val String.lastChar: Char get() = this[length - 1]

// 可空类型扩展
fun String?.orEmpty(): String = this ?: ""

// 泛型扩展
fun <T> List<T>.secondOrNull(): T? = if (size >= 2) this[1] else null
```
