# Clean Architecture 实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 分层结构

```
app/
├── presentation/    # UI 层（Activity/Fragment/Compose, ViewModel）
├── domain/          # 领域层（UseCase, Repository 接口, Entity）
└── data/            # 数据层（Repository 实现, DataSource, DTO）
```

## 2. Domain 层（纯 Kotlin，无 Android 依赖）

```kotlin
// Entity
data class Article(
    val id: String,
    val title: String,
    val content: String,
    val author: String,
    val publishedAt: Long
)

// Repository 接口
interface ArticleRepository {
    fun getArticles(): Flow<List<Article>>
    suspend fun getArticleById(id: String): Article
    suspend fun saveArticle(article: Article)
    suspend fun deleteArticle(id: String)
}

// UseCase
class GetArticlesUseCase(private val repository: ArticleRepository) {
    operator fun invoke(): Flow<List<Article>> =
        repository.getArticles().map { articles ->
            articles.sortedByDescending { it.publishedAt }
        }
}

class GetArticleDetailUseCase(private val repository: ArticleRepository) {
    suspend operator fun invoke(id: String): Article =
        repository.getArticleById(id)
}

// 带参数的 UseCase 基类
abstract class FlowUseCase<in P, R>(private val dispatcher: CoroutineDispatcher) {
    operator fun invoke(params: P): Flow<Result<R>> = execute(params)
        .map { Result.success(it) }
        .catch { emit(Result.failure(it)) }
        .flowOn(dispatcher)

    protected abstract fun execute(params: P): Flow<R>
}
```

## 3. Data 层

```kotlin
// DTO（网络模型）
@Serializable
data class ArticleDto(
    val id: String,
    val title: String,
    val content: String,
    @SerialName("author_name") val author: String,
    @SerialName("published_at") val publishedAt: String
) {
    fun toDomain() = Article(
        id = id, title = title, content = content,
        author = author, publishedAt = parseTimestamp(publishedAt)
    )
}

// Entity（数据库模型）
@Entity(tableName = "articles")
data class ArticleEntity(
    @PrimaryKey val id: String,
    val title: String,
    val content: String,
    val author: String,
    val publishedAt: Long
) {
    fun toDomain() = Article(id, title, content, author, publishedAt)
}

fun Article.toEntity() = ArticleEntity(id, title, content, author, publishedAt)

// Repository 实现
class ArticleRepositoryImpl @Inject constructor(
    private val api: ApiService,
    private val dao: ArticleDao
) : ArticleRepository {

    override fun getArticles(): Flow<List<Article>> =
        dao.getAllArticles().map { entities -> entities.map { it.toDomain() } }

    override suspend fun getArticleById(id: String): Article =
        dao.getById(id)?.toDomain() ?: api.getArticle(id).toDomain()

    override suspend fun saveArticle(article: Article) =
        dao.insert(article.toEntity())

    override suspend fun deleteArticle(id: String) =
        dao.deleteById(id)
}
```

## 4. Presentation 层

```kotlin
@HiltViewModel
class ArticleListViewModel @Inject constructor(
    private val getArticles: GetArticlesUseCase
) : ViewModel() {

    val uiState: StateFlow<ArticleListUiState> = getArticles()
        .map { ArticleListUiState(articles = it) }
        .catch { emit(ArticleListUiState(error = it.message)) }
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), ArticleListUiState(isLoading = true))
}

data class ArticleListUiState(
    val articles: List<Article> = emptyList(),
    val isLoading: Boolean = false,
    val error: String? = null
)
```

## 5. DI 模块

```kotlin
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    @Singleton
    abstract fun bindArticleRepository(impl: ArticleRepositoryImpl): ArticleRepository
}

@Module
@InstallIn(ViewModelComponent::class)
object UseCaseModule {
    @Provides
    fun provideGetArticles(repo: ArticleRepository) = GetArticlesUseCase(repo)
}
```
