# Swift 面向对象编程
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 类与结构体

```swift
// 结构体（值类型，推荐优先使用）
struct Point {
    var x: Double
    var y: Double

    func distance(to other: Point) -> Double {
        sqrt(pow(x - other.x, 2) + pow(y - other.y, 2))
    }

    mutating func move(dx: Double, dy: Double) {
        x += dx
        y += dy
    }
}

// 类（引用类型）
class Vehicle {
    var brand: String
    var speed: Double = 0

    init(brand: String) {
        self.brand = brand
    }

    func accelerate(by amount: Double) {
        speed += amount
    }

    deinit {
        print("\(brand) 被销毁")
    }
}

// 值类型 vs 引用类型
var p1 = Point(x: 0, y: 0)
var p2 = p1        // 拷贝
p2.x = 10
print(p1.x)       // 0（不受影响）

let v1 = Vehicle(brand: "Tesla")
let v2 = v1        // 引用同一对象
v2.speed = 100
print(v1.speed)    // 100（被修改了）
```

## 2. 属性

```swift
class User {
    // 存储属性
    var name: String
    let id: Int

    // 计算属性
    var displayName: String {
        get { return "[\(id)] \(name)" }
        set { name = newValue }
    }

    // 属性观察器
    var age: Int = 0 {
        willSet { print("age 将变为 \(newValue)") }
        didSet { print("age 从 \(oldValue) 变为 \(age)") }
    }

    // 懒加载属性
    lazy var avatar: UIImage = {
        return loadAvatar()
    }()

    // 类型属性（静态）
    static let maxAge = 150
    static var count = 0

    init(id: Int, name: String) {
        self.id = id
        self.name = name
        User.count += 1
    }
}
```

## 3. 继承

```swift
class Animal {
    var name: String
    init(name: String) { self.name = name }
    func speak() -> String { return "\(name) makes a sound" }
}

class Dog: Animal {
    var breed: String

    init(name: String, breed: String) {
        self.breed = breed
        super.init(name: name)
    }

    override func speak() -> String {
        return "\(name) barks"
    }

    // final 防止子类重写
    final func fetch() { }
}

// final 类不能被继承
final class Singleton { }
```

## 4. 扩展（Extension）

```swift
// 为现有类型添加功能
extension String {
    var isEmail: Bool {
        contains("@") && contains(".")
    }

    func truncated(to length: Int) -> String {
        count > length ? String(prefix(length)) + "..." : self
    }
}

"test@example.com".isEmail  // true
"Hello World".truncated(to: 5)  // "Hello..."

// 为协议提供默认实现
extension Collection {
    var isNotEmpty: Bool { !isEmpty }
}
```

## 5. 访问控制

```swift
// open     — 可跨模块继承和重写
// public   — 可跨模块访问，不可继承
// internal — 模块内访问（默认）
// fileprivate — 文件内访问
// private  — 声明作用域内访问

public class APIClient {
    private let baseURL: String
    internal var token: String?

    public init(baseURL: String) {
        self.baseURL = baseURL
    }

    public func fetch() async throws -> Data { /* ... */ }
    private func buildRequest() -> URLRequest { /* ... */ }
}
```
