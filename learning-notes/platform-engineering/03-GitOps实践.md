# GitOps 实践

> Author: Walter Wang

<!-- version-check: Argo CD 3.4.3, Flux 2.8 GA, Argo Rollouts 1.8, checked 2026-05-31 -->
<!-- 修复于 2026-05-31: Argo CD 2.14 → 3.x 系列（3.0 于 2025-05 发布，2.x 全部 EOL）；Flux 2.5 → 2.8 GA -->
<!-- 注：正文第 4-12 节的 apiVersion 和命令在 Argo CD 3.x 仍兼容，最新版本动态见文末第 14 节 -->

## 1. 什么是 GitOps

Weaveworks 2017 年提出，四大原则：

```
1. 声明式：整个系统的期望状态用代码表达
2. 版本化：代码在 Git，任何变更都有审计
3. 自动部署：Git 是源头，Operator 拉取并同步集群
4. 持续协调：集群状态漂移时自动恢复
```

```
传统 CI/CD：
  push code → CI → deploy → 集群
  （推模型，CI 系统有集群凭证）

GitOps：
  push code → CI（构建镜像）→ 更新 Git
  Argo CD 拉取 Git → 同步到集群
  （拉模型，集群无需暴露给 CI）
```

## 2. 为什么 GitOps 赢了

```
├─ 审计性：所有变更有 Commit 历史
├─ 可回滚：git revert 就能回滚基础设施
├─ 可重建：灾难恢复时从 Git 重建集群
├─ 安全性：CI 不需要集群 admin 权限
├─ 多集群：同一个仓库部署到多个环境
└─ 团队协作：Pull Request 走审批流程
```

## 3. Argo CD vs Flux

2026 年主流二选一：

```
Argo CD                     Flux v2
├─ UI 体验强（Dashboard）      ├─ 纯 CLI / Kubectl 风格
├─ App of Apps 模式            ├─ Kustomize + Helm 原生
├─ ApplicationSet 多集群        ├─ OCI Artifacts 支持好
├─ Argo Rollouts 配合           ├─ Flagger 配合
├─ 功能最全                     ├─ 更轻量、K8s native
└─ CNCF Graduated               └─ CNCF Graduated

选型：
├─ 要 GUI、功能丰富 → Argo CD
├─ 纯 GitOps 极简主义 → Flux
├─ 多集群、跨 Region → Argo CD（ApplicationSet 强）
```

## 4. Argo CD 基础

### 4.1 安装

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml

# 初始密码
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

### 4.2 Application 定义

```yaml
# apps/my-service.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-service
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://github.com/myorg/infra.git
    targetRevision: main
    path: apps/my-service/overlays/production

  destination:
    server: https://kubernetes.default.svc
    namespace: production

  syncPolicy:
    automated:
      prune: true           # 资源在 Git 里删了就从集群删
      selfHeal: true        # 集群被手动改了就恢复
    syncOptions:
      - CreateNamespace=true
      - PrunePropagationPolicy=foreground
      - PruneLast=true
    retry:
      limit: 5
      backoff:
        duration: 5s
        factor: 2
        maxDuration: 3m
```

### 4.3 App of Apps 模式

一个"主 App"管理多个子 App：

```yaml
# apps/root.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: root
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/infra.git
    targetRevision: main
    path: apps/    # 包含所有子 Application 定义
  destination:
    server: https://kubernetes.default.svc
    namespace: argocd
  syncPolicy:
    automated: {prune: true, selfHeal: true}
```

## 5. 标准仓库结构

**推荐：应用代码仓库 和 基础设施仓库分离**。

```
应用代码仓库（app-repo）
├── src/
├── Dockerfile
└── .github/workflows/build.yml   # 构建镜像，推送到 Registry，更新 infra-repo 的镜像 tag

基础设施仓库（infra-repo）
├── apps/
│   ├── my-service/
│   │   ├── base/                 # 基础 Kustomize
│   │   │   ├── deployment.yaml
│   │   │   ├── service.yaml
│   │   │   └── kustomization.yaml
│   │   └── overlays/
│   │       ├── dev/
│   │       ├── staging/
│   │       └── production/
│   └── another-service/
├── argocd/
│   └── apps/                      # Argo CD Application 定义
└── clusters/
    ├── dev/
    ├── staging/
    └── production/
```

## 6. Kustomize 实战

```yaml
# apps/my-service/base/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - deployment.yaml
  - service.yaml

commonLabels:
  app: my-service

images:
  - name: myapp
    newName: ghcr.io/myorg/my-service
    newTag: placeholder   # CI 会更新这个 tag
```

```yaml
# apps/my-service/overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization
resources:
  - ../../base

namespace: production

replicas:
  - name: my-service
    count: 5

patches:
  - path: resources-patch.yaml
    target:
      kind: Deployment
      name: my-service
```

## 7. Helm 与 GitOps 协同

GitOps 推荐 **Helm 渲染后提交**（而不是 Argo CD 运行时渲染）：

