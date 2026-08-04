# Prometheus 与 Grafana

> Author: Walter Wang

<!-- version-check: Prometheus 3.13.0 (2026-07-01), Grafana 13.1.0 (2026-07-01), Alertmanager 0.28, checked 2026-07-07 -->

## 1. Prometheus 架构

```
┌────────── Prometheus 拉取模型 ──────────┐
│                                          │
│  目标服务（暴露 /metrics 端点）             │
│       ▲                                  │
│       │ pull（HTTP，每 15-30s）            │
│       │                                  │
│  ┌────┴─────┐                             │
│  │ Prometheus│── 本地 TSDB                │
│  │  Server   │                            │
│  └────┬──────┘                             │
│       │                                  │
│  ┌────┴─────┐  ┌─────────────┐          │
│  │ Grafana  │  │ Alertmanager │          │
│  │ (可视化)  │  │ (告警路由)    │          │
│  └──────────┘  └─────────────┘          │
└──────────────────────────────────────────┘
```

**拉取模型**的优势：目标发现、健康检查都由 Prometheus 主动做，服务不用维护推送目标。

## 2. 数据模型

```
每个时间序列（time series）由三部分唯一标识：

  metric_name{label1="value1", label2="value2"}  value@timestamp

例如：
  http_requests_total{method="POST", route="/orders", status="200"}  1234@1712345678
```

**标签爆炸是最大的坑**：见 [01-可观测性基础.md 5.2 节](./01-可观测性基础.md)。

## 3. PromQL 实战

### 3.1 四种操作符

```promql
# Instant vector（瞬时向量）
http_requests_total

# Range vector（范围向量）
http_requests_total[5m]

# 速率（一定要对 Counter 用 rate 不能直接看）
rate(http_requests_total[5m])

# 聚合
sum by (route) (rate(http_requests_total[5m]))
```

### 3.2 常用生产查询

```promql
# QPS by route
sum by (route) (rate(http_requests_total[5m]))

# 错误率
sum(rate(http_requests_total{status=~"5.."}[5m]))
  /
sum(rate(http_requests_total[5m]))

# P99 时延
histogram_quantile(0.99,
  sum by (le, route) (rate(http_request_duration_seconds_bucket[5m]))
)

# 过去 1 小时 CPU 平均使用率 by 实例
avg by (instance) (rate(node_cpu_seconds_total{mode!="idle"}[1h]))

# 预测磁盘 4 小时后是否会满
predict_linear(node_filesystem_free_bytes[1h], 4 * 3600) < 0

# 对比昨天同时段
sum(rate(http_requests_total[5m]))
  -
sum(rate(http_requests_total[5m] offset 1d))
```

### 3.3 Recording Rules 预计算

复杂查询提前计算，避免每次查询都重算：

```yaml
# /etc/prometheus/rules.yml
groups:
  - name: http.recording
    interval: 30s
    rules:
      - record: job:http_requests:rate5m
        expr: sum by (job, route) (rate(http_requests_total[5m]))

      - record: job:http_error_rate:ratio5m
        expr: |
          sum by (job) (rate(http_requests_total{status=~"5.."}[5m]))
          /
          sum by (job) (rate(http_requests_total[5m]))
```

## 4. Alerting Rules

```yaml
groups:
  - name: slo.alerts
    rules:
      # 错误率 SLO：过去 5 分钟错误率 > 1%
      - alert: HighErrorRate
        expr: |
          job:http_error_rate:ratio5m > 0.01
        for: 5m
        labels:
          severity: page
          team: platform
        annotations:
          summary: "{{ $labels.job }} 错误率 {{ $value | humanizePercentage }}"
          runbook: "https://runbooks.example.com/high-error-rate"

      # P99 延迟 > 1s 持续 10 分钟
      - alert: HighLatencyP99
        expr: |
          histogram_quantile(0.99,
            sum by (le, job) (rate(http_request_duration_seconds_bucket[5m]))
          ) > 1
        for: 10m
        labels:
          severity: ticket

      # 磁盘 2 小时内会满
      - alert: DiskWillFill
        expr: |
          predict_linear(node_filesystem_free_bytes[1h], 2 * 3600) < 0
        for: 15m
        labels:
          severity: page
```

