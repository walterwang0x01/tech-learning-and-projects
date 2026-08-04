# SwiftUI 与 UIKit 混合开发
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. UIHostingController（SwiftUI → UIKit）

```swift
import SwiftUI

// 在 UIKit 中使用 SwiftUI 视图
class ViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        let swiftUIView = ProfileView(user: currentUser)
        let hostingController = UIHostingController(rootView: swiftUIView)

        addChild(hostingController)
        view.addSubview(hostingController.view)
        hostingController.view.translatesAutoresizingMaskIntoConstraints = false
        NSLayoutConstraint.activate([
            hostingController.view.topAnchor.constraint(equalTo: view.topAnchor),
            hostingController.view.bottomAnchor.constraint(equalTo: view.bottomAnchor),
            hostingController.view.leadingAnchor.constraint(equalTo: view.leadingAnchor),
            hostingController.view.trailingAnchor.constraint(equalTo: view.trailingAnchor)
        ])
        hostingController.didMove(toParent: self)
    }
}

// Push SwiftUI 页面
func showSwiftUIDetail() {
    let detailView = DetailView(itemId: selectedId)
    let hostingVC = UIHostingController(rootView: detailView)
    navigationController?.pushViewController(hostingVC, animated: true)
}
```


## 2. UIViewRepresentable（UIKit → SwiftUI）

```swift
// 将 UIKit 视图包装为 SwiftUI 视图
struct MapViewWrapper: UIViewRepresentable {
    @Binding var region: MKCoordinateRegion

    func makeUIView(context: Context) -> MKMapView {
        let mapView = MKMapView()
        mapView.delegate = context.coordinator
        return mapView
    }

    func updateUIView(_ mapView: MKMapView, context: Context) {
        mapView.setRegion(region, animated: true)
    }

    func makeCoordinator() -> Coordinator {
        Coordinator(self)
    }

    class Coordinator: NSObject, MKMapViewDelegate {
        var parent: MapViewWrapper
        init(_ parent: MapViewWrapper) { self.parent = parent }

        func mapView(_ mapView: MKMapView, regionDidChangeAnimated animated: Bool) {
            parent.region = mapView.region
        }
    }
}

// 在 SwiftUI 中使用
struct ContentView: View {
    @State private var region = MKCoordinateRegion(
        center: CLLocationCoordinate2D(latitude: 39.9, longitude: 116.4),
        span: MKCoordinateSpan(latitudeDelta: 0.05, longitudeDelta: 0.05)
    )
    var body: some View {
        MapViewWrapper(region: $region)
            .frame(height: 300)
    }
}
```

## 3. UIViewControllerRepresentable

```swift
struct ImagePickerView: UIViewControllerRepresentable {
    @Binding var selectedImage: UIImage?
    @Environment(\.dismiss) var dismiss

    func makeUIViewController(context: Context) -> UIImagePickerController {
        let picker = UIImagePickerController()
        picker.delegate = context.coordinator
        picker.sourceType = .photoLibrary
        return picker
    }

    func updateUIViewController(_ uiViewController: UIImagePickerController, context: Context) {}

    func makeCoordinator() -> Coordinator { Coordinator(self) }

    class Coordinator: NSObject, UIImagePickerControllerDelegate, UINavigationControllerDelegate {
        let parent: ImagePickerView
        init(_ parent: ImagePickerView) { self.parent = parent }

        func imagePickerController(_ picker: UIImagePickerController,
                                   didFinishPickingMediaWithInfo info: [UIImagePickerController.InfoKey: Any]) {
            parent.selectedImage = info[.originalImage] as? UIImage
            parent.dismiss()
        }
    }
}
```

## 4. 数据共享（ObservableObject）

```swift
// 共享数据模型
class SharedViewModel: ObservableObject {
    @Published var count = 0
}

// UIKit 中使用
class CounterVC: UIViewController {
    let viewModel = SharedViewModel()
    private var cancellables = Set<AnyCancellable>()

    func setupBinding() {
        viewModel.$count
            .sink { [weak self] value in self?.label.text = "\(value)" }
            .store(in: &cancellables)
    }

    func showSwiftUIView() {
        let swiftUIView = CounterView(viewModel: viewModel)
        let hostingVC = UIHostingController(rootView: swiftUIView)
        present(hostingVC, animated: true)
    }
}

// SwiftUI 中使用同一个 ViewModel
struct CounterView: View {
    @ObservedObject var viewModel: SharedViewModel
    var body: some View {
        Button("计数: \(viewModel.count)") { viewModel.count += 1 }
    }
}
```

