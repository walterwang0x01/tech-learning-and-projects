# URLSession 与网络请求
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 基础 GET 请求

```swift
func fetchUsers() async throws -> [User] {
    let url = URL(string: "https://api.example.com/users")!
    let (data, response) = try await URLSession.shared.data(from: url)

    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw NetworkError.invalidResponse
    }
    return try JSONDecoder().decode([User].self, from: data)
}
```

## 2. POST 请求

```swift
func createUser(_ user: CreateUserRequest) async throws -> User {
    var request = URLRequest(url: URL(string: "https://api.example.com/users")!)
    request.httpMethod = "POST"
    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
    request.setValue("Bearer \(token)", forHTTPHeaderField: "Authorization")
    request.httpBody = try JSONEncoder().encode(user)
    request.timeoutInterval = 30

    let (data, _) = try await URLSession.shared.data(for: request)
    return try JSONDecoder().decode(User.self, from: data)
}
```

## 3. 下载任务

```swift
func downloadFile(from url: URL) async throws -> URL {
    let (localURL, response) = try await URLSession.shared.download(from: url)

    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw NetworkError.downloadFailed
    }

    // 移动到 Documents 目录
    let docsURL = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask).first!
    let destURL = docsURL.appendingPathComponent(url.lastPathComponent)
    try FileManager.default.moveItem(at: localURL, to: destURL)
    return destURL
}

// 带进度的下载
class DownloadManager: NSObject, URLSessionDownloadDelegate {
    func startDownload(url: URL) {
        let session = URLSession(configuration: .default, delegate: self, delegateQueue: nil)
        session.downloadTask(with: url).resume()
    }

    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask,
                    didWriteData bytesWritten: Int64, totalBytesWritten: Int64,
                    totalBytesExpectedToWrite: Int64) {
        let progress = Double(totalBytesWritten) / Double(totalBytesExpectedToWrite)
        DispatchQueue.main.async { self.updateProgress(progress) }
    }

    func urlSession(_ session: URLSession, downloadTask: URLSessionDownloadTask,
                    didFinishDownloadingTo location: URL) {
        // 处理下载完成
    }
}
```

## 4. 上传任务

```swift
func uploadImage(_ image: UIImage) async throws {
    let url = URL(string: "https://api.example.com/upload")!
    var request = URLRequest(url: url)
    request.httpMethod = "POST"

    let boundary = UUID().uuidString
    request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

    var body = Data()
    body.append("--\(boundary)\r\n".data(using: .utf8)!)
    body.append("Content-Disposition: form-data; name=\"file\"; filename=\"photo.jpg\"\r\n".data(using: .utf8)!)
    body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
    body.append(image.jpegData(compressionQuality: 0.8)!)
    body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)

    let (_, response) = try await URLSession.shared.upload(for: request, from: body)
    guard (response as? HTTPURLResponse)?.statusCode == 200 else {
        throw NetworkError.uploadFailed
    }
}
```

## 5. URLSession 配置

```swift
// 自定义配置
let config = URLSessionConfiguration.default
config.timeoutIntervalForRequest = 30
config.waitsForConnectivity = true
config.httpAdditionalHeaders = ["Accept": "application/json"]

let session = URLSession(configuration: config)

// 后台下载配置
let bgConfig = URLSessionConfiguration.background(withIdentifier: "com.app.download")
bgConfig.isDiscretionary = true
bgConfig.sessionSendsLaunchEvents = true
```

## 6. Certificate Pinning

```swift
class PinnedSessionDelegate: NSObject, URLSessionDelegate {
    func urlSession(_ session: URLSession, didReceive challenge: URLAuthenticationChallenge,
                    completionHandler: @escaping (URLSession.AuthChallengeDisposition, URLCredential?) -> Void) {
        guard let serverTrust = challenge.protectionSpace.serverTrust,
              let certificate = SecTrustGetCertificateAtIndex(serverTrust, 0) else {
            completionHandler(.cancelAuthenticationChallenge, nil)
            return
        }
        let serverCertData = SecCertificateCopyData(certificate) as Data
        let localCertData = NSData(contentsOfFile: Bundle.main.path(forResource: "cert", ofType: "cer")!)! as Data

        if serverCertData == localCertData {
            completionHandler(.useCredential, URLCredential(trust: serverTrust))
        } else {
            completionHandler(.cancelAuthenticationChallenge, nil)
        }
    }
}
```

## 7. iOS 26 / Swift 6.2 网络编程更新

<!-- version-check: URLSession iOS 26 (Swift 6.2), HTTP/3 auto, checked 2026-05-04 -->

> 🔄 更新于 2026-04-23

### 结构化并发与 URLSession

Swift 6.2 的 Approachable Concurrency 改变了网络编程的默认行为。新代码默认在 MainActor 上执行，网络请求需要显式标注 `@concurrent`：

```swift
// Swift 6.2 推荐写法：显式并发的网络层
@concurrent
func fetchUsers() async throws -> [User] {
    let url = URL(string: "https://api.example.com/users")!
    let (data, response) = try await URLSession.shared.data(from: url)

    guard let httpResponse = response as? HTTPURLResponse,
          httpResponse.statusCode == 200 else {
        throw NetworkError.invalidResponse
    }
    return try JSONDecoder().decode([User].self, from: data)
}

// ViewModel 中调用（默认 MainActor，无需 DispatchQueue.main.async）
@Observable
class UserListViewModel {
    var users: [User] = []
    var isLoading = false

    func loadUsers() async {
        isLoading = true
        defer { isLoading = false }
        do {
            // fetchUsers 标记了 @concurrent，会在后台执行
            // 返回后自动回到 MainActor 更新 UI
            users = try await fetchUsers()
        } catch {
            print("加载失败: \(error)")
        }
    }
}
```

### HTTP/3 自动升级

iOS 26 中 URLSession 会自动尝试 HTTP/3（QUIC），无需额外配置。对于需要强制 HTTP/2 的场景：

```swift
let config = URLSessionConfiguration.default
config.multipathServiceType = .handover // 多路径 TCP
// HTTP/3 默认启用，URLSession 自动协商最佳协议
```

### 2026 年 iOS 网络层推荐架构

```
推荐方案（按项目规模）：
├── 小型项目 → URLSession + async/await（原生，零依赖）
├── 中型项目 → URLSession + 自定义 NetworkClient 封装
└── 大型项目 → Alamofire 6.x（拦截器、重试、认证刷新）

关键原则：
- 使用 @concurrent 标注网络函数
- 使用 @Observable 替代 ObservableObject
- 优先 async/await，避免 Combine 做网络请求
- Certificate Pinning 用于金融/医疗等安全敏感场景
```

来源：[Swift 6.2 Released](https://www.swift.org/blog/swift-6.2-released/) | [iOS 26 Release Notes](https://support.apple.com/en-us/123075)
