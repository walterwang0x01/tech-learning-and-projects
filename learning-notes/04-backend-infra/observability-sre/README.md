# 可观测性与 SRE

> Author: Walter Wang

<!-- version-check: OpenTelemetry Collector v0.155.0, Prometheus 3.13.0, Grafana 13.1.0, checked 2026-07-07 -->

这个目录覆盖现代系统的可观测性和 SRE 实践，是各技术栈（Java/Go/Python/Frontend）共用的"工程侧"内容。配合 `ai-agent/14-可观测与评估/` 可以看到 LLM 时代的可观测性全景。

## 📁 目录结构

```
observability-sre/
├── 01-可观测性基础.md           # 三支柱、信号类型、范式演进
├── 02-OpenTelemetry完全指南.md  # OTLP、Collector、各语言 SDK
├── 03-Prometheus与Grafana.md   # 指标监控、PromQL、告警
├── 04-日志聚合Loki-ELK.md       # 结构化日志、聚合查询
├── 05-SLO-SLI实践.md            # 错误预算、工程治理
├── 06-分布式追踪实战.md          # Trace 上下文传播、采样策略
├── 07-AI-Agent可观测性.md        # LLM Trace、Token 追踪、Agent 评估
└── 08-事件响应与Postmortem.md   # On-call、事故处理、无责复盘
```

## 🎯 适用场景

- 新项目搭建监控体系（OpenTelemetry + Prometheus + Grafana + Loki）
- 现有系统迁移到标准可观测性栈
- 设计 SLO/SLI，推动工程治理
- AI Agent 系统的可观测性改造
- 事故响应流程规范化

## 🔗 关联内容

- **AI 侧可观测性** → [ai-agent/14-可观测与评估/](../../00-ai/04-ai-agent/14-可观测与评估/)
- **K8s 运维** → [java/03-容器化/03-kubernetes-overview.md](../../01-languages/java/03-容器化/03-kubernetes-overview.md)
- **事件驱动架构** → [architecture/01-事件驱动架构.md](../architecture/01-事件驱动架构.md)
- **安全侧** → [security/](../security/)

## 📚 权威参考

- [OpenTelemetry 官方](https://opentelemetry.io/)
- [Google SRE Books](https://sre.google/books/)
- [Prometheus 官方文档](https://prometheus.io/docs/)
- [CNCF Landscape - Observability](https://landscape.cncf.io/)
