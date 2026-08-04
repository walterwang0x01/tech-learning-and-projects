# FinOps 成本治理

> Author: Walter Wang

<!-- version-check: FinOps Framework 2026（2026-03 更新，Technology Value + AI/ML 分类）, KubeCost 2.x, OpenCost（FOCUS 1.3 支持）, checked 2026-07-10 -->

## 1. 什么是 FinOps

```
FinOps = Finance + DevOps
    ├─ 把云成本纳入工程决策
    ├─ 让团队对自己的成本负责
    └─ 平衡速度、质量、成本

2019 FinOps Foundation 成立
2024+ FinOps 成为大型公司标配
```

**FinOps 不是"省钱"**，是"让花钱更明智"——有时候加钱买速度是对的。

## 2. FinOps 三阶段

```
Inform（知道花了多少）
  ├─ 成本可视化
  ├─ 按团队/服务/环境分摊
  └─ 历史趋势

Optimize（怎么花得更值）
  ├─ Rightsizing
  ├─ 购买策略（预留实例 / Savings Plan）
  ├─ 删除 orphan 资源
  └─ 改架构（Serverless / Spot）

Operate（持续治理）
  ├─ 预算和告警
  ├─ 异常检测
  ├─ 每季度 review
  └─ 激励和文化
```

## 3. 成本可见性：Tag 是基础

```
必备 Tag：
├─ Team / Owner
├─ Environment（dev / staging / prod）
├─ CostCenter
├─ Service（业务服务名）
└─ Project

工具强制：
├─ AWS Tag Policy（组织级强制）
├─ Azure Policy（标签继承）
└─ Terraform 中 default_tags
```

Terraform 示例：

```hcl
provider "aws" {
  default_tags {
    tags = {
      Team        = var.team
      Environment = var.environment
      CostCenter  = var.cost_center
      Managed     = "terraform"
    }
  }
}
```

## 4. Kubernetes 成本分摊

K8s 多租户环境下，"这个 Pod 花了多少钱"是经典难题：

```
┌──── KubeCost / OpenCost 原理 ────┐
│                                    │
│  节点成本（AWS/GCP/Azure 计费）      │
│    ÷                                │
│  节点容量（CPU / Memory）            │
│    ×                                │
│  Pod 使用（Request / Usage）         │
│    =                                │
│  Pod 成本                            │
└────────────────────────────────────┘
```

**OpenCost** 是 CNCF 毕业项目，KubeCost 的开源核心：

```bash
helm install opencost opencost/opencost -n opencost
```

查询示例：

```promql
# 按 namespace 每日成本
sum by (namespace) (
  node_total_hourly_cost * on(node) pod_node_info * 24
)

# 按 label 聚合（比如按 team）
sum by (label_team) (
  kubecost_cluster_costs * on(pod, namespace) group_left(label_team) kube_pod_labels
)
```

## 5. Rightsizing

最大的云成本浪费来自**过度配置**：

```
调查：
├─ 容器申请 4 CPU 实际用 0.3 → 浪费 92%
├─ RDS 买 db.r5.4xlarge 实际 CPU 20% → 买小一档
├─ S3 热桶放冷数据 → 迁 IA 或 Glacier
└─ 忘了关的 dev EBS → 白白花钱

自动化：
├─ AWS Compute Optimizer
├─ Azure Advisor
├─ GCP Recommender
└─ VPA（Kubernetes Vertical Pod Autoscaler）
```

### Rightsizing 前后（K8s 示例）

```yaml
# Before: 过度请求
resources:
  requests: {cpu: "2000m", memory: "4Gi"}
  limits:   {cpu: "4000m", memory: "8Gi"}
# 实际高峰 CPU 0.5，内存 1.5G

# After
resources:
  requests: {cpu: "500m", memory: "1.5Gi"}
  limits:   {cpu: "1000m", memory: "2Gi"}
# 同等节点可以装 4 倍 Pod
```

## 6. 购买策略

```
AWS：
├─ Reserved Instance（RI）：1/3 年固定，60-70% 折扣
├─ Savings Plan：更灵活，适合稳定工作负载
├─ Spot：最多 90% 折扣，但可能被回收
└─ 策略：基线用 RI/SP，弹性用 Spot，突发用 On-Demand

GCP：Committed Use Discount（CUD）
Azure：Reserved VM Instances、Savings Plans

Kubernetes 混合：
├─ 关键业务 → On-Demand
├─ 批处理 → Spot（Karpenter 支持）
├─ 开发环境 → Spot + 可停机
└─ Savings Plan 覆盖基线
```

## 7. Serverless / Autoscaling

```
按量付费 + 自动伸缩：
├─ AWS Lambda / GCP Cloud Run / Azure Functions
├─ K8s：HPA + KEDA
└─ 对 burst 场景成本优化最好

注意：
├─ Serverless 对长时间任务成本高（比 VM 贵 3-5x）
├─ Cold Start 也是隐形成本
└─ 稳定流量还是预留实例便宜
```

Karpenter（K8s 节点自动伸缩）：

```yaml
apiVersion: karpenter.sh/v1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      requirements:
        - key: karpenter.k8s.aws/instance-category
          operator: In
          values: [c, m, r]
        - key: karpenter.k8s.aws/instance-generation
          operator: Gt
          values: ["2"]
        - key: karpenter.sh/capacity-type
          operator: In
          values: [spot, on-demand]
  disruption:
    consolidationPolicy: WhenEmptyOrUnderutilized
    consolidateAfter: 1m
```

