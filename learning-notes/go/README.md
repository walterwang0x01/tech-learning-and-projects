# Go 技术栈

> Author: Walter Wang

<!-- version-check: Go 1.26.x (2026-02-10 release), client-go v0.36, golangci-lint v2.12, checked 2026-05-15 -->

Go 在 2026 年是云原生、微服务、CLI 工具、高性能网关的主力语言。K8s、Docker、Istio、Traefik、Kafka Connect、CockroachDB 都是 Go 写的。

> 🔄 更新于 2026-05-15
>
> **2026 年 Go 生态关键节点**：
>
> - **Go 1.26** 于 2026-02-10 发布，Green Tea GC 默认启用，cgo 开销降 30%（[Go Blog](https://blog.golang.org/go1.26)）
> - **Kubernetes 1.36** 于 2026-04-22 发布，client-go v0.36 同步 cut，Declarative Validation GA（[K8s Release](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/)）
> - **JetBrains 2025 调查**：Gin 占 48% Go Web 框架份额，46% Go 开发者用于 web/API（[JetBrains Blog](https://blog.jetbrains.com/go/2026/04/28/popular-golang-web-frameworks/)）
> - **golangci-lint v2** 成为主线，v2.12.2 已发布，需要从 v1 配置迁移
> - **Go 1.26.1 / 1.25.8** 安全补丁（2026-03-03）已发布，建议线上集群尽快升级

## 📁 目录结构

```
go/
├── 00-Go基础/
│   ├── 01-Go语法基础.md
│   ├── 02-类型系统与泛型.md
│   ├── 03-错误处理.md
│   ├── 04-接口与组合.md
│   └── 05-内存与GC.md
├── 01-并发编程/
│   ├── 01-Goroutine与Channel.md
│   ├── 02-Context与取消.md
│   ├── 03-sync包与原子操作.md
│   └── 04-并发模式.md
├── 02-Web开发/
│   ├── 01-net-http与路由.md
│   ├── 02-Gin与Echo框架.md
│   ├── 03-gRPC与Protobuf.md
│   └── 04-中间件模式.md
├── 03-云原生/
│   ├── 01-Kubernetes-Client-go.md
│   ├── 02-Operator开发.md
│   └── 03-Controller模式.md
├── 04-工程化/
│   ├── 01-模块与依赖管理.md
│   ├── 02-测试与基准.md
│   └── 03-工具链与linter.md
└── 05-面试准备/
    ├── 01-Go语言面试题.md
    └── 02-并发与内存面试题.md
```

## 🎯 核心特点

- **简单**：关键字只有 25 个，语法学起来快
- **并发原生**：Goroutine + Channel，百万级并发不费力
- **编译单二进制**：部署极简，零依赖
- **标准库强大**：`net/http`、`encoding/json`、`io` 开箱即用
- **生态**：云原生、CLI、微服务最强

## 🔗 关联内容

- **K8s** → [java/03-容器化/03-kubernetes-overview.md](../java/03-容器化/03-kubernetes-overview.md)
- **gRPC** → [java/05-网络编程/05-gRPC-Java.md](../java/05-网络编程/05-gRPC-Java.md)
- **可观测性** → [observability-sre/](../observability-sre/)
- **平台工程** → [platform-engineering/](../platform-engineering/)
