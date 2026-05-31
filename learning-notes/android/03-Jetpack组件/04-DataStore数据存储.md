# DataStore 数据存储
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Preferences DataStore

```kotlin
// 创建 DataStore
val Context.dataStore by preferencesDataStore(name = "settings")

// 定义 Key
object PrefsKeys {
    val DARK_MODE = booleanPreferencesKey("dark_mode")
    val FONT_SIZE = intPreferencesKey("font_size")
    val USERNAME = stringPreferencesKey("username")
    val LANGUAGE = stringPreferencesKey("language")
}

// 读取数据（Flow）
class SettingsRepository(private val dataStore: DataStore<Preferences>) {

    val darkMode: Flow<Boolean> = dataStore.data
        .catch { if (it is IOException) emit(emptyPreferences()) else throw it }
        .map { it[PrefsKeys.DARK_MODE] ?: false }

    val fontSize: Flow<Int> = dataStore.data
        .map { it[PrefsKeys.FONT_SIZE] ?: 14 }

    // 写入数据
    suspend fun setDarkMode(enabled: Boolean) {
        dataStore.edit { it[PrefsKeys.DARK_MODE] = enabled }
    }

    suspend fun setFontSize(size: Int) {
        dataStore.edit { it[PrefsKeys.FONT_SIZE] = size }
    }

    // 清除所有
    suspend fun clearAll() {
        dataStore.edit { it.clear() }
    }
}
```

## 2. 在 ViewModel 中使用

```kotlin
class SettingsViewModel(private val repository: SettingsRepository) : ViewModel() {

    val uiState: StateFlow<SettingsUiState> = combine(
        repository.darkMode,
        repository.fontSize
    ) { darkMode, fontSize ->
        SettingsUiState(darkMode = darkMode, fontSize = fontSize)
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5000), SettingsUiState())

    fun toggleDarkMode() {
        viewModelScope.launch {
            repository.setDarkMode(!uiState.value.darkMode)
        }
    }
}

data class SettingsUiState(
    val darkMode: Boolean = false,
    val fontSize: Int = 14
)
```

## 3. Proto DataStore

```protobuf
// app/src/main/proto/user_prefs.proto
syntax = "proto3";
option java_package = "com.example.app";
message UserPrefs {
    string theme = 1;
    int32 font_size = 2;
    bool notifications_enabled = 3;
}
```

```kotlin
// Serializer
object UserPrefsSerializer : Serializer<UserPrefs> {
    override val defaultValue: UserPrefs = UserPrefs.getDefaultInstance()

    override suspend fun readFrom(input: InputStream): UserPrefs =
        try { UserPrefs.parseFrom(input) }
        catch (e: InvalidProtocolBufferException) { throw CorruptionException("Cannot read proto", e) }

    override suspend fun writeTo(t: UserPrefs, output: OutputStream) = t.writeTo(output)
}

// 创建 Proto DataStore
val Context.userPrefsStore by dataStore(
    fileName = "user_prefs.pb",
    serializer = UserPrefsSerializer
)

// 读写
class UserPrefsRepository(private val dataStore: DataStore<UserPrefs>) {
    val prefs: Flow<UserPrefs> = dataStore.data

    suspend fun updateTheme(theme: String) {
        dataStore.updateData { it.toBuilder().setTheme(theme).build() }
    }
}
```

## 4. 从 SharedPreferences 迁移

```kotlin
val Context.dataStore by preferencesDataStore(
    name = "settings",
    produceMigrations = { context ->
        listOf(SharedPreferencesMigration(context, "old_shared_prefs"))
    }
)

// 迁移完成后旧 SharedPreferences 文件自动删除
```

## 5. DataStore 1.1.x / 1.2.x 版本演进

> 🔄 更新于 2026-05-01（2026-05-31 校准版本）

DataStore 1.1.x 引入了 Kotlin Multiplatform（KMP）支持和存储后端抽象。**DataStore 1.2.1 已发布稳定版**（androidx maven 实测），进一步增强 KMP 和文件系统抽象；1.3.0 处于 alpha 阶段。来源：[Android Developers - DataStore Releases](https://developer.android.com/jetpack/androidx/releases/datastore)

<!-- version-check: DataStore 1.2.1 stable, 1.3.0-alpha, checked 2026-05-31 -->
<!-- 修复于 2026-05-31: 原文写"1.1.7 stable + 1.2.0-alpha01"，实测 androidx maven 已发布 1.2.1 stable -->

### DataStore 1.1.x 核心变化

| 特性 | DataStore 1.0.x | DataStore 1.1.x |
|------|----------------|----------------|
| KMP 支持 | ❌ 仅 Android | ✅ Android + iOS + JVM + JS |
| 存储后端 | 固定文件系统 | `Storage<T>` 接口可替换 |
| OkIO 集成 | ❌ | ✅ `OkioStorage` |
| 文件路径 | `Context.dataStore` | `DataStoreFactory.create(storage)` |

### KMP 跨平台用法

```kotlin
// 共享模块（commonMain）
// 定义 DataStore 创建函数
fun createDataStore(producePath: () -> String): DataStore<Preferences> =
    PreferenceDataStoreFactory.createWithPath(
        produceFile = { producePath().toPath() }
    )

// Android 端（androidMain）
fun createAndroidDataStore(context: Context): DataStore<Preferences> =
    createDataStore(
        producePath = { context.filesDir.resolve("settings.preferences_pb").absolutePath }
    )

// iOS 端（iosMain）
fun createIOSDataStore(): DataStore<Preferences> =
    createDataStore(
        producePath = {
            val dir = NSFileManager.defaultManager.URLForDirectory(
                NSDocumentDirectory, NSUserDomainMask, null, true, null
            )!!
            "${dir.path}/settings.preferences_pb"
        }
    )
```

### DataStore 1.2.x 新特性

- **MultiProcess DataStore 改进**：跨进程数据一致性增强
- **FileStorage 抽象**：更灵活的文件系统操作
- **compileSdk 35+ 要求**：最低编译 SDK 版本提升

### 版本选择建议

```
你的项目情况？
├─ 仅 Android → DataStore 1.2.1（稳定版）
├─ KMP（Android + iOS） → DataStore 1.2.1 + OkioStorage
├─ 需要多进程支持 → DataStore 1.2.1（MultiProcess 已稳定）
└─ 尝试最新特性 → DataStore 1.3.0-alpha（实验性）
```
