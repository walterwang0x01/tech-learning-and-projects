# Xcode 项目配置与构建
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Build Settings 关键配置

```
// 常用 Build Settings
PRODUCT_BUNDLE_IDENTIFIER = com.company.app
SWIFT_VERSION = 5.9
IPHONEOS_DEPLOYMENT_TARGET = 16.0
TARGETED_DEVICE_FAMILY = 1,2  // 1=iPhone, 2=iPad

// 优化级别
// Debug:   SWIFT_OPTIMIZATION_LEVEL = -Onone（无优化，方便调试）
// Release: SWIFT_OPTIMIZATION_LEVEL = -O（速度优先）
//          或 -Osize（体积优先）

// 代码签名
CODE_SIGN_STYLE = Automatic
DEVELOPMENT_TEAM = XXXXXXXXXX
```

## 2. xcconfig 配置文件

```
// Base.xcconfig
PRODUCT_NAME = MyApp
SWIFT_VERSION = 5.9
IPHONEOS_DEPLOYMENT_TARGET = 16.0

// Debug.xcconfig
#include "Base.xcconfig"
API_BASE_URL = https:\/\/dev-api.example.com
SWIFT_ACTIVE_COMPILATION_CONDITIONS = DEBUG
GCC_OPTIMIZATION_LEVEL = 0

// Release.xcconfig
#include "Base.xcconfig"
API_BASE_URL = https:\/\/api.example.com
SWIFT_ACTIVE_COMPILATION_CONDITIONS = RELEASE
ENABLE_TESTABILITY = NO
```

## 3. 多环境配置

```swift
// Info.plist 中引用 xcconfig 变量
// API_BASE_URL = $(API_BASE_URL)

// 代码中读取
enum Environment {
    static var apiBaseURL: String {
        Bundle.main.infoDictionary?["API_BASE_URL"] as? String ?? ""
    }

    static var isDebug: Bool {
        #if DEBUG
        return true
        #else
        return false
        #endif
    }
}

// 编译条件
#if DEBUG
let logger = DebugLogger()
#elseif STAGING
let logger = StagingLogger()
#else
let logger = ProductionLogger()
#endif
```

## 4. Scheme 配置

```swift
// Xcode → Product → Scheme → Edit Scheme
// - Build: 选择编译的 Target
// - Run: 选择 Debug/Release Configuration
// - Test: 配置测试 Target
// - Archive: 发布配置

// 创建多个 Scheme：MyApp-Dev, MyApp-Staging, MyApp-Prod
// 每个 Scheme 关联不同的 xcconfig
```

## 5. Build Phase 脚本

```bash
# SwiftLint 检查（Build Phases → New Run Script Phase）
if which swiftlint > /dev/null; then
    swiftlint
else
    echo "warning: SwiftLint not installed"
fi

# 自动递增 Build Number
buildNumber=$(/usr/libexec/PlistBuddy -c "Print CFBundleVersion" "${PROJECT_DIR}/${INFOPLIST_FILE}")
buildNumber=$(($buildNumber + 1))
/usr/libexec/PlistBuddy -c "Set :CFBundleVersion $buildNumber" "${PROJECT_DIR}/${INFOPLIST_FILE}"
```

## 6. 编译速度优化

```swift
// 1. 查看编译耗时
// Build Settings → Other Swift Flags → -Xfrontend -warn-long-function-bodies=100

// 2. 减少类型推断复杂度
// ❌ 编译器推断耗时
let result = items.map { $0.value }.filter { $0 > 0 }.reduce(0, +)

// ✅ 显式标注类型
let values: [Int] = items.map { $0.value }
let filtered: [Int] = values.filter { $0 > 0 }
let result: Int = filtered.reduce(0, +)

// 3. 模块化编译（SPM 分模块，只重编修改的模块）
// 4. 开启 Eager Linking: Build Settings → EAGER_LINKING = YES
```

## 7. Xcode 26 版本演进

> 🔄 更新于 2026-04-18

<!-- version-check: Xcode 26.4, checked 2026-04-18 -->

