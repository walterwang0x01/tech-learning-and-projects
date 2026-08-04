# Room 数据库
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Entity 定义

```kotlin
@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    @ColumnInfo(name = "user_name") val name: String,
    val email: String,
    val createdAt: Long = System.currentTimeMillis()
)

// 复合主键
@Entity(primaryKeys = ["userId", "postId"])
data class UserPostCrossRef(
    val userId: Long,
    val postId: Long
)

// 索引
@Entity(indices = [Index(value = ["email"], unique = true)])
data class User(
    @PrimaryKey val id: Long,
    val email: String
)
```

## 2. Dao 操作

```kotlin
@Dao
interface UserDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: UserEntity)

    @Insert
    suspend fun insertAll(users: List<UserEntity>)

    @Update
    suspend fun update(user: UserEntity)

    @Delete
    suspend fun delete(user: UserEntity)

    @Query("SELECT * FROM users ORDER BY created_at DESC")
    fun getAllUsers(): Flow<List<UserEntity>>  // 响应式查询

    @Query("SELECT * FROM users WHERE id = :userId")
    suspend fun getUserById(userId: Long): UserEntity?

    @Query("SELECT * FROM users WHERE user_name LIKE '%' || :query || '%'")
    fun searchUsers(query: String): Flow<List<UserEntity>>

    @Query("DELETE FROM users")
    suspend fun deleteAll()

    @Transaction
    suspend fun replaceAll(users: List<UserEntity>) {
        deleteAll()
        insertAll(users)
    }
}
```

## 3. Database

```kotlin
@Database(
    entities = [UserEntity::class, PostEntity::class],
    version = 2,
    exportSchema = true
)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun postDao(): PostDao
}

// Hilt 提供
@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    @Provides
    @Singleton
    fun provideDatabase(@ApplicationContext context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "app.db")
            .addMigrations(MIGRATION_1_2)
            .build()

    @Provides
    fun provideUserDao(db: AppDatabase): UserDao = db.userDao()
}
```

## 4. TypeConverter

```kotlin
class Converters {
    @TypeConverter
    fun fromStringList(value: List<String>): String = Json.encodeToString(value)

    @TypeConverter
    fun toStringList(value: String): List<String> = Json.decodeFromString(value)

    @TypeConverter
    fun fromDate(date: Date?): Long? = date?.time

    @TypeConverter
    fun toDate(timestamp: Long?): Date? = timestamp?.let { Date(it) }
}
```

## 5. 关系查询

```kotlin
// 一对多
data class UserWithPosts(
    @Embedded val user: UserEntity,
    @Relation(parentColumn = "id", entityColumn = "user_id")
    val posts: List<PostEntity>
)

@Dao
interface UserDao {
    @Transaction
    @Query("SELECT * FROM users WHERE id = :userId")
    fun getUserWithPosts(userId: Long): Flow<UserWithPosts>
}

// 多对多
data class UserWithTags(
    @Embedded val user: UserEntity,
    @Relation(
        parentColumn = "id",
        entityColumn = "id",
        associateBy = Junction(UserTagCrossRef::class, parentColumn = "userId", entityColumn = "tagId")
    )
    val tags: List<TagEntity>
)
```

## 6. Migration

```kotlin
val MIGRATION_1_2 = object : Migration(1, 2) {
    override fun migrate(db: SupportSQLiteDatabase) {
        db.execSQL("ALTER TABLE users ADD COLUMN avatar_url TEXT DEFAULT NULL")
    }
}

// 自动迁移（Room 2.4+）
@Database(
    version = 3,
    autoMigrations = [AutoMigration(from = 2, to = 3)]
)
abstract class AppDatabase : RoomDatabase()
```

## 7. Room 3.0 版本演进

> 🔄 更新于 2026-04-21

Room 3.0 alpha 已发布，是一个重大 Breaking 版本，核心目标是 Kotlin Multiplatform（KMP）全面支持。来源：[Android Developers Blog](https://developer.android.com/blog/posts/modernizing-the-room)

<!-- version-check: Room 2.8.4 stable, Room 3.0 alpha, checked 2026-04-21 -->

### Room 3.0 Breaking Changes

| 变化 | Room 2.x | Room 3.0 |
|------|----------|----------|
| 包名 | `androidx.room` | `androidx.room3` |
| Maven 坐标 | `androidx.room:room-runtime` | `androidx.room3:room3-runtime` |
| 数据库 API | SupportSQLite + SQLiteDriver | 仅 SQLiteDriver |
| 代码生成 | Java + Kotlin | 仅 Kotlin |
| 注解处理 | AP / KAPT / KSP | 仅 KSP |
| DAO 函数 | 支持阻塞函数 | 必须 suspend 或返回 Flow |
| KMP 支持 | Android + iOS + JVM | + JavaScript + WASM |

### 迁移路径

```kotlin
// Room 2.x → 3.0 迁移步骤：
// 1. 先迁移到 Room 2.8.x + SQLiteDriver API（兼容层）
// 2. 使用 room-sqlite-wrapper 过渡（Room 2.8.0 新增）
// 3. 更新包名 androidx.room → androidx.room3
// 4. 确保所有 DAO 函数为 suspend 或返回 Flow

// Room 3.0 DAO 示例（协程优先）
@Dao
interface UserDao {
    // ✅ Room 3.0：必须是 suspend
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(user: UserEntity)

    // ✅ Room 3.0：返回 Flow 的不需要 suspend
    @Query("SELECT * FROM users ORDER BY created_at DESC")
    fun getAllUsers(): Flow<List<UserEntity>>

    // ❌ Room 3.0 不再允许阻塞函数
    // @Query("SELECT * FROM users WHERE id = :userId")
    // fun getUserByIdBlocking(userId: Long): UserEntity?
}
```

### 版本选择建议

```
你的项目情况？
├─ 新项目 + 仅 Android → Room 2.8.4（稳定，等 3.0 稳定后迁移）
├─ 新项目 + KMP（Android + iOS） → Room 2.8.4 + SQLiteDriver
├─ 新项目 + KMP（含 JS/WASM） → Room 3.0 alpha（实验性）
├─ 现有项目 → 先迁移到 Room 2.8.x + SQLiteDriver
└─ 生产环境 → Room 2.8.4（不建议用 3.0 alpha）
```
## 🎬 推荐视频资源

- [Philipp Lackner - Room Database](https://www.youtube.com/watch?v=bOd3wO0uFr8) — Room数据库完整教程
- [CodingWithMitch - Room Persistence](https://www.youtube.com/watch?v=xPOIaKVFz5Y) — Room持久化教程
