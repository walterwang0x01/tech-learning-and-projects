# Nginx 前端部署配置
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. SPA 部署

```nginx
server {
    listen 80;
    server_name example.com;
    root /var/www/html;
    index index.html;

    # SPA 路由：所有路径回退到 index.html
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存（带哈希的文件名）
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # API 反向代理
    location /api/ {
        proxy_pass http://localhost:8080/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Gzip 压缩
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript
               text/xml application/xml application/xml+rss text/javascript
               image/svg+xml;

    # 安全头
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "0" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self'" always;
}
```

## 2. HTTPS 配置

```nginx
server {
    listen 443 ssl http2;
    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
}

# HTTP → HTTPS 重定向
server {
    listen 80;
    server_name example.com;
    return 301 https://$server_name$request_uri;
}
```

## 3. 负载均衡

```nginx
upstream backend {
    server 127.0.0.1:3001;
    server 127.0.0.1:3002;
    server 127.0.0.1:3003;
}

server {
    location /api/ {
        proxy_pass http://backend;
    }
}
```

## 4. HTTP/3 与 Brotli 配置（2026）

> 🔄 更新于 2026-04-30

<!-- version-check: Nginx 1.28.x stable (1.30.0 新 stable 已发布), HTTP/3 QUIC module, checked 2026-05-20 -->

### 4.1 HTTP/3 (QUIC) 配置

HTTP/3 已被全球 30%+ 的网站采用（具体数据需以 [Cloudflare Radar](https://radar.cloudflare.com) 或 W3Techs 为准），所有主流浏览器支持。Nginx 1.25+ 内置 HTTP/3 模块（需编译时启用 `--with-http_v3_module`）。当前 stable 分支为 1.28.x（1.30.0 stable 已于 2026-06 发布）。

> ⚠️ 安全提示：CVE-2026-42945（"NGINX Rift"）影响 Nginx 0.6.27 至 1.30.0，涉及 rewrite 模块的 HTTP/2 和 HTTP/3 请求注入漏洞。请确保使用已修补版本（1.28.3+ 或 1.30.1+）。
<!-- 修复于 2026-05-20: 补充 Nginx 版本更新和 CVE-2026-42945 安全提示 -->

> ⚠️ 待确认：HTTP/3 具体采用率（之前引用 38.8% 来源不够权威，建议以官方统计源核实）
<!-- 修复于 2026-05-19: 弱化具体百分比，明确引用源标注 -->

```nginx
server {
    # HTTP/3 需要同时监听 TCP（HTTP/2 回退）和 UDP（QUIC）
    listen 443 ssl;
    listen 443 quic reuseport;
    http2 on;

    server_name example.com;

    ssl_certificate /etc/letsencrypt/live/example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/example.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;

    # 告知浏览器支持 HTTP/3
    add_header Alt-Svc 'h3=":443"; ma=86400' always;

    # QUIC 特定设置
    quic_retry on;
    ssl_early_data on;

    root /var/www/html;
    index index.html;

    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

> ⚠️ 注意：Nginx HTTP/3 在 reload 时可能导致约 50% 的 QUIC 连接中断（已知问题），建议使用 graceful restart 替代 reload。来源：[GetPageSpeed](https://www.getpagespeed.com/server-setup/nginx/nginx-http3-reload-quic-connections-fail)

### 4.2 Brotli 压缩

Brotli 比 Gzip 压缩率高 15-25%，所有现代浏览器支持。

```nginx
# 需要安装 ngx_brotli 模块
brotli on;
brotli_comp_level 6;
brotli_types text/plain text/css application/json application/javascript
             text/xml application/xml application/xml+rss text/javascript
             image/svg+xml application/wasm;

# 同时保留 Gzip 作为回退
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css application/json application/javascript
           image/svg+xml;
```

### 4.3 2026 年推荐安全头组合

```nginx
# 2026 年推荐的完整安全响应头
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "strict-origin-when-cross-origin" always;
add_header Permissions-Policy "camera=(), microphone=(), geolocation=()" always;
add_header Cross-Origin-Opener-Policy "same-origin" always;
add_header Cross-Origin-Embedder-Policy "require-corp" always;

# 注意：X-XSS-Protection 已废弃，现代浏览器使用 CSP 替代
# 注意：CSP 建议通过应用层（meta 标签或 Trusted Types）配置，而非 Nginx 硬编码
```

> 来源：[Nginx HTTP/3 Guide](https://cubepath.com/docs/web-performance/http3-quic-configuration-guide)、HTTP/3 全球采用率统计建议参考 [Cloudflare Radar](https://radar.cloudflare.com)
