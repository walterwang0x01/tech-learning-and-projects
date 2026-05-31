# Internal Developer Portal（IDP）

> Author: Walter Wang

<!-- version-check: Backstage 1.51, Port 2024, Cortex, OpsLevel, AIContext RFC, checked 2026-05-31 -->
<!-- 修复于 2026-05-31: Backstage 1.50 → 1.51（2026-05 稳定发布） -->

## 1. Portal 的核心价值

```
Internal Developer Portal 回答的问题：
├─ 我们有哪些服务？谁负责？    （Catalog）
├─ 怎么新建一个服务？           （Scaffolder）
├─ 这个服务的文档/接口/指标？    （Tech Docs + Plugins）
├─ 这个服务符合我们的标准吗？    （Scorecards）
└─ 我怎么做 X？（部署、扩容等）  （Actions）
```

## 2. 工具对比（2026）

| 工具 | 定位 | 特点 |
|------|------|------|
| **Backstage** | 开源 | Spotify 开源，CNCF 孵化，自定义强、需要工程投入 |
| **Port** | SaaS | 开箱即用、上手快、按需付费 |
| **Cortex** | SaaS | 侧重 Scorecards / Ownership |
| **OpsLevel** | SaaS | 侧重成熟度评估 |
| **Compass**（Atlassian）| SaaS | Jira 集成好 |
| **Humanitec** | SaaS | 侧重"应用部署"自助 |

**选型建议**：
- **有专人维护、定制需求强** → Backstage
- **要快速上手、中小团队** → Port / Cortex
- **Atlassian 生态** → Compass

## 3. Backstage 基础

### 3.1 安装

```bash
npx @backstage/create-app@latest
cd my-backstage
yarn install
yarn start
# 访问 http://localhost:3000
```

### 3.2 Catalog：服务/资源清单

```yaml
# catalog-info.yaml（放在每个服务的仓库）
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: payment-service
  description: 支付服务
  annotations:
    github.com/project-slug: myorg/payment-service
    backstage.io/techdocs-ref: dir:.
    prometheus.io/rule: payment-service
    pagerduty.com/service-id: PXXXXXX
    argocd/app-name: payment-service
  tags:
    - go
    - critical
  links:
    - url: https://grafana.company/d/payment
      title: Grafana
spec:
  type: service
  lifecycle: production
  owner: team-payments
  system: commerce-platform
  providesApis:
    - payment-api
  dependsOn:
    - resource:postgres-payment
    - component:notification-service
```

### 3.3 用 Scaffolder 创建服务

```yaml
# templates/go-service/template.yaml
apiVersion: scaffolder.backstage.io/v1beta3
kind: Template
metadata:
  name: go-microservice
  title: Create a Go Microservice
spec:
  owner: platform-team
  type: service

  parameters:
    - title: Service Info
      required: [name, owner]
      properties:
        name: {type: string, pattern: '^[a-z-]+$'}
        description: {type: string}
        owner:
          type: string
          ui:field: OwnerPicker

  steps:
    - id: fetch
      name: Fetch skeleton
      action: fetch:template
      input:
        url: ./skeleton
        values:
          name: ${{ parameters.name }}
          owner: ${{ parameters.owner }}

    - id: publish
      name: Publish to GitHub
      action: publish:github
      input:
        repoUrl: github.com?repo=${{ parameters.name }}&owner=myorg
        defaultBranch: main
        gitAuthorName: Backstage

    - id: register
      name: Register in Catalog
      action: catalog:register
      input:
        repoContentsUrl: ${{ steps.publish.output.repoContentsUrl }}
        catalogInfoPath: /catalog-info.yaml

    - id: argo-app
      name: Create Argo CD App
      action: http:backstage:request
      input:
        method: POST
        path: /api/argocd/app
        body:
          name: ${{ parameters.name }}
          # ...

  output:
    links:
      - title: Repository
        url: ${{ steps.publish.output.remoteUrl }}
      - title: Backstage Catalog
        icon: catalog
        entityRef: ${{ steps.register.output.entityRef }}
```

这样开发者点"Create Go Microservice"填表单，几分钟内就有：
- GitHub 仓库（代码骨架、CI、Dockerfile）
- Argo CD App
- Backstage Catalog 注册
- Grafana Dashboard 模板
- PagerDuty 服务

