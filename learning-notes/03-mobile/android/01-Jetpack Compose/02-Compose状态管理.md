# Compose 状态管理
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. remember 与 mutableStateOf

```kotlin
@Composable
fun Counter() {
    // 重组时保留状态
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) {
        Text("点击次数: $count")
    }
}

// remember 缓存计算结果
@Composable
fun FilteredList(items: List<String>, query: String) {
    val filtered = remember(items, query) {
        items.filter { it.contains(query, ignoreCase = true) }
    }
    LazyColumn {
        items(filtered) { Text(it) }
    }
}
```

## 2. rememberSaveable

```kotlin
// 配置变更（旋转屏幕）后保留状态
@Composable
fun InputForm() {
    var text by rememberSaveable { mutableStateOf("") }

    OutlinedTextField(
        value = text,
        onValueChange = { text = it },
        label = { Text("用户名") }
    )
}

// 自定义 Saver
data class City(val name: String, val country: String)

val CitySaver = run {
    val nameKey = "name"
    val countryKey = "country"
    mapSaver(
        save = { mapOf(nameKey to it.name, countryKey to it.country) },
        restore = { City(it[nameKey] as String, it[countryKey] as String) }
    )
}

@Composable
fun CityScreen() {
    var city by rememberSaveable(stateSaver = CitySaver) {
        mutableStateOf(City("北京", "中国"))
    }
}
```

## 3. State Hoisting（状态提升）

```kotlin
// 无状态组件
@Composable
fun SearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    modifier: Modifier = Modifier
) {
    OutlinedTextField(
        value = query,
        onValueChange = onQueryChange,
        modifier = modifier.fillMaxWidth(),
        placeholder = { Text("搜索...") },
        leadingIcon = { Icon(Icons.Default.Search, null) }
    )
}

// 有状态的父组件
@Composable
fun SearchScreen(viewModel: SearchViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    Column {
        SearchBar(
            query = uiState.query,
            onQueryChange = viewModel::onQueryChange
        )
        SearchResults(results = uiState.results)
    }
}
```

## 4. derivedStateOf

```kotlin
@Composable
fun TodoList(todos: List<Todo>) {
    // 仅在计算结果变化时触发重组
    val completedCount by remember(todos) {
        derivedStateOf { todos.count { it.isCompleted } }
    }

    val listState = rememberLazyListState()
    val showButton by remember {
        derivedStateOf { listState.firstVisibleItemIndex > 0 }
    }

    Scaffold(
        floatingActionButton = {
            if (showButton) {
                FloatingActionButton(onClick = { /* 回到顶部 */ }) {
                    Icon(Icons.Default.KeyboardArrowUp, null)
                }
            }
        }
    ) { padding ->
        Column(Modifier.padding(padding)) {
            Text("已完成: $completedCount / ${todos.size}")
            LazyColumn(state = listState) {
                items(todos) { TodoItem(it) }
            }
        }
    }
}
```

## 5. Side Effects

```kotlin
// LaunchedEffect：在组合中启动协程
@Composable
fun UserProfile(userId: String, viewModel: UserViewModel = hiltViewModel()) {
    LaunchedEffect(userId) {
        viewModel.loadUser(userId)  // userId 变化时重新加载
    }
}

// DisposableEffect：需要清理的副作用
@Composable
fun LocationTracker(onLocationUpdate: (Location) -> Unit) {
    val context = LocalContext.current
    DisposableEffect(Unit) {
        val locationManager = context.getSystemService<LocationManager>()
        val listener = LocationListener { onLocationUpdate(it) }
        locationManager?.requestLocationUpdates(GPS_PROVIDER, 1000, 10f, listener)
        onDispose {
            locationManager?.removeUpdates(listener)
        }
    }
}

// SideEffect：每次重组后执行
@Composable
fun AnalyticsScreen(screenName: String) {
    val analytics = LocalAnalytics.current
    SideEffect {
        analytics.logScreenView(screenName)
    }
}

// snapshotFlow：将 Compose State 转为 Flow
@Composable
fun ScrollTracker(listState: LazyListState) {
    LaunchedEffect(listState) {
        snapshotFlow { listState.firstVisibleItemIndex }
            .distinctUntilChanged()
            .collect { index -> analytics.logScroll(index) }
    }
}
```
## 🎬 推荐视频资源

- [Philipp Lackner - State in Compose](https://www.youtube.com/watch?v=mymWGMy9pYI) — Compose状态管理
- [Android Developers - State and Jetpack Compose](https://www.youtube.com/watch?v=rmv2ug-wW4U) — 官方状态管理讲解


## 6. 2026 状态管理更新

<!-- version-check: Compose 1.11.4, Lifecycle 2.11.0, Kotlin 2.4.0, AGP 8.5.2+, checked 2026-07-08 -->

> 🔄 更新于 2026-04-21（2026-07-08 校准至 BOM 2026.06.01 清单）

### collectAsStateWithLifecycle（推荐替代 collectAsState）

```kotlin
// ❌ 旧写法：不感知生命周期，后台仍在收集
val uiState by viewModel.uiState.collectAsState()

// ✅ 新写法：生命周期感知，后台自动停止收集
// 依赖: androidx.lifecycle:lifecycle-runtime-compose
val uiState by viewModel.uiState.collectAsStateWithLifecycle()
```

### Compose 强稳定性（Strong Skipping Mode）

```kotlin
// Compose Compiler 2.0+ 默认启用 Strong Skipping Mode
// 所有 Composable 函数参数都会被自动比较，减少不必要的重组

// 不再需要手动标注 @Stable 或 @Immutable（大多数情况下）
// 但对于复杂对象，仍建议使用 @Immutable 提示编译器
@Immutable
data class UserState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)
```

### Kotlin 2.4.0 与状态管理工具链

Kotlin **2.4.0**（2026-06-03）将 **explicit backing fields** 升为稳定特性，可简化 ViewModel 中 `_uiState` / `uiState` 双属性模式，与 `collectAsStateWithLifecycle` 配合更简洁。最低 AGP **8.5.2**，推荐 `lifecycle-runtime-compose` **2.11.0**。来源：[What's new in Kotlin 2.4.0](https://kotlinlang.org/docs/whatsnew24.html)、[Lifecycle Runtime Compose](https://developer.android.com/jetpack/androidx/releases/lifecycle)