## 5. iOS 26 / Swift 6.2 互操作改进

> 🔄 更新于 2026-05-01

iOS 26 和 Swift 6.2 对 SwiftUI 与 UIKit 的互操作做了多项改进，降低了混合开发的摩擦。来源：[Apple Developer Documentation](https://developer.apple.com/documentation/swiftui/uikit-interoperability)、[Swift 6.2 Release Notes](https://www.swift.org/blog/swift-6.2-released)

<!-- version-check: SwiftUI iOS 26, Swift 6.2, Xcode 26.4, checked 2026-05-01 -->

### UIHostingController 改进

iOS 26 中 `UIHostingController` 的尺寸协商和生命周期管理更加自然：

```swift
// iOS 26：UIHostingController 自动适配 Safe Area
// 不再需要手动处理 additionalSafeAreaInsets
let hostingVC = UIHostingController(rootView: MySwiftUIView())

// 新增：sizingOptions 控制尺寸行为
hostingVC.sizingOptions = [.preferredContentSize]  // 自动更新 preferredContentSize
hostingVC.sizingOptions = [.intrinsicContentSize]   // 基于内容自适应

// 在 UIKit 容器中嵌入时更自然
addChild(hostingVC)
view.addSubview(hostingVC.view)
hostingVC.view.translatesAutoresizingMaskIntoConstraints = false
NSLayoutConstraint.activate([
    hostingVC.view.topAnchor.constraint(equalTo: view.safeAreaLayoutGuide.topAnchor),
    hostingVC.view.bottomAnchor.constraint(equalTo: view.safeAreaLayoutGuide.bottomAnchor),
    hostingVC.view.leadingAnchor.constraint(equalTo: view.leadingAnchor),
    hostingVC.view.trailingAnchor.constraint(equalTo: view.trailingAnchor)
])
hostingVC.didMove(toParent: self)
```

### @Observable 替代 ObservableObject

iOS 17+ 推荐使用 `@Observable` 宏替代 `ObservableObject`，在混合开发中同样适用：

```swift
// 2026 推荐：使用 @Observable（iOS 17+）
@Observable
class SharedModel {
    var count = 0
    var name = ""
}

// SwiftUI 中直接使用（无需 @ObservedObject）
struct CounterView: View {
    var model: SharedModel
    var body: some View {
        Button("计数: \(model.count)") { model.count += 1 }
    }
}

// UIKit 中使用 withObservationTracking
class CounterVC: UIViewController {
    let model = SharedModel()

    func setupObservation() {
        withObservationTracking {
            label.text = "\(model.count)"
        } onChange: {
            DispatchQueue.main.async { [weak self] in
                self?.setupObservation()  // 重新订阅
            }
        }
    }
}
```

### Liquid Glass 自动适配

iOS 26 的 Liquid Glass 设计语言对混合开发的影响：

```swift
// 使用 Xcode 26 重新编译后，UIKit 和 SwiftUI 组件自动获得 Liquid Glass 外观
// UINavigationBar、UITabBar、UIToolbar 自动应用新样式

// SwiftUI 中手动应用 Glass 效果
struct GlassCard: View {
    var body: some View {
        VStack {
            Text("Glass 效果卡片")
        }
        .padding()
        .glassEffect()  // iOS 26 新增
    }
}

// UIKit 中使用 Glass 效果
// UINavigationBar 和 UITabBar 自动应用
// 自定义视图需要使用 UIVisualEffectView 配合新的 Glass 材质
```

### 2026 年混合开发策略

```
你的项目情况？
├─ 全新项目 → 纯 SwiftUI（iOS 17+ 最低部署目标）
├─ 现有 UIKit 项目 → 新页面用 SwiftUI，UIHostingController 嵌入
├─ 复杂 UIKit 组件 → UIViewRepresentable 包装（地图、相机、WebView）
├─ iOS 26 原生 WebView → 不再需要 UIViewRepresentable 包装 WKWebView
└─ 数据共享 → @Observable（iOS 17+）或 ObservableObject（iOS 13+）
```
