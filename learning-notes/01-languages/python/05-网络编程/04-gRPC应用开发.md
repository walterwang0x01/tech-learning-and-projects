# gRPC 应用开发
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 使用 gRPC 构建高性能 RPC 服务

## 1. gRPC 概述

gRPC 是高性能、跨语言的 RPC 框架：
- 基于 HTTP/2
- 使用 Protocol Buffers
- 支持流式传输
- 跨语言支持

## 2. 定义服务

### 2.1 编写 .proto 文件

```protobuf
syntax = "proto3";

package user;

service UserService {
  rpc GetUser (UserRequest) returns (UserResponse);
  rpc CreateUser (CreateUserRequest) returns (UserResponse);
  rpc ListUsers (ListUsersRequest) returns (stream UserResponse);
}

message UserRequest {
  int32 id = 1;
}

message CreateUserRequest {
  string name = 1;
  string email = 2;
}

message UserResponse {
  int32 id = 1;
  string name = 2;
  string email = 3;
}

message ListUsersRequest {
  int32 page = 1;
  int32 page_size = 2;
}
```

### 2.2 生成代码

```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. user.proto
```

## 3. 实现服务端

```python
import grpc
from concurrent import futures
import user_pb2
import user_pb2_grpc

class UserService(user_pb2_grpc.UserServiceServicer):
    def GetUser(self, request, context):
        return user_pb2.UserResponse(
            id=request.id,
            name="Alice",
            email="alice@example.com"
        )
    
    def CreateUser(self, request, context):
        # 创建用户逻辑
        return user_pb2.UserResponse(
            id=1,
            name=request.name,
            email=request.email
        )
    
    def ListUsers(self, request, context):
        # 流式返回
        for i in range(10):
            yield user_pb2.UserResponse(
                id=i,
                name=f"User{i}",
                email=f"user{i}@example.com"
            )

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    user_pb2_grpc.add_UserServiceServicer_to_server(
        UserService(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
```

## 4. 实现客户端

```python
import grpc
import user_pb2
import user_pb2_grpc

def run():
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = user_pb2_grpc.UserServiceStub(channel)
        
        # 调用服务
        response = stub.GetUser(user_pb2.UserRequest(id=1))
        print(f"用户: {response.name}")
        
        # 流式调用
        responses = stub.ListUsers(user_pb2.ListUsersRequest(page=1, page_size=10))
        for response in responses:
            print(f"用户: {response.name}")

if __name__ == '__main__':
    run()
```

## 5. 总结

gRPC 应用开发要点：
- **Protocol Buffers**：定义服务接口
- **服务端实现**：实现服务方法
- **客户端调用**：使用生成的客户端代码
- **流式传输**：支持单向和双向流
- **跨语言**：支持多种编程语言

gRPC 适合构建高性能的微服务系统。


## 6. gRPC Python 2026 版本演进

<!-- version-check: grpcio 1.80.0, grpcio-tools 1.80.0, checked 2026-05-04 -->

> 🔄 更新于 2026-05-04

### 6.1 版本跃升

gRPC Python（grpcio）从文档中的早期版本跃升至 **1.80.0**（2026-01-16 发布），版本号与 gRPC-Core C++ 保持同步。

来源：[grpcio PyPI](https://pypi.org/project/grpcio/)、[gRPC-Core 1.80.0 Release](https://groups.google.com/g/grpc-io/c/D65xLNpE5Eg)

**关键里程碑**：

| 版本 | 发布时间 | 重要变化 |
|------|---------|---------|
| 1.60.x | 2023 | Python 3.8+ 最低要求 |
| 1.66.x | 2024 | Python 3.13 支持 |
| 1.70.x | 2025 | 性能优化、xDS 负载均衡增强 |
| 1.78.0 | 2026-02-20 | Python 3.14 支持 |
| **1.80.0** | **2026-01-16** | **当前稳定版**，Python 3.9-3.14 支持 |

### 6.2 推荐依赖版本（2026）

```bash
# 使用 uv 安装（推荐）
uv add grpcio==1.80.0 grpcio-tools==1.80.0

# 或使用 pip
pip install grpcio==1.80.0 grpcio-tools==1.80.0

# 可选扩展包
pip install grpcio-health-checking==1.80.0  # 健康检查
pip install grpcio-reflection==1.80.0       # 服务反射
pip install grpcio-status==1.80.0           # 状态码映射
```

### 6.3 异步 gRPC 服务端（推荐）

Python 3.14 的 asyncio 改进让异步 gRPC 成为生产推荐方案：

```python
import grpc
import grpc.aio
import user_pb2
import user_pb2_grpc

class UserService(user_pb2_grpc.UserServiceServicer):
    async def GetUser(self, request, context):
        # 异步数据库查询
        user = await db.get_user(request.id)
        if not user:
            await context.abort(
                grpc.StatusCode.NOT_FOUND,
                f"用户 {request.id} 不存在"
            )
        return user_pb2.UserResponse(
            id=user.id, name=user.name, email=user.email
        )

    async def ListUsers(self, request, context):
        # 异步流式返回
        async for user in db.list_users(request.page, request.page_size):
            yield user_pb2.UserResponse(
                id=user.id, name=user.name, email=user.email
            )

async def serve():
    server = grpc.aio.server()
    user_pb2_grpc.add_UserServiceServicer_to_server(UserService(), server)
    # 生产环境使用 TLS
    server.add_insecure_port('[::]:50051')
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    import asyncio
    asyncio.run(serve())
```

### 6.4 版本选择建议

| 场景 | 推荐版本 |
|------|---------|
| 新项目 | grpcio 1.80.0 + Python 3.12+ |
| 需要 Python 3.14 | grpcio 1.78.0+ |
| 与 Java gRPC 互操作 | grpcio 版本与 gRPC-Java 保持一致（1.78-1.80） |
| Protobuf 版本 | protobuf 4.29.x（Editions 语法） |
