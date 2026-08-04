# iOS 系统与框架面试题
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. App 生命周期

```swift
// UIKit 生命周期（SceneDelegate）
class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options: UIScene.ConnectionOptions) {
        // 场景创建
    }
    func sceneDidBecomeActive(_ scene: UIScene) { }    // 进入前台活跃
    func sceneWillResignActive(_ scene: UIScene) { }    // 即将进入非活跃
    func sceneDidEnterBackground(_ scene: UIScene) { }  // 进入后台
    func sceneWillEnterForeground(_ scene: UIScene) { } // 即将进入前台
}

// ViewController 生命周期
// init → loadView → viewDidLoad → viewWillAppear → viewDidAppear
// → viewWillDisappear → viewDidDisappear → deinit

// 常见问题：viewDidLoad 只调用一次，viewWillAppear 每次显示都调用
```

## 2. RunLoop

```swift
// RunLoop 是事件循环机制，处理输入源和定时器
// 主线程 RunLoop 自动启动，子线程需要手动启动

// Mode:
// .default: 默认模式
// .common: 包含 default + tracking
// .tracking: ScrollView 滚动时

// Timer 在滚动时停止的问题
let timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
    print("tick")
}
// ❌ 默认在 .default mode，滚动时不执行
// ✅ 添加到 .common mode
RunLoop.current.add(timer, forMode: .common)

// 子线程 RunLoop
DispatchQueue.global().async {
    let runLoop = RunLoop.current
    let timer = Timer(timeInterval: 1, repeats: true) { _ in print("子线程 tick") }
    runLoop.add(timer, forMode: .default)
    runLoop.run()  // 手动启动
}
```

## 3. 事件响应链

```swift
// 响应链：UIView → SuperView → ... → ViewController → Window → Application
// Hit Testing：从 Window 开始，递归调用 hitTest(_:with:) 找到最上层响应视图

// 自定义 Hit Test（扩大点击区域）
class LargeButton: UIButton {
    override func point(inside point: CGPoint, with event: UIEvent?) -> Bool {
        let expandedBounds = bounds.insetBy(dx: -20, dy: -20)
        return expandedBounds.contains(point)
    }
}

// 事件传递：hitTest → touchesBegan → touchesMoved → touchesEnded
// 如果当前视图不处理，沿响应链向上传递
override func touchesBegan(_ touches: Set<UITouch>, with event: UIEvent?) {
    // 处理触摸事件
    // 不调用 super 则事件不会继续传递
    super.touchesBegan(touches, with: event)
}
```

## 4. 离屏渲染

```swift
// 离屏渲染：GPU 在屏幕缓冲区之外开辟新缓冲区进行渲染
// 触发条件：
// - cornerRadius + masksToBounds/clipsToBounds
// - shadow（无 shadowPath）
// - mask
// - group opacity

// 检测：模拟器 → Debug → Color Off-screen Rendered（黄色高亮）

// ✅ 优化方案
// 1. 预设 shadowPath
view.layer.shadowPath = UIBezierPath(roundedRect: view.bounds, cornerRadius: 10).cgPath

// 2. 使用 CAShapeLayer 做圆角
// 3. 后台线程预渲染圆角图片
func roundedImage(_ image: UIImage, radius: CGFloat) -> UIImage {
    let renderer = UIGraphicsImageRenderer(size: image.size)
    return renderer.image { _ in
        let rect = CGRect(origin: .zero, size: image.size)
        UIBezierPath(roundedRect: rect, cornerRadius: radius).addClip()
        image.draw(in: rect)
    }
}
```

## 5. GCD 与多线程

```swift
// 队列类型
let serial = DispatchQueue(label: "com.app.serial")           // 串行队列
let concurrent = DispatchQueue(label: "com.app.concurrent",
                                attributes: .concurrent)       // 并发队列
let main = DispatchQueue.main                                  // 主队列（串行）
let global = DispatchQueue.global(qos: .userInitiated)         // 全局并发队列

// 同步 vs 异步
serial.sync { }   // 同步执行，阻塞当前线程
serial.async { }   // 异步执行，不阻塞

// ⚠️ 主线程 sync 调用主队列 → 死锁
// DispatchQueue.main.sync { }  // 死锁！

// 栅栏函数（读写锁）
class ThreadSafeArray<T> {
    private var array: [T] = []
    private let queue = DispatchQueue(label: "com.app.array", attributes: .concurrent)

    func read() -> [T] {
        queue.sync { array }
    }

    func write(_ element: T) {
        queue.async(flags: .barrier) { self.array.append(element) }
    }
}
```

## 6. KVO / KVC / Notification

```swift
// KVO（键值观察）
class UserProfile: NSObject {
    @objc dynamic var name: String = ""
}

let observation = profile.observe(\.name, options: [.new, .old]) { _, change in
    print("名字从 \(change.oldValue ?? "") 变为 \(change.newValue ?? "")")
}

// NotificationCenter
NotificationCenter.default.post(name: .userDidLogin, object: nil, userInfo: ["userId": "123"])

NotificationCenter.default.addObserver(forName: .userDidLogin, object: nil, queue: .main) { notification in
    let userId = notification.userInfo?["userId"] as? String
}
```

> 🔄 更新于 2026-05-02

<!-- version-check: iOS 26, SwiftUI iOS 26, Xcode 26.4, checked 2026-05-02 -->

## 7. 2026 年 iOS 系统面试新题

```swift
// Q: iOS 26 的 Liquid Glass 对 UIKit 应用有什么影响？
// A: 用 Xcode 26 重新编译即可自动获得 Liquid Glass 外观：
// - UINavigationBar、UITabBar、UIToolbar 自动应用 Glass 效果
// - 自定义 UI 组件可能需要调整以适配新的视觉风格
// - iOS 27 将强制要求 UIScene 生命周期（不再支持 AppDelegate-only）
// 建议：尽早用 Xcode 26 编译测试，检查自定义 UI 的兼容性

// Q: SwiftUI 原生 WebView 怎么用？
// A: iOS 26 新增原生 WebView，不再需要 UIViewRepresentable：
// WebPage 是 @Observable 类，提供完整的导航控制
// 支持 JavaScript 交互、Cookie 管理、导航委托

// Q: Xcode 26.3 的 Agentic Coding 是什么？
// A: Xcode 26.3 引入 AI Agent 编码能力：
// - Claude Agent 和 Codex 可自主分析项目、修改文件
// - 搜索文档、捕获 Previews 并迭代修复
// - 标志着 IDE 从"辅助工具"向"AI 协作伙伴"转变

// Q: Privacy Manifests 在 2026 年有什么变化？
// A: Privacy Manifests 已成为 App Store 提交的强制要求：
// - 所有使用 Required Reason API 的框架必须声明用途
// - 第三方 SDK 必须提供 PrivacyInfo.xcprivacy 文件
// - App Store Connect 会自动检查并拒绝不合规的提交
```
