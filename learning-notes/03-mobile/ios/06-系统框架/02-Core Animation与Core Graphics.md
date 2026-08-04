# Core Animation 与 Core Graphics
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. CALayer 基础

```swift
let layer = CALayer()
layer.frame = CGRect(x: 50, y: 50, width: 200, height: 200)
layer.backgroundColor = UIColor.systemBlue.cgColor
layer.cornerRadius = 20
layer.borderWidth = 2
layer.borderColor = UIColor.white.cgColor
layer.shadowColor = UIColor.black.cgColor
layer.shadowOpacity = 0.3
layer.shadowOffset = CGSize(width: 0, height: 4)
layer.shadowRadius = 8
view.layer.addSublayer(layer)

// 渐变层
let gradientLayer = CAGradientLayer()
gradientLayer.frame = view.bounds
gradientLayer.colors = [UIColor.systemBlue.cgColor, UIColor.systemPurple.cgColor]
gradientLayer.startPoint = CGPoint(x: 0, y: 0)
gradientLayer.endPoint = CGPoint(x: 1, y: 1)
view.layer.insertSublayer(gradientLayer, at: 0)

// 形状层
let shapeLayer = CAShapeLayer()
shapeLayer.path = UIBezierPath(ovalIn: CGRect(x: 0, y: 0, width: 100, height: 100)).cgPath
shapeLayer.fillColor = UIColor.systemRed.cgColor
shapeLayer.strokeColor = UIColor.white.cgColor
shapeLayer.lineWidth = 3
```

## 2. CABasicAnimation

```swift
// 位移动画
let moveAnimation = CABasicAnimation(keyPath: "position.x")
moveAnimation.fromValue = 50
moveAnimation.toValue = 300
moveAnimation.duration = 1.0
moveAnimation.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
layer.add(moveAnimation, forKey: "move")

// 缩放动画
let scaleAnimation = CABasicAnimation(keyPath: "transform.scale")
scaleAnimation.fromValue = 1.0
scaleAnimation.toValue = 1.5
scaleAnimation.duration = 0.5
scaleAnimation.autoreverses = true
layer.add(scaleAnimation, forKey: "scale")

// 旋转动画
let rotateAnimation = CABasicAnimation(keyPath: "transform.rotation.z")
rotateAnimation.fromValue = 0
rotateAnimation.toValue = CGFloat.pi * 2
rotateAnimation.duration = 2.0
rotateAnimation.repeatCount = .infinity
layer.add(rotateAnimation, forKey: "rotate")
```

## 3. CAKeyframeAnimation

```swift
// 关键帧路径动画
let pathAnimation = CAKeyframeAnimation(keyPath: "position")
let path = UIBezierPath()
path.move(to: CGPoint(x: 50, y: 300))
path.addCurve(to: CGPoint(x: 300, y: 300),
              controlPoint1: CGPoint(x: 100, y: 100),
              controlPoint2: CGPoint(x: 250, y: 500))
pathAnimation.path = path.cgPath
pathAnimation.duration = 2.0
pathAnimation.timingFunction = CAMediaTimingFunction(name: .easeInEaseOut)
layer.add(pathAnimation, forKey: "pathMove")

// 颜色关键帧
let colorAnimation = CAKeyframeAnimation(keyPath: "backgroundColor")
colorAnimation.values = [UIColor.red.cgColor, UIColor.green.cgColor, UIColor.blue.cgColor]
colorAnimation.keyTimes = [0, 0.5, 1.0]
colorAnimation.duration = 3.0
layer.add(colorAnimation, forKey: "colorChange")
```

## 4. CAAnimationGroup

```swift
let group = CAAnimationGroup()
group.animations = [moveAnimation, scaleAnimation, rotateAnimation]
group.duration = 2.0
group.fillMode = .forwards
group.isRemovedOnCompletion = false
layer.add(group, forKey: "group")
```

## 5. Core Graphics 绘制

```swift
class CustomDrawView: UIView {
    override func draw(_ rect: CGRect) {
        guard let context = UIGraphicsGetCurrentContext() else { return }

        // 矩形
        context.setFillColor(UIColor.systemBlue.cgColor)
        context.fill(CGRect(x: 20, y: 20, width: 100, height: 60))

        // 圆形
        context.setFillColor(UIColor.systemRed.cgColor)
        context.fillEllipse(in: CGRect(x: 150, y: 20, width: 80, height: 80))

        // 线条
        context.setStrokeColor(UIColor.systemGreen.cgColor)
        context.setLineWidth(3)
        context.move(to: CGPoint(x: 20, y: 150))
        context.addLine(to: CGPoint(x: 300, y: 150))
        context.strokePath()
    }
}
```

## 6. UIBezierPath 贝塞尔曲线

