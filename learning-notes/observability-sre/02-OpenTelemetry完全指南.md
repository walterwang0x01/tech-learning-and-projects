# OpenTelemetry 完全指南

> Author: Walter Wang

<!-- version-check: OpenTelemetry 1.x stable, OTLP 1.10.0, Collector v0.151.0 (2026-05-04), Declarative Config 1.0 stable, GenAI semconv (development), Profiles signal alpha, Winget support, checked 2026-05-20 -->

## 1. 核心架构

```
┌────────────── OpenTelemetry 数据流 ──────────────┐
│                                                   │
│  应用代码（各语言 SDK/Instrumentation）              │
│       │                                           │
│       │ OTLP (gRPC/HTTP)                          │
│       ▼                                           │
│  ┌────────────────────┐                           │
│  │  OTel Collector    │ ← 可选，但生产强烈推荐      │
│  │  ├─ Receiver       │                           │
│  │  ├─ Processor      │（批处理、尾部采样、属性处理）│
│  │  └─ Exporter       │                           │
│  └────────┬───────────┘                           │
│           │                                       │
│   ┌───────┼────────┐                              │
│   ▼       ▼        ▼                              │
│ Metrics  Traces  Logs（后端：Prometheus/Jaeger/Loki/Datadog...）│
└──────────────────────────────────────────────────┘
```

**为什么要有 Collector？**
1. 解耦应用和后端，后端切换不用改代码
2. 统一做采样、过滤、脱敏
3. 批量发送，降低网络开销
4. 多后端扇出（同时发 Prometheus 和 Datadog）

## 2. OTel Collector 配置实战

生产级配置示例（`otel-collector-config.yaml`）：

```yaml
receivers:
  otlp:
    protocols:
      grpc:
        endpoint: 0.0.0.0:4317
      http:
        endpoint: 0.0.0.0:4318

  # Prometheus 格式指标的反向采集
  prometheus:
    config:
      scrape_configs:
        - job_name: 'node-exporter'
          static_configs:
            - targets: ['node-exporter:9100']

processors:
  # 批量发送，降低网络开销
  batch:
    timeout: 10s
    send_batch_size: 1024

  # 内存保护
  memory_limiter:
    check_interval: 1s
    limit_mib: 512

  # 尾部采样：错误和慢请求 100% 保留，其他 10% 采样
  tail_sampling:
    decision_wait: 10s
    policies:
      - name: errors-policy
        type: status_code
        status_code: {status_codes: [ERROR]}
      - name: slow-policy
        type: latency
        latency: {threshold_ms: 1000}
      - name: probabilistic-policy
        type: probabilistic
        probabilistic: {sampling_percentage: 10}

  # 属性处理：脱敏
  attributes:
    actions:
      - key: user.email
        action: delete
      - key: http.request.header.authorization
        action: delete

  # 资源属性（服务名、环境等）
  resource:
    attributes:
      - key: deployment.environment
        value: production
        action: upsert

exporters:
  # Prometheus Remote Write
  prometheusremotewrite:
    endpoint: http://prometheus:9090/api/v1/write

  # Loki（日志）
  loki:
    endpoint: http://loki:3100/loki/api/v1/push

  # OTLP（Tempo、Jaeger、Honeycomb 都支持）
  otlp/tempo:
    endpoint: tempo:4317
    tls:
      insecure: true

service:
  pipelines:
    metrics:
      receivers: [otlp, prometheus]
      processors: [memory_limiter, batch, resource]
      exporters: [prometheusremotewrite]
    traces:
      receivers: [otlp]
      processors: [memory_limiter, tail_sampling, attributes, batch, resource]
      exporters: [otlp/tempo]
    logs:
      receivers: [otlp]
      processors: [memory_limiter, attributes, batch, resource]
      exporters: [loki]
```

## 3. Python 应用接入（FastAPI 示例）

```bash
pip install opentelemetry-distro opentelemetry-exporter-otlp \
            opentelemetry-instrumentation-fastapi \
            opentelemetry-instrumentation-sqlalchemy \
            opentelemetry-instrumentation-redis \
            opentelemetry-instrumentation-httpx
```

