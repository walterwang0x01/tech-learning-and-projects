# Clean Architecture 实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 分层架构概览

```
┌─────────────────────────────┐
│   Presentation Layer        │  ← ViewModel, View, Coordinator
├─────────────────────────────┤
│   Domain Layer              │  ← UseCase, Entity, Repository Protocol
├─────────────────────────────┤
│   Data Layer                │  ← Repository Impl, API, Database
└─────────────────────────────┘
依赖方向：外层 → 内层（Domain 不依赖任何外层）
```

## 2. Domain Layer（核心业务）

```swift
// Entity
struct User {
    let id: Int
    let name: String
    let email: String
}

// Repository 协议（定义在 Domain 层）
protocol UserRepository {
    func getUsers() async throws -> [User]
    func getUser(id: Int) async throws -> User
    func saveUser(_ user: User) async throws
}

// Use Case
class FetchUsersUseCase {
    private let repository: UserRepository

    init(repository: UserRepository) {
        self.repository = repository
    }

    func execute() async throws -> [User] {
        try await repository.getUsers()
    }
}

class GetUserDetailUseCase {
    private let repository: UserRepository

    init(repository: UserRepository) {
        self.repository = repository
    }

    func execute(id: Int) async throws -> User {
        try await repository.getUser(id: id)
    }
}
```

## 3. Data Layer（数据实现）

```swift
// DTO（Data Transfer Object）
struct UserDTO: Codable {
    let id: Int
    let name: String
    let email: String

    func toDomain() -> User {
        User(id: id, name: name, email: email)
    }
}

// Repository 实现
class UserRepositoryImpl: UserRepository {
    private let remoteDataSource: UserRemoteDataSource
    private let localDataSource: UserLocalDataSource

    init(remote: UserRemoteDataSource, local: UserLocalDataSource) {
        self.remoteDataSource = remote
        self.localDataSource = local
    }

    func getUsers() async throws -> [User] {
        do {
            let dtos = try await remoteDataSource.fetchUsers()
            let users = dtos.map { $0.toDomain() }
            try await localDataSource.cacheUsers(dtos)  // 缓存
            return users
        } catch {
            // 网络失败时读取缓存
            let cached = try await localDataSource.getCachedUsers()
            return cached.map { $0.toDomain() }
        }
    }

    func getUser(id: Int) async throws -> User {
        let dto = try await remoteDataSource.fetchUser(id: id)
        return dto.toDomain()
    }

    func saveUser(_ user: User) async throws {
        try await remoteDataSource.createUser(user)
    }
}

// Remote Data Source
class UserRemoteDataSource {
    private let apiClient: APIClient

    init(apiClient: APIClient) { self.apiClient = apiClient }

    func fetchUsers() async throws -> [UserDTO] {
        try await apiClient.request("/users")
    }

    func fetchUser(id: Int) async throws -> UserDTO {
        try await apiClient.request("/users/\(id)")
    }
}
```

## 4. Presentation Layer

```swift
class UserListViewModel: ObservableObject {
    @Published var users: [UserViewData] = []
    @Published var isLoading = false

    private let fetchUsersUseCase: FetchUsersUseCase

    init(fetchUsersUseCase: FetchUsersUseCase) {
        self.fetchUsersUseCase = fetchUsersUseCase
    }

    @MainActor
    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }
        do {
            let domainUsers = try await fetchUsersUseCase.execute()
            users = domainUsers.map { UserViewData(name: $0.name, email: $0.email) }
        } catch {
            // 处理错误
        }
    }
}

// View Data（展示模型）
struct UserViewData: Identifiable {
    let id = UUID()
    let name: String
    let email: String
}
```

## 5. 组装依赖

```swift
class AppDIContainer {
    // Data Layer
    lazy var apiClient = APIClient.shared
    lazy var remoteDataSource = UserRemoteDataSource(apiClient: apiClient)
    lazy var localDataSource = UserLocalDataSource()
    lazy var userRepository: UserRepository = UserRepositoryImpl(
        remote: remoteDataSource, local: localDataSource
    )

    // Domain Layer
    func makeFetchUsersUseCase() -> FetchUsersUseCase {
        FetchUsersUseCase(repository: userRepository)
    }

    // Presentation Layer
    func makeUserListViewModel() -> UserListViewModel {
        UserListViewModel(fetchUsersUseCase: makeFetchUsersUseCase())
    }
}
```

## 6. 2026 现代版 Clean Architecture

> 🔄 更新于 2026-05-18

<!-- version-check: Swift 6.2 strict concurrency, @Observable, TCA 1.20+, checked 2026-05-18 -->