```swift
class HeartView: UIView {
    override func draw(_ rect: CGRect) {
        let path = UIBezierPath()
        let center = CGPoint(x: rect.midX, y: rect.midY)

        path.move(to: CGPoint(x: center.x, y: center.y + 30))
        path.addCurve(to: CGPoint(x: center.x, y: center.y - 30),
                      controlPoint1: CGPoint(x: center.x - 60, y: center.y),
                      controlPoint2: CGPoint(x: center.x - 30, y: center.y - 50))
        path.addCurve(to: CGPoint(x: center.x, y: center.y + 30),
                      controlPoint1: CGPoint(x: center.x + 30, y: center.y - 50),
                      controlPoint2: CGPoint(x: center.x + 60, y: center.y))

        UIColor.systemRed.setFill()
        path.fill()
    }
}

// 圆形进度条
class CircularProgressView: UIView {
    var progress: CGFloat = 0.7 {
        didSet { progressLayer.strokeEnd = progress }
    }

    private let progressLayer = CAShapeLayer()

    override func layoutSubviews() {
        super.layoutSubviews()
        let path = UIBezierPath(arcCenter: CGPoint(x: bounds.midX, y: bounds.midY),
                                radius: bounds.width / 2 - 10,
                                startAngle: -.pi / 2,
                                endAngle: .pi * 1.5,
                                clockwise: true)
        progressLayer.path = path.cgPath
        progressLayer.strokeColor = UIColor.systemBlue.cgColor
        progressLayer.fillColor = UIColor.clear.cgColor
        progressLayer.lineWidth = 8
        progressLayer.lineCap = .round
        progressLayer.strokeEnd = progress
        layer.addSublayer(progressLayer)
    }
}
```

## 7. iOS 26 Liquid Glass 与 Core Animation

<!-- version-check: iOS 26 Liquid Glass, Core Animation, checked 2026-04-24 -->

> 🔄 更新于 2026-04-24

iOS 26 引入了 Liquid Glass 设计语言，这是自 iOS 7 以来最大的视觉重设计。Liquid Glass 是一种动态半透明材质，能够实时模糊背后内容、反射环境光线，并响应触摸和指针交互。

来源：[Apple WWDC25 Session 284](https://developer.apple.com/videos/play/wwdc2025/284/)、[Donny Wals: Designing custom UI with Liquid Glass](https://www.donnywals.com/designing-custom-ui-with-liquid-glass-on-ios-26/)

### 7.1 SwiftUI 中使用 Liquid Glass

```swift
import SwiftUI

// 基础 Glass Effect
struct GlassButton: View {
    var body: some View {
        Button("操作") {
            // 按钮动作
        }
        .buttonStyle(.glass)  // 内置 Glass 按钮样式
    }
}

// 自定义 Glass Effect
struct FloatingActionButton: View {
    var body: some View {
        Button(action: { /* 动作 */ }) {
            Image(systemName: "plus")
                .font(.title2)
                .padding()
        }
        .glassEffect(.regular)  // 应用 Liquid Glass 材质
    }
}

// GlassEffectContainer：多个 Glass 元素分组混合
struct ToolbarView: View {
    var body: some View {
        GlassEffectContainer {
            HStack(spacing: 16) {
                ForEach(0..<4) { index in
                    Button(action: {}) {
                        Image(systemName: "star.fill")
                    }
                    .glassEffect()
                    .glassEffectID(index)  // 用于 morphing 动画
                }
            }
        }
    }
}
```

### 7.2 UIKit 中使用 Liquid Glass

```swift
import UIKit

// UIKit 中应用 Liquid Glass
class GlassViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        // 工具栏自动获得 Liquid Glass 外观
        // 使用 Xcode 26 重新编译即可，无需额外代码

        // 自定义 Glass 视图
        let glassView = UIView()
        glassView.frame = CGRect(x: 50, y: 100, width: 200, height: 60)

        // 使用 UIGlassEffect 配置
        let config = UIGlassEffect()
        config.isInteractive = true  // 响应触摸交互
        glassView.configuration = config

        view.addSubview(glassView)
    }
}
```

### 7.3 Liquid Glass 设计原则

Liquid Glass 应该用于**浮在内容之上**的 UI 元素，而不是内容本身：

| 适合使用 Glass | 不适合使用 Glass |
|---------------|----------------|
| 工具栏、标签栏 | 列表单元格 |
| 浮动操作按钮 | 文本内容区域 |
| 导航栏 | 图片/视频内容 |
| 弹出菜单 | 表单输入框 |

### 7.4 Core Animation 与 Liquid Glass 的关系

Liquid Glass 底层依赖 Core Animation 的图层合成能力。系统控件（UINavigationBar、UITabBar 等）在 Xcode 26 编译后自动获得 Liquid Glass 外观。自定义 Core Animation 动画仍然完全兼容，开发者可以在 Glass 元素上叠加 `CABasicAnimation`、`CAKeyframeAnimation` 等传统动画。

`glassEffectID` 和 `glassEffectUnion` 修饰符支持 Glass 元素之间的 morphing 动画——当视图层级变化时，Glass 效果会平滑过渡而非突然切换。
