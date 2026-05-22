# Web 安全 XSS / CSRF
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. XSS（跨站脚本攻击）

### 1.1 类型

```
存储型 XSS：恶意脚本存储在服务器（数据库），其他用户访问时执行
反射型 XSS：恶意脚本在 URL 参数中，服务器返回时执行
DOM 型 XSS：恶意脚本通过 DOM 操作注入，不经过服务器
```

### 1.2 防御

```javascript
// 1. 输出编码（最基本的防御）
function escapeHtml(str) {
  const map = { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#x27;' };
  return str.replace(/[&<>"']/g, (c) => map[c]);
}

// 2. React/Vue 默认转义（安全）
<div>{userInput}</div>  // React 自动转义
<div>{{ userInput }}</div>  // Vue 自动转义

// ⚠️ 危险操作（避免使用）
<div dangerouslySetInnerHTML={{ __html: userInput }} />  // React
<div v-html="userInput"></div>  // Vue

// 3. CSP（Content Security Policy）
// HTTP 响应头
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-abc123'; style-src 'self' 'unsafe-inline'

// 4. HttpOnly Cookie（防止 JS 读取）
Set-Cookie: token=abc; HttpOnly; Secure; SameSite=Strict
```

## 2. CSRF（跨站请求伪造）

### 2.1 原理

```
1. 用户登录 A 网站，浏览器保存 Cookie
2. 用户访问恶意网站 B
3. B 网站向 A 发起请求，浏览器自动携带 A 的 Cookie
4. A 网站无法区分是用户还是恶意请求
```

### 2.2 防御

```javascript
// 1. CSRF Token
// 服务端生成 Token，嵌入表单或请求头
<input type="hidden" name="_csrf" value="token123">

// 2. SameSite Cookie
Set-Cookie: token=abc; SameSite=Strict  // 完全禁止跨站携带
Set-Cookie: token=abc; SameSite=Lax     // 允许导航跳转携带（默认）

// 3. 验证 Origin / Referer 头
if (req.headers.origin !== 'https://mysite.com') {
  return res.status(403).json({ error: 'Forbidden' });
}

// 4. 双重 Cookie 验证
// Cookie 中设置 csrf_token，请求头中也携带，服务端比对
```

## 3. 其他安全措施

```javascript
// CORS 跨域配置
app.use(cors({
  origin: ['https://mysite.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
}));

// 点击劫持防御
X-Frame-Options: DENY
Content-Security-Policy: frame-ancestors 'none'

// 子资源完整性（SRI）
<script src="https://cdn.example.com/lib.js"
  integrity="sha384-oqVuAfXRKap7fdgcCY5uykM6+R9GqQ8K/uxy9rx7HNQlGYl1kPzQho1wx4JwY8w"
  crossorigin="anonymous">
</script>

// 安全响应头
Strict-Transport-Security: max-age=31536000; includeSubDomains  // HSTS
X-Content-Type-Options: nosniff
X-XSS-Protection: 0  // 现代浏览器建议关闭，使用 CSP 替代
Referrer-Policy: strict-origin-when-cross-origin
```

<!-- version-check: Trusted Types Baseline 2026-02, CSP Level 3, React RSC CVE-2025-55182, Next.js 16.2.5, npm Shai-Hulud 2026-05-19, checked 2026-05-21 -->

> 🔄 更新于 2026-04-27

## 4. Trusted Types API（2026 年全浏览器支持）

Trusted Types 自 2026 年 2 月起成为 **Baseline Newly Available**，所有主流浏览器均已支持。它从根本上防止 DOM XSS：不再依赖开发者"记得转义"，而是让浏览器强制要求只有经过策略处理的类型化值才能传入危险 DOM API。

