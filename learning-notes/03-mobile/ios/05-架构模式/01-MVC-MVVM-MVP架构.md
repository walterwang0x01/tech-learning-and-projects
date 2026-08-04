# MVC / MVVM / MVP 架构
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. MVC（Apple 默认）

```swift
// Controller 承担过多职责（Massive View Controller 问题）
class UserListViewController: UIViewController {
    private let tableView = UITableView()
    private var users: [User] = []

    override func viewDidLoad() {
        super.viewDidLoad()
        // 网络请求、数据解析、UI 配置、事件处理全在 Controller
        fetchUsers()
    }

    func fetchUsers() {
        URLSession.shared.dataTask(with: url) { data, _, _ in
            self.users = try! JSONDecoder().decode([User].self, from: data!)
            DispatchQueue.main.async { self.tableView.reloadData() }
        }.resume()
    }
}
```

## 2. MVVM 架构

```swift
// Model
struct User: Codable, Identifiable {
    let id: Int
    let name: String
    let email: String
}

// ViewModel
class UserListViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    private let repository: UserRepository

    init(repository: UserRepository = UserRepository()) {
        self.repository = repository
    }

    @MainActor
    func fetchUsers() async {
        isLoading = true
        defer { isLoading = false }
        do {
            users = try await repository.getUsers()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

// View (SwiftUI)
struct UserListView: View {
    @StateObject private var viewModel = UserListViewModel()

    var body: some View {
        List(viewModel.users) { user in
            Text(user.name)
        }
        .overlay { if viewModel.isLoading { ProgressView() } }
        .task { await viewModel.fetchUsers() }
    }
}
```

## 3. MVVM + UIKit（Combine 绑定）

```swift
class UserListViewController: UIViewController {
    private let viewModel = UserListViewModel()
    private var cancellables = Set<AnyCancellable>()

    override func viewDidLoad() {
        super.viewDidLoad()
        bindViewModel()
        Task { await viewModel.fetchUsers() }
    }

    private func bindViewModel() {
        viewModel.$users
            .receive(on: DispatchQueue.main)
            .sink { [weak self] _ in self?.tableView.reloadData() }
            .store(in: &cancellables)

        viewModel.$isLoading
            .receive(on: DispatchQueue.main)
            .sink { [weak self] loading in
                loading ? self?.spinner.startAnimating() : self?.spinner.stopAnimating()
            }
            .store(in: &cancellables)
    }
}
```

## 4. MVP 架构

```swift
// Presenter 协议
protocol UserListPresenter {
    func viewDidLoad()
    func didSelectUser(at index: Int)
}

// View 协议
protocol UserListViewProtocol: AnyObject {
    func showUsers(_ users: [User])
    func showLoading()
    func hideLoading()
    func showError(_ message: String)
}

// Presenter 实现
class UserListPresenterImpl: UserListPresenter {
    weak var view: UserListViewProtocol?
    private let repository: UserRepository

    init(view: UserListViewProtocol, repository: UserRepository) {
        self.view = view
        self.repository = repository
    }

    func viewDidLoad() {
        view?.showLoading()
        Task {
            do {
                let users = try await repository.getUsers()
                await MainActor.run {
                    view?.hideLoading()
                    view?.showUsers(users)
                }
            } catch {
                await MainActor.run { view?.showError(error.localizedDescription) }
            }
        }
    }

    func didSelectUser(at index: Int) { /* 导航逻辑 */ }
}
```

## 5. VIPER 概览

```swift
// VIPER 五层：View - Interactor - Presenter - Entity - Router
// View: 显示 UI
// Interactor: 业务逻辑
// Presenter: 连接 View 和 Interactor
// Entity: 数据模型
// Router: 页面跳转

protocol UserRouterProtocol {
    func navigateToDetail(user: User)
}

protocol UserInteractorProtocol {
    func fetchUsers() async throws -> [User]
}
```
## 🎬 推荐视频资源

- [Sean Allen - MVVM in SwiftUI](https://www.youtube.com/watch?v=wEf1YS4vyW8) — SwiftUI MVVM架构
- [Essential Developer - iOS Architecture](https://www.youtube.com/c/EssentialDeveloper) — iOS架构设计频道

## 6. 2026 年 iOS 架构选型建议

<!-- version-check: iOS Architecture 2026, @Observable (iOS 17+), Swift 6.2, checked 2026-04-23 -->

> 🔄 更新于 2026-04-23

### @Observable 替代 ObservableObject

iOS 17+ 引入的 `@Observable` 宏已成为 2026 年 SwiftUI MVVM 的推荐方案，替代 `ObservableObject` + `@Published`：

```swift
import Observation

// 2026 推荐：@Observable（iOS 17+）
@Observable
class UserListViewModel {
    var users: [User] = []
    var isLoading = false
    var errorMessage: String?

    private let repository: UserRepository

    init(repository: UserRepository = UserRepository()) {
        self.repository = repository
    }

    func fetchUsers() async {
        isLoading = true
        defer { isLoading = false }
        do {
            users = try await repository.getUsers()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

// View 不再需要 @StateObject，直接用 @State
struct UserListView: View {
    @State private var viewModel = UserListViewModel()

    var body: some View {
        List(viewModel.users) { user in
            Text(user.name)
        }
        .overlay { if viewModel.isLoading { ProgressView() } }
        .task { await viewModel.fetchUsers() }
    }
}
```

### @Observable vs ObservableObject 对比

| 特性 | @Observable (iOS 17+) | ObservableObject |
|------|----------------------|-----------------|
| 属性标注 | 无需（自动追踪） | 需要 `@Published` |
| View 注入 | `@State` | `@StateObject` / `@ObservedObject` |
| 性能 | 属性级精确追踪 | 对象级通知（任一属性变化触发全部） |
| Environment | `@Environment(ViewModel.self)` | `@EnvironmentObject` |
| 最低版本 | iOS 17 | iOS 13 |

### 架构选型决策树（2026）

```
新项目（iOS 17+）
├── SwiftUI 为主 → MVVM + @Observable
│   ├── 小型项目 → 直接 @Observable ViewModel
│   └── 大型项目 → Clean Architecture + @Observable
├── UIKit 为主 → MVVM + Combine 绑定
└── 混合项目 → MVVM + @Observable（SwiftUI）+ Combine（UIKit）

维护项目
├── 已用 ObservableObject → 逐步迁移到 @Observable
├── 已用 MVC → 新模块用 MVVM，旧模块保持
└── 已用 VIPER → 继续维护，新模块可简化为 MVVM
```

来源：[Apple Observation Framework](https://developer.apple.com/documentation/observation) | [SwiftUI MVVM 2026 Best Practices](https://copyprogramming.com/howto/ios-app-architecture)
