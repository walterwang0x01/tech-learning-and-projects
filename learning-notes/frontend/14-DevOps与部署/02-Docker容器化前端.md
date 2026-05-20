# Docker 容器化前端
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 多阶段构建

<!-- 修复于 2026-05-19: 示例使用 node:24 LTS（2025-10 进入 LTS），与第 6 节 2026 推荐保持一致 -->

```dockerfile
# 阶段1：构建
FROM node:24-alpine AS builder
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile
COPY . .
RUN pnpm build

# 阶段2：运行
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## 2. nginx.conf

```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|svg|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript image/svg+xml;
}
```

## 3. Docker Compose

<!-- 修复于 2026-05-19: 移除已废弃的 version 字段（Docker Compose v2 不再需要） -->

```yaml
# docker-compose.yml
services:
  web:
    build: .
    ports:
      - "80:80"
    environment:
      - VITE_API_URL=http://api:8080
    depends_on:
      - api
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost"]
      interval: 30s
      timeout: 10s
      retries: 3

  api:
    image: my-api:latest
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgresql://db:5432/mydb
```

## 4. 环境变量注入

```bash
# 构建时注入
docker build --build-arg VITE_API_URL=https://api.example.com -t my-app .

# 运行时注入（需要特殊处理，因为前端是静态文件）
# 方案：使用 entrypoint 脚本替换占位符
```

```bash
#!/bin/sh
# entrypoint.sh
# 将环境变量注入到 JS 文件中
envsubst < /usr/share/nginx/html/env-config.template.js > /usr/share/nginx/html/env-config.js
nginx -g "daemon off;"
```

## 5. 镜像优化

```
优化策略：
1. 使用 alpine 基础镜像（更小）
2. 多阶段构建（只保留产物）
3. .dockerignore 排除不需要的文件
4. 合理利用构建缓存（先 COPY package.json）
```

```
# .dockerignore
node_modules
dist
.git
*.md
.env*
```

## 6. 2026 年 Docker 前端最佳实践

> 🔄 更新于 2026-04-30

<!-- version-check: Docker Engine 29.x, Node.js 24 LTS, Nginx 1.28 stable, checked 2026-05-20 -->

### 6.1 Node.js 24 LTS + Docker 29 推荐 Dockerfile

Docker 29 的三个 Breaking Changes（API 1.44 最低、containerd 默认、nftables 可选）和 Node.js 24 LTS 的发布，要求更新前端容器化实践。

```dockerfile
# 2026 推荐：Node.js 24 LTS + 非 root 用户 + BuildKit 缓存
# syntax=docker/dockerfile:1

# 阶段1：依赖安装（利用 BuildKit 缓存）
FROM node:24-alpine AS deps
WORKDIR /app
COPY package.json pnpm-lock.yaml ./
RUN corepack enable && \
    --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile

# 阶段2：构建
FROM node:24-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN corepack enable && pnpm build

# 阶段3：运行（非 root 用户）
FROM nginx:1.28-alpine
# 安全：以非 root 用户运行
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
# Nginx 需要 root 启动后切换用户，使用 nginx 官方非 root 方案
EXPOSE 8080
USER appuser
CMD ["nginx", "-g", "daemon off;"]
```

### 6.2 Docker Compose v2 语法（移除 version 字段）

```yaml
# docker-compose.yml（2026 推荐：不再需要 version 字段）
services:
  web:
    build:
      context: .
      dockerfile: Dockerfile
    ports:
      - "80:8080"
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:8080"]
      interval: 30s
      timeout: 5s
      retries: 3
    deploy:
      resources:
        limits:
          memory: 128M
```

### 6.3 2026 年关键变化

| 变化 | 影响 |
|------|------|
| Docker 29 API 1.44 最低 | Docker 25 以下版本不再兼容 |
| Docker 29 containerd 默认 | 镜像拉取和存储行为可能变化 |
| Node.js 24 LTS | 推荐基础镜像从 `node:20` 升级到 `node:24` |
| Nginx 1.27 EOS | `nginx:1.27-alpine` 已停止支持，升级到 `nginx:1.28-alpine`（stable） |
| `version` 字段废弃 | Docker Compose 文件不再需要 `version: '3.8'` |
| BuildKit 缓存挂载 | `--mount=type=cache` 显著加速依赖安装 |
| 非 root 用户 | 安全最佳实践，减少容器逃逸风险 |

> 来源：[Docker Engine v29](https://www.docker.com/blog/docker-engine-version-29/)、[Docker Best Practices 2026](https://webcoderspeed.com/blog/scaling/docker-2026-best-practices)
