# Swift 并发编程
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. async/await

```swift
// 异步函数
func fetchUser(id: Int) async throws -> User {
    let url = URL(string: "https://api.example.com/users/\(id)")!
    let (data, response) = try await URLSession.shared.data(from: url)
    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw NetworkError.serverError
    }
    return try JSONDecoder().decode(User.self, from: data)
}

// 调用异步函数
let user = try await fetchUser(id: 1)

// 并发执行
async let user = fetchUser(id: 1)
async let posts = fetchPosts(userId: 1)
let (userData, postsData) = try await (user, posts)
```

## 2. Task 与 TaskGroup

```swift
// Task（创建异步任务）
Task {
    let user = try await fetchUser(id: 1)
    await MainActor.run {
        self.user = user  // 回到主线程更新 UI
    }
}

// Task.detached（不继承上下文）
Task.detached(priority: .background) {
    await processLargeData()
}

// TaskGroup（并发执行多个任务）
let users = try await withThrowingTaskGroup(of: User.self) { group in
    for id in userIds {
        group.addTask { try await fetchUser(id: id) }
    }
    var results: [User] = []
    for try await user in group {
        results.append(user)
    }
    return results
}
```

## 3. Actor

```swift
// Actor（线程安全的引用类型）
actor UserCache {
    private var cache: [Int: User] = [:]

    func getUser(id: Int) -> User? {
        return cache[id]
    }

    func setUser(_ user: User) {
        cache[user.id] = user
    }
}

let cache = UserCache()
await cache.setUser(user)
let cached = await cache.getUser(id: 1)

// @MainActor（主线程执行）
@MainActor
class ViewModel: ObservableObject {
    @Published var users: [User] = []

    func loadUsers() async {
        let users = try? await fetchUsers()
        self.users = users ?? []  // 自动在主线程
    }
}
```

## 4. AsyncSequence

```swift
// 异步序列
for try await line in url.lines {
    print(line)
}

// AsyncStream
let stream = AsyncStream<Int> { continuation in
    for i in 0..<10 {
        continuation.yield(i)
        try? await Task.sleep(nanoseconds: 1_000_000_000)
    }
    continuation.finish()
}

for await value in stream {
    print(value)
}
```

## 5. GCD（Grand Central Dispatch）

```swift
// 主队列
DispatchQueue.main.async {
    // UI 更新
}

// 全局队列
DispatchQueue.global(qos: .userInitiated).async {
    // 后台任务
    DispatchQueue.main.async {
        // 回到主线程
    }
}

// 自定义队列
let queue = DispatchQueue(label: "com.app.processing", qos: .utility)

// DispatchGroup
let group = DispatchGroup()
group.enter()
fetchData { group.leave() }
group.enter()
fetchMore { group.leave() }
group.notify(queue: .main) {
    print("全部完成")
}
```
## 6. Swift 6.2 Approachable Concurrency（2025-09）

> 🔄 更新于 2026-04-18

<!-- version-check: Swift 6.2 Approachable Concurrency, checked 2026-04-18 -->

