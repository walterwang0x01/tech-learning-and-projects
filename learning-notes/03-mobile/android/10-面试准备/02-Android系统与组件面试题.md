# Android 系统与组件面试题
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Activity 启动模式

```kotlin
// standard：默认，每次创建新实例
// singleTop：栈顶复用，触发 onNewIntent
// singleTask：栈内复用，清除其上所有 Activity
// singleInstance：独占任务栈

// AndroidManifest.xml
// <activity android:launchMode="singleTask" />

// Intent Flag
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP

// 场景：
// standard → 普通页面
// singleTop → 通知点击打开的页面（避免重复创建）
// singleTask → 首页（返回时清除栈）
// singleInstance → 来电界面（独立任务栈）

// taskAffinity 控制任务栈归属
// <activity android:taskAffinity="com.example.task2" />
```

## 2. Handler 机制

```kotlin
// 核心组件: Looper, MessageQueue, Handler, Message

// 主线程 Looper 在 ActivityThread.main() 中创建
// Looper.prepareMainLooper() → Looper.loop()

// 工作原理:
// 1. Handler.sendMessage() → MessageQueue.enqueueMessage()
// 2. Looper.loop() 不断从 MessageQueue 取消息
// 3. msg.target.dispatchMessage(msg) → Handler.handleMessage()

// 子线程使用 Handler
class WorkerThread : Thread() {
    lateinit var handler: Handler

    override fun run() {
        Looper.prepare()
        handler = Handler(Looper.myLooper()!!) { msg ->
            // 在子线程处理消息
            true
        }
        Looper.loop()
    }
}

// 现代替代方案
// 协程: viewModelScope.launch { }
// Flow: flow { }.flowOn(Dispatchers.IO)

// IdleHandler: 主线程空闲时执行
Looper.myQueue().addIdleHandler {
    doIdleWork()
    false  // false = 执行一次
}
```

## 3. Binder IPC

```kotlin
// Binder 是 Android 跨进程通信的核心机制
// Client → Proxy → Binder Driver(内核) → Stub → Server

// AIDL 定义接口
// IUserService.aidl
// interface IUserService {
//     User getUser(int id);
//     void saveUser(in User user);
// }

// 服务端
class UserService : Service() {
    private val binder = object : IUserService.Stub() {
        override fun getUser(id: Int): User = database.getUser(id)
        override fun saveUser(user: User) { database.save(user) }
    }
    override fun onBind(intent: Intent): IBinder = binder
}

// 客户端
val connection = object : ServiceConnection {
    override fun onServiceConnected(name: ComponentName, service: IBinder) {
        val userService = IUserService.Stub.asInterface(service)
        val user = userService.getUser(1)
    }
    override fun onServiceDisconnected(name: ComponentName) {}
}
bindService(intent, connection, BIND_AUTO_CREATE)
```

## 4. View 绘制流程

```kotlin
// ViewRootImpl.performTraversals() 触发三大流程

// 1. Measure（测量）
// MeasureSpec = Mode + Size
// EXACTLY: match_parent / 固定值
// AT_MOST: wrap_content
// UNSPECIFIED: 不限制

// 2. Layout（布局）
// 确定 View 在父容器中的位置 (left, top, right, bottom)

// 3. Draw（绘制）
// drawBackground → onDraw → dispatchDraw(子View) → onDrawForeground

// requestLayout(): 重新 measure + layout
// invalidate(): 重新 draw（主线程）
// postInvalidate(): 重新 draw（子线程）

// View.post() 为什么能获取宽高？
// 因为 post 的 Runnable 在 performTraversals 之后执行
view.post {
    val width = view.width   // 此时已完成测量
    val height = view.height
}
```

## 5. 事件分发机制

