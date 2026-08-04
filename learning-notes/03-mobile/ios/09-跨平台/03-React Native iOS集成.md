# React Native iOS 集成
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 集成到现有 iOS 项目

```ruby
# Podfile
require_relative '../node_modules/react-native/scripts/react_native_pods'

platform :ios, '16.0'

target 'MyApp' do
  config = use_native_modules!
  use_react_native!(path: '../node_modules/react-native')
end
```

```bash
# 安装依赖
cd ios && pod install
```

## 2. 加载 RN 页面

```swift
import React

class RNViewController: UIViewController {
    override func viewDidLoad() {
        super.viewDidLoad()

        let jsCodeLocation = URL(string: "http://localhost:8081/index.bundle?platform=ios")!

        let rootView = RCTRootView(
            bundleURL: jsCodeLocation,
            moduleName: "MyRNModule",
            initialProperties: ["userId": "123"],
            launchOptions: nil
        )
        view = rootView
    }
}

// 跳转到 RN 页面
func openRNPage() {
    let rnVC = RNViewController()
    navigationController?.pushViewController(rnVC, animated: true)
}
```

## 3. Native Module（原生模块）

```swift
import React

@objc(DeviceInfoModule)
class DeviceInfoModule: NSObject {

    @objc static func requiresMainQueueSetup() -> Bool { return false }

    @objc func getDeviceInfo(_ resolve: @escaping RCTPromiseResolveBlock,
                              rejecter reject: @escaping RCTPromiseRejectBlock) {
        let info: [String: Any] = [
            "model": UIDevice.current.model,
            "systemVersion": UIDevice.current.systemVersion,
            "name": UIDevice.current.name
        ]
        resolve(info)
    }

    @objc func showNativeAlert(_ title: String, message: String) {
        DispatchQueue.main.async {
            let alert = UIAlertController(title: title, message: message, preferredStyle: .alert)
            alert.addAction(UIAlertAction(title: "OK", style: .default))
            UIApplication.shared.keyWindow?.rootViewController?.present(alert, animated: true)
        }
    }
}
```

```objc
// DeviceInfoModule.m（桥接文件）
#import <React/RCTBridgeModule.h>

@interface RCT_EXTERN_MODULE(DeviceInfoModule, NSObject)
RCT_EXTERN_METHOD(getDeviceInfo:(RCTPromiseResolveBlock)resolve
                  rejecter:(RCTPromiseRejectBlock)reject)
RCT_EXTERN_METHOD(showNativeAlert:(NSString *)title message:(NSString *)message)
@end
```

```javascript
// JavaScript 端调用
import { NativeModules } from 'react-native';
const { DeviceInfoModule } = NativeModules;

const info = await DeviceInfoModule.getDeviceInfo();
console.log(info.model);

DeviceInfoModule.showNativeAlert('提示', '来自 RN 的消息');
```

## 4. Native 事件发送

```swift
@objc(EventEmitterModule)
class EventEmitterModule: RCTEventEmitter {
    override func supportedEvents() -> [String]! {
        return ["onLocationUpdate", "onNetworkChange"]
    }

    override static func requiresMainQueueSetup() -> Bool { return true }

    func sendLocationUpdate(lat: Double, lng: Double) {
        sendEvent(withName: "onLocationUpdate", body: ["lat": lat, "lng": lng])
    }
}
```

```javascript
// JavaScript 端监听
import { NativeEventEmitter, NativeModules } from 'react-native';

const emitter = new NativeEventEmitter(NativeModules.EventEmitterModule);
const subscription = emitter.addListener('onLocationUpdate', (event) => {
  console.log(`位置: ${event.lat}, ${event.lng}`);
});

// 清理
subscription.remove();
```

## 5. Turbo Module（新架构）

```swift
// 新架构使用 Turbo Module 替代 Bridge Module
// 优势：JSI 直接调用，无需序列化，性能更好

@objc(NativeDeviceInfo)
class NativeDeviceInfo: NSObject {
    @objc func getModel() -> String {
        return UIDevice.current.model
    }

    @objc func getSystemVersion() -> String {
        return UIDevice.current.systemVersion
    }
}
```

## 6. React Native 0.79 新架构与 iOS 集成

> 🔄 更新于 2026-05-01

React Native 0.79 是当前稳定版（2026-04），新架构（Fabric + TurboModules）已成为默认。来源：[React Native Blog](https://reactnative.dev/blog)、[React Native Releases](https://github.com/facebook/react-native/releases)

<!-- version-check: React Native 0.79.x, New Architecture default, checked 2026-05-01 -->

### 新架构核心变化

| 特性 | 旧架构（Bridge） | 新架构（Fabric + TurboModules） |
|------|-----------------|-------------------------------|
| JS ↔ Native 通信 | JSON 序列化 Bridge | JSI 直接调用 |
| UI 渲染 | 异步 Bridge | Fabric 同步渲染 |
| 原生模块 | Bridge Module | TurboModule（懒加载） |
| 并发 | 单线程 Bridge | 多线程支持 |
| 类型安全 | 运行时检查 | Codegen 编译时检查 |

### TurboModule 完整示例（Swift）

```swift
// 1. 定义 Spec（TypeScript → Codegen 生成 ObjC++ 接口）
// NativeDeviceInfo.ts
import type { TurboModule } from 'react-native';
import { TurboModuleRegistry } from 'react-native';

export interface Spec extends TurboModule {
  getModel(): string;
  getSystemVersion(): string;
  getBatteryLevel(): Promise<number>;
}

export default TurboModuleRegistry.getEnforcing<Spec>('DeviceInfo');
```

```swift
// 2. Swift 实现（RCTDeviceInfoSpec 由 Codegen 生成）
@objc(DeviceInfo)
class DeviceInfo: NSObject, NativeDeviceInfoSpec {
    @objc static func moduleName() -> String! { "DeviceInfo" }

    func getModel() -> String {
        UIDevice.current.model
    }

    func getSystemVersion() -> String {
        UIDevice.current.systemVersion
    }

    func getBatteryLevel(_ resolve: @escaping RCTPromiseResolveBlock,
                         reject: @escaping RCTPromiseRejectBlock) {
        UIDevice.current.isBatteryMonitoringEnabled = true
        resolve(UIDevice.current.batteryLevel * 100)
    }
}
```

### React Native 0.79 iOS 关键改进

- **最低 iOS 版本提升至 16.0**：与 Apple 生态保持一致
- **Hermes 引擎默认启用**：启动速度提升 30-50%
- **Codegen 自动生成**：TypeScript 定义自动生成 ObjC++ 接口
- **Swift 原生模块支持改善**：不再强制需要 ObjC 桥接文件

### 版本选择建议

```
你的项目情况？
├─ 新项目 → RN 0.79 + 新架构（默认）
├─ 现有旧架构项目 → 逐步迁移，先升级到 0.76+
├─ 大量 Bridge Module → 使用 interop layer 过渡
└─ 需要 iOS 15 支持 → 停留在 RN 0.77.x
```
