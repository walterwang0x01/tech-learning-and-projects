# 事件响应与 Postmortem

> Author: Walter Wang

<!-- version-check: Grafana 13.1.0 Alert Activity, Grafana IRM, Incident response best practices 2026, checked 2026-07-08 -->

## 1. 事件响应的目标

```
事件响应不是"找出谁错了"，而是：
  1. 尽快恢复服务
  2. 把事故变成组织的学习资产
  3. 改进系统，让同类事故不再发生
```

## 2. 事件分级

```
┌─────── 参考分级（按业务影响）───────┐
│                                     │
│  SEV-1 核心功能不可用，收入损失         │
│    响应时间：立即                     │
│    通知：On-call + 相关团队 + 管理层   │
│    Postmortem：强制                   │
│                                     │
│  SEV-2 部分功能降级，用户体验受损       │
│    响应时间：15 分钟内                 │
│    通知：On-call + 相关团队            │
│    Postmortem：推荐                   │
│                                     │
│  SEV-3 局部问题，少量用户受影响         │
│    响应时间：工作时间内                │
│    通知：On-call                     │
│    Postmortem：可选                   │
│                                     │
│  SEV-4 潜在风险，无用户影响            │
│    响应时间：下一个工作日              │
│    通知：Ticket                      │
│    Postmortem：可选                   │
└─────────────────────────────────────┘
```

## 3. 事件响应角色

```
Incident Commander (IC)
  ├─ 总指挥，决策优先级
  ├─ 负责协调，不亲自动手
  └─ 定期对外更新状态

Technical Lead
  ├─ 技术决策
  ├─ 实际排查和修复
  └─ 向 IC 汇报

Communications Lead
  ├─ 对内对外沟通
  ├─ 状态页更新
  └─ 客户支持协调

Scribe（记录员）
  ├─ 记录所有行动和时间线
  ├─ 为 Postmortem 提供素材
  └─ 可以是 On-call 或任何在场者
```

小团队可以一人多角，但 IC 必须独立（否则会陷入技术细节）。

## 4. 响应流程

```
检测（Detection）
  └─ 告警触发 / 用户报告 / 监控异常

升级（Escalation）
  └─ On-call 确认 → 定级 → 召集 IC 和团队

诊断（Diagnosis）
  ├─ 查看近期变更（部署、配置）
  ├─ Grafana Alert Activity（13.1）查看告警历史、静默与规则上下文
  ├─ 查看 Metric 异常点
  ├─ 看 Error Logs
  └─ 看 Trace 异常链路

缓解（Mitigation）
  ├─ 先止血，不追求根因
  ├─ 回滚最近的变更
  ├─ 降级 / 熔断
  └─ 扩容

恢复（Recovery）
  └─ 服务完全恢复，通知结束

复盘（Postmortem）
  └─ 48 小时内完成初稿
```

**核心原则**：**mitigate first, diagnose later**。先止血，根因可以之后慢慢查。

## 5. On-call 文化

```
On-call 健康的标志：
├─ 一周一次 On-call 班
├─ 不超过 2 个告警/晚（否则 burnout）
├─ 告警必须 actionable（有 runbook）
├─ 白天 / 夜间告警严格分级
├─ 有"follow-the-sun"跨时区安排
└─ 值班津贴和调休机制

反模式：
├─ 告警轰炸：一次事故 100+ 条告警
├─ 告警疲劳：80% 的告警不需要行动
├─ 无 Runbook：每次都要重新摸索
├─ 英雄主义：同一个人值班所有重要时段
└─ 惩罚性值班：用 On-call 惩罚犯错的工程师
```

## 6. Runbook 写作

每个告警都应该有 Runbook，回答：

```
Runbook 必备内容：
├─ 这个告警什么意思？（业务影响）
├─ 第一步做什么？（查哪个 Dashboard）
├─ 常见原因列表
├─ 对应的处理步骤
├─ 升级到谁（如果解决不了）
└─ 相关链接（Dashboard、历史事故）
```

示例：

```markdown
# Runbook: HighErrorRate on order-service

## 影响
订单服务 5xx 错误率 > 1%，用户无法下单。

## 第一步
1. 打开 Dashboard: https://grafana/d/order-overview
2. 在 Grafana **Alert Activity（13.1）** 查看告警状态历史、静默与规则上下文
3. 看过去 1 小时错误率趋势
4. 看过去 30 分钟的 Trace 样本 (错误 Trace)

## 常见原因

### 数据库慢查询
现象：Trace 中 DB Span 占比 > 80%
处理：
- 查看 pg_stat_activity 里的长事务
- 必要时 pg_cancel_backend()
- 看最近是否有新功能引入 N+1 查询

### 下游支付服务超时
现象：Trace 显示卡在 payment-service
处理：
- 查看 payment-service 自身状态
- 触发熔断（如果未配置自动熔断）
- 联系支付团队值班

### 部署引入 Bug
现象：错误时间点 = 最近部署时间
处理：
- 立即回滚：kubectl rollout undo deploy/order-service
- 事后定位 bug

## 升级
15 分钟内无法定位 → 升级到 IC
涉及数据问题 → @dba-oncall
涉及支付问题 → @payment-oncall

## 历史事故
- 2026-03-15 类似告警：slow query 导致 (链接)
- 2026-02-08 类似告警：支付超时 (链接)
```

## 7. Postmortem 撰写

### 7.1 无责文化（Blameless）

