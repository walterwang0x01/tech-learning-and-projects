# FastAPI 快速入门
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 从 private-notes 提取的技术学习笔记

## FastAPI 简介

FastAPI 是一个现代、快速的 Web 框架，用于构建 API，基于 Python 类型提示。

> 🔄 更新于 2026-04-18

<!-- version-check: FastAPI 0.136.1, checked 2026-05-21 -->

**当前版本**：FastAPI 0.136.1（2026-04-23），支持 free-threaded Python 3.14t。

## 核心特性

- **高性能**：JSON 基准测试下可达 15,000-20,000 RPS，与 NodeJS 和 Go 相当
- **快速开发**：开发速度提升约 200% 到 300%
- **类型提示**：基于 Python 类型提示（要求 Pydantic ≥ 2.9.0）
- **自动文档**：自动生成 OpenAPI 和 Swagger 文档
- **异步支持**：原生支持 async/await
- **Free-threaded 支持**：0.136.0 起支持 Python 3.14t（无 GIL）

## 快速开始

### 安装

```bash
# 使用 uv（推荐）
uv add fastapi uvicorn

# 或使用 pip
pip install fastapi uvicorn
```

### 基本示例

```python
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

### 运行

```bash
uvicorn main:app --reload
```

## 核心功能

### 1. 路径参数

```python
@app.get("/items/{item_id}")
async def read_item(item_id: int):
    return {"item_id": item_id}
```

### 2. 查询参数

```python
@app.get("/items/")
async def read_items(skip: int = 0, limit: int = 10):
    return {"skip": skip, "limit": limit}
```

### 3. 请求体

```python
from pydantic import BaseModel

class Item(BaseModel):
    name: str
    price: float

@app.post("/items/")
async def create_item(item: Item):
    return item
```

### 4. WebSocket

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message: {data}")
```

## 最佳实践

1. **使用类型提示**：提高代码可读性和 IDE 支持
2. **依赖注入**：使用 Depends 管理依赖
3. **异常处理**：统一异常处理
4. **中间件**：CORS、日志等
5. **测试**：使用 TestClient 进行测试

## 参考资料

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [FastAPI 中文文档](https://fastapi.tiangolo.com/zh/)
## 🎬 推荐视频资源

- [freeCodeCamp - FastAPI Course](https://www.youtube.com/watch?v=0sOvCWFmrtA) — FastAPI完整课程（19小时）
- [Bitfumes - FastAPI Tutorial](https://www.youtube.com/watch?v=7t2alSnE2-I) — FastAPI快速入门
- [ArjanCodes - FastAPI Best Practices](https://www.youtube.com/watch?v=B9hLkfzgq0s) — FastAPI最佳实践
### 📺 B站（Bilibili）
- [FastAPI中文教程](https://www.bilibili.com/video/BV1iN411X72b) — FastAPI完整中文教程

### 🌐 其他平台
- [FastAPI官方中文文档](https://fastapi.tiangolo.com/zh/) — 官方中文文档（含交互式教程）
