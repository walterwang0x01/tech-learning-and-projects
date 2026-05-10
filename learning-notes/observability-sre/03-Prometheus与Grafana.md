# Prometheus 与 Grafana

> Author: Walter Wang

<!-- version-check: Prometheus 3.x, Grafana 11.x, Alertmanager 0.28, checked 2026-05-10 -->

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

## 7. Grafana 11 实战要点

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