## 8. 数据存储成本

```
对象存储分层：
├─ Standard / Hot
├─ Infrequent Access（读少）
├─ Archive / Glacier（基本不读，便宜 10x）
└─ Lifecycle Rule 自动迁移

示例 S3 Lifecycle：
├─ 30 天后 → Standard-IA
├─ 90 天后 → Glacier Flexible
└─ 365 天后 → Glacier Deep Archive

数据库：
├─ 冷数据归档到 Iceberg + S3（详见 data-engineering/04）
├─ 大字段（图片、PDF）不放 RDS
└─ 日志用 Loki/ClickHouse，不要放 Elasticsearch 长期存
```

## 9. LLM 成本 FinOps

2026 年的新成本大户：

```
LLM 成本特点：
├─ Token 成本不直观（一次请求几美分到几美元）
├─ 用量爆发（一个恶意用户一夜刷爆）
├─ 模型切换 10x 成本差
└─ 缓存和路由能省大钱

优化策略：
├─ Prompt 压缩 + Context 裁剪
├─ Semantic Cache（相似 query 命中）
├─ 模型路由：简单任务用便宜模型
├─ 批处理 API（便宜 50%）
├─ Finetuning 长尾高频 prompt
└─ 设置 Budget + Token / User 限额
```

见 [observability-sre/07-AI-Agent可观测性.md](../observability-sre/07-AI-Agent可观测性.md) 的成本监控代码。

## 10. 异常检测与告警

```python
# Prometheus + Alertmanager
- alert: DailyCostSpike
  expr: |
    increase(cloud_daily_cost[1d])
    > 1.5 * avg_over_time(increase(cloud_daily_cost[1d])[7d:])
  for: 1h
  annotations:
    summary: "Daily cost spiked: ${{ $value }} today, 50% above 7d avg"
```

商业工具：
- **Vantage** / **Cloudability** / **Finout**：多云成本聚合
- **CloudHealth**（VMware）：企业级
- **Infracost**：Terraform plan 时预估成本

## 11. 文化与激励

```
组织层面：
├─ 每个服务 Owner 看得到自己的成本
├─ 月度 FinOps review
├─ 成本 KPI 纳入团队目标
└─ "省下的钱可以用于技术债还款"

反模式：
├─ 只有运维团队关心成本
├─ 罚性 KPI（导致团队隐瞒真实成本）
└─ 一刀切要求降 20%（该花的也不花）
```

## 11.5 FinOps Framework 2026 更新（2026-03）

> 更新于 2026-07-10

<!-- version-check: FinOps Framework 2026 (Executive Strategy Alignment + Technology Categories), checked 2026-07-10 -->

FinOps Foundation 于 **2026-03** 发布了 Framework 的一次重大改版，核心是把 FinOps 的使命从"管理云的价值"扩展为**"管理技术的价值"**（[FinOps Framework 2026](https://www.finops.org/insights/2026-finops-framework/)）：

- **新定义**：FinOps 是一种运营框架和文化实践，通过工程、财务、业务团队协作，最大化技术的业务价值、支持及时数据驱动决策、建立财务责任制——关键变化是从"cloud"改为"technology"
- **新增 Capability：Executive Strategy Alignment**（归入"管理 FinOps 实践"域）：把技术支出决策和企业战略正式挂钩，包含四个方向——高管优先级对齐、多年投资策略、产品优先级排序支持、战略决策支持
- **Technology Categories 分类法**：明确区分 Public Cloud / SaaS / Licensing / Data Center / **AI/ML**（基础模型 API、微调、推理、训练）/ 其他技术支出，每类下都有对应 Capability、Persona 和成功指标的定制指引
- **能力改名**：Workload Optimization → **Usage Optimization**（不再局限于云工作负载）；DevOps Tools and Services → **Automation, Tools and Services**（自动化被提升为一级关注点）
- **AI/ML 专属指引**：GPU/CPU 差异化定价、token 计价模式、build-vs-buy 经济性分析，作为 FinOps 实践新的重点方向

对已落地 FinOps 实践的团队，建议评估现有 Capability 是否需要按新分类法重新归类，尤其是有大量 LLM/AI 支出（对应本文第 9 节）的团队应优先补齐 AI/ML Technology Category 的度量指标。来源：[FinOps Framework 2026 官方说明](https://www.finops.org/insights/2026-finops-framework/)、[State of FinOps 2026 Report](https://data.finops.org/)

## 12. 生产检查清单

```
☐ 100% 资源打上 Owner + Env + CostCenter 标签
☐ 每周成本报告自动发给团队
☐ 月度异常（突增 >30%）告警
☐ 预算 + 80% 用量告警
☐ 季度 Rightsizing Review
☐ Reserved / Savings Plan 覆盖率 > 60%
☐ K8s 启用 VPA + Karpenter
☐ S3 Lifecycle Policy 到位
☐ LLM 用量按用户/服务追踪 + 预算
☐ FinOps 有明确负责人
```

## 📖 参考资料

- [FinOps Foundation](https://www.finops.org/)
- [FinOps Framework](https://www.finops.org/framework/)
- [OpenCost](https://www.opencost.io/)
- [KubeCost Blog](https://blog.kubecost.com/)
- [Karpenter](https://karpenter.sh/)
- [AWS Cost Optimization Pillar](https://docs.aws.amazon.com/wellarchitected/latest/cost-optimization-pillar/)
