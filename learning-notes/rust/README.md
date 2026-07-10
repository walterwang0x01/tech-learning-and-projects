# Rust

> Author: Walter Wang

<!-- version-check: Rust 1.97.0 (2026-07-09), Edition 2024, Tokio 1.52.3, Axum 0.8.9, checked 2026-07-09 -->
<!-- 修复于 2026-07-09: 1.96.0 → 1.97.0（v0 symbol mangling 默认、pin! 修复） -->

Rust 在 2026 年不是"可能有用的"，而是"你正在使用的工具的底层语言"：uv、ruff、Vite、Turbopack、Polars、SurrealDB、Rustls、Alacritty、zed 全部 Rust 写的。

<!-- 修复于 2026-05-30: 原文将不存在的 "Rust 1.97.1（2026-03-26）" 写成当前最新稳定版（与 01 文件同一杜撰来源）。经 blog.rust-lang.org / releases.rs 权威源核实，审查时点最新稳定版为 1.96.0（2026-05-28 发布）。 -->
> 🔄 更新于 2026-07-07
>
> **Rust 1.97.0**（2026-07-09）是当前最新稳定版：v0 symbol mangling 成为默认、修复 `pin!` 可变引用 soundness 回归（来源：[Rust Blog](https://blog.rust-lang.org/)）。
>
> **Axum 0.8.x** 已成为生态事实稳定线（不是之前笔记里写的 0.9），最新为 **0.8.9**。新项目直接用 0.8 即可。
>
> **Tokio 1.52.3**（2026-05-08）是当前最新稳定版；当前 LTS 线为 **1.51.x**（维护至 2027-03）。配套的 **dial9 飞行记录器**（2026-03）用于高并发服务定位调度延迟，详见 [03-异步编程.md](./03-异步编程.md)。
>
> **sqlx 0.9.0**（2026-05-21）带 Breaking Change：新增 `SqlSafeStr` trait，`query()`/`query_as()` 默认只接受 `&'static str`，动态 SQL 需要 `AssertSqlSafe` 显式放行或改用 `QueryBuilder` 绑定参数，详见 [03-异步编程.md](./03-异步编程.md) 第 6 节。

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