```python
# app/telemetry.py
"""统一初始化 OpenTelemetry。"""
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor


def setup_telemetry(app, service_name: str, otlp_endpoint: str):
    """在 FastAPI 应用启动时调用一次。"""
    resource = Resource.create({
        "service.name": service_name,
        "service.version": "1.0.0",
        "deployment.environment": "production",
    })

    # Traces
    trace_provider = TracerProvider(resource=resource)
    trace_provider.add_span_processor(
        BatchSpanProcessor(OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True))
    )
    trace.set_tracer_provider(trace_provider)

    # Metrics
    metric_reader = PeriodicExportingMetricReader(
        OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True),
        export_interval_millis=30000,  # 每 30 秒
    )
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))

    # 自动埋点：HTTP、SQL、Redis、下游 HTTP 调用
    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument()
    RedisInstrumentor().instrument()
    HTTPXClientInstrumentor().instrument()


# app/main.py
from fastapi import FastAPI
from app.telemetry import setup_telemetry

app = FastAPI()
setup_telemetry(app, service_name="order-service", otlp_endpoint="otel-collector:4317")

# 手动埋点示例
from opentelemetry import trace
tracer = trace.get_tracer(__name__)

@app.post("/orders")
async def create_order(payload: dict):
    with tracer.start_as_current_span("validate_order") as span:
        span.set_attribute("order.amount", payload["amount"])
        span.set_attribute("order.user_id", payload["user_id"])
        # ... 验证逻辑
    # ... 保存订单（SQLAlchemy 已被自动埋点）
    return {"ok": True}
```

## 4. Java 应用接入（Spring Boot 3.x）

```xml
<!-- 不需要改代码，加 Agent 即可 -->
<!-- 启动参数：-javaagent:opentelemetry-javaagent.jar -->
```

```yaml
# application.yml
otel:
  service:
    name: order-service
  exporter:
    otlp:
      endpoint: http://otel-collector:4317
  instrumentation:
    common:
      default-enabled: true
```

或者用 Spring Boot 3 自带的 Micrometer + OTel Bridge：

```java
// 使用 Micrometer Tracing + OTel
@Configuration
public class TelemetryConfig {
    @Bean
    public OpenTelemetry openTelemetry() {
        return AutoConfiguredOpenTelemetrySdk.initialize().getOpenTelemetrySdk();
    }
}

// 使用（自动生成 Trace + Metric）
@Service
public class OrderService {
    private final Tracer tracer;

    @Observed(name = "orders.create", contextualName = "createOrder")
    public Order create(CreateOrderCommand cmd) {
        // Micrometer Observation 会自动生成 Span 和 Metrics
        return repository.save(new Order(cmd));
    }
}
```

## 5. Go 应用接入

```go
package main

import (
    "context"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/propagation"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.26.0"
)

func initTracer(ctx context.Context, endpoint string) (*sdktrace.TracerProvider, error) {
    exporter, err := otlptracegrpc.New(ctx,
        otlptracegrpc.WithEndpoint(endpoint),
        otlptracegrpc.WithInsecure(),
    )
    if err != nil {
        return nil, err
    }

    res := resource.NewWithAttributes(
        semconv.SchemaURL,
        semconv.ServiceName("order-service"),
        semconv.ServiceVersion("1.0.0"),
        attribute.String("deployment.environment", "production"),
    )

    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(res),
        sdktrace.WithSampler(sdktrace.ParentBased(sdktrace.TraceIDRatioBased(0.1))),
    )
    otel.SetTracerProvider(tp)
    otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
        propagation.TraceContext{}, propagation.Baggage{},
    ))
    return tp, nil
}

// 使用
func CreateOrder(ctx context.Context, payload Order) error {
    tracer := otel.Tracer("order-service")
    ctx, span := tracer.Start(ctx, "create_order")
    defer span.End()

    span.SetAttributes(
        attribute.Int64("order.amount", payload.Amount),
        attribute.String("order.user_id", payload.UserID),
    )
    // ... 业务逻辑
    return nil
}
```

## 6. W3C Trace Context 传播

跨服务调用时，trace_id 必须通过 HTTP Header 传递：

```
GET /api/orders HTTP/1.1
traceparent: 00-4bf92f3577b34da6a3ce929d0e0e4736-00f067aa0ba902b7-01
#              ^version-^trace-id-------------^span-id---------^flags
tracestate: vendor1=value1,vendor2=value2
```

所有主流 OTel SDK 默认启用 W3C propagator，**不要**把老的 Zipkin B3 header 和 W3C 混用。

## 7. 语义约定（Semantic Conventions）

2026 年稳定的核心命名空间：

```
http.*        HTTP 客户端/服务端
db.*          数据库操作
messaging.*   消息队列
rpc.*         RPC（gRPC、Thrift）
network.*     网络属性
url.*         URL 解析
server.*      服务器属性
client.*      客户端属性
exception.*   异常
gen_ai.*      GenAI / LLM（2026 扩展）
```

