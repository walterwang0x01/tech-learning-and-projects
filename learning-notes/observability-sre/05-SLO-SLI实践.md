# SLO/SLI 实践

> Author: Walter Wang

<!-- version-check: SRE practices 2026, Error Budget, checked 2026-05-22 -->

## 1. 为什么要 SLO

没有 SLO 的团队，长期会陷入两种极端：

```
极端 A：过度可用性追求
  任何 bug 都要立即修 → 开发被运维压垮 → 创新停滞

极端 B：无人关心可用性
  功能排期无休止 → 线上问题累积 → 信任崩塌

SLO 解决的问题：
  把"可用性"变成可量化的工程目标
  给产品/研发/运维一个共同的数字
```

## 2. 核心概念

```
SLI（Service Level Indicator）
  指标本身，如"过去 30 天成功的 HTTP 请求比例"

SLO（Service Level Objective）
  内部目标，如"SLI >= 99.9%"

SLA（Service Level Agreement）
  对外合同，如"承诺 99.5%，违反赔偿"

关系：SLA ≤ SLO ≤ SLI 实际值
     对外承诺比内部目标松，内部目标比实际要严
```

## 3. 设计 SLI 的三个典型场景

### 3.1 请求类服务

```
SLI = 成功请求数 / 有效请求数

"成功"定义示例：
  - HTTP 状态码 < 500
  - 时延 < 500ms
  - 业务层面的 status_code == "OK"

重要：排除非用户请求
  - 健康检查
  - 运维扫描
  - 内部任务
```

### 3.2 数据处理类

```
SLI = 按时处理的数据量 / 总数据量

例如：日志管道
  "按时"= 产生后 30 秒内被索引
  SLO：99% 的日志在 30s 内可查询
```

### 3.3 存储类

```
SLI = 成功读写次数 / 总次数（分读和写）

分位数友好：
  读操作 P99 < 50ms，SLO 99.9%
  写操作 P99 < 200ms，SLO 99.5%
```

## 4. 错误预算（Error Budget）

这是 Google SRE 最有价值的概念之一。

```
如果 SLO = 99.9%（30 天）：
  允许的错误时间 = 30 天 × 0.1% = 43 分 12 秒
  这 43 分钟就是"错误预算"

  花在哪里由研发决定：
  ├─ 新功能上线出 bug 消耗了 20 分钟 ✓
  ├─ 数据库迁移故障消耗了 10 分钟 ✓
  ├─ 灰度发布占用 5 分钟 ✓
  └─ 剩 8 分钟 → 本月还能激进发布

  如果预算耗尽：
  ├─ 冻结非必要发布
  ├─ 团队优先修复稳定性问题
  └─ 下月预算重置
```

**错误预算让 SRE 和研发有了共同语言**：不再争"可不可靠""稳不稳定"，而是"预算还剩多少"。

## 5. 基于 SLO 的多窗口多燃烧率告警

传统告警："错误率 > 1% 持续 5 分钟 → 告警" 的问题：
- 阈值拍脑袋定，和 SLO 无关
- 误报多（瞬时抖动）
- 漏报多（慢慢烧掉预算的"温水煮青蛙"）

**基于错误预算的告警**更精准：

```
燃烧率（burn rate）= 当前错误率 / SLO 允许的错误率

如果 1 小时的燃烧率 = 14.4：
  1 小时就消耗了 2% 的月预算 → 严重，需要立即响应

如果 6 小时的燃烧率 = 6：
  6 小时消耗 5% 预算 → 次严重

如果 24 小时的燃烧率 = 3：
  消耗 10% 预算 → 一般警告，工作时间处理
```

Prometheus 实现：

