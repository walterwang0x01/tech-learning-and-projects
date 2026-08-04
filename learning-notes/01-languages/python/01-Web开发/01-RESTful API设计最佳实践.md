# RESTful API 设计最佳实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 设计和实现高质量 RESTful API 的指南

## 1. RESTful 原则

### 1.1 核心原则

- **资源导向**：URL 表示资源，不是动作
- **HTTP 方法**：GET、POST、PUT、DELETE、PATCH
- **无状态**：每个请求包含所有必要信息
- **统一接口**：标准化的接口设计

### 1.2 URL 设计

```python
# ✅ 好的设计
GET    /api/v1/users          # 获取用户列表
GET    /api/v1/users/123      # 获取特定用户
POST   /api/v1/users          # 创建用户
PUT    /api/v1/users/123      # 更新用户（完整）
PATCH  /api/v1/users/123      # 更新用户（部分）
DELETE /api/v1/users/123      # 删除用户

# ❌ 不好的设计
GET    /api/v1/getUsers
POST   /api/v1/user/create
GET    /api/v1/user/123/delete
```

## 2. HTTP 状态码

### 2.1 常用状态码

```python
from fastapi import status

# 成功
200 OK              # 请求成功
201 Created         # 资源创建成功
204 No Content      # 删除成功，无返回内容

# 客户端错误
400 Bad Request     # 请求参数错误
401 Unauthorized    # 未认证
403 Forbidden       # 无权限
404 Not Found       # 资源不存在
409 Conflict        # 资源冲突
422 Unprocessable   # 验证失败

# 服务器错误
500 Internal Server Error
503 Service Unavailable
```

### 2.2 状态码使用示例

```python
from fastapi import HTTPException, status

@app.post("/users/", status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    # 创建用户
    return {"id": 1, **user.dict()}

@app.get("/users/{user_id}")
async def get_user(user_id: int):
    user = find_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    # 删除用户
    pass
```

## 3. 请求和响应格式

### 3.1 统一响应格式

```python
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel

T = TypeVar('T')

class APIResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: Optional[T] = None
    timestamp: int = Field(default_factory=lambda: int(time.time()))

@app.get("/users/", response_model=APIResponse[List[User]])
async def get_users():
    users = [{"id": 1, "name": "Alice"}]
    return APIResponse(data=users)
```

### 3.2 分页响应

```python
class PaginationParams:
    def __init__(self, page: int = 1, size: int = 10):
        self.page = max(1, page)
        self.size = min(100, max(1, size))
        self.skip = (self.page - 1) * self.size

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    size: int
    pages: int

@app.get("/users/")
async def get_users(
    page: int = 1,
    size: int = 10
):
    params = PaginationParams(page, size)
    users, total = get_users_paginated(params.skip, params.size)
    return PaginatedResponse(
        items=users,
        total=total,
        page=params.page,
        size=params.size,
        pages=(total + params.size - 1) // params.size
    )
```

## 4. 版本控制

### 4.1 URL 版本控制

```python
v1_router = APIRouter(prefix="/api/v1", tags=["v1"])
v2_router = APIRouter(prefix="/api/v2", tags=["v2"])

@v1_router.get("/users/")
async def get_users_v1():
    return {"version": "v1", "users": []}

@v2_router.get("/users/")
async def get_users_v2():
    return {"version": "v2", "users": []}

app.include_router(v1_router)
app.include_router(v2_router)
```

### 4.2 Header 版本控制

```python
from fastapi import Header

@app.get("/api/users/")
async def get_users(api_version: str = Header("v1", alias="API-Version")):
    if api_version == "v1":
        return get_users_v1()
    elif api_version == "v2":
        return get_users_v2()
    else:
        raise HTTPException(400, "不支持的API版本")
```

## 5. 过滤、排序和搜索

### 5.1 查询参数

