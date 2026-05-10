# Go 工具链与 linter

> Author: Walter Wang

<!-- version-check: golangci-lint 1.65, goreleaser 2.5, delve 1.24, checked 2026-05-10 -->

## 1. 必装工具（2026 年推荐）

```
每个 Go 开发者机器上应该有：
├─ go（1.24 或 1.26）
├─ gopls（LSP，IDE 用）
├─ dlv（Delve 调试器）
├─ golangci-lint（代码检查）
├─ gofumpt（更严格的 gofmt）
├─ govulncheck（漏洞扫描）
├─ mockery（Mock 生成）
├─ goreleaser（发布工具）
└─ air（热重载开发）
```

一键安装：

```bash
#!/bin/bash
go install golang.org/x/tools/gopls@latest
go install github.com/go-delve/delve/cmd/dlv@latest
go install mvdan.cc/gofumpt@latest
go install github.com/golangci/golangci-lint/cmd/golangci-lint@latest
go install golang.org/x/vuln/cmd/govulncheck@latest
go install github.com/vektra/mockery/v3@latest
go install github.com/goreleaser/goreleaser/v2@latest
go install github.com/air-verse/air@latest
```

## 2. golangci-lint 配置

```yaml
# .golangci.yml
run:
  timeout: 5m
  tests: true

linters:
  disable-all: true
  enable:
    - errcheck        # 检查未处理的错误
    - gosimple        # 建议简化代码
    - govet           # 标准 vet 检查
    - ineffassign     # 无用赋值
    - staticcheck     # 静态分析（最全）
    - unused          # 未使用代码
    - gofumpt         # 更严格的格式
    - goimports       # import 排序
    - gocritic        # 大量有用检查
    - revive          # 替代 golint
    - gosec           # 安全问题
    - misspell        # 拼写
    - bodyclose       # HTTP body 未关闭
    - noctx           # net/http 未传 context
    - errorlint       # 错误处理最佳实践
    - exhaustive      # enum switch 穷尽
    - nilnil          # return nil, nil（通常是 bug）
    - prealloc        # slice 预分配
    - wastedassign    # 浪费的赋值

linters-settings:
  gocritic:
    enabled-tags: [diagnostic, style, performance]
  revive:
    rules:
      - name: exported
      - name: error-return
      - name: error-strings
      - name: var-naming

issues:
  exclude-rules:
    - path: _test\.go
      linters: [errcheck, gosec]
    - path: examples/
      linters: [errcheck]
```

```bash
# 运行
golangci-lint run

# 只看新代码（增量）
golangci-lint run --new-from-rev HEAD~1

# 修自动可修的
golangci-lint run --fix
```

## 3. gopls（IDE 开发）

gopls 是 Go 官方 LSP，VS Code / Neovim / JetBrains 都用它。

```json
// VS Code settings.json
{
    "go.useLanguageServer": true,
    "gopls": {
        "ui.semanticTokens": true,
        "ui.diagnostic.analyses": {
            "unusedparams": true,
            "shadow": true,
            "fieldalignment": false
        },
        "formatting.gofumpt": true
    },
    "go.lintTool": "golangci-lint",
    "go.lintOnSave": "package"
}
```

## 4. Delve 调试

```bash
# 调试运行中的程序
dlv debug ./cmd/myapp

# 调试测试
dlv test -- -run TestFoo

# attach 到运行中的进程
dlv attach $(pgrep myapp)

# 远程调试（容器内）
dlv --listen=:2345 --headless=true --api-version=2 exec ./myapp
```

在 VS Code / GoLand 里一键调试，不用记命令。

## 5. 热重载开发：Air

```toml
# .air.toml
[build]
cmd = "go build -o ./tmp/main ./cmd/myapp"
bin = "./tmp/main"
include_ext = ["go", "tpl", "tmpl", "html", "yaml"]
exclude_dir = ["tmp", "vendor", "node_modules"]

[log]
time = true

[color]
main = "magenta"
```

```bash
air
# 改代码自动重编译重启
```

## 6. 性能剖析（pprof）

Go 内置最强大的性能工具：

```go
// 开启 pprof 端点
import _ "net/http/pprof"

go func() {
    http.ListenAndServe(":6060", nil)
}()
```

```bash
# CPU profile（30 秒）
go tool pprof http://localhost:6060/debug/pprof/profile?seconds=30

# 内存
go tool pprof http://localhost:6060/debug/pprof/heap

# Goroutine
go tool pprof http://localhost:6060/debug/pprof/goroutine

# 在交互式界面
(pprof) top10           # 耗时前 10 的函数
(pprof) web             # 浏览器看火焰图（需 graphviz）
(pprof) list funcName   # 看某函数耗时在哪行

# 更好的 UI
go tool pprof -http=:8080 http://localhost:6060/debug/pprof/profile
```