### 3.4 TechDocs

把每个服务的 Markdown 文档自动构建成在线文档：

```yaml
# catalog-info.yaml
metadata:
  annotations:
    backstage.io/techdocs-ref: dir:.
```

```
repo/
├── catalog-info.yaml
├── mkdocs.yml
└── docs/
    ├── index.md
    ├── getting-started.md
    └── api/
        └── endpoints.md
```

Backstage 自动渲染，搜索全局可用。

## 4. Scorecards：服务成熟度评估

自动检查每个服务是否达标：

```yaml
# scorecard.yaml
metadata:
  name: production-readiness
spec:
  rules:
    - title: Has an Owner
      expression: has_annotation("owner")

    - title: Has OpenAPI spec
      expression: has_annotation("openapi.spec-url")

    - title: Has Dashboard
      expression: has_annotation("grafana.com/dashboard")

    - title: PagerDuty integration
      expression: has_annotation("pagerduty.com/service-id")

    - title: Has Runbook
      expression: has_link(title="Runbook")

    - title: Has SLO defined
      expression: has_annotation("slo.defined")

    - title: Test coverage > 70%
      expression: metric("coverage") > 70
```

仪表盘显示全公司服务的"合规率"，Owner 能一眼看到自己需要补哪些。

## 5. 关键插件

```
Backstage Plugin 生态：
├─ GitHub Pull Requests
├─ Kubernetes（查每个服务的 Pod/Service）
├─ Argo CD（部署状态）
├─ Prometheus / Grafana（指标）
├─ PagerDuty（On-call 状态）
├─ Sentry（错误聚合）
├─ SonarQube（代码质量）
├─ OpenCost / Kubecost（成本）
└─ AI Assistant（2026 年流行，自然语言查 Catalog）
```

## 6. Portal as Product（作为产品运营）

Platform Team 要把 Portal 当产品做：

```
├─ 用户调研（开发者痛点）
├─ 衡量指标（DAU、创建数、Scorecard 合规率）
├─ 迭代节奏（每两周发布）
├─ 文档和培训
├─ Office Hour（让开发者来问）
└─ NPS / 满意度调查
```

**反模式**：
- 平台团队关起门来造东西
- 三个月大版本发布
- 没人用就硬推
- 不听用户反馈

## 7. 成功指标

```
短期（0-6 个月）：
├─ Catalog 覆盖 50%+ 服务
├─ 1-2 个 Scaffolder 模板上线
└─ 第一批 pilot 团队满意

中期（6-12 个月）：
├─ Catalog 覆盖 90%+
├─ 90% 新服务走 Scaffolder
├─ Scorecard 合规率监控
└─ 至少 5 个高价值自助 Action

长期：
├─ 新开发者 onboarding 时间减半
├─ MTTR 下降
├─ 事故响应自动化
└─ AI Agent 可以通过 Portal 自助操作
```

## 8. AI 与 IDP 的融合（2026 趋势）

```
├─ 自然语言查询 Catalog
│   "哪些服务在用 Python 3.10 以下？"
│
├─ AI 生成 Scorecard 修复建议
│   "为什么我的服务 6 项没达标？"
│
├─ AI 辅助 Scaffolder 填表
│   自动根据业务描述生成 spec
│
└─ AI Agent 作为 Catalog 消费者
   Agent 读 Catalog 了解服务依赖，做 incident response
```

## 9. 常见坑

```
❌ Portal 当文档站
   → 看完就没后续动作，价值低

❌ 只做查询，不做 Action
   → 还是得去 N 个地方点按钮

❌ Catalog 和实际不一致
   → 服务改了没同步，信息过时
   → 用 git 作为 source of truth，自动同步

❌ 大而全 vs 小而精
   → 新 Portal 先从 5-10 个高频场景开始，不要一上来全上

❌ 没人 onboard
   → 再好的工具没人用也没价值
```

## 10. Backstage 1.50+ 版本演进（2026）

> 🔄 更新于 2026-05-14

### 10.1 版本里程碑

| 版本 | 日期 | 重点 |
| ---- | ---- | ---- |
| v1.49.0 | 2026-03-18 | New Frontend System 1.0 RC，成为新应用默认 |
| v1.50.0 | 2026-04-14 | Identity token ownership claims 变更、废弃 API 移除 |
| v1.50.2 | 2026-04 | TechDocs 改进 |
| v1.51.0-next.0 | 2026-04 | 下一周期开启 |