```yaml
# 计算 30 天窗口的燃烧率
- record: slo:http_availability:burn_rate1h
  expr: |
    (
      sum(rate(http_requests_total{status=~"5.."}[1h]))
      /
      sum(rate(http_requests_total[1h]))
    ) / (1 - 0.999)   # SLO = 99.9%

- record: slo:http_availability:burn_rate6h
  expr: |
    (
      sum(rate(http_requests_total{status=~"5.."}[6h]))
      /
      sum(rate(http_requests_total[6h]))
    ) / (1 - 0.999)

# 多窗口联合告警：避免假阳性和假阴性
- alert: SLOBurnRateFast
  expr: |
    slo:http_availability:burn_rate1h > 14.4
    and
    slo:http_availability:burn_rate5m > 14.4
  for: 2m
  labels:
    severity: page
  annotations:
    summary: "高速消耗错误预算：1h 内已烧 2% 月预算"

- alert: SLOBurnRateSlow
  expr: |
    slo:http_availability:burn_rate6h > 6
    and
    slo:http_availability:burn_rate30m > 6
  for: 15m
  labels:
    severity: ticket
  annotations:
    summary: "中速消耗错误预算：6h 内已烧 5% 月预算"
```

## 6. SLO 治理流程

```
季度 SLO Review：
├─ 1. 收集过去一季度 SLI 实际值
├─ 2. 检查预算消耗，找出消耗大户
├─ 3. 调整 SLO（收紧或放松都可以）
│     - 持续达标 → 收紧目标
│     - 连续未达 → 研发补齐稳定性债务
├─ 4. 更新告警阈值
└─ 5. 同步到所有 Stakeholder
```

## 7. 工具生态

```
SLO as Code：
├─ Sloth（Prometheus 原生）：YAML → 生成 recording/alerting rules
├─ OpenSLO：Spec 规范，多后端支持
├─ Nobl9（SaaS）：可视化 SLO 管理
└─ Grafana SLO：Grafana 11+ 内置

使用 Sloth 示例：
  slos:
    - name: http-availability
      objective: 99.9
      sli:
        events:
          error_query: sum(rate(http_requests_total{status=~"5.."}[{{.window}}]))
          total_query: sum(rate(http_requests_total[{{.window}}]))
      alerting:
        name: HTTPAvailability
        page_alert:
          labels: {severity: page}
        ticket_alert:
          labels: {severity: ticket}
```

Sloth 会自动生成多窗口多燃烧率的告警规则，不用手写。

## 8. 常见陷阱

```
反模式：
├─ 把 SLO 定得太激进（99.999%）
│   → 和商业价值不匹配，永远达不到
├─ 把 SLI 定得太复杂（5 个维度 AND）
│   → 没人能说清楚，也没人能调试
├─ SLO 制定后不复盘
│   → 变成摆设，最后被团队遗忘
├─ 不告知产品经理 SLO 目标
│   → 新功能继续超速上线，预算频繁烧光
└─ "全年 99.9%"而非滚动窗口
    → 年初挥霍，年末紧张；滚动窗口公平得多

推荐：
├─ 从 99% 或 99.5% 开始，逐步收紧
├─ SLI 公式简单（1-2 个条件）
├─ 30 天滚动窗口
├─ 每季度 Review 一次
└─ 错误预算耗尽时真的冻结发布
```

## 9. 可靠性不等同于可用性

Google SRE 书里的经典段子：

```
产品经理："我们要 100% 可用"

SRE："那就别发布。因为：
  1. 每次发布都有风险
  2. 依赖的 AWS 也不是 100%
  3. 100% 和 99.99% 成本差 10 倍，收益差 0

  我们来谈谈你真正需要多少个 9，以及你愿意为此付什么代价。"
```

## 📖 参考资料

- [Google SRE Workbook - Implementing SLOs](https://sre.google/workbook/implementing-slos/)
- [Google SRE Workbook - Alerting on SLOs](https://sre.google/workbook/alerting-on-slos/)
- [The Site Reliability Workbook (O'Reilly)](https://sre.google/workbook/table-of-contents/)
- [Sloth Documentation](https://sloth.dev/)
- [OpenSLO](https://openslo.com/)
