# UIKit 导航与页面跳转
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. UINavigationController

```swift
// AppDelegate / SceneDelegate 中设置
let rootVC = HomeViewController()
let nav = UINavigationController(rootViewController: rootVC)
window?.rootViewController = nav

// Push / Pop
navigationController?.pushViewController(detailVC, animated: true)
navigationController?.popViewController(animated: true)
navigationController?.popToRootViewController(animated: true)

// 自定义导航栏
navigationItem.title = "首页"
navigationItem.rightBarButtonItem = UIBarButtonItem(
    image: UIImage(systemName: "plus"),
    style: .plain,
    target: self,
    action: #selector(addTapped)
)

// 大标题
navigationController?.navigationBar.prefersLargeTitles = true
navigationItem.largeTitleDisplayMode = .always
```

## 2. UITabBarController

```swift
class MainTabBarController: UITabBarController {
    override func viewDidLoad() {
        super.viewDidLoad()

        let homeNav = UINavigationController(rootViewController: HomeVC())
        homeNav.tabBarItem = UITabBarItem(title: "首页", image: UIImage(systemName: "house"), tag: 0)

        let profileNav = UINavigationController(rootViewController: ProfileVC())
        profileNav.tabBarItem = UITabBarItem(title: "我的", image: UIImage(systemName: "person"), tag: 1)

        viewControllers = [homeNav, profileNav]
        tabBar.tintColor = .systemBlue
    }
}
```

> 更新于 2026-07-10

<!-- version-check: UITabBarController sidebar API + UIBarMinimizeBehavior (WWDC26, 2027 releases), checked 2026-07-10 -->

**WWDC26 新增**：`UITabBarController` 支持在合适场景（横屏、外接显示器、iPad）自动切换为侧边栏形式，无需维护两套控件：

```swift
// 让 Tab Bar 在空间充足时自动切换为 Sidebar 形式
tabBarController.sidebar.preferredPlacement = .automatic
```

配套的导航栏收起行为，让导航栏在滚动时可以滑出（呼应 SwiftUI 的 `toolbarMinimizeBehavior`）：

```swift
navigationController?.navigationBar.barMinimizationBehavior = .automatic  // UIBarMinimizeBehavior
```

来源：[What's New in UIKit in iOS 27 - Kyle Howells](https://ikyle.me/blog/2026/whats-new-in-uikit-ios-27)

## 3. Present / Dismiss

```swift
// 模态弹出
let settingsVC = SettingsViewController()
settingsVC.modalPresentationStyle = .pageSheet  // .fullScreen, .formSheet
settingsVC.modalTransitionStyle = .coverVertical
present(settingsVC, animated: true)

// 关闭
dismiss(animated: true)

// Sheet 半屏（iOS 15+）
if let sheet = settingsVC.sheetPresentationController {
    sheet.detents = [.medium(), .large()]
    sheet.prefersGrabberVisible = true
}
present(settingsVC, animated: true)
```

## 4. 页面传值

```swift
// 正向传值：属性赋值
let detailVC = DetailViewController()
detailVC.userId = selectedUser.id
navigationController?.pushViewController(detailVC, animated: true)

// 反向传值：Delegate
protocol DetailDelegate: AnyObject {
    func detailDidUpdate(_ data: String)
}

class DetailViewController: UIViewController {
    weak var delegate: DetailDelegate?

    func save() {
        delegate?.detailDidUpdate("新数据")
        navigationController?.popViewController(animated: true)
    }
}

// 反向传值：闭包
class DetailViewController: UIViewController {
    var onComplete: ((String) -> Void)?

    func save() {
        onComplete?("新数据")
        dismiss(animated: true)
    }
}
```

## 5. Coordinator 模式

```swift
protocol Coordinator: AnyObject {
    var childCoordinators: [Coordinator] { get set }
    var navigationController: UINavigationController { get set }
    func start()
}

class AppCoordinator: Coordinator {
    var childCoordinators: [Coordinator] = []
    var navigationController: UINavigationController

    init(navigationController: UINavigationController) {
        self.navigationController = navigationController
    }

    func start() {
        let homeVC = HomeViewController()
        homeVC.coordinator = self
        navigationController.pushViewController(homeVC, animated: false)
    }

    func showDetail(for user: User) {
        let detailVC = DetailViewController()
        detailVC.user = user
        navigationController.pushViewController(detailVC, animated: true)
    }

    func showLogin() {
        let loginCoordinator = LoginCoordinator(navigationController: navigationController)
        childCoordinators.append(loginCoordinator)
        loginCoordinator.start()
    }
}
```
