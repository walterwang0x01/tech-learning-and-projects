# iOS 日志最佳实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Apple 统一日志系统

```swift
// iOS 14+ 推荐使用 Logger API
import OSLog

extension Logger {
    static let network = Logger(subsystem: Bundle.main.bundleIdentifier!, category: "Network")
    static let ui = Logger(subsystem: Bundle.main.bundleIdentifier!, category: "UI")
    static let auth = Logger(subsystem: Bundle.main.bundleIdentifier!, category: "Auth")
}

Logger.network.info("请求发起: \(url)")
Logger.auth.error("登录失败: \(error.localizedDescription)")
```

## 2. Logger 日志级别

| 级别 | 用途 | 持久化 | Console.app |
|------|------|--------|-------------|
| `.debug` | 开发调试，生产不记录 | ❌ | 仅调试可见 |
| `.info` | 有用但非关键 | 内存中 | ✅ |
| `.notice` | 关键业务事件（默认） | ✅ 持久化 | ✅ |
| `.error` | 错误，进程级问题 | ✅ 持久化 | ✅ |
| `.fault` | 系统级严重错误 | ✅ + 堆栈 | ✅ |

```swift
logger.debug("缓存命中: key=\(cacheKey)")
logger.notice("用户登录成功: userId=\(userId)")
logger.error("网络请求失败: \(error.localizedDescription)")
logger.fault("数据库损坏，无法恢复")
```

## 3. 隐私保护

```swift
let token = "sk-abc123secret"

// .public：明文显示
logger.info("用户: \(userId, privacy: .public)")
// .private（默认）：生产环境显示 <private>
logger.info("Token: \(token)")  // 生产: Token: <private>
// .sensitive：比 private 更严格
logger.info("密码: \(passwordHash, privacy: .sensitive)")
// 数值类型默认 public
logger.info("金额: \(amount)") // 99.9
```

## 4. OSSignpost 性能标记

```swift
// 配合 Instruments 使用
let signposter = OSSignposter(logger: Logger.network)

func fetchData() async throws -> Data {
    let state = signposter.beginInterval("fetchData", id: signposter.makeSignpostID())
    defer { signposter.endInterval("fetchData", state) }
    let (data, _) = try await URLSession.shared.data(from: url)
    signposter.emitEvent("数据接收完成", "\(data.count) bytes")
    return data
}
```

## 5. CocoaLumberjack

```swift
import CocoaLumberjack

func setupLogging() {
    DDLog.add(DDOSLogger.sharedInstance) // 控制台
    let fileLogger = DDFileLogger()
    fileLogger.rollingFrequency = 60 * 60 * 24  // 24h 轮转
    fileLogger.logFileManager.maximumNumberOfLogFiles = 7
    fileLogger.maximumFileSize = 10 * 1024 * 1024  // 10MB
    DDLog.add(fileLogger)
}

DDLogInfo("用户 \(userId) 登录")
DDLogError("网络错误: \(error)")
```

## 6. SwiftLog

```swift
// Apple 官方日志标准（服务端 + 客户端通用）
import Logging

LoggingSystem.bootstrap { label in
    var handler = StreamLogHandler.standardOutput(label: label)
    handler.logLevel = .info
    return handler
}

let logger = Logging.Logger(label: "com.example.app.network")
logger.info("请求发起", metadata: ["url": "\(url)", "method": "GET"])
```

## 7. 崩溃日志

```swift
// Firebase Crashlytics
import FirebaseCrashlytics

Crashlytics.crashlytics().log("用户进入支付页面")
Crashlytics.crashlytics().setCustomValue(userId, forKey: "user_id")
Crashlytics.crashlytics().record(error: error)

// Sentry iOS
import Sentry
SentrySDK.start { options in
    options.dsn = "https://xxx@sentry.io/123"
    options.tracesSampleRate = 0.2
    options.attachScreenshot = true
}
SentrySDK.capture(error: error)
```

## 8. 日志级别使用规范

| 级别 | 场景 | 示例 |
|------|------|------|
| debug | 开发调试 | 网络请求参数、JSON 解析细节 |
| info | 运行信息 | 页面浏览、缓存命中率 |
| notice | 关键业务 | 用户登录、支付成功 |
| error | 可恢复错误 | API 超时重试、数据格式异常 |
| fault | 不可恢复 | 数据库损坏、密钥丢失 |

## 9. 生产环境日志策略

```swift
final class AppLogger {
    static let shared = AppLogger()
    private let logger = Logger(subsystem: Bundle.main.bundleIdentifier!, category: "App")

    func debug(_ message: String) {
        #if DEBUG
        logger.debug("\(message, privacy: .public)")
        #endif
    }

    func info(_ message: String, metadata: [String: String] = [:]) {
        let meta = metadata.map { "\($0.key)=\($0.value)" }.joined(separator: ", ")
        logger.info("\(message) \(meta, privacy: .public)")
    }

    func error(_ message: String, error: Error? = nil) {
        logger.error("\(message): \(error?.localizedDescription ?? "unknown", privacy: .public)")
        if let error { Crashlytics.crashlytics().record(error: error) }
    }
}
```

## 10. 调试技巧

```swift
// Console.app：按 subsystem/category 过滤设备日志
// LLDB: log stream --predicate 'subsystem == "com.example.app"'
// Xcode 条件断点 → Action → Log Message → "Automatically continue"（不改代码加日志）
// Instruments → Logging 模板：可视化 os_log + OSSignpost 时间线
// 网络调试：Pulse (https://github.com/kean/Pulse) 可视化网络日志
```
