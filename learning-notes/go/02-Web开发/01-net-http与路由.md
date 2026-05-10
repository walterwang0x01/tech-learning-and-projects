# net/http 与路由

> Author: Walter Wang

<!-- version-check: Go 1.26 net/http, ServeMux 1.22+ enhanced, checked 2026-05-10 -->

## 1. Go 1.22 让 net/http 变强

Go 1.22 大幅增强了 `net/http.ServeMux`，**很多项目不再需要 Gin/Echo 这种框架**：

```go
package main

import (
    "encoding/json"
    "log/slog"
    "net/http"
)

func main() {
    mux := http.NewServeMux()

    // 方法 + 路径匹配（1.22+）
    mux.HandleFunc("GET /users", listUsers)
    mux.HandleFunc("POST /users", createUser)

    // 路径参数（1.22+）
    mux.HandleFunc("GET /users/{id}", getUser)
    mux.HandleFunc("DELETE /users/{id}", deleteUser)

    // 通配符
    mux.HandleFunc("GET /files/{path...}", serveFile)

    // 主机匹配
    mux.HandleFunc("api.example.com/health", healthCheck)

    slog.Info("listening", "addr", ":8080")
    http.ListenAndServe(":8080", mux)
}

func getUser(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")  // 1.22+ 新 API
    json.NewEncoder(w).Encode(map[string]string{"id": id})
}
```

## 2. 路由匹配规则

```
具体优先：
  /users/{id}   match "GET /users/123"
  /users/list   match "GET /users/list"（不会 match {id}）

方法匹配：
  GET /users    只匹配 GET，其他方法返回 405

主机匹配：
  example.com/x  比 /x 更具体

通配符：
  /files/{path...}  贪婪匹配剩余路径
  /files/a/b/c     → path = "a/b/c"
```

## 3. 标准 Handler 模式

### 3.1 HandlerFunc

```go
func homeHandler(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "text/plain")
    w.WriteHeader(http.StatusOK)
    fmt.Fprintln(w, "Hello")
}
```

### 3.2 带状态的 Handler

```go
type UserHandler struct {
    svc *UserService
}

func (h *UserHandler) List(w http.ResponseWriter, r *http.Request) {
    users, err := h.svc.List(r.Context())
    if err != nil {
        http.Error(w, err.Error(), 500)
        return
    }
    writeJSON(w, 200, users)
}

// 注册
uh := &UserHandler{svc: service}
mux.HandleFunc("GET /users", uh.List)
```

## 4. 请求解析

### 4.1 JSON Body

```go
type CreateUserReq struct {
    Name  string `json:"name"`
    Email string `json:"email"`
}

func createUser(w http.ResponseWriter, r *http.Request) {
    // 限制 Body 大小（防 DoS）
    r.Body = http.MaxBytesReader(w, r.Body, 1<<20)  // 1 MB

    var req CreateUserReq
    dec := json.NewDecoder(r.Body)
    dec.DisallowUnknownFields()  // 严格模式：未知字段报错
    if err := dec.Decode(&req); err != nil {
        http.Error(w, "invalid JSON: "+err.Error(), 400)
        return
    }

    // 验证
    if req.Name == "" {
        http.Error(w, "name is required", 400)
        return
    }

    // ...
}
```

### 4.2 Query 参数

```go
func search(w http.ResponseWriter, r *http.Request) {
    q := r.URL.Query().Get("q")
    page, _ := strconv.Atoi(r.URL.Query().Get("page"))
    // ...
}
```

### 4.3 Form 数据

```go
func login(w http.ResponseWriter, r *http.Request) {
    if err := r.ParseForm(); err != nil {
        http.Error(w, err.Error(), 400)
        return
    }
    username := r.FormValue("username")
    password := r.FormValue("password")
    // ...
}
```

### 4.4 文件上传

```go
func upload(w http.ResponseWriter, r *http.Request) {
    r.Body = http.MaxBytesReader(w, r.Body, 10<<20)  // 10 MB

    if err := r.ParseMultipartForm(10 << 20); err != nil {
        http.Error(w, err.Error(), 400)
        return
    }

    file, header, err := r.FormFile("file")
    if err != nil {
        http.Error(w, err.Error(), 400)
        return
    }
    defer file.Close()

    slog.Info("upload", "filename", header.Filename, "size", header.Size)

    // ... 保存
}
```

## 5. 响应

```go
// 辅助函数：统一 JSON 响应
func writeJSON(w http.ResponseWriter, status int, data any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(data)
}

// 错误响应
func writeError(w http.ResponseWriter, status int, msg string) {
    writeJSON(w, status, map[string]string{"error": msg})
}

// 使用
func getUser(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")
    user, err := svc.Get(r.Context(), id)
    if err != nil {
        if errors.Is(err, ErrNotFound) {
            writeError(w, 404, "user not found")
            return
        }
        writeError(w, 500, "internal error")
        return
    }
    writeJSON(w, 200, user)
}
```

