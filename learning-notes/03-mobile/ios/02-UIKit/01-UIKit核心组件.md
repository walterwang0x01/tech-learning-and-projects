# UIKit 核心组件
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. UIView 基础

```swift
// 创建视图
let view = UIView(frame: CGRect(x: 0, y: 0, width: 200, height: 100))
view.backgroundColor = .systemBlue
view.layer.cornerRadius = 12
view.layer.shadowColor = UIColor.black.cgColor
view.layer.shadowOpacity = 0.2
view.layer.shadowOffset = CGSize(width: 0, height: 2)
view.layer.shadowRadius = 4

// 添加子视图
parentView.addSubview(view)
parentView.insertSubview(view, at: 0)
parentView.bringSubviewToFront(view)
view.removeFromSuperview()
```

## 2. UILabel

```swift
let label = UILabel()
label.text = "Hello UIKit"
label.font = .systemFont(ofSize: 16, weight: .bold)
label.textColor = .label
label.textAlignment = .center
label.numberOfLines = 0  // 多行显示
label.lineBreakMode = .byWordWrapping

// 富文本
let attributed = NSMutableAttributedString(string: "加粗和颜色")
attributed.addAttribute(.font, value: UIFont.boldSystemFont(ofSize: 18), range: NSRange(location: 0, length: 2))
attributed.addAttribute(.foregroundColor, value: UIColor.red, range: NSRange(location: 3, length: 2))
label.attributedText = attributed
```

## 3. UIButton

```swift
let button = UIButton(type: .system)
button.setTitle("点击", for: .normal)
button.setTitleColor(.white, for: .normal)
button.backgroundColor = .systemBlue
button.layer.cornerRadius = 8
button.addTarget(self, action: #selector(buttonTapped), for: .touchUpInside)

// iOS 15+ UIButton.Configuration
var config = UIButton.Configuration.filled()
config.title = "确认"
config.image = UIImage(systemName: "checkmark")
config.imagePadding = 8
config.cornerStyle = .medium
let modernButton = UIButton(configuration: config)
```

## 4. UIImageView

```swift
let imageView = UIImageView()
imageView.image = UIImage(named: "photo")
imageView.contentMode = .scaleAspectFill
imageView.clipsToBounds = true
imageView.layer.cornerRadius = 40  // 圆形头像

// SF Symbols
imageView.image = UIImage(systemName: "heart.fill")
imageView.tintColor = .systemRed
```

## 5. UITextField

```swift
let textField = UITextField()
textField.placeholder = "请输入用户名"
textField.borderStyle = .roundedRect
textField.clearButtonMode = .whileEditing
textField.returnKeyType = .done
textField.delegate = self

// UITextFieldDelegate
extension ViewController: UITextFieldDelegate {
    func textFieldShouldReturn(_ textField: UITextField) -> Bool {
        textField.resignFirstResponder()
        return true
    }
    func textField(_ textField: UITextField, shouldChangeCharactersIn range: NSRange,
                   replacementString string: String) -> Bool {
        let maxLength = 20
        let currentText = textField.text ?? ""
        let newLength = currentText.count + string.count - range.length
        return newLength <= maxLength
    }
}
```

## 6. UIScrollView

```swift
let scrollView = UIScrollView()
scrollView.contentSize = CGSize(width: view.bounds.width, height: 2000)
scrollView.showsVerticalScrollIndicator = true
scrollView.isPagingEnabled = false
scrollView.delegate = self

// 分页滚动
scrollView.isPagingEnabled = true
scrollView.contentSize = CGSize(width: view.bounds.width * 3, height: view.bounds.height)

extension ViewController: UIScrollViewDelegate {
    func scrollViewDidScroll(_ scrollView: UIScrollView) {
        let offsetY = scrollView.contentOffset.y
        print("滚动偏移: \(offsetY)")
    }
}
```

## 7. UIStackView

