# CDN 与静态资源管理
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. CDN 原理

<!-- version-check: HTTP/2/3 多路复用时代部署模式, checked 2026-05-19 -->
<!-- 修复于 2026-05-19: 补充 version-check -->

```
用户请求 → DNS 解析 → CDN 边缘节点
  ├── 缓存命中 → 直接返回（快）
  └── 缓存未命中 → 回源到源站 → 缓存 → 返回
```

## 2. 资源哈希与缓存策略

```javascript
// Vite 默认输出带哈希的文件名
// dist/assets/index-a1b2c3d4.js
// dist/assets/style-e5f6g7h8.css

// 缓存策略：
// HTML → no-cache（每次协商）
// JS/CSS/图片（带哈希）→ max-age=31536000, immutable（永久缓存）
// API → no-store 或短时间缓存
```

## 3. 多环境资源管理

```javascript
// 根据环境使用不同的 CDN 域名
const CDN_MAP = {
  development: '',
  staging: 'https://cdn-staging.example.com',
  production: 'https://cdn.example.com',
};

// vite.config.ts
export default defineConfig({
  base: CDN_MAP[process.env.NODE_ENV] || '/',
});
```

## 4. 资源预热

```bash
# 部署后主动推送资源到 CDN 边缘节点
# 避免首批用户请求回源导致的延迟

# 常见 CDN 提供预热 API
# 阿里云 CDN、CloudFront、Cloudflare 等
```

## 5. 域名分片（HTTP/1.1，已不推荐）

> ⚠️ 2026 年提示：HTTP/2 和 HTTP/3 已被 95%+ 现代浏览器支持（HTTP/3 站点采用率约 38.8%，需第三方数据复核）。**新项目不应再使用域名分片**，多路复用已彻底解决并发连接限制。
<!-- 修复于 2026-05-19: 标注域名分片为反模式，避免新项目误用 -->

```
# HTTP/1.1 下浏览器对同一域名有并发连接限制（6个）
# 历史上的做法：使用多个域名分散请求

cdn1.example.com → JS 文件
cdn2.example.com → CSS 文件
cdn3.example.com → 图片资源

# HTTP/2 / HTTP/3 多路复用，单连接即可并发请求
# 域名分片反而引入额外 DNS / TLS 握手成本，性能更差
```
