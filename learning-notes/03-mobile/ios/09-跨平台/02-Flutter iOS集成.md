# Flutter iOS 集成
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 创建 Flutter Module

```bash
# 创建 Flutter 模块
flutter create --template module my_flutter_module

# 目录结构
# my_flutter_module/
# ├── .ios/          # iOS 宿主工程（自动生成）
# ├── lib/           # Dart 代码
# └── pubspec.yaml
```

## 2. CocoaPods 集成

```ruby
# iOS 项目的 Podfile
flutter_application_path = '../my_flutter_module'
load File.join(flutter_application_path, '.ios', 'Flutter', 'podhelper.rb')

target 'MyApp' do
  install_all_flutter_pods(flutter_application_path)
end

post_install do |installer|
  flutter_post_install(installer)
end
```

## 3. 打开 Flutter 页面

```swift
import Flutter

class AppDelegate: FlutterAppDelegate {
    lazy var flutterEngine = FlutterEngine(name: "my_engine")

    override func application(_ application: UIApplication,
                              didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?) -> Bool {
        flutterEngine.run()
        return super.application(application, didFinishLaunchingWithOptions: launchOptions)
    }
}

// 跳转到 Flutter 页面
class ViewController: UIViewController {
    @objc func openFlutter() {
        let engine = (UIApplication.shared.delegate as! AppDelegate).flutterEngine
        let flutterVC = FlutterViewController(engine: engine, nibName: nil, bundle: nil)
        present(flutterVC, animated: true)
    }
}
```

## 4. Platform Channel（原生通信）

```swift
// iOS 端：接收 Flutter 调用
let channel = FlutterMethodChannel(name: "com.app/native",
                                    binaryMessenger: flutterVC.binaryMessenger)

channel.setMethodCallHandler { (call, result) in
    switch call.method {
    case "getBatteryLevel":
        let level = UIDevice.current.batteryLevel
        result(Int(level * 100))
    case "showNativeAlert":
        let args = call.arguments as? [String: Any]
        let title = args?["title"] as? String ?? ""
        self.showAlert(title: title)
        result(nil)
    default:
        result(FlutterMethodNotImplemented)
    }
}

// iOS 端：主动调用 Flutter
channel.invokeMethod("updateData", arguments: ["key": "value"]) { result in
    print("Flutter 返回: \(result ?? "nil")")
}
```

```dart
// Flutter 端（Dart）
const channel = MethodChannel('com.app/native');

// 调用原生方法
Future<int> getBatteryLevel() async {
  final level = await channel.invokeMethod<int>('getBatteryLevel');
  return level ?? 0;
}

// 接收原生调用
channel.setMethodCallHandler((call) async {
  if (call.method == 'updateData') {
    final data = call.arguments as Map;
    // 处理数据
    return 'success';
  }
});
```

## 5. EventChannel（事件流）

```swift
// iOS 端：持续发送事件
let eventChannel = FlutterEventChannel(name: "com.app/events",
                                        binaryMessenger: flutterVC.binaryMessenger)

class LocationStreamHandler: NSObject, FlutterStreamHandler {
    var eventSink: FlutterEventSink?

    func onListen(withArguments arguments: Any?, eventSink events: @escaping FlutterEventSink) -> FlutterError? {
        self.eventSink = events
        startLocationUpdates()
        return nil
    }

    func onCancel(withArguments arguments: Any?) -> FlutterError? {
        eventSink = nil
        stopLocationUpdates()
        return nil
    }

    func sendLocation(_ lat: Double, _ lng: Double) {
        eventSink?(["lat": lat, "lng": lng])
    }
}

eventChannel.setStreamHandler(LocationStreamHandler())
```

## 6. Flutter 3.32 / Dart 3.8 版本演进

> 🔄 更新于 2026-05-01

Flutter 3.32 是当前稳定版（2026-04-30），Dart 3.8 同步发布。iOS 集成方面有多项重要改进。来源：[Flutter Release Notes](https://docs.flutter.dev/release/release-notes)、[Dart 3.8 Release](https://medium.com/dartlang/dart-3-8)

<!-- version-check: Flutter 3.32.0, Dart 3.8, checked 2026-05-01 -->

### iOS 集成关键变化

| 特性 | Flutter 3.24 | Flutter 3.32 |
|------|-------------|-------------|
| 最低 iOS 版本 | iOS 12 | iOS 13 |
| Swift Package Manager | 实验性 | ✅ 默认启用 |
| Impeller 渲染引擎 | iOS 默认 | iOS + Android 默认 |
| Platform View 性能 | 一般 | 显著提升（Impeller 优化） |
| Dart 版本 | 3.5 | 3.8 |

### Swift Package Manager 集成（推荐）

Flutter 3.32 默认使用 Swift Package Manager 替代 CocoaPods：

```swift
// 不再需要 Podfile！
// Flutter 3.32 自动生成 Package.swift 集成

// 如果仍需 CocoaPods（兼容旧插件）：
// flutter config --no-enable-swift-package-manager
```

### Dart 3.8 新特性对 iOS 开发的影响

```dart
// Dart 3.8：Null-aware 元素（简化列表构建）
Widget build(BuildContext context) {
  return Column(
    children: [
      Text('标题'),
      ?subtitle,  // 如果 subtitle 为 null，自动跳过
      ?trailing,  // 不再需要 if (trailing != null) trailing!
    ],
  );
}

// Dart 3.8：交叉引用类型提升
void processData(Object data) {
  if (data is String && data.length > 5) {
    // data 自动提升为 String 类型
    print(data.substring(0, 5));
  }
}
```

### 版本选择建议

```
你的项目情况？
├─ 新项目 → Flutter 3.32 + Swift Package Manager
├─ 现有 CocoaPods 项目 → 逐步迁移到 SPM
├─ 需要 iOS 12 支持 → 停留在 Flutter 3.27.x
└─ 性能敏感 → Impeller 已默认启用，无需额外配置
```
