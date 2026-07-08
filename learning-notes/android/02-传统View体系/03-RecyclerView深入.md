# RecyclerView 深入
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Adapter 与 ViewHolder

```kotlin
class UserAdapter(
    private val onItemClick: (User) -> Unit
) : ListAdapter<User, UserAdapter.UserViewHolder>(UserDiffCallback()) {

    inner class UserViewHolder(
        private val binding: ItemUserBinding
    ) : RecyclerView.ViewHolder(binding.root) {
        fun bind(user: User) {
            binding.tvName.text = user.name
            binding.tvEmail.text = user.email
            binding.root.setOnClickListener { onItemClick(user) }
        }
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): UserViewHolder {
        val binding = ItemUserBinding.inflate(
            LayoutInflater.from(parent.context), parent, false
        )
        return UserViewHolder(binding)
    }

    override fun onBindViewHolder(holder: UserViewHolder, position: Int) {
        holder.bind(getItem(position))
    }
}
```

## 2. DiffUtil

```kotlin
class UserDiffCallback : DiffUtil.ItemCallback<User>() {
    override fun areItemsTheSame(oldItem: User, newItem: User) = oldItem.id == newItem.id
    override fun areContentsTheSame(oldItem: User, newItem: User) = oldItem == newItem
}

// 使用 ListAdapter 自动处理差异更新
adapter.submitList(newList)
```

## 3. LayoutManager

```kotlin
// 线性布局
recyclerView.layoutManager = LinearLayoutManager(context)
recyclerView.layoutManager = LinearLayoutManager(context, RecyclerView.HORIZONTAL, false)

// 网格布局
recyclerView.layoutManager = GridLayoutManager(context, 2).apply {
    spanSizeLookup = object : GridLayoutManager.SpanSizeLookup() {
        override fun getSpanSize(position: Int) = if (position == 0) 2 else 1
    }
}

// 瀑布流
recyclerView.layoutManager = StaggeredGridLayoutManager(2, StaggeredGridLayoutManager.VERTICAL)

// ItemDecoration
recyclerView.addItemDecoration(DividerItemDecoration(context, DividerItemDecoration.VERTICAL))
```

## 4. 多类型列表

```kotlin
sealed class ListItem {
    data class Header(val title: String) : ListItem()
    data class Content(val user: User) : ListItem()
}

class MultiTypeAdapter : ListAdapter<ListItem, RecyclerView.ViewHolder>(DiffCallback()) {
    override fun getItemViewType(position: Int) = when (getItem(position)) {
        is ListItem.Header -> TYPE_HEADER
        is ListItem.Content -> TYPE_CONTENT
    }

    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int) = when (viewType) {
        TYPE_HEADER -> HeaderViewHolder(ItemHeaderBinding.inflate(/*..*/))
        else -> ContentViewHolder(ItemContentBinding.inflate(/*..*/))
    }

    override fun onBindViewHolder(holder: RecyclerView.ViewHolder, position: Int) {
        when (val item = getItem(position)) {
            is ListItem.Header -> (holder as HeaderViewHolder).bind(item)
            is ListItem.Content -> (holder as ContentViewHolder).bind(item)
        }
    }

    companion object { const val TYPE_HEADER = 0; const val TYPE_CONTENT = 1 }
}
```

## 5. Paging3

```kotlin
// PagingSource
class UserPagingSource(private val api: ApiService) : PagingSource<Int, User>() {
    override suspend fun load(params: LoadParams<Int>): LoadResult<Int, User> {
        val page = params.key ?: 1
        return try {
            val response = api.getUsers(page, params.loadSize)
            LoadResult.Page(
                data = response.data,
                prevKey = if (page == 1) null else page - 1,
                nextKey = if (response.data.isEmpty()) null else page + 1
            )
        } catch (e: Exception) {
            LoadResult.Error(e)
        }
    }

    override fun getRefreshKey(state: PagingState<Int, User>) =
        state.anchorPosition?.let { state.closestPageToPosition(it)?.prevKey?.plus(1) }
}

// ViewModel
class UserViewModel(private val api: ApiService) : ViewModel() {
    val users: Flow<PagingData<User>> = Pager(
        config = PagingConfig(pageSize = 20, prefetchDistance = 5)
    ) { UserPagingSource(api) }.flow.cachedIn(viewModelScope)
}

// Activity / Compose
val lazyPagingItems = viewModel.users.collectAsLazyPagingItems()
LazyColumn {
    items(lazyPagingItems.itemCount) { index ->
        lazyPagingItems[index]?.let { UserCard(it) }
    }
}
```

## 6. 2026 版本演进

<!-- version-check: RecyclerView 1.4.0, Paging 3.5.0 stable, Kotlin 2.4.0, compileSdk 37, checked 2026-07-08 -->

> 🔄 更新于 2026-05-04（2026-07-08 校准 compileSdk 37 与 Kotlin 2.4.0 工具链）

### 6.1 RecyclerView 1.4.0（2025-01-15）

RecyclerView 最新稳定版为 **1.4.0**，主要新增自适应刷新率支持：

