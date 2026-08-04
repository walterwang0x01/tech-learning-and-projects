# MVVM 与 MVI 架构
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. MVVM（ViewModel + StateFlow + Repository）

```kotlin
// --- UiState ---
data class UserListUiState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)

// --- ViewModel ---
@HiltViewModel
class UserListViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {

    private val _uiState = MutableStateFlow(UserListUiState())
    val uiState: StateFlow<UserListUiState> = _uiState.asStateFlow()

    init { loadUsers() }

    fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true, error = null) }
            try {
                val users = repository.getUsers()
                _uiState.update { it.copy(users = users, isLoading = false) }
            } catch (e: Exception) {
                _uiState.update { it.copy(error = e.message, isLoading = false) }
            }
        }
    }

    fun deleteUser(userId: String) {
        viewModelScope.launch {
            repository.deleteUser(userId)
            loadUsers()
        }
    }
}

// --- Repository ---
class UserRepository @Inject constructor(
    private val api: ApiService,
    private val dao: UserDao
) {
    suspend fun getUsers(): List<User> {
        val remote = api.getUsers()
        dao.insertAll(remote.map { it.toEntity() })
        return remote
    }
}

// --- UI (Compose) ---
@Composable
fun UserListScreen(viewModel: UserListViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when {
        uiState.isLoading -> CircularProgressIndicator()
        uiState.error != null -> ErrorView(uiState.error!!) { viewModel.loadUsers() }
        else -> UserList(uiState.users, onDelete = viewModel::deleteUser)
    }
}
```

## 2. MVI（单向数据流）

```kotlin
// --- Intent（用户意图）---
sealed class UserIntent {
    data object LoadUsers : UserIntent()
    data class DeleteUser(val id: String) : UserIntent()
    data class SearchUsers(val query: String) : UserIntent()
}

// --- State ---
data class UserState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null,
    val query: String = ""
)

// --- Side Effect（一次性事件）---
sealed class UserEffect {
    data class ShowToast(val message: String) : UserEffect()
    data object NavigateBack : UserEffect()
}

// --- ViewModel ---
@HiltViewModel
class UserMviViewModel @Inject constructor(
    private val repository: UserRepository
) : ViewModel() {

    private val _state = MutableStateFlow(UserState())
    val state: StateFlow<UserState> = _state.asStateFlow()

    private val _effect = MutableSharedFlow<UserEffect>()
    val effect: SharedFlow<UserEffect> = _effect.asSharedFlow()

    fun onIntent(intent: UserIntent) {
        when (intent) {
            is UserIntent.LoadUsers -> loadUsers()
            is UserIntent.DeleteUser -> deleteUser(intent.id)
            is UserIntent.SearchUsers -> search(intent.query)
        }
    }

    private fun loadUsers() {
        viewModelScope.launch {
            _state.update { it.copy(isLoading = true) }
            try {
                val users = repository.getUsers()
                _state.update { it.copy(users = users, isLoading = false) }
            } catch (e: Exception) {
                _state.update { it.copy(error = e.message, isLoading = false) }
                _effect.emit(UserEffect.ShowToast("加载失败"))
            }
        }
    }

    private fun deleteUser(id: String) {
        viewModelScope.launch {
            repository.deleteUser(id)
            _effect.emit(UserEffect.ShowToast("已删除"))
            loadUsers()
        }
    }

    private fun search(query: String) {
        _state.update { it.copy(query = query) }
    }
}

// --- UI ---
@Composable
fun UserMviScreen(viewModel: UserMviViewModel = hiltViewModel()) {
    val state by viewModel.state.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        viewModel.effect.collect { effect ->
            when (effect) {
                is UserEffect.ShowToast -> { /* show snackbar */ }
                is UserEffect.NavigateBack -> { /* navigate */ }
            }
        }
    }

    LaunchedEffect(Unit) { viewModel.onIntent(UserIntent.LoadUsers) }

    Column {
        SearchBar(state.query) { viewModel.onIntent(UserIntent.SearchUsers(it)) }
        UserList(state.users) { viewModel.onIntent(UserIntent.DeleteUser(it)) }
    }
}
```
## 🎬 推荐视频资源

- [Philipp Lackner - MVVM Tutorial](https://www.youtube.com/watch?v=ijXjCtCXcN4) — Android MVVM教程
- [Philipp Lackner - MVI Architecture](https://www.youtube.com/watch?v=hlBsrsVFgIk) — MVI架构讲解

## 3. 2026 架构选型建议

> 🔄 更新于 2026-04-21

<!-- version-check: Android Architecture 2026, Compose 1.11.x (latest 1.11.2), checked 2026-05-31 -->

<!-- 修复于 2026-05-31: Compose 1.10.x → 1.11.x，与同栈 01-Jetpack Compose/ 文档（第 34/35 次审查确认 1.11.2）对齐 -->

### MVVM vs MVI 选型指南（2026）

| 维度 | MVVM | MVI |
|------|------|-----|
| 状态管理 | 多个 StateFlow | 单一 State 对象 |
| 复杂度 | 低（适合简单页面） | 中（适合复杂交互） |
| 可测试性 | 好 | 更好（纯函数 reducer） |
| 调试 | 需要追踪多个流 | 单一状态快照，易于调试 |
| Compose 适配 | ✅ 原生适配 | ✅ 原生适配 |
| 推荐场景 | CRUD 页面、简单列表 | 表单、多步骤流程、复杂交互 |

### 2026 年推荐实践

- **状态收集**：统一使用 `collectAsStateWithLifecycle()`（Lifecycle 2.10+）
- **Side Effect**：MVI 中使用 `SharedFlow` 处理一次性事件（Toast、导航）
- **ViewModel 作用域**：Compose Navigation 中使用 `hiltViewModel()` 或 `koinViewModel()` 自动绑定生命周期
- **Strong Skipping Mode**：Compose 1.10+ 默认启用，减少不必要的重组
- **KMP 共享**：ViewModel 可通过 Lifecycle 2.10 KMP 支持跨平台共享
