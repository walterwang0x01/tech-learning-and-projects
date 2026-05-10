# 日志聚合 Loki 与 ELK

> Author: Walter Wang

<!-- version-check: Loki 3.x, Elasticsearch 9.x, Fluent Bit 3.x, Vector 0.44, checked 2026-05-10 -->

## 1. 方案对比

```
┌────────── Loki vs ELK ──────────┐
│                                  │
│  Loki（Grafana Labs）            │
│  ├─ 标签索引 + 原始日志存 S3       │
│  ├─ 成本最低（10x 便宜于 ES）      │
│  ├─ LogQL 语法类似 PromQL         │
│  └─ 和 Grafana 深度集成            │
│                                  │
│  ELK / Elastic Stack             │
│  ├─ 全文倒排索引                  │
│  ├─ 查询最灵活                    │
│  ├─ 存储和计算成本高               │
│  └─ 适合需要全文搜索的场景          │
│                                  │
│  OpenSearch                      │
│  ├─ AWS 主导的 ES fork            │
│  └─ 特性接近 ES 7.x                │
└──────────────────────────────────┘
```

**2026 年选型建议**：
- **偏运维日志**（应用日志、审计日志）→ Loki（成本优势太大）
- **需要全文搜索、复杂分析**（APM、业务日志）→ ES / OpenSearch
- **超大规模**（PB 级）→ ClickHouse（SigNoz、Uptrace 的选择）

## 2. 结构化日志是前提

```python
# ❌ 字符串日志：后期分析地狱
logger.info(f"User {user.id} placed order {order.id} with amount {amount}")

# ✅ 结构化日志（JSON）
import structlog
logger = structlog.get_logger()
logger.info("order_placed",
    user_id=user.id,
    order_id=order.id,
    amount=amount,
    trace_id=get_trace_id(),
)
# 输出：{"event":"order_placed","user_id":"u1","order_id":"o1","amount":99.9,"trace_id":"..."}
```

Java/Go/Node.js 都有对应的结构化日志库（Logback JSON encoder、zap、pino 等）。

## 3. Loki 生产部署

```
┌───────── Loki 架构 ─────────┐
│                              │
│  App → Promtail/Alloy/       │
│        Fluent Bit/Vector     │
│          │                   │
│          ▼                   │
│       Loki（压缩 + 标签索引）   │
│          │                   │
│          ▼                   │
│       S3 / GCS / MinIO       │
│          │                   │
│          ▼                   │
│     Grafana（查询 + 可视化）   │
└─────────────────────────────┘
```

### 3.1 LogQL 核心语法

```logql
# 选择器 + 过滤
{service="order", env="prod"} |= "ERROR"

# JSON 解析并过滤字段
{service="order"} | json | user_id = "u1"

# 统计错误率
sum by (service) (
  rate({env="prod"} |= "ERROR" [5m])
)
/
sum by (service) (
  rate({env="prod"} [5m])
)

# 提取数值聚合（如请求时延）
{service="order"} | json | unwrap duration_ms | rate(5m)

# 模式挖掘（类似日志分组）
{service="order"} |~ "error.*timeout" |> pattern `<level> <msg> <kv>`
```

### 3.2 Promtail / Grafana Alloy 配置

Grafana Alloy（2024 年发布，Grafana Agent 的继任者）是当前推荐的采集器：

```river
// alloy.river
loki.source.kubernetes_events "default" {
  forward_to = [loki.write.default.receiver]
}

discovery.kubernetes "pods" {
  role = "pod"
}

loki.source.kubernetes "pods" {
  targets    = discovery.kubernetes.pods.targets
  forward_to = [loki.process.parse.receiver]
}

loki.process "parse" {
  // 自动解析 JSON 日志
  stage.json {
    expressions = {
      level = "",
      trace_id = "",
      user_id = "",
    }
  }
  // 只把 level 作为标签（高基数 user_id 不作为标签！）
  stage.labels {
    values = { level = "" }
  }
  forward_to = [loki.write.default.receiver]
}

loki.write "default" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}
```

**关键**：把 user_id 作为 JSON 字段保留（可过滤），但**不要**作为标签（会爆索引）。

## 4. Elasticsearch 生产部署要点

### 4.1 索引生命周期管理（ILM）

