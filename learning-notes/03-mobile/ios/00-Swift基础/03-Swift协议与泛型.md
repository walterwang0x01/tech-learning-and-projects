# Swift 协议与泛型
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 协议

```swift
// 协议定义
protocol Drawable {
    var color: String { get set }
    func draw()
}

protocol Resizable {
    func resize(to size: CGSize)
}

// 遵循协议
struct Circle: Drawable, Resizable {
    var color: String
    var radius: Double

    func draw() { print("Drawing circle with radius \(radius)") }
    func resize(to size: CGSize) { /* ... */ }
}

// 协议继承
protocol Shape: Drawable, Resizable {
    var area: Double { get }
}

// 协议扩展（提供默认实现）
extension Drawable {
    func draw() {
        print("Default drawing with color \(color)")
    }
}
```

## 2. 面向协议编程（POP）

```swift
// 用协议定义能力，而非继承层级
protocol Identifiable {
    var id: String { get }
}

protocol Displayable {
    var displayName: String { get }
}

protocol Cacheable {
    func cacheKey() -> String
}

// 组合协议
struct Product: Identifiable, Displayable, Cacheable {
    let id: String
    let name: String
    let price: Double

    var displayName: String { "\(name) - ¥\(price)" }
    func cacheKey() -> String { "product_\(id)" }
}

// 协议作为类型约束
func display<T: Displayable>(_ item: T) {
    print(item.displayName)
}

// 协议组合
func process(_ item: Identifiable & Displayable) {
    print("\(item.id): \(item.displayName)")
}
```

## 3. 泛型

```swift
// 泛型函数
func swapValues<T>(_ a: inout T, _ b: inout T) {
    let temp = a; a = b; b = temp
}

// 泛型类型
struct Stack<Element> {
    private var items: [Element] = []

    mutating func push(_ item: Element) { items.append(item) }
    mutating func pop() -> Element? { items.popLast() }
    var top: Element? { items.last }
    var isEmpty: Bool { items.isEmpty }
}

var intStack = Stack<Int>()
intStack.push(1)
intStack.push(2)

// 类型约束
func findIndex<T: Equatable>(of value: T, in array: [T]) -> Int? {
    array.firstIndex(of: value)
}

// where 子句
func allMatch<C: Collection>(_ collection: C, predicate: (C.Element) -> Bool) -> Bool
    where C.Element: Equatable {
    collection.allSatisfy(predicate)
}

// 关联类型
protocol Repository {
    associatedtype Entity
    func getAll() async throws -> [Entity]
    func getById(_ id: String) async throws -> Entity?
    func save(_ entity: Entity) async throws
}

class UserRepository: Repository {
    typealias Entity = User
    func getAll() async throws -> [User] { /* ... */ }
    func getById(_ id: String) async throws -> User? { /* ... */ }
    func save(_ entity: User) async throws { /* ... */ }
}
```

## 4. 不透明类型

```swift
// some（不透明类型）— 隐藏具体类型，编译器知道
func makeShape() -> some Shape {
    Circle(color: "red", radius: 10)
}

// any（存在类型）— 类型擦除，运行时多态
func processShapes(_ shapes: [any Shape]) {
    for shape in shapes {
        shape.draw()
    }
}

// SwiftUI 中的 some View
var body: some View {
    VStack {
        Text("Hello")
        Image(systemName: "star")
    }
}
```