```kotlin
// 分发顺序: Activity → Window → DecorView → ViewGroup → View

// ViewGroup 三个关键方法:
// dispatchTouchEvent(): 分发事件
// onInterceptTouchEvent(): 是否拦截（ViewGroup 独有）
// onTouchEvent(): 处理事件

// 伪代码
fun dispatchTouchEvent(ev: MotionEvent): Boolean {
    var consumed = false
    if (onInterceptTouchEvent(ev)) {
        consumed = onTouchEvent(ev)      // 自己处理
    } else {
        consumed = child.dispatchTouchEvent(ev)  // 传给子 View
    }
    return consumed
}

// 滑动冲突解决
// 外部拦截法（父 View 决定）
override fun onInterceptTouchEvent(ev: MotionEvent): Boolean {
    return when (ev.action) {
        MotionEvent.ACTION_DOWN -> false
        MotionEvent.ACTION_MOVE -> needIntercept(ev)  // 根据条件拦截
        else -> false
    }
}

// 内部拦截法（子 View 决定）
// 子 View: parent.requestDisallowInterceptTouchEvent(true)
```

## 6. Context 类型

```kotlin
// Application Context: 全局单例，生命周期 = 应用
// Activity Context: 随 Activity 销毁
// Service Context: 随 Service 销毁

// 使用原则:
// 启动 Activity → Activity Context
// 弹 Dialog → Activity Context
// 启动 Service → 任意 Context
// 发送广播 → 任意 Context
// 加载资源 → 任意 Context
// 单例中 → Application Context（避免泄漏）
```

> 🔄 更新于 2026-05-02

<!-- version-check: Android 16 API 36, Compose 1.11, checked 2026-05-02 -->

## 7. 2026 年 Android 系统面试新题

```kotlin
// Q: Android 16 QPR2 的 Minor SDK Version 对开发者意味着什么？
// A: 这是 Android 平台演进的重大变化：
// - Google 可以在年度大版本之外发布新 API（QPR2 是首个 Minor SDK 版本）
// - Minor 版本的变更主要是增量的，不引入 targetSdkVersion 行为变更
// - 开发者不需要对 Minor 版本做全面回归测试
// - 安全和无障碍相关的行为变更仍可能包含（如 SMS OTP 保护）

// Q: Compose 1.11 的 Trackpad 事件改进是什么？
// A: 之前 Trackpad 事件被解释为 PointerType.Touch（假触摸），
// 导致点击拖拽时触发滚动而非选择。
// Compose 1.11 将 Trackpad 事件改为 PointerType.Mouse：
// - 点击拖拽 → 选择文本（而非滚动）
// - 支持双指滑动和捏合手势（API 34+）
// - 文本框支持双击/三击选择和桌面风格右键菜单
// 新增 performTrackpadInput 测试 API

// Q: Android 16 的 Predictive Back 有什么变化？
// A: Android 16 强制启用 Predictive Back 动画：
// - 用户从屏幕边缘滑动时可预览返回目标
// - App 必须正确处理 OnBackPressedCallback
// - Fragment 和 Activity 转场需要适配预测性返回动画
```

## 8. 2026 年 Android 17 面试新热点

<!-- version-check: Android 17 API 37 Beta 4 (April 2026), Contact Picker, EyeDropper, MessageQueue rewrite, SMS protection, checked 2026-05-22 -->

> 🔄 更新于 2026-05-22

