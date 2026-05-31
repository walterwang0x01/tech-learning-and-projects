# WorkManager 后台任务
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 基本 Worker

```kotlin
class UploadWorker(
    context: Context,
    params: WorkerParameters
) : CoroutineWorker(context, params) {

    override suspend fun doWork(): Result {
        val imageUri = inputData.getString("image_uri") ?: return Result.failure()

        return try {
            val url = uploadImage(imageUri)
            val output = workDataOf("uploaded_url" to url)
            Result.success(output)
        } catch (e: Exception) {
            if (runAttemptCount < 3) Result.retry() else Result.failure()
        }
    }
}
```

## 2. OneTimeWorkRequest

```kotlin
val uploadWork = OneTimeWorkRequestBuilder<UploadWorker>()
    .setInputData(workDataOf("image_uri" to uri.toString()))
    .setConstraints(
        Constraints.Builder()
            .setRequiredNetworkType(NetworkType.CONNECTED)
            .setRequiresBatteryNotLow(true)
            .build()
    )
    .setBackoffCriteria(BackoffPolicy.EXPONENTIAL, 30, TimeUnit.SECONDS)
    .addTag("upload")
    .build()

WorkManager.getInstance(context).enqueue(uploadWork)
```

## 3. PeriodicWorkRequest

```kotlin
val syncWork = PeriodicWorkRequestBuilder<SyncWorker>(
    repeatInterval = 1, repeatIntervalTimeUnit = TimeUnit.HOURS,
    flexTimeInterval = 15, flexTimeIntervalUnit = TimeUnit.MINUTES
)
    .setConstraints(
        Constraints.Builder().setRequiredNetworkType(NetworkType.CONNECTED).build()
    )
    .build()

// 唯一任务（避免重复）
WorkManager.getInstance(context).enqueueUniquePeriodicWork(
    "sync_data",
    ExistingPeriodicWorkPolicy.KEEP,
    syncWork
)
```

## 4. 任务链

```kotlin
WorkManager.getInstance(context)
    .beginWith(listOf(downloadWork1, downloadWork2))  // 并行
    .then(processWork)                                  // 串行
    .then(uploadWork)                                   // 串行
    .enqueue()

// 唯一任务链
WorkManager.getInstance(context)
    .beginUniqueWork("import_flow", ExistingWorkPolicy.REPLACE, downloadWork)
    .then(parseWork)
    .then(saveWork)
    .enqueue()
```

## 5. 观察任务状态

```kotlin
// ViewModel 中观察
class UploadViewModel(application: Application) : AndroidViewModel(application) {
    private val workManager = WorkManager.getInstance(application)

    fun startUpload(uri: String) {
        val request = OneTimeWorkRequestBuilder<UploadWorker>()
            .setInputData(workDataOf("image_uri" to uri))
            .build()
        workManager.enqueue(request)
    }

    // 通过 ID 观察
    fun getWorkInfo(id: UUID): LiveData<WorkInfo> =
        workManager.getWorkInfoByIdLiveData(id)

    // 通过 Tag 观察
    val uploadProgress: LiveData<List<WorkInfo>> =
        workManager.getWorkInfosByTagLiveData("upload")
}

// Compose 中观察
@Composable
fun UploadStatus(workId: UUID) {
    val workInfo = WorkManager.getInstance(LocalContext.current)
        .getWorkInfoByIdLiveData(workId)
        .observeAsState()

    when (workInfo.value?.state) {
        WorkInfo.State.RUNNING -> CircularProgressIndicator()
        WorkInfo.State.SUCCEEDED -> {
            val url = workInfo.value?.outputData?.getString("uploaded_url")
            Text("上传成功: $url")
        }
        WorkInfo.State.FAILED -> Text("上传失败")
        else -> {}
    }
}
```

## 6. 前台 Worker（长时间任务）

```kotlin
class LongUploadWorker(context: Context, params: WorkerParameters)
    : CoroutineWorker(context, params) {

    override suspend fun getForegroundInfo(): ForegroundInfo {
        val notification = NotificationCompat.Builder(applicationContext, "upload_channel")
            .setContentTitle("正在上传")
            .setSmallIcon(R.drawable.ic_upload)
            .setProgress(100, 0, true)
            .build()
        return ForegroundInfo(NOTIFICATION_ID, notification)
    }

    override suspend fun doWork(): Result {
        setForeground(getForegroundInfo())
        // 执行长时间任务...
        return Result.success()
    }
}
```

## 7. WorkManager 2.10 / 2.11 版本演进

> 🔄 更新于 2026-05-01（2026-05-31 校准版本）

**WorkManager 2.11.2 是当前稳定版**（androidx maven 实测）。WorkManager 持续改进网络约束和任务追踪能力。来源：[Android Developers](https://developer.android.com/jetpack/androidx/releases/work)

<!-- version-check: WorkManager 2.11.2 stable, checked 2026-05-31 -->
<!-- 修复于 2026-05-31: 原文写"2.10.0 stable + 2.11.0-alpha01"，实测 androidx maven 已发布 2.11.2 stable -->

### 关键更新

- **精细化网络约束**（2.10+）：更精确的网络类型和连接状态判断
- **Generation 追踪**（2.10+）：任务代际追踪，更好地管理周期性任务
- **Flow API**（2.10+）：`getWorkInfoByIdFlow()` 替代 LiveData 版本
- **持续迭代**（2.11）：稳定性与约束处理改进

```kotlin
// WorkManager 2.11.x 依赖
// libs.versions.toml
// [versions]
// work = "2.11.2"
// [libraries]
// androidx-work-runtime = { module = "androidx.work:work-runtime-ktx", version.ref = "work" }

// 2026 推荐：使用 Flow API 替代 LiveData
@Composable
fun UploadStatus(workId: UUID) {
    val workInfo by WorkManager.getInstance(LocalContext.current)
        .getWorkInfoByIdFlow(workId)  // Flow API（2.10+）
        .collectAsStateWithLifecycle(initialValue = null)

    when (workInfo?.state) {
        WorkInfo.State.RUNNING -> CircularProgressIndicator()
        WorkInfo.State.SUCCEEDED -> {
            val url = workInfo?.outputData?.getString("uploaded_url")
            Text("上传成功: $url")
        }
        WorkInfo.State.FAILED -> Text("上传失败")
        else -> {}
    }
}
```
