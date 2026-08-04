# Swift 内存管理与 ARC
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. ARC 原理

```swift
// ARC（Automatic Reference Counting）自动引用计数
// 每个类实例有一个引用计数器
// 引用计数为 0 时自动释放内存

class User {
    let name: String
    init(name: String) {
        self.name = name
        print("\(name) 被创建")
    }
    deinit {
        print("\(name) 被销毁")
    }
}

var user1: User? = User(name: "张三")  // 引用计数 = 1
var user2 = user1                       // 引用计数 = 2
user1 = nil                             // 引用计数 = 1
user2 = nil                             // 引用计数 = 0 → 销毁
```

## 2. 循环引用

```swift
// ❌ 循环引用（内存泄漏）
class Person {
    var apartment: Apartment?
}
class Apartment {
    var tenant: Person?  // 强引用
}

let person = Person()
let apartment = Apartment()
person.apartment = apartment
apartment.tenant = person
// 即使设为 nil，两者互相引用，无法释放

// ✅ weak 解决（可选类型，自动置 nil）
class Apartment {
    weak var tenant: Person?
}

// ✅ unowned 解决（非可选，确保不会为 nil）
class Customer {
    var card: CreditCard?
}
class CreditCard {
    unowned let customer: Customer
    init(customer: Customer) { self.customer = customer }
}
```

## 3. 闭包中的循环引用

```swift
// ❌ 闭包捕获 self
class ViewModel {
    var name = "张三"
    var onUpdate: (() -> Void)?

    func setup() {
        onUpdate = {
            print(self.name)  // 闭包强引用 self → 循环引用
        }
    }
}

// ✅ 捕获列表
func setup() {
    onUpdate = { [weak self] in
        guard let self = self else { return }
        print(self.name)
    }
}

// ✅ unowned（确定 self 不会先被释放）
func setup() {
    onUpdate = { [unowned self] in
        print(self.name)
    }
}
```

## 4. 值类型 vs 引用类型

```swift
// 值类型（struct, enum, tuple）：赋值时拷贝
// 引用类型（class, closure）：赋值时共享引用

// 选择建议：
// 优先使用 struct（值类型）
// 需要继承、引用语义、deinit 时使用 class
// Swift 标准库大量使用 struct（String, Array, Dictionary 都是值类型）

// Copy-on-Write（COW）
var arr1 = [1, 2, 3]
var arr2 = arr1       // 此时共享存储
arr2.append(4)        // 修改时才真正拷贝
```
