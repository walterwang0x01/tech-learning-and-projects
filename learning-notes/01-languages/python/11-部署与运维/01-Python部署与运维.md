# Python部署与运维
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 部署概述

Python应用的部署需要考虑：
- **Web服务器**：Gunicorn、uWSGI
- **反向代理**：Nginx
- **容器化**：Docker
- **进程管理**：Supervisor、systemd
- **监控**：日志、性能监控

## 2. Gunicorn部署

### 2.1 安装

```bash
pip install gunicorn
```

### 2.2 基本使用

```bash
# 启动Flask应用
gunicorn app:app

# 指定配置
gunicorn app:app -w 4 -b 0.0.0.0:8000

# 使用配置文件
gunicorn app:app -c gunicorn.conf.py
```

### 2.3 配置文件

```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 50
preload_app = True
daemon = False
pidfile = "/var/run/gunicorn.pid"
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
```

### 2.4 启动脚本

```bash
#!/bin/bash
# start.sh
gunicorn app:app \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --worker-class gevent \
    --access-logfile /var/log/gunicorn/access.log \
    --error-logfile /var/log/gunicorn/error.log \
    --daemon \
    --pid /var/run/gunicorn.pid
```

## 3. uWSGI部署

### 3.1 安装

```bash
pip install uwsgi
```

### 3.2 基本使用

```bash
# 启动应用
uwsgi --http :8000 --wsgi-file app.py --callable app

# 使用配置文件
uwsgi --ini uwsgi.ini
```

### 3.3 配置文件

```ini
# uwsgi.ini
[uwsgi]
http = 0.0.0.0:8000
wsgi-file = app.py
callable = app
processes = 4
threads = 2
master = true
daemonize = /var/log/uwsgi/uwsgi.log
pidfile = /var/run/uwsgi.pid
vacuum = true
```

## 4. Nginx配置

### 4.1 基本配置

```nginx
server {
    listen 80;
    server_name example.com;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /static {
        alias /path/to/static;
        expires 30d;
    }
}
```

### 4.2 负载均衡

```nginx
upstream app_servers {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    listen 80;
    server_name example.com;
    
    location / {
        proxy_pass http://app_servers;
    }
}
```

## 5. Docker部署

### 5.1 Dockerfile

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "app:app", "-w", "4", "-b", "0.0.0.0:8000"]
```

### 5.2 docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    environment:
      - FLASK_ENV=production
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=mydb
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine
    volumes:
      - redis_data:/data

volumes:
  postgres_data:
  redis_data:
```

### 5.3 构建和运行

```bash
# 构建镜像
docker build -t myapp .

# 运行容器
docker run -d -p 8000:8000 myapp

# 使用docker-compose
docker-compose up -d
```

## 6. Supervisor进程管理

### 6.1 安装

```bash
pip install supervisor
```

### 6.2 配置文件

```ini
# supervisord.conf
[program:myapp]
command=/path/to/venv/bin/gunicorn app:app -w 4 -b 0.0.0.0:8000
directory=/path/to/app
user=www-data
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/myapp.log
```

### 6.3 管理命令

```bash
# 启动
supervisord -c supervisord.conf

# 管理
supervisorctl start myapp
supervisorctl stop myapp
supervisorctl restart myapp
supervisorctl status
```

## 7. systemd服务

### 7.1 服务文件

```ini
# /etc/systemd/system/myapp.service
[Unit]
Description=My Python App
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/app
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn app:app -w 4 -b 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

### 7.2 管理命令

```bash
# 启动服务
sudo systemctl start myapp

# 停止服务
sudo systemctl stop myapp

# 重启服务
sudo systemctl restart myapp

# 查看状态
sudo systemctl status myapp

# 开机自启
sudo systemctl enable myapp
```

## 8. 日志管理

### 8.1 日志配置

```python
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                'app.log',
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            logging.StreamHandler()
        ]
    )
