# Python网络编程
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 网络编程概述

Python提供了丰富的网络编程库，可以用于：
- Socket编程：底层网络通信
- HTTP客户端：发送HTTP请求
- WebSocket：实时双向通信
- FTP/SMTP等协议：文件传输和邮件发送

## 2. Socket编程

### 2.1 TCP服务器

```python
import socket

# 创建TCP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# 绑定地址和端口
server_socket.bind(('localhost', 8888))
server_socket.listen(5)

print('服务器启动，等待连接...')

while True:
    # 接受连接
    client_socket, address = server_socket.accept()
    print(f'客户端连接: {address}')
    
    # 接收数据
    data = client_socket.recv(1024)
    print(f'收到数据: {data.decode()}')
    
    # 发送数据
    client_socket.send(b'Hello, Client!')
    
    # 关闭连接
    client_socket.close()
```

### 2.2 TCP客户端

```python
import socket

# 创建TCP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# 连接服务器
client_socket.connect(('localhost', 8888))

# 发送数据
client_socket.send(b'Hello, Server!')

# 接收数据
data = client_socket.recv(1024)
print(f'收到数据: {data.decode()}')

# 关闭连接
client_socket.close()
```

### 2.3 UDP服务器

```python
import socket

# 创建UDP socket
server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_socket.bind(('localhost', 8888))

print('UDP服务器启动...')

while True:
    # 接收数据
    data, address = server_socket.recvfrom(1024)
    print(f'收到来自 {address} 的数据: {data.decode()}')
    
    # 发送响应
    server_socket.sendto(b'Hello, Client!', address)
```

### 2.4 UDP客户端

```python
import socket

# 创建UDP socket
client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# 发送数据
client_socket.sendto(b'Hello, Server!', ('localhost', 8888))

# 接收响应
data, address = client_socket.recvfrom(1024)
print(f'收到来自 {address} 的响应: {data.decode()}')

client_socket.close()
```

### 2.5 多线程服务器

```python
import socket
import threading

def handle_client(client_socket, address):
    print(f'处理客户端 {address} 的请求')
    while True:
        data = client_socket.recv(1024)
        if not data:
            break
        print(f'收到: {data.decode()}')
        client_socket.send(data)
    client_socket.close()

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('localhost', 8888))
server_socket.listen(5)

print('多线程服务器启动...')

while True:
    client_socket, address = server_socket.accept()
    thread = threading.Thread(target=handle_client, args=(client_socket, address))
    thread.start()
```

## 3. HTTP客户端

### 3.1 使用urllib

```python
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import json

# GET请求
response = urlopen('https://www.example.com')
print(response.read().decode())

# POST请求
data = urlencode({'key': 'value'}).encode()
request = Request('https://httpbin.org/post', data=data)
response = urlopen(request)
print(response.read().decode())
```

### 3.2 使用requests库

#### 安装

```bash
pip install requests
```

#### GET请求

```python
import requests

# 基本GET请求
response = requests.get('https://www.example.com')
print(response.status_code)
print(response.text)

# 带参数的GET请求
params = {'key1': 'value1', 'key2': 'value2'}
response = requests.get('https://httpbin.org/get', params=params)
print(response.json())

# 带请求头
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get('https://www.example.com', headers=headers)
```

#### POST请求

```python
import requests

# 表单数据
data = {'key1': 'value1', 'key2': 'value2'}
response = requests.post('https://httpbin.org/post', data=data)
print(response.json())

# JSON数据
json_data = {'key': 'value'}
response = requests.post('https://httpbin.org/post', json=json_data)
print(response.json())

# 文件上传
files = {'file': open('test.txt', 'rb')}
response = requests.post('https://httpbin.org/post', files=files)
```

#### 会话管理

```python
import requests

# 创建会话
session = requests.Session()

# 设置Cookie
session.cookies.set('name', 'value')

# 使用会话发送请求
response = session.get('https://www.example.com')
```

#### 超时和重试

```python
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

# 设置超时
response = requests.get('https://www.example.com', timeout=5)

# 配置重试策略
retry_strategy = Retry(
    total=3,
    backoff_factor=1,
    status_forcelist=[429, 500, 502, 503, 504]
)

adapter = HTTPAdapter(max_retries=retry_strategy)
session = requests.Session()
session.mount("https://", adapter)
```

## 4. WebSocket编程

### 4.1 使用websockets库

#### 安装

```bash
pip install websockets
```

#### WebSocket服务器

```python
import asyncio
import websockets

async def handle_client(websocket, path):
    print(f'客户端连接: {websocket.remote_address}')
    try:
        async for message in websocket:
            print(f'收到消息: {message}')
            await websocket.send(f'服务器回复: {message}')
    except websockets.exceptions.ConnectionClosed:
        print('客户端断开连接')

async def main():
    async with websockets.serve(handle_client, "localhost", 8765):
        print('WebSocket服务器启动在 ws://localhost:8765')
        await asyncio.Future()  # 永久运行

asyncio.run(main())
```

#### WebSocket客户端

```python
import asyncio
import websockets

async def client():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # 发送消息
        await websocket.send("Hello, Server!")
        
        # 接收消息
        response = await websocket.recv()
        print(f'收到: {response}')

asyncio.run(client())
```

## 5. FTP客户端