来源：[MDN Trusted Types API](https://developer.mozilla.org/docs/Web/API/Trusted_Types_API)

```javascript
// 1. 启用 Trusted Types（CSP 头）
// Content-Security-Policy: trusted-types myPolicy; require-trusted-types-for 'script'

// 2. 定义策略
const policy = trustedTypes.createPolicy('myPolicy', {
  createHTML: (input) => {
    // 在这里做安全处理（转义、白名单过滤等）
    return DOMPurify.sanitize(input);
  },
  createScriptURL: (input) => {
    // 只允许可信域名的脚本
    const url = new URL(input);
    if (url.origin === 'https://cdn.mysite.com') return input;
    throw new TypeError('不允许的脚本来源');
  }
});

// 3. 使用策略创建可信值
element.innerHTML = policy.createHTML(userInput);  // ✅ 通过策略
element.innerHTML = userInput;                      // ❌ 浏览器拒绝

// Trusted Types 类型：
// TrustedHTML    → innerHTML, outerHTML, insertAdjacentHTML
// TrustedScript  → eval(), setTimeout(string)
// TrustedScriptURL → script.src, Worker()
```

来源：[Stop Sanitizing HTML: Use Trusted Types](https://loke.dev/blog/stop-sanitizing-html-use-trusted-types)

### CSP Level 3 更新

W3C CSP Level 3 规范在 2026 年持续更新，关键变化：

```
# 2026 年推荐的安全响应头组合
Content-Security-Policy: default-src 'self'; script-src 'self' 'nonce-{random}'; style-src 'self' 'unsafe-inline'; trusted-types myPolicy; require-trusted-types-for 'script'
Strict-Transport-Security: max-age=63072000; includeSubDomains; preload
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Permissions-Policy: camera=(), microphone=(), geolocation=()
```

来源：[W3C CSP Level 3](https://www.w3.org/TR/CSP/)
> 🔄 更新于 2026-05-21

<!-- version-check: React 19.x.6/19.1.7/19.2.6 (CVE-2026-23870 fix), Next.js 16.2.5/15.5.16, checked 2026-05-22 -->

## 5. React Server Components RCE 漏洞（CVE-2025-55182）

2025 年 12 月 3 日披露的 **CVSS 10.0** 严重漏洞，影响 React 19 的 Server Components "Flight" 协议。攻击者可通过向 Server Function 端点发送恶意构造的 HTTP 请求，实现未认证远程代码执行（Pre-auth RCE）。

**受影响版本**：React 19.0.0、19.1.0、19.1.1、19.2.0（包含 react-server-dom-webpack、react-server-dom-turbopack、react-server-dom-parcel）

**修复版本**：19.0.1、19.1.2、19.2.1（RCE 修复）→ 19.0.4、19.1.5、19.2.4（后续 DoS + 源码泄露修复）→ **19.x.6**（最新安全版本）

来源：[React 官方安全公告](https://react.dev/blog/2025/12/03/critical-security-vulnerability-in-react-server-components)、[AWS 安全公告](https://aws.amazon.com/security/security-bulletins/rss/aws-2025-030/)

```javascript
// 漏洞原理：Flight 协议不安全地反序列化 HTTP 请求中的 payload
// 攻击者可以通过不安全的原型引用注入恶意代码

// ⚠️ 检查你的项目是否受影响：
// 1. 使用 React 19 + Server Components / Server Functions
// 2. 使用 Next.js App Router（内置 RSC）
// 3. 使用 react-server-dom-* 包

// 修复方式：立即升级
// npm install react@latest react-dom@latest
// npm install react-server-dom-webpack@latest  # 如果使用
```

### Next.js May 2026 安全发布

Vercel 于 2026-05-07 发布协调安全更新，修复 **13 个安全公告**，覆盖 DoS、中间件绕过、SSRF、缓存投毒、XSS 等多种攻击面。

**修复版本**：Next.js 15.5.16 / 16.2.5

**三个高危漏洞**：

| CVE | 类型 | 影响 |
|-----|------|------|
| CVE-2026-44574 | 中间件/代理绕过 | 动态路由参数注入绕过认证中间件 |
| CVE-2026-23870 | RSC DoS（上游 React 漏洞） | 攻击者通过精心构造的 HTTP 请求触发服务端 OOM 或 CPU 耗尽 |
| CVE-2026-44581 | App Router XSS | 利用 CSP nonce 机制绕过 CSP 防护 |

来源：[Vercel Changelog](https://vercel.com/changelog/next-js-may-2026-security-release)、[Cloudflare WAF 公告](https://developers.cloudflare.com/changelog/post/2026-05-06-react-nextjs-vulnerabilities/)、[CyberKendra - 12 Security Flaws](https://www.cyberkendra.com/2026/05/react-and-nextjs-hit-with-12-security.html)

> 🔄 更新于 2026-05-22

### CVE-2026-23870 React Server Components DoS

2026-05-06 与 Next.js 安全更新同步披露的高危漏洞，是 CVE-2025-55182 后续不完整修复链上的最新一环。攻击者无需认证即可向 Server Function 端点发送特制 HTTP 请求，触发反序列化阶段的 CPU 耗尽或 OOM。

**修复版本**：`react-server-dom-webpack` / `react-server-dom-parcel` / `react-server-dom-turbopack` **19.0.6 / 19.1.7 / 19.2.6**

```bash
# 检查并升级 RSC 相关包
npm ls react-server-dom-webpack react-server-dom-parcel react-server-dom-turbopack
npm install react-server-dom-webpack@latest

# Next.js 用户：升级 Next.js 即可包含上游修复
npm install next@latest
```

来源：[NVD - CVE-2026-23870](https://nvd.nist.gov/vuln/detail/CVE-2026-23870)、[GHSA-83fc-fqcc-2hmg](https://github.com/facebook/react/security/advisories/GHSA-83fc-fqcc-2hmg)、[ZeroPath 漏洞分析](https://zeropath.com/blog/cve-2026-23870-react-server-components-dos)

```bash
# 立即升级
npm install next@latest

# 如果无法立即升级，临时缓解措施：
# 1. AWS WAF：启用 AWSManagedRulesKnownBadInputsRuleSet v1.24+
# 2. Cloudflare WAF：已自动部署规则
# 3. 自定义 WAF：检测 Flight 协议异常 payload
```

**影响范围**：所有使用 App Router、Pages Router、中间件、代理逻辑、WebSocket 升级、缓存层、Server Functions、Cache Components、Image Optimization API 的 Next.js 应用。

来源：[InfoWorld](https://www.infoworld.com/article/4100641/developers-urged-to-immediately-upgrade-react-next-js.html)、[CyberKendra](https://www.cyberkendra.com/2026/05/react-and-nextjs-hit-with-12-security.html)

### npm 供应链攻击：Mini Shai-Hulud（2026-05-19）

npm 账户 `atool`（i@hust.cc）被入侵，攻击者在 22 分钟内向 317+ 个包发布了 637 个恶意版本。受影响包的周下载量合计约 **1600 万**。

**受影响的高流量包**：

| 包名 | 月下载量 |
|------|---------|
| size-sensor | 420 万 |
| echarts-for-react | 380 万 |
| @antv/scale | 220 万 |
| timeago.js | 115 万 |
| @antv/g2, g6, x6, l7, s2, f2 | 数百万 |

**应对措施**：

```bash
# 1. 检查项目是否使用受影响的包
npm ls size-sensor echarts-for-react timeago.js

# 2. 锁定已知安全版本（使用 lockfile）
# 确保 package-lock.json 或 pnpm-lock.yaml 已提交到 Git

# 3. 使用 Socket.dev 或 npm audit 检查
npm audit

# 4. 如果已安装恶意版本，立即降级到攻击前的版本
# 恶意版本已被 npm 撤回，但本地缓存可能仍存在
```

来源：[The Register](https://www.theregister.com/cyber-crime/2026/05/19/shai-hulud-keeps-burrowing-314-npm-packages-infected-after-another-account-compromise/5242601)、[SafeDep](https://safedep.io/mini-shai-hulud-strikes-again-314-npm-packages-compromised/)、[SecurityWeek](https://www.securityweek.com/over-320-npm-packages-hit-by-fresh-mini-shai-hulud-supply-chain-attack/)

## 🎬 推荐视频资源

- [Fireship - Web Security in 100 Seconds](https://www.youtube.com/watch?v=4YOpILi9Oxs) — Web安全快速了解
- [Computerphile - Cross Site Scripting](https://www.youtube.com/watch?v=L5l9lSnNMxg) — XSS详解
