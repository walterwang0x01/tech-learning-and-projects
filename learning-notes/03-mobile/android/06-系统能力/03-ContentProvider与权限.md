# ContentProvider 与权限
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. ContentProvider 基础

```kotlin
class NoteProvider : ContentProvider() {
    private lateinit var db: AppDatabase

    companion object {
        const val AUTHORITY = "com.example.app.provider"
        val CONTENT_URI: Uri = Uri.parse("content://$AUTHORITY/notes")
    }

    override fun onCreate(): Boolean {
        db = Room.databaseBuilder(context!!, AppDatabase::class.java, "notes.db").build()
        return true
    }

    override fun query(uri: Uri, projection: Array<String>?, selection: String?,
                       selectionArgs: Array<String>?, sortOrder: String?): Cursor {
        val cursor = db.openHelper.readableDatabase
            .query("SELECT * FROM notes ORDER BY ${sortOrder ?: "id DESC"}")
        cursor.setNotificationUri(context!!.contentResolver, uri)
        return cursor
    }

    override fun insert(uri: Uri, values: ContentValues?): Uri {
        val id = db.openHelper.writableDatabase
            .insert("notes", SQLiteDatabase.CONFLICT_REPLACE, values!!)
        context!!.contentResolver.notifyChange(uri, null)
        return ContentUris.withAppendedId(CONTENT_URI, id)
    }

    override fun update(uri: Uri, values: ContentValues?, sel: String?, args: Array<String>?) = 0
    override fun delete(uri: Uri, sel: String?, args: Array<String>?) = 0
    override fun getType(uri: Uri) = "vnd.android.cursor.dir/vnd.example.notes"
}
```

## 2. 运行时权限

```kotlin
// Compose 方式
@Composable
fun CameraScreen() {
    val cameraPermissionState = rememberPermissionState(Manifest.permission.CAMERA)

    when {
        cameraPermissionState.status.isGranted -> CameraPreview()
        cameraPermissionState.status.shouldShowRationale -> {
            AlertDialog(
                onDismissRequest = {},
                title = { Text("需要相机权限") },
                text = { Text("拍照功能需要相机权限") },
                confirmButton = {
                    Button(onClick = { cameraPermissionState.launchPermissionRequest() }) {
                        Text("授权")
                    }
                }
            )
        }
        else -> {
            Button(onClick = { cameraPermissionState.launchPermissionRequest() }) {
                Text("请求相机权限")
            }
        }
    }
}

// 多权限
@Composable
fun LocationScreen() {
    val permissionState = rememberMultiplePermissionsState(
        listOf(
            Manifest.permission.ACCESS_FINE_LOCATION,
            Manifest.permission.ACCESS_COARSE_LOCATION
        )
    )

    LaunchedEffect(Unit) {
        if (!permissionState.allPermissionsGranted) {
            permissionState.launchMultiplePermissionRequest()
        }
    }
}
```

## 3. Activity Result API 方式

```kotlin
class PhotoActivity : AppCompatActivity() {
    private val requestPermission = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val allGranted = permissions.values.all { it }
        if (allGranted) startCamera()
        else handleDenied(permissions)
    }

    private fun checkAndRequestPermissions() {
        val needed = arrayOf(
            Manifest.permission.CAMERA,
            Manifest.permission.WRITE_EXTERNAL_STORAGE
        ).filter {
            ContextCompat.checkSelfPermission(this, it) != PackageManager.PERMISSION_GRANTED
        }
        if (needed.isEmpty()) startCamera()
        else requestPermission.launch(needed.toTypedArray())
    }
}
```

## 4. FileProvider

```kotlin
// AndroidManifest.xml
// <provider
//     android:name="androidx.core.content.FileProvider"
//     android:authorities="${applicationId}.fileprovider"
//     android:exported="false"
//     android:grantUriPermissions="true">
//     <meta-data
//         android:name="android.support.FILE_PROVIDER_PATHS"
//         android:resource="@xml/file_paths" />
// </provider>

// res/xml/file_paths.xml
// <paths>
//     <external-path name="images" path="Pictures/" />
//     <cache-path name="cache" path="/" />
// </paths>

// 使用 FileProvider 分享文件
fun shareImage(context: Context, file: File) {
    val uri = FileProvider.getUriForFile(
        context, "${context.packageName}.fileprovider", file
    )
    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "image/*"
        putExtra(Intent.EXTRA_STREAM, uri)
        addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }
    context.startActivity(Intent.createChooser(intent, "分享图片"))
}
```

## 5. Android 17 Contact Picker 与通讯录权限新政策

> 🔄 更新于 2026-05-11