```bash
# CI 中
helm template my-service charts/my-service \
    -f values-production.yaml \
    --output-dir rendered/

# 提交 rendered/ 到 infra repo
# Argo CD 只需要管纯 K8s YAML
```

好处：
- 更可审计（Git diff 看到实际 YAML）
- Argo CD 不用管 Helm 版本
- 多集群部署行为一致

## 8. Image Updater：自动化镜像发布

Argo CD Image Updater 监视镜像 Registry，自动更新 Git：

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-service
  annotations:
    argocd-image-updater.argoproj.io/image-list: myapp=ghcr.io/myorg/my-service
    argocd-image-updater.argoproj.io/myapp.update-strategy: semver
    argocd-image-updater.argoproj.io/myapp.allow-tags: "regexp:^v[0-9]+\\.[0-9]+\\.[0-9]+$"
    argocd-image-updater.argoproj.io/write-back-method: git
    argocd-image-updater.argoproj.io/git-branch: main
spec: { ... }
```

CI 只需推镜像，后面 Image Updater 自动写 Git。

## 9. Progressive Delivery（渐进式发布）

### 9.1 Argo Rollouts

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-service
spec:
  replicas: 10
  strategy:
    canary:
      steps:
        - setWeight: 10          # 10% 流量
        - pause: {duration: 5m}
        - setWeight: 30
        - pause: {duration: 10m}
        - setWeight: 50
        - pause: {duration: 10m}
        - setWeight: 100
      analysis:
        templates:
          - templateName: error-rate
        args:
          - name: service-name
            value: my-service
        startingStep: 2
        interval: 30s
        failureLimit: 3
  selector:
    matchLabels: {app: my-service}
  template: { ... }

---
# AnalysisTemplate：定义成功指标
apiVersion: argoproj.io/v1alpha1
kind: AnalysisTemplate
metadata:
  name: error-rate
spec:
  args:
    - name: service-name
  metrics:
    - name: error-rate
      interval: 1m
      successCondition: result[0] < 0.01   # 错误率 < 1%
      failureLimit: 3
      provider:
        prometheus:
          address: http://prometheus:9090
          query: |
            sum(rate(http_requests_total{service="{{args.service-name}}",status=~"5.."}[5m]))
            /
            sum(rate(http_requests_total{service="{{args.service-name}}"}[5m]))
```

发布自动在每一步后查 Prometheus，指标不达标自动回滚。

### 9.2 Flagger（配合 Flux）

类似功能，但基于 Service Mesh（Istio / Linkerd / Envoy）。

## 10. 密钥管理

GitOps 仓库里**不能**放明文密钥：

```
方案：
├─ SOPS（Mozilla）+ Argo CD Plugin
│   └─ 用 GPG/KMS 加密文件后提交 Git
│
├─ External Secrets Operator
│   └─ K8s 中的 ExternalSecret 资源拉取 Vault/AWS SM/GCP SM
│
├─ Sealed Secrets（Bitnami）
│   └─ K8s 集群私钥解密，其他环境解密不了
│
└─ Vault Agent Injector
    └─ Pod 启动时自动注入 Vault Token
```

2026 年推荐 **External Secrets Operator**（功能最全）。

## 11. 多环境 + 多集群

```
单仓库 + 多 Overlay（推荐）：
infra-repo/
├── base/
├── overlays/
│   ├── dev/
│   ├── staging/
│   └── production/
└── argocd/
    └── apps-{dev,staging,production}.yaml  # 每环境一个 App 集合

Argo CD ApplicationSet：一份配置生成 N 个 App
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: my-service
spec:
  generators:
    - list:
        elements:
          - cluster: dev
            url: https://dev.k8s.local
          - cluster: prod
            url: https://prod.k8s.local
  template:
    metadata:
      name: '{{cluster}}-my-service'
    spec:
      source:
        path: apps/my-service/overlays/{{cluster}}
      destination:
        server: '{{url}}'
        namespace: production
```

## 12. 生产检查清单

```
☐ 应用代码和基础设施仓库分离
☐ 所有环境用 Overlay（不要直接改 base）
☐ Argo CD Self-Heal + Prune 开启（生产慎用 prune）
☐ 密钥用 SOPS / External Secrets，不提交明文
☐ Image Updater 自动化镜像发布
☐ Progressive Delivery（Argo Rollouts / Flagger）
☐ Analysis Template 基于 Prometheus SLO 指标
☐ Argo CD 自身也用 GitOps 管理（self-hosting）
☐ RBAC：Argo CD 按团队 / 项目隔离权限
☐ 备份 Argo CD 配置（它管理的状态）
☐ 监控 Argo CD 同步延迟和失败率
☐ DR：从 Git 重建集群的剧本
```

## 13. 反模式