## 5. Alertmanager 路由

```yaml
# alertmanager.yml
route:
  receiver: default
  group_by: [alertname, cluster]
  group_wait: 30s          # 首次等 30s 聚合同组告警
  group_interval: 5m       # 同组新告警通知间隔
  repeat_interval: 4h      # 未解决告警的重复提醒间隔

  routes:
    # 半夜只 PagerDuty，不发 Slack
    - matchers: [severity="page"]
      receiver: pagerduty
      continue: true

    # Ticket 级别发 Jira
    - matchers: [severity="ticket"]
      receiver: jira

    # 静默维护窗口
    - matchers: [team="data-platform"]
      active_time_intervals: [business-hours]
      receiver: slack-data-platform

receivers:
  - name: pagerduty
    pagerduty_configs:
      - service_key: xxx

  - name: slack-data-platform
    slack_configs:
      - channel: '#data-oncall'
        send_resolved: true

time_intervals:
  - name: business-hours
    time_intervals:
      - weekdays: [monday:friday]
        times:
          - start_time: 09:00
            end_time: 18:00
        location: Asia/Shanghai
```

## 6. 大规模 Prometheus：Thanos / Mimir / VictoriaMetrics

单机 Prometheus 的天花板大约是 **100 万活跃时间序列 + 本地 15 天存储**。超过要做长期存储和高可用：

| 方案 | 特点 |
|------|------|
| **Thanos** | Prometheus Sidecar 模式，S3 做长期存储，全局查询 |
| **Grafana Mimir** | 多租户，Helm 部署简单，Grafana 生态一体 |
| **VictoriaMetrics** | 性能最好，单体或集群都行，资源消耗最低 |
| **Cortex** | 多租户先驱，Mimir 的前身，Grafana 已推荐切 Mimir |

**2026 年选型建议**：
- 中小规模（<1000 万时间序列）：**VictoriaMetrics 单节点或集群**
- 大规模、多租户：**Mimir**
- 已有 S3 基础设施、只要长期存储：**Thanos**

## 7. Grafana 13 实战要点

### 7.1 Dashboard as Code

```json
{
  "title": "Order Service Overview",
  "panels": [
    {
      "title": "QPS",
      "type": "timeseries",
      "targets": [{
        "expr": "sum by (route) (rate(http_requests_total{service=\"order\"}[5m]))"
      }]
    }
  ]
}
```

用 Grafonnet（Jsonnet）或 Grafana Terraform Provider 把 Dashboard 纳入 GitOps。

### 7.2 2026 年 Grafana 新能力

- **Scenes（动态面板）**：面板可以用代码组合和复用
- **Explore Logs / Explore Traces**：LogQL、TraceQL 零学习成本查询
- **Grafana LLM App**：Dashboard 中直接嵌入 LLM 问答，自然语言查询
- **Correlations**：Logs ↔ Traces ↔ Metrics 一键跳转
- **Adaptive Metrics**：自动识别无人查询的指标并降采样，省存储
- **Alert Activity（13.1）**：把告警状态历史、静默与规则上下文放进同一条工作流，减少值班时在多个页面来回切换
- **Mimir Alertmanager Auto-sync（13.1）**：Grafana 设置页可直接同步 Mimir Alertmanager 配置，减轻多租户环境下的手工配置成本

## 8. RED / USE 仪表盘模板

一个标准服务 Dashboard 只需要 4 行：

```
第一行：RED（服务黄金指标）
├─ Request Rate（QPS）
├─ Error Rate
├─ Duration P50/P95/P99
└─ Saturation（队列长度、线程池利用率）

第二行：运行时
├─ CPU / Memory / GC
├─ DB 连接池
├─ 缓存命中率
└─ 下游依赖延迟

第三行：业务
├─ 订单创建数
├─ 支付成功率
└─ 客户活跃度

第四行：基础设施
├─ Node CPU / Memory / Disk
├─ 网络带宽
└─ Pod 数量
```

