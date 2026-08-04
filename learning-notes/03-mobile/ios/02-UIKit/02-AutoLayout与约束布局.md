# AutoLayout 与约束布局
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. NSLayoutConstraint 基础

```swift
let redView = UIView()
redView.backgroundColor = .systemRed
redView.translatesAutoresizingMaskIntoConstraints = false
view.addSubview(redView)

// 激活约束
NSLayoutConstraint.activate([
    redView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor, constant: 20),
    redView.leadingAnchor.constraint(equalTo: view.leadingAnchor, constant: 16),
    redView.trailingAnchor.constraint(equalTo: view.trailingAnchor, constant: -16),
    redView.heightAnchor.constraint(equalToConstant: 100)
])

// 优先级
let widthConstraint = redView.widthAnchor.constraint(equalToConstant: 200)
widthConstraint.priority = .defaultHigh  // 750
widthConstraint.isActive = true
```

## 2. 常用约束模式

```swift
// 居中
NSLayoutConstraint.activate([
    childView.centerXAnchor.constraint(equalTo: parentView.centerXAnchor),
    childView.centerYAnchor.constraint(equalTo: parentView.centerYAnchor),
    childView.widthAnchor.constraint(equalToConstant: 200),
    childView.heightAnchor.constraint(equalToConstant: 200)
])

// 填满父视图（带边距）
NSLayoutConstraint.activate([
    childView.topAnchor.constraint(equalTo: parentView.topAnchor, constant: 16),
    childView.bottomAnchor.constraint(equalTo: parentView.bottomAnchor, constant: -16),
    childView.leadingAnchor.constraint(equalTo: parentView.leadingAnchor, constant: 16),
    childView.trailingAnchor.constraint(equalTo: parentView.trailingAnchor, constant: -16)
])

// 宽高比
imageView.heightAnchor.constraint(equalTo: imageView.widthAnchor, multiplier: 9.0/16.0).isActive = true
```

## 3. Safe Area

```swift
// 适配刘海屏
NSLayoutConstraint.activate([
    contentView.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
    contentView.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor),
    contentView.leadingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.leadingAnchor),
    contentView.trailingAnchor.constraint(equalTo: view.safeAreaLayoutGuide.trailingAnchor)
])

// 获取安全区域边距
override func viewDidLayoutSubviews() {
    super.viewDidLayoutSubviews()
    let insets = view.safeAreaInsets  // top, bottom, left, right
}
```

## 4. Content Hugging / Compression Resistance

```swift
// Content Hugging: 抗拉伸（值越高越不容易被拉伸）
titleLabel.setContentHuggingPriority(.required, for: .horizontal)

// Compression Resistance: 抗压缩（值越高越不容易被压缩）
titleLabel.setContentCompressionResistancePriority(.required, for: .horizontal)
descLabel.setContentCompressionResistancePriority(.defaultLow, for: .horizontal)

// 典型场景：左边标题固定宽度，右边描述自适应
// titleLabel 高 Hugging → 不被拉伸
// descLabel 低 Hugging → 自动填充剩余空间
```

## 5. 动态约束更新

```swift
var heightConstraint: NSLayoutConstraint!

override func viewDidLoad() {
    super.viewDidLoad()
    heightConstraint = redView.heightAnchor.constraint(equalToConstant: 100)
    heightConstraint.isActive = true
}

func expandView() {
    heightConstraint.constant = 300
    UIView.animate(withDuration: 0.3) {
        self.view.layoutIfNeeded()
    }
}
```

## 6. SnapKit（第三方约束库）

```swift
import SnapKit

// 基础用法
redView.snp.makeConstraints { make in
    make.top.equalTo(view.safeAreaLayoutGuide).offset(20)
    make.leading.trailing.equalToSuperview().inset(16)
    make.height.equalTo(100)
}

// 居中 + 固定大小
blueView.snp.makeConstraints { make in
    make.center.equalToSuperview()
    make.size.equalTo(CGSize(width: 200, height: 200))
}

// 更新约束
redView.snp.updateConstraints { make in
    make.height.equalTo(300)
}

// 重做约束
redView.snp.remakeConstraints { make in
    make.edges.equalToSuperview()
}
```
