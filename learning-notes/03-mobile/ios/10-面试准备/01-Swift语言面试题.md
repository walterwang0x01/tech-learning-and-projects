# Swift 语言面试题
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 值类型 vs 引用类型

```swift
// 值类型：struct, enum, tuple（复制语义）
struct Point {
    var x: Int
    var y: Int
}
var a = Point(x: 1, y: 2)
var b = a       // 复制
b.x = 10
print(a.x)     // 1（不受影响）

// 引用类型：class（共享语义）
class Person {
    var name: String
    init(name: String) { self.name = name }
}
let p1 = Person(name: "张三")
let p2 = p1     // 共享同一实例
p2.name = "李四"
print(p1.name)  // "李四"（被修改）

// 选择原则：
// - 优先使用 struct（线程安全、性能好）
// - 需要继承、共享状态、deinit 时用 class
// - Swift 标准库大量使用 struct：String, Array, Dictionary
```

## 2. Optional 原理

```swift
// Optional 本质是枚举
enum Optional<Wrapped> {
    case none
    case some(Wrapped)
}

// 解包方式对比
var name: String? = "Swift"

// 1. if let（安全）
if let name = name { print(name) }

// 2. guard let（提前退出）
guard let name = name else { return }

// 3. ?? 空合运算符
let display = name ?? "默认值"

// 4. 可选链
let count = name?.count  // Int?

// 5. 强制解包（危险）
let forced = name!  // nil 时崩溃

// 6. Swift 5.7 简写
if let name { print(name) }  // 等同于 if let name = name
```

> 🔄 更新于 2026-05-02

<!-- version-check: Swift 6.2, iOS 26, Xcode 26.4, checked 2026-05-02 -->

## 7. 2026 年 Swift 面试新增热点

### 7.1 Swift 6.2 并发模型面试题

```swift
// Q: Swift 6.2 的 Approachable Concurrency 是什么？
// A: Swift 6.2 彻底改变了并发编程模型：
// - 默认 MainActor 隔离：所有代码默认在主线程执行
// - @concurrent 显式并发：需要并发时显式标注
// - 从"默认并发，手动标注安全"变为"默认安全，显式引入并发"

// Swift 6.1 及之前：需要手动标注 @MainActor
@MainActor
class OldViewModel: ObservableObject {
    func updateUI() { /* 在主线程 */ }
}

// Swift 6.2：默认就在 MainActor，需要并发时用 @concurrent
class NewViewModel: ObservableObject {
    func updateUI() { /* 默认在主线程 */ }
    
    @concurrent
    func fetchData() async throws -> Data {
        // 显式声明在后台执行
        return try await URLSession.shared.data(from: url).0
    }
}

// Q: async 函数在 Swift 6.2 中的行为变化？
// A: async 函数现在在调用者的上下文中执行（而非自动切换到后台）：
// - 如果从 MainActor 调用 async 函数，它在主线程执行
// - 需要后台执行必须显式标注 @concurrent
// - 这避免了意外的线程切换和数据竞争
```

### 7.2 Swift 6 严格并发面试题

```swift
// Q: Swift 6 的 Sendable 协议是什么？为什么重要？
// A: Sendable 标记类型可以安全地跨并发域传递：
// - struct 默认 Sendable（如果所有属性都是 Sendable）
// - class 需要显式遵循 Sendable 并确保线程安全
// - Swift 6 将数据竞争从警告升级为编译错误

// ❌ 编译错误：class 默认不是 Sendable
class UserData {
    var name: String = ""
}
// 跨 Actor 传递 UserData 会报错

// ✅ 方案1：使用 struct
struct UserData: Sendable {
    let name: String
}

// ✅ 方案2：使用 Actor
actor UserData {
    var name: String = ""
}

// ✅ 方案3：@unchecked Sendable（自行保证线程安全）
final class UserData: @unchecked Sendable {
    private let lock = NSLock()
    private var _name: String = ""
    var name: String {
        get { lock.withLock { _name } }
        set { lock.withLock { _name = newValue } }
    }
}
```

### 7.3 iOS 26 / Liquid Glass 面试题