Xcode 26 于 WWDC 2025 发布，当前稳定版为 Xcode 26.4（2026-03-24）。来源：[Xcode What's New](https://developer.apple.com/xcode/whats-new/)、[Apple Newsroom - Xcode 26.3](https://www.apple.com/gq/newsroom/2026/02/xcode-26-point-3-unlocks-the-power-of-agentic-coding/)

### 版本对比

| 版本 | 发布时间 | Swift | 关键特性 |
|------|---------|-------|---------|
| Xcode 16 | 2024-09 | Swift 6.0 | Swift 6 严格并发、Swift Testing |
| Xcode 26 | 2025-09 | Swift 6.2 | AI 编码助手、Liquid Glass、Approachable Concurrency |
| Xcode 26.3 | 2026-02 | Swift 6.2 | **Agentic Coding**（Claude Agent、Codex 集成） |
| Xcode 26.4 | 2026-03 | Swift 6.2 | 稳定性修复 |
| Xcode 26.5 | Beta | Swift 6.2 | 预览中 |

### AI Coding Intelligence

Xcode 26 内置 AI 编码助手（Coding Intelligence），默认使用 ChatGPT，也支持其他 LLM。

```
// Xcode 26 AI 功能
// - 代码补全和生成
// - 代码重构建议
// - Bug 修复建议
// - 自然语言交互

// Xcode 26.3 Agentic Coding
// - Claude Agent 和 Codex 可以自主分析项目
// - 修改文件、搜索文档、更新项目设置
// - 捕获 Xcode Previews 并迭代修复
```

### 性能改进

```
// Xcode 26 性能数据
// - 下载体积减少 24%
// - 工作区加载速度提升 40%
// - 编译缓存（Compilation Caching）加速增量构建
```

### Build Settings 更新

```
// Xcode 26 推荐配置
SWIFT_VERSION = 6.2
IPHONEOS_DEPLOYMENT_TARGET = 18.0  // 或 26.0（新命名）

// Approachable Concurrency（新项目默认开启）
// Build Settings → Swift Compiler - Upcoming Features
// → Default Actor Isolation = MainActor

// 严格内存安全（可选）
// SWIFT_STRICT_MEMORY_SAFETY = YES
```


## 8. iOS 26 SDK 强制要求与 iOS 27 准备

> 🔄 更新于 2026-05-18

<!-- version-check: SDK 26 deadline 2026-04-28, iOS 27 / Xcode 27 breaking changes preparation, checked 2026-05-18 -->

### 8.1 SDK 26 提交 Deadline（已生效）

自 2026-04-28 起，所有上传到 App Store Connect 的 App 必须使用 iOS 26 SDK（即 Xcode 26 及以上）构建。这是 Apple 持续收紧的工具链要求节奏：

```
SDK Deadline 节奏
├── 2026-04-28：所有 App 必须基于 SDK 26 构建（已生效）
├── iOS 27 / Xcode 27（预计 2026-09）：UIScene lifecycle 强制
└── iOS 27 之后：Liquid Glass 强制采用、UIKit 旧式 lifecycle 不再启动
```

来源：[The iOS Weekly Brief #46](https://vladkhambir.substack.com/p/the-ios-weekly-brief-issue-46)、[Apple Developer 升级要求](https://developer.apple.com/news/releases/)

### 8.2 UIScene Lifecycle 强制迁移（iOS 27 必须完成）

Apple 在 WWDC25 已声明：iOS 26 之后的下一个主版本（iOS 27）中，所有用 `latest SDK` 构建的 UIKit 应用必须采用 UIScene 生命周期，否则不会启动。Xcode 26 控制台已开始打印警告。

```
"UIScene lifecycle will soon be required.
 Failure to adopt will result in an assert in the future."
```

来源：[Apple Developer Forum 820807](https://developer.apple.com/forums/thread/820807)、[TN3187](https://developer.apple.com/documentation/technotes/tn3187-migrating-to-the-uikit-scene-based-life-cycle)、[Flutter UIScene 迁移指南](https://docs.flutter.dev/release/breaking-changes/uiscenedelegate)

#### 检查项目是否需要迁移

```swift
// 满足任一条件需要迁移：
// 1) Info.plist 中缺失 UIApplicationSceneManifest，或没有声明 configurations
// 2) AppDelegate 未实现 application(_:configurationForConnecting:options:)
```

#### 最小迁移示例

```xml
<!-- Info.plist -->
<key>UIApplicationSceneManifest</key>
<dict>
    <key>UIApplicationSupportsMultipleScenes</key>
    <false/>
    <key>UISceneConfigurations</key>
    <dict>
        <key>UIWindowSceneSessionRoleApplication</key>
        <array>
            <dict>
                <key>UISceneConfigurationName</key>
                <string>Default Configuration</string>
                <key>UISceneDelegateClassName</key>
                <string>$(PRODUCT_MODULE_NAME).SceneDelegate</string>
            </dict>
        </array>
    </dict>
</dict>
```

```swift
// AppDelegate
@main
class AppDelegate: UIResponder, UIApplicationDelegate {
    func application(
        _ application: UIApplication,
        configurationForConnecting connectingSceneSession: UISceneSession,
        options: UIScene.ConnectionOptions
    ) -> UISceneConfiguration {
        UISceneConfiguration(name: "Default Configuration", sessionRole: connectingSceneSession.role)
    }
}

// SceneDelegate
class SceneDelegate: UIResponder, UIWindowSceneDelegate {
    var window: UIWindow?

    func scene(_ scene: UIScene, willConnectTo session: UISceneSession, options: UIScene.ConnectionOptions) {
        guard let windowScene = scene as? UIWindowScene else { return }
        let window = UIWindow(windowScene: windowScene)
        window.rootViewController = RootViewController()
        self.window = window
        window.makeKeyAndVisible()
    }

    func sceneDidBecomeActive(_ scene: UIScene) { /* 替代 applicationDidBecomeActive */ }
    func sceneWillResignActive(_ scene: UIScene) { /* 替代 applicationWillResignActive */ }
}
```

> ⚠️ 待确认：第三方 SDK（推送、地图、广告）若在 `applicationDidBecomeActive` 中执行关键初始化，需要同步迁移到 `sceneDidBecomeActive`，否则可能丢失事件。常见的影响包括 APNs token 上报、Deep Link 处理、广告初始化。

来源：[Courier - iOS 27 UISceneDelegate Push Notification Deadline](https://www.courier.com/blog/ios-27-uiscenedelegate-push-notification-deadline-what-breaks-and-how-to)

### 8.3 Liquid Glass 自动适配

用 Xcode 26 SDK 构建后，原生 UIKit 组件（NavigationBar、TabBar、Toolbar、Popover、SearchBar）会自动应用 Liquid Glass 样式，无需修改代码。来源：[Apple Newsroom - 新软件设计](https://www.apple.com/newsroom/2025/06/apple-introduces-a-delightful-and-elegant-new-software-design/)、[Krishna Substack - Xcode 26 + April 28 Deadline](https://krishna806083.substack.com/p/xcode-26-liquid-glass-and-the-april)

```swift
// 自定义 UI 启用 Liquid Glass（UIKit）
let backdrop = UIBackdropView()
backdrop.style = .liquidGlass        // iOS 26+ 新样式
view.insertSubview(backdrop, at: 0)

// 工具栏隐式适配
navigationItem.compactAppearance?.configureWithDefaultBackground()
navigationItem.scrollEdgeAppearance?.configureWithTransparentBackground()
```

### 8.4 升级路径与 CI 配置

```yaml
# .github/workflows/ios-ci.yml — 切换到 Xcode 26
jobs:
  build:
    runs-on: macos-15
    steps:
      - uses: maxim-lobanov/setup-xcode@v1
        with:
          xcode-version: '26.4'   # 或 '26.5' Beta
      - run: xcodebuild -version  # 验证 SDK 26
      - run: xcodebuild build -scheme MyApp -destination 'generic/platform=iOS'
```

```
Xcode 26 / 26.3 / 26.4 / 26.5 选型
├── 生产线打包：Xcode 26.4（最新稳定版）
├── 体验 Agentic Coding（Claude/Codex）：Xcode 26.3+
└── Beta 体验 + 26.5 新特性验证：保留单独的 mac runner，避免影响主线
```

来源：[Apple Newsroom - Xcode 26.3 Agentic Coding](https://www.apple.com/ca/newsroom/2026/02/xcode-26-point-3-unlocks-the-power-of-agentic-coding/)、[ClassMethod - iOS 27 / Xcode 27 准备指南](https://dev.classmethod.jp/en/articles/ios27-xcode27-migration-preparation-guide/)
