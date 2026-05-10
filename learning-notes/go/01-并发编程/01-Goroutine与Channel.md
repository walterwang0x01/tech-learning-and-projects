# Goroutine 与 Channel

> Author: Walter Wang

<!-- version-check: Go 1.26 concurrency primitives, checked 2026-05-10 -->

## 1. Goroutine 基础

Goroutine 是 Go 运行时管理的轻量级线程，启动只要 2KB 栈空间。

```go
// 启动 Goroutine
go doWork()

// 带参数
go process(data)

// 匿名函数
go func() {
    fmt.Println("in goroutine")
}()
```

**M:N 调度模型**：N 个 Goroutine 映射到 M 个 OS 线程（由 GOMAXPROCS 决定）。

```
┌──── Go Runtime 调度器 ────┐
│                            │
│  G  G  G  G  G  G  G       │  ← Goroutines
│   \ | / | \ | / | \        │
│    M     M     M           │  ← OS Threads
│    |     |     |           │
│    P     P     P           │  ← Processors (逻辑 CPU)
└────────────────────────────┘
```

## 2. Channel：Goroutine 间通信

```
Don't communicate by sharing memory;
share memory by communicating.
 — Rob Pike
```

```go
// 无缓冲 Channel（同步）
ch := make(chan int)

go func() {
    ch <- 42  // 阻塞直到被读
}()

v := <-ch  // 阻塞直到有值

// 有缓冲 Channel（异步）
ch := make(chan int, 10)

// 关闭 Channel
close(ch)

// 读取直到关闭（range）
for v := range ch {
    fmt.Println(v)
}

// 判断是否关闭
v, ok := <-ch
if !ok {
    // channel 已关闭且无缓冲值
}
```

**Channel 方向**（作为参数时的约束）：

```go
func send(ch chan<- int) {   // 只发送
    ch <- 1
}

func recv(ch <-chan int) {   // 只接收
    <-ch
}
```

## 3. select：多路复用

```go
select {
case v := <-ch1:
    // 从 ch1 收到
case ch2 <- v:
    // 发送到 ch2
case <-time.After(1 * time.Second):
    // 超时
case <-ctx.Done():
    // 上下文取消
default:
    // 所有 case 都不就绪（非阻塞）
}
```

**常见模式**：

```go
// 超时
select {
case result := <-ch:
    return result
case <-time.After(5 * time.Second):
    return errors.New("timeout")
}

// 取消
for {
    select {
    case <-ctx.Done():
        return ctx.Err()
    case work := <-workCh:
        process(work)
    }
}
```

## 4. 生产级并发模式

### 4.1 Worker Pool

```go
func main() {
    jobs := make(chan Job, 100)
    results := make(chan Result, 100)

    // 启动 10 个 worker
    var wg sync.WaitGroup
    for w := 1; w <= 10; w++ {
        wg.Add(1)
        go worker(w, jobs, results, &wg)
    }

    // 发送任务
    for _, j := range generateJobs() {
        jobs <- j
    }
    close(jobs)

    // 等所有 worker 完成后关闭 results
    go func() {
        wg.Wait()
        close(results)
    }()

    // 收集结果
    for r := range results {
        fmt.Println(r)
    }
}

func worker(id int, jobs <-chan Job, results chan<- Result, wg *sync.WaitGroup) {
    defer wg.Done()
    for j := range jobs {
        results <- process(j)
    }
}
```

### 4.2 Fan-out / Fan-in

```go
// Fan-out：一个输入 → 多个 worker
func fanOut(input <-chan int, workers int) []<-chan int {
    outputs := make([]<-chan int, workers)
    for i := 0; i < workers; i++ {
        out := make(chan int)
        outputs[i] = out
        go func() {
            defer close(out)
            for v := range input {
                out <- heavyWork(v)
            }
        }()
    }
    return outputs
}

// Fan-in：多个输入 → 一个输出
func fanIn(inputs ...<-chan int) <-chan int {
    out := make(chan int)
    var wg sync.WaitGroup

    for _, ch := range inputs {
        wg.Add(1)
        go func(c <-chan int) {
            defer wg.Done()
            for v := range c {
                out <- v
            }
        }(ch)
    }

    go func() {
        wg.Wait()
        close(out)
    }()
    return out
}
```

### 4.3 Pipeline

```go
// 阶段 1：生成
func generate(nums ...int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for _, n := range nums {
            out <- n
        }
    }()
    return out
}

// 阶段 2：转换
func square(in <-chan int) <-chan int {
    out := make(chan int)
    go func() {
        defer close(out)
        for n := range in {
            out <- n * n
        }
    }()
    return out
}

// 组合
for v := range square(square(generate(1, 2, 3, 4))) {
    fmt.Println(v)  // 1, 16, 81, 256
}
```

### 4.4 errgroup：并发 + 错误传播

