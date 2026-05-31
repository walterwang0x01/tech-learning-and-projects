# Cargo 与 Rust 生态

> Author: Walter Wang

<!-- version-check: Cargo 1.96, crates.io, Edition 2024, checked 2026-05-30 -->

## 1. Cargo 基础

```bash
# 创建新项目
cargo new myapp                 # 二进制
cargo new --lib mylib            # 库

# 编译运行
cargo build                      # debug
cargo build --release            # 发布
cargo run                        # 编译并运行
cargo check                      # 只检查不编译（快）
cargo test                       # 测试

# 依赖管理
cargo add tokio --features full
cargo remove tokio
cargo update

# 工具
cargo fmt                        # 格式化
cargo clippy                     # Linter
cargo doc --open                 # 生成文档
```

## 2. Cargo.toml

```toml
[package]
name = "myapp"
version = "0.1.0"
edition = "2024"
rust-version = "1.85"            # 最低支持版本

description = "A sample app"
license = "MIT OR Apache-2.0"
repository = "https://github.com/myorg/myapp"
keywords = ["cli", "tool"]
categories = ["command-line-utilities"]

[dependencies]
tokio = { version = "1.49", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }
serde_json = "1.0"

# 可选依赖
reqwest = { version = "0.12", optional = true }

[dev-dependencies]
criterion = "0.5"
mockall = "0.13"

[build-dependencies]
cc = "1.0"

[features]
default = []
http = ["reqwest"]

[[bin]]
name = "myapp"
path = "src/main.rs"

[[bench]]
name = "bench"
harness = false

[profile.release]
opt-level = 3
lto = true
codegen-units = 1
strip = true
panic = "abort"

[profile.dev]
opt-level = 0           # 默认，编译快但运行慢
debug = true
```

## 3. Workspace：多 Crate 项目

大型项目通常拆成多个 crate：

```toml
# 根 Cargo.toml
[workspace]
resolver = "2"
members = [
    "crates/core",
    "crates/api",
    "crates/cli",
]

[workspace.dependencies]
# 所有子 crate 共享的版本
tokio = { version = "1.49", features = ["full"] }
serde = { version = "1.0", features = ["derive"] }

[workspace.package]
version = "0.1.0"
edition = "2024"
license = "MIT"
```

```toml
# crates/api/Cargo.toml
[package]
name = "myapp-api"
version.workspace = true
edition.workspace = true

[dependencies]
tokio.workspace = true
myapp-core = { path = "../core" }
```

## 4. Features：可选能力

```toml
[features]
default = ["sync"]
sync = []
async = ["tokio", "futures"]
serde = ["dep:serde"]
```

```rust
#[cfg(feature = "async")]
pub async fn fetch() { /* ... */ }

#[cfg(feature = "sync")]
pub fn fetch_sync() { /* ... */ }
```

用户可以按需启用：

```bash
cargo add mylib --features async
```

## 5. crates.io 核心库（2026 版）

### 异步运行时
- **tokio** — 事实标准（99% 用这个）
- **smol** — 轻量替代
- **async-std** — 活跃度下降

### Web
- **axum** — 现代首选
- **actix-web** — 性能王者
- **rocket** — 语法糖多，活跃度一般
- **warp** — 函数式风格

### 序列化
- **serde** — 事实标准
- **serde_json** / **serde_yaml** / **serde_toml**
- **bincode** — 二进制
- **rmp-serde** — MessagePack

### 错误处理
- **anyhow** — 应用层
- **thiserror** — 库层
- **eyre** — anyhow 的改进版

### HTTP 客户端
- **reqwest** — 最流行
- **hyper** — 底层
- **ureq** — 同步轻量

### 数据库
- **sqlx** — 异步 + 编译期 SQL 校验
- **diesel** — ORM，同步
- **sea-orm** — 异步 ORM

### 命令行
- **clap** — 事实标准
- **structopt** — 已合并到 clap

### 日志
- **tracing** — 结构化日志（推荐）
- **log** — 老牌
- **env_logger** / **tracing-subscriber**

