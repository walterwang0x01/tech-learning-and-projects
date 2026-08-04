# ViewModel 与 LiveData
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. ViewModel 生命周期

```kotlin
// ViewModel 在配置变更（旋转屏幕）时存活
class UserViewModel(
    private val repository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    private val _uiState = MutableStateFlow(UserUiState())
    val uiState: StateFlow<UserUiState> = _uiState.asStateFlow()

    init { loadUsers() }

    private fun loadUsers() {
        viewModelScope.launch {
            _uiState.update { it.copy(isLoading = true) }
            try {
                val users = repository.getUsers()
                _uiState.update { it.copy(users = users, isLoading = false) }
            } catch (e: Exception) {
                _uiState.update { it.copy(error = e.message, isLoading = false) }
            }
        }
    }

    override fun onCleared() {
        super.onCleared()
        // 清理资源
    }
}

data class UserUiState(
    val users: List<User> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)
```

## 2. SavedStateHandle

```kotlin
class SearchViewModel(private val savedStateHandle: SavedStateHandle) : ViewModel() {
    // 进程被杀后恢复
    var query: String
        get() = savedStateHandle["query"] ?: ""
        set(value) { savedStateHandle["query"] = value }

    val queryFlow: StateFlow<String> = savedStateHandle.getStateFlow("query", "")

    // 配合 Navigation 获取参数
    private val userId: String = savedStateHandle["userId"] ?: ""
}
```

## 3. LiveData

```kotlin
class PostViewModel : ViewModel() {
    private val _posts = MutableLiveData<List<Post>>()
    val posts: LiveData<List<Post>> = _posts

    fun loadPosts() {
        viewModelScope.launch {
            _posts.value = repository.getPosts()  // 主线程
            _posts.postValue(data)                 // 任意线程
        }
    }
}

// 观察 LiveData
class PostFragment : Fragment() {
    private val viewModel: PostViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.posts.observe(viewLifecycleOwner) { posts ->
            adapter.submitList(posts)
        }
    }
}
```

## 4. Transformations

```kotlin
class UserViewModel : ViewModel() {
    private val _userId = MutableLiveData<String>()

    // map：同步转换
    val userName: LiveData<String> = _userId.map { id ->
        "User: $id"
    }

    // switchMap：异步转换（返回新 LiveData）
    val userDetail: LiveData<User> = _userId.switchMap { id ->
        repository.getUserLiveData(id)
    }

    // MediatorLiveData：合并多个源
    val combined = MediatorLiveData<Pair<User?, List<Post>?>>().apply {
        addSource(userLiveData) { user -> value = Pair(user, postsLiveData.value) }
        addSource(postsLiveData) { posts -> value = Pair(userLiveData.value, posts) }
    }
}
```

## 5. StateFlow 替代 LiveData（推荐）

```kotlin
class ModernViewModel(private val repository: UserRepository) : ViewModel() {
    private val _uiState = MutableStateFlow(UiState())
    val uiState: StateFlow<UiState> = _uiState.asStateFlow()

    // 事件用 SharedFlow（一次性事件）
    private val _events = MutableSharedFlow<UiEvent>()
    val events: SharedFlow<UiEvent> = _events.asSharedFlow()

    fun onAction(action: UserAction) {
        when (action) {
            is UserAction.Delete -> deleteUser(action.userId)
            is UserAction.Refresh -> refresh()
        }
    }

    private fun deleteUser(id: String) {
        viewModelScope.launch {
            repository.deleteUser(id)
            _events.emit(UiEvent.ShowSnackbar("已删除"))
        }
    }
}

// Compose 中收集
@Composable
fun UserScreen(viewModel: ModernViewModel = hiltViewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    LaunchedEffect(Unit) {
        viewModel.events.collect { event ->
            when (event) {
                is UiEvent.ShowSnackbar -> snackbarHostState.showSnackbar(event.message)
            }
        }
    }
}
```

## 6. Lifecycle 2.10 版本演进

> 🔄 更新于 2026-04-21

Jetpack Lifecycle 2.10.0 是当前稳定版（2026-01），核心更新为 Compose 集成增强和 Kotlin Multiplatform（KMP）支持。来源：[Android Developers](https://developer.android.com/jetpack/androidx/releases/lifecycle)

<!-- version-check: Lifecycle 2.10.0, checked 2026-04-21 -->

### 关键更新

- **KMP 支持**：ViewModel 可跨 Android、iOS、JVM、Web 平台共享
- **Compose 集成**：`viewModel()` 和 `SavedStateHandle` 在 Compose 中更自然
- **LiveData 逐步淘汰**：官方推荐 `StateFlow` + `collectAsStateWithLifecycle` 替代 LiveData

```kotlin
// 2026 推荐：StateFlow + collectAsStateWithLifecycle
@Composable
fun UserScreen(viewModel: UserViewModel = viewModel()) {
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    when {
        uiState.isLoading -> CircularProgressIndicator()
        uiState.error != null -> ErrorMessage(uiState.error!!)
        else -> UserList(uiState.users)
    }
}

// ⚠️ LiveData 仍可用但不推荐新项目使用
// val users by viewModel.users.observeAsState()
```

### 迁移建议

```
你的项目情况？
├─ 新项目 → 直接用 StateFlow + collectAsStateWithLifecycle
├─ 现有 LiveData 项目 → 逐步迁移，新代码用 StateFlow
├─ KMP 项目 → 必须用 StateFlow（LiveData 不支持 KMP）
└─ Java 项目 → LiveData 仍然是最佳选择
```

## 🎬 推荐视频资源

- [Philipp Lackner - ViewModel Tutorial](https://www.youtube.com/watch?v=9sqvBydNJSg) — ViewModel教程
- [CodingWithMitch - Android Architecture](https://www.youtube.com/watch?v=ijXjCtCXcN4) — Android架构组件
