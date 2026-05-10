# Context 与取消传播

> Author: Walter Wang

<!-- version-check: Go context package, checked 2026-05-10 -->

## 1. Context 的四个用途

```
context.Context 是 Go 的"请求域"基础设施：
├─ Deadline / Timeout：自动超时
├─ Cancellation：取消信号向下传播
├─ Value：请求域数据（trace_id、user_id）
└─ Done channel：接收取消信号
```

**黄金法则**：任何可能长时间运行或调用下游的函数，第一个参数必须是 `ctx context.Context`。

## 2. 四种 Context

```go
// 根 Context
ctx := context.Background()  // 入口处用（main、init）
ctx := context.TODO()        // 占位，以后补

// 超时
ctx, cancel := context.WithTimeout(parent, 5*time.Second)
defer cancel()

// Deadline（绝对时间）
ctx, cancel := context.WithDeadline(parent, time.Now().Add(time.Hour))
defer cancel()

// 可取消（手动取消）
ctx, cancel := context.WithCancel(parent)
defer cancel()

// Value
ctx := context.WithValue(parent, userKey, "alice")
```

**关键**：`cancel` 必须调用，否则内存泄漏。用 `defer cancel()` 是惯例。

## 3. 在函数间传递

```go
func handler(w http.ResponseWriter, r *http.Request) {
    ctx := r.Context()  // HTTP Server 已经给了一个 context

    // 5 秒超时
    ctx, cancel := context.WithTimeout(ctx, 5*time.Second)
    defer cancel()

    result, err := service.DoSomething(ctx, ...)
    if err != nil {
        // ...
    }
    // ...
}

func (s *Service) DoSomething(ctx context.Context, ...) (Result, error) {
    // 传给下游
    data, err := s.repo.Query(ctx, ...)

    // 传给 HTTP 客户端
    req, _ := http.NewRequestWithContext(ctx, "GET", url, nil)
    resp, err := s.httpClient.Do(req)

    // 传给 DB
    rows, err := s.db.QueryContext(ctx, sql, args...)

    return ..., err
}
```

**任何外部调用（DB / Redis / HTTP / gRPC）都必须接受 context**。否则服务关闭时下游操作无法中断，出现"卡死"。

## 4. 监听 Done

长循环或阻塞操作要显式监听：

```go
func worker(ctx context.Context, jobs <-chan Job) {
    for {
        select {
        case <-ctx.Done():
            slog.Info("worker stopped", "reason", ctx.Err())
            return
        case job := <-jobs:
            process(job)
        }
    }
}

// 在长计算中定期检查
func compute(ctx context.Context, data []int) (int, error) {
    sum := 0
    for i, v := range data {
        if i%1000 == 0 {
            select {
            case <-ctx.Done():
                return 0, ctx.Err()
            default:
            }
        }
        sum += v
    }
    return sum, nil
}
```

## 5. ctx.Err() 判断原因

```go
select {
case <-ctx.Done():
    switch ctx.Err() {
    case context.DeadlineExceeded:
        return errors.New("operation timeout")
    case context.Canceled:
        return errors.New("operation canceled")
    }
case result := <-ch:
    return result
}

// 等价写法（Go 1.20+）
if ctx.Err() != nil {
    if errors.Is(ctx.Err(), context.DeadlineExceeded) {
        // 超时
    }
}
```

## 6. Context Value 的正确用法

```go
// ✅ 定义类型安全的 Key（避免字符串碰撞）
type ctxKey string

const userKey ctxKey = "user"

// 写
ctx := context.WithValue(parent, userKey, user)

// 读
user, ok := ctx.Value(userKey).(*User)
if !ok {
    // ...
}

// ❌ 不要用 Context 传业务参数
// context.Value 只适合请求域元数据：trace_id、user_id、locale
// 业务参数通过函数参数传
```

## 7. 与 errgroup 协同