### 10.2 New Frontend System 成为默认

v1.49.0 起，所有新创建的 Backstage 应用默认使用 New Frontend System。核心变化：

```
旧系统：
├─ 插件通过 createPlugin() 注册
├─ 路由在 App.tsx 中集中配置
└─ 主题通过 createTheme() 全局设置

新系统：
├─ 插件通过 createFrontendPlugin() 声明式注册
├─ 路由由插件自行声明，App 自动发现
├─ 主题通过 createThemeExtension() 扩展
└─ 更好的代码分割和懒加载
```

### 10.3 AIContext Catalog Kind（RFC）

Backstage 社区引入了新的 `AIContext` catalog kind，用于结构化 AI Agent 集成：

```yaml
# 示例：为 AI Agent 暴露服务上下文
apiVersion: backstage.io/v1alpha1
kind: AIContext
metadata:
  name: payment-service-context
  annotations:
    backstage.io/ai-context-type: service-metadata
spec:
  owner: team-payments
  targetComponent: payment-service
  contextData:
    description: "支付服务，处理订单支付和退款"
    dependencies: [postgres-payment, notification-service]
    onCall: team-payments
    runbook: "https://wiki.company/payment-runbook"
    slo: "99.9% availability, p99 < 200ms"
```

**价值**：AI Agent（如 incident response bot）可以通过 Catalog API 获取结构化的服务上下文，而不是从非结构化文档中猜测。

### 10.4 Context Engineering 与 IDP 的融合

2026 年 IDP 的核心趋势是成为 AI Agent 的"上下文基础设施"：

```
IDP 作为 Context Engineering 基础设施：
├─ Service Catalog → Agent 了解服务拓扑
├─ Ownership → Agent 知道找谁
├─ Scorecards → Agent 评估服务健康度
├─ TechDocs → Agent 查阅操作手册
├─ Dependencies → Agent 分析影响范围
└─ AIContext → Agent 获取结构化元数据
```

94% 组织已采用或计划采用平台团队（Frontiers in Computer Science 2026 研究），Gartner 预测 2026 年底 80% 大型工程组织将有专职平台团队。

> 来源：[Backstage Weekly #130](https://roadie.io/backstage-weekly/130-v1-50-0-backstagecon-context-engineering/)、[Backstage Weekly #131 AIContext RFC](https://roadie.io/backstage-weekly/131-context-engineering-for-developers-and-new-releases/)、[IDP as AI Goldmine](https://roadie.io/blog/idp-ai-goldmine-context-engineering/)

### 10.5 Backstage 1.51（2026-05）

> 🔄 更新于 2026-05-31

Backstage **v1.51.0** 已稳定发布（继 v1.50.0 之后的常规月度版本）。本次主要是核心服务和组件层面的打磨：

```
v1.51.0 关键变化
├─ 新增 CachedUserInfoService（5 秒 TTL 缓存 + 并发请求合并）
│   减少重复的用户信息查询，降低 auth backend 压力
├─ Backend.start() 返回 BackendStartupResult
│   提供每个插件/模块的成功/失败状态和启动耗时，便于排查启动问题
└─ New Frontend System 组件库持续完善
    Select 组件支持分组分区、Header 组件新增 description/tags/metadata 属性
```

来源：[Backstage v1.51.0 Release Notes](https://backstage.io/docs/releases/v1.51.0)、[Spotify for Backstage Release Notes](https://backstage.spotify.com/release-notes/)

升级提示：v1.51 延续 New Frontend System 默认化的方向（v1.49 起），仍在用旧 Frontend System 的应用建议参考官方迁移指南逐步切换。`BackendStartupResult` 是新增返回值，不影响现有 `Backend.start()` 调用，属于向后兼容的增强。

## 📖 参考资料

- [Backstage 官网](https://backstage.io/)
- [Backstage Plugin Marketplace](https://backstage.io/plugins)
- [Port Documentation](https://docs.getport.io/)
- [CNCF IDP Working Group](https://tag-app-delivery.cncf.io/)
- [Humanitec Platform Engineering](https://humanitec.com/platform-engineering)