```python
from ftplib import FTP

# 连接FTP服务器
ftp = FTP('ftp.example.com')
ftp.login('username', 'password')

# 列出文件
ftp.retrlines('LIST')

# 下载文件
with open('local_file.txt', 'wb') as f:
    ftp.retrbinary('RETR remote_file.txt', f.write)

# 上传文件
with open('local_file.txt', 'rb') as f:
    ftp.storbinary('STOR remote_file.txt', f)

# 关闭连接
ftp.quit()
```

## 6. SMTP邮件发送

```python
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 创建邮件
msg = MIMEMultipart()
msg['From'] = 'sender@example.com'
msg['To'] = 'receiver@example.com'
msg['Subject'] = '测试邮件'

body = '这是一封测试邮件'
msg.attach(MIMEText(body, 'plain', 'utf-8'))

# 发送邮件
server = smtplib.SMTP('smtp.example.com', 587)
server.starttls()
server.login('username', 'password')
server.send_message(msg)
server.quit()
```

## 7. 网络工具

### 7.1 DNS查询

```python
import socket

# 域名解析
hostname = 'www.example.com'
ip = socket.gethostbyname(hostname)
print(f'{hostname} -> {ip}')

# 反向解析
ip = '93.184.216.34'
hostname = socket.gethostbyaddr(ip)
print(f'{ip} -> {hostname[0]}')
```

### 7.2 端口扫描

```python
import socket

def scan_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((host, port))
        if result == 0:
            print(f'端口 {port} 开放')
        sock.close()
    except socket.error:
        pass

host = 'localhost'
for port in range(1, 1024):
    scan_port(host, port)
```

## 8. 异步网络编程

### 8.1 异步HTTP客户端

```python
import aiohttp
import asyncio

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    async with aiohttp.ClientSession() as session:
        urls = [
            'https://www.example.com',
            'https://www.python.org',
            'https://www.github.com'
        ]
        tasks = [fetch(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        for result in results:
            print(result[:100])  # 打印前100个字符

asyncio.run(main())
```

### 8.2 异步WebSocket客户端

```python
import asyncio
import websockets

async def client():
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        # 发送消息
        await websocket.send("Hello, Server!")
        
        # 接收消息
        while True:
            try:
                message = await websocket.recv()
                print(f'收到: {message}')
            except websockets.exceptions.ConnectionClosed:
                break

asyncio.run(client())
```

## 9. 最佳实践

1. **异常处理**：网络操作可能失败，需要适当的异常处理
2. **超时设置**：避免程序无限等待
3. **连接池**：对于频繁的网络请求，使用连接池提高性能
4. **异步编程**：对于高并发场景，使用异步编程
5. **安全考虑**：使用HTTPS、验证证书、防止注入攻击

## 10. 总结

Python提供了丰富的网络编程工具：
- **Socket**：底层网络通信
- **requests**：简单易用的HTTP客户端
- **websockets**：WebSocket通信
- **asyncio + aiohttp**：异步网络编程

选择合适的工具可以高效地实现网络通信功能。


## 11. 2026 年 Python HTTP 客户端选型

<!-- version-check: httpx 0.28.1, aiohttp 3.11.x, requests 2.32.3, checked 2026-05-04 -->

> 🔄 更新于 2026-05-04

### 11.1 httpx：现代 Python HTTP 客户端

httpx 是 requests 的现代替代品，同时支持同步和异步 API，内置 HTTP/2 支持。当前稳定版 **0.28.1**（2024-12-06），1.0 开发版已在 PyPI 上发布（`1.0.dev1`），正式版预计 2026 年内发布。

来源：[httpx 官方文档](https://www.python-httpx.org/)、[httpx GitHub](https://github.com/encode/httpx)

```bash
# 安装
uv add httpx
# HTTP/2 支持
uv add "httpx[http2]"
```

```python
import httpx

# 同步用法（替代 requests）
response = httpx.get("https://httpbin.org/get", params={"key": "value"})
print(response.json())

# 异步用法（替代 aiohttp）
async with httpx.AsyncClient() as client:
    response = await client.get("https://httpbin.org/get")
    print(response.json())

# HTTP/2 支持
async with httpx.AsyncClient(http2=True) as client:
    response = await client.get("https://www.example.com")
    print(response.http_version)  # "HTTP/2"

# 超时和重试配置
client = httpx.Client(
    timeout=httpx.Timeout(10.0, connect=5.0),
    follow_redirects=True,
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=20),
)
```

### 11.2 2026 年 Python HTTP 客户端选型表

| 库 | 版本 | 同步 | 异步 | HTTP/2 | 适用场景 |
|----|------|------|------|--------|---------|
| **httpx** | 0.28.1 | ✅ | ✅ | ✅ | **新项目推荐**，统一同步/异步 API |
| requests | 2.32.3 | ✅ | ❌ | ❌ | 简单同步请求，生态最丰富 |
| aiohttp | 3.11.x | ❌ | ✅ | ❌ | 纯异步场景，WebSocket 支持好 |
| urllib3 | 2.3.x | ✅ | ❌ | ❌ | 底层库，requests 的依赖 |

**选型建议**：
- **新项目**：优先选择 httpx，一个库覆盖同步和异步场景
- **已有 requests 项目**：httpx API 与 requests 高度兼容，迁移成本低
- **纯异步高并发**：aiohttp 仍然是成熟选择，WebSocket 支持更完善
- **AI Agent / LLM 调用**：httpx 是 OpenAI、Anthropic 等 SDK 的底层 HTTP 客户端
