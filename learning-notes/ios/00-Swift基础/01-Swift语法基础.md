# Swift 语法基础
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 变量与常量

```swift
let constant = 10       // 常量（不可变）
var variable = 20       // 变量（可变）

// 类型注解
let name: String = "张三"
let age: Int = 25
let height: Double = 1.75
let isActive: Bool = true

// 类型推断
let message = "Hello"   // 自动推断为 String
let count = 42          // 自动推断为 Int
```

## 2. 可选类型（Optional）

```swift
var nickname: String? = nil  // 可选类型，可以为 nil

// 可选绑定（推荐）
if let name = nickname {
    print("昵称: \(name)")
} else {
    print("没有昵称")
}

// guard let（提前退出）
func greet(_ name: String?) {
    guard let name = name else {
        print("名字为空")
        return
    }
    print("Hello, \(name)")
}

// 可选链
let length = nickname?.count  // Int?

// 空合运算符
let displayName = nickname ?? "匿名"

// 强制解包（谨慎使用）
let forcedName = nickname!  // 如果为 nil 会崩溃
```

## 3. 集合类型

```swift
// 数组
var fruits: [String] = ["苹果", "香蕉", "橙子"]
fruits.append("葡萄")
fruits.insert("西瓜", at: 0)
let first = fruits.first  // Optional
fruits.remove(at: 1)
let sorted = fruits.sorted()

// 字典
var scores: [String: Int] = ["张三": 90, "李四": 85]
scores["王五"] = 95
let zhangScore = scores["张三"]  // Optional

// 集合
var tags: Set<String> = ["Swift", "iOS", "Xcode"]
tags.insert("SwiftUI")
let hasSwift = tags.contains("Swift")

// 高阶函数
let numbers = [1, 2, 3, 4, 5]
let doubled = numbers.map { $0 * 2 }           // [2, 4, 6, 8, 10]
let evens = numbers.filter { $0 % 2 == 0 }     // [2, 4]
let sum = numbers.reduce(0, +)                   // 15
let names = users.compactMap { $0.name }         // 过滤 nil
let allGroups = users.flatMap { $0.groups }      // 展平嵌套数组
```

## 4. 控制流

```swift
// if-else
if score >= 90 { print("优秀") }
else if score >= 60 { print("及格") }
else { print("不及格") }

// switch（强大的模式匹配）
switch value {
case 0:
    print("零")
case 1...9:
    print("个位数")
case let x where x > 100:
    print("大于100: \(x)")
default:
    print("其他")
}

// 枚举匹配
enum Direction { case north, south, east, west }
switch direction {
case .north: print("北")
case .south: print("南")
default: print("其他方向")
}

// for-in
for i in 0..<5 { print(i) }           // 0,1,2,3,4
for (index, value) in array.enumerated() { }
for (key, value) in dictionary { }

// while / repeat-while
while condition { }
repeat { } while condition
```

## 5. 函数与闭包

```swift
// 函数
func greet(name: String, greeting: String = "Hello") -> String {
    return "\(greeting), \(name)"
}
greet(name: "张三")
greet(name: "李四", greeting: "Hi")

// 参数标签
func move(from source: String, to destination: String) { }
move(from: "北京", to: "上海")

// 忽略参数标签
func add(_ a: Int, _ b: Int) -> Int { a + b }
add(1, 2)

// inout 参数
func swap(_ a: inout Int, _ b: inout Int) {
    let temp = a; a = b; b = temp
}

// 闭包
let multiply: (Int, Int) -> Int = { a, b in a * b }
let doubled = numbers.map { $0 * 2 }  // 尾随闭包 + 简写

// 逃逸闭包
func fetchData(completion: @escaping (Result<Data, Error>) -> Void) {
    URLSession.shared.dataTask(with: url) { data, _, error in
        if let data = data { completion(.success(data)) }
        else if let error = error { completion(.failure(error)) }
    }.resume()
}
```

## 6. 枚举与结构体

```swift
// 枚举（值类型）
enum NetworkError: Error {
    case noConnection
    case timeout
    case serverError(code: Int, message: String)
}

// 关联值
enum Result<Success, Failure: Error> {
    case success(Success)
    case failure(Failure)
}

// 结构体（值类型，推荐优先使用）
struct User {
    let id: Int
    var name: String
    var email: String

    func displayName() -> String {
        return "\(name) (\(email))"
    }

    // mutating 方法修改属性
    mutating func updateName(_ newName: String) {
        name = newName
    }
}
```

## 7. 错误处理

```swift
// 定义错误
enum ValidationError: Error {
    case emptyField(String)
    case invalidEmail
    case passwordTooShort(minLength: Int)
}

// 抛出错误
func validate(email: String, password: String) throws -> Bool {
    guard !email.isEmpty else { throw ValidationError.emptyField("email") }
    guard email.contains("@") else { throw ValidationError.invalidEmail }
    guard password.count >= 8 else { throw ValidationError.passwordTooShort(minLength: 8) }
    return true
}

// 处理错误
do {
    try validate(email: "test@example.com", password: "12345678")
} catch ValidationError.invalidEmail {
    print("邮箱格式不正确")
} catch {
    print("验证失败: \(error)")
}

// try? 转为可选值
let isValid = try? validate(email: "test@example.com", password: "123")
```
## 8. Swift 6.2 新增特性（2025-09）

> 🔄 更新于 2026-04-18

<!-- version-check: Swift 6.2, checked 2026-04-18 -->

