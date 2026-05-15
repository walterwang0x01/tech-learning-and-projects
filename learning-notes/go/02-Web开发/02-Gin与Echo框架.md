# Gin 与 Echo 框架

> Author: Walter Wang

<!-- version-check: Gin 1.12.0 (2026-03), Echo 5.x, Fiber 2.53, Chi 5.x, checked 2026-05-15 -->

## 1. Go Web 框架全景

```
2026 年主流 Web 框架：
├─ net/http（标准库）         简洁、零依赖，大型项目可用
├─ Chi                      最接近标准库的 idiomatic 选择
├─ Gin                      最流行，中间件生态丰富
├─ Echo                     API 更优雅，内置功能多
├─ Fiber                    基于 fasthttp，性能最高（但生态稍小）
└─ Huma / Fuego             声明式 OpenAPI 优先（2026 新趋势）
```

**选型建议**：
- 新项目、重视标准库兼容：**Chi** 或 **net/http**（Go 1.22+ 路由已经很强）
- 团队熟悉 Express 风格：**Gin** 或 **Echo**
- 极致性能：**Fiber**
- API First：**Huma**

> 🔄 更新于 2026-05-15
>
> **JetBrains 2025 Go Developer Ecosystem 报告**给出的市场份额（2025 年底数据）：
>
> | 框架 | 市场份额 | GitHub Stars（2026-05） | 状态 |
> | ---- | -------- | ----------------------- | ---- |
> | Gin | 48% | 75K+ | 事实标准 |
> | Gorilla | 17% | — | 项目已重启维护 |
> | Echo | 16% | 30K+ | 企业方向 |
> | Fiber | 11% | — | 性能优先 |
>
> 数据来源：[Tech Insider — Gin Golang Tutorial 2026](https://tech-insider.org/gin-golang-tutorial-rest-api-2026/)、[JetBrains Blog — Popular Go Web Frameworks](https://blog.jetbrains.com/go/2026/04/28/popular-golang-web-frameworks/)
>
> **Gin v1.12.0**（2026-03）：基准测试在 Go 1.25.8 下完成，httprouter 路由器仍然是性能护城河（来源：[Gin Benchmarks](https://gin-gonic.com/en/docs/benchmarks/)）。
>
> **2026 年新趋势**：
>
> - **AI Gateway / Agent 中间层**成为 Gin 的新主战场（46% Go 开发者用于 web/API 服务，相当一部分接入 LLM）
> - **Huma / Fuego** 等 OpenAPI-first 框架在企业内部 API 场景增长，编译期生成 schema，减少手写 Swagger 注解
> - **Chi v5** 持续被 Cloud Native 项目（如 Tempo、Loki）采用，因为最贴近 `net/http`

## 2. net/http：Go 1.22+ 已经很够用

Go 1.22 改进了 `net/http.ServeMux`，支持路径参数和方法匹配：

```go
package main

import (
    "encoding/json"
    "log/slog"
    "net/http"
)

func main() {
    mux := http.NewServeMux()

    mux.HandleFunc("GET /users/{id}", getUser)
    mux.HandleFunc("POST /users", createUser)
    mux.HandleFunc("DELETE /users/{id}", deleteUser)

    slog.Info("server starting", "addr", ":8080")
    http.ListenAndServe(":8080", mux)
}

func getUser(w http.ResponseWriter, r *http.Request) {
    id := r.PathValue("id")  // Go 1.22+ 新 API
    w.Header().Set("Content-Type", "application/json")
    json.NewEncoder(w).Encode(map[string]string{"id": id})
}
```

很多简单的 API 服务不再需要框架。

## 3. Gin 实战

```bash
go get github.com/gin-gonic/gin
```

### 3.1 基础结构

```go
package main

import (
    "context"
    "errors"
    "log/slog"
    "net/http"
    "os/signal"
    "syscall"
    "time"

    "github.com/gin-gonic/gin"
)

func main() {
    r := gin.New()
    r.Use(gin.Recovery(), slogMiddleware())

    // 分组路由
    v1 := r.Group("/api/v1")
    {
        v1.GET("/users/:id", getUser)
        v1.POST("/users", createUser)

        // 需要鉴权的组
        auth := v1.Group("/", authMiddleware())
        auth.DELETE("/users/:id", deleteUser)
    }

    // Graceful Shutdown
    srv := &http.Server{
        Addr:    ":8080",
        Handler: r,
    }

    go func() {
        if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
            slog.Error("server error", "err", err)
        }
    }()

    ctx, stop := signal.NotifyContext(context.Background(), syscall.SIGINT, syscall.SIGTERM)
    defer stop()
    <-ctx.Done()

    shutdownCtx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    srv.Shutdown(shutdownCtx)
}
```

### 3.2 处理器与绑定

```go
type CreateUserReq struct {
    Name  string `json:"name" binding:"required,min=2,max=50"`
    Email string `json:"email" binding:"required,email"`
    Age   int    `json:"age" binding:"gte=0,lte=150"`
}

func createUser(c *gin.Context) {
    var req CreateUserReq
    if err := c.ShouldBindJSON(&req); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    user, err := userService.Create(c.Request.Context(), req.Name, req.Email, req.Age)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "internal error"})
        return
    }

    c.JSON(http.StatusCreated, user)
}

func getUser(c *gin.Context) {
    id := c.Param("id")           // 路径参数
    page := c.Query("page")        // 查询参数
    auth := c.GetHeader("Authorization")

    // ...
}
```

### 3.3 中间件

```go
func authMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        token := c.GetHeader("Authorization")
        if token == "" {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "unauthorized"})
            return
        }

        userID, err := verifyToken(token)
        if err != nil {
            c.AbortWithStatusJSON(http.StatusUnauthorized, gin.H{"error": "invalid token"})
            return
        }

        c.Set("user_id", userID)
        c.Next()  // 继续处理
    }
}

// 使用
func someHandler(c *gin.Context) {
    userID, _ := c.Get("user_id")
    // ...
}
```

### 3.4 结构化日志中间件（slog）

```go
func slogMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        c.Next()

        slog.InfoContext(c.Request.Context(), "request",
            "method", c.Request.Method,
            "path", c.Request.URL.Path,
            "status", c.Writer.Status(),
            "duration_ms", time.Since(start).Milliseconds(),
            "client_ip", c.ClientIP(),
        )
    }
}
```

## 4. 分层架构

```
┌────────── 推荐的分层 ──────────┐
│                                 │
│  Handler                        │
│  ├─ HTTP 处理、参数绑定           │
│  └─ 调用 Service                 │
│         ↓                       │
│  Service                        │
│  ├─ 业务逻辑                     │
│  └─ 调用 Repository + 外部服务   │
│         ↓                       │
│  Repository                     │
│  ├─ 数据持久化                   │
│  └─ 调用 DB / Cache             │
│         ↓                       │
│  Domain Model                   │
│  └─ 业务实体和规则               │
└─────────────────────────────────┘
```

### 目录示例

```go
// internal/domain/user.go
package domain

type User struct {
    ID    int64
    Name  string
    Email string
}

// internal/repository/user_repo.go
package repository

type UserRepository interface {
    FindByID(ctx context.Context, id int64) (*domain.User, error)
    Create(ctx context.Context, u *domain.User) error
}

type pgUserRepo struct {
    db *pgx.Conn
}

func NewUserRepo(db *pgx.Conn) UserRepository {
    return &pgUserRepo{db: db}
}

func (r *pgUserRepo) FindByID(ctx context.Context, id int64) (*domain.User, error) {
    var u domain.User
    err := r.db.QueryRow(ctx, "SELECT id, name, email FROM users WHERE id=$1", id).
        Scan(&u.ID, &u.Name, &u.Email)
    if err != nil {
        return nil, err
    }
    return &u, nil
}

// internal/service/user_service.go
package service

type UserService struct {
    repo repository.UserRepository
}

func (s *UserService) Create(ctx context.Context, name, email string, age int) (*domain.User, error) {
    u := &domain.User{Name: name, Email: email}
    if err := s.repo.Create(ctx, u); err != nil {
        return nil, fmt.Errorf("create user: %w", err)
    }
    return u, nil
}

// internal/handler/user_handler.go
package handler

type UserHandler struct {
    svc *service.UserService
}

func (h *UserHandler) Create(c *gin.Context) {
    // 见前面的例子
}
```

## 5. 数据库访问

### 5.1 pgx（PostgreSQL 推荐）

```go
import "github.com/jackc/pgx/v5/pgxpool"

pool, err := pgxpool.New(ctx, "postgres://user:pass@host/db")
if err != nil {
    log.Fatal(err)
}
defer pool.Close()

var name string
err = pool.QueryRow(ctx, "SELECT name FROM users WHERE id=$1", 1).Scan(&name)
```

### 5.2 sqlx（通用 SQL）

```go
import "github.com/jmoiron/sqlx"

db, _ := sqlx.Connect("postgres", dsn)

var users []User
err := db.SelectContext(ctx, &users, "SELECT * FROM users WHERE age > $1", 18)
```

### 5.3 ORM：sqlc（推荐）vs GORM

```
sqlc：SQL-first，从 SQL 生成类型安全代码
  ├─ 优点：零运行时开销，类型完全安全
  ├─ 缺点：需要写 SQL
  └─ 2026 年推荐

GORM：类似 Hibernate 的 ORM
  ├─ 优点：CRUD 快
  ├─ 缺点：性能、可读性都较弱
  └─ 遗留项目维护用
```

sqlc 示例：

```sql
-- queries.sql
-- name: GetUser :one
SELECT id, name, email FROM users WHERE id = $1;

-- name: CreateUser :one
INSERT INTO users (name, email) VALUES ($1, $2)
RETURNING id, name, email;
```

```bash
sqlc generate  # 生成类型安全的 Go 代码
```

```go
// 使用
user, err := q.GetUser(ctx, 1)
```

## 6. 生产级要点

### 6.1 配置管理

```go
// 推荐：viper 或 koanf + env
type Config struct {
    Server struct {
        Addr            string        `env:"SERVER_ADDR" envDefault:":8080"`
        ReadTimeout     time.Duration `env:"READ_TIMEOUT" envDefault:"10s"`
        WriteTimeout    time.Duration `env:"WRITE_TIMEOUT" envDefault:"10s"`
    }
    DB struct {
        URL      string `env:"DB_URL,required"`
        MaxConns int    `env:"DB_MAX_CONNS" envDefault:"25"`
    }
}
```

### 6.2 请求 ID 和 Trace

```go
func traceMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        reqID := c.GetHeader("X-Request-ID")
        if reqID == "" {
            reqID = uuid.NewString()
        }
        c.Writer.Header().Set("X-Request-ID", reqID)

        ctx := context.WithValue(c.Request.Context(), "request_id", reqID)
        c.Request = c.Request.WithContext(ctx)
        c.Next()
    }
}
```

生产环境建议用 **OpenTelemetry 自动埋点**（见 [observability-sre/02-OpenTelemetry完全指南.md](../../observability-sre/02-OpenTelemetry完全指南.md)）。

### 6.3 限流

```go
import "golang.org/x/time/rate"

func rateLimitMiddleware() gin.HandlerFunc {
    limiter := rate.NewLimiter(rate.Limit(100), 200)  // 100/s，突发 200
    return func(c *gin.Context) {
        if !limiter.Allow() {
            c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{"error": "rate limit"})
            return
        }
        c.Next()
    }
}
```

## 7. 生产检查清单

```
☐ graceful shutdown（监听 SIGTERM）
☐ 所有 handler 用 request context
☐ 每个外部调用都有 timeout
☐ 结构化日志（slog）
☐ 错误不直接暴露内部细节给客户端
☐ 请求绑定有 validate
☐ 限流 / 熔断配置
☐ OpenTelemetry 自动埋点
☐ Health 端点（/healthz、/readyz 区分）
☐ 配置从环境变量读取（12-factor）
☐ Docker 镜像多阶段构建（< 50MB）
```

## 📖 参考资料

- [Gin 官方文档](https://gin-gonic.com/)
- [Echo 官方文档](https://echo.labstack.com/)
- [sqlc](https://sqlc.dev/)
- [Huma - OpenAPI-first](https://huma.rocks/)
- [Go Web Examples](https://gowebexamples.com/)
