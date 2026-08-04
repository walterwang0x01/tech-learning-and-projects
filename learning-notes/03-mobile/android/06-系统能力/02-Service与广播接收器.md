# Service 与广播接收器
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Started Service

```kotlin
class DownloadService : Service() {
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val url = intent?.getStringExtra("url") ?: return START_NOT_STICKY
        scope.launch {
            downloadFile(url)
            stopSelf(startId)
        }
        return START_REDELIVER_INTENT  // 被杀后重新传递 Intent
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        scope.cancel()
        super.onDestroy()
    }
}

// 启动
context.startService(Intent(context, DownloadService::class.java).apply {
    putExtra("url", "https://example.com/file.zip")
})
```

## 2. Bound Service

```kotlin
class MusicService : Service() {
    private val binder = MusicBinder()
    private var mediaPlayer: MediaPlayer? = null

    inner class MusicBinder : Binder() {
        fun getService(): MusicService = this@MusicService
    }

    override fun onBind(intent: Intent): IBinder = binder

    fun play(uri: Uri) {
        mediaPlayer = MediaPlayer.create(this, uri).apply { start() }
    }

    fun pause() { mediaPlayer?.pause() }
    fun stop() { mediaPlayer?.stop(); mediaPlayer?.release() }
}

// 绑定
class MusicActivity : AppCompatActivity() {
    private var musicService: MusicService? = null
    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName, service: IBinder) {
            musicService = (service as MusicService.MusicBinder).getService()
        }
        override fun onServiceDisconnected(name: ComponentName) { musicService = null }
    }

    override fun onStart() {
        super.onStart()
        bindService(Intent(this, MusicService::class.java), connection, BIND_AUTO_CREATE)
    }

    override fun onStop() {
        unbindService(connection)
        super.onStop()
    }
}
```

## 3. 前台 Service

```kotlin
class LocationService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = NotificationCompat.Builder(this, "location_channel")
            .setContentTitle("位置追踪中")
            .setSmallIcon(R.drawable.ic_location)
            .setOngoing(true)
            .build()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            startForeground(1, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_LOCATION)
        } else {
            startForeground(1, notification)
        }
        startLocationUpdates()
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

// AndroidManifest.xml
// <service android:name=".LocationService"
//     android:foregroundServiceType="location"
//     android:exported="false" />
```

## 4. BroadcastReceiver

```kotlin
// 静态注册（AndroidManifest.xml）
class BootReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BOOT_COMPLETED) {
            // 开机启动任务
            WorkManager.getInstance(context).enqueue(syncWorkRequest)
        }
    }
}

// 动态注册
class NetworkFragment : Fragment() {
    private val networkReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            val isConnected = isNetworkAvailable(context)
            updateUI(isConnected)
        }
    }

    override fun onStart() {
        super.onStart()
        val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        requireContext().registerReceiver(networkReceiver, filter)
    }

    override fun onStop() {
        requireContext().unregisterReceiver(networkReceiver)
        super.onStop()
    }
}

// 发送本地广播
LocalBroadcastManager.getInstance(context)
    .sendBroadcast(Intent("com.example.DATA_UPDATED"))
```

## 5. Android 16（API 36）Service 与广播变化

<!-- version-check: Android 16 API 36, Service & Broadcast changes, checked 2026-04-24 -->

> 🔄 更新于 2026-04-24

Android 16 继续收紧后台执行限制，对 Service 和 BroadcastReceiver 都有重要影响。

### 5.1 前台服务 JobScheduler 配额限制

Android 16 对从前台服务启动的 JobScheduler 任务施加更严格的配额限制。即使应用有前台服务在运行，后台 Job 也可能因配额耗尽而静默失败。

