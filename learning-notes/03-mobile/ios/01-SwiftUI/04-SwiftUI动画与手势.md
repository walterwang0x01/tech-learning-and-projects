# SwiftUI 动画与手势
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 基础动画

```swift
struct AnimationDemo: View {
    @State private var isExpanded = false

    var body: some View {
        VStack {
            RoundedRectangle(cornerRadius: 12)
                .fill(.blue)
                .frame(width: isExpanded ? 300 : 100, height: isExpanded ? 300 : 100)
                .animation(.spring(response: 0.5, dampingFraction: 0.6), value: isExpanded)

            Button("切换") {
                isExpanded.toggle()
            }

            // 显式动画
            Button("显式动画") {
                withAnimation(.easeInOut(duration: 0.5)) {
                    isExpanded.toggle()
                }
            }
        }
    }
}
```

## 2. 过渡动画

```swift
struct TransitionDemo: View {
    @State private var showDetail = false

    var body: some View {
        VStack {
            if showDetail {
                DetailView()
                    .transition(.asymmetric(
                        insertion: .slide.combined(with: .opacity),
                        removal: .scale.combined(with: .opacity)
                    ))
            }
            Button("切换") {
                withAnimation { showDetail.toggle() }
            }
        }
    }
}
```

## 3. 手势

```swift
struct GestureDemo: View {
    @State private var offset = CGSize.zero
    @State private var scale: CGFloat = 1.0
    @GestureState private var dragOffset = CGSize.zero

    var body: some View {
        Image("photo")
            .resizable()
            .scaledToFit()
            .scaleEffect(scale)
            .offset(x: offset.width + dragOffset.width,
                    y: offset.height + dragOffset.height)
            // 拖拽手势
            .gesture(
                DragGesture()
                    .updating($dragOffset) { value, state, _ in
                        state = value.translation
                    }
                    .onEnded { value in
                        offset.width += value.translation.width
                        offset.height += value.translation.height
                    }
            )
            // 缩放手势
            .gesture(
                MagnificationGesture()
                    .onChanged { value in scale = value }
            )
            // 双击重置
            .onTapGesture(count: 2) {
                withAnimation {
                    scale = 1.0
                    offset = .zero
                }
            }
    }
}
```

## 5. iOS 26 动画新特性

> 🔄 更新于 2026-04-18

<!-- version-check: SwiftUI Animation iOS 26, checked 2026-04-18 -->

iOS 26 引入了 `@Animatable` 宏，大幅简化自定义动画的实现。来源：[SwiftUI for iOS 26](https://www.infoq.com/news/2025/06/swiftui-ios26-liquid-glass/)

### @Animatable 宏

`@Animatable` 宏自动合成 `Animatable` 协议的 `animatableData` 属性，无需手动实现。

```swift
// iOS 26 之前：需要手动实现 animatableData
struct OldWave: Shape {
    var amplitude: CGFloat
    var frequency: CGFloat

    var animatableData: AnimatablePair<CGFloat, CGFloat> {
        get { AnimatablePair(amplitude, frequency) }
        set {
            amplitude = newValue.first
            frequency = newValue.second
        }
    }

    func path(in rect: CGRect) -> Path { /* ... */ }
}

// iOS 26：使用 @Animatable 宏自动合成
@Animatable
struct Wave: Shape {
    var amplitude: CGFloat    // 自动参与动画
    var frequency: CGFloat    // 自动参与动画
    @AnimatableIgnored var lineWidth: CGFloat  // 排除在动画之外

    func path(in rect: CGRect) -> Path { /* ... */ }
}

// 使用
Wave(amplitude: isActive ? 50 : 10, frequency: 3, lineWidth: 2)
    .stroke(.blue, lineWidth: 2)
    .animation(.easeInOut(duration: 1), value: isActive)
```

`@Animatable` 适用于 View、ViewModifier、Shape、TextRenderer 等类型，显著减少动画相关的样板代码。
