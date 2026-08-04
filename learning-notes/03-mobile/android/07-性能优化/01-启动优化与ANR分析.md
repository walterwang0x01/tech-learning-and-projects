# 启动优化与 ANR 分析
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 启动类型

```kotlin
// 冷启动：进程不存在 → 创建进程 → Application → Activity
// 温启动：进程存在，Activity 被回收 → 重建 Activity
// 热启动：进程和 Activity 都在 → onRestart → onStart

// 测量启动时间
// adb shell am start-activity -W com.example.app/.MainActivity
// TotalTime: 冷启动总时间
```

## 2. App Startup 库

```kotlin
// 依赖: androidx.startup:startup-runtime

// 定义 Initializer
class TimberInitializer : Initializer<Unit> {
    override fun create(context: Context) {
        Timber.plant(Timber.DebugTree())
    }
    override fun dependencies(): List<Class<out Initializer<*>>> = emptyList()
}

class CoilInitializer : Initializer<ImageLoader> {
    override fun create(context: Context): ImageLoader {
        return ImageLoader.Builder(context)
            .memoryCache { MemoryCache.Builder(context).maxSizePercent(0.25).build() }
            .build()
    }
    override fun dependencies() = listOf(TimberInitializer::class.java)
}

// AndroidManifest.xml
// <provider android:name="androidx.startup.InitializationProvider"
//     android:authorities="${applicationId}.androidx-startup">
//     <meta-data android:name="com.example.CoilInitializer"
//         android:value="androidx.startup" />
// </provider>

// 延迟初始化
AppInitializer.getInstance(context).initializeComponent(CoilInitializer::class.java)
```

## 3. 启动优化策略

```kotlin
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // 1. 必要初始化（主线程）
        initCrashReporter()

        // 2. 异步初始化
        CoroutineScope(Dispatchers.Default).launch {
            initAnalytics()
            initPush()
        }

        // 3. 延迟初始化（首屏显示后）
        // 在 Activity.onResume 后执行
    }
}

// IdleHandler：空闲时执行
class MainActivity : AppCompatActivity() {
    override fun onResume() {
        super.onResume()
        Looper.myQueue().addIdleHandler {
            initNonCriticalSDKs()
            false  // 返回 false 表示只执行一次
        }
    }
}
```

## 4. Baseline Profiles

```kotlin
// 依赖: androidx.benchmark:benchmark-macro-junit4

@RunWith(AndroidJUnit4::class)
class BaselineProfileGenerator {
    @get:Rule
    val rule = BaselineProfileRule()

    @Test
    fun generateBaselineProfile() {
        rule.collect(packageName = "com.example.app") {
            // 冷启动
            pressHome()
            startActivityAndWait()

            // 关键用户路径
            device.findObject(By.text("搜索")).click()
            device.waitForIdle()
            device.findObject(By.res("search_input")).text = "kotlin"
        }
    }
}

// build.gradle.kts
// baselineProfile { automaticGenerationDuringBuild = true }
```

## 5. ANR 分析

<!-- version-check: Android Performance Tools 2026, Baseline Profiles, Android 17 ProfilingManager, Kotlin 2.4.0, checked 2026-07-08 -->

```kotlin
// ANR 触发条件：
// - 主线程 5 秒内未响应输入事件
// - BroadcastReceiver 10 秒内未完成
// - Service 20 秒内未完成

// ❌ 错误：主线程执行耗时操作
class BadActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val data = database.queryAll()  // 主线程 IO → ANR
    }
}

// ✅ 正确：异步执行
class GoodActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            val data = withContext(Dispatchers.IO) { database.queryAll() }
            updateUI(data)
        }
    }
}

// StrictMode 检测
if (BuildConfig.DEBUG) {
    StrictMode.setThreadPolicy(
        StrictMode.ThreadPolicy.Builder()
            .detectDiskReads()
            .detectDiskWrites()
            .detectNetwork()
            .penaltyLog()
            .build()
    )
}

// ANR 日志位置: /data/anr/traces.txt
// adb pull /data/anr/traces.txt
```

> 🔄 更新于 2026-07-08

## 6. Android 17 启动与 ANR 相关变化

<!-- version-check: Android 17 API 37 stable, lock-free MessageQueue, ProfilingManager COLD_START, Kotlin 2.4.0 K2, checked 2026-07-08 -->

Android 17（2026-06 stable）在消息队列、ART 垃圾回收和系统级 Profiling 三方面直接影响启动流畅度与 ANR 诊断。来源：[MessageQueue behavior change](https://developer.android.com/about/versions/17/changes/messagequeue)、[Android 17 Release Notes](https://developer.android.com/about/versions/17/release-notes)、[Android 17 Features — ProfilingManager](https://developer.android.com/about/versions/17/features#profilingmanager)

### 6.1 lock-free MessageQueue 减少主线程丢帧

```kotlin
// targetSdk 37+ 默认启用 lock-free MessageQueue，降低锁竞争导致的 UI jank
// 反射访问 MessageQueue.mMessages 在新实现中恒为 null — 卡顿监测库必须升级

// 调试：在不改 targetSdk 的情况下提前验证（debuggable build）
// adb shell am compat enable USE_NEW_MESSAGEQUEUE <package>

// 回退排查：adb shell am compat disable USE_NEW_MESSAGEQUEUE <package>
```

来源：[MessageQueue behavior change guidance](https://developer.android.com/about/versions/17/changes/messagequeue)

### 6.2 ProfilingManager 新增启动与异常触发器

```kotlin
// Android 17 扩展 ProfilingManager 系统触发器，可在生产环境捕获启动与性能异常
val profilingManager = getSystemService(ProfilingManager::class.java)

// COLD_START — 冷启动时自动采集 profile
profilingManager.registerForProfiling(
    ProfilingManager.ProfilingTriggerRequest.Builder()
        .setTriggerType(ProfilingManager.TRIGGER_TYPE_COLD_START)
        .build(),
    executor,
    profilingCallback
)

// KILL_EXCESSIVE_CPU_USAGE — CPU 滥用被系统终止前采样
// TRIGGER_TYPE_ANOMALY — 含 binder 风暴、内存逼近上限等异常
```

来源：[Android 17 Features — ProfilingManager triggers](https://developer.android.com/about/versions/17/features#profilingmanager)

### 6.3 ART 分代 GC 与启动路径

```
Android 17 Performance & Runtime：
├─ Concurrent Mark-Compact 支持分代 GC（young generation 优先、低成本）
├─ 短生命周期对象回收更快 → 冷启动后首批对象分配压力降低
└─ 配合 Baseline Profile + R8 fullMode 效果更明显
```

### 6.4 Kotlin 2.4.0 编译器与 Compose 启动

Kotlin **2.4.0**（2026-06-03）移除 K1 前端，K2 为唯一编译路径；Compose Compiler 与之紧耦合，升级后编译期优化与增量编译更稳定。升级前确保 AGP ≥ **8.5.2**，并在 CI 跑一遍 Baseline Profile 生成任务验证启动指标。来源：[What's new in Kotlin 2.4.0](https://kotlinlang.org/docs/whatsnew24.html)
