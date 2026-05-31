# Retrofit 与 OkHttp
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Retrofit 接口定义

```kotlin
interface ApiService {
    @GET("users")
    suspend fun getUsers(@Query("page") page: Int): Response<List<User>>

    @GET("users/{id}")
    suspend fun getUser(@Path("id") userId: String): User

    @POST("users")
    suspend fun createUser(@Body user: CreateUserRequest): User

    @PUT("users/{id}")
    suspend fun updateUser(@Path("id") id: String, @Body user: User): User

    @DELETE("users/{id}")
    suspend fun deleteUser(@Path("id") id: String): Response<Unit>

    @Multipart
    @POST("upload")
    suspend fun uploadFile(
        @Part file: MultipartBody.Part,
        @Part("description") desc: RequestBody
    ): UploadResponse

    @Headers("Cache-Control: max-age=600")
    @GET("config")
    suspend fun getConfig(): AppConfig
}
```

## 2. Retrofit 配置

```kotlin
@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {

    @Provides
    @Singleton
    fun provideOkHttpClient(): OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .addInterceptor(AuthInterceptor())
        .addInterceptor(HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        })
        .build()

    @Provides
    @Singleton
    fun provideRetrofit(client: OkHttpClient): Retrofit = Retrofit.Builder()
        .baseUrl("https://api.example.com/v1/")
        .client(client)
        .addConverterFactory(Json.asConverterFactory("application/json".toMediaType()))
        .build()

    @Provides
    @Singleton
    fun provideApiService(retrofit: Retrofit): ApiService =
        retrofit.create(ApiService::class.java)
}
```

## 3. OkHttp 拦截器

```kotlin
// 认证拦截器
class AuthInterceptor @Inject constructor(
    private val tokenManager: TokenManager
) : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        val request = chain.request().newBuilder()
            .addHeader("Authorization", "Bearer ${tokenManager.getToken()}")
            .addHeader("Accept", "application/json")
            .build()
        return chain.proceed(request)
    }
}

// Token 刷新拦截器
class TokenRefreshInterceptor(
    private val tokenManager: TokenManager
) : Authenticator {
    override fun authenticate(route: Route?, response: Response): Request? {
        if (response.code == 401) {
            val newToken = runBlocking { tokenManager.refreshToken() } ?: return null
            return response.request.newBuilder()
                .header("Authorization", "Bearer $newToken")
                .build()
        }
        return null
    }
}
```

## 4. 统一错误处理

```kotlin
sealed class ApiResult<out T> {
    data class Success<T>(val data: T) : ApiResult<T>()
    data class Error(val code: Int, val message: String) : ApiResult<Nothing>()
    data class Exception(val e: Throwable) : ApiResult<Nothing>()
}

suspend fun <T> safeApiCall(call: suspend () -> Response<T>): ApiResult<T> {
    return try {
        val response = call()
        if (response.isSuccessful) {
            ApiResult.Success(response.body()!!)
        } else {
            ApiResult.Error(response.code(), response.message())
        }
    } catch (e: IOException) {
        ApiResult.Exception(e)
    }
}

// 使用
class UserRepository @Inject constructor(private val api: ApiService) {
    suspend fun getUsers(page: Int): ApiResult<List<User>> =
        safeApiCall { api.getUsers(page) }
}
```

<!-- 修复于 2026-05-31: 调整章节顺序，原"## 5. 连接池与性能"误排在"## 6. 版本演进"之后，现移回此处恢复 1-2-3-4-5-6 顺序 -->

## 5. 连接池与性能

```kotlin
val client = OkHttpClient.Builder()
    .connectionPool(ConnectionPool(5, 5, TimeUnit.MINUTES))
    .protocols(listOf(Protocol.HTTP_2, Protocol.HTTP_1_1))
    .dns(object : Dns {
        override fun lookup(hostname: String): List<InetAddress> {
            // 自定义 DNS 解析
            return Dns.SYSTEM.lookup(hostname)
        }
    })
    .build()
```

## 6. OkHttp 5.x 与 Retrofit 3.0 版本演进

<!-- version-check: OkHttp 5.3.2, Retrofit 3.0.0, checked 2026-04-22 -->

> 🔄 更新于 2026-04-22

OkHttp 5.0 于 2025-07-02 发布首个稳定版，当前最新为 5.3.2（2025-11-18）。Retrofit 3.0 同步升级，采用 Kotlin 原生设计。来源：[OkHttp Changelog](https://square.github.io/okhttp/changelogs/changelog/)

### 6.1 OkHttp 5.x 核心变化

```kotlin
// OkHttp 5.x 主要变化：
// - Kotlin 优先（协程原生支持）
// - Zstd 压缩支持
// - JPMS 模块化
// - Call tags（应用级元数据）
// - QUERY HTTP 方法

// Zstd 压缩（OkHttp 5.2+）
val client = OkHttpClient.Builder()
    .addInterceptor(CompressionInterceptor(Zstd, Gzip))
    .build()

// Call Tags（OkHttp 5.3+）：在拦截器间传递元数据
class AnalyticsInterceptor : Interceptor {
    override fun intercept(chain: Interceptor.Chain): Response {
        chain.call().tag(AnalyticsTag::class) {
            AnalyticsTag(startTime = System.currentTimeMillis())
        }
        return chain.proceed(chain.request())
    }
}

// QUERY HTTP 方法（OkHttp 5.2+）
val request = Request.Builder()
    .url("https://api.example.com/search")
    .method("QUERY", queryBody)
    .cacheUrlOverride(
        "https://api.example.com/search?hash=${queryBody.sha256()}"
            .toHttpUrl()
    )
    .build()

// toCurl() 调试辅助（OkHttp 5.2+）
val curlCommand = request.toCurl()
// 输出类似 Chrome 的 "copy as cURL" 格式
```

### 6.2 Retrofit 3.0 核心变化

```kotlin
// Retrofit 3.0 主要变化：
// - 要求 OkHttp 5.x
// - Kotlin 协程原生支持增强
// - kotlinx.serialization 推荐为默认序列化方案

// build.gradle.kts 依赖更新
dependencies {
    implementation("com.squareup.retrofit2:retrofit:3.0.0")
    implementation("com.squareup.retrofit2:converter-kotlinx-serialization:3.0.0")
    implementation("com.squareup.okhttp3:okhttp:5.3.2")
    implementation("com.squareup.okhttp3:logging-interceptor:5.3.2")
}

// 配置（与 2.x 基本兼容）
val retrofit = Retrofit.Builder()
    .baseUrl("https://api.example.com/v1/")
    .client(okHttpClient)
    .addConverterFactory(json.asConverterFactory("application/json".toMediaType()))
    .build()
```

### 6.3 版本选择建议

```
场景                    推荐版本
──────────────────────────────────────────
新项目                  OkHttp 5.3.x + Retrofit 3.0
已有项目（OkHttp 4.x）  按需升级，API 基本兼容
需要 Zstd 压缩          OkHttp 5.2+
需要 JPMS              OkHttp 5.2+
```
