# gRPC 与 Protobuf

> Author: Walter Wang

<!-- version-check: google.golang.org/grpc 1.76.0, protoc-gen-go (protobuf-go) 1.36.1, Buf 1.52.1, checked 2026-05-30 -->

## 1. 为什么微服务用 gRPC

```
REST vs gRPC：
                         REST        gRPC
格式                     JSON         Protobuf 二进制
协议                     HTTP/1.1     HTTP/2
类型安全                  无           编译期强类型
代码生成                  无           自动生成
流式                     弱           双向流原生
延迟                     中           低（二进制+复用连接）
人类可读                  好           差（二进制）
浏览器直接调用             ✅           ❌（需 grpc-web / Connect）

用 REST：
├─ 面向浏览器 / 第三方
├─ 简单 CRUD
└─ 公开 API

用 gRPC：
├─ 内部微服务
├─ 流式 / 长连接
├─ 多语言栈
└─ 严格的 API 契约
```

## 2. Protobuf 定义

```proto
// proto/user/v1/user.proto
syntax = "proto3";

package user.v1;
option go_package = "myorg/gen/user/v1;userv1";

import "google/protobuf/timestamp.proto";

service UserService {
  rpc GetUser(GetUserRequest) returns (GetUserResponse);
  rpc ListUsers(ListUsersRequest) returns (ListUsersResponse);
  rpc CreateUser(CreateUserRequest) returns (CreateUserResponse);

  // 服务端流
  rpc WatchUsers(WatchUsersRequest) returns (stream User);

  // 客户端流
  rpc UploadAvatar(stream UploadAvatarRequest) returns (UploadAvatarResponse);

  // 双向流
  rpc Chat(stream ChatMessage) returns (stream ChatMessage);
}

message User {
  int64 id = 1;
  string name = 2;
  string email = 3;
  google.protobuf.Timestamp created_at = 4;
}

message GetUserRequest {
  int64 id = 1;
}

message GetUserResponse {
  User user = 1;
}

message ListUsersRequest {
  int32 page_size = 1;
  string page_token = 2;
}

message ListUsersResponse {
  repeated User users = 1;
  string next_page_token = 2;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

message CreateUserResponse {
  User user = 1;
}
```

## 3. Buf：现代 Protobuf 工具链

```bash
# 安装
go install github.com/bufbuild/buf/cmd/buf@latest

# buf.yaml
version: v2
lint:
  use: [DEFAULT]
breaking:
  use: [FILE]

# buf.gen.yaml
version: v2
plugins:
  - remote: buf.build/protocolbuffers/go
    out: gen
    opt: paths=source_relative
  - remote: buf.build/grpc/go
    out: gen
    opt:
      - paths=source_relative
      - require_unimplemented_servers=false
```

```bash
# 工作流
buf lint                # 代码规范检查
buf breaking            # 破坏性变更检查（对比 main 分支）
buf generate            # 生成代码
buf dep update          # 依赖管理
```

Buf 替代了 `protoc + 一堆插件 + Makefile` 的传统方案，是 2026 年 Protobuf 开发的标准工具链。

## 4. 服务端实现

```go
package main

import (
    "context"
    "log/slog"
    "net"

    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/reflection"
    "google.golang.org/grpc/status"

    userv1 "myorg/gen/user/v1"
)

type UserServer struct {
    userv1.UnimplementedUserServiceServer
    repo UserRepo
}

func (s *UserServer) GetUser(ctx context.Context, req *userv1.GetUserRequest) (*userv1.GetUserResponse, error) {
    if req.Id <= 0 {
        return nil, status.Error(codes.InvalidArgument, "id must be positive")
    }

    user, err := s.repo.Find(ctx, req.Id)
    if err != nil {
        if errors.Is(err, ErrNotFound) {
            return nil, status.Errorf(codes.NotFound, "user %d not found", req.Id)
        }
        return nil, status.Error(codes.Internal, "internal error")
    }

    return &userv1.GetUserResponse{
        User: &userv1.User{
            Id:        user.ID,
            Name:      user.Name,
            Email:     user.Email,
            CreatedAt: timestamppb.New(user.CreatedAt),
        },
    }, nil
}

func (s *UserServer) WatchUsers(req *userv1.WatchUsersRequest, stream userv1.UserService_WatchUsersServer) error {
    ctx := stream.Context()
    events := s.repo.Subscribe(ctx)

    for {
        select {
        case <-ctx.Done():
            return ctx.Err()
        case user := <-events:
            if err := stream.Send(user); err != nil {
                return err
            }
        }
    }
}

func main() {
    lis, _ := net.Listen("tcp", ":50051")

    grpcServer := grpc.NewServer(
        grpc.ChainUnaryInterceptor(
            loggingInterceptor,
            recoveryInterceptor,
            authInterceptor,
        ),
    )

    userv1.RegisterUserServiceServer(grpcServer, &UserServer{repo: repo})

    // 反射 API（grpcurl 用）
    reflection.Register(grpcServer)

    slog.Info("gRPC listening", "addr", ":50051")
    grpcServer.Serve(lis)
}
```

## 5. 客户端调用

```go
import (
    "context"
    "time"

    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"

    userv1 "myorg/gen/user/v1"
)

func main() {
    conn, err := grpc.NewClient(
        "localhost:50051",
        grpc.WithTransportCredentials(insecure.NewCredentials()),
    )
    if err != nil {
        panic(err)
    }
    defer conn.Close()

    client := userv1.NewUserServiceClient(conn)

    // Unary 调用
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    resp, err := client.GetUser(ctx, &userv1.GetUserRequest{Id: 1})
    if err != nil {
        if status.Code(err) == codes.NotFound {
            fmt.Println("user not found")
            return
        }
        panic(err)
    }
    fmt.Println(resp.User)

    // 流式调用
    stream, _ := client.WatchUsers(ctx, &userv1.WatchUsersRequest{})
    for {
        user, err := stream.Recv()
        if err == io.EOF {
            break
        }
        if err != nil {
            panic(err)
        }
        fmt.Println("received", user.Name)
    }
}
```

