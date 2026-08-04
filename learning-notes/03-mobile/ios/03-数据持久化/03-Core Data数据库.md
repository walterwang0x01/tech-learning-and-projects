# Core Data 数据库
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Core Data Stack 初始化

```swift
import CoreData

class CoreDataStack {
    static let shared = CoreDataStack()

    lazy var persistentContainer: NSPersistentContainer = {
        let container = NSPersistentContainer(name: "MyApp")
        container.loadPersistentStores { _, error in
            if let error = error { fatalError("Core Data 加载失败: \(error)") }
        }
        container.viewContext.automaticallyMergesChangesFromParent = true
        return container
    }()

    var context: NSManagedObjectContext {
        persistentContainer.viewContext
    }

    func saveContext() {
        guard context.hasChanges else { return }
        do { try context.save() }
        catch { print("保存失败: \(error)") }
    }
}
```

## 2. NSManagedObject 子类

```swift
// Xcode 自动生成或手动创建
@objc(Task)
public class Task: NSManagedObject {
    @NSManaged public var id: UUID
    @NSManaged public var title: String
    @NSManaged public var isCompleted: Bool
    @NSManaged public var createdAt: Date
    @NSManaged public var category: Category?  // 关系
}

extension Task {
    @nonobjc public class func fetchRequest() -> NSFetchRequest<Task> {
        return NSFetchRequest<Task>(entityName: "Task")
    }
}
```

## 3. CRUD 操作

```swift
class TaskRepository {
    private let context = CoreDataStack.shared.context

    // 创建
    func createTask(title: String) -> Task {
        let task = Task(context: context)
        task.id = UUID()
        task.title = title
        task.isCompleted = false
        task.createdAt = Date()
        CoreDataStack.shared.saveContext()
        return task
    }

    // 查询
    func fetchTasks(completed: Bool? = nil) -> [Task] {
        let request: NSFetchRequest<Task> = Task.fetchRequest()
        request.sortDescriptors = [NSSortDescriptor(keyPath: \Task.createdAt, ascending: false)]
        if let completed = completed {
            request.predicate = NSPredicate(format: "isCompleted == %@", NSNumber(value: completed))
        }
        return (try? context.fetch(request)) ?? []
    }

    // 更新
    func toggleTask(_ task: Task) {
        task.isCompleted.toggle()
        CoreDataStack.shared.saveContext()
    }

    // 删除
    func deleteTask(_ task: Task) {
        context.delete(task)
        CoreDataStack.shared.saveContext()
    }
}
```

## 4. NSFetchRequest 高级查询

```swift
// 复合谓词
let predicate = NSCompoundPredicate(andPredicateWithSubpredicates: [
    NSPredicate(format: "isCompleted == NO"),
    NSPredicate(format: "title CONTAINS[cd] %@", searchText)
])
request.predicate = predicate

// 分页
request.fetchLimit = 20
request.fetchOffset = page * 20

// 聚合查询
let countRequest = NSFetchRequest<NSNumber>(entityName: "Task")
countRequest.resultType = .countResultType
let count = try? context.fetch(countRequest).first?.intValue
```

## 5. 关系与数据模型

```swift
// 一对多关系：Category -> [Task]
// 在 .xcdatamodeld 中配置 relationship

// 访问关系
let category = Category(context: context)
category.name = "工作"
task.category = category  // 设置关系

// 获取某分类下的所有任务
let tasks = category.tasks?.allObjects as? [Task] ?? []
```

## 6. 轻量级迁移

```swift
// 在 persistentContainer 配置中启用自动迁移
let description = NSPersistentStoreDescription()
description.shouldMigrateStoreAutomatically = true
description.shouldInferMappingModelAutomatically = true
container.persistentStoreDescriptions = [description]
```
