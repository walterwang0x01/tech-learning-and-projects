# Flutter 与 Dart 基础
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Dart 语法

```dart
// 变量
var name = '张三';           // 类型推断
String city = '北京';        // 显式类型
final age = 25;              // 运行时常量
const pi = 3.14;             // 编译时常量
int? nullable;               // 可空类型

// 函数
String greet(String name, {int age = 18}) => 'Hello $name, $age';

// 类
class User {
  final String name;
  final int age;
  User({required this.name, required this.age});
}

// 异步
Future<String> fetchData() async {
  final response = await http.get(Uri.parse('https://api.example.com'));
  return response.body;
}
```

## 2. Widget 体系

```dart
// StatelessWidget（无状态）
class Greeting extends StatelessWidget {
  final String name;
  const Greeting({super.key, required this.name});

  @override
  Widget build(BuildContext context) {
    return Text('Hello, $name', style: const TextStyle(fontSize: 24));
  }
}

// StatefulWidget（有状态）
class Counter extends StatefulWidget {
  const Counter({super.key});
  @override
  State<Counter> createState() => _CounterState();
}

class _CounterState extends State<Counter> {
  int _count = 0;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text('Count: $_count'),
        ElevatedButton(
          onPressed: () => setState(() => _count++),
          child: const Text('+1'),
        ),
      ],
    );
  }
}
```

## 3. 布局

```dart
// Row / Column（类似 Flex）
Row(
  mainAxisAlignment: MainAxisAlignment.spaceBetween,
  children: [Text('左'), Text('右')],
)

// Container（类似 div）
Container(
  padding: const EdgeInsets.all(16),
  margin: const EdgeInsets.symmetric(horizontal: 8),
  decoration: BoxDecoration(
    color: Colors.white,
    borderRadius: BorderRadius.circular(8),
    boxShadow: [BoxShadow(color: Colors.grey.shade200, blurRadius: 8)],
  ),
  child: const Text('卡片内容'),
)

// ListView（列表）
ListView.builder(
  itemCount: items.length,
  itemBuilder: (context, index) => ListTile(title: Text(items[index].name)),
)
```

## 4. 状态管理

```dart
// Provider（官方推荐）
class CounterProvider extends ChangeNotifier {
  int _count = 0;
  int get count => _count;
  void increment() { _count++; notifyListeners(); }
}

// 使用
ChangeNotifierProvider(
  create: (_) => CounterProvider(),
  child: Consumer<CounterProvider>(
    builder: (context, counter, child) => Text('${counter.count}'),
  ),
)

// Riverpod（更现代的方案）
final counterProvider = StateNotifierProvider<CounterNotifier, int>((ref) => CounterNotifier());
```

## 5. Flutter 3.41 与 Dart 3.11 版本演进

<!-- version-check: Flutter 3.41.5, Dart 3.11.1, checked 2026-05-15 -->

> 🔄 更新于 2026-05-15

<!-- 修复于 2026-05-15: 补丁版本更新到 3.41.5（2026-05-05 docs.flutter.dev 确认） -->

Flutter 3.41.5 是当前稳定版（2026-05），搭配 Dart 3.11.1。从 Flutter 3.32（2025-05）到 3.41，经历了多次重大升级。来源：[Flutter 3.41 What Changed](https://alexanderobregon.substack.com/p/what-changed-in-flutter-341-and-why)

### 5.1 关键版本里程碑

| 版本 | 时间 | 核心特性 |
|------|------|---------|
| 3.32 | 2025-05 | Web Hot Reload（实验性）、Cupertino squircle、Firebase AI 集成 |
| 3.38+ | 2025 | iOS 26 SDK 支持 |
| 3.41 | 2026-02 | Impeller 2.0、AI DevTools Profiler |
| 3.41.5 | 2026-05 | 当前稳定版，Dart 3.11.1 |

### 5.2 Impeller 2.0 渲染引擎

Impeller 2.0 是 Flutter 自研的 GPU 加速渲染引擎，在 Android API 29+ 设备上默认启用：
- 消除着色器编译卡顿（jank-free）
- 更一致的帧率表现
- 更低的 GPU 内存占用

### 5.3 Dart 3.11 新特性

Dart 3.11（2026-03）聚焦开发体验改进，无新语言特性。来源：[Announcing Dart 3.11](https://dart.dev/blog/announcing-dart-3-11)

- **更智能的分析服务器**：更快的代码补全和诊断
- **pub 客户端增强**：依赖解析和发布流程改进
- **AI 支持增强**：更好的 AI 辅助编码集成
- **Dart 3.10 引入的 dot shorthands**：`.foo` 简写语法在 3.11 中持续优化

### 5.4 版本选择建议

| 场景 | 推荐版本 |
|------|---------|
| 新项目 | Flutter 3.41.x + Dart 3.11.1 |
| iOS 26 适配 | Flutter 3.38+ |
| 稳定生产环境 | Flutter 3.41.5（最新 stable） |
