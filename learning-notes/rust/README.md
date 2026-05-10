# Rust

> Author: Walter Wang

<!-- version-check: Rust 1.97, Edition 2024, Tokio 1.47, Axum 0.9, checked 2026-05-10 -->

Rust 在 2026 年不是"可能有用的"，而是"你正在使用的工具的底层语言"：uv、ruff、Vite、Turbopack、Polars、SurrealDB、Rustls、Alacritty、zed 全部 Rust 写的。

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