```python
from typing import Optional
from enum import Enum

class SortOrder(str, Enum):
    asc = "asc"
    desc = "desc"

@app.get("/users/")
async def get_users(
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    min_age: Optional[int] = None,
    max_age: Optional[int] = None,
    sort_by: str = "id",
    order: SortOrder = SortOrder.asc
):
    # 构建查询
    query = build_query(name, min_age, max_age)
    users = query.order_by(getattr(User, sort_by)).all()
    return users
```

### 5.2 全文搜索

```python
@app.get("/users/search/")
async def search_users(q: str):
    # 使用全文搜索
    users = db.query(User).filter(
        User.name.contains(q) | User.email.contains(q)
    ).all()
    return users
```

## 6. 错误处理

### 6.1 统一错误响应

```python
class ErrorResponse(BaseModel):
    code: int
    message: str
    detail: Optional[str] = None
    timestamp: int = Field(default_factory=lambda: int(time.time()))

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            code=exc.status_code,
            message=exc.detail,
            detail=str(exc)
        ).dict()
    )
```

### 6.2 验证错误

```python
from fastapi.exceptions import RequestValidationError

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content=ErrorResponse(
            code=422,
            message="验证失败",
            detail=exc.errors()
        ).dict()
    )
```

## 7. 认证和授权

### 7.1 JWT 认证

```python
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"

def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(401, "无效的令牌")
```

### 7.2 权限控制

```python
from enum import Enum

class Role(str, Enum):
    admin = "admin"
    user = "user"
    guest = "guest"

def require_role(required_role: Role):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            current_user = kwargs.get("current_user")
            if not current_user or current_user.role != required_role:
                raise HTTPException(403, "权限不足")
            return await func(*args, **kwargs)
        return wrapper
    return decorator

@app.delete("/users/{user_id}")
@require_role(Role.admin)
async def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    # 删除用户
    pass
```

## 8. 速率限制

### 8.1 基于IP的限流

```python
from collections import defaultdict
from datetime import datetime, timedelta

class RateLimiter:
    def __init__(self, max_requests: int = 100, window: int = 60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)
    
    def is_allowed(self, client_id: str) -> bool:
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window)
        
        # 清理过期请求
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id]
            if req_time > window_start
        ]
        
        if len(self.requests[client_id]) >= self.max_requests:
            return False
        
        self.requests[client_id].append(now)
        return True

rate_limiter = RateLimiter(max_requests=100, window=60)

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    client_id = request.client.host
    if not rate_limiter.is_allowed(client_id):
        return JSONResponse(
            status_code=429,
            content={"message": "请求过于频繁"}
        )
    return await call_next(request)
```

## 9. API 文档

### 9.1 OpenAPI 配置

```python
app = FastAPI(
    title="My API",
    description="API 描述",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
```

### 9.2 标签和描述

```python
@app.post(
    "/users/",
    tags=["用户管理"],
    summary="创建用户",
    description="创建一个新用户",
    response_description="创建的用户信息"
)
async def create_user(user: UserCreate):
    """创建用户的详细说明"""
    return user
```

## 10. 最佳实践总结

### 10.1 设计原则

1. **资源命名**：使用名词，复数形式
2. **HTTP方法**：正确使用GET、POST、PUT、DELETE
3. **状态码**：使用标准HTTP状态码
4. **版本控制**：URL或Header版本控制
5. **分页**：大数据集使用分页
6. **过滤排序**：通过查询参数实现
7. **错误处理**：统一的错误响应格式
8. **安全**：HTTPS、认证、授权
9. **限流**：防止滥用
10. **文档**：完整的API文档

### 10.2 性能优化

- 使用缓存（Redis）
- 数据库查询优化
- 异步处理
- 连接池
- 压缩响应

## 11. 总结

RESTful API 设计要点：
- **资源导向**：URL表示资源
- **HTTP标准**：正确使用方法和状态码
- **统一格式**：一致的请求响应格式
- **版本控制**：支持API演进
- **安全**：认证、授权、限流
- **文档**：完整的API文档
- **性能**：缓存、优化、异步

遵循这些最佳实践，可以设计出高质量、易用的 RESTful API。