来源：[AndroidX RecyclerView Releases](https://developer.android.com/jetpack/androidx/releases/recyclerview)

- **自适应刷新率**：滚动时自动调用 `setFrameContentVelocity`，在支持可变刷新率的设备上提供更流畅的滚动体验
- **`isLayoutReversed` API**：新增 `LayoutManager#isLayoutReversed()` 方法
- **Trace 改进**：bind/create trace 中包含 item view type，prefetch 标记是否为下一帧所需

```kotlin
// 推荐依赖版本（2026）
dependencies {
    implementation("androidx.recyclerview:recyclerview:1.4.0")
    implementation("androidx.recyclerview:recyclerview-selection:1.2.0")
}
```

> ⚠️ RecyclerView 1.4.0 最低要求 compileSdk 35+；2026 年新项目建议 **compileSdk 37**（Android 17 stable），配合 Kotlin **2.4.0** 与 AGP **≥ 8.5.2**。

### 6.2 Paging 3.5.0（已发布稳定版）

Paging 3.5.0 已正式发布稳定版（`androidx.paging:paging-runtime:3.5.0`，androidx maven 实测）。<!-- 修复于 2026-05-31: 原文写"目前处于 rc01 阶段、即将发布"，实测 androidx maven 已发布 3.5.0 stable -->

来源：[AndroidX Paging Releases](https://developer.android.com/jetpack/androidx/releases/paging)

```kotlin
// 推荐依赖版本（2026）
dependencies {
    implementation("androidx.paging:paging-runtime:3.5.0")
    implementation("androidx.paging:paging-compose:3.5.0")
}
```

Compose 中展示分页数据的标准 API 仍是 `collectAsLazyPagingItems()`（见上方第 5 节），它返回 `LazyPagingItems`，可直接配合 `LazyColumn` 的 `items` 使用：

```kotlin
// Compose 标准用法（官方推荐）
val lazyPagingItems = viewModel.users.collectAsLazyPagingItems()
LazyColumn {
    items(
        count = lazyPagingItems.itemCount,
        key = lazyPagingItems.itemKey { it.id }
    ) { index ->
        lazyPagingItems[index]?.let { UserCard(it) }
    }
}
```

Paging 3.5.0 在 `paging-common` 中新增了 `Flow<PagingData>.asItemSnapshotListFlow` 操作符（3.5.0-alpha01 时名为 `asState`，3.5.0-beta01 起重命名为 `asItemSnapshotListFlow`），将 `Flow<PagingData>` 转换为 `Flow<ItemSnapshotList>`，可把分页数据作为 UI 状态的一部分缓存/共享：<!-- 修复于 2026-05-31: 经官方 release notes 核实，asState/append/prepend 确为 3.5.0 真实新增 API；asState 已于 3.5.0-beta01 重命名为 asItemSnapshotListFlow -->

```kotlin
// ViewModel 中：转换为 ItemSnapshotList 流
val pager = Pager(pagingConfig, pagingSourceFactory)
val snapshotFlow = pager.flow.asItemSnapshotListFlow()  // 3.5.0-alpha01 时为 asState()

// Compose UI 中收集
val snapshot by viewModel.snapshotFlow.collectAsStateWithLifecycle(ItemSnapshotList(0, 0, emptyList()))
LazyColumn {
    items(items = snapshot.items) { item -> UserCard(item) }
}
```

配合 `asItemSnapshotListFlow` 使用时，`Pager.append()` / `Pager.prepend()` 用于手动触发加载（不依赖滚动），`Pager.refresh()` / `Pager.retry()` 用于从加载错误中恢复：

```kotlin
// 手动触发加载（不依赖滚动）
LazyColumn {
    item { LaunchedEffect(viewModel) { viewModel.prepend() } }  // 顶部加载更多
    items(snapshot.items) { item -> Text("Item: $item") }
    item { LaunchedEffect(viewModel) { viewModel.append() } }   // 底部加载更多
}
```

> 详见官方示例 [PagerAsStateSamples.kt](https://cs.android.com/androidx/platform/frameworks/support/+/androidx-main:paging/samples/src/main/java/androidx/paging/samples/PagerAsStateSamples.kt)（来源：Paging 3.5.0 / 3.5.0-alpha01 release notes）。

### 6.3 Compose 迁移趋势

Google 官方提供了 RecyclerView → LazyList 迁移指南。2026 年新项目推荐直接使用 Compose `LazyColumn`/`LazyRow`，但 RecyclerView 在以下场景仍有优势：

| 场景 | 推荐方案 |
|------|---------|
| 新项目 | Compose LazyColumn + Paging 3.5 |
| 已有 View 项目 | RecyclerView 1.4.0 + ListAdapter |
| 复杂 ItemDecoration | RecyclerView（Compose 暂无等价 API） |
| 嵌套滚动复杂场景 | RecyclerView（更成熟的嵌套滚动支持） |

来源：[Migrate RecyclerView to Lazy list](https://developer.android.com/develop/ui/compose/migrate/migration-scenarios/recycler-view)
