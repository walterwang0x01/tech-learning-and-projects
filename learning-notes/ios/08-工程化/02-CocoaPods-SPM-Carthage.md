# CocoaPods / SPM / Carthage
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. CocoaPods

```ruby
# Podfile
platform :ios, '16.0'
use_frameworks!

target 'MyApp' do
  pod 'Alamofire', '~> 5.8'
  pod 'SnapKit', '~> 5.6'
  pod 'Kingfisher', '~> 7.0'
  pod 'SwiftLint'

  target 'MyAppTests' do
    inherit! :search_paths
    pod 'Quick'
    pod 'Nimble'
  end
end

post_install do |installer|
  installer.pods_project.targets.each do |target|
    target.build_configurations.each do |config|
      config.build_settings['IPHONEOS_DEPLOYMENT_TARGET'] = '16.0'
    end
  end
end
```

```bash
# 常用命令
pod init              # 创建 Podfile
pod install           # 安装依赖
pod update            # 更新依赖
pod update Alamofire  # 更新指定库
pod outdated          # 查看可更新的库
pod deintegrate       # 移除 CocoaPods
```

## 2. Swift Package Manager (SPM)

```swift
// Package.swift（本地包）
// swift-tools-version: 5.9
import PackageDescription

let package = Package(
    name: "MyLibrary",
    platforms: [.iOS(.v16)],
    products: [
        .library(name: "MyLibrary", targets: ["MyLibrary"]),
    ],
    dependencies: [
        .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.8.0"),
        .package(url: "https://github.com/SnapKit/SnapKit.git", from: "5.6.0"),
    ],
    targets: [
        .target(
            name: "MyLibrary",
            dependencies: ["Alamofire", "SnapKit"]
        ),
        .testTarget(
            name: "MyLibraryTests",
            dependencies: ["MyLibrary"]
        ),
    ]
)
```

```swift
// Xcode 中添加 SPM 依赖：
// File → Add Package Dependencies → 输入 GitHub URL
// 选择版本规则：Up to Next Major / Exact Version / Branch

// 代码中使用
import Alamofire
import SnapKit
```

## 3. Carthage

```
# Cartfile
github "Alamofire/Alamofire" ~> 5.8
github "SnapKit/SnapKit" ~> 5.6
github "onevcat/Kingfisher" ~> 7.0
```

```bash
# 构建
carthage update --platform iOS --use-xcframeworks

# 生成的 .xcframework 在 Carthage/Build/ 目录
# 手动拖入 Xcode → Target → Frameworks, Libraries
```

## 4. 三者对比

```
特性            CocoaPods       SPM             Carthage
─────────────────────────────────────────────────────────
集成方式        修改项目结构     Xcode 原生       手动链接
配置文件        Podfile         Package.swift    Cartfile
中心化          是（Specs仓库） 去中心化          去中心化
编译方式        源码/预编译      源码编译          预编译 framework
二进制缓存      支持            Xcode 15+        天然支持
学习成本        低              低               中
推荐场景        老项目兼容       新项目首选        需要预编译
```

## 5. SPM 本地包开发

```swift
// 项目中创建本地包用于模块化
// File → New → Package

// 主项目引用本地包
// 将包文件夹拖入 Xcode 项目
// Target → General → Frameworks → 添加本地包

// 本地包之间的依赖
.target(
    name: "Feature",
    dependencies: [
        .product(name: "Core", package: "CoreModule"),
    ]
)
```

## 6. Swift 6.3 与 SPM 新特性

<!-- 修复于 2026-07-10: 补充 Swift 6.4 当前状态（WWDC26 已发布但仍是 Xcode 27 beta，未出正式 toolchain），修正本节与"5. SPM 本地包开发"顺序颠倒问题（原文件中 6 排在 5 之前） -->
<!-- version-check: Swift 6.3.3 (stable, 2026-06-30), Swift 6.4 (WWDC26 announced, Xcode 27 beta, 尚未出正式 toolchain release), SPM with Swift Build preview, checked 2026-07-10 -->

> 🔄 更新于 2026-07-10：Swift 6.4 已在 WWDC26（2026-06-09）随 Xcode 27 beta 发布预览（async defer、更少并发样板代码、URL 解析提速 4x 等），但截至 2026-07 尚未在 swift.org 出正式 toolchain release，服务端 Swift / Linux CI 场景仍应使用 **Swift 6.3.3**（stable，2026-06-30）。App 开发可用 Xcode 27 beta 提前验证 Swift 6.4。

Swift 6.3（2026-03-24）为 SPM 带来了重要改进，包括 Swift Build 集成预览和预编译 Swift Syntax 支持。同时 Swift 6.3 新增 `@c` 属性实现 Swift→C 互操作，以及官方 Android SDK。来源：[Swift 6.3 Released](https://www.swift.org/blog/swift-6.3-released/)

### 6.1 SPM 新功能

```swift
// swift-tools-version: 6.3
import PackageDescription

let package = Package(
    name: "MyLibrary",
    platforms: [.iOS(.v18)],
    products: [
        .library(name: "MyLibrary", targets: ["MyLibrary"]),
    ],
    dependencies: [
        .package(url: "https://github.com/Alamofire/Alamofire.git", from: "5.10.0"),
        // Swift 6.3：预编译 Swift Syntax 支持（宏库编译更快）
        .package(url: "https://github.com/swiftlang/swift-syntax.git", from: "602.0.0"),
    ],
    targets: [
        .target(
            name: "MyLibrary",
            dependencies: ["Alamofire"]
        ),
        // 宏目标可以使用预编译的 swift-syntax
        .macro(
            name: "MyMacros",
            dependencies: [
                .product(name: "SwiftSyntaxMacros", package: "swift-syntax"),
            ]
        ),
        .testTarget(
            name: "MyLibraryTests",
            dependencies: ["MyLibrary"]
        ),
    ]
)
```

### 6.2 Swift Build 集成预览

```bash
# Swift 6.3 将 Swift Build 集成到 SPM（预览阶段）
# 统一构建引擎，跨平台一致的构建体验
swift build --build-system swift-build

# 传统构建系统仍然是默认选项
swift build
```

### 6.3 @c 属性（Swift→C 互操作）

```swift
// Swift 6.3 新增：将 Swift 函数暴露给 C 代码
@c
func callFromC() { ... }

// 生成的 C 头文件：
// void callFromC(void);

// 自定义 C 名称
@c(MyLibrary_callFromC)
func callFromC() { ... }

// 配合 @implementation 实现 C 头文件中声明的函数
@c @implementation
func callFromC() { ... }
```

### 6.4 模块选择器

```swift
import ModuleA
import ModuleB

// Swift 6.3：使用 :: 语法消除同名 API 歧义
let x = ModuleA::getValue()
let y = ModuleB::getValue()

// 访问 Swift 标准库的并发 API
let task = Swift::Task {
    // 异步工作
}
```

### 6.5 版本对比

```
特性                SPM (Swift 5.9)    SPM (Swift 6.3)
──────────────────────────────────────────────────────
构建引擎            llbuild            Swift Build（预览）
宏编译              源码编译            预编译 swift-syntax
C 互操作            桥接头文件          @c 属性
模块歧义            类型别名            :: 模块选择器
Android 支持        ❌                 ✅ 官方 SDK
```

> **建议**：新项目使用 `swift-tools-version: 6.3`，利用预编译 swift-syntax 加速宏编译。Swift Build 集成仍在预览阶段，生产项目暂时使用默认构建系统。
