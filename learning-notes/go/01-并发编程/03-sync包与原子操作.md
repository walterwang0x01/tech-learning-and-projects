# sync 包与原子操作

> Author: Walter Wang

<!-- version-check: Go 1.26 sync, atomic 1.19+ generic, checked 2026-05-10 -->

## 1. 并发安全的三种选择

```
1. Channel（CSP 风格）
   share memory by communicating

2. sync 包（Mutex、RWMutex、WaitGroup、Once）
   传统的锁 + 同步原语

3. sync/atomic（无锁原子操作）
   计数器、状态机、flag
```

## 2. sync.Mutex

```go
import "sync"

type Counter struct {
    mu    sync.Mutex
    count int
}

func (c *Counter) Inc() {
    c.mu.Lock()
    defer c.mu.Unlock()
    c.count++
}

func (c *Counter) Get() int {
    c.mu.Lock()
    defer c.mu.Unlock()
    return c.count
}
```

**规则**：
- Mutex 零值可用，不要 copy
- 作为 struct 字段时放最前（内存对齐）
- defer Unlock 是 Go 惯例

## 3. sync.RWMutex

读多写少时用：

```go
type Cache struct {
    mu   sync.RWMutex
    data map[string]string
}

func (c *Cache) Get(key string) (string, bool) {
    c.mu.RLock()         // 读锁（可多个协程同时持有）
    defer c.mu.RUnlock()
    v, ok := c.data[key]
    return v, ok
}

func (c *Cache) Set(key, value string) {
    c.mu.Lock()          // 写锁（互斥）
    defer c.mu.Unlock()
    c.data[key] = value
}
```

**注意**：
- RWMutex 在**极度读多写少**时才明显优于 Mutex
- 读写比例 > 100:1 时才考虑
- 标准 map 不是并发安全，必须加锁

## 4. sync.WaitGroup

等待一组 goroutine 完成：

```go
var wg sync.WaitGroup

for i := 0; i < 10; i++ {
    wg.Add(1)
    go func(n int) {
        defer wg.Done()
        process(n)
    }(i)
}

wg.Wait()  // 阻塞到所有 goroutine 完成
```

**反模式**：
```go
// ❌ Add 在 goroutine 里
go func() {
    wg.Add(1)  // race condition：Wait 可能已经返回
    ...
}()

// ❌ 忘记 Done 导致永久阻塞
go func() {
    doWork()
    // 缺 wg.Done()
}()
```

## 5. sync.Once

只执行一次（经典单例模式）：

```go
var (
    once   sync.Once
    config *Config
)

func GetConfig() *Config {
    once.Do(func() {
        config = loadConfig()  // 只执行一次，线程安全
    })
    return config
}
```

Go 1.21+ 加了 `sync.OnceFunc`、`sync.OnceValue`、`sync.OnceValues`：

```go
var GetConfig = sync.OnceValue(func() *Config {
    return loadConfig()
})
```

## 6. sync.Map

Go 1.9+ 内置的并发安全 map。**不是 map 的通用替代**，只在特定场景有优势：

```go
var cache sync.Map

cache.Store("key", "value")
v, ok := cache.Load("key")
cache.Delete("key")
cache.Range(func(k, v any) bool {
    fmt.Println(k, v)
    return true   // false 停止
})
```

**使用场景**：
- 读多写少（一次写多次读）
- Key 集合稳定
- 多个 goroutine 读写**不同**的 key

不建议场景：
- 需要类型安全 → 用泛型的 sync.Map 包装
- 需要批量操作 → 标准 map + RWMutex

## 7. sync.Cond

条件变量（等某个条件满足后唤醒）：

```go
var (
    mu   sync.Mutex
    cond = sync.NewCond(&mu)
    data []int
)

// 消费者
func consumer() {
    mu.Lock()
    for len(data) == 0 {
        cond.Wait()  // 释放锁并等待
    }
    item := data[0]
    data = data[1:]
    mu.Unlock()
    process(item)
}

// 生产者
func producer(item int) {
    mu.Lock()
    data = append(data, item)
    mu.Unlock()
    cond.Signal()    // 唤醒一个等待者
    // 或 cond.Broadcast() 唤醒所有
}
```

