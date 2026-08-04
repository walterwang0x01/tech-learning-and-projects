# Instruments 性能分析
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Time Profiler（CPU 分析）

```swift
// 识别耗时操作：Xcode → Product → Profile → Time Profiler
// 常见问题：主线程执行耗时任务

// ❌ 主线程执行耗时操作
func loadData() {
    let data = try! Data(contentsOf: largeFileURL)  // 阻塞主线程
    processData(data)
}

// ✅ 移到后台线程
func loadData() {
    Task.detached {
        let data = try Data(contentsOf: largeFileURL)
        let result = processData(data)
        await MainActor.run { self.updateUI(result) }
    }
}
```

## 2. Allocations（内存分配）

```swift
// 追踪内存分配：查看对象创建和销毁
// 关注 Persistent（持久）对象数量是否持续增长

// ❌ 频繁创建大对象
func renderCells() {
    for item in items {
        let formatter = DateFormatter()  // 每次循环都创建
        cell.dateLabel.text = formatter.string(from: item.date)
    }
}

// ✅ 复用对象
private let dateFormatter: DateFormatter = {
    let f = DateFormatter()
    f.dateFormat = "yyyy-MM-dd"
    return f
}()

func renderCells() {
    for item in items {
        cell.dateLabel.text = dateFormatter.string(from: item.date)
    }
}
```

## 3. Leaks（内存泄漏）

```swift
// Leaks 工具自动检测循环引用

// ❌ 闭包循环引用
class ViewController: UIViewController {
    var timer: Timer?

    override func viewDidLoad() {
        timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { _ in
            self.updateUI()  // 强引用 self → 泄漏
        }
    }
}

// ✅ 使用 [weak self]
timer = Timer.scheduledTimer(withTimeInterval: 1, repeats: true) { [weak self] _ in
    self?.updateUI()
}

// deinit 验证释放
deinit {
    print("\(Self.self) 已释放")
    timer?.invalidate()
}
```

## 4. Energy Log（能耗分析）

```swift
// 高能耗操作：GPS、网络、CPU 密集计算

// ❌ 持续高精度定位
locationManager.desiredAccuracy = kCLLocationAccuracyBest
locationManager.startUpdatingLocation()

// ✅ 按需定位
locationManager.desiredAccuracy = kCLLocationAccuracyHundredMeters
locationManager.requestLocation()  // 单次定位

// ✅ 批量网络请求
func syncData() async {
    // 合并多个小请求为一个批量请求
    let batchRequest = BatchRequest(items: pendingItems)
    try await apiClient.send(batchRequest)
}
```

## 5. Network（网络分析）

```swift
// 使用 Instruments Network 或 Charles 抓包分析

// 优化策略
let config = URLSessionConfiguration.default
config.urlCache = URLCache(memoryCapacity: 50_000_000, diskCapacity: 100_000_000)
config.requestCachePolicy = .returnCacheDataElseLoad

// 使用 ETag / Last-Modified 条件请求
var request = URLRequest(url: url)
request.setValue(cachedETag, forHTTPHeaderField: "If-None-Match")
```

## 6. os_signpost 自定义埋点

```swift
import os.signpost

let log = OSLog(subsystem: "com.app", category: "Performance")

func loadImages() {
    let signpostID = OSSignpostID(log: log)
    os_signpost(.begin, log: log, name: "ImageLoading", signpostID: signpostID)

    // 执行操作...
    downloadAndDecodeImages()

    os_signpost(.end, log: log, name: "ImageLoading", signpostID: signpostID)
}
```


## 7. Xcode 26 Instruments 新工具

<!-- version-check: Xcode 26.6（当前稳定版，Xcode 27 beta 3 开发中）, Instruments 2026, checked 2026-07-10 -->
<!-- 修复于 2026-07-10: Xcode 稳定版已从 26.4 更新到 26.6（2026-06-25），Xcode 27 beta 处于开发预览阶段 -->