**务必使用标准命名**：这样 Grafana、Datadog、Honeycomb 的开箱仪表盘才能识别你的数据。

## 8. 常见坑

```
生产常见问题：
├─ BatchSpanProcessor 阻塞 → 配合超时和队列丢弃策略
├─ 无限循环埋点：instrumentation 自身产生 Trace
│   → 用 suppress_instrumentation
├─ 采样率低 + 无尾部采样 → 丢失关键错误 Trace
│   → Collector 做 tail_sampling
├─ 跨进程 Context 丢失 → gRPC/消息队列要显式注入 carrier
├─ Resource Attributes 放到 Span Attributes → 噪音大、开销大
└─ 本地开发没 Collector 直连 Jaeger → 需要改 endpoint
```

## 9. 生产检查清单

```
上线前 checklist：
☐ Collector 部署为 DaemonSet（K8s）或独立集群
☐ 配置批处理 + 内存保护
☐ 尾部采样策略已配置（错误和慢请求 100%）
☐ 敏感字段脱敏（认证头、Email、身份证）
☐ 资源属性（service.name、version、env）已设置
☐ 跨服务 trace context 已验证（在 dashboard 中能看到完整链路）
☐ 监控 Collector 自身（CPU、内存、drop rate）
☐ 采样率可动态调整（不用重启应用）
```

## 📖 参考资料

