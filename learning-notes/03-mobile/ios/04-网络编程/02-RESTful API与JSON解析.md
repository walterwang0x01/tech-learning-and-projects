# RESTful API 与 JSON 解析
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Codable 协议基础

```swift
// 同时支持编码和解码
struct User: Codable {
    let id: Int
    let name: String
    let email: String
    let avatarURL: URL?
    let isActive: Bool
}

// 仅解码（来自服务端的只读数据）
struct ServerStatus: Decodable {
    let version: String
    let uptime: TimeInterval
}

// 仅编码（发送到服务端的请求体）
struct CreatePostRequest: Encodable {
    let title: String
    let content: String
    let tags: [String]
}
```

## 2. JSONDecoder / JSONEncoder

```swift
// 解码 JSON -> Model
func decodeUser(from data: Data) throws -> User {
    let decoder = JSONDecoder()
    decoder.keyDecodingStrategy = .convertFromSnakeCase
    decoder.dateDecodingStrategy = .iso8601
    return try decoder.decode(User.self, from: data)
}

// 编码 Model -> JSON
func encodeUser(_ user: User) throws -> Data {
    let encoder = JSONEncoder()
    encoder.keyEncodingStrategy = .convertToSnakeCase
    encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    encoder.dateEncodingStrategy = .iso8601
    return try encoder.encode(user)
}
```

## 3. CodingKeys 自定义映射

```swift
struct Article: Codable {
    let id: Int
    let title: String
    let coverImage: URL
    let createdAt: Date
    let authorName: String

    enum CodingKeys: String, CodingKey {
        case id
        case title
        case coverImage = "cover_img"
        case createdAt = "created_at"
        case authorName = "author"
    }
}
```

## 4. 自定义编码与解码

```swift
struct Payment: Codable {
    let amount: Decimal
    let currency: String
    let status: Status

    enum Status: String, Codable {
        case pending, completed, failed
    }

    // 自定义解码：处理服务端返回字符串金额
    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        let amountString = try container.decode(String.self, forKey: .amount)
        guard let value = Decimal(string: amountString) else {
            throw DecodingError.dataCorruptedError(
                forKey: .amount, in: container,
                debugDescription: "无法将字符串转为 Decimal")
        }
        self.amount = value
        self.currency = try container.decode(String.self, forKey: .currency)
        self.status = try container.decode(Status.self, forKey: .status)
    }
}
```

## 5. 嵌套 JSON 处理

```swift
// 响应格式: { "code": 0, "data": { "user": { ... }, "token": "xxx" } }
struct APIResponse<T: Decodable>: Decodable {
    let code: Int
    let message: String?
    let data: T?
}

struct LoginResult: Decodable {
    let user: User
    let token: String
}

// 扁平化嵌套结构
struct Product: Decodable {
    let name: String
    let price: Decimal
    let categoryName: String

    enum CodingKeys: String, CodingKey {
        case name, price, category
    }
    enum CategoryKeys: String, CodingKey {
        case name
    }

    init(from decoder: Decoder) throws {
        let container = try decoder.container(keyedBy: CodingKeys.self)
        self.name = try container.decode(String.self, forKey: .name)
        self.price = try container.decode(Decimal.self, forKey: .price)
        let nested = try container.nestedContainer(keyedBy: CategoryKeys.self, forKey: .category)
        self.categoryName = try nested.decode(String.self, forKey: .name)
    }
}
```

## 6. 日期格式处理

```swift
let decoder = JSONDecoder()

// ISO 8601 标准格式
decoder.dateDecodingStrategy = .iso8601

// 时间戳（秒）
decoder.dateDecodingStrategy = .secondsSince1970

// 自定义格式
let formatter = DateFormatter()
formatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
formatter.locale = Locale(identifier: "en_US_POSIX")
decoder.dateDecodingStrategy = .formatted(formatter)

// 多种日期格式兼容
decoder.dateDecodingStrategy = .custom { decoder in
    let container = try decoder.singleValueContainer()
    let dateString = try container.decode(String.self)

    let iso = ISO8601DateFormatter()
    if let date = iso.date(from: dateString) { return date }

    let custom = DateFormatter()
    custom.dateFormat = "yyyy-MM-dd"
    if let date = custom.date(from: dateString) { return date }

    throw DecodingError.dataCorruptedError(
        in: container, debugDescription: "无法解析日期: \(dateString)")
}
```

## 7. 错误处理

```swift
func fetchArticle(id: Int) async throws -> Article {
    let url = URL(string: "https://api.example.com/articles/\(id)")!
    let (data, response) = try await URLSession.shared.data(from: url)

    guard let httpResponse = response as? HTTPURLResponse else {
        throw NetworkError.invalidResponse
    }

    switch httpResponse.statusCode {
    case 200:
        do {
            let wrapper = try JSONDecoder().decode(APIResponse<Article>.self, from: data)
            guard let article = wrapper.data else {
                throw NetworkError.emptyData
            }
            return article
        } catch let error as DecodingError {
            switch error {
            case .keyNotFound(let key, _):
                print("缺少字段: \(key.stringValue)")
            case .typeMismatch(let type, let context):
                print("类型不匹配: 期望 \(type), 路径: \(context.codingPath)")
            case .valueNotFound(_, let context):
                print("值为空: \(context.codingPath)")
            default:
                print("解码错误: \(error.localizedDescription)")
            }
            throw NetworkError.decodingFailed(error)
        }
    case 401: throw NetworkError.unauthorized
    case 404: throw NetworkError.notFound
    default:  throw NetworkError.serverError(httpResponse.statusCode)
    }
}

enum NetworkError: Error {
    case invalidResponse, emptyData, unauthorized, notFound
    case serverError(Int)
    case decodingFailed(Error)
}
```
