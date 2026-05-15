# Rust

> Author: Walter Wang

<!-- version-check: Rust 1.97.1 (2026-03-26 with CVE-2026-33055/33056 fix), Edition 2024, Tokio 1.47, Axum 0.8.8, checked 2026-05-15 -->

Rust 在 2026 年不是"可能有用的"，而是"你正在使用的工具的底层语言"：uv、ruff、Vite、Turbopack、Polars、SurrealDB、Rustls、Alacritty、zed 全部 Rust 写的。

> 🔄 更新于 2026-05-15
>
> **Rust 1.97.1**（2026-03-26）修复了 Cargo 依赖的 tar 库的 **CVE-2026-33055 / CVE-2026-33056**，所有使用非 crates.io 来源（git、tar.gz）依赖的项目都应升级（来源：[Rust Release Notes](https://doc.rust-lang.org/stable/releases.html)）。
>
> **Axum 0.8.x** 已成为生态事实稳定线（不是之前笔记里写的 0.9），最新为 0.8.8。新项目直接用 0.8 即可。
>
> **Tokio dial9 飞行记录器**（2026-03）：用于高并发服务定位调度延迟，详见 [03-异步编程.md](./03-异步编程.md)。

这个目录是精简的"为什么 + 最小工作集"，不追求和 iOS/Android 那种全栈覆盖。

## 📁 目录结构

```
rust/
├── 01-语法与所有权.md         # Ownership、Borrowing、Lifetime 核心
├── 02-Cargo与生态.md          # Crate、Cargo.toml、workspace、发布
├── 03-异步编程.md              # Tokio、Axum、sqlx 实战
├── 04-错误处理与测试.md        # Result、anyhow、thiserror、proptest
└── 05-高性能工具开发.md        # CLI、Wasm、和 Python/JS 互操作
```

## 🎯 什么时候值得用 Rust

```
非常适合：
├─ CLI 工具（更快启动、零依赖）
├─ 高性能网络服务（Axum）
├─ 系统编程（嵌入式、OS 模块）
├─ 高 CPU 计算（数据处理、加密、压缩）
├─ WebAssembly 目标
├─ 为 Python / Node 写性能扩展（PyO3、napi-rs）
└─ 数据引擎和数据库

不适合：
├─ 简单 CRUD（Go / Python 更快上手）
├─ 原型验证（编译慢、学习曲线陡）
└─ 团队 Rust 经验少时的关键服务
```

## 🔗 关联内容

- **Python 的 Rust 工具**：uv、ruff、Polars → [python/09-工具与规范/](../python/09-工具与规范/)
- **前端的 Rust 工具**：Vite (Rolldown)、Turbopack → [frontend/05-工程化与构建/](../frontend/05-工程化与构建/)
- **和 Go 的对比** → [go/README.md](../go/README.md)

## 📚 权威参考

- [The Rust Book（中文版）](https://rustwiki.org/zh-CN/book/)
- [Rust by Example](https://doc.rust-lang.org/rust-by-example/)
- [Rust Async Book](https://rust-lang.github.io/async-book/)
- [This Week in Rust](https://this-week-in-rust.org/)
- [Are We Learning Yet（AI/ML 生态）](https://www.arewelearningyet.com/)