## 6. 拦截器（中间件）

```go
// Unary 拦截器
func loggingInterceptor(
    ctx context.Context,
    req any,
    info *grpc.UnaryServerInfo,
    handler grpc.UnaryHandler,
) (any, error) {
    start := time.Now()
    resp, err := handler(ctx, req)

    slog.InfoContext(ctx, "grpc",
        "method", info.FullMethod,
        "code", status.Code(err),
        "duration_ms", time.Since(start).Milliseconds(),
    )
    return resp, err
}

// Auth 拦截器
func authInterceptor(
    ctx context.Context,
    req any,
    info *grpc.UnaryServerInfo,
    handler grpc.UnaryHandler,
) (any, error) {
    // 跳过公开方法
    if info.FullMethod == "/user.v1.UserService/HealthCheck" {
        return handler(ctx, req)
    }

    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return nil, status.Error(codes.Unauthenticated, "no metadata")
    }
    tokens := md.Get("authorization")
    if len(tokens) == 0 {
        return nil, status.Error(codes.Unauthenticated, "no token")
    }

    userID, err := verifyToken(tokens[0])
    if err != nil {
        return nil, status.Error(codes.Unauthenticated, "invalid token")
    }

    ctx = context.WithValue(ctx, userKey, userID)
    return handler(ctx, req)
}
```

## 7. TLS + 认证

```go
// 服务端
creds, err := credentials.NewServerTLSFromFile("cert.pem", "key.pem")
grpcServer := grpc.NewServer(grpc.Creds(creds))

// 客户端
creds, _ := credentials.NewClientTLSFromFile("ca.pem", "")
conn, _ := grpc.NewClient(addr, grpc.WithTransportCredentials(creds))

// mTLS（相互认证）：客户端和服务端都带证书
// 生产环境推荐：SPIFFE / Service Mesh 自动管理
```

## 8. gRPC 健康检查

```go
import (
    "google.golang.org/grpc/health"
    healthpb "google.golang.org/grpc/health/grpc_health_v1"
)

// 注册
healthServer := health.NewServer()
healthpb.RegisterHealthServer(grpcServer, healthServer)

// 更新状态
healthServer.SetServingStatus("user.v1.UserService", healthpb.HealthCheckResponse_SERVING)

// K8s livenessProbe 可以直接用 grpc_health_probe 工具
```

## 9. Connect：更现代的替代

[Connect-Go](https://connectrpc.com/) 同时支持 gRPC、gRPC-Web 和 HTTP+JSON，浏览器直接调用无需代理：

```go
import (
    "connectrpc.com/connect"
    userv1 "myorg/gen/user/v1"
    "myorg/gen/user/v1/userv1connect"
)

type UserServer struct{}

func (s *UserServer) GetUser(
    ctx context.Context,
    req *connect.Request[userv1.GetUserRequest],
) (*connect.Response[userv1.GetUserResponse], error) {
    // ...
}

mux := http.NewServeMux()
path, handler := userv1connect.NewUserServiceHandler(&UserServer{})
mux.Handle(path, handler)

http.ListenAndServe(":8080", h2c.NewHandler(mux, &http2.Server{}))
```

**Connect 的优势**：
- 同一个 Server 支持 gRPC + gRPC-Web + HTTP/JSON
- 浏览器可以直接调用
- 比 grpc-gateway 更简洁

2026 年新项目推荐 Connect 而非传统 gRPC。

## 10. 反模式

```
❌ 不做 Breaking Change 检查
   → 改字段编号导致客户端崩溃
   ✅ buf breaking

❌ 用 proto3 的 optional 不加 "optional" 关键字
   → 无法区分零值和缺省

❌ 把业务错误塞 Internal
   → 客户端无法区分
   ✅ 用准确的 Code（NotFound、InvalidArgument...）

❌ 不设置 metadata 大小限制
   → DoS 风险
   ✅ MaxRecvMsgSize / MaxHeaderListSize

❌ 一次 Stream 发 1GB 数据
   → 内存爆
   ✅ 分片 + 流控

❌ 不做反射 / 健康检查
   → 调试、部署都痛苦
```

## 11. 生产检查清单

```
☐ Protobuf 用 Buf 管理（lint + breaking）
☐ 每个服务有 Health 接口
☐ 服务端启用 reflection（便于 grpcurl 调试）
☐ 服务间 mTLS（Service Mesh 自动）
☐ 所有调用带 context timeout
☐ 拦截器：日志、recovery、auth、trace
☐ OpenTelemetry 自动埋点
☐ Status Code 准确映射
☐ 错误详情（error_details）用 google.rpc.Status
☐ MaxRecvMsgSize / MaxSendMsgSize 明确
☐ Keepalive 参数合理
☐ 有容量规划（QPS、连接数、并发数）
```

## 📖 参考资料

- [gRPC Go 官方](https://grpc.io/docs/languages/go/)
- [Buf 文档](https://buf.build/docs)
- [Connect-Go](https://connectrpc.com/)
- [Google API 设计指南](https://cloud.google.com/apis/design)
- [gRPC 的最佳实践](https://grpc.io/docs/guides/performance/)
- 关联：[java/05-网络编程/05-gRPC-Java.md](../../java/05-网络编程/05-gRPC-Java.md)
