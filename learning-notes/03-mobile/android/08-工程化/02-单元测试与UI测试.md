# 单元测试与 UI 测试
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. JUnit5 + MockK

```kotlin
// 依赖: io.mockk:mockk, org.junit.jupiter:junit-jupiter

class UserRepositoryTest {
    private val api = mockk<ApiService>()
    private val dao = mockk<UserDao>(relaxed = true)
    private lateinit var repository: UserRepository

    @BeforeEach
    fun setup() {
        repository = UserRepository(api, dao)
    }

    @Test
    fun `getUsers returns mapped users`() = runTest {
        val apiUsers = listOf(UserDto(1, "张三", "test@example.com"))
        coEvery { api.getUsers() } returns apiUsers

        val result = repository.getUsers()

        assertEquals(1, result.size)
        assertEquals("张三", result[0].name)
        coVerify { dao.insertAll(any()) }
    }

    @Test
    fun `getUsers throws on network error`() = runTest {
        coEvery { api.getUsers() } throws IOException("Network error")

        assertThrows<IOException> { repository.getUsers() }
    }
}
```

## 2. ViewModel 测试

```kotlin
@OptIn(ExperimentalCoroutinesApi::class)
class UserViewModelTest {
    @get:Rule
    val mainDispatcherRule = MainDispatcherRule()

    private val repository = mockk<UserRepository>()
    private lateinit var viewModel: UserViewModel

    @Test
    fun `loadUsers updates state to success`() = runTest {
        val users = listOf(User(1, "张三"))
        coEvery { repository.getUsers() } returns users

        viewModel = UserViewModel(repository)

        val state = viewModel.uiState.value
        assertEquals(users, state.users)
        assertFalse(state.isLoading)
    }

    @Test
    fun `loadUsers updates state to error on failure`() = runTest {
        coEvery { repository.getUsers() } throws Exception("Failed")

        viewModel = UserViewModel(repository)

        assertNotNull(viewModel.uiState.value.error)
    }
}

// MainDispatcherRule
class MainDispatcherRule(
    private val dispatcher: TestDispatcher = UnconfinedTestDispatcher()
) : TestWatcher() {
    override fun starting(description: Description) {
        Dispatchers.setMain(dispatcher)
    }
    override fun finished(description: Description) {
        Dispatchers.resetMain()
    }
}
```

## 3. Turbine（Flow 测试）

```kotlin
// 依赖: app.cash.turbine:turbine

@Test
fun `search flow emits filtered results`() = runTest {
    val viewModel = SearchViewModel(repository)

    viewModel.uiState.test {
        assertEquals(SearchUiState(), awaitItem())  // 初始状态

        viewModel.onSearch("kotlin")
        val loading = awaitItem()
        assertTrue(loading.isLoading)

        val success = awaitItem()
        assertFalse(success.isLoading)
        assertTrue(success.results.isNotEmpty())

        cancelAndIgnoreRemainingEvents()
    }
}
```

## 4. Espresso（View UI 测试）

```kotlin
@RunWith(AndroidJUnit4::class)
class LoginActivityTest {
    @get:Rule
    val activityRule = ActivityScenarioRule(LoginActivity::class.java)

    @Test
    fun loginWithValidCredentials() {
        onView(withId(R.id.etUsername))
            .perform(typeText("admin"), closeSoftKeyboard())

        onView(withId(R.id.etPassword))
            .perform(typeText("password"), closeSoftKeyboard())

        onView(withId(R.id.btnLogin)).perform(click())

        onView(withId(R.id.tvWelcome))
            .check(matches(isDisplayed()))
            .check(matches(withText(containsString("欢迎"))))
    }
}
```

## 5. Compose Testing

```kotlin
class UserListScreenTest {
    @get:Rule
    val composeTestRule = createComposeRule()

    @Test
    fun displayUserList() {
        val users = listOf(User(1, "张三"), User(2, "李四"))

        composeTestRule.setContent {
            MyTheme { UserList(users = users, onItemClick = {}) }
        }

        composeTestRule.onNodeWithText("张三").assertIsDisplayed()
        composeTestRule.onNodeWithText("李四").assertIsDisplayed()
    }

    @Test
    fun clickUserNavigatesToDetail() {
        var clickedId: Int? = null
        val users = listOf(User(1, "张三"))

        composeTestRule.setContent {
            UserList(users = users, onItemClick = { clickedId = it })
        }

        composeTestRule.onNodeWithText("张三").performClick()
        assertEquals(1, clickedId)
    }

    @Test
    fun emptyStateShown() {
        composeTestRule.setContent {
            UserList(users = emptyList(), onItemClick = {})
        }

        composeTestRule.onNodeWithText("暂无数据").assertIsDisplayed()
    }
}
```
