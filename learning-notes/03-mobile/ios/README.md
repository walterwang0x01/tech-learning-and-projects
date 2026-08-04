# iOS 技术学习笔记
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> 本目录包含 iOS 技术栈的学习笔记，按类别组织

## 📁 目录结构

```
ios/
├── 00-Swift基础/              # Swift 语言基础
│   ├── Swift语法基础.md
│   ├── Swift面向对象编程.md
│   ├── Swift协议与泛型.md
│   ├── Swift并发编程.md
│   └── Swift内存管理与ARC.md
│
├── 01-SwiftUI/                # SwiftUI 声明式UI
│   ├── SwiftUI基础与布局.md
│   ├── SwiftUI状态管理.md
│   ├── SwiftUI导航与路由.md
│   └── SwiftUI动画与手势.md
│
├── 02-UIKit/                  # UIKit 传统UI框架
│   ├── UIKit核心组件.md
│   ├── AutoLayout与约束布局.md
│   ├── UITableView与UICollectionView.md
│   └── UIKit导航与页面跳转.md
│
├── 03-数据持久化/              # 数据存储
│   ├── UserDefaults与Keychain.md
│   ├── Core Data数据库.md
│   ├── SwiftData与Realm.md
│   └── 文件系统与沙盒机制.md
│
├── 04-网络编程/                # 网络请求
│   ├── URLSession与网络请求.md
│   ├── Alamofire与Moya.md
│   ├── WebSocket与实时通信.md
│   └── RESTful API与JSON解析.md
│
├── 05-架构模式/                # 架构设计
│   ├── MVC-MVVM-MVP架构.md
│   ├── Combine响应式编程.md
│   ├── 依赖注入与模块化.md
│   └── Clean Architecture实践.md
│
├── 06-系统框架/                # Apple 系统框架
│   ├── 推送通知与后台任务.md
│   ├── Core Location与MapKit.md
│   ├── AVFoundation多媒体.md
│   └── Core Animation与Core Graphics.md
│
├── 07-性能优化/                # 性能调优
│   ├── Instruments性能分析.md
│   ├── 内存优化与泄漏排查.md
│   ├── 启动优化与包体积优化.md
│   └── 列表性能与渲染优化.md
│
├── 08-工程化/                  # 工程化实践
│   ├── Xcode项目配置与构建.md
│   ├── CocoaPods-SPM-Carthage.md
│   ├── 单元测试与UI测试.md
│   └── CI-CD与自动化发布.md
│
├── 09-跨平台/                  # 跨平台方案
│   ├── Flutter iOS集成.md
│   ├── React Native iOS集成.md
│   └── SwiftUI与UIKit混合开发.md
│
├── 10-面试准备/                # 面试题整理
│   ├── Swift语言面试题.md
│   ├── iOS系统与框架面试题.md
│   └── 架构与性能面试题.md
│
└── README.md                  # 本文件
```

## 📚 内容说明

### Swift 基础

- **Swift语法基础**：变量与常量（let/var）、数据类型、可选类型（Optional）、控制流、集合类型（Array/Dictionary/Set）、函数与闭包、枚举与结构体、错误处理
- **Swift面向对象编程**：类与结构体对比、属性（存储属性、计算属性、属性观察器）、方法、继承、初始化器、析构器、扩展（Extension）、访问控制
- **Swift协议与泛型**：协议定义与遵循、协议扩展、面向协议编程（POP）、泛型函数与泛型类型、关联类型、类型约束、where子句、不透明类型（some/any）
- **Swift并发编程**：async/await、Task与TaskGroup、Actor模型、Sendable协议、AsyncSequence、结构化并发、GCD（Grand Central Dispatch）、OperationQueue
- **Swift内存管理与ARC**：ARC原理、强引用与弱引用（weak/unowned）、循环引用与解决方案、值类型vs引用类型、Copy-on-Write、内存布局

### SwiftUI

- **SwiftUI基础与布局**：View协议、Text/Image/Button基础组件、HStack/VStack/ZStack布局、List与ForEach、修饰符链式调用、GeometryReader、LazyVGrid/LazyHGrid
- **SwiftUI状态管理**：@State、@Binding、@StateObject、@ObservedObject、@EnvironmentObject、@Published、ObservableObject协议、@Observable（iOS 17+）
- **SwiftUI导航与路由**：NavigationStack、NavigationLink、NavigationPath、Sheet/FullScreenCover、TabView、深度链接、路由管理方案
- **SwiftUI动画与手势**：withAnimation、Animation修饰符、transition、matchedGeometryEffect、手势识别（Tap/Drag/Long Press/Rotation/Magnification）、自定义动画

### UIKit

- **UIKit核心组件**：UIView、UILabel、UIButton、UIImageView、UITextField、UITextView、UISwitch、UISlider、UIScrollView、UIStackView
- **AutoLayout与约束布局**：NSLayoutConstraint、Visual Format Language、SnapKit/Masonry、Safe Area、Intrinsic Content Size、Content Hugging/Compression Resistance
- **UITableView与UICollectionView**：DataSource与Delegate、Cell复用机制、DiffableDataSource、Compositional Layout、自定义Cell、下拉刷新与加载更多
- **UIKit导航与页面跳转**：UINavigationController、UITabBarController、Present/Dismiss、Segue、Coordinator模式

### 数据持久化

- **UserDefaults与Keychain**：UserDefaults存取、@AppStorage、Keychain安全存储、KeychainAccess库
- **Core Data数据库**：数据模型设计、NSManagedObject、NSFetchRequest、NSPredicate、关系映射、数据迁移、CloudKit同步
- **SwiftData与Realm**：SwiftData（@Model、@Query、ModelContainer）、Realm（对象模型、查询、迁移）
- **文件系统与沙盒机制**：沙盒目录结构、FileManager、Documents/Library/tmp、App Groups共享数据