```swift
// Q: Liquid Glass 是什么？对开发者有什么影响？
// A: iOS 26 引入的全新设计语言（iOS 7 以来最大视觉重设计）：
// - 所有 Apple 平台统一采用 Liquid Glass 设计
// - 用 Xcode 26 重新编译即可自动获得新外观
// - .glassEffect() 修饰符一行代码应用效果
// - iOS 26.1 添加 Tinted 选项，26.4 可禁用部分效果
// - iOS 27 将强制要求 Liquid Glass 设计

// Q: SwiftUI 在 iOS 26 有哪些重要新特性？
// A: 核心新特性：
// 1. 原生 WebView（不再需要 UIViewRepresentable 包装 WKWebView）
// 2. 富文本编辑（TextEditor + AttributedString）
// 3. 3D Swift Charts
// 4. @Animatable 宏（自动合成 animatableData，减少样板代码）
// 5. TabView 搜索标签（.search role）

// Q: @Observable 和 @ObservableObject 怎么选？
// A: 2026 年推荐 @Observable（iOS 17+）：
// - 更细粒度的观察（属性级别，而非对象级别）
// - 不需要 @Published 标注
// - 性能更好（只在读取的属性变化时触发更新）
// @ObservableObject 仍然支持，但新项目应使用 @Observable
```

## 3. 闭包与捕获

```swift
// 闭包捕获值（引用捕获）
func makeCounter() -> () -> Int {
    var count = 0
    return {
        count += 1  // 捕获 count 的引用
        return count
    }
}
let counter = makeCounter()
counter()  // 1
counter()  // 2

// 捕获列表（值捕获）
var value = 10
let closure = { [value] in print(value) }
value = 20
closure()  // 10（捕获时的值）

// 逃逸闭包 vs 非逃逸闭包
func doWork(completion: @escaping () -> Void) {
    DispatchQueue.global().async { completion() }  // 逃逸：闭包在函数返回后执行
}
func doSync(action: () -> Void) {
    action()  // 非逃逸：闭包在函数返回前执行（默认）
}
```

## 4. ARC 与内存管理

```swift
// strong（默认）：增加引用计数
// weak：不增加引用计数，对象释放后自动置 nil（必须是 Optional）
// unowned：不增加引用计数，对象释放后不置 nil（访问会崩溃）

class Owner {
    var pet: Pet?
    deinit { print("Owner 释放") }
}
class Pet {
    weak var owner: Owner?  // weak 打破循环引用
    deinit { print("Pet 释放") }
}

// 闭包中的循环引用
class ViewModel {
    var name = "test"
    var onUpdate: (() -> Void)?

    func setup() {
        // ❌ 循环引用：self → onUpdate → self
        onUpdate = { print(self.name) }

        // ✅ weak self
        onUpdate = { [weak self] in print(self?.name ?? "") }

        // ✅ unowned self（确定 self 不会先释放时）
        onUpdate = { [unowned self] in print(self.name) }
    }
}
```

## 5. async/await 与 Actor

```swift
// async/await
func fetchUser() async throws -> User {
    let (data, _) = try await URLSession.shared.data(from: url)
    return try JSONDecoder().decode(User.self, from: data)
}

// 并发执行
async let users = fetchUsers()
async let posts = fetchPosts()
let (u, p) = try await (users, posts)  // 并行请求

// TaskGroup
let results = try await withThrowingTaskGroup(of: User.self) { group in
    for id in ids {
        group.addTask { try await fetchUser(id: id) }
    }
    var users: [User] = []
    for try await user in group { users.append(user) }
    return users
}

// Actor（线程安全）
actor BankAccount {
    private var balance: Double = 0

    func deposit(_ amount: Double) { balance += amount }
    func getBalance() -> Double { balance }
}

let account = BankAccount()
await account.deposit(100)  // 必须 await
```

## 6. 协议与泛型

```swift
// 协议关联类型
protocol Repository {
    associatedtype Item
    func getAll() async throws -> [Item]
    func save(_ item: Item) async throws
}

// 泛型约束
func findFirst<T: Collection>(in collection: T, where predicate: (T.Element) -> Bool) -> T.Element? {
    collection.first(where: predicate)
}

// some vs any
func makeView() -> some View { Text("Hello") }  // 不透明类型（编译时确定）
func getRepository() -> any Repository { RemoteRepo() }  // 存在类型（运行时多态）
```
