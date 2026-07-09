# Compose 基础与布局
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. @Composable 基础

```kotlin
// 可组合函数
@Composable
fun Greeting(name: String, modifier: Modifier = Modifier) {
    Text(
        text = "Hello, $name!",
        modifier = modifier.padding(16.dp),
        style = MaterialTheme.typography.headlineMedium
    )
}

// 预览
@Preview(showBackground = true)
@Composable
fun GreetingPreview() {
    MyTheme { Greeting("Android") }
}
```

## 2. 基础组件

```kotlin
// Text
Text(
    text = "标题",
    fontSize = 24.sp,
    fontWeight = FontWeight.Bold,
    color = Color.DarkGray,
    maxLines = 2,
    overflow = TextOverflow.Ellipsis
)

// Image
Image(
    painter = painterResource(R.drawable.photo),
    contentDescription = "照片",
    modifier = Modifier.size(120.dp).clip(CircleShape),
    contentScale = ContentScale.Crop
)

// AsyncImage (Coil)
AsyncImage(
    model = "https://example.com/image.jpg",
    contentDescription = null,
    modifier = Modifier.fillMaxWidth(),
    placeholder = painterResource(R.drawable.placeholder)
)

// Button
Button(
    onClick = { /* 点击事件 */ },
    colors = ButtonDefaults.buttonColors(containerColor = Color.Blue)
) {
    Icon(Icons.Default.Add, contentDescription = null)
    Spacer(Modifier.width(8.dp))
    Text("添加")
}
```

## 3. 布局

```kotlin
// Column（垂直排列）
Column(
    modifier = Modifier.fillMaxSize().padding(16.dp),
    verticalArrangement = Arrangement.spacedBy(8.dp),
    horizontalAlignment = Alignment.CenterHorizontally
) {
    Text("第一行")
    Text("第二行")
}

// Row（水平排列）
Row(
    modifier = Modifier.fillMaxWidth(),
    horizontalArrangement = Arrangement.SpaceBetween,
    verticalAlignment = Alignment.CenterVertically
) {
    Text("左侧")
    IconButton(onClick = {}) { Icon(Icons.Default.ArrowForward, null) }
}

// Box（层叠布局）
Box(modifier = Modifier.size(200.dp)) {
    Image(painter, null, Modifier.matchParentSize())
    Text("覆盖文字", Modifier.align(Alignment.BottomCenter))
}
```

## 4. LazyColumn / LazyRow

```kotlin
@Composable
fun UserList(users: List<User>) {
    LazyColumn(
        contentPadding = PaddingValues(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(users, key = { it.id }) { user ->
            UserCard(user)
        }
        item { Spacer(Modifier.height(80.dp)) }
    }
}

// LazyVerticalGrid
LazyVerticalGrid(
    columns = GridCells.Adaptive(minSize = 128.dp),
    contentPadding = PaddingValues(8.dp)
) {
    items(photos) { photo -> PhotoCard(photo) }
}
```

## 5. Modifier

```kotlin
Modifier
    .fillMaxWidth()
    .padding(horizontal = 16.dp, vertical = 8.dp)
    .clip(RoundedCornerShape(12.dp))
    .background(MaterialTheme.colorScheme.surface)
    .border(1.dp, Color.Gray, RoundedCornerShape(12.dp))
    .clickable { onClick() }
    .shadow(4.dp, RoundedCornerShape(12.dp))
```

## 6. Scaffold 与 Material3

```kotlin
@Composable
fun MainScreen(navController: NavController) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("首页") },
                actions = {
                    IconButton(onClick = {}) { Icon(Icons.Default.Search, "搜索") }
                }
            )
        },
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = true,
                    onClick = {},
                    icon = { Icon(Icons.Default.Home, null) },
                    label = { Text("首页") }
                )
            }
        },
        floatingActionButton = {
            FloatingActionButton(onClick = {}) { Icon(Icons.Default.Add, "添加") }
        }
    ) { padding ->
        LazyColumn(modifier = Modifier.padding(padding)) {
            items(dataList) { item -> ListItem(item) }
        }
    }
}
```
## 🎬 推荐视频资源

