# UserDefaults 与 Keychain
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. UserDefaults 基础

```swift
let defaults = UserDefaults.standard

// 存储
defaults.set("张三", forKey: "username")
defaults.set(25, forKey: "age")
defaults.set(true, forKey: "isLoggedIn")
defaults.set(["Swift", "iOS"], forKey: "skills")

// 读取
let name = defaults.string(forKey: "username") ?? "未知"
let age = defaults.integer(forKey: "age")
let isLoggedIn = defaults.bool(forKey: "isLoggedIn")

// 删除
defaults.removeObject(forKey: "username")

// 存储自定义对象（需要 Codable）
struct UserSettings: Codable {
    var theme: String
    var fontSize: Int
}

func saveSettings(_ settings: UserSettings) {
    if let data = try? JSONEncoder().encode(settings) {
        defaults.set(data, forKey: "settings")
    }
}

func loadSettings() -> UserSettings? {
    guard let data = defaults.data(forKey: "settings") else { return nil }
    return try? JSONDecoder().decode(UserSettings.self, from: data)
}
```

## 2. @AppStorage（SwiftUI）

```swift
import SwiftUI

struct SettingsView: View {
    @AppStorage("username") var username = "默认用户"
    @AppStorage("isDarkMode") var isDarkMode = false
    @AppStorage("fontSize") var fontSize = 14.0

    var body: some View {
        Form {
            TextField("用户名", text: $username)
            Toggle("深色模式", isOn: $isDarkMode)
            Slider(value: $fontSize, in: 12...24, step: 1) {
                Text("字体大小: \(Int(fontSize))")
            }
        }
    }
}
```

## 3. PropertyWrapper 封装

```swift
@propertyWrapper
struct UserDefault<T> {
    let key: String
    let defaultValue: T

    var wrappedValue: T {
        get { UserDefaults.standard.object(forKey: key) as? T ?? defaultValue }
        set { UserDefaults.standard.set(newValue, forKey: key) }
    }
}

class AppSettings {
    @UserDefault(key: "hasLaunched", defaultValue: false)
    static var hasLaunched: Bool

    @UserDefault(key: "selectedTab", defaultValue: 0)
    static var selectedTab: Int
}
```

## 4. Keychain 安全存储

```swift
import Security

class KeychainHelper {
    static let shared = KeychainHelper()

    func save(_ data: Data, forKey key: String) -> Bool {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecValueData as String: data
        ]
        SecItemDelete(query as CFDictionary)  // 先删除旧值
        let status = SecItemAdd(query as CFDictionary, nil)
        return status == errSecSuccess
    }

    func read(forKey key: String) -> Data? {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key,
            kSecReturnData as String: true,
            kSecMatchLimit as String: kSecMatchLimitOne
        ]
        var result: AnyObject?
        SecItemCopyMatching(query as CFDictionary, &result)
        return result as? Data
    }

    func delete(forKey key: String) {
        let query: [String: Any] = [
            kSecClass as String: kSecClassGenericPassword,
            kSecAttrAccount as String: key
        ]
        SecItemDelete(query as CFDictionary)
    }
}

// 使用
let token = "abc123".data(using: .utf8)!
KeychainHelper.shared.save(token, forKey: "authToken")

if let data = KeychainHelper.shared.read(forKey: "authToken"),
   let token = String(data: data, encoding: .utf8) {
    print("Token: \(token)")
}
```