## 9. 生产检查清单

```
上线前：
☐ 服务暴露 /metrics 端点（OTel 或 Prometheus client）
☐ Scrape 间隔 15-30s
☐ Recording Rules 覆盖复杂查询
☐ Alerting Rules 覆盖 SLO 目标
☐ Alertmanager 路由配置（分级、静默）
☐ Grafana Dashboard（RED + USE + 业务）
☐ 长期存储方案（VictoriaMetrics/Mimir/Thanos）
☐ 告警抑制规则（防告警风暴）
☐ Runbook 链接在告警里
☐ 同事能看懂 Dashboard（一眼定位问题）
```

## 📖 参考资料

- [Prometheus 官方文档](https://prometheus.io/docs/introduction/overview/)
- [PromQL Examples](https://promlabs.com/promql-cheat-sheet/)
- [Grafana Documentation](https://grafana.com/docs/)
- [SRE Workbook - Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
- [VictoriaMetrics 与 Prometheus 对比](https://docs.victoriametrics.com/)

## 8. 2026 年版本演进

> 🔄 更新于 2026-05-13

### 8.1 Prometheus 3.9.x

Prometheus 3.x 在 2025 年底发布，核心新特性是 **Native Histograms**（原生直方图）成为标准功能。使用指数桶边界，无需手动配置桶，自动适应数据分布，显著减少存储和配置复杂度。来源：[dasroot.net](https://dasroot.net/posts/2026/02/go-observability-stack-prometheus-grafana-opentelemetry/)

### 8.2 Grafana 12.x / 13.1

| 版本 | 发布时间 | 核心特性 |
|------|---------|---------|
| 12.0 | 2025-04 | Drilldown GA（Explore Metrics/Logs/Traces）、Grafana-managed alerts GA、Git Sync 预览、SQL Expressions、SCIM sync |
| 12.2 | 2025-08 | 增强 ad hoc 过滤、重新设计的 Table 可视化 |
| 12.4 | 2025-12 | Dynamic Dashboards、模板驱动工作流、Observability as Code 更新 |
| 13.0 | 2026-04 | 解决"空白光标问题"——帮助团队更快上手并从数据中获取洞察 |
| 13.1 | 2026-07 | Alert Activity、Mimir Alertmanager auto-sync、色盲友好图表填充、告警权限收紧 |

来源：[Grafana What's New](https://grafana.com/docs/grafana/latest/whatsnew/)、[Releasebot](https://releasebot.io/updates/grafana)

**Grafana 12.0 关键改进**：
- **Drilldown GA**：无需写 PromQL/LogQL 即可探索 Prometheus 指标和 Loki 日志
- **Git Sync 预览**：Dashboard 直接同步到 GitHub 仓库
- **新 Terraform Provider + CLI**：Dashboard as Code 完整工具链
- **SQL Expressions**：在 Dashboard 中直接用 SQL 转换数据

### 8.3 Prometheus 3.13 新特性

> 🔄 更新于 2026-07-07

Prometheus **3.13.0** 于 **2026-07-01** 发布，并被标注为一条 **LTS** 版本线。对工程团队最重要的不是单个语法糖，而是 3.x 线进入更稳的生产节奏：原生直方图、Remote Write v2、distroless 镜像和近期 PromQL 演进可以按 LTS 节点统一落地，而不必追每个小版本。来源：[Prometheus 3.13.0 Release](https://github.com/prometheus/prometheus/releases/tag/v3.13.0)、[Prometheus Download](https://prometheus.io/download/)

```promql
# 旧问题：A and on(label) B 中如果某些标签组合在 B 里不存在，结果直接消失
# 新方案：fill() 让缺失序列得到默认值

# 例子：错误率（失败率） / 总请求率，希望没有错误的服务也能显示 0
sum by (service) (rate(http_errors_total[5m]))
  /
sum by (service) (rate(http_requests_total[5m]))

# 新版本可以这样保留所有 service：
fill(
  sum by (service) (rate(http_errors_total[5m])),
  default=0
)
  /
sum by (service) (rate(http_requests_total[5m]))
```

`fill_left()` / `fill_right()` 控制填充方向，对 `or` / `unless` / `and` 等二元运算特别有用；在 3.13 LTS 上已经可以把这些 3.x 新能力当成默认基线，而不是实验特性。

**其他改进**：
- **Distroless Docker 镜像**：除默认 busybox 镜像外，新增 distroless 变体，攻击面更小、镜像更小
- **OpenMetrics 2.0 进展**：原生直方图与 OpenMetrics 协议对齐
- **Remote Write v2 持续完善**：减少远程写入开销

### 8.4 Grafana 13 / 13.1 发布节奏

> 🔄 更新于 2026-07-07

Grafana 13 于 2026-04 在 GrafanaCON 2026 发布，**Grafana 13.1.0** 又在 **2026-07-01** 推出一轮更适合生产团队感知的增强：Alert Activity、Mimir Alertmanager auto-sync、告警权限收紧和图表无障碍改进。来源：[Grafana Releases](https://github.com/grafana/grafana/releases)、[Grafana 13 Blog](https://grafana.com/blog/grafana-13-release-all-the-latest-features/)

**核心改进**：

| 维度 | 改进 | 数据 |
|------|------|------|
| Loki 架构 | Kafka 后端日志接入 | 数据扫描量减少最高 20x，查询提速最高 10x |
| Grafana 体验 | 新版 Dashboard 编辑器、Explore Metrics 升级、Alert Activity | 从“看图”走向“看图 + 值班动作”一体化 |
| OpenTelemetry 路径 | Linux/K8s 自动 OTel 采集 | 简化指标 + 日志 + 追踪上手 |
| GCX CLI | 全新 Observability CLI | 把观测性嵌入 IDE / Coding Agent |

**Kafka-backed Loki**：将日志写入路径前置到 Kafka，消除了之前 Ingester 的内存压力，对日志量大的场景（每秒 GB 级）是质变。来源：[TechMonk India](https://techmonk.economictimes.indiatimes.com/news/software-devops/grafana-13-introduces-kafka-backed-loki-and-new-observability-cli/130482002)

**GCX CLI**：

```bash
# 在 IDE / Coding Agent 中查询观测性数据
gcx query --from "now-1h" --query 'rate(http_errors_total[5m])'

# 让 Claude Code / Cursor 直接读取 Grafana 数据
gcx mcp serve  # 暴露 MCP Server
```

GCX 是 Grafana 拥抱 AI Agent 工作流的关键产品——观测性数据成为 Agent 的"长期记忆"。

**升级建议**：

```
Grafana 12.x  →  Grafana 13.1
├─ Loki 用户：评估 Kafka 后端（生产前先在 staging 验证）
├─ K8s 用户：检查 OTel 自动采集是否覆盖现有 Prometheus 指标
├─ AI 团队：试用 GCX CLI 把观测性接入 Coding Agent
└─ 企业用户：若重视值班体验与 Mimir 一体化，可以直接评估 13.1；极保守团队仍可等待 13.x 更长维护窗口
```

> 更新于 2026-07-09

**Prometheus 3.13 LTS + OTel Collector v0.156**（2026-07）组合建议：

- Prometheus 3.13 LTS 适合按季度规划升级；与 OTel Collector remote write 保持兼容
- Collector v0.156.0（07-07）为当前最新；declarative config 1.0 可用 GitOps 管理采集管道
- Grafana 13.1 Alert Activity 减少值班切页；与 Mimir Alertmanager auto-sync 适合多区域部署

> 来源：[OTel Collector v0.156.0](https://github.com/open-telemetry/opentelemetry-collector/releases/tag/v0.156.0)、[Prometheus 3.13 LTS](https://github.com/prometheus/prometheus/releases)