Swift 6.2 于 2025 年 9 月随 Xcode 26 发布，带来了性能和安全性方面的重要新特性。来源：[Swift 6.2 Released](https://www.swift.org/blog/swift-6.2-released)

### InlineArray — 固定大小内联数组

`InlineArray` 是一种新的固定大小数组类型，元素直接存储在栈上或嵌入到其他类型中，避免额外的堆分配。

```swift
// InlineArray：固定大小，栈分配，零堆开销
struct Game {
    // 简写语法：[数量 of 类型]
    var bricks: [40 of Sprite]

    init(_ brickSprite: Sprite) {
        bricks = .init(repeating: brickSprite)
    }
}

// 完整语法
let buffer: InlineArray<10, Int> = .init(repeating: 0)
```

### Span — 安全的连续内存访问

`Span` 提供对连续内存的安全直接访问，是 `UnsafeBufferPointer` 的安全替代方案。编译时检查内存有效性，零运行时开销。

```swift
// Span 确保内存在使用期间保持有效
func processData(_ span: Span<UInt8>) {
    for byte in span {
        // 安全访问，无 use-after-free 风险
    }
}
```

### WebAssembly 支持

Swift 6.2 新增 Wasm SDK，可以将 Swift 代码编译为 WebAssembly 并运行。

```bash
# 编译为 Wasm 并运行
swift build --swift-sdk wasm
swift run --swift-sdk wasm
```

### 严格内存安全模式

新增 opt-in 的严格内存安全检查，可以检测代码中的不安全构造。

```swift
// 在 Package.swift 中启用
.target(
    name: "MyTarget",
    swiftSettings: [.strictMemorySafety]
)
```

## 9. Swift 6.3 / 6.4 新增特性（WWDC26）

> 🔄 更新于 2026-07-08

<!-- version-check: Swift 6.3 + 6.4 (WWDC26), Xcode 27 / Swift 6.4, checked 2026-07-08 -->

WWDC26 一次性发布 **Swift 6.3 与 6.4**，随 **Xcode 27** 提供。变更分两类：日常语法摩擦消除，以及所有权系统进入普通业务代码。来源：[What's new in Swift (WWDC26 Session 262)](https://developer.apple.com/videos/play/wwdc2026/262/)、[WWDC26 Swift Guide](https://developer.apple.com/wwdc26/guides/swift/)

### 日常语法改进（Swift 6.4）

```swift
// 1) anyAppleOS — 跨平台可用性一行声明
@available(anyAppleOS 27, *)
func newFeature() { }

// 2) @diagnose — 单声明级警告控制（迁移期抑制 deprecation 等）
@diagnose(.ignored, group: .deprecatedDeclaration)
func legacyWrapper() { callOldAPI() }

// 3) 模块选择器 :: — 解决跨模块同名冲突（Swift 6.3）
let rocket = Rocket::SaturnV   // 左侧始终是模块名，不是类型

// 4) 可选 existential 去括号
let handler: any P? = nil      // 不再需要 (any P)?

// 5) defer 中支持 async 清理（SE-0493）
defer { await flushBuffer() }

// 6) weak let / ~Sendable
weak let delegate: Delegate?   // 替代 @unchecked Sendable 的常见场景
struct NotSendable: ~Sendable { }
```

### 所有权与性能（Swift 6.4）

`Iterable` 协议让 `for` 循环可**借用**元素而非拷贝，适用于 `Span`、`InlineArray` 等非可复制类型；`borrow`/`mutate` 访问器替代 `get`/`set`，避免大结构体拷贝。

```swift
// Iterable：for 循环优先 Sequence，回退 Iterable（批量 Span 迭代）
for element in uniqueArray { process(element) }  // 无引用计数开销

// borrow / mutate 访问器
var box: UniqueBox<[256 of Int]>
box[0] = 42   // 原地修改，不拷贝整个 InlineArray
```

新增标准库类型：`UniqueArray`、`UniqueBox`、`Continuation`（单次 resume 编译期检查）、`Ref`/`MutableRef`（单值借用容器）。`Containers` 模块（SE-0527）可通过 [swift-collections 1.3](https://github.com/apple/swift-collections) 提前试用。

### 跨平台与工具链

| 变更 | 版本 | 说明 |
|------|------|------|
| Swift SDK for Android | 6.3 | 首次官方 Android SDK，iOS/Android 共享 Swift 代码 |
| Swift Build 默认后端 | 6.4 | SPM 默认使用 Swift Build，与 Xcode 构建行为一致 |
| `@C` 属性 | 6.4 | 将 Swift 函数导出给 C 调用 |
| Foundation URL 解析 | 6.4 | 性能最高 **4×** 提升 |
| Subprocess 1.0 | 6.4 | 子进程 API 正式版，`AsyncBufferSequence` 流式输出 |

来源：[Swift 6.4 Release Blog](https://www.swift.org/blog/)、[What's New in Swift 2026](https://blakecrosley.com/blog/whats-new-swift-2026)

## 🎬 推荐视频资源

- [CodeWithChris - Swift Tutorial for Beginners](https://www.youtube.com/watch?v=comQ1-x2a1Q) — Swift入门教程
- [Paul Hudson - 100 Days of SwiftUI](https://www.hackingwithswift.com/100/swiftui) — 100天SwiftUI挑战
- [Sean Allen - Swift Fundamentals](https://www.youtube.com/watch?v=CwA1VWP0Ldw) — Swift基础教程