iOS 进入 Swift 6.2 + iOS 26 时代后，Clean Architecture 在保留四层结构的同时，重点变化集中在「响应式层」与「Actor 隔离」。来源：[Forasoft - Advanced iOS App Architecture 2026](https://www.forasoft.com/blog/article/advanced-ios-app-architecture-explained-on-mvvm-977)、[7span - MVVM vs Clean Architecture vs TCA](https://7span.com/blog/mvvm-vs-clean-architecture-vs-tca)

### 6.1 用 @Observable 替代 ObservableObject

```swift
import Observation

// 旧版本（继续可用，但 SwiftUI 项目优先迁移）
class UserListViewModel_v1: ObservableObject {
    @Published var users: [User] = []
}

// 2026 推荐：@Observable，支持属性级精确追踪
@Observable
@MainActor
final class UserListViewModel {
    private(set) var users: [User] = []
    private(set) var isLoading = false
    private(set) var errorMessage: String?

    private let fetchUsersUseCase: FetchUsersUseCase

    init(fetchUsersUseCase: FetchUsersUseCase) {
        self.fetchUsersUseCase = fetchUsersUseCase
    }

    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }
        do {
            let domainUsers = try await fetchUsersUseCase.execute()
            users = domainUsers
        } catch {
            errorMessage = (error as? LocalizedError)?.errorDescription ?? "未知错误"
        }
    }
}

// View 直接使用 @State 持有
struct UserListView: View {
    @State private var viewModel: UserListViewModel

    init(viewModel: UserListViewModel) {
        _viewModel = State(initialValue: viewModel)
    }

    var body: some View {
        List(viewModel.users) { user in Text(user.name) }
            .overlay { if viewModel.isLoading { ProgressView() } }
            .task { await viewModel.loadUsers() }
    }
}
```

### 6.2 Swift 6 严格并发对各层的约束

Swift 6.2 的 Approachable Concurrency 默认让模块级 Actor 隔离为 `MainActor`。Clean Architecture 各层需要显式声明执行域：

| 层 | 推荐隔离 | 原因 |
| -- | -- | -- |
| Presentation（ViewModel） | `@MainActor` | UI 更新必须在主线程 |
| Domain（UseCase） | `nonisolated` | 纯逻辑，由调用方决定执行域 |
| Data（Repository / DataSource） | actor 或 `nonisolated` + `Sendable` | 共享缓存/连接需序列化访问 |
| 模型（Entity / DTO） | `Sendable` 值类型 | 跨 actor 安全传递 |

```swift
// Domain 层：纯函数式 UseCase，不绑定线程
struct FetchUsersUseCase: Sendable {
    let repository: any UserRepository

    func callAsFunction() async throws -> [User] {
        try await repository.getUsers()
    }
}

// Data 层：用 actor 包装可变缓存
actor UserCache {
    private var cache: [Int: User] = [:]

    func get(_ id: Int) -> User? { cache[id] }
    func set(_ user: User) { cache[user.id] = user }
}

final class UserRepositoryImpl: UserRepository, Sendable {
    private let remote: UserRemoteDataSource
    private let cache = UserCache()

    init(remote: UserRemoteDataSource) { self.remote = remote }

    func getUsers() async throws -> [User] {
        let users = try await remote.fetchUsers()
        for u in users { await cache.set(u) }
        return users
    }
}
```

> ⚠️ 待确认：将 Repository 实现声明为 `Sendable` 时，必须确保所有可变状态都封装在 actor 内或使用 `let`。否则 Swift 6 的严格检查会在编译期报错。

### 6.3 与 TCA 的取舍（2026）

The Composable Architecture（[swift-composable-architecture](https://github.com/pointfreeco/swift-composable-architecture)，14K+ Stars，1.20.x 已支持 Swift 6 / @Observable）适合状态高度结构化、对可测试性要求极高的项目；普通业务 App 使用 MVVM + @Observable + Clean Architecture 即可。

```
项目类型决策树（2026）
├── 强一致状态 + 多设备同步 + 重测试覆盖 → TCA
├── 中大型业务 App + 团队熟悉 SwiftUI → @Observable + Clean Architecture
└── 小型 / 工具类 App → 直接 @Observable ViewModel + 单层 Repository
```

### 6.4 与历史代码并存

```swift
// 同一项目内允许：
// - 旧模块继续使用 ObservableObject + MVC
// - 新模块采用 @Observable + Clean Architecture
// - 共享 Domain 层（UseCase / Entity）保持纯净，不感知 UI 框架
```

来源：[Apple Developer - Observation](https://developer.apple.com/documentation/Observation)、[@Observable Beyond SwiftUI](https://open.substack.com/pub/krishna806083/p/observable-beyond-swiftui)、[Captain SwiftUI - Objectively Better, Observably Trickier](https://captainswiftui.substack.com/p/objectively-better-observably-trickier)