> 🔄 更新于 2026-04-27

### 7.1 Foundation Models Instrument

Xcode 26 新增了专用的 **Foundation Models** 性能分析工具，用于测量和优化设备端 AI 模型会话的性能。

**分析维度**：
- **Asset 加载时间**：模型资源加载耗时
- **Session 信息**：总响应时间、Prompt 处理时间
- **Token 计数**：输入/输出 Token 数量（系统模型上限 4,096 tokens）
- **Tool Calling 耗时**：工具调用的处理时间，识别耗时较长的工具

```swift
import FoundationModels

// 创建会话并添加工具
let session = LanguageModelSession(tools: [MoodTool()]) {
    "You're a haiku generator."
}

// 预热会话以减少响应延迟
session.prewarm()

// 如果已知 Prompt，可以传入预热以进一步降低延迟
let prompt = Prompt { "Generate a haiku about Swift" }
session.prewarm(promptPrefix: prompt)

// 生成响应
let response = try await session.respond(to: prompt)
```

**优化技巧**：
- 使用 `session.prewarm()` 预热会话，减少首次响应延迟
- 传入 `promptPrefix` 预热可进一步降低延迟（系统提前处理 Prompt）
- 通过 Instruments 识别耗时较长的 Tool Calling，考虑缓存结果
- 调整 Prompt 减少不必要的工具调用次数

> ⚠️ 注意：iOS 模拟器上 Token 计数始终为 0（Xcode 26.1 已修复部分问题，但仍需真机测试）

> 来源：[Foundation Models profiling with Xcode Instruments](https://artemnovichkov.com/blog/foundation-models-profiling-with-xcode-instruments)

### 7.2 Processor Trace 和 CPU Counter

Xcode 26 新增两个硬件辅助性能分析工具：

- **Processor Trace**：基于 Apple Silicon 硬件追踪能力，提供指令级别的 CPU 执行追踪
- **CPU Counter**：硬件性能计数器，测量缓存命中率、分支预测等底层指标

这两个工具需要 Apple Silicon Mac，提供比 Time Profiler 更精细的性能数据。

> 来源：[What's new in Xcode 26](https://developer.apple.com/xcode/whats-new/)

### 7.3 Run Comparison（Xcode 26.4 新增）

> 🔄 更新于 2026-05-06

Xcode 26.4 给 Instruments 添加了 Run Comparison 功能，可以直接对比两次 profiling 的调用树，找出哪些函数变快了、哪些变慢了。优化前后的性能对比不再需要手动记笔记。

操作路径：View → Detail Area → Compare With… 或 jump bar 上的 ⇆ 按钮，选择要对比的 run，结果会以差值标注展示每个函数耗时的变化。

> 来源：[Xcode 26.4 Release Notes](https://mjtsai.com/blog/2026/03/25/xcode-26-4/)

### 7.4 2026 年 iOS 性能分析工具选型

| 场景 | 推荐工具 | 说明 |
| ---- | ------ | ---- |
| CPU 热点分析 | Time Profiler | 通用 CPU 分析，首选工具 |
| 指令级追踪 | Processor Trace（Xcode 26） | Apple Silicon 硬件辅助，更精细 |
| SwiftUI 卡顿定位 | SwiftUI Instrument（Xcode 26） | view body 耗时、重建原因、Cause & Effect Graph |
| 内存分配追踪 | Allocations | 追踪对象创建和持久化 |
| 内存泄漏检测 | Leaks | 自动检测循环引用 |
| AI 模型性能 | Foundation Models（Xcode 26） | 设备端模型响应时间和 Token 分析 |
| 能耗分析 | Energy Log | GPS、网络、CPU 能耗 |
| 优化前后对比 | Run Comparison（Xcode 26.4） | 两次 profiling 的调用树差值对比 |
| 自定义埋点 | os_signpost | 精确测量特定代码段 |
