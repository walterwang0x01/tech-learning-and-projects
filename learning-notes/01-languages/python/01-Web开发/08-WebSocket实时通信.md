# WebSocket 实时通信
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 使用 Python 实现 WebSocket 实时通信

## 1. WebSocket 概述

WebSocket 特点：
- 全双工通信
- 低延迟
- 持久连接
- 支持二进制和文本数据

## 2. FastAPI WebSocket

### 2.1 基础实现

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        print("客户端断开连接")
```

### 2.2 连接管理

```python
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.send_personal_message(f"Client {client_id}: {data}", websocket)
            await manager.broadcast(f"Client {client_id} says: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        await manager.broadcast(f"Client {client_id} left")
```

## 3. Flask-SocketIO

### 3.1 安装和配置

```bash
pip install flask-socketio
```

```python
from flask import Flask, render_template
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('connect')
def handle_connect():
    print('客户端已连接')
    emit('response', {'data': '连接成功'})

@socketio.on('disconnect')
def handle_disconnect():
    print('客户端已断开')

@socketio.on('message')
def handle_message(data):
    print(f'收到消息: {data}')
    emit('response', {'data': f'收到: {data}'}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, debug=True)
```

## 4. Django Channels

### 4.1 安装配置

```bash
pip install channels channels-redis
```

```python
# settings.py
INSTALLED_APPS = [
    'channels',
    # ...
]

ASGI_APPLICATION = 'myproject.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [('127.0.0.1', 6379)],
        },
    },
}
```

### 4.2 消费者实现

```python
# consumers.py
from channels.generic.websocket import AsyncWebsocketConsumer
import json

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message
            }
        )
    
    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))
```

## 5. aiohttp WebSocket

### 5.1 服务器实现

```python
from aiohttp import web
import aiohttp

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            await ws.send_str(f"Echo: {msg.data}")
        elif msg.type == aiohttp.WSMsgType.ERROR:
            break
    
    return ws

app = web.Application()
app.router.add_get('/ws', websocket_handler)
web.run_app(app)
```

## 6. 客户端示例

### 6.1 JavaScript 客户端

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onopen = () => {
    console.log('连接已建立');
    ws.send('Hello Server');
};

ws.onmessage = (event) => {
    console.log('收到消息:', event.data);
};

ws.onerror = (error) => {
    console.error('错误:', error);
};

ws.onclose = () => {
    console.log('连接已关闭');
};
```

## 7. 总结

WebSocket实时通信要点：
- **FastAPI WebSocket**：原生支持、连接管理
- **Flask-SocketIO**：事件驱动、房间管理
- **Django Channels**：异步支持、组播
- **aiohttp WebSocket**：异步WebSocket服务器
- **客户端**：JavaScript WebSocket API

WebSocket适用于实时聊天、通知、数据推送等场景。