## 6. 中间件

```go
// 中间件签名
type Middleware func(http.Handler) http.Handler

// 日志中间件
func loggingMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        start := time.Now()
        wrapped := &statusWriter{ResponseWriter: w, status: 200}
        next.ServeHTTP(wrapped, r)

        slog.InfoContext(r.Context(), "request",
            "method", r.Method,
            "path", r.URL.Path,
            "status", wrapped.status,
            "duration_ms", time.Since(start).Milliseconds(),
        )
    })
}

type statusWriter struct {
    http.ResponseWriter
    status int
}

func (w *statusWriter) WriteHeader(s int) {
    w.status = s
    w.ResponseWriter.WriteHeader(s)
}

// 认证中间件
func authMiddleware(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        token := r.Header.Get("Authorization")
        if token == "" {
            writeError(w, 401, "unauthorized")
            return
        }
        userID, err := verifyToken(token)
        if err != nil {
            writeError(w, 401, "invalid token")
            return
        }
        ctx := context.WithValue(r.Context(), userKey, userID)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

// 组合中间件
func chain(h http.Handler, mws ...Middleware) http.Handler {
    for i := len(mws) - 1; i >= 0; i-- {
        h = mws[i](h)
    }
    return h
}

// 使用
mux := http.NewServeMux()
mux.HandleFunc("GET /users", listUsers)
mux.HandleFunc("GET /health", health)

handler := chain(mux, loggingMiddleware, recoveryMiddleware, corsMiddleware)
http.ListenAndServe(":8080", handler)
```

## 7. Graceful Shutdown

```go
func main() {
    mux := http.NewServeMux()
    // ... 路由注册

    srv := &http.Server{
        Addr:         ":8080",
        Handler:      mux,
        ReadTimeout:  10 * time.Second,
        WriteTimeout: 10 * time.Second,
        IdleTimeout:  60 * time.Second,
    }

    go func() {
        if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
            slog.Error("server", "err", err)
            os.Exit(1)
        }
    }()

    // 等待信号
    sig := make(chan os.Signal, 1)
    signal.Notify(sig, os.Interrupt, syscall.SIGTERM)
    <-sig

    slog.Info("shutting down")
    ctx, cancel := context.WithTimeout(context.Background(), 25*time.Second)
    defer cancel()

    if err := srv.Shutdown(ctx); err != nil {
        slog.Error("shutdown", "err", err)
    }
    slog.Info("shutdown complete")
}
```

## 8. HTTP 客户端

```go
// 不要用 http.DefaultClient（没有超时！）
var client = &http.Client{
    Timeout: 10 * time.Second,
    Transport: &http.Transport{
        MaxIdleConns:        100,
        MaxIdleConnsPerHost: 10,
        IdleConnTimeout:     90 * time.Second,
    },
}

// 使用
req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
req.Header.Set("Authorization", "Bearer xxx")

resp, err := client.Do(req)
if err != nil {
    return fmt.Errorf("request: %w", err)
}
defer resp.Body.Close()

if resp.StatusCode >= 400 {
    return fmt.Errorf("bad status: %d", resp.StatusCode)
}

var result MyResult
if err := json.NewDecoder(resp.Body).Decode(&result); err != nil {
    return fmt.Errorf("decode: %w", err)
}
```

## 9. 反模式

```
❌ 不设置 HTTP Server timeout
   → 慢客户端把连接全占
   ✅ ReadTimeout + WriteTimeout + IdleTimeout

❌ 不 Close response body
   → 连接泄漏
   ✅ defer resp.Body.Close()

❌ 用 http.DefaultClient 做生产请求
   → 无超时，无连接池调优
   ✅ 自建 Client

❌ 不限制 Body 大小
   → DoS 风险
   ✅ http.MaxBytesReader

❌ handler 里起 goroutine 不管
   → 请求已返回但 goroutine 还跑
   ✅ 异步任务用消息队列 / Worker
```

## 10. 什么时候还需要 Gin/Echo

2022 年之前：一定需要（标准库路由弱）
2022-2026：越来越不需要

```
Gin/Echo 还有的优势：
├─ 更友好的 Context（请求级数据、绑定、验证内置）
├─ 中间件生态丰富
├─ 更多 API 风格：route groups、more）
└─ 团队熟悉，招人快

net/http 够用的场景：
├─ 简单 API
├─ 小团队
├─ 对依赖控制严格
└─ 追求极致性能
```

## 📖 参考资料

- [net/http 包文档](https://pkg.go.dev/net/http)
- [Go 1.22 ServeMux 增强](https://go.dev/blog/routing-enhancements)
- [Writing Web Applications - Go 官方](https://go.dev/doc/articles/wiki/)
- [Let's Go - Alex Edwards](https://lets-go.alexedwards.net/)