生产级工具：**Pyroscope**、**Parca** 持续 profiling，eBPF 抓取所有服务。

## 7. trace：并发分析

```bash
# 生成 trace
go test -trace trace.out ./...

# 查看
go tool trace trace.out
# 浏览器打开，看 goroutine 调度、GC 等
```

## 8. benchstat：基准对比

```bash
# 对比两次 benchmark（优化前 vs 优化后）
go test -bench=. -count=10 > old.txt
# ... 改代码 ...
go test -bench=. -count=10 > new.txt
benchstat old.txt new.txt

# 输出：
# name                old time/op  new time/op  delta
# FibRecursive-8      100ms ± 2%   50ms ± 1%    -50.00%  (p=0.001 n=10)
```

## 9. 代码生成（go generate）

```go
//go:generate mockery --name UserRepo
//go:generate protoc --go_out=. --go-grpc_out=. ./proto/user.proto
//go:generate go run ./cmd/gen-api

package mypkg
```

```bash
go generate ./...    # 运行所有 generate 指令
```

## 10. CI 标准流水线

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true

      - name: Download deps
        run: go mod download

      - name: Verify
        run: |
          go mod verify
          go mod tidy -diff    # 1.23+ 检查 go.mod 是否最新

      - name: Lint
        uses: golangci/golangci-lint-action@v6
        with:
          version: latest

      - name: Test
        run: go test -race -coverprofile=coverage.out -covermode=atomic ./...

      - name: Vulnerability scan
        run: |
          go install golang.org/x/vuln/cmd/govulncheck@latest
          govulncheck ./...

      - name: Upload coverage
        uses: codecov/codecov-action@v5
        with:
          files: coverage.out

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod

      - name: Build
        run: go build -v ./...
```

## 11. Dockerfile 最佳实践

```dockerfile
# 多阶段构建
FROM golang:1.26-alpine AS builder

WORKDIR /src
COPY go.mod go.sum ./
RUN --mount=type=cache,target=/go/pkg/mod \
    go mod download

COPY . .
RUN --mount=type=cache,target=/go/pkg/mod \
    --mount=type=cache,target=/root/.cache/go-build \
    CGO_ENABLED=0 go build \
    -ldflags="-w -s -X main.version=$(git rev-parse --short HEAD)" \
    -o /out/myapp ./cmd/myapp

# 运行时镜像
FROM gcr.io/distroless/static-debian12:nonroot
COPY --from=builder /out/myapp /myapp
USER nonroot:nonroot
ENTRYPOINT ["/myapp"]
```

镜像大小：5-20 MB（纯静态二进制）。

## 12. Makefile 模板

```makefile
.PHONY: all build test lint fmt clean docker

all: fmt lint test build

build:
	CGO_ENABLED=0 go build -ldflags="-w -s" -o bin/myapp ./cmd/myapp

test:
	go test -race -coverprofile=coverage.out -covermode=atomic ./...

lint:
	golangci-lint run

fmt:
	gofumpt -l -w .
	goimports -w .

vulncheck:
	govulncheck ./...

docker:
	docker build -t myorg/myapp:latest .

clean:
	rm -rf bin/ coverage.out

.PHONY: help
help:
	@echo "build       - Build binary"
	@echo "test        - Run tests with race detector"
	@echo "lint        - Run golangci-lint"
	@echo "fmt         - Format code"
	@echo "docker      - Build Docker image"
```

## 13. 生产检查清单

```
☐ golangci-lint 接入（配置 + CI 强制）
☐ gofumpt 作为 formatter
☐ govulncheck 在 CI 跑
☐ 所有 goroutine 有明确退出条件
☐ go test -race 通过
☐ 覆盖率上传（Codecov）
☐ Dockerfile 多阶段 + distroless
☐ SBOM 生成（syft）
☐ 镜像签名（cosign）
☐ pprof 端点仅暴露到管理网络
☐ goreleaser 自动化 Release
```

## 📖 参考资料

- [golangci-lint 文档](https://golangci-lint.run/)
- [gopls 文档](https://github.com/golang/tools/tree/master/gopls)
- [Delve 调试器](https://github.com/go-delve/delve)
- [Go pprof](https://pkg.go.dev/net/http/pprof)
- [goreleaser](https://goreleaser.com/)
- [Air 热重载](https://github.com/air-verse/air)