```go
import "golang.org/x/sync/errgroup"

func fetchData(ctx context.Context, urls []string) error {
    g, ctx := errgroup.WithContext(ctx)
    // errgroup 会在任何 goroutine 出错时取消 ctx

    for _, url := range urls {
        url := url
        g.Go(func() error {
            return fetchOne(ctx, url)  // ctx 传到下游
        })
    }
    return g.Wait()
}
```

## 8. HTTP 客户端的 Context

```go
// ✅ 用 NewRequestWithContext
req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
resp, err := http.DefaultClient.Do(req)

// 服务端：r.Context() 在客户端断开连接时自动取消
func handler(w http.ResponseWriter, r *http.Request) {
    // 用户关闭浏览器 → r.Context().Done() 触发
    result, err := longQuery(r.Context())
    // ...
}
```

## 9. 数据库 Context

```go
// database/sql 标准库
rows, err := db.QueryContext(ctx, "SELECT * FROM users WHERE id = $1", id)
tx, err := db.BeginTx(ctx, nil)
_, err := tx.ExecContext(ctx, "UPDATE ...")

// GORM
db.WithContext(ctx).Find(&users)

// pgx
rows, err := pool.Query(ctx, "SELECT ...")
```

**所有数据库驱动都支持 Context**。不用 Context 的代码现在是反模式。

## 10. 容器终止信号

K8s 发 SIGTERM 后给应用 30 秒 graceful shutdown 时间。标准做法：

```go
func main() {
    ctx, stop := signal.NotifyContext(
        context.Background(),
        syscall.SIGINT, syscall.SIGTERM,
    )
    defer stop()

    srv := &http.Server{Addr: ":8080"}

    go func() {
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            slog.Error("server", "err", err)
        }
    }()

    <-ctx.Done()
    slog.Info("shutting down")

    shutdownCtx, cancel := context.WithTimeout(context.Background(), 25*time.Second)
    defer cancel()

    if err := srv.Shutdown(shutdownCtx); err != nil {
        slog.Error("shutdown", "err", err)
    }

    slog.Info("shutdown complete")
}
```

## 11. 常见反模式

```
❌ 把 Context 作为 struct 字段
type Service struct {
    ctx context.Context  // 不要这样做
}
→ Context 应该随请求传递，不是随对象

❌ 传 nil Context
svc.Do(nil, ...)
→ 改用 context.TODO() 或 context.Background()

❌ 忘记 cancel
ctx, _ := context.WithTimeout(parent, 5*time.Second)
→ 必须 defer cancel()

❌ 用 context.Value 传业务数据
ctx := context.WithValue(ctx, "orderID", "123")
→ 用函数参数传

❌ 设置了 Timeout 但下游没传
s.doSomething()  // 不传 ctx
→ 超时不起作用
```

## 12. 链路追踪的 Context

OpenTelemetry 也用 Context 传播 trace 信息：

```go
tracer := otel.Tracer("my-service")

ctx, span := tracer.Start(ctx, "operation-name")
defer span.End()

// ctx 继续传到下游，trace context 会自动注入到 HTTP header / gRPC metadata
```

这也是为什么**所有函数的第一个参数都要是 context**：既能超时，又能传递 Trace。

## 13. 生产检查清单

```
☐ 所有"可能慢"的函数首参是 ctx context.Context
☐ WithTimeout / WithCancel 都有对应的 defer cancel()
☐ 所有外部调用（DB/Redis/HTTP/gRPC）用 context 版本的 API
☐ 长循环中定期检查 ctx.Done()
☐ HTTP Handler 用 r.Context()
☐ main 用 signal.NotifyContext 监听 SIGTERM
☐ Graceful shutdown 有明确超时（通常 25-30s）
☐ Context.Value 只存请求域元数据
☐ 错误处理区分 DeadlineExceeded 和 Canceled
```

## 📖 参考资料

- [context package](https://pkg.go.dev/context)
- [Go Concurrency Patterns: Context](https://go.dev/blog/context)
- [Go Memory Model](https://go.dev/ref/mem)
