# Android 日志最佳实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Android 日志基础

```kotlin
import android.util.Log

Log.d("UserRepo", "Debug: 调试信息")
Log.i("UserRepo", "Info: 关键流程")
Log.w("UserRepo", "Warn: 警告")
Log.e("UserRepo", "Error: 错误", exception)
// Logcat 过滤: adb logcat -s UserRepo | adb logcat *:W
```

| 级别 | 方法 | 场景 |
|------|------|------|
| VERBOSE | `Log.v()` | 最细粒度，仅开发 |
| DEBUG | `Log.d()` | 调试信息 |
| INFO | `Log.i()` | 关键业务事件 |
| WARN | `Log.w()` | 异常但可恢复 |
| ERROR | `Log.e()` | 错误，需要关注 |

## 2. Timber（推荐）

```kotlin
// Jake Wharton 的日志库，自动 Tag、Tree 系统
// implementation("com.jakewharton.timber:timber:5.0.1")

class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree()) // 自动以类名为 Tag
        } else {
            Timber.plant(CrashReportingTree())
        }
    }
}

Timber.d("用户 %s 登录", userId)
Timber.i("订单创建: orderId=%s, amount=%.2f", orderId, amount)
Timber.e(exception, "网络请求失败: url=%s", url)
```

## 3. 自定义 Tree

```kotlin
// 生产环境：只上报 Warn/Error 到 Crashlytics
class CrashReportingTree : Timber.Tree() {
    override fun log(priority: Int, tag: String?, message: String, t: Throwable?) {
        if (priority < Log.WARN) return
        FirebaseCrashlytics.getInstance().apply {
            setCustomKey("priority", priority)
            log(message)
            t?.let { recordException(it) }
        }
    }
}

// 文件日志 Tree
class FileLoggingTree(context: Context) : Timber.Tree() {
    private val logDir = File(context.filesDir, "logs").also { it.mkdirs() }
    override fun log(priority: Int, tag: String?, message: String, t: Throwable?) {
        if (priority < Log.WARN) return
        val line = "${Date()} [${tag}] $message\n"
        File(logDir, "app-${LocalDate.now()}.log").appendText(line)
    }
}
```

## 4. 结构化日志

```kotlin
data class LogEvent(
    val timestamp: Long = System.currentTimeMillis(),
    val level: String, val tag: String, val message: String,
    val metadata: Map<String, Any?> = emptyMap(),
)

class StructuredTree : Timber.Tree() {
    private val json = Json { encodeDefaults = true }
    override fun log(priority: Int, tag: String?, message: String, t: Throwable?) {
        val event = LogEvent(
            level = priorityToLevel(priority), tag = tag ?: "App", message = message,
            metadata = buildMap { t?.let { put("stack", Log.getStackTraceString(it)) } },
        )
        writeToFile(json.encodeToString(event))
    }
}
```

## 5. ProGuard/R8 移除日志

```proguard
# proguard-rules.pro — Release 构建移除 debug 日志
-assumenosideeffects class android.util.Log {
    public static int v(...);
    public static int d(...);
}
-assumenosideeffects class timber.log.Timber {
    public static void v(...);
    public static void d(...);
}
```

```kotlin
// build.gradle.kts — 必须开启 minify 才生效
android {
    buildTypes {
        release {
            isMinifyEnabled = true
            proguardFiles(getDefaultProguardFile("proguard-android-optimize.txt"), "proguard-rules.pro")
        }
    }
}
```

## 6. Firebase Crashlytics

```kotlin
import com.google.firebase.crashlytics.ktx.crashlytics
import com.google.firebase.ktx.Firebase

Firebase.crashlytics.log("用户进入支付页面")
Firebase.crashlytics.setCustomKey("userId", userId)

try { parseResponse(json) }
catch (e: JsonException) {
    Firebase.crashlytics.recordException(e)
    Timber.e(e, "JSON 解析失败")
}
```

## 7. OkHttp 网络请求日志

```kotlin
val loggingInterceptor = HttpLoggingInterceptor { Timber.tag("OkHttp").d(it) }.apply {
    level = if (BuildConfig.DEBUG) HttpLoggingInterceptor.Level.BODY
            else HttpLoggingInterceptor.Level.BASIC
}

val client = OkHttpClient.Builder()
    .addInterceptor(loggingInterceptor)
    .addInterceptor { chain ->
        val req = chain.request()
        val start = System.nanoTime()
        val resp = chain.proceed(req)
        Timber.i("${req.method} ${req.url} → ${resp.code} (${(System.nanoTime()-start)/1_000_000}ms)")
        resp
    }
    .build()
```

## 8. 敏感信息保护

```kotlin
// ❌ 绝对不要
Timber.d("Token: $accessToken")
Timber.d("Password: $password")

// ✅ 脱敏处理
fun String.maskToken() = if (length > 8) "${take(4)}****${takeLast(4)}" else "****"
fun String.maskPhone() = if (length == 11) "${take(3)}****${takeLast(4)}" else "****"

Timber.d("Token: %s", token.maskToken())  // sk-a****ef12
```

## 9. Compose 调试日志

```kotlin
@Composable
fun UserCard(user: User) {
    SideEffect { Timber.d("UserCard recomposed: userId=${user.id}") }
    Card { Text(user.name); Text(user.email) }
}
// Compose Compiler Metrics: ./gradlew assembleRelease -PcomposeCompilerReports=true
// Layout Inspector: Tools → Layout Inspector → 实时查看重组次数
```

## 10. 生产环境日志策略

```kotlin
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        } else {
            Timber.plant(CrashReportingTree())
            Timber.plant(FileLoggingTree(this))
        }
    }
}

// 日志文件清理（保留 7 天）
fun cleanOldLogs(context: Context) {
    val cutoff = System.currentTimeMillis() - 7 * 24 * 3600_000L
    File(context.filesDir, "logs").listFiles()
        ?.filter { it.lastModified() < cutoff }
        ?.forEach { it.delete() }
}
```
