# SwiftUI 导航与路由
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. NavigationStack（iOS 16+）

```swift
struct ContentView: View {
    @State private var path = NavigationPath()

    var body: some View {
        NavigationStack(path: $path) {
            List(users) { user in
                NavigationLink(value: user) {
                    Text(user.name)
                }
            }
            .navigationTitle("用户列表")
            .navigationDestination(for: User.self) { user in
                UserDetailView(user: user)
            }
        }
    }

    // 编程式导航
    func navigateToUser(_ user: User) {
        path.append(user)
    }

    func popToRoot() {
        path = NavigationPath()
    }
}
```

## 2. Sheet / FullScreenCover

```swift
struct ContentView: View {
    @State private var showSheet = false
    @State private var showFullScreen = false

    var body: some View {
        VStack {
            Button("打开 Sheet") { showSheet = true }
            Button("全屏弹窗") { showFullScreen = true }
        }
        .sheet(isPresented: $showSheet) {
            SettingsView()
                .presentationDetents([.medium, .large])  // 半屏
        }
        .fullScreenCover(isPresented: $showFullScreen) {
            LoginView()
        }
    }
}
```

## 3. TabView

```swift
struct MainTabView: View {
    @State private var selectedTab = 0

    var body: some View {
        TabView(selection: $selectedTab) {
            HomeView()
                .tabItem { Label("首页", systemImage: "house") }
                .tag(0)
            SearchView()
                .tabItem { Label("搜索", systemImage: "magnifyingglass") }
                .tag(1)
            ProfileView()
                .tabItem { Label("我的", systemImage: "person") }
                .tag(2)
        }
    }
}
```

## 4. 路由管理

```swift
// 集中式路由管理
enum Route: Hashable {
    case userDetail(User)
    case settings
    case editProfile
}

class Router: ObservableObject {
    @Published var path = NavigationPath()

    func navigate(to route: Route) { path.append(route) }
    func pop() { path.removeLast() }
    func popToRoot() { path = NavigationPath() }
}
```
<!-- 修复于 2026-05-31: 第4节 Router 代码块缺少闭合标记，导致第5节内容渲染错乱 -->

## 5. iOS 26 导航与 TabView 新特性

> 🔄 更新于 2026-04-18

<!-- version-check: SwiftUI Navigation iOS 26, checked 2026-04-18 -->

iOS 26 为 TabView 和搜索功能带来了重要改进。来源：[SwiftUI in iOS 26 - What's new](https://differ.blog/p/swift-ui-in-ios-26-what-s-new-from-wwdc-2025-819b42)

### TabView 搜索标签

可以在 TabView 中添加专用的搜索标签页，类似 Apple 健康和音乐应用的体验。

```swift
struct MainTabView: View {
    var body: some View {
        TabView {
            Tab("首页", systemImage: "house") {
                HomeView()
            }
            // 新增：搜索标签页（.search role）
            Tab("搜索", systemImage: "magnifyingglass", role: .search) {
                SearchView()
            }
            Tab("我的", systemImage: "person") {
                ProfileView()
            }
        }
    }
}
```

### iPad 菜单栏命令

SwiftUI 应用现在可以在 iPad 上添加原生菜单栏命令，与 macOS 体验一致。

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .commands {
            TextEditingCommands()  // 标准编辑命令（剪切、复制、粘贴）
            // 自定义命令
            CommandMenu("工具") {
                Button("格式化") { format() }
                    .keyboardShortcut("f", modifiers: [.command, .shift])
            }
        }
    }
}
```

### UIHostingSceneDelegate

新增 `UIHostingSceneDelegate`，可以将 SwiftUI Scene 桥接到 UIKit，扩展了 SwiftUI 与 UIKit 的集成能力。
