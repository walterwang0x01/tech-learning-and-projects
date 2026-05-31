# 依赖注入 Hilt / Koin
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Hilt 基础

```kotlin
// Application
@HiltAndroidApp
class MyApp : Application()

// Activity
@AndroidEntryPoint
class MainActivity : ComponentActivity()

// ViewModel 注入
@HiltViewModel
class UserViewModel @Inject constructor(
    private val repository: UserRepository,
    private val savedStateHandle: SavedStateHandle
) : ViewModel()
```

## 2. Hilt Module

```kotlin
// 接口绑定
@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    @Binds
    @Singleton
    abstract fun bindUserRepository(impl: UserRepositoryImpl): UserRepository
}

// 实例提供
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient = OkHttpClient.Builder()
        .addInterceptor(HttpLoggingInterceptor())
        .build()

    @Provides
    @Singleton
    fun provideRetrofit(client: OkHttpClient): Retrofit = Retrofit.Builder()
        .baseUrl("https://api.example.com/")
        .client(client)
        .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
        .build()

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService =
        retrofit.create(ApiService::class.java)
}
```

## 3. Hilt Scope

```kotlin
// SingletonComponent  → Application 生命周期
// ActivityComponent   → Activity 生命周期
// ViewModelComponent  → ViewModel 生命周期
// FragmentComponent   → Fragment 生命周期

// Qualifier（区分同类型）
@Qualifier
@Retention(AnnotationRetention.BINARY)
annotation class IoDispatcher

@Module
@InstallIn(SingletonComponent::class)
object DispatcherModule {
    @Provides
    @IoDispatcher
    fun provideIoDispatcher(): CoroutineDispatcher = Dispatchers.IO
}

class UserRepository @Inject constructor(
    private val api: ApiService,
    @IoDispatcher private val dispatcher: CoroutineDispatcher
)
```

## 4. Koin 基础

```kotlin
// Application
class MyApp : Application() {
    override fun onCreate() {
        super.onCreate()
        startKoin {
            androidContext(this@MyApp)
            modules(appModule, networkModule, viewModelModule)
        }
    }
}

// Module 定义
val appModule = module {
    single<UserRepository> { UserRepositoryImpl(get(), get()) }
    factory { GetUsersUseCase(get()) }
}

val networkModule = module {
    single {
        OkHttpClient.Builder()
            .addInterceptor(HttpLoggingInterceptor())
            .build()
    }
    single {
        Retrofit.Builder()
            .baseUrl("https://api.example.com/")
            .client(get())
            .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
            .build()
    }
    single { get<Retrofit>().create(ApiService::class.java) }
}

val viewModelModule = module {
    viewModel { UserViewModel(get()) }
    viewModel { (userId: String) -> DetailViewModel(userId, get()) }
}
```

## 5. Koin 使用

```kotlin
// Activity 中注入
class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModel()
}

// Compose 中注入
@Composable
fun UserScreen(viewModel: UserViewModel = koinViewModel()) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
}

// 带参数
val detailVm: DetailViewModel by viewModel { parametersOf("user_123") }

// Scope
val sessionModule = module {
    scope<UserSession> {
        scoped { AuthRepository(get()) }
    }
}
```

## 6. Hilt vs Koin 对比

```kotlin
// Hilt：编译时检查，Google 官方，注解驱动，学习曲线较高
// Koin：运行时解析，DSL 简洁，轻量，适合中小项目
// 推荐：大型项目用 Hilt，快速原型用 Koin
```

## 7. 2026 版本演进

> 🔄 更新于 2026-04-21

<!-- version-check: Hilt/Dagger 2.59.2, Koin 4.2.1, checked 2026-05-31 -->

<!-- 修复于 2026-05-31: Dagger 2.57.1 → 2.59.2（Maven Central 实测最新 stable）；Koin 4.1 → 4.2.1（Maven Central 实测最新 stable，4.2 引入 Kotlin Compiler Plugin） -->

