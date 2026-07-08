# 内存优化与 LeakCanary
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 常见内存泄漏场景

```kotlin
// ❌ 错误：匿名内部类持有 Activity 引用
class LeakyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val handler = object : Handler(Looper.getMainLooper()) {
            override fun handleMessage(msg: Message) {
                // 隐式持有 Activity 引用
                updateUI()
            }
        }
        handler.sendEmptyMessageDelayed(0, 60_000)
    }
}

// ✅ 正确：使用弱引用或 lifecycleScope
class SafeActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            delay(60_000)
            updateUI()  // 自动随生命周期取消
        }
    }
}

// ❌ 错误：Fragment 中持有 Binding
class LeakyFragment : Fragment() {
    private val binding: FragmentBinding = FragmentBinding.inflate(layoutInflater)
    // binding 在 onDestroyView 后仍被持有
}

// ✅ 正确：onDestroyView 中置空
class SafeFragment : Fragment() {
    private var _binding: FragmentBinding? = null
    private val binding get() = _binding!!
    override fun onDestroyView() { super.onDestroyView(); _binding = null }
}

// ❌ 错误：单例持有 Context
object AppManager {
    lateinit var context: Context  // 如果传入 Activity 会泄漏
}

// ✅ 正确：使用 Application Context
object AppManager {
    lateinit var context: Context
    fun init(app: Application) { context = app.applicationContext }
}
```

## 2. LeakCanary

```kotlin
// build.gradle.kts
// debugImplementation("com.squareup.leakcanary:leakcanary-android:2.13")

// 自动检测：Activity/Fragment/ViewModel/View/Service 泄漏
// 无需额外代码，debug 构建自动启用

// 手动监控自定义对象
class MyManager {
    fun destroy() {
        // 清理后告诉 LeakCanary 监控此对象
        AppWatcher.objectWatcher.expectWeaklyReachable(
            this, "MyManager was destroyed"
        )
    }
}
```

## 3. Android Profiler 内存分析

```kotlin
// 触发 GC 后查看内存快照
// Android Studio → Profiler → Memory → Dump Java Heap

// 代码中记录内存信息
fun logMemoryInfo(context: Context) {
    val activityManager = context.getSystemService<ActivityManager>()
    val memInfo = ActivityManager.MemoryInfo()
    activityManager?.getMemoryInfo(memInfo)
    Log.d("Memory", "可用: ${memInfo.availMem / 1024 / 1024}MB")
    Log.d("Memory", "总量: ${memInfo.totalMem / 1024 / 1024}MB")
    Log.d("Memory", "低内存: ${memInfo.lowMemory}")
}
```

## 4. Bitmap 优化

```kotlin
// 按需采样加载大图
fun decodeSampledBitmap(res: Resources, resId: Int, reqWidth: Int, reqHeight: Int): Bitmap {
    val options = BitmapFactory.Options().apply { inJustDecodeBounds = true }
    BitmapFactory.decodeResource(res, resId, options)

    options.inSampleSize = calculateInSampleSize(options, reqWidth, reqHeight)
    options.inJustDecodeBounds = false
    return BitmapFactory.decodeResource(res, resId, options)
}

fun calculateInSampleSize(options: BitmapFactory.Options, reqW: Int, reqH: Int): Int {
    val (height, width) = options.outHeight to options.outWidth
    var inSampleSize = 1
    if (height > reqH || width > reqW) {
        val halfH = height / 2; val halfW = width / 2
        while (halfH / inSampleSize >= reqH && halfW / inSampleSize >= reqW) {
            inSampleSize *= 2
        }
    }
    return inSampleSize
}

// 使用 Coil 自动处理
AsyncImage(
    model = ImageRequest.Builder(context)
        .data(largeImageUrl)
        .size(300, 300)  // 自动缩放
        .build(),
    contentDescription = null
)
```

## 5. 内存优化策略

