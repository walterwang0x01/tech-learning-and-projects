# SwiftUI 状态管理
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. @State

```swift
// 视图内部的简单状态
struct CounterView: View {
    @State private var count = 0

    var body: some View {
        VStack {
            Text("Count: \(count)")
            Button("+1") { count += 1 }
        }
    }
}
```

## 2. @Binding

```swift
// 父子组件共享状态
struct ParentView: View {
    @State private var isOn = false

    var body: some View {
        ToggleView(isOn: $isOn)  // 传递 Binding
    }
}

struct ToggleView: View {
    @Binding var isOn: Bool

    var body: some View {
        Toggle("开关", isOn: $isOn)
    }
}
```

## 3. @StateObject / @ObservedObject

```swift
// ObservableObject（iOS 13+）
class UserViewModel: ObservableObject {
    @Published var users: [User] = []
    @Published var isLoading = false
    @Published var errorMessage: String?

    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }
        do {
            users = try await UserService.fetchUsers()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

// @StateObject（创建并持有，视图重建不会重新创建）
struct UserListView: View {
    @StateObject private var viewModel = UserViewModel()

    var body: some View {
        List(viewModel.users) { user in
            Text(user.name)
        }
        .task { await viewModel.loadUsers() }
    }
}

// @ObservedObject（外部传入，不持有）
struct UserDetailView: View {
    @ObservedObject var viewModel: UserViewModel
    // ...
}
```

## 4. @EnvironmentObject

```swift
// 跨层级共享状态
class AppState: ObservableObject {
    @Published var isLoggedIn = false
    @Published var currentUser: User?
    @Published var theme: Theme = .light
}

// 注入
@main
struct MyApp: App {
    @StateObject private var appState = AppState()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
        }
    }
}

// 任意子视图中使用
struct ProfileView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        if let user = appState.currentUser {
            Text("Hello, \(user.name)")
        }
    }
}
```

## 5. @Observable（iOS 17+）

```swift
import Observation

// 更简洁的状态管理
@Observable
class UserViewModel {
    var users: [User] = []
    var isLoading = false
    var errorMessage: String?

    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }
        do {
            users = try await UserService.fetchUsers()
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

// 使用（不需要 @StateObject/@ObservedObject）
struct UserListView: View {
    @State private var viewModel = UserViewModel()

    var body: some View {
        List(viewModel.users) { user in
            Text(user.name)
        }
        .task { await viewModel.loadUsers() }
    }
}
```
## 6. @Observable 改进与 iOS 26 更新

> 🔄 更新于 2026-04-18

<!-- version-check: SwiftUI @Observable iOS 26, checked 2026-04-18 -->

### @Observable 成为推荐方案

随着 iOS 17+ 的 `@Observable` 宏成熟，它已成为 SwiftUI 状态管理的推荐方案。在 iOS 26 / Xcode 26 中，`@Observable` 与 Liquid Glass 设计语言完全兼容，性能进一步优化。

```swift
import Observation

// 推荐：使用 @Observable（iOS 17+）
@Observable
class AppState {
    var isLoggedIn = false
    var currentUser: User?
    var theme: Theme = .light

    // 计算属性自动追踪依赖
    var greeting: String {
        guard let user = currentUser else { return "请登录" }
        return "你好，\(user.name)"
    }
}

// 使用 @State 持有（替代 @StateObject）
struct ContentView: View {
    @State private var appState = AppState()

    var body: some View {
        // 直接传递，无需 @EnvironmentObject
        NavigationStack {
            HomeView(appState: appState)
        }
        // 也可以通过 Environment 注入
        .environment(appState)
    }
}

// 子视图直接接收
struct HomeView: View {
    var appState: AppState  // 无需 @ObservedObject

    var body: some View {
        Text(appState.greeting)
    }
}

// 或通过 @Environment 获取
struct ProfileView: View {
    @Environment(AppState.self) private var appState

    var body: some View {
        Text(appState.greeting)
    }
}
```

### 状态管理方案选择指南（2026）

| 方案 | 适用场景 | 最低版本 |
|------|---------|---------|
| `@State` | 视图内部简单状态 | iOS 13+ |
| `@Binding` | 父子组件共享状态 | iOS 13+ |
| `@Observable` + `@State` | **推荐**：ViewModel 和共享状态 | iOS 17+ |
| `@Observable` + `@Environment` | **推荐**：跨层级共享 | iOS 17+ |
| `@StateObject` / `@ObservedObject` | 兼容 iOS 13-16 的旧项目 | iOS 13+ |
| `@EnvironmentObject` | 兼容 iOS 13-16 的旧项目 | iOS 13+ |

> **迁移建议**：新项目最低支持 iOS 17 时，全面使用 `@Observable` 替代 `ObservableObject`。`@StateObject` / `@ObservedObject` / `@EnvironmentObject` 仅在需要兼容旧版本时使用。

## 7. WWDC26：`@State` 变为宏 + `@Observable` 惰性初始化

> 更新于 2026-07-10

<!-- version-check: SwiftUI @State macro + lazy Observable init, WWDC26 2027 releases (back-ported to iOS 17/macOS 14), checked 2026-07-10 -->

2027 releases 中 `@State` 从 Dynamic Property **转变为宏**，带来一个此前一直存在的性能陷阱的修复：存储在 `@State` 里的 `@Observable` 类实例，此前每次父视图重新初始化时都会创建一次新实例（哪怕最终会被 SwiftUI 丢弃），现在**整个视图生命周期内只初始化一次**。

```swift
struct StickerStoreView: View {
    // 2027 releases 起：AppState() 只在视图生命周期内构造一次，
    // 父视图反复 init 不再触发重复分配
    @State private var appState = AppState()

    var body: some View {
        HomeView(appState: appState)
    }
}
```

**关键点**：

- 这不是新 API，代码写法完全不变——纯粹是编译器/运行时层面的优化，**无需修改现有代码**即可受益
- 官方明确**反向移植**到 `@Observable` 最早支持的版本：iOS 17、macOS 14 及对齐平台版本，不是 iOS 27 专属特性
- 对高频重建的列表 / 容器视图（如 `List` 内每行都持有一个 `@Observable` 状态）收益最明显，减少了大量本可避免的对象分配

来源：[WWDC26 SwiftUI guide](https://developer.apple.com/wwdc26/guides/swiftui/)、[What's new in SwiftUI - WWDC26 视频](https://developer.apple.com/videos/play/wwdc2026/269/)

## 🎬 推荐视频资源

- [Swiftful Thinking - SwiftUI State Management](https://www.youtube.com/watch?v=KD4OAjQJYPc) — SwiftUI状态管理
- [Sean Allen - @State @Binding @ObservedObject](https://www.youtube.com/watch?v=stSB04C4iS4) — 属性包装器详解