来源：[Android 16 Migration Hacks](https://proandroiddev.com/android-16-migration-hacks-the-developers-survival-guide-81c3722bb122)

```kotlin
// ❌ Android 16 上可能静默失败：前台服务中调度大量 Job
class MyForegroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // 前台服务中频繁调度 Job 会触发配额限制
        val jobScheduler = getSystemService(JobScheduler::class.java)
        repeat(10) { i ->
            val job = JobInfo.Builder(i, ComponentName(this, MyJobService::class.java))
                .setRequiredNetworkType(JobInfo.NETWORK_TYPE_ANY)
                .build()
            jobScheduler.schedule(job)  // 部分 Job 可能被拒绝
        }
        return START_STICKY
    }
}

// ✅ 推荐：使用 WorkManager 替代直接 JobScheduler
class MyForegroundService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // WorkManager 内部处理配额和重试逻辑
        val workRequest = OneTimeWorkRequestBuilder<SyncWorker>()
            .setConstraints(Constraints.Builder()
                .setRequiredNetworkType(NetworkType.CONNECTED)
                .build())
            .build()
        WorkManager.getInstance(this).enqueue(workRequest)
        return START_STICKY
    }
}
```

### 5.2 JobScheduler 调试增强

Android 16 新增 `getPendingJobReasons()` API，帮助开发者诊断 Job 为何处于 pending 状态：

```kotlin
// Android 16 新增：查询 Job 挂起原因
val jobScheduler = getSystemService(JobScheduler::class.java)
val pendingJobs = jobScheduler.allPendingJobs
pendingJobs.forEach { job ->
    // getPendingJobReasons() 返回 Job 未执行的原因
    // 如：PENDING_JOB_REASON_QUOTA（配额限制）
    //     PENDING_JOB_REASON_DEVICE_STATE（设备状态）
    Log.d("JobDebug", "Job ${job.id}: pending")
}
```

### 5.3 广播接收器变化

**有序广播优先级范围限定**：Android 16 将有序广播的优先级范围限定在应用进程内，跨进程广播优先级不再保证顺序。

**`RECEIVER_NOT_EXPORTED` 强制要求**：从 Android 13 开始引入的 `RECEIVER_NOT_EXPORTED` 标志在 Android 16 上更加严格，未标注的动态注册接收器可能导致安全异常。

```kotlin
// ✅ Android 16 推荐：动态注册时显式声明导出状态
val filter = IntentFilter("com.example.MY_ACTION")
if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
    // 仅接收应用内广播
    registerReceiver(myReceiver, filter, Context.RECEIVER_NOT_EXPORTED)
}
```

### 5.4 LocalBroadcastManager 替代方案

`LocalBroadcastManager` 已完全废弃（[官方公告](https://developer.android.com/jetpack/androidx/releases/localbroadcastmanager)），2026 年推荐的替代方案：

| 方案 | 适用场景 | 特点 |
|------|---------|------|
| `SharedFlow` | Service → Activity/Fragment 通信 | 协程原生、生命周期安全、支持多订阅者 |
| `StateFlow` | 状态共享 | 始终有最新值、Compose 友好 |
| `LiveData` | 简单 UI 更新 | 生命周期感知、Java 友好 |
| `Channel` | 一次性事件 | 不丢失事件、单消费者 |

```kotlin
// ✅ 推荐：使用 SharedFlow 替代 LocalBroadcastManager
// 定义事件总线
object EventBus {
    private val _events = MutableSharedFlow<AppEvent>(
        extraBufferCapacity = 64
    )
    val events: SharedFlow<AppEvent> = _events.asSharedFlow()

    suspend fun emit(event: AppEvent) {
        _events.emit(event)
    }
}

sealed class AppEvent {
    data class DataUpdated(val id: String) : AppEvent()
    data class DownloadComplete(val path: String) : AppEvent()
}

// Service 中发送事件
class DownloadService : Service() {
    private val scope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    private fun onDownloadComplete(path: String) {
        scope.launch {
            EventBus.emit(AppEvent.DownloadComplete(path))
        }
    }
}

// Activity/Fragment 中接收事件
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                EventBus.events.collect { event ->
                    when (event) {
                        is AppEvent.DataUpdated -> refreshUI(event.id)
                        is AppEvent.DownloadComplete -> showToast(event.path)
                    }
                }
            }
        }
    }
}
```

### 5.5 2026 年 Android 后台任务选型建议

| 场景 | 推荐方案 | 说明 |
|------|---------|------|
| 可延迟的后台任务 | WorkManager | 系统自动管理配额和重试 |
| 用户可见的持续任务 | 前台 Service（声明类型） | 必须声明 `foregroundServiceType` |
| 精确定时任务 | AlarmManager（exact） | 需要 `SCHEDULE_EXACT_ALARM` 权限 |
| 实时数据同步 | FCM + WorkManager | 推送触发 + 后台执行 |
| 组件间通信 | SharedFlow / StateFlow | 替代 LocalBroadcastManager |
| 短时后台处理 | CoroutineScope + Job | 配合 `onDestroy` 取消 |
