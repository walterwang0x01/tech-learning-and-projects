# WebSocket 与 gRPC
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. OkHttp WebSocket 客户端

```kotlin
class ChatWebSocket(private val client: OkHttpClient) {

    private var webSocket: WebSocket? = null

    fun connect(url: String) {
        val request = Request.Builder().url(url)
            .addHeader("Authorization", "Bearer $token")
            .build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                Log.d("WS", "连接已建立")
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                val message = Json.decodeFromString<ChatMessage>(text)
                handleMessage(message)
            }

            override fun onMessage(webSocket: WebSocket, bytes: ByteString) {
                // 处理二进制消息
            }

            override fun onClosing(webSocket: WebSocket, code: Int, reason: String) {
                webSocket.close(1000, null)
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Log.e("WS", "连接失败: ${t.message}")
                reconnect(url)
            }
        })
    }

    fun sendMessage(text: String) {
        webSocket?.send(text)
    }

    fun disconnect() {
        webSocket?.close(1000, "客户端主动关闭")
    }
}
```

## 2. Scarlet WebSocket 框架

```kotlin
// 定义 WebSocket 服务接口
interface ChatService {
    @Receive
    fun observeMessages(): Flow<ChatMessage>

    @Receive
    fun observeState(): Flow<WebSocket.Event>

    @Send
    fun sendMessage(message: ChatMessage): Boolean
}

// 配置 Scarlet 实例
@Provides @Singleton
fun provideChatService(client: OkHttpClient): ChatService {
    val scarlet = Scarlet.Builder()
        .webSocketFactory(client.newWebSocketFactory("wss://chat.example.com/ws"))
        .addMessageAdapterFactory(MoshiMessageAdapter.Factory())
        .addStreamAdapterFactory(FlowStreamAdapter.Factory)
        .lifecycle(AndroidLifecycle.ofApplicationForeground(application))
        .backoffStrategy(ExponentialBackoffStrategy(1000, maxDuration = 30000))
        .build()
    return scarlet.create(ChatService::class.java)
}

// 在 ViewModel 中使用
@HiltViewModel
class ChatViewModel @Inject constructor(
    private val chatService: ChatService
) : ViewModel() {

    val messages = chatService.observeMessages()
        .catch { e -> Log.e("Chat", "消息流异常: ${e.message}") }
        .stateIn(viewModelScope, SharingStarted.Lazily, emptyList())

    fun send(text: String) {
        chatService.sendMessage(
            ChatMessage(content = text, timestamp = System.currentTimeMillis())
        )
    }
}
```

## 3. gRPC — Protobuf 定义

```protobuf
syntax = "proto3";
package com.example.chat;

option java_multiple_files = true;

service ChatService {
    // 一元调用
    rpc SendMessage(ChatRequest) returns (ChatResponse);
    // 服务端流
    rpc SubscribeMessages(SubscribeRequest) returns (stream ChatEvent);
    // 双向流
    rpc BiChat(stream ChatRequest) returns (stream ChatEvent);
}

message ChatRequest {
    string room_id = 1;
    string content = 2;
    int64 timestamp = 3;
}

message ChatResponse {
    string message_id = 1;
    bool success = 2;
}

message SubscribeRequest {
    string room_id = 1;
}

message ChatEvent {
    string sender = 1;
    string content = 2;
    int64 timestamp = 3;
}
```

## 4. gRPC-Kotlin Stub 使用

```kotlin
// build.gradle.kts 配置 protobuf 插件生成 Stub 后使用
class GrpcChatRepository(private val channel: ManagedChannel) {

    private val stub = ChatServiceGrpcKt.ChatServiceCoroutineStub(channel)

    // 一元调用
    suspend fun sendMessage(roomId: String, content: String): ChatResponse {
        val request = chatRequest {
            this.roomId = roomId
            this.content = content
            this.timestamp = System.currentTimeMillis()
        }
        return stub.sendMessage(request)
    }

    // 服务端流式接收
    fun subscribeMessages(roomId: String): Flow<ChatEvent> {
        val request = subscribeRequest { this.roomId = roomId }
        return stub.subscribeMessages(request)
    }
}
```

## 5. 双向流式通信

```kotlin
fun biChat(outgoing: Flow<ChatRequest>): Flow<ChatEvent> {
    return stub.biChat(outgoing)
}

// 在 ViewModel 中使用双向流
class LiveChatViewModel @Inject constructor(
    private val repo: GrpcChatRepository
) : ViewModel() {

    private val _outgoing = MutableSharedFlow<ChatRequest>()

    val incomingMessages: Flow<ChatEvent> = repo.biChat(_outgoing)
        .catch { e ->
            when (e) {
                is StatusException -> Log.e("gRPC", "状态异常: ${e.status}")
                else -> Log.e("gRPC", "流异常: ${e.message}")
            }
        }

    fun send(roomId: String, text: String) {
        viewModelScope.launch {
            _outgoing.emit(chatRequest {
                this.roomId = roomId
                content = text
                timestamp = System.currentTimeMillis()
            })
        }
    }
}
```

## 6. gRPC Channel 配置

```kotlin
@Provides @Singleton
fun provideManagedChannel(): ManagedChannel =
    ManagedChannelBuilder.forAddress("grpc.example.com", 443)
        .useTransportSecurity()
        .keepAliveTime(30, TimeUnit.SECONDS)
        .keepAliveTimeout(10, TimeUnit.SECONDS)
        .idleTimeout(5, TimeUnit.MINUTES)
        .intercept(object : ClientInterceptor {
            override fun <Req, Resp> interceptCall(
                method: MethodDescriptor<Req, Resp>,
                callOptions: CallOptions,
                next: Channel
            ): ClientCall<Req, Resp> {
                val newOptions = callOptions.withDeadlineAfter(15, TimeUnit.SECONDS)
                return next.newCall(method, newOptions)
            }
        })
        .build()
```
