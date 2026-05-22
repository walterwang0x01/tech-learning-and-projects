# Combine 响应式编程
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Publisher 与 Subscriber

```swift
import Combine

// 基础发布者
let publisher = [1, 2, 3, 4, 5].publisher
publisher.sink { completion in
    print("完成: \(completion)")
} receiveValue: { value in
    print("收到: \(value)")
}

// Just: 发送单个值
let just = Just("Hello Combine")
just.sink { print($0) }

// Future: 异步单次结果
let future = Future<String, Error> { promise in
    DispatchQueue.global().asyncAfter(deadline: .now() + 1) {
        promise(.success("异步结果"))
    }
}
```

## 2. 常用操作符

```swift
var cancellables = Set<AnyCancellable>()

// map / filter / compactMap
[1, 2, 3, 4, 5].publisher
    .filter { $0 % 2 == 0 }
    .map { "数字: \($0)" }
    .sink { print($0) }
    .store(in: &cancellables)

// flatMap: 将值转换为新的 Publisher
func fetchUser(id: Int) -> AnyPublisher<User, Error> { /* ... */ }

[1, 2, 3].publisher
    .flatMap { id in fetchUser(id: id) }
    .sink(receiveCompletion: { _ in }, receiveValue: { print($0) })
    .store(in: &cancellables)

// combineLatest: 合并多个流
let name = CurrentValueSubject<String, Never>("张三")
let age = CurrentValueSubject<Int, Never>(25)

name.combineLatest(age)
    .map { "\($0) - \($1)岁" }
    .sink { print($0) }
    .store(in: &cancellables)

// debounce: 防抖（搜索场景）
searchTextField.textPublisher
    .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
    .removeDuplicates()
    .sink { query in search(query) }
    .store(in: &cancellables)
```

## 3. Subject

```swift
// PassthroughSubject: 无初始值
let eventBus = PassthroughSubject<String, Never>()
eventBus.sink { print("事件: \($0)") }.store(in: &cancellables)
eventBus.send("用户登录")
eventBus.send("数据刷新")

// CurrentValueSubject: 有初始值
let counter = CurrentValueSubject<Int, Never>(0)
counter.sink { print("计数: \($0)") }.store(in: &cancellables)
counter.value += 1  // 直接修改
counter.send(10)    // 发送新值
print(counter.value) // 读取当前值
```

## 4. @Published 属性包装器

```swift
class LoginViewModel: ObservableObject {
    @Published var username = ""
    @Published var password = ""
    @Published var isLoginEnabled = false
    @Published var errorMessage: String?

    private var cancellables = Set<AnyCancellable>()

    init() {
        // 组合多个 @Published 属性
        $username.combineLatest($password)
            .map { !$0.isEmpty && $1.count >= 6 }
            .assign(to: &$isLoginEnabled)
    }

    func login() {
        $username
            .combineLatest($password)
            .first()
            .flatMap { [weak self] username, password in
                self?.authService.login(username: username, password: password)
                    ?? Fail(error: AuthError.unknown).eraseToAnyPublisher()
            }
            .sink(
                receiveCompletion: { [weak self] completion in
                    if case .failure(let error) = completion {
                        self?.errorMessage = error.localizedDescription
                    }
                },
                receiveValue: { token in print("登录成功: \(token)") }
            )
            .store(in: &cancellables)
    }
}
```

## 5. Cancellable 生命周期管理

```swift
class MyViewController: UIViewController {
    private var cancellables = Set<AnyCancellable>()

    override func viewDidLoad() {
        super.viewDidLoad()

        // 订阅会在 cancellables 被释放时自动取消
        NotificationCenter.default.publisher(for: UIApplication.didBecomeActiveNotification)
            .sink { _ in print("App 激活") }
            .store(in: &cancellables)
    }

    // 手动取消
    private var singleCancellable: AnyCancellable?

    func startListening() {
        singleCancellable = timer.sink { print($0) }
    }

    func stopListening() {
        singleCancellable?.cancel()
        singleCancellable = nil
    }
}
```

## 6. 错误处理

```swift
URLSession.shared.dataTaskPublisher(for: url)
    .map(\.data)
    .decode(type: [User].self, decoder: JSONDecoder())
    .retry(2)                          // 失败重试2次
    .catch { _ in Just([]) }           // 错误时返回空数组
    .receive(on: DispatchQueue.main)
    .assign(to: &$users)
```

## 7. Combine 在 2026 年的定位

<!-- version-check: Combine framework, Swift 6.2, iOS 26, checked 2026-04-23 -->

> 🔄 更新于 2026-04-23

### Combine vs async/await：何时用哪个

Apple 自 Swift 5.5 引入 async/await 后，Combine 的定位逐渐收窄。2026 年的共识是：

| 场景 | 推荐方案 | 原因 |
|------|---------|------|
| 网络请求 | async/await | 更简洁，错误处理更直观 |
| 单次异步操作 | async/await | Future 过于冗长 |
| 多值流（实时数据） | AsyncSequence 或 Combine | 两者都可，AsyncSequence 更轻量 |
| 搜索防抖 | Combine | `debounce` + `removeDuplicates` 仍是最优雅的方案 |
| UIKit 数据绑定 | Combine | `@Published` + `sink` 是 UIKit 响应式绑定的标准方式 |
| SwiftUI 状态管理 | @Observable | 不再需要 Combine 做 SwiftUI 绑定 |
| 多流合并/转换 | Combine | `combineLatest`、`merge`、`zip` 等操作符仍然强大 |