```go
import "golang.org/x/sync/errgroup"

func fetchAll(ctx context.Context, urls []string) ([]string, error) {
    g, ctx := errgroup.WithContext(ctx)
    results := make([]string, len(urls))

    // 限制并发数（2026 年推荐）
    g.SetLimit(10)

    for i, url := range urls {
        i, url := i, url  // Go 1.22+ 不需要这一行，但老版本需要
        g.Go(func() error {
            data, err := fetch(ctx, url)
            if err != nil {
                return err  // 任何一个出错，其他会被取消
            }
            results[i] = data
            return nil
        })
    }

    if err := g.Wait(); err != nil {
        return nil, err
    }
    return results, nil
}
```

**2026 年最佳实践**：生产代码不用原始 `sync.WaitGroup`，用 `errgroup`。

## 5. Goroutine 泄漏排查

最常见的 Bug：Goroutine 启动后永远阻塞，无法退出。

```go
// ❌ 泄漏：如果没人读 ch，goroutine 永远阻塞
func leak() {
    ch := make(chan int)
    go func() {
        val := <-ch
        fmt.Println(val)
    }()
    // 函数返回，channel 没人写，goroutine 永远等
}

// ✅ 带超时或 context
func noLeak(ctx context.Context) {
    ch := make(chan int)
    go func() {
        select {
        case val := <-ch:
            fmt.Println(val)
        case <-ctx.Done():
            return  // 可以退出
        }
    }()
}
```

**排查工具**：

```go
// 1. runtime.NumGoroutine()：监控数量
fmt.Println("goroutines:", runtime.NumGoroutine())

// 2. pprof 看每个 goroutine 的栈
import _ "net/http/pprof"
// 访问 /debug/pprof/goroutine?debug=2

// 3. 测试中用 goleak
import "go.uber.org/goleak"

func TestFoo(t *testing.T) {
    defer goleak.VerifyNone(t)  // 测试结束时检查无泄漏
    // ... 测试
}
```

## 6. 并发安全数据结构

```go
// sync.Mutex：互斥锁
var mu sync.Mutex
mu.Lock()
defer mu.Unlock()
// 临界区

// sync.RWMutex：读写锁（读多写少）
var rw sync.RWMutex
rw.RLock()   // 读锁
rw.RUnlock()
rw.Lock()    // 写锁

// sync.Map：并发安全 map
var m sync.Map
m.Store("key", "value")
v, ok := m.Load("key")
m.Delete("key")
m.Range(func(k, v any) bool { return true })

// sync.Once：只执行一次
var once sync.Once
once.Do(func() {
    // 初始化逻辑
})

// atomic 原子操作
var counter int64
atomic.AddInt64(&counter, 1)
val := atomic.LoadInt64(&counter)
```

## 7. Race Detector

Go 内置数据竞争检测，开发时必开：

```bash
# 运行
go run -race main.go

# 测试
go test -race ./...

# 构建（仅开发，性能开销大）
go build -race
```

**生产代码上线前**必须 `go test -race` 通过。

## 8. Channel vs Mutex：怎么选

```
用 Channel：
├─ 多个 goroutine 之间传递数据所有权
├─ 分发任务和收集结果
├─ 取消信号（close channel）
└─ 构建 pipeline

用 Mutex：
├─ 保护共享状态的读写
├─ 计数器、缓存、连接池
├─ 避免需要序列化顺序的场景
└─ 性能敏感场景（Channel 有开销）

经验法则：
  先用 Channel 表达结构，性能不够再换 Mutex
```

## 9. 常见陷阱

```
并发陷阱：
├─ 忘记 close channel → reader for range 永远阻塞
├─ 向已关闭的 channel 写 → panic
├─ 对 nil channel 读写 → 永久阻塞
├─ for v := range ch 在 goroutine 内，可能泄漏
├─ 变量在循环中被 goroutine 捕获（Go < 1.22 的经典坑）
├─ WaitGroup 的 Add 要在 goroutine 外
├─ Mutex 不可复制（传入函数时要用指针）
└─ 没关注 GOMAXPROCS（容器中是关键）
```

## 10. 2026 年特性：容器感知 GOMAXPROCS

Go 1.25 起，默认会读取 cgroup 设置的 CPU 限额。

```bash
# K8s 里 limits.cpu = 2
# 以前：GOMAXPROCS = 宿主机核数（比如 32）→ 过度调度
# 1.25+：GOMAXPROCS = 2 → 正好
```

所以 2026 年在 K8s 中运行 Go 程序，不用再手动设 `GOMAXPROCS` 环境变量。

## 📖 参考资料

- [Go Concurrency Patterns - Rob Pike](https://go.dev/talks/2012/concurrency.slide)
- [Advanced Go Concurrency Patterns](https://go.dev/talks/2013/advconc.slide)
- [Go Memory Model](https://go.dev/ref/mem)
- [errgroup](https://pkg.go.dev/golang.org/x/sync/errgroup)
- [Go 1.25 Container-aware GOMAXPROCS](https://go.dev/doc/go1.25)
