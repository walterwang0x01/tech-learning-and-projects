# Activity 与 Fragment 生命周期
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Activity 生命周期

```kotlin
class MainActivity : AppCompatActivity() {
    // 完整生命周期: onCreate → onStart → onResume → onPause → onStop → onDestroy
    // 可见: onStart ~ onStop
    // 前台: onResume ~ onPause

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        // 初始化 UI、恢复状态
        savedInstanceState?.let {
            val query = it.getString("search_query", "")
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putString("search_query", currentQuery)
    }

    override fun onStart() { super.onStart(); /* 注册监听 */ }
    override fun onResume() { super.onResume(); /* 恢复动画/传感器 */ }
    override fun onPause() { super.onPause(); /* 暂停动画 */ }
    override fun onStop() { super.onStop(); /* 释放资源 */ }
    override fun onDestroy() { super.onDestroy(); /* 最终清理 */ }
}
```

## 2. Fragment 生命周期

```kotlin
class UserFragment : Fragment(R.layout.fragment_user) {
    // onAttach → onCreate → onCreateView → onViewCreated → onStart → onResume
    // → onPause → onStop → onDestroyView → onDestroy → onDetach

    private var _binding: FragmentUserBinding? = null
    private val binding get() = _binding!!

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        _binding = FragmentUserBinding.bind(view)
        setupUI()
        observeData()
    }

    private fun observeData() {
        viewLifecycleOwner.lifecycleScope.launch {
            repeatOnLifecycle(Lifecycle.State.STARTED) {
                viewModel.uiState.collect { updateUI(it) }
            }
        }
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null  // 防止内存泄漏
    }
}
```

## 3. 配置变更处理

```kotlin
// 方式一：ViewModel 保存数据（推荐）
class SearchViewModel : ViewModel() {
    var searchQuery = ""  // 配置变更后自动保留
}

// 方式二：声明处理特定配置变更
// AndroidManifest.xml:
// android:configChanges="orientation|screenSize|keyboardHidden"
override fun onConfigurationChanged(newConfig: Configuration) {
    super.onConfigurationChanged(newConfig)
    if (newConfig.orientation == Configuration.ORIENTATION_LANDSCAPE) {
        // 横屏处理
    }
}

// 方式三：rememberSaveable（Compose）
var text by rememberSaveable { mutableStateOf("") }
```

## 4. Activity Result API

```kotlin
class PhotoFragment : Fragment() {
    // 替代 startActivityForResult
    private val pickImage = registerForActivityResult(
        ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let { loadImage(it) }
    }

    private val requestPermission = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) openCamera() else showPermissionDenied()
    }

    private val takePicture = registerForActivityResult(
        ActivityResultContracts.TakePicturePreview()
    ) { bitmap ->
        bitmap?.let { showPreview(it) }
    }

    fun onPickImageClick() { pickImage.launch("image/*") }
    fun onCameraClick() { requestPermission.launch(Manifest.permission.CAMERA) }
}
```

## 5. Fragment 通信

```kotlin
// 方式一：共享 ViewModel
class SharedViewModel : ViewModel() {
    val selectedItem = MutableStateFlow<Item?>(null)
}

class ListFragment : Fragment() {
    private val sharedVm: SharedViewModel by activityViewModels()
    fun onItemClick(item: Item) { sharedVm.selectedItem.value = item }
}

class DetailFragment : Fragment() {
    private val sharedVm: SharedViewModel by activityViewModels()
}

// 方式二：Fragment Result API
// 发送
parentFragmentManager.setFragmentResult("requestKey", bundleOf("data" to "value"))

// 接收
parentFragmentManager.setFragmentResultListener("requestKey", viewLifecycleOwner) { _, bundle ->
    val result = bundle.getString("data")
}
```

> 🔄 更新于 2026-04-23

## 6. Android 16 (API 36) 行为变化

<!-- version-check: Android 16 API 36, Activity behavior changes, checked 2026-04-23 -->