```
❌ 传统做法：
  "谁部署的？为什么不做 code review？"
  → 工程师开始掩盖问题、害怕承担

✅ 无责文化：
  "系统的哪个环节让这个 bug 能进入生产？"
  "我们怎么改进流程，让任何人都不会再犯？"
  → 工程师愿意分享细节，组织持续学习
```

### 7.2 Postmortem 模板

```markdown
# Postmortem: [简明标题]

- **日期**：2026-05-10
- **事件等级**：SEV-2
- **持续时间**：14:23 - 15:47（1 小时 24 分钟）
- **影响**：订单创建成功率从 99.9% 降至 87%，约 3,500 次下单失败
- **撰写人**：张三
- **参与人**：张三（IC）、李四（Tech Lead）、王五（Comm）

## 时间线（TL;DR 时间顺序，所有时间 UTC+8）

| 时间 | 事件 |
|------|------|
| 14:23 | 高错误率告警触发 |
| 14:25 | On-call 张三确认，定级 SEV-2 |
| 14:30 | 发现问题时间点对齐最近一次部署 v2.34.5 |
| 14:35 | 执行回滚到 v2.34.4 |
| 14:42 | 错误率开始下降 |
| 15:00 | 错误率回到正常水平 |
| 15:47 | 声明事故结束 |

## 什么发生了？（不含主观判断）

v2.34.5 中引入了新的订单验证逻辑，使用了 Redis 作为临时去重。
由于 Redis 集群在当天有维护操作，部分 Key 的 GET 返回超时。
新代码没有为这个超时做 fallback，直接抛出异常导致请求失败。

## 为什么会这样？（5 Whys）

1. 为什么用户无法下单？
   → 订单服务返回 500

2. 为什么订单服务返回 500？
   → 新的 Redis GET 超时了

3. 为什么 Redis 超时不降级？
   → 新代码没有 try/except 和降级逻辑

4. 为什么 Code Review 没发现？
   → 审核人没有看出这里缺少降级

5. 为什么我们的体系允许"无降级"的依赖进生产？
   → 缺少 linter/静态检查来强制外部依赖必须有降级

## 做得好的地方

- 告警在 2 分钟内响应
- 回滚决策果断
- 通信清晰，客服提前有话术

## 做得不好的地方

- 新代码没有 fallback 逻辑
- Staging 环境没有模拟 Redis 故障的混沌测试
- Runbook 里没有"Redis 故障"的应对章节

## Action Items

| 编号 | 行动 | 负责人 | 截止 | 优先级 |
|------|------|--------|------|--------|
| AI-1 | 为所有 Redis 调用增加 fallback 降级 | 李四 | 2026-05-20 | P0 |
| AI-2 | 引入 chaos-redis 做故障演练 | 王五 | 2026-06-01 | P1 |
| AI-3 | Runbook 增加 Redis 故障章节 | 张三 | 2026-05-15 | P1 |
| AI-4 | 代码规范加入"外部依赖必须有降级" | 团队 | 2026-05-25 | P1 |

## 学到了什么？

1. 任何外部依赖都不可信，必须有降级
2. 部署时段应避开依赖系统的维护窗口
3. 我们的 chaos engineering 覆盖还不够

## 附录

- 链接：告警详情、Grafana Alert Activity 时间线、Dashboard 截图、相关 Trace、回滚 PR
```

### 7.3 Action Items 治理

```
常见失败：Postmortem 写完 Action Items 就没人跟进
改进：
├─ Action Items 进入产品 Backlog，有明确负责人
├─ 超过截止期自动升级
├─ 季度 Review 所有未完成的 AI
└─ 和 OKR / 绩效挂钩（轻度）
```

## 8. Chaos Engineering

**不等事故发生，主动制造故障来检验系统韧性。**

```
阶梯式引入 Chaos：
├─ 阶段 1：Game Day（半年一次）
│   手动触发故障，全团队参与演练
│
├─ 阶段 2：Chaos in Staging
│   部署 Chaos Mesh / Litmus，Staging 自动化
│
├─ 阶段 3：Chaos in Production
│   生产小流量、业务低峰期定期演练
│
└─ 阶段 4：Continuous Chaos
    CI/CD 中持续运行，作为发布门禁
```

工具：
- **Chaos Mesh**（K8s 原生，CNCF 孵化）
- **Litmus**（K8s 原生，CNCF 毕业）
- **Gremlin**（商业，易用）
- **Netflix Chaos Monkey**（鼻祖）

## 9. 生产检查清单

```
事件响应成熟度：
☐ 有明确的事件分级（SEV-1/2/3/4）
☐ 每个告警有 Runbook
☐ On-call 排班工具（PagerDuty / Opsgenie / Grafana IRM）
☐ Grafana Alert Activity（13.1）已启用，值班可在同一视图查看告警历史与静默
☐ 事故协调 channel 标准（Slack #incident-xxx）
☐ 事故时间线自动记录（OncallLogger / Firehydrant）
☐ 状态页更新流程（Statuspage / Cachet）
☐ Postmortem 模板固定
☐ Action Items 有跟踪
☐ 季度 Game Day
☐ 无责文化贯彻
```

## 📖 参考资料

- [Google SRE Book - Managing Incidents](https://sre.google/sre-book/managing-incidents/)
- [SRE Workbook - Postmortem Culture](https://sre.google/workbook/postmortem-culture/)
- [PagerDuty Incident Response](https://response.pagerduty.com/)
- [Learning from Incidents](https://www.learningfromincidents.io/)
- [Chaos Mesh](https://chaos-mesh.org/)