### 网络编程

- **URLSession与网络请求**：URLSession配置、URLRequest、数据任务/下载任务/上传任务、后台下载、证书校验、网络状态监听（NWPathMonitor）
- **Alamofire与Moya**：Alamofire（请求封装、拦截器、响应验证）、Moya（TargetType、Provider、插件机制）
- **WebSocket与实时通信**：URLSessionWebSocketTask、Starscream库、Socket.IO、实时消息推送
- **RESTful API与JSON解析**：Codable协议（Encodable/Decodable）、JSONDecoder/JSONEncoder、自定义编解码、CodingKeys、嵌套JSON处理

### 架构模式

- **MVC-MVVM-MVP架构**：MVC（Apple MVC、Massive ViewController问题）、MVVM（数据绑定、ViewModel职责）、MVP（Presenter模式）、VIPER
- **Combine响应式编程**：Publisher与Subscriber、Operators（map/filter/flatMap/combineLatest/merge）、Subject（PassthroughSubject/CurrentValueSubject）、@Published、Cancellable
- **依赖注入与模块化**：构造器注入、属性注入、Swinject容器、模块化拆分、SPM模块化、接口隔离
- **Clean Architecture实践**：分层架构（Presentation/Domain/Data）、Use Case、Repository模式、实体与DTO映射

### 系统框架

- **推送通知与后台任务**：本地通知（UNUserNotificationCenter）、远程推送（APNs）、后台刷新（BGTaskScheduler）、静默推送、通知扩展
- **Core Location与MapKit**：位置权限、CLLocationManager、地理编码、MKMapView、自定义标注、路线规划
- **AVFoundation多媒体**：音频播放（AVAudioPlayer）、视频播放（AVPlayer）、相机拍照与录像、音视频编辑、语音识别
- **Core Animation与Core Graphics**：CALayer属性、CABasicAnimation/CAKeyframeAnimation、CATransition、CGContext绑定、贝塞尔曲线、自定义绘制

### 性能优化

- **Instruments性能分析**：Time Profiler、Allocations、Leaks、Network、Energy Log、Core Animation
- **内存优化与泄漏排查**：循环引用检测、Xcode Memory Graph、MLeaksFinder、图片内存优化、大对象释放
- **启动优化与包体积优化**：冷启动/热启动、pre-main优化、dyld加载优化、Asset Catalog优化、无用代码移除、App Thinning
- **列表性能与渲染优化**：Cell复用、预计算高度、异步渲染、离屏渲染优化、图片解码优化

### 工程化

- **Xcode项目配置与构建**：Build Settings、Build Phases、Scheme配置、xcconfig文件、多环境配置（Debug/Release/Staging）
- **CocoaPods-SPM-Carthage**：CocoaPods（Podfile、私有Pod）、Swift Package Manager（Package.swift、本地/远程包）、Carthage
- **单元测试与UI测试**：XCTest框架、XCTestCase、Mock与Stub、异步测试、XCUITest UI自动化、快照测试
- **CI-CD与自动化发布**：Fastlane（lane、match、gym、deliver）、GitHub Actions、Xcode Cloud、TestFlight分发、App Store Connect API

### 跨平台

- **Flutter iOS集成**：Flutter Module嵌入、Platform Channel通信、混合导航栈
- **React Native iOS集成**：原生模块开发、Native UI组件、桥接通信
- **SwiftUI与UIKit混合开发**：UIHostingController、UIViewRepresentable、UIViewControllerRepresentable、渐进式迁移策略

### 面试准备

- **Swift语言面试题**：值类型vs引用类型、Optional原理、闭包捕获列表、ARC与循环引用、协议与泛型、async/await原理
- **iOS系统与框架面试题**：App生命周期、RunLoop、事件响应链、离屏渲染、AutoLayout原理、推送通知流程
- **架构与性能面试题**：MVVM vs MVC、Combine vs RxSwift、启动优化方案、内存泄漏排查、卡顿检测与优化

## 🎯 学习路径建议

### 基础阶段
1. **Swift语言**：语法基础 → 面向对象 → 协议与泛型 → 内存管理
2. **SwiftUI**：基础组件 → 布局 → 状态管理 → 导航 → 动画
3. **UIKit**（了解）：核心组件 → AutoLayout → TableView/CollectionView

### 进阶阶段
4. **数据持久化**：UserDefaults → Core Data / SwiftData → 文件系统
5. **网络编程**：URLSession → Codable → Alamofire/Moya
6. **架构模式**：MVVM → Combine → Clean Architecture

### 高级阶段
7. **系统框架**：推送通知 → 地图定位 → 多媒体 → Core Animation
8. **性能优化**：Instruments → 内存优化 → 启动优化 → 渲染优化
9. **工程化**：包管理 → 测试 → CI/CD → 自动化发布
10. **面试准备**：Swift面试题 → iOS系统面试题 → 架构面试题

## 📖 使用说明

- 所有笔记从个人学习过程中整理，已移除敏感信息
- 包含代码示例和最佳实践
- 适合系统学习和面试准备

## 🔗 相关资源

- [Apple Developer Documentation](https://developer.apple.com/documentation/)
- [Swift 官方文档](https://docs.swift.org/swift-book/)
- [SwiftUI Tutorials](https://developer.apple.com/tutorials/swiftui)
- [Hacking with Swift](https://www.hackingwithswift.com/)