```

### 8.2 日志轮转

```bash
# 使用logrotate
# /etc/logrotate.d/myapp
/path/to/app/*.log {
    daily
    rotate 7
    compress
    delaycompress
    notifempty
    create 0644 www-data www-data
    sharedscripts
    postrotate
        systemctl reload myapp
    endscript
}
```

## 9. 监控

### 9.1 健康检查

```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })
```

### 9.2 性能监控

```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start
        logger.info(f'{func.__name__} took {duration:.2f}s')
        return result
    return wrapper
```

### 9.3 Prometheus监控

```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('requests_total', 'Total requests')
REQUEST_DURATION = Histogram('request_duration_seconds', 'Request duration')

@app.route('/metrics')
def metrics():
    return generate_latest()
```

## 10. 环境变量管理

### 10.1 使用python-decouple

```bash
pip install python-decouple
```

```python
from decouple import config

DATABASE_URL = config('DATABASE_URL')
SECRET_KEY = config('SECRET_KEY', default='default-secret')
DEBUG = config('DEBUG', default=False, cast=bool)
```

### 10.2 .env文件

```env
DATABASE_URL=postgresql://user:password@localhost/dbname
SECRET_KEY=your-secret-key
DEBUG=False
```

## 11. 数据库迁移

### 11.1 Flask-Migrate

```bash
pip install flask-migrate
```

```python
from flask_migrate import Migrate

migrate = Migrate(app, db)

# 初始化
flask db init

# 创建迁移
flask db migrate -m "Initial migration"

# 应用迁移
flask db upgrade
```

### 11.2 Django迁移

```bash
# 创建迁移
python manage.py makemigrations

# 应用迁移
python manage.py migrate
```

## 12. 静态文件处理

### 12.1 收集静态文件

```bash
# Django
python manage.py collectstatic

# Flask
flask collectstatic
```

### 12.2 Nginx配置

```nginx
location /static {
    alias /path/to/static;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

## 13. SSL/TLS配置

### 13.1 Let's Encrypt

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d example.com
```

### 13.2 Nginx HTTPS配置

```nginx
server {
    listen 443 ssl;
    server_name example.com;
    
    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

## 14. 备份策略

### 14.1 数据库备份

```bash
#!/bin/bash
# backup.sh
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U user dbname > backup_$DATE.sql
```

### 14.2 定时备份

```bash
# crontab
0 2 * * * /path/to/backup.sh
```

## 15. 最佳实践

1. **使用虚拟环境**：隔离依赖
2. **环境变量**：敏感信息使用环境变量
3. **日志管理**：完善的日志记录和轮转
4. **监控告警**：实时监控应用状态
5. **自动化部署**：使用CI/CD自动化部署流程
6. **安全加固**：定期更新依赖，使用HTTPS

## 16. 2026 年 Python 部署演进

> 🔄 更新于 2026-05-02

<!-- version-check: Gunicorn 23.x, Uvicorn 0.34.x, Docker 29, checked 2026-05-02 -->

### 16.1 ASGI 成为新项目默认

2026 年，ASGI 已从实验性方案变为新项目的默认选择。FastAPI、现代 Django（4.0+）和 Starlette 都原生支持 ASGI。

**Gunicorn + Uvicorn Workers 是生产标准组合**：

```python
# gunicorn.conf.py — 2026 年推荐配置
import multiprocessing

# Uvicorn worker 处理 ASGI 异步请求
worker_class = "uvicorn.workers.UvicornWorker"

# Worker 数量：CPU 核心数 × 2 + 1
workers = multiprocessing.cpu_count() * 2 + 1

bind = "0.0.0.0:8000"
timeout = 120
keepalive = 5
max_requests = 1000
max_requests_jitter = 50
accesslog = "-"
errorlog = "-"
loglevel = "info"

# 优雅关闭超时
graceful_timeout = 30
```

```bash
# 启动命令
gunicorn app.main:app -c gunicorn.conf.py
```

### 16.2 2026 年推荐 Dockerfile

```dockerfile
# 多阶段构建，Docker 29 + Python 3.14
FROM python:3.14-slim AS builder

# 使用 uv 替代 pip（10-100x 速度提升）
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.14-slim AS runtime

# 非 root 用户运行
RUN groupadd -r app && useradd -r -g app app

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY . .

# 设置 PATH 使用虚拟环境
ENV PATH="/app/.venv/bin:$PATH"

USER app
EXPOSE 8000

CMD ["gunicorn", "app.main:app", "-c", "gunicorn.conf.py"]
```

### 16.3 Python Web 服务器选型表（2026）

| 服务器 | 协议 | 适用场景 | 推荐度 |
|--------|------|---------|--------|
| Gunicorn + Uvicorn Workers | ASGI | FastAPI/Django 异步 | ⭐⭐⭐⭐⭐ |
| Uvicorn 单独运行 | ASGI | 开发环境/小型应用 | ⭐⭐⭐ |
| Gunicorn（sync workers） | WSGI | Flask/Django 同步 | ⭐⭐⭐⭐ |
| Hypercorn | ASGI/HTTP2/HTTP3 | 需要 HTTP/3 支持 | ⭐⭐⭐ |
| uWSGI | WSGI | 遗留项目 | ⭐⭐（不推荐新项目） |

> 来源：[Python Application Servers in 2025](https://www.deployhq.com/blog/python-application-servers-in-2025-from-wsgi-to-modern-asgi-solutions)、[FastAPI Deployment Guide 2026](https://zestminds.com/blog/fastapi-deployment-guide/)

## 17. 总结

Python应用部署涉及多个方面：
- **Web服务器**：Gunicorn + Uvicorn Workers（ASGI 标准组合）
- **反向代理**：Nginx（HTTP/3 支持）
- **容器化**：Docker 29 + uv 构建
- **进程管理**：systemd（推荐）、Supervisor
- **监控**：Prometheus + 结构化日志

合理的部署方案可以确保应用的稳定运行。