### 测试
- **tokio-test** — async 测试
- **proptest** — property-based testing
- **mockall** — mock 框架
- **criterion** — 基准测试
- **insta** — snapshot 测试

### 实用
- **uuid** / **chrono** / **regex** / **rand** / **itertools**

## 6. 发布到 crates.io

```bash
# 登录（从 https://crates.io 获取 token）
cargo login

# 打包
cargo package --list   # 列出将要发布的文件
cargo publish --dry-run

# 发布
cargo publish
```

**注意**：crates.io 的版本**不可删除**，只能 yank（防止新用户下载）。发布前反复测试。

## 7. Cargo 2024 的新特性

### cargo-binstall

免编译安装预编译二进制：

```bash
cargo install cargo-binstall
cargo binstall ripgrep          # 直接下载编译好的，不用等编译
cargo binstall dprint
```

### cargo-nextest

比内置 test 快 60%：

```bash
cargo install cargo-nextest
cargo nextest run
```

### cargo-deny

安全和许可证检查：

```toml
# deny.toml
[advisories]
vulnerability = "deny"
unmaintained = "warn"

[licenses]
allow = ["MIT", "Apache-2.0", "BSD-3-Clause"]
deny = ["GPL-3.0"]

[bans]
multiple-versions = "warn"

[sources]
unknown-registry = "deny"
```

```bash
cargo deny check
```

### cargo-machete

找出未使用的依赖：

```bash
cargo install cargo-machete
cargo machete
```

## 8. CI 标准 workflow

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy, rustfmt

      - name: Cache
        uses: Swatinem/rust-cache@v2

      - name: Format check
        run: cargo fmt --all -- --check

      - name: Clippy
        run: cargo clippy --all-targets --all-features -- -D warnings

      - name: Test
        run: cargo test --all-features

      - name: Security audit
        uses: actions-rust-lang/audit@v1
```

## 9. Cargo 生态治理工具

```
审计与依赖检查：
├─ cargo-audit        漏洞扫描
├─ cargo-deny         策略检查（许可证、ban 版本）
├─ cargo-outdated     依赖过时
└─ cargo-udeps        未使用依赖

性能与调试：
├─ cargo-flamegraph   火焰图
├─ cargo-llvm-cov     代码覆盖率
└─ cargo-expand       宏展开

开发辅助：
├─ cargo-watch        文件变更自动重编
├─ cargo-edit         命令行编辑 Cargo.toml
├─ cargo-generate     项目模板
└─ cargo-release      自动化版本发布
```

## 10. 反模式

```
❌ 把大量 features 默认启用
   → 用户不用也被装进来，编译慢、二进制大

❌ 在 lib crate 里 unwrap / panic
   → 库应该返回 Result，让调用方决定

❌ 多个 crate 依赖不同版本
   → 编译慢、二进制大
   ✅ workspace 统一管理

❌ 把 Cargo.lock 从 lib crate 里提交
   → lib 不提交 lock，bin 必须提交

❌ 不写 `#![deny(missing_docs)]`（public crate）
   → 文档缺失无法察觉

❌ cargo publish 前不 dry-run
   → 发出去就收不回
```

## 11. 生产检查清单

```
☐ Workspace 统一版本
☐ Cargo.toml 有 license / description / repository
☐ CI：fmt + clippy（-D warnings）+ test + audit
☐ Cargo.lock 提交（bin）/ 不提交（lib）
☐ Release profile 优化（lto、strip）
☐ SBOM：cargo-cyclonedx 生成
☐ 漏洞扫描：cargo-audit / cargo-deny
☐ 文档覆盖（deny(missing_docs)）
☐ 版本发布：cargo-release 自动化
☐ CHANGELOG.md 维护
```

## 📖 参考资料

- [The Cargo Book](https://doc.rust-lang.org/cargo/)
- [crates.io](https://crates.io/)
- [lib.rs（更快的浏览）](https://lib.rs/)
- [cargo-deny](https://embarkstudios.github.io/cargo-deny/)
- [Rust CLI Book](https://rust-cli.github.io/book/)
