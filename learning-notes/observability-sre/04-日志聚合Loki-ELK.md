# 日志聚合 Loki 与 ELK

> Author: Walter Wang

<!-- version-check: Loki 3.x stable, Loki 4.0 architecture (Kafka + DataObject), Elasticsearch 9.x, Fluent Bit 3.x, Vector 0.44, GrafanaCON 2026, checked 2026-05-20 -->

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

## 9. Loki 4.0 与 Kafka-backed 架构（GrafanaCON 2026）

> 🔄 更新于 2026-05-20

<!-- version-check: Loki 4.0 architecture (Kafka-backed, DataObject columnar storage), Grafana 13 GrafanaCON 2026 (2026-04-21 Barcelona), checked 2026-05-20 -->

GrafanaCON 2026（2026-04-21 巴塞罗那）发布的 Grafana 13 把 Loki 推向 4.0 架构方向，**核心变化是从单层"标签索引 + 对象存储"演进为"Kafka 摄取 + 列式 DataObject 存储 + 重写查询引擎"**。这是 Loki 自 3.0（2024）以来最大的架构重写。来源：[Inside Loki's new architecture for faster logging at petabyte scale](https://www.grafana.com/events/grafanacon/agenda/loki-petabyte-scale-logging-architecture/)、[InfoQ: Grafana Rearchitects Loki with Kafka and Ships a CLI](https://www.infoq.com/news/2026/04/grafana-loki-ai-agents/)、[The Road to Loki 4.0 — Loki Community Call June 2025](https://nicolevanderhoeven.com/blog/20250624-lcc-the-road-to-loki-4_0/)

### 9.1 四大架构变化

```
旧架构（Loki 2.x / 3.x）:
  Distributor → Ingester (in-memory) → Object Store (chunks)
                                       └─ Index (BoltDB / TSDB)
  Querier → Index → Chunks → 解压 → 行扫描

新架构（Loki 4.0 方向，已部分在 Loki 3.x 实验启用）:
  Distributor → Kafka (RF-1 持久化) → Ingester → DataObject (列式) → Object Store
                                                                     ├─ 结构化元数据列
                                                                     └─ 日志正文列
  Query Planner → Scheduler → 跨分区并行扫描 → 列裁剪 → 仅读必要列
```

| 维度 | Loki 3.x | Loki 4.0 方向 |
|------|----------|---------------|
| 摄取持久化 | Ingester 副本（RF-3） | **Kafka 单副本（RF-1）**——Kafka 自身保证持久化 |
| 存储格式 | Chunk（行式） | **DataObject（列式）**——结构化元数据成为独立列 |
| 索引 | TSDB | DataObject 内嵌轻量索引（无需独立 BoltDB） |
| 查询并行度 | 按 chunk 分区 | **按 DataObject 列 + Kafka 分区两层并行** |
| 部署模式 | SSD（Simple Scalable）/ Microservices | SSD 模式**计划在 4.0 前废弃**，统一为 Microservices |
| 数据扫描量（同等查询） | 100% | **5%**（20x 减少） |
| 聚合查询延迟 | 1x | **0.1x**（10x 提速） |

### 9.2 DataObject 列式存储

Loki 4.0 引入新的存储格式 **DataObject**，把结构化元数据（labels、structured metadata）从行内存储改为独立列：

```
DataObject 物理布局:
┌──────────────────────────────────────────────────┐
│ Header                                            │
├──────────────────────────────────────────────────┤
│ Column: timestamp        (delta + zstd)          │
│ Column: trace_id         (dictionary + zstd)     │
│ Column: user_id          (dictionary + zstd)     │
│ Column: status_code      (RLE + zstd)            │
│ Column: log_line         (zstd)                  │
├──────────────────────────────────────────────────┤
│ Footer + 列偏移索引                                │
└──────────────────────────────────────────────────┘
```

**好处**：

- **列裁剪**：查询 `trace_id="..."` 只读 timestamp + trace_id 列，不必解压 log_line
- **更高压缩率**：同列数据相似度高，zstd 压缩率比行式格式高 30-50%
- **结构化元数据天然查询**：之前 structured metadata 必须 parse 后才能过滤，现在可以直接走列扫描

来源：[The Road to Loki 4.0 with Ed Welch](https://notes.nicolevanderhoeven.com/system/cards/The+Road+to+Loki+4.0+with+Ed+Welch+-+Loki+Community+Call+June+2025)

### 9.3 Kafka-backed 摄取路径

```yaml
# loki-config.yaml — Kafka 摄取（4.0 方向，3.5+ 实验性可用）
ingester:
  kafka:
    enabled: true
    brokers: ["kafka-0:9092", "kafka-1:9092", "kafka-2:9092"]
    topic: loki-ingest
    # Kafka 已经保证 RF-3 副本，Loki 自身只需 RF-1
    replication_factor: 1
  flush_period: 30s
  max_chunk_age: 1h

storage_config:
  # DataObject 存储仍写到对象存储（S3/GCS/Azure Blob）
  object_store:
    type: s3
    s3:
      bucket: loki-data-objects
      region: us-east-1
```

**收益**：

| 项 | 旧（Ingester RF-3） | 新（Kafka RF-1） |
|----|---------------------|------------------|
| Ingester 内存占用 | 高（每副本一份） | 低（单副本+ Kafka 缓冲） |
| 重启恢复 | 慢（需要从其他副本拉取 WAL） | 快（从 Kafka offset 重放） |
| 跨可用区成本 | 高（3 副本网络写入） | 低（Kafka 自身分区） |
| 端到端延迟 | <10s | <30s（Kafka 引入额外一跳，但仍 P99 < 1min） |

### 9.4 SSD 模式废弃路径

Loki 自 2024 起标记 **Simple Scalable Deployment (SSD) 模式将在 Loki 4.0 前废弃**，新部署应直接使用：

- **Monolithic（单二进制）**：开发 / 小规模 / Demo
- **Microservices（分布式）**：生产 / 大规模 / 多租户

来源：[Upgrade the Helm chart to 6.0](https://grafana.com/docs/loki/latest/setup/upgrade/upgrade-to-6x/)、[Install the simple scalable Helm chart](https://grafana.com/docs/loki/latest/setup/install/helm/install-scalable/)

### 9.5 适配建议（2026 H2）

| 当前 Loki 版本 | 建议 |
|----------------|------|
| 2.9.x | 升级到 3.x microservices，避免 SSD 模式 |
| 3.0 / 3.5 | 持续保持 microservices，跟踪 4.0 RC（预计 2026 Q4） |
| Loki + Helm chart 6.x SSD 模式 | **开始迁移到 microservices**，4.0 不再支持 SSD |
| 自建 ELK / OpenSearch | 评估 Loki 4.0 是否能取代——大多数运维日志场景成本下降 10x |

> Grafana 13 同步发布 **GCX CLI**（`gcx query` / `gcx mcp serve`），让 Coding Agent / IDE 可以直接通过 MCP 协议查询日志，把"日志故障定位"嵌入开发工作流。这部分详见可观测性平台详解。

## 📖 参考资料

- [Loki 官方文档](https://grafana.com/docs/loki/latest/)
- [LogQL 语法](https://grafana.com/docs/loki/latest/query/)
- [Elasticsearch ILM](https://www.elastic.co/guide/en/elasticsearch/reference/current/index-lifecycle-management.html)
- [Grafana Alloy](https://grafana.com/docs/alloy/latest/)
- [Vector 文档](https://vector.dev/docs/)
- [Inside Loki's new architecture — GrafanaCON 2026](https://www.grafana.com/events/grafanacon/agenda/loki-petabyte-scale-logging-architecture/)