### 从 Combine 迁移到 async/await

```swift
// 旧方式：Combine 网络请求
func fetchUsersCombine() -> AnyPublisher<[User], Error> {
    URLSession.shared.dataTaskPublisher(for: url)
        .map(\.data)
        .decode(type: [User].self, decoder: JSONDecoder())
        .eraseToAnyPublisher()
}

// 新方式：async/await（推荐）
func fetchUsers() async throws -> [User] {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode([User].self, from: data)
}

// 旧方式：Combine 搜索防抖
$searchText
    .debounce(for: .milliseconds(300), scheduler: RunLoop.main)
    .removeDuplicates()
    .sink { query in self.search(query) }
    .store(in: &cancellables)

// 新方式：AsyncSequence 搜索防抖（iOS 17+）
// 注意：AsyncSequence 目前没有内置 debounce，
// 搜索防抖场景 Combine 仍然更优雅
```

### 2026 年建议

- **新 SwiftUI 项目**：优先 async/await + @Observable，Combine 仅用于复杂流操作
- **UIKit 项目**：Combine 仍是数据绑定的最佳选择
- **混合项目**：网络层用 async/await，UI 绑定层按框架选择
- Combine 不会被废弃，但 Apple 已停止为其添加新功能

来源：[Swift Forums - Move from Combine to Swift concurrency?](https://forums.swift.org/t/move-from-combine-to-swift-concurrency) | [Swift 6 Concurrency Patterns](https://ignit.group/blog/swift-6-concurrency-advanced-patterns-2-3)

## 8. Apple 官方信号：Combine 在 SwiftUI 中正式落幕

<!-- version-check: Apple AI guidance "Avoid Combine", Observation framework, Observations type, checked 2026-05-22 -->

> 🔄 更新于 2026-05-22

### 8.1 Apple Intelligence 的明确指引

Apple 在自家 AI 模型的代码生成指引中，**已显式要求避免使用 Combine**——这是迄今最强烈的信号，表明 SwiftUI 中 Combine 时代正式落幕。Observation framework 也在持续成熟，最新加入了 `Observations` 类型，提供更细粒度的订阅控制。

来源：[Captain SwiftUI - Objectively Better, Observably Trickier](https://captainswiftui.substack.com/p/objectively-better-observably-trickier)、[@Observable Beyond SwiftUI](https://open.substack.com/pub/krishna806083/p/observable-beyond-swiftui)、[Forasoft - 2026 iOS Architecture](https://www.forasoft.com/blog/article/advanced-ios-app-architecture-explained-on-mvvm-977)

### 8.2 2026 年 SwiftUI 推荐栈

| 维度 | 推荐方案 | 取代的旧方案 |
|------|---------|-------------|
| 状态管理 | `@Observable` 类 | `ObservableObject` + `@Published` |
| 异步加载 | `async/await` + `.task {}` | `Combine.Future` / `dataTaskPublisher` |
| 多值流 | `AsyncSequence` / `Observations` | `Publisher` |
| 防抖 | 自定义 actor 或第三方 | `Combine.debounce` |
| 跨视图同步 | `@Environment` + `@Observable` | `EnvironmentObject` + `@Published` |

来源：Forasoft 实测数据，2026 iOS MVVM 栈相比 2022 版本可减少 **30-50% 样板代码**，但要求开发者掌握 actor 隔离与所有权规则。

### 8.3 App Store Connect 强制 SDK 26（2026-04-28 起）

```
2026-04-28 起，所有提交到 App Store Connect 的应用必须使用 SDK 26 构建。
```

这进一步加速了迁移：使用 SDK 26 编译时，Xcode 会对 `ObservableObject` 等旧 API 提示更强烈的弃用警告，为 iOS 27（预计 2026-09 随 WWDC26 发布）做准备。来源：[iOS Weekly Brief Issue 46](https://vladkhambir.substack.com/p/the-ios-weekly-brief-issue-46)

### 8.4 迁移路径建议

1. **新项目**：直接用 `@Observable` + `async/await`，不引入 Combine
2. **存量项目（< 5 万行）**：Combine → @Observable 一次性迁移，复杂流操作用 AsyncSequence + 自定义 actor
3. **存量项目（> 5 万行）**：渐进式迁移——View Model 层先迁移到 @Observable，网络层先迁移到 async/await，跨流合并/防抖暂时保留 Combine
4. **UIKit 部分**：保持 Combine，无需变更
5. **测试代码**：注意 @Observable 的测试需要订阅 `withObservationTracking` 而非 `@Published`，旧测试可能需要重写

来源：[Bluewaves Combine Migration Skill](https://playbooks.com/skills/bluewaves-creations/bluewaves-skills/combine-migration)、[Refactoring Combine to async](https://kylenazario.com/blog/refactoring-swift-combine-to-async-await)