```json
PUT _ilm/policy/logs-policy
{
  "policy": {
    "phases": {
      "hot": {
        "actions": {
          "rollover": { "max_size": "50gb", "max_age": "1d" },
          "set_priority": { "priority": 100 }
        }
      },
      "warm": {
        "min_age": "7d",
        "actions": {
          "shrink": { "number_of_shards": 1 },
          "forcemerge": { "max_num_segments": 1 },
          "set_priority": { "priority": 50 }
        }
      },
      "cold": {
        "min_age": "30d",
        "actions": {
          "searchable_snapshot": { "snapshot_repository": "s3-backup" }
        }
      },
      "delete": {
        "min_age": "90d",
        "actions": { "delete": {} }
      }
    }
  }
}
```

热/温/冷三层存储让成本可控。

### 4.2 Index Template

```json
PUT _index_template/logs-template
{
  "index_patterns": ["logs-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "refresh_interval": "30s",
      "index.lifecycle.name": "logs-policy"
    },
    "mappings": {
      "dynamic_templates": [{
        "strings_as_keywords": {
          "match_mapping_type": "string",
          "mapping": { "type": "keyword", "ignore_above": 256 }
        }
      }],
      "properties": {
        "@timestamp": { "type": "date" },
        "level": { "type": "keyword" },
        "message": { "type": "text" },
        "trace_id": { "type": "keyword" },
        "service": { "type": "keyword" }
      }
    }
  }
}
```

**注意**：默认把 string 映射为 keyword，需要全文搜索的字段单独声明为 `text`，否则索引爆炸。

## 5. 日志采集器对比

| 工具 | 语言 | 性能 | 生态 | 适用场景 |
|------|------|------|------|----------|
| **Fluent Bit** | C | ⭐⭐⭐⭐⭐ | 广 | 通用采集，K8s DaemonSet 首选 |
| **Vector** | Rust | ⭐⭐⭐⭐⭐ | 中 | 复杂处理管道，高性能 |
| **Grafana Alloy** | Go | ⭐⭐⭐⭐ | Grafana 生态 | Prometheus/Loki 全家桶 |
| **OTel Collector** | Go | ⭐⭐⭐⭐ | 标准 | 统一 M/T/L 采集 |
| **Logstash** | JVM | ⭐⭐ | ES 生态 | 过时，只在 Elastic 老架构中见 |

2026 年推荐：**OTel Collector 作为中心网关**，边缘用 **Fluent Bit 或 Alloy** 做采集。

## 6. 日志、指标、追踪关联

关键原则：**trace_id 是黏合剂**。

```
看到告警 →
  点击看 Metric 图表 →
    发现某时段异常 →
      跳转 Logs 查看那段时间的错误日志 →
        从日志里拿 trace_id →
          跳转 Trace 查看完整请求链路 →
            定位到具体的下游服务和 Span
```

Grafana 的 Explore 和 Correlations 功能专门优化这个跳转链路。

## 7. 常见坑

```
日志系统反模式：
├─ 把 ID/UUID 作为 ES keyword 索引
│   → 倒排索引爆炸，磁盘飙升
├─ 生产日志保留 365 天
│   → 90% 的日志永远不会被查
├─ 日志里存整个请求体（含大 JSON）
│   → 带宽爆炸 + 查询慢
├─ 不做采样，DEBUG 日志全部保留
│   → 生产开销大，信号淹没在噪音里
├─ 在日志里写敏感信息（密码、token）
│   → 合规事故
└─ 日志采集失败时直接丢弃
    → 关键错误日志消失

推荐：
├─ 用 trace_id 串联，不要重复写业务上下文
├─ ERROR 全量、INFO 采样、DEBUG 关闭或极低采样
├─ 大字段脱敏或截断
├─ 关键业务日志双写（Loki + 业务库备份）
└─ 采集链路设置 buffer 和 disk fallback
```

## 8. 生产检查清单

```
☐ 日志结构化（JSON）
☐ trace_id 注入到每条日志
☐ 敏感字段脱敏（password、token、身份证）
☐ 日志级别分级（ERROR 全量、INFO 采样）
☐ 保留策略明确（热/温/冷/删除）
☐ 告警不依赖日志（用指标告警，日志只做定位）
☐ Grafana Explore 可以从 Trace/Metric 跳转
☐ 采集器健康监控（drop rate、延迟）
☐ 日志成本可观（按 GB/天 监控）
```

## 📖 参考资料

- [Loki 官方文档](https://grafana.com/docs/loki/latest/)
- [LogQL 语法](https://grafana.com/docs/loki/latest/query/)
- [Elasticsearch ILM](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-lifecycle-management.html)
- [Grafana Alloy](https://grafana.com/docs/alloy/latest/)
- [Vector 文档](https://vector.dev/docs/)