```swift
let stackView = UIStackView(arrangedSubviews: [label, button, imageView])
stackView.axis = .vertical
stackView.spacing = 12
stackView.alignment = .fill
stackView.distribution = .fillEqually

// 动态添加/移除
stackView.addArrangedSubview(newView)
stackView.removeArrangedSubview(oldView)
oldView.removeFromSuperview()

// 嵌套 StackView 构建复杂布局
let row = UIStackView(arrangedSubviews: [icon, titleLabel, Spacer()])
row.axis = .horizontal
row.spacing = 8
```

## 8. UIKit + iOS 26 Liquid Glass 适配

> 🔄 更新于 2026-05-18

<!-- version-check: UIKit iOS 26 Liquid Glass, SDK 26 mandatory (2026-04-28), checked 2026-05-18 -->

iOS 26 引入 Liquid Glass 设计语言。用 Xcode 26 SDK 重新编译后，原生 UIKit 组件会自动获得磨砂玻璃外观；自定义 UI 需要按需适配。来源：[WWDC25 - Build a UIKit app with the new design](https://developer.apple.com/videos/play/wwdc2025/284/)、[Liquid Glass Cheatsheet](https://github.com/GonzaloFuentes28/LiquidGlassCheatsheet)

### 8.1 自动适配的组件

```
重新编译即生效（无需改代码）
├── UINavigationBar / UIToolbar
├── UITabBar
├── UISearchBar
├── UIPopover / UIBarButtonItem
└── 系统 Sheet（pageSheet / formSheet）
```

### 8.2 自定义 View 启用 Liquid Glass

<!-- 修复于 2026-05-31: 移除私有 API UIBackdropView（历来非公开，App Store 会拒）。
     iOS 26 Liquid Glass 的公开 API 是 UIGlassEffect / UIGlassContainerEffect，
     通过 UIVisualEffectView 使用。来源：腾讯云 iOS26 适配指南之 UIVisualEffectView -->

```swift
// 1) UIVisualEffectView + UIGlassEffect（iOS 26 公开 API）
let glass = UIVisualEffectView(effect: UIGlassEffect())   // iOS 26 新效果类型
glass.frame = container.bounds
glass.clipsToBounds = true
container.insertSubview(glass, at: 0)

// 2) 多个玻璃元素相互融合时，用 UIGlassContainerEffect 容器
let containerEffect = UIGlassContainerEffect()
let glassContainer = UIVisualEffectView(effect: containerEffect)
glassContainer.frame = panel.bounds
panel.insertSubview(glassContainer, at: 0)

// 3) 工具栏间距 + tint
let spacer = UIBarButtonItem(systemItem: .flexibleSpace) // ToolbarSpacer 等价
toolbarItems = [back, spacer, share, action]
toolbar.tintColor = .systemBlue
```

### 8.3 Sheet / Popover 改造

```swift
// iOS 26 Sheet 边缘自带模糊和 detents 自适应
let sheet = SettingsViewController()
if let pc = sheet.sheetPresentationController {
    pc.detents = [.custom { $0.maximumDetentValue * 0.4 }, .large()]
    pc.prefersScrollingExpandsWhenScrolledToEdge = false
    pc.preferredCornerRadius = 28           // Liquid Glass 推荐圆角
}
present(sheet, animated: true)
```

### 8.4 关闭 Liquid Glass（迁移期）

```swift
// 部分场景下若希望保留旧外观（例如品牌一致性），
// 可显式将 appearance 设回 default。
let appearance = UINavigationBarAppearance()
appearance.configureWithDefaultBackground()      // 不使用 transparentBackground
navigationItem.standardAppearance = appearance
navigationItem.scrollEdgeAppearance = appearance
```

来源：[Stackademic - Disable or Opt-Out Liquid Glass](https://blog.stackademic.com/disable-or-opt-out-liquid-glass-in-swiftui-and-uikit-ios-26-5c6d55d3e8e5)、[Fatbobman - Liquid Glass Adaptation in UIKit + SwiftUI Hybrid](https://fatbobman.com/en/posts/grow-on-ios26/)

### 8.5 iOS 27 重要前瞻

- iOS 27（预计 2026-09 发布）将强制要求 UIScene lifecycle，详见工程化笔记 → [Xcode 项目配置与构建 §8.2](../08-工程化/01-Xcode项目配置与构建.md)
- Liquid Glass 在 iOS 27 进入"必须采用"阶段，opt-out 路径可能逐步关闭，新组件应优先按 Liquid Glass 设计

来源：[ClassMethod - iOS 27 / Xcode 27 准备指南](https://dev.classmethod.jp/en/articles/ios27-xcode27-migration-preparation-guide/)

## 9. WWDC26：UIKit Adaptivity 与新 API（2027 releases）

> 更新于 2026-07-10

<!-- version-check: UIKit iOS 27 adaptivity APIs (WWDC26), UIScene lifecycle mandatory, checked 2026-07-10 -->

WWDC26 对 UIKit 的更新体量不大（无新的顶层范式），但集中在**强制 Adaptivity（自适应布局）**上，这是继 Liquid Glass 之后 UIKit 又一次面向"同一份代码适配多种运行环境"（iPhone Mirroring、iPad Split View、外接显示器）的推动（[Modernize your UIKit app - WWDC26](https://developer.apple.com/videos/play/wwdc2026/278/)）。

**必须改的旧写法**（`UIScene` lifecycle 成为强制要求）：

```swift
// ❌ 过时：依赖 AppDelegate 生命周期、直接取 mainScreen
let scale = UIScreen.main.scale
if UIDevice.current.userInterfaceIdiom == .phone {
    // 布局决策
}

// ✅ 新写法：通过 traitCollection / windowScene 动态获取
let scale = traitCollection.displayScale
let availableSpace = windowScene?.effectiveGeometry  // 而不是 UIScreen.main.bounds
// 布局决策改用 size class，不再依赖 idiom 或方向
```

原因：iPhone Mirroring、Split View 等场景下，`UIScreen.main`、`UIUserInterfaceIdiom`、`Interface Orientation` 都不能可靠反映应用实际可用空间——即使 idiom 返回 `.phone`，应用也可能是被镜像投屏或以非全屏方式运行。`UIRequiresFullScreen` 在 iOS 27 起废弃。

**新增 API**：

- **Tab Bar → Sidebar**：`tabBarController.sidebar.preferredPlacement` 让 iPhone 应用也能在合适场景下（如横屏、外接显示器）自动切换为侧边栏
- **导航栏最小化**：`barMinimizationBehavior`（配套新枚举 `UIBarMinimizeBehavior`）让导航栏在滚动时可以滑出收起，呼应 SwiftUI 侧的 `toolbarMinimizeBehavior`
- **Apple Intelligence 集成**：菜单自动显示 "Ask Siri" 按钮；新的 View Annotations API 配合 `AppEntities` 为 Siri 提供页面上下文
- **TextKit 2 增强**：`NSTextViewportRenderingSurface` 支持视口级渲染、`UITextAttachmentViewProviderReusePolicy` 让附件视图在滚动进出时可复用，避免反复创建销毁
- **场景管理**：`UISceneAccessory` 挂载场景配件、`UISceneClosureConfirmation` 关闭场景前二次确认；`CADisplayLink` 改为 scene-scoped

**迁移辅助**：Xcode 27 内置一个专门的"App Modernization"编码 Agent Skill，能理解上述 adaptivity 迁移任务，自动完成 `mainScreen` 引用替换、方向判断改 size class、迁移到 scene lifecycle 等改动；该 skill 也可导出给其他 Agent/工具使用。

来源：[What's New in UIKit in iOS 27 - Kyle Howells](https://ikyle.me/blog/2026/whats-new-in-uikit-ios-27)、[WWDC26 for UIKit App Developers — Adaptivity](https://medium.com/@choiysapple/wwdc26-for-uikit-app-developers-adaptivity-ef4d23b0b95b)、[UIKit Full API Diff iOS 26.2 → iOS 27 beta](https://gist.github.com/kylehowells/32c7f7475698b5f74eeb183f8db9d186)