Swift 6.2 引入了 **Approachable Concurrency**（易用并发），这是 Swift 并发模型最重大的改进。核心理念：**默认单线程，显式并发**。来源：[Swift 6.2 Released](https://www.swift.org/blog/swift-6.2-released)、[Donny Wals - Approachable Concurrency](https://www.donnywals.com/what-is-approachable-concurrency-in-xcode-26/)

### 默认 MainActor 隔离

Xcode 26 新建项目默认启用 MainActor 隔离，代码默认运行在主线程上，无需手动标注 `@MainActor`。

```swift
// 在 '-default-isolation MainActor' 模式下
// 所有代码默认在主线程执行，无需 @MainActor 标注

struct ImageCache {
    // 缓存受 MainActor 保护，线程安全
    static var cachedImages: [URL: Image] = [:]

    static func create(from url: URL) async throws -> Image {
        if let image = cachedImages[url] {
            return image
        }

        // fetchImage 标记为 @concurrent，在并发线程池执行
        let image = try await fetchImage(at: url)

        cachedImages[url] = image
        return image
    }

    // @concurrent 显式标记需要并发执行的代码
    @concurrent
    static func fetchImage(at url: URL) async throws -> Image {
        let (data, _) = try await URLSession.shared.data(from: url)
        return await decode(data: data)
    }
}
```

### @concurrent 属性

当需要代码在并发线程池上执行时，使用 `@concurrent` 显式标记：

```swift
// 默认：代码在调用者的执行上下文中运行（通常是主线程）
func processData() async {
    // 在主线程执行
}

// @concurrent：显式声明在并发线程池执行
@concurrent
func heavyComputation() async -> Result {
    // 在后台线程池执行，不阻塞主线程
    return performExpensiveWork()
}
```

### async 函数行为变化

Swift 6.2 中，`nonisolated async` 方法默认在调用者的执行上下文中运行，而不是自动切换到全局并发线程池。这使得异步代码的行为更加可预测。

```swift
class DataManager {
    var data: [String] = []

    // Swift 6.1：自动切换到全局线程池，可能导致数据竞争
    // Swift 6.2：在调用者上下文执行，更安全
    func loadData() async {
        data = await fetchFromNetwork()
    }
}
```

### 迁移建议

| 场景 | Swift 6.1 | Swift 6.2 |
|------|-----------|-----------|
| UI 代码 | 需要 `@MainActor` | 默认在主线程 |
| 后台计算 | 默认并发 | 需要 `@concurrent` |
| async 方法 | 切换到全局线程池 | 在调用者上下文执行 |
| 数据竞争检查 | 编译器警告 | 编译器错误（Swift 6 模式） |

> **注意**：Swift 6 严格并发检查将数据竞争从警告升级为编译器错误。所有主流框架在 2026 年已完成 Swift 6 适配。来源：[Swift Concurrency Safety in 2026](https://vocal.media/01/swift-concurrency-safety-navigating-xcode-checks-in-2026)

## 7. Swift 6.4（WWDC26）并发新特性

> 更新于 2026-07-10

<!-- version-check: Swift 6.4 concurrency (SE-0493/0504/0518/0520), WWDC26, checked 2026-07-10 -->

Swift 6.4 随 WWDC26 发布，带来一批解决实际痛点的并发改进（来源：[SwiftLee: Swift 6.4 What's New in Concurrency](https://www.avanderlee.com/concurrency/swift-6-4-whats-new-in-concurrency/)）：

**SE-0493：`defer` 中支持 async 调用**——此前 `defer` 块内不能调用异步函数，异步清理逻辑必须用别的方式绕过；6.4 起限制解除：

```swift
func processFile() async throws {
    let handle = try openFile()
    defer {
        Task { await handle.close() }  // Swift 6.4 之前的变通写法
    }
    // Swift 6.4：defer 内可直接 await
    defer { await handle.closeAsync() }
    try await handle.write(data)
}
```

**SE-0504：Task Cancellation Shields**——`withTaskCancellationShield { ... }` 让作用域内的代码暂时"看不到"取消信号，适合数据库写入、文件落盘等必须完整执行的清理逻辑：

```swift
await withTaskCancellationShield {
    // 即使外部 Task 已被取消，这段关键收尾逻辑也会完整执行完
    await database.commitPendingWrites()
}

// 调试用：检查当前是否处于 shield 保护中
if Task.hasActiveCancellationShield {
    logger.debug("running inside a cancellation shield")
}
```

注意：shield 不会被子任务自动继承，每个子任务需要自己单独包裹。

**SE-0520：忽略抛错 Task 的诊断警告**——创建一个会抛错的 unstructured `Task` 却不保存其句柄时，编译器现在会发出警告，提醒你要么在任务内处理错误，要么保存任务后续检查。

**Sendable 相关改进**：

- `weak let`（Swift 6.3 引入的 SE-0481）+ Swift 6.4：只因为 `weak var` 而被迫用 `@unchecked Sendable` 的类型，改成 `weak let` 即可参与正规的 Sendable 检查
- **SE-0518：`~Sendable`**：显式声明"这个类型不应该是 Sendable"，且不会阻止其子类被判定为 Sendable
- **`@Diagnose` 属性**：可在函数粒度控制特定警告的行为（如临时忽略 deprecated 警告、或反过来在安全敏感函数内提升为 strict memory safety / strict concurrency 检查），便于渐进式迁移到 Swift 6 语言模式

来源：[SwiftLee: Swift 6.4 Concurrency](https://www.avanderlee.com/concurrency/swift-6-4-whats-new-in-concurrency/)、[SE-0504 Task Cancellation Shields](https://github.com/swiftlang/swift-evolution/blob/main/proposals/0504-task-cancellation-shields.md)、[What's New in Swift 2026](https://blakecrosley.com/blog/whats-new-swift-2026)

## 🎬 推荐视频资源

- [Sean Allen - Swift Concurrency](https://www.youtube.com/watch?v=U6lQOo5aGmE) — Swift并发编程教程
- [Paul Hudson - Concurrency in Swift](https://www.youtube.com/watch?v=sGnxBiLL3Gc) — async/await详解
