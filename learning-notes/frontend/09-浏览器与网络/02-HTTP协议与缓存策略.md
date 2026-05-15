# HTTP 协议与缓存策略
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. HTTP 版本对比

| 特性 | HTTP/1.1 | HTTP/2 | HTTP/3 |
|------|---------|--------|--------|
| 传输层 | TCP | TCP | QUIC (UDP) |
| 多路复用 | 否（队头阻塞） | 是 | 是 |
| 头部压缩 | 否 | HPACK | QPACK |
| 服务器推送 | 否 | 是 | 否 |
| 连接建立 | TCP + TLS | TCP + TLS | 0-RTT / 1-RTT |

## 2. HTTPS / TLS

```
客户端                    服务器
  │── ClientHello ──────────>│  （支持的加密套件）
  │<── ServerHello ──────────│  （选择的加密套件 + 证书）
  │── 验证证书 + 密钥交换 ──>│
  │<── 完成握手 ─────────────│
  │<══ 加密通信 ════════════>│
```

## 3. 缓存策略

### 3.1 强缓存（不发请求）

```
Cache-Control: max-age=31536000    # 缓存1年
Cache-Control: no-cache            # 每次都协商
Cache-Control: no-store            # 不缓存
Cache-Control: private             # 仅浏览器缓存
Cache-Control: public              # 允许CDN缓存

Expires: Thu, 01 Jan 2026 00:00:00 GMT  # 过期时间（优先级低于 Cache-Control）
```

### 3.2 协商缓存（发请求验证）

```
# 基于修改时间
Last-Modified: Wed, 01 Jan 2025 00:00:00 GMT  # 响应头
If-Modified-Since: Wed, 01 Jan 2025 00:00:00 GMT  # 请求头
# 返回 304 Not Modified 或 200 + 新内容

# 基于内容哈希（更精确）
ETag: "abc123"                    # 响应头
If-None-Match: "abc123"           # 请求头
```

### 3.3 缓存策略实践

```
# 静态资源（带哈希的文件名）
Cache-Control: max-age=31536000, immutable
# 例：app.a1b2c3.js, style.d4e5f6.css

# HTML 文件
Cache-Control: no-cache
# 每次协商，确保获取最新版本

# API 响应
Cache-Control: no-store
# 或 Cache-Control: max-age=60（短时间缓存）
```

## 4. Service Worker 缓存

```javascript
// sw.js
const CACHE_NAME = 'v1';
const ASSETS = ['/', '/index.html', '/style.css', '/app.js'];

// 安装：预缓存资源
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(ASSETS))
  );
});

// 请求拦截：缓存优先策略
self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then(cached => {
      return cached || fetch(event.request).then(response => {
        const clone = response.clone();
        caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone));
        return response;
      });
    })
  );
});
```

## 5. 常见状态码

```
200 OK                    # 成功
201 Created               # 创建成功
204 No Content            # 成功但无内容
301 Moved Permanently     # 永久重定向
302 Found                 # 临时重定向
304 Not Modified          # 协商缓存命中
400 Bad Request           # 请求参数错误
401 Unauthorized          # 未认证
403 Forbidden             # 无权限
404 Not Found             # 资源不存在
429 Too Many Requests     # 限流
500 Internal Server Error # 服务器错误
502 Bad Gateway           # 网关错误
503 Service Unavailable   # 服务不可用
```

<!-- version-check: HTTP/3 38.8% adoption (April 2026), checked 2026-04-27 -->

> 🔄 更新于 2026-04-27

## 6. HTTP/3 与 QUIC 2026 年现状

### 6.1 采用率

截至 2026 年 4 月，HTTP/3 已被约 **38.8%** 的网站采用，所有主流浏览器（Chrome、Firefox、Safari、Edge）均已支持。主要 CDN（Cloudflare、Fastly、AWS CloudFront）默认启用 HTTP/3。

> ⚠️ 待确认：38.8% 数据来源为单一第三方统计，建议以 [W3Techs HTTP/3 Usage](https://w3techs.com/technologies/details/ce-http3) 或 [Cloudflare Radar](https://radar.cloudflare.com) 为准定期复核。

来源：[HTTP/3 SEO Performance](https://blckalpaca.at/en/knowledge-base/seo-geo/technisches-seo/http3-performance)

### 6.2 QUIC 核心优势

```
TCP + TLS 1.3（HTTP/2）          QUIC（HTTP/3）
┌─────────────────────┐          ┌─────────────────────┐
│ TCP 握手 (1 RTT)     │          │ QUIC 握手 (0-1 RTT)  │
│ TLS 握手 (1-2 RTT)   │          │ 加密内置于传输层      │
│ 总计: 2-3 RTT        │          │ 总计: 0-1 RTT        │
│                     │          │                     │
│ 队头阻塞（TCP 层）   │          │ 无队头阻塞           │
│ 连接迁移需重建       │          │ 连接 ID 支持迁移     │
└─────────────────────┘          └─────────────────────┘
```

**性能改进**：
- 连接建立：0-RTT 恢复连接（已知服务器），1-RTT 新连接
- 多路复用：单个流丢包不影响其他流（消除 TCP 层队头阻塞）
- 连接迁移：Wi-Fi ↔ 4G/5G 切换时连接不中断
- Core Web Vitals：LCP 和 INP 均有可测量的改善

### 6.3 服务端配置

```nginx
# Nginx 1.25+ 启用 HTTP/3
server {
    listen 443 quic reuseport;  # QUIC/HTTP3
    listen 443 ssl;              # HTTP/2 回退

    ssl_certificate     /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # 告知浏览器支持 HTTP/3
    add_header Alt-Svc 'h3=":443"; ma=86400';
}
```

## 7. Speculation Rules API（预测性加载）

Speculation Rules API 让浏览器在用户点击前预渲染或预取即将导航的页面，实现近乎即时的页面切换。

来源：[Speculation Rules at Shopify](https://performance.shopify.com/blogs/blog/speculation-rules-at-shopify)

```html
<!-- 在 HTML 中声明预测规则 -->
<script type="speculationrules">
{
  "prerender": [
    {
      "where": { "href_matches": "/products/*" },
      "eagerness": "moderate"
    }
  ],
  "prefetch": [
    {
      "where": { "href_matches": "/blog/*" },
      "eagerness": "conservative"
    }
  ]
}
</script>

<!--
eagerness 级别：
- immediate：立即预渲染（适合确定性高的导航）
- eager：尽快预渲染
- moderate：悬停 200ms 后预渲染（推荐默认值）
- conservative：点击/触摸开始时预渲染
-->
```

**浏览器支持**：Chrome 121+、Edge 121+（基于 Chromium），Safari 和 Firefox 暂不支持。
## 🎬 推荐视频资源

- [Fireship - HTTP in 100 Seconds](https://www.youtube.com/watch?v=iYM2zFP3Zn0) — HTTP快速了解
- [Traversy Media - HTTP Crash Course](https://www.youtube.com/watch?v=iYM2zFP3Zn0) — HTTP速成
