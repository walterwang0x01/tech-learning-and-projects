# SwiftData 与 Realm
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. SwiftData 数据模型（iOS 17+）

```swift
import SwiftData

@Model
class Task {
    var id: UUID
    var title: String
    var isCompleted: Bool
    var createdAt: Date
    @Relationship(deleteRule: .cascade) var subtasks: [Subtask]

    init(title: String) {
        self.id = UUID()
        self.title = title
        self.isCompleted = false
        self.createdAt = Date()
        self.subtasks = []
    }
}

@Model
class Subtask {
    var title: String
    var isDone: Bool
    var task: Task?

    init(title: String) {
        self.title = title
        self.isDone = false
    }
}
```

## 2. SwiftData 容器配置

```swift
import SwiftUI

@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        .modelContainer(for: [Task.self, Subtask.self])
    }
}
```

## 3. SwiftData CRUD（SwiftUI）

```swift
struct TaskListView: View {
    @Environment(\.modelContext) private var context
    @Query(sort: \Task.createdAt, order: .reverse) var tasks: [Task]

    var body: some View {
        List {
            ForEach(tasks) { task in
                HStack {
                    Image(systemName: task.isCompleted ? "checkmark.circle.fill" : "circle")
                    Text(task.title)
                }
                .onTapGesture { task.isCompleted.toggle() }
            }
            .onDelete(perform: deleteTasks)
        }
    }

    func addTask(title: String) {
        let task = Task(title: title)
        context.insert(task)
    }

    func deleteTasks(at offsets: IndexSet) {
        for index in offsets {
            context.delete(tasks[index])
        }
    }
}
```

## 4. @Query 过滤与排序

```swift
// 过滤未完成任务
@Query(filter: #Predicate<Task> { !$0.isCompleted },
       sort: \Task.createdAt)
var pendingTasks: [Task]

// 动态过滤
struct FilteredView: View {
    @Query var tasks: [Task]

    init(showCompleted: Bool) {
        let predicate = #Predicate<Task> { task in
            showCompleted || !task.isCompleted
        }
        _tasks = Query(filter: predicate, sort: \Task.createdAt)
    }

    var body: some View {
        List(tasks) { task in Text(task.title) }
    }
}
```

## 5. SwiftData iOS 26 新特性：继承与 Schema 迁移

<!-- version-check: SwiftData iOS 26 (Xcode 26.4), Unique Constraints, checked 2026-05-04 -->

> 🔄 更新于 2026-04-22

iOS 26 为 SwiftData 带来了**类继承**支持和 **Schema 迁移**改进，这是自 iOS 17 引入 SwiftData 以来最重要的数据建模能力升级。来源：[WWDC25 Session 291](https://developer.apple.com/videos/play/wwdc2025/291/)

### 5.1 类继承建模

```swift
import SwiftData

// 父类模型
@Model
class Vehicle {
    var make: String
    var model: String
    var year: Int

    init(make: String, model: String, year: Int) {
        self.make = make
        self.model = model
        self.year = year
    }
}

// 子类继承父类属性，并添加自己的属性
@Model
class Car: Vehicle {
    var numberOfDoors: Int

    init(make: String, model: String, year: Int, numberOfDoors: Int) {
        self.numberOfDoors = numberOfDoors
        super.init(make: make, model: model, year: year)
    }
}

@Model
class Truck: Vehicle {
    var payloadCapacity: Double

    init(make: String, model: String, year: Int, payloadCapacity: Double) {
        self.payloadCapacity = payloadCapacity
        super.init(make: make, model: model, year: year)
    }
}
```

### 5.2 继承模型的查询优化

```swift
// 查询所有 Vehicle（包括 Car 和 Truck）
@Query var allVehicles: [Vehicle]

// 只查询 Car 子类
@Query var cars: [Car]

// 使用 #Predicate 过滤继承层级
@Query(filter: #Predicate<Vehicle> { $0.year >= 2024 })
var recentVehicles: [Vehicle]
```

### 5.3 容器配置（需注册所有子类）

```swift
@main
struct MyApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
        }
        // 注册父类和所有子类
        .modelContainer(for: [Vehicle.self, Car.self, Truck.self])
    }
}
```

### 5.4 Schema 迁移到继承

```swift
// 从扁平模型迁移到继承模型时，使用 SchemaMigrationPlan
enum VehicleMigrationPlan: SchemaMigrationPlan {
    static var schemas: [any VersionedSchema.Type] {
        [SchemaV1.self, SchemaV2.self]
    }

    static var stages: [MigrationStage] {
        [migrateV1toV2]
    }

    // 自定义迁移逻辑
    static let migrateV1toV2 = MigrationStage.custom(
        fromVersion: SchemaV1.self,
        toVersion: SchemaV2.self
    ) { context in
        // 将旧数据迁移到新的继承结构
        try context.save()
    }
}
```

### 5.5 Unique Constraints（唯一约束）

> 🔄 更新于 2026-05-04

iOS 26 新增 `#Unique` 宏，可以为 SwiftData 模型添加唯一约束，防止重复数据并提升查询性能。来源：[What's new about SwiftData (WWDC25)](https://askwwdc.com/q/whats-new-about-swiftdata)

```swift
import SwiftData

@Model
class Contact {
    #Unique<Contact>([\.email])  // email 字段唯一

    var name: String
    var email: String
    var phone: String?

    init(name: String, email: String, phone: String? = nil) {
        self.name = name
        self.email = email
        self.phone = phone
    }
}

// 复合唯一约束
@Model
class OrderItem {
    #Unique<OrderItem>([\.orderId, \.productId])  // 订单+商品组合唯一

    var orderId: String
    var productId: String
    var quantity: Int

    init(orderId: String, productId: String, quantity: Int) {
        self.orderId = orderId
        self.productId = productId
        self.quantity = quantity
    }
}
```

### 5.6 继承 vs 组合选择

```
场景                    推荐方式        原因
──────────────────────────────────────────────────
共享属性 + 多态查询      继承           父类查询自动包含子类
独立数据 + 关联关系      组合           @Relationship 更灵活
跨模块复用              组合           继承耦合度高
简单标记区分            枚举属性        不需要继承的复杂性
```

## 6. Realm 数据模型

```swift
import RealmSwift

class Dog: Object {
    @Persisted(primaryKey: true) var id: ObjectId
    @Persisted var name: String
    @Persisted var age: Int
    @Persisted var owner: Person?
}

class Person: Object {
    @Persisted(primaryKey: true) var id: ObjectId
    @Persisted var name: String
    @Persisted var dogs: List<Dog>
}
```

## 6. Realm CRUD

```swift
let realm = try! Realm()

// 创建
try! realm.write {
    let dog = Dog()
    dog.name = "旺财"
    dog.age = 3
    realm.add(dog)
}

// 查询
let puppies = realm.objects(Dog.self).where { $0.age < 2 }
let sorted = realm.objects(Dog.self).sorted(byKeyPath: "name")

// 更新
try! realm.write {
    dog.age += 1
}

// 删除
try! realm.write {
    realm.delete(dog)
}
```