```
❌ 手动 kubectl apply
   → 和 GitOps 原则违背，会被 Argo 覆盖

❌ 代码仓库里直接 commit yaml
   → 分两个仓库，avoid cross-concerns

❌ 明文密钥进 Git
   → 即使 private repo 也是事故隐患

❌ 一个 Application 管所有东西
   → 变更爆炸半径大，出错全挂

❌ 生产环境开 auto-sync
   → 小改动直接生产，建议 manual approve

❌ 不用 Rollouts，直接 Deployment
   → 新版本有 bug，全流量中招
```

## 14. 2026 年 5 月版本动态

> 🔄 更新于 2026-05-31

> 本节内容为版本演进信息增量补充，前文第 4-12 节的 `apiVersion: argoproj.io/v1alpha1`、安装命令、Application/Rollout 写法在 Argo CD 3.x 中均保持兼容，无需改动。

### 14.1 Argo CD 进入 3.x 系列（重要：本文前文基于 2.x）

Argo CD 的 2.x 系列已全部 EOL。2026 年的版本格局：

| 版本线 | 首次发布 | 最新补丁 | 状态 |
| ---- | ---- | ---- | ---- |
| 3.4 | 2026-05-05 | 3.4.3（2026-05-28） | 当前最新稳定线 |
| 3.3 | 2026-02-02 | 3.3.11 | 维护中 |
| 3.2 | 2025-11-04 | 3.2.12 | 维护中 |
| 3.1 | 2025-08-13 | 3.1.16 | 2026-05-05 EOL |
| 3.0 | 2025-05-06 | 3.0.23 | 2026-02-02 EOL |
| 2.14 及更早 | — | — | 全部 EOL，不应再用于新集群 |

来源：[endoflife.date - Argo CD](https://endoflife.date/argo-cd)、[Argo CD Releases](https://github.com/argoproj/argo-cd/releases)

Argo CD 维护策略是「最近 3 个 minor 版本」，升级要逐个 minor 递进（如 3.1 → 3.2 → 3.3 → 3.4），不能跨多个 minor 直跳。3.0 的主要 Breaking Change 是默认 RBAC 收紧和 Server-Side Apply 成为同步默认行为，升级前需查官方迁移说明。

> ⚠️ 待确认：3.4 的逐版本新特性清单建议以官方 Release Notes 为准，本表仅记录版本时间线与 EOL 状态（已通过 endoflife.date 精确核对）。

### 14.2 Flux v2.8 GA — Helm v4 支持

Flux v2.8.0 已 GA（Q1 2026 路线图里程碑），核心变化：

```
Flux 2.8 关键更新
├─ Helm v4 支持（helm-controller 适配 Helm 4 API）
├─ Server-Side Apply 成为新默认
├─ kstatus-based 健康检查成为新默认（更准确判断资源就绪）
└─ 降低应用部署的 MTTR（平均恢复时间）
```

来源：[Announcing Flux 2.8 GA](https://fluxcd.io/blog/)、[Flux Roadmap](https://fluxcd.io/roadmap/)

注意：Server-Side Apply 和 kstatus 健康检查改为默认后，部分依赖旧 client-side apply 行为的清单可能出现 diff 变化，升级前建议在非生产环境验证。Flux v2.7+ 的升级流程参见官方 Discussion #5572。

### 14.3 选型补充（2026）

第 3 节的 Argo CD vs Flux 对比仍然成立，补充一条 2026 年观察：两者都已是 CNCF Graduated 项目，差异主要在「GUI 优先 vs CLI/K8s-native 优先」。Flux 2.8 的 Helm v4 原生支持让它在「以 Helm 为核心的平台」场景更有优势；Argo CD 3.x 的 ApplicationSet 仍是多集群/跨 Region 的首选。

> 更新于 2026-07-09

### 14.4 OTel Collector 声明式配置与 GitOps 联动（2026-07）

可观测性管道配置正与 GitOps 收敛：

- OTel Declarative Config **1.0 stable** 可用 YAML 定义 pipeline，纳入 Git 版本管理
- Collector **v0.156.0** 与 contrib 同步发布，平台团队应在 IDP 中提供标准 Collector profile
- 与 Flux 2.8 Server-Side Apply 默认行为一致：Collector 配置变更走 PR 审查 + 渐进 rollout

> 来源：[OTel Declarative Config Stable](https://opentelemetry.io/blog/2026/stable-declarative-config/)、[Flux 2.8 GA](https://fluxcd.io/blog/)、[Collector v0.156.0](https://github.com/open-telemetry/opentelemetry-collector-releases/releases/tag/v0.156.0)

## 📖 参考资料

- [Argo CD 官方文档](https://argo-cd.readthedocs.io/)
- [Flux 文档](https://fluxcd.io/docs/)
- [GitOps Principles](https://opengitops.dev/)
- [Argo Rollouts](https://argoproj.github.io/argo-rollouts/)
- [External Secrets Operator](https://external-secrets.io/)
- [CNCF GitOps Working Group](https://github.com/open-gitops/project)
- [endoflife.date - Argo CD 版本周期](https://endoflife.date/argo-cd)
