# Go 技术栈

> Author: Walter Wang

<!-- version-check: Go 1.26 (2026-02), Go 1.24/1.25 stable, checked 2026-05-10 -->

Go 在 2026 年是云原生、微服务、CLI 工具、高性能网关的主力语言。K8s、Docker、Istio、Traefik、Kafka Connect、CockroachDB 都是 Go 写的。

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