### Hilt/Dagger 2.59.2（当前稳定版）

- 新增 `jakarta.inject.Provider` 注入支持（与 `javax.inject.Provider` 同等使用）
- 要求 Kotlin 2.0+（与 Kotlin 1.9 不兼容，需注意升级）
- 来源：[Dagger Releases](https://github.com/google/dagger/releases)

```kotlin
// Hilt 2.59.2 版本配置
// build.gradle.kts (Project)
plugins {
    id("com.google.dagger.hilt.android") version "2.59.2" apply false
}

// build.gradle.kts (App)
plugins {
    id("com.google.dagger.hilt.android")
    id("com.google.devtools.ksp") // KSP 替代 kapt
}

dependencies {
    implementation("com.google.dagger:hilt-android:2.59.2")
    ksp("com.google.dagger:hilt-android-compiler:2.59.2")
    // jakarta.inject.Provider 现在可以直接使用
    // 无需额外依赖
}
```

### Koin 4.2.1（Kotlin Compiler Plugin 成熟版）

Koin 4.1（2025-06）引入 Kotlin Compiler Plugin，4.2 进一步打磨编译时安全与自动装配，当前最新稳定版为 **4.2.1**：

- **Kotlin Compiler Plugin**：原生编译时安全 + 自动装配，推荐所有 Kotlin 2.x 新项目使用
- **模块化解析引擎**：可复用配置块、运行时特性标志
- **Archetype-based Scopes**：包括 ViewModel 构造函数注入的人体工学改进
- **Compose / MPP 支持**：自动上下文处理、更快注入、预览支持
- **Ktor 集成**：内联模块、请求作用域、多平台 artifact
- **WASM-safe UUID**：支持 Kotlin/WASM 目标
- 来源：[Koin Powered by Kotlin Compiler](https://blog.insert-koin.io/koin-powered-by-kotlin-compiler-0722f1cc96a4)、[Koin Releases](https://insert-koin.io/docs/support/releases/)

```kotlin
// Koin 4.2.1 + Kotlin Compiler Plugin 配置
// build.gradle.kts
plugins {
    id("io.insert-koin.koin") version "4.2.1" // Koin Compiler Plugin
}

dependencies {
    implementation("io.insert-koin:koin-android:4.2.1")
    implementation("io.insert-koin:koin-androidx-compose:4.2.1")
}

// 使用 Compiler Plugin 的自动装配（无需手动 get()）
@Single
class UserRepository(
    private val api: ApiService,  // 自动装配
    private val dao: UserDao      // 自动装配
)

@Factory
class GetUsersUseCase(
    private val repository: UserRepository  // 编译时检查
)
```

### 更新后的 Hilt vs Koin 对比

| 维度 | Hilt 2.59.2 | Koin 4.2.1 |
|------|-------------|----------|
| 检查时机 | 编译时 | 编译时（Compiler Plugin）或运行时 |
| 官方支持 | Google 官方 | 社区驱动 |
| KMP 支持 | ❌ 仅 Android | ✅ 全平台（iOS/JS/WASM） |
| Compose 集成 | `hiltViewModel()` | `koinViewModel()`，自动上下文 |
| 注解/DSL | 注解驱动 | DSL + 注解（可选） |
| Jakarta 支持 | ✅ 2.57+ | N/A |
| 学习曲线 | 较高 | 较低 |
| 推荐场景 | 大型 Android 项目 | KMP 项目、中小项目 |

## 8. 2026-Q2 版本演进：Dagger 2.59.2 + Hilt-AndroidX 1.4.0-beta01

> 🔄 更新于 2026-05-20

<!-- version-check: Dagger 2.59.2, Hilt-AndroidX 1.4.0-beta01 (Google Maven 实测), Hilt Gradle Plugin 2.59.x, checked 2026-05-31 -->

<!-- 修复于 2026-05-31: Dagger 2.59 → 2.59.2（Maven Central 实测最新 stable）；androidx.hilt 1.4.0-alpha01 → 1.4.0-beta01（Google Maven 实测已推进到 beta） -->

### Dagger 2.59.2（当前推荐稳定版）

Dagger 是 Hilt 的底层 DI 引擎。2026 年 Dagger 推进到 **2.59.2**，作为生产稳定线持续接收 Bug 修复。来源：[Dagger 官网](https://dagger.dev/)、[google/dagger Releases](https://github.com/google/dagger/releases)

`com.google.dagger:hilt-android` 与 Dagger 同步发版，Hilt Gradle 插件版本号即对应 Dagger 版本号。Android 项目升级到 Dagger 2.59.2 时，只需把 `com.google.dagger.hilt.android` 插件号升级即可，无 Breaking。

```kotlin
// build.gradle.kts (Project) — 升级 Dagger / Hilt 到 2.59.2
plugins {
    id("com.google.dagger.hilt.android") version "2.59.2" apply false
}

// build.gradle.kts (App)
dependencies {
    implementation("com.google.dagger:hilt-android:2.59.2")
    ksp("com.google.dagger:hilt-android-compiler:2.59.2")
}
```

### Hilt-AndroidX 1.4.0-beta01

`androidx.hilt:hilt-*` 系列（即 Hilt 与 AndroidX Navigation / WorkManager / ViewModel 的桥接库）已从 1.4.0-alpha01 推进到 **1.4.0-beta01**。来源：[Android Developers — Hilt Releases](https://developer.android.com/jetpack/androidx/releases/hilt)

需要区分两个版本号：

| 工件坐标 | 当前版本 | 含义 |
|----------|----------|------|
| `com.google.dagger:hilt-android` | 2.59.2 | Hilt 核心 + 编译器 |
| `com.google.dagger.hilt.android`（Gradle 插件） | 2.59.2 | 与上面同步 |
| `androidx.hilt:hilt-navigation-compose` | 1.4.0-beta01 | Compose 导航集成 |
| `androidx.hilt:hilt-work` | 1.4.0-beta01 | WorkManager 集成 |
| `androidx.hilt:hilt-common` | 1.4.0-beta01 | 公共工具 |

升级到 1.4.0-beta01 主要为获取与最新 Navigation 3 和 WorkManager 的兼容性。生产项目仍可继续使用 1.3.x 稳定线。

```kotlin
// build.gradle.kts (App) — 同时引入 Dagger 2.59.2 + AndroidX Hilt 1.4.0-beta01
dependencies {
    // Hilt 核心（生产稳定）
    implementation("com.google.dagger:hilt-android:2.59.2")
    ksp("com.google.dagger:hilt-android-compiler:2.59.2")

    // AndroidX Hilt 桥接（beta 仅在需要 Navigation 3 / 最新 WorkManager 时使用）
    implementation("androidx.hilt:hilt-navigation-compose:1.4.0-beta01")
    implementation("androidx.hilt:hilt-work:1.4.0-beta01")
    ksp("androidx.hilt:hilt-compiler:1.4.0-beta01")
}
```

### 升级建议（2026-Q2）

| 当前版本 | 建议路径 |
|----------|----------|
| Hilt 2.55 / 2.56 | 直接升 2.59.2，无 Breaking |
| Hilt 2.57.x | 升 2.59.2，受益于 Bug 修复 |
| Koin 4.0 / 4.1 | 升 Koin 4.2.1（受益于 Compiler Plugin 编译时检查） |
| Dagger（无 Hilt）项目 | 升 2.59.2 即可，迁移到 Hilt 是另一个独立决策 |

**新项目选型决策树（2026-05 修订版）**：

```
是否纯 Android（不需要 KMP）？
├─ 是 → Hilt 2.59.2 + AndroidX Hilt 1.3.x（生产）/ 1.4.0-beta01（实验）
└─ 否 → Koin 4.2.1 + Compiler Plugin（编译时安全 + KMP）
```