Android 17（API 37，代号 "Cinnamon Bun"）已于 2026-03 进入 platform stability（Beta 3），Beta 4 为 2026-04 最后一个 Beta，stable 版本预计 2026-06 随 Pixel 设备发布。来源：[Android 17 Release Notes](https://developer.android.com/about/versions/17/release-notes)、[Android 17 Behavior Changes](https://developer.android.com/about/versions/17/behavior-changes-17)

```kotlin
// Q: Android 17 的 Contact Picker 强制对什么场景产生影响？
// A: targetSdk 37+ 应用如果还想直接申请 READ_CONTACTS 权限，
//    必须证明 Contact Picker 不能满足核心功能，否则在 Play Console 提交时会被拒。
// - Contact Picker 是系统级 UI，用户从中选择具体联系人，应用获得选中条目的访问权
// - 类似 Photo Picker 的隐私改造模式
// - 入口：Intent.ACTION_PICK_CONTACTS + EXTRA_REQUESTED_DATA_FIELDS
// - 来源：https://developer.android.com/about/versions/17/features/contact-picker

val pickContactLauncher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    val contactUri = result.data?.data
    // 仅获得选中联系人的访问权，未选中条目无权访问
}

fun launchContactPicker() {
    val intent = Intent(Intent.ACTION_PICK_CONTACTS).apply {
        putStringArrayListExtra(
            Intent.EXTRA_REQUESTED_DATA_FIELDS,
            arrayListOf(
                ContactsContract.CommonDataKinds.Phone.CONTENT_ITEM_TYPE,
                ContactsContract.CommonDataKinds.Email.CONTENT_ITEM_TYPE
            )
        )
    }
    pickContactLauncher.launch(intent)
}

// Q: Android 17 大屏强制适配是什么？为什么对手机 App 也有影响？
// A: targetSdk 37+ 后，开发者无法再通过 manifest 的 resizeableActivity / orientation
//    opt-out 屏幕方向和可调整大小的限制（仅限 sw > 600dp 设备）。
// - 在折叠屏、平板、Chromebook 上必须能自由旋转和调整窗口
// - 强制 ConstraintLayout / WindowSizeClass 自适应布局
// - Material 3 Adaptive 1.2.0 配合 NavigableListDetailPaneScaffold 是推荐方案
// - 来源：https://android-developers.googleblog.com/2026/02/prepare-your-app-for-resizability-and.html

// Q: Android 17 的 EyeDropper API 解决了什么权限问题？
// A: 之前应用想做"屏幕取色"必须申请 MediaProjection（截屏权限），
//    用户不愿授予敏感权限。
// - EyeDropper API 是系统级取色器，由系统 UI 弹出
// - 不需要任何敏感权限，应用获得用户主动选择的像素颜色
// - 适合设计/绘图/Markdown 编辑器场景

// Q: Android 17 的 MessageQueue 重写带来什么开发影响？
// A: Looper / Handler 底层的 MessageQueue 被全面重写：
// - 性能提升（具体数据待 stable 公布）
// - 行为变化：依赖 MessageQueue 内部 IdleHandler 时序的库需要重新验证
// - 受影响场景：自定义 Looper、Choreographer 优化、性能监控库（Matrix、ANR-WatchDog）
// - 来源：https://developer.android.com/about/versions/17/changes/messagequeue

// Q: Android 17 Beta 3 的 SMS 安全增强是什么？
// A: targetSdk 37+ 应用接收 OTP 短信受限制：
// - 系统会自动遮蔽包含验证码的通知预览
// - 后台应用读取 SMS 受限，金融类应用必须用 SmsRetriever API 替代
// - 应对 SMS 钓鱼攻击的延伸防护
// - 来源：https://gagadget.com/en/711274-android-17-beta-3-arrives-on-vivo-x300-pro-and-iqoo-15-with-tighter-sms-security/

// Q: APNs Broadcast Push 和 Android 端的等价方案是什么？
// A: 这是 iOS 26 的能力（向 Live Activities 订阅者批量推送），
//    Android 端没有完全等价的方案，但有以下替代：
// - FCM Topic Messaging：按主题订阅，单次发送给所有订阅者
//    fun subscribeToTopic() {
//        FirebaseMessaging.getInstance().subscribeToTopic("nba-finals-g4")
//    }
// - Firebase Cloud Messaging HTTP v1：单次请求 + topic 模式
// - 区别：iOS APNs Broadcast 限制更严但延迟更稳定，FCM Topic 更灵活但有秒级延迟波动
```