- [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/otel/)
- [OpenTelemetry Collector](https://opentelemetry.io/docs/collector/)
- [Semantic Conventions](https://opentelemetry.io/docs/specs/semconv/)
- [OTel Contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib)

## 10. 2026 年重大进展

> 🔄 更新于 2026-05-13

### 10.1 Declarative Configuration 稳定版（2026-03-05）

OpenTelemetry 声明式配置规范的关键部分已标记为 stable，包括 JSON Schema 数据模型（opentelemetry-configuration 发布 stable 1.0）。这意味着可以用 YAML/JSON 文件统一配置 SDK，无需在代码中硬编码 exporter/processor/sampler。来源：[OTel Blog](https://opentelemetry.io/blog/2026/stable-declarative-config/)

```yaml
# otel-config.yaml — 声明式配置示例
file_format: "0.4"
sdk:
  resource:
    attributes:
      service.name: my-service
      deployment.environment: production
  tracer_provider:
    processors:
      - batch:
          exporter:
            otlp:
              endpoint: http://collector:4317
              protocol: grpc
  meter_provider:
    readers:
      - periodic:
          interval: 30000
          exporter:
            otlp:
              endpoint: http://collector:4317
```

### 10.2 GenAI 语义约定（Development 状态）

OTel 新增了 Generative AI 系统的语义约定，定义了 `gen_ai.*` 属性命名空间，覆盖模型调用、Agent 运行和工具调用三个层级。虽然仍处于 Development 状态，但 Datadog、Honeycomb、LangSmith 等平台已原生支持。85% 的组织计划启用 LLM 可观测性，但仅 8% 完成了部署。来源：[OTel GenAI Semconv](https://opentelemetry.io/docs/specs/semconv/gen-ai/)、[Elastic 2026 调研](https://maketocreate.com/opentelemetry-genai-tracing-ai-agents-without-leaking-pii/)

**Agent Spans 语义约定**：专门为 Agent 框架定义的 span 类型，覆盖推理、工具调用、检索等步骤，每个操作成为子 span，形成完整的推理链追踪。来源：[OTel GenAI Agent Spans](https://opentelemetry.io/docs/specs/semconv/gen-ai/gen-ai-agent-spans/)

关键属性：

| 属性 | 说明 |
|------|------|
| `gen_ai.system` | 模型提供商（openai/anthropic/...） |
| `gen_ai.request.model` | 请求的模型名称 |
| `gen_ai.response.model` | 实际响应的模型名称 |
| `gen_ai.usage.input_tokens` | 输入 Token 数 |
| `gen_ai.usage.output_tokens` | 输出 Token 数 |
| `gen_ai.response.finish_reasons` | 完成原因（stop/tool_calls/...） |

### 10.3 其他重要变化

- **Span Event API 废弃**：社区决定收敛到 Logs API 作为唯一推荐的事件发射方式
- **Kotlin Multiplatform SDK 开发中**：将 OTel 扩展到 Android、iOS、JVM 等平台
- **OTLP 1.10.0**：Traces/Metrics/Logs 信号稳定，Profiles 信号处于 Development 状态
- **eBPF Instrumentation 1.0 目标**：零代码侵入的自动化遥测采集
- **Ecosystem Explorer 项目**：帮助开发者在 240+ Java 自动 instrumentation 和数百个 Collector 组件中导航

来源：[Datadog OTel News 2026-03](https://opensource.datadoghq.com/otel-news/2026/03/)、[Datadog OTel News 2026-04](https://opensource.datadoghq.com/otel-news/2026/04/)


### 10.4 OpenTelemetry Collector v0.150（2026-04-13）

> 🔄 更新于 2026-05-16

Collector 在 4 月连续发布三个版本，节奏明显加快——v0.149 / v0.150 / v0.151 都在两周内完成。来源：[Datadog OTel News 2026-04](https://opensource.datadoghq.com/otel-news/2026/04/)、[OTel Collector v0.150](https://sourceforge.net/projects/opentelemetry-collector.mirror/files/v0.150.0/)

**关键变化**：

| 变化 | 影响 | 紧迫性 |
|------|------|-------|
| azure_auth 扩展安全修复 | CVSS 严重等级，必须升级 | 高 |
| Profiles 信号升级到 Alpha | OTel 第四种核心信号正式可用 | 中 |
| 组件类型 snake_case 重命名 | 配置文件需要适配新命名 | 中 |
| 三个新组件：Log Clustering Processor 等 | 提供更强的边缘聚合能力 | 低 |
| semconv 1.38.0 → 1.40.0 | 包含部分 GenAI 属性更新 | 低 |

**Profiles 信号 Alpha**：OpenTelemetry 终于把"持续性能剖析"作为标准信号纳入——和 Traces、Metrics、Logs 同级。这意味着以后 Datadog Continuous Profiler、Pyroscope、Parca 等工具会逐步切换到 OTLP profiles 协议。

**Log Clustering Processor**：在 Collector 边缘做日志去重和模式提取，传到后端的日志体积可减少 60-80%（重复模板日志合并）。对于日志量大的微服务这是显著的成本优化。

**snake_case 重命名示例**：

```yaml
# 旧配置（仍兼容，但会有 deprecation 警告）
processors:
  batchProcessor:
    timeout: 10s

# 新配置（推荐）
processors:
  batch:
    timeout: 10s
```

**升级路径**：

```
< v0.149：必须升级（azure_auth CVE）
v0.149 → v0.150：profiles 信号 alpha 试用
v0.150 → v0.151：包含 v0.150 所有改进 + 更多 bug 修复
```

来源：[OTel Collector CHANGELOG-API](https://github.com/open-telemetry/opentelemetry-collector/blob/main/CHANGELOG-API.md)


### 10.5 OpenTelemetry Collector v0.151（2026-05-04）

> 🔄 更新于 2026-05-20

<!-- version-check: OTel Collector v0.151.0 (2026-05-04), Winget Windows package manager support, checked 2026-05-20 -->

Collector v0.151.0 是 v0.150 的稳定补强版本，**最大变化是新增 Winget（Windows Package Manager）支持**——Windows 端可通过单条命令完成安装、升级、卸载，与 Linux 的 apt/yum 体验对齐。来源：[Sumo Logic — OTel Collector v0.151.0 Release Notes](https://www.sumologic.com/help/release-notes-collector/2026/05/04/otel/)

```powershell
# Windows 一键安装（v0.151.0+）
winget install OpenTelemetry.Collector

# 升级（与现有安装方式完全兼容）
winget upgrade OpenTelemetry.Collector

# 卸载
winget uninstall OpenTelemetry.Collector
```

**其他 v0.151 改动**：

| 变化 | 影响 |
|------|------|
| Winget 包管理器支持（Windows） | Windows IT 部署流程显著简化 |
| azure_auth 后续 bug 修复 | v0.150 引入修复后的连带回归 |
| Profiles 信号实现细节稳定 | Alpha 阶段的 OTLP profiles encoding 实现固化 |
| 与 v0.150 配置完全兼容 | 升级零成本 |

**升级建议（修订版）**：

```
< v0.149：必须立即升级（azure_auth CVE）
v0.149 → v0.151：跳过 v0.150，直接升 v0.151（Winget + 稳定性双收益）
v0.150 → v0.151：受益于 bug 修复和 Profiles encoding 稳定
v0.151 已是当前推荐生产版本（截至 2026-05-20）
```

来源：[Sumo Logic OTel Collector v0.151.0](https://www.sumologic.com/help/release-notes-collector/2026/05/04/otel/)、[open-telemetry/opentelemetry-collector-releases](https://github.com/open-telemetry/opentelemetry-collector-releases)

