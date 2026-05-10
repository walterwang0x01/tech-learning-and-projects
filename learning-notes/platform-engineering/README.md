# 平台工程

> Author: Walter Wang

<!-- version-check: Platform Engineering 2026, Backstage 1.35, Argo CD 2.14, Crossplane 2.x, checked 2026-05-10 -->

> "Platform Engineering is the discipline of designing and building toolchains and workflows that enable self-service capabilities for software engineering organizations." — Team Topologies

Gartner 预测 2026 年底 80% 的大型软件组织将拥有平台工程团队。

## 📁 目录结构

```
platform-engineering/
├── 01-平台工程概览.md          # 为什么、目标、Team Topologies、IDP
├── 02-Internal-Developer-Portal.md  # Backstage、Port、Cortex
├── 03-GitOps实践.md            # Argo CD、Flux、Rollouts
├── 04-IaC基础设施即代码.md     # Terraform、OpenTofu、Pulumi、Crossplane
├── 05-Policy-as-Code.md        # OPA、Kyverno、Conftest、Cedar
├── 06-FinOps成本治理.md         # 云成本监控、KubeCost、OpenCost
└── 07-CI-CD设计模式.md          # 多环境发布、蓝绿、金丝雀、特性旗标
```

## 🎯 Platform Engineering vs DevOps

```
DevOps（2010s）：
  每个团队自己搞定构建、部署、运维
  → 认知负担巨大，重复劳动

Platform Engineering（2020s）：
  专门的平台团队构建 Internal Developer Platform（IDP）
  → 业务团队通过"金色路径"（Golden Paths）自助
  → Platform 团队是 "建公路" 的，业务团队是 "开车" 的
```

## 🔗 关联内容

- **K8s** → [java/03-容器化/03-kubernetes-overview.md](../java/03-容器化/03-kubernetes-overview.md)
- **可观测性** → [observability-sre/](../observability-sre/)
- **安全** → [security/](../security/)
- **数据工程** → [data-engineering/](../data-engineering/)
- **CI/CD 前端侧** → [frontend/14-DevOps与部署/01-CI-CD与自动化部署.md](../frontend/14-DevOps与部署/01-CI-CD与自动化部署.md)

## 📚 权威参考

- [Team Topologies](https://teamtopologies.com/)
- [Platform Engineering (platformengineering.org)](https://platformengineering.org/)
- [CNCF Platforms White Paper](https://tag-app-delivery.cncf.io/whitepapers/platforms/)
- [ThoughtWorks Tech Radar](https://www.thoughtworks.com/radar)