```kotlin
// 监听内存不足
class MyApp : Application(), ComponentCallbacks2 {
    override fun onTrimMemory(level: Int) {
        when (level) {
            TRIM_MEMORY_UI_HIDDEN -> clearImageCache()
            TRIM_MEMORY_RUNNING_LOW -> reduceMemoryUsage()
            TRIM_MEMORY_COMPLETE -> releaseAllCaches()
        }
    }
}

// 使用 SparseArray 替代 HashMap<Int, Object>
val sparseArray = SparseArray<String>()
sparseArray.put(1, "one")

// 避免自动装箱
val intArray = IntArray(100)  // 而非 Array<Int>
```

> 🔄 更新于 2026-07-08

## 6. Android 17 应用内存限制与 Profiling

<!-- version-check: Android 17 API 37 MemoryLimiter, ProfilingManager ANOMALY/OOM, LeakCanary 2.14+, Kotlin 2.4.0, checked 2026-07-08 -->

Android 17 Beta 4 起引入基于设备总 RAM 的**每进程内存上限**（2026-06 stable 起在部分设备强制执行），超限进程被系统直接终止，**不一定产生标准 crash 堆栈**。来源：[Behavior changes: all apps — App memory limits](https://developer.android.com/about/versions/17/behavior-changes-all)、[Android 17 Release Notes](https://developer.android.com/about/versions/17/release-notes)

### 6.1 检测 MemoryLimiter 终止

```kotlin
// ApplicationExitInfo 中 exit reason = REASON_OTHER
// description 含 "MemoryLimiter:AnonSwap" 表示被内存限制器杀死
fun checkMemoryKill(context: Context) {
    val am = context.getSystemService(ActivityManager::class.java)
    am.getHistoricalProcessExitReasons(context.packageName, 0, 10).forEach { info ->
        if (info.reason == ApplicationExitInfo.REASON_OTHER &&
            info.description?.contains("MemoryLimiter:AnonSwap") == true
        ) {
            reportMemoryLimitKill(info)  // 上报 + 降级缓存策略
        }
    }
}
```

### 6.2 ProfilingManager 在杀进程前抓 Heap Dump

```kotlin
// TRIGGER_TYPE_ANOMALY — 内存逼近上限时系统在杀进程前触发，可拿到现场 heap dump
// TRIGGER_TYPE_OOM — 下次启动时上传上次 OOM 的 Java Heap Dump
profilingManager.registerForProfiling(
    ProfilingManager.ProfilingTriggerRequest.Builder()
        .setTriggerType(ProfilingManager.TRIGGER_TYPE_ANOMALY)
        .build(),
    executor,
    object : ProfilingManager.ProfilingResultCallback {
        override fun onResultReady(result: ProfilingResult) {
            uploadHeapDump(result.artifact)
        }
    }
)
```

来源：[Android 17 Features — ProfilingManager](https://developer.android.com/about/versions/17/features#profilingmanager)

### 6.3 本地调试内存上限

```bash
# 查看当前内存限制器状态
adb shell am memory-limiter status

# 对指定 PID 施加 30MB 上限（仅支持设备已启用限制器时有效）
adb shell am memory-limiter manual <pid> 30

# 移除手动限制，恢复系统默认
adb shell am memory-limiter manual <pid> none

# 全局忽略 / 恢复限制（调试用）
adb shell am memory-limiter ignore all
adb shell am memory-limiter ignore none
```

### 6.4 防御性优化清单（2026 Q3）

| 措施 | 说明 |
|------|------|
| `onTrimMemory()` | 后台立即释放图片缓存、预览 Buffer |
| R8 fullMode | 确认 release 未关闭 `android.enableR8.fullMode` |
| LeakCanary 2.14+ | 开发期捕获泄漏，避免生产触发 MemoryLimiter |
| Coil / Glide 尺寸约束 | 大图按 View 尺寸采样，禁止无界内存缓存 |
| FGS 内存审计 | 前台服务持有大 Buffer 是高风险场景 |

来源：[New Memory Limits in Android 17](https://pbxscience.com/new-memory-limits-in-android-17-can-kill-your-app-without-a-crash-log/)