**实际中**：Cond 很少用，用 Channel 替代通常更简单。

## 8. sync.Pool：对象复用

减少 GC 压力：

```go
var bufPool = sync.Pool{
    New: func() any {
        return new(bytes.Buffer)
    },
}

func handleRequest() {
    buf := bufPool.Get().(*bytes.Buffer)
    defer func() {
        buf.Reset()
        bufPool.Put(buf)
    }()

    // 使用 buf
}
```

**注意**：
- Pool 里的对象随时可能被 GC 回收
- 不要 Put 之后还用原来的引用
- 对象必须是自包含的（不要有指向外部的指针）
- 高并发下明显降低 GC

## 9. sync/atomic

无锁原子操作：

```go
import "sync/atomic"

var counter int64

// 在 goroutine 中
atomic.AddInt64(&counter, 1)

// 读
value := atomic.LoadInt64(&counter)

// CAS（compare-and-swap）
for {
    old := atomic.LoadInt64(&counter)
    new := computeNew(old)
    if atomic.CompareAndSwapInt64(&counter, old, new) {
        break
    }
}
```

## 10. Go 1.19+ 泛型原子类型

更好的 API：

```go
var counter atomic.Int64
counter.Add(1)
v := counter.Load()

var flag atomic.Bool
flag.Store(true)

// 泛型 Pointer
var cache atomic.Pointer[Config]
cache.Store(&Config{...})
cfg := cache.Load()
```

## 11. 选择哪个原语

```
简单 flag / counter：
  → atomic.Bool / atomic.Int64

保护共享数据（读写均衡）：
  → sync.Mutex

读多写少：
  → sync.RWMutex

一次初始化：
  → sync.OnceValue / sync.Once

等待多个 goroutine：
  → sync.WaitGroup / golang.org/x/sync/errgroup

多 goroutine 通信 / 信号 / 取消：
  → Channel / context.Context

对象复用减少 GC：
  → sync.Pool

分布式或复杂场景：
  → 分布式锁（Redis）/ 专用中间件
```

## 12. 生产检查清单

```
☐ 所有共享可变状态都有同步保护
☐ Lock 后 defer Unlock
☐ go test -race 跑通所有测试
☐ 热点路径用 atomic 替代 Mutex
☐ 读多写少用 RWMutex
☐ 高频分配的临时对象用 sync.Pool
☐ 单例用 sync.OnceValue（1.21+）
☐ 不在 goroutine 里 wg.Add
☐ Mutex 不跨 API 边界暴露
☐ 长操作不持锁（如 HTTP 请求）
```

## 13. 反模式

```
❌ Mutex 值拷贝
type Bad struct { mu sync.Mutex }
func (b Bad) Inc() { ... }     // b 是值，mu 被拷贝

// ✅ 指针 receiver
func (b *Bad) Inc() { ... }

❌ 嵌套锁死锁
mu1.Lock()
mu2.Lock()   // 另一个 goroutine 反向顺序 → deadlock

❌ 持锁做 I/O
mu.Lock()
http.Get(url)   // 持锁 3 秒，其他 goroutine 都等
mu.Unlock()

❌ sync.Map 作为通用 map
→ 类型不安全 + 无批量操作，先用 map+Mutex

❌ atomic 读写不匹配大小
atomic.StoreInt32(&x, 1)
y := atomic.LoadInt64(&x)  // ❌ 大小不一致
```

## 📖 参考资料

- [sync 包文档](https://pkg.go.dev/sync)
- [sync/atomic 包文档](https://pkg.go.dev/sync/atomic)
- [Go Memory Model](https://go.dev/ref/mem)
- [Dave Cheney - Sync Primitives](https://dave.cheney.net/category/go)
