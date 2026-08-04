# WebSocket 与实时通信
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. URLSessionWebSocketTask 基础

```swift
class WebSocketManager {
    private var webSocketTask: URLSessionWebSocketTask?
    private let session = URLSession(configuration: .default)

    func connect() {
        let url = URL(string: "wss://echo.websocket.org")!
        webSocketTask = session.webSocketTask(with: url)
        webSocketTask?.resume()
        receiveMessage()
    }

    func disconnect() {
        webSocketTask?.cancel(with: .goingAway, reason: nil)
    }
}
```

## 2. 发送消息

```swift
extension WebSocketManager {
    func sendText(_ text: String) {
        let message = URLSessionWebSocketTask.Message.string(text)
        webSocketTask?.send(message) { error in
            if let error = error {
                print("发送失败: \(error)")
            }
        }
    }

    func sendJSON<T: Encodable>(_ object: T) {
        guard let data = try? JSONEncoder().encode(object) else { return }
        let message = URLSessionWebSocketTask.Message.data(data)
        webSocketTask?.send(message) { error in
            if let error = error { print("发送失败: \(error)") }
        }
    }
}
```

## 3. 接收消息

```swift
extension WebSocketManager {
    func receiveMessage() {
        webSocketTask?.receive { [weak self] result in
            switch result {
            case .success(let message):
                switch message {
                case .string(let text):
                    print("收到文本: \(text)")
                case .data(let data):
                    print("收到数据: \(data.count) bytes")
                @unknown default:
                    break
                }
                self?.receiveMessage()  // 继续监听
            case .failure(let error):
                print("接收失败: \(error)")
            }
        }
    }
}
```

## 4. 心跳保活

```swift
class WebSocketManager {
    private var pingTimer: Timer?

    func startPing() {
        pingTimer = Timer.scheduledTimer(withTimeInterval: 30, repeats: true) { [weak self] _ in
            self?.webSocketTask?.sendPing { error in
                if let error = error {
                    print("Ping 失败: \(error)")
                    self?.reconnect()
                }
            }
        }
    }

    func stopPing() {
        pingTimer?.invalidate()
        pingTimer = nil
    }
}
```

## 5. 自动重连机制

```swift
class WebSocketManager {
    private var retryCount = 0
    private let maxRetries = 5

    func reconnect() {
        guard retryCount < maxRetries else {
            print("达到最大重连次数")
            return
        }
        retryCount += 1
        let delay = Double(min(retryCount * 2, 30))  // 指数退避，最大30秒
        DispatchQueue.main.asyncAfter(deadline: .now() + delay) { [weak self] in
            print("第 \(self?.retryCount ?? 0) 次重连...")
            self?.connect()
        }
    }

    func onConnected() {
        retryCount = 0
        startPing()
    }
}
```

## 6. 聊天室示例

```swift
struct ChatMessage: Codable {
    let type: String      // "message", "join", "leave"
    let userId: String
    let content: String
    let timestamp: Date
}

class ChatService: ObservableObject {
    @Published var messages: [ChatMessage] = []
    private let ws = WebSocketManager()

    func joinRoom(_ roomId: String) {
        ws.connect()
        ws.sendJSON(["type": "join", "roomId": roomId])
    }

    func sendMessage(_ content: String) {
        let msg = ChatMessage(type: "message", userId: "me",
                              content: content, timestamp: Date())
        ws.sendJSON(msg)
        messages.append(msg)
    }
}
```
