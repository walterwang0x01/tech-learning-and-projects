# Go 技术栈

> Author: Walter Wang

<!-- version-check: Go 1.26.5 (2026-07-07 release), Kubernetes 1.37.0-alpha (GA 计划 2026-08-26), client-go v0.37.0-alpha, Echo 5.2.1, Fiber 3.4.0, golangci-lint v2.12.2, checked 2026-07-10 -->

Go 在 2026 年是云原生、微服务、CLI 工具、高性能网关的主力语言。K8s、Docker、Istio、Traefik、Kafka Connect、CockroachDB 都是 Go 写的。

> 更新于 2026-07-10
>
> **Go 1.26.5 安全发布（2026-07-07）**：修复两个安全问题——`os.Root` 在路径以 `/` 结尾且末段是符号链接时会逃逸 Root 边界（CVE-2026-39822），以及 `crypto/tls` 的 Encrypted Client Hello 实现会在握手中泄露 PSK identity，使被动网络观察者能反匿名化 ECH 保护的主机名（CVE-2026-42505）。生产集群建议尽快升级到 1.26.5 / 1.25.12（[Go 1.26.5 release notes](https://go.dev/doc/devel/release#go1.26.5)）。
>
> **Kubernetes 1.37 进入 Alpha**：v1.37 发布周期于 2026-05-18 开始，Enhancements Freeze 已过（06-17），Code Freeze 定在 2026-07-22/23，GA 计划 **2026-08-26**（[K8s v1.37 Release Schedule](https://github.com/kubernetes/sig-release/tree/master/releases/release-1.37)）。`client-go` 已发布 `v0.37.0-alpha.x` 供提前适配测试，生产 Operator/Controller 暂持续锁定 v0.36.x。
>
> **golangci-lint 保持 v2.12.2**（2026-05-06 发布）为最新稳定版，近 30 天无新 minor 版本；v2 迁移仍是当前唯一主线（[Changelog](https://golangci-lint.run/docs/product/changelog/)）。

> 🔄 更新于 2026-07-07
>
> **2026 年 Go 生态关键节点**：
>
> - **Go 1.26** 于 2026-02-10 发布，Green Tea GC 默认启用，cgo 开销降 30%（[Go Blog](https://blog.golang.org/go1.26)）
> - **Kubernetes 1.36** 于 2026-04-22 发布，client-go v0.36 同步 cut，Declarative Validation GA（[K8s Release](https://kubernetes.io/blog/2026/04/22/kubernetes-v1-36-release/)）
> - **JetBrains 2025 调查**：Gin 占 48% Go Web 框架份额，46% Go 开发者用于 web/API（[JetBrains Blog](https://blog.jetbrains.com/go/2026/04/28/popular-golang-web-frameworks/)）
> - **Echo 5.2.1**（2026-06-15）是当前稳定版，Go 最低要求 1.25，`v4` 安全维护到 2026-12-31（[Echo Release](https://github.com/labstack/echo/releases/tag/v5.2.1)）
> - **Fiber 3.4.0**（2026-07-02）继续推进 v3 主线，统一绑定 API、增强 hooks，适合极致吞吐场景（[Fiber Release](https://github.com/gofiber/fiber/releases/tag/v3.4.0)）
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