- [Philipp Lackner - Jetpack Compose Full Course](https://www.youtube.com/watch?v=cDabx3SjuOY) — Compose完整课程
- [Android Developers - Compose Tutorial](https://www.youtube.com/watch?v=cDabx3SjuOY) — 官方Compose教程
- [Stevdza-San - Jetpack Compose](https://www.youtube.com/@StevdzaSan) — Compose教程频道
### 📺 B站（Bilibili）
- [Jetpack Compose中文教程](https://www.bilibili.com/video/BV1HV4y1a7n4) — Compose入门到实战

### 🌐 其他平台
- [Android官方Compose教程](https://developer.android.com/courses/android-basics-compose/course) — Google官方Compose课程（免费）
- [Jetpack Compose官方文档](https://developer.android.com/develop/ui/compose/documentation) — 官方文档


## 7. Compose 2026 版本演进

<!-- version-check: 见第 8 节最新清单（Compose BOM 2026.06.01, Compose 1.11.4, Navigation 3 1.1.4, Kotlin 2.4.0），本节为版本演进背景，checked 2026-07-08 -->

> 🔄 更新于 2026-05-04（2026-05-18 增补与 CMP 1.11 对齐说明；2026-05-31 注：最新版本以第 8 节清单为准）
>
> ℹ️ 下表为 2026-04 时点的版本快照，用于说明版本演进脉络。**当前最新版本请以第 8 节「Compose BOM 2026.06.01 简明清单」为准。**

### 当前版本

| 组件 | 版本 | 说明 |
|------|------|------|
| Compose BOM | **2026.04.01** | 统一管理所有 Compose 库版本 |
| Compose UI | **1.11.0** | 核心 UI 库（2026-04 稳定） |
| Material3 | **1.4.x** | Material Design 3 组件 |
| Compose Compiler | 与 Kotlin 对齐 | Kotlin 2.0+ 内置，无需单独指定版本 |
| Navigation3 | **1.1.1** | Compose-first 导航库（稳定） |
| Compose Multiplatform | **1.11.0** | 与 Jetpack Compose 1.11 对齐（2026-05-15）|

### Compose 1.11 新特性（2026-04）

**测试 API v2 成为默认**：`StandardTestDispatcher` 替代 `UnconfinedTestDispatcher`，协程在测试中排队执行而非立即执行，更接近生产行为，减少 flaky 测试。

**共享元素调试工具**：`LookaheadAnimationVisualDebugging` 可视化共享元素过渡的目标边界、动画轨迹和匹配状态。

```kotlin
// 在 Compose 1.11 中调试共享元素过渡
SharedTransitionLayout(
    modifier = Modifier.lookaheadAnimationVisualDebugging(
        enabled = BuildConfig.DEBUG  // 仅 debug 包启用
    )
) {
    AnimatedContent(targetState = state) { targetState ->
        when (targetState) {
            is State.List -> ListScreen(...)
            is State.Detail -> DetailScreen(...)
        }
    }
}
```

**触控板事件改进**：触控板事件现在被识别为 `PointerType.Mouse`（之前是 `PointerType.Touch`），支持双指滑动和捏合手势。这条变更同步出现在 Compose Multiplatform 1.11 中，桌面与折叠屏的多指手势行为不再依赖额外适配。

来源：[Jetpack Compose April '26 Release](https://android-developers.googleblog.com/2026/04/jetpack-compose-april-2026-updates.html)、[Compose Multiplatform 1.11.0](https://blog.jetbrains.com/kotlin/2026/05/compose-multiplatform-1-11-0/)

### Compose Compiler 变化（Kotlin 2.0+）

```kotlin
// Kotlin 2.0 之前：Compose Compiler 是独立的 Kotlin 编译器插件
// Kotlin 2.0 之后：Compose Compiler 集成到 Kotlin Gradle 插件中

// build.gradle.kts
plugins {
    alias(libs.plugins.kotlin.android)
    alias(libs.plugins.compose.compiler)  // 新增
}

// 不再需要 composeOptions 块
// Compose Compiler 版本自动与 Kotlin 版本对齐
```

### 强类型资源（Compose 1.7+）

```kotlin
// 类型安全的资源访问（替代 R.string / R.drawable）
// 需要在 build.gradle.kts 中启用
android {
    buildFeatures {
        compose = true
    }
}

// 使用
@Composable
fun Greeting() {
    Text(text = stringResource(Res.string.greeting))
    Image(painter = painterResource(Res.drawable.logo), contentDescription = null)
}
```

> 来源：[Compose BOM](https://developer.android.com/develop/ui/compose/bom)、[Compose Releases](https://developer.android.com/jetpack/androidx/releases/compose)

## 8. Compose May 2026 与 Material 3 Expressive

> 🔄 更新于 2026-05-20

<!-- version-check: Compose BOM 2026.06.01 (latest), Compose 1.11.4, Kotlin 2.4.0, AGP 8.5.2+, Material3 Adaptive 1.2.0, checked 2026-07-08 -->

### Compose Material3 Adaptive 1.2.0 稳定（2026-05-06）

`androidx.compose.material3.adaptive` 系列推进到 **1.2.0 stable**，是面向折叠屏 / 平板 / 大屏 ChromeOS 的官方自适应布局库。来源：[Compose Material3 Adaptive Releases](https://developer.android.com/jetpack/androidx/releases/compose-material3-adaptive)

```kotlin
// build.gradle.kts — Compose BOM 2026.06 + Adaptive 1.2.0 + Kotlin 2.4.0
dependencies {
    implementation(platform("androidx.compose:compose-bom:2026.06.01"))
    implementation("androidx.compose.material3:material3")

    // Adaptive layout（折叠/平板/大屏）
    implementation("androidx.compose.material3.adaptive:adaptive:1.2.0")
    implementation("androidx.compose.material3.adaptive:adaptive-layout:1.2.0")
    implementation("androidx.compose.material3.adaptive:adaptive-navigation:1.2.0")

    // Material 3 Expressive 视觉风格
    implementation("androidx.compose.material3:material3-window-size-class")
}
```

```kotlin
// 使用 NavigableListDetailPaneScaffold 自动适配 list-detail 布局
@OptIn(ExperimentalMaterial3AdaptiveApi::class)
@Composable
fun MyApp() {
    val navigator = rememberListDetailPaneScaffoldNavigator<UserId>()

    NavigableListDetailPaneScaffold(
        navigator = navigator,
        listPane = {
            UserListScreen(
                onUserClick = { userId ->
                    navigator.navigateTo(ListDetailPaneScaffoldRole.Detail, userId)
                }
            )
        },
        detailPane = {
            val userId = navigator.currentDestination?.contentKey
            userId?.let { UserDetailScreen(it) }
        }
    )
    // 手机：单栏覆盖；平板/折叠屏：list + detail 双栏
}
```

### Material 3 Expressive 设计语言

Material 3 Expressive 是 Google I/O 2026 公布的新视觉系统，核心是 **流体动画 + 鲜活配色 + 触觉反馈**，与 iOS 26 Liquid Glass 形成对照（iOS 强调半透明玻璃质感，Android 强调情绪化的运动）。来源：[Google's Material 3 Expressive Redesign](https://www.androidsage.com/2026/05/13/google-material-3-expressive-redesign-with-gemini-intelligence-for-android/)、[Gemini 3.5 Arrives alongside Neural Expressive design](https://eftm.com/2026/05/google-i-o-keynote-gemini-3-5-arrives-alongside-neural-expressive-design-275940)

落地路径：Compose Material3 **1.4.0** 已稳定引入 Expressive 主题 token；`MaterialExpressiveTheme` 包装器随 Compose BOM **2026.06.01** 全量可用。当前最稳的做法是：

```kotlin
// 当前可用的 expressive 风格触觉反馈（2026-05）
import androidx.compose.material3.MaterialTheme
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalHapticFeedback

@Composable
fun ExpressiveButton(onClick: () -> Unit, content: @Composable () -> Unit) {
    val haptic = LocalHapticFeedback.current
    Button(
        onClick = {
            // M3 Expressive 强调"按下立即反馈"，先触觉再处理点击
            haptic.performHapticFeedback(HapticFeedbackType.LongPress)
            onClick()
        }
    ) { content() }
}
```

### Compose BOM 2026.06.01 简明清单

| 组件 | 版本 |
|------|------|
| Compose UI / Foundation / Animation | **1.11.4** |
| Material3 | **1.4.0** |
| Material3 Adaptive | **1.2.0 stable**（2026-05-06）|
| Lifecycle Compose | **2.11.0** |
| Navigation Compose | **2.9.8** |
| Navigation 3 | **1.1.4 stable** |
| Kotlin | **2.4.0**（Compose Compiler 内置，无需单独指定）|
| AGP | **≥ 8.5.2**（compileSdk 37 推荐）|
| Hilt Navigation Compose | **1.4.0**（按需引入）|

### Kotlin 2.4.0 与 Compose 工具链

Kotlin **2.4.0**（2026-06-03 stable）移除 K1 前端，Compose Compiler 与之紧耦合；升级前确保 AGP **≥ 8.5.2**，`compileSdk` 建议 **37**（Android 17 stable）。来源：[What's new in Kotlin 2.4.0](https://kotlinlang.org/docs/whatsnew24.html)

```kotlin
// build.gradle.kts（根项目）
plugins {
    alias(libs.plugins.android.application) version "8.5.2" apply false
    alias(libs.plugins.kotlin.android) version "2.4.0" apply false
    alias(libs.plugins.compose.compiler) apply false
}
```

### 升级建议

| 当前 BOM | 建议路径 |
|----------|----------|
| 2026.03.00 / 2026.04.00 / 2026.05.x | 直接升 2026.06.01（无 Breaking） |
| 2026.06.00 / 2026.06.01 | 持续保持；Material 3 Expressive 主题 token 已随 BOM 2026.06 GA |
| Kotlin 2.3.x | 先升 AGP 8.5.2+，再升 Kotlin 2.4.0，最后升 BOM 2026.06.01 |
| 不使用 Adaptive | 在折叠屏 / 平板 / Chromebook 项目中**强烈建议**引入 `material3-adaptive` 1.2.0 |

> 更新于 2026-07-09

**Android 17 stable + Kotlin 2.4.0 联调要点**（2026-07）：

- `compileSdk = 37` 对齐 Android 17；`targetSdk` 升级需验证新权限模型
- Compose BOM **2026.06.01** 与 Kotlin 2.4.0 编译器版本锁定，不可混用旧 BOM
- K1 已移除：检查自定义 compiler plugin 是否支持 K2

> 来源：[Kotlin 2.4.0 发布](https://blog.jetbrains.com/kotlin/2026/06/kotlin-2-4-0-released/)、[Compose BOM 2026.06](https://developer.android.com/jetpack/compose/bom)