Android 16 对 Activity 和窗口行为引入了多项强制性变化，面向 targetSdk 36 的应用必须适配。来源：[Android 16 Behavior Changes](https://developer.android.com/about/versions/16/behavior-changes-16)

### 6.1 Edge-to-Edge 强制启用

```kotlin
// Android 15 中可以通过以下方式 opt-out：
// R.attr.windowOptOutEdgeToEdgeEnforcement = true
// ⚠️ Android 16 中此属性已废弃且无效！

// 正确做法：适配 edge-to-edge
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // enableEdgeToEdge() 在 API 36 中已默认启用
        enableEdgeToEdge()

        setContent {
            // 使用 WindowInsets 处理系统栏
            Scaffold(
                modifier = Modifier.fillMaxSize(),
                contentWindowInsets = WindowInsets(0) // 自行处理 insets
            ) { innerPadding ->
                Content(modifier = Modifier.padding(innerPadding))
            }
        }
    }
}
```

### 6.2 Predictive Back 默认启用

```kotlin
// Android 16 中 predictive back 系统动画默认启用：
// - back-to-home 动画
// - cross-task 动画
// - cross-activity 动画

// 如果使用自定义返回逻辑，必须迁移到 OnBackPressedCallback
class MyFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // ✅ 正确：使用 OnBackPressedCallback
        requireActivity().onBackPressedDispatcher.addCallback(
            viewLifecycleOwner
        ) {
            // 自定义返回逻辑
            if (hasUnsavedChanges) {
                showSaveDialog()
            } else {
                isEnabled = false
                requireActivity().onBackPressedDispatcher.onBackPressed()
            }
        }
    }
}
```

### 6.3 大屏幕适配

```
Android 16 大屏幕变化：
├─ 限制屏幕方向和可调整大小的能力被逐步移除
├─ 应用必须支持任意窗口大小和宽高比
├─ 多窗口模式成为标准行为
└─ 建议使用 WindowSizeClass 适配不同屏幕
```

## 7. Android 17 (API 37) 行为变化

> 🔄 更新于 2026-05-18

<!-- version-check: Android 17 API 37 "Cinnamon Bun", Beta 4, stable June 2026 expected, checked 2026-05-18 -->

Android 17（内部代号 **Cinnamon Bun**，API 37）已于 2026-03 进入 Beta 3 平台稳定阶段，API 表面冻结；Beta 4（2026-04）增加了 app 内存限制等运行时变化，**正式稳定版预计 2026-06 发布**。来源：[The Third Beta of Android 17](https://android-developers.googleblog.com/2026/03/the-third-beta-of-android-17.html)、[Android 17 Behavior Changes](https://developer.android.com/about/versions/17/behavior-changes-17)

### 7.1 lock-free MessageQueue 与 main looper 行为

```kotlin
// Android 17 中 android.os.MessageQueue 改为 lock-free 实现
// 性能提升 + 减少丢帧，但反射访问私有字段/方法的代码会失效

// ⚠️ 反模式：用反射读取 MessageQueue 私有字段
val mq = Looper.getMainLooper().queue
val field = MessageQueue::class.java.getDeclaredField("mMessages")  // API 37 上可能为 null 或不存在

// ✅ 正确做法：使用公开 API
Looper.getMainLooper().queue.addIdleHandler {
    // 处理空闲队列
    false
}
```

> 老旧的卡顿监测库（早期 BlockCanary）依赖反射访问 `mMessages` 链表，**面向 targetSdk 37 的应用必须升级到使用公开 API 的版本**，否则在 Android 17 设备上无法启动卡顿监测。

### 7.2 隐私优先的 Contact Picker

```kotlin
// Android 17 引入系统级 Contact Picker，不再需要 READ_CONTACTS 权限
// Google Play 政策（2026-04-15 生效）要求：仅在确实需要全量通讯录时声明 READ_CONTACTS

// ✅ 推荐：用 Contact Picker 让用户主动选择联系人
val pickContact = registerForActivityResult(
    ActivityResultContracts.PickContact()
) { contactUri ->
    // 用户主动选择的联系人 URI
    contactUri ?: return@registerForActivityResult
    // 读取选中联系人的字段
}

// 触发选择
pickContact.launch(null)
```

来源：[Privacy-First Contact Sharing](https://android-developers.googleblog.com/2026/03/contact-picker-privacy-first-contact.html)、[Boosting User Privacy with Updated Play Policies](https://android-developers.googleblog.com/2026/04/giving-users-clearer-choice-and-everyone-a-safer-more-trusted-app-ecosystem.html)

### 7.3 应用内存限制（Beta 4 引入）

```kotlin
// Android 17 Beta 4 引入运行时内存限制，超限的应用会被系统终止
// 终止描述会写入 ApplicationExitInfo

class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        val activityManager = getSystemService(ACTIVITY_SERVICE) as ActivityManager
        val exitReasons = activityManager.getHistoricalProcessExitReasons(packageName, 0, 5)

        for (info in exitReasons) {
            // 检查是否被新内存限制器杀死
            if (info.description?.contains("MemoryLimiter") == true) {
                // 上报异常，触发降级（停止预加载、清理缓存等）
                reportMemoryKill(info)
            }
        }
    }
}
```

来源：[Android 17 Release Notes — Beta 4](https://developer.android.com/about/versions/17/release-notes)

### 7.4 加速发布周期

Google 官宣 Android 17 缩短开发周期：跳过传统 "Developer Preview" 阶段，直接以公开 Beta 起步，**目标是与 H1 硬件发布对齐**。这意味着应用团队的合规节奏从过去的"Q4 适配"变成"Q2 适配"。来源：[Wikipedia: Android 17](https://en.wikipedia.org/wiki/Android_17)

### 7.5 适配优先级建议（2026 H2）

| 优先级 | 项目 | 风险 |
|--------|------|------|
| ⭐️⭐️⭐️ | targetSdk = 37 + Contact Picker 适配 | Play 政策硬要求 |
| ⭐️⭐️⭐️ | 移除 MessageQueue 反射 / 升级卡顿监测库 | Crash 风险 |
| ⭐️⭐️ | 内存敏感场景增加 ApplicationExitInfo 监控 | 用户感知 ANR/Kill |
| ⭐️⭐️ | OTP 延迟保护（前台敏感字段读取行为） | UX 差异 |
| ⭐️ | 系统级 Bubbles + Cross-device task handoff | 平板/折叠屏体验 |

## 8. Android 17 Stable 跟进与 Material 3 Expressive

> 🔄 更新于 2026-05-20

<!-- version-check: Android 17 API 37 stable expected June 2026, Material 3 Expressive, Google I/O 2026, checked 2026-05-20 -->

Google I/O 2026（2026-05-19 至 05-20）正式公布 Android 17 的最终特性集和 Pixel/Galaxy 首批落地计划。稳定版仍按节奏在 **2026-06** 发布到 AOSP，Pixel/Galaxy 的 Gemini Intelligence 套件作为 OEM 增量功能在夏季陆续推送。来源：[Android Show 2026 — The Verge](https://www.theverge.com/tech/928624/android-show-2026-all-the-news-and-announcements)、[Android 17 Release Date — Tech Advisor](https://www.techadvisor.com/article/3122614/android-17-release-date-new-features-eligible-phones.html)

### 8.1 与开发者直接相关的 12 项新特性

| 类别 | 特性 | 对应用的影响 |
|------|------|--------------|
| 多任务 | App Bubbles（系统级悬浮气泡） | 需要适配 `Notification.BubbleMetadata`，类似 iOS Picture-in-Picture |
| 输入法 | Rambler 语音转写 | 系统级，无需应用集成；建议优化 `EditText` 的语音输入兼容 |
| 桌面 | AI 自定义 Widget（Gemini 生成） | Glance Widget 必须正确暴露 `WidgetMetadata` 才能被 AI 索引 |
| 数字健康 | Pause Point（防止刷屏） | 系统级提示，应用不强制改造，但视频/Feed 流可主动尊重 |
| 安全 | Banker Impersonator 防护 | 短信/呼叫权限审查更严，金融 App 需在权限提示中说明用途 |
| 隐私 | One-time location（精细化） | `ACCESS_FINE_LOCATION` 用户可选 "仅这一次精确" |
| 游戏 | Native controller remapping | `InputDevice` 新 API，游戏 App 应不再硬编码按键映射 |
| 多设备 | Quick Share / AirDrop 互通 | 通过系统 Share Sheet 即可，无需修改应用代码 |
| 输入 | EyeDropper API（Beta 2 引入） | 颜色选择、设计工具类应用可直接使用 |
| 大屏 | 强制移除 orientation/resizability opt-out | sw > 600dp 设备必须支持横竖屏，影响 Activity 配置 |
| 视觉 | 3D Emoji | 系统级，emoji 渲染会自动升级 |
| 安全 | 系统级 Anti-Theft 持续模式 | Lock screen 与 SIM 绑定增强 |

### 8.2 Material 3 Expressive 设计语言

**Material 3 Expressive** 是 Android 17 的视觉重设计，与 iOS 26 Liquid Glass 在设计哲学上互为对照——但 M3 Expressive 强调"流体动画 + 鲜活配色 + 触觉反馈"，而非 iOS 的"半透明玻璃"。Gemini App、Google Tasks、Pixel 系统 UI 已开始采用。来源：[Google's Material 3 Expressive Redesign](https://www.androidsage.com/2026/05/13/google-material-3-expressive-redesign-with-gemini-intelligence-for-android/)

```kotlin
// Compose Material3 Adaptive 1.2.0（2026-05-06 stable）配合 M3 Expressive
// build.gradle.kts
dependencies {
    implementation(platform("androidx.compose:compose-bom:2026.05.00"))
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material3.adaptive:adaptive:1.2.0")
    implementation("androidx.compose.material3.adaptive:adaptive-layout:1.2.0")
}
```

### 8.3 适配优先级建议（2026 H2 修订）

| 优先级 | 项目 | 来源 |
|--------|------|------|
| ⭐️⭐️⭐️ | targetSdk = 37 + Contact Picker | Play 政策硬要求（2026-04-15 已生效） |
| ⭐️⭐️⭐️ | 移除 MessageQueue 反射 / 升级卡顿监测库 | Android 17 lock-free MessageQueue |
| ⭐️⭐️⭐️ | sw > 600dp 设备适配横竖屏 | API 37 移除 opt-out |
| ⭐️⭐️ | App Bubbles + Notification.BubbleMetadata | 多任务 UX 跃升 |
| ⭐️⭐️ | Glance Widget 暴露元数据 | AI 自定义 Widget 索引 |
| ⭐️⭐️ | 内存敏感场景增加 ApplicationExitInfo 监控 | Beta 4 内存限制器 |
| ⭐️ | Material 3 Expressive 视觉适配 | 视觉一致性，非阻塞 |
| ⭐️ | 系统级 Bubbles + Cross-device task handoff | 平板/折叠屏体验 |

> 工具链节奏：iOS 27 在 2026-04-28 强制 SDK 26 与 UIScene；Android 17 强制 targetSdk 36（Play 政策）已先行落地，targetSdk 37 适配窗口为 2026-06 至 2026-09。