<!-- version-check: Android 17 Contact Picker API 37, READ_CONTACTS policy, checked 2026-05-11 -->

Android 17（API 37）引入**系统级 Contact Picker**，并配合 Google Play 2026-04-15 生效的 Contacts Permissions 政策，从根本上改变了应用访问通讯录的方式。面向 targetSdk 37+ 的应用受影响最大。来源：[Android 17 Contact Picker](https://developer.android.com/about/versions/17/features/contact-picker)、[Google Play Policy Announcement](https://support.google.com/googleplay/android-developer/answer/16926792)

### 5.1 政策核心变化

| 维度 | Android 16 及之前 | Android 17+ 新政策 |
| ---- | ----------------- | ------------------ |
| 默认方式 | `READ_CONTACTS` 全量读取 | Contact Picker 按需选择 |
| 授权粒度 | 全部通讯录 or 拒绝 | 用户选择具体联系人 + 字段（手机/邮箱） |
| 政策要求 | 无强制限制 | 不需要完整通讯录的应用必须改用 Picker |
| `READ_CONTACTS` 使用 | 自由申请 | 仅核心功能无法通过 Picker 实现时才允许 |
| 触发时机 | 2026-04-15 政策生效 | targetSdk 37+ 的应用 |

### 5.2 Contact Picker 调用示例（推荐新方式）

```kotlin
// 使用 Android 17 系统 Contact Picker（无需 READ_CONTACTS 权限）
class InviteActivity : ComponentActivity() {

    // 注册 Contact Picker 结果回调
    private val pickContact = registerForActivityResult(
        ActivityResultContracts.PickContact()
    ) { contactUri: Uri? ->
        contactUri?.let { uri ->
            // 仅能访问用户明确选择的联系人
            contentResolver.query(uri, null, null, null, null)?.use { cursor ->
                if (cursor.moveToFirst()) {
                    val nameIndex = cursor.getColumnIndex(
                        ContactsContract.Contacts.DISPLAY_NAME
                    )
                    val name = cursor.getString(nameIndex)
                    // 处理单个联系人
                }
            }
        }
    }

    fun onInviteClick() {
        // 无需权限检查，系统 UI 由用户控制数据共享范围
        pickContact.launch(null)
    }
}
```

### 5.3 从 READ_CONTACTS 迁移到 Contact Picker

需要迁移的场景：分享邀请、一次性联系人查找、单次选择。

仍可保留 READ_CONTACTS 的场景：通讯录管理应用、系统级同步、备份恢复等核心功能无法通过 Picker 实现的用例。

```kotlin
// 旧做法：申请全量通讯录权限（Android 17+ 面临政策风险）
private val requestPermission = registerForActivityResult(
    ActivityResultContracts.RequestPermission()
) { granted ->
    if (granted) {
        loadAllContacts()  // 全量读取
    }
}

// 新做法：改用 Contact Picker，用户按需授权
private val pickContact = registerForActivityResult(
    ActivityResultContracts.PickContact()
) { uri ->
    uri?.let { handleSelectedContact(it) }
}

// 在 AndroidManifest.xml 中移除（targetSdk 37+）
// <uses-permission android:name="android.permission.READ_CONTACTS" />
```

### 5.4 Play Console 预审检查（2026-10-27 生效）

Play Console 将引入提交前预审，自动检测违反 Contacts 与 Location 权限政策的应用。应用必须在提交前修复才能通过审核。来源：[Help Net Security 2026-04-16](https://www.helpnetsecurity.com/2026/04/16/google-play-store-policy-updates/)

### 5.5 2026 年权限最小化策略

```
Android 权限申请决策树（2026）：
│
├─ 是否是"一次性"操作（邀请、分享）？
│   └─ 是 → 使用 Contact Picker / Sharesheet，不申请权限 ✓
│
├─ 是否需要持续访问同步？
│   ├─ 是 → 声明 READ_CONTACTS（需通过政策审核）
│   └─ 否 → 改用系统 Picker
│
└─ 是否涉及健康数据（心率、运动）？
    └─ 使用 Android 16+ 细粒度权限（如 READ_HEART_RATE
       替代广义 BODY_SENSORS）
```

### 5.6 与其他 2026 隐私政策联动

- **Accessibility API**：禁止用于"自主发起、规划、执行操作"（2026 新政，影响 Accessibility Agent 类应用）
- **Location 精确位置**：推荐使用"位置按钮"作为最小授权范围
- **Account Transfer**：必须走 Play Console 官方"转移所有权"流程

来源：[Google Play Updated Policies 2026-04](https://android-developers.googleblog.com/2026/04/giving-users-clearer-choice-and-everyone-a-safer-more-trusted-app-ecosystem.html)
