# CI/CD 设计模式

> Author: Walter Wang

<!-- version-check: GitHub Actions 2026, Argo Workflows 3.6, checked 2026-05-10 -->

## 1. CI 和 CD 的边界

```
CI（Continuous Integration）
  └─ 代码变更合并到主干
     ├─ 自动化构建
     ├─ 自动化测试
     └─ 产出可部署 artifact

CD（Continuous Delivery / Deployment）
  ├─ Delivery：任何版本都可以一键部署
  └─ Deployment：每次合并自动部署到生产
```

## 2. 标准 Pipeline 结构

```
┌──────── 完整 CI/CD Pipeline ────────┐
│                                      │
│  Commit → Build → Test → Scan →      │
│  Package → Deploy to Staging →       │
│  E2E Test → Deploy to Production →   │
│  Smoke Test → Monitor                 │
│                                      │
│  横切：                                │
│  ├─ Secret Scan                      │
│  ├─ Cache                            │
│  ├─ Parallelism                      │
│  ├─ SBOM + Signature                 │
│  └─ Rollback Plan                    │
└──────────────────────────────────────┘
```

## 3. 分支策略

```
Trunk-Based Development（推荐）
  ├─ 主干一个（main）
  ├─ 短期 feature branch
  ├─ 合入 main 即触发 CI
  └─ Feature Flags 控制未完成功能

Git Flow（大型项目，遗留）
  ├─ main / develop / feature / release / hotfix
  └─ 复杂，适合版本化发布（SaaS 少见）

GitHub Flow（最简单）
  ├─ main 永远可部署
  └─ feature branch → PR → merge
```

**2026 年推荐**：Trunk-Based + Feature Flags（LaunchDarkly / Unleash）。

## 4. GitHub Actions 实战

### 4.1 多环境 CI

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request: {branches: [main]}
  push: {branches: [main]}

concurrency:
  group: ${{ github.ref }}
  cancel-in-progress: true

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: {node-version: '22', cache: 'npm'}
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node: [20, 22, 24]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: {node-version: ${{ matrix.node }}, cache: 'npm'}
      - run: npm ci
      - run: npm test -- --coverage

  security:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      security-events: write
    steps:
      - uses: actions/checkout@v4
      - uses: aquasecurity/trivy-action@0.28.0
        with:
          scan-type: fs
          severity: HIGH,CRITICAL
          exit-code: 1

  build:
    needs: [lint, test, security]
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write  # for cosign keyless
    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - id: meta
        uses: docker/metadata-action@v5
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha,prefix=
            type=ref,event=branch
            type=semver,pattern={{version}}

      - uses: docker/build-push-action@v6
        with:
          context: .
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

      - name: Sign image
        if: github.event_name != 'pull_request'
        uses: sigstore/cosign-installer@v3
      - if: github.event_name != 'pull_request'
        run: |
          cosign sign --yes ghcr.io/${{ github.repository }}@${{ steps.meta.outputs.digest }}
```

### 4.2 部署（GitOps 风格）

Build 阶段推镜像后，更新 Git（不直接部署）：

```yaml
update-manifests:
  needs: build
  if: github.ref == 'refs/heads/main'
  runs-on: ubuntu-latest
  steps:
    - name: Checkout infra repo
      uses: actions/checkout@v4
      with:
        repository: myorg/infra
        token: ${{ secrets.INFRA_PAT }}

    - name: Update image tag
      run: |
        cd apps/myapp/overlays/staging
        yq -i '.images[0].newTag = "${{ github.sha }}"' kustomization.yaml

    - name: Commit
      run: |
        git config user.name 'CI'
        git config user.email 'ci@example.com'
        git add .
        git commit -m "staging: myapp ${{ github.sha }}"
        git push
```

Argo CD 拉取 Git 自动同步到集群（见 [03-GitOps实践.md](./03-GitOps实践.md)）。

## 5. 部署策略

### 5.1 蓝绿部署

```
┌──── Blue (当前生产) ────┐
│  流量 100% → v1.0       │
└─────────────────────────┘

┌──── Green (新版本) ────┐
│  流量 0% → v1.1         │
│  内部测试、烟雾测试       │
└─────────────────────────┘

切换：流量瞬间从 Blue 切到 Green
问题发现：秒级回切 Blue
```

**优势**：可以快速回滚。
**代价**：需要 2 倍资源。

### 5.2 金丝雀发布

```
┌──── Canary（1 个 Pod） ────┐
│  流量 5% → v1.1             │
│  观察 5 分钟                 │
└──────────────────────────┘

┌──── Stable（9 个 Pod） ──────┐
│  流量 95% → v1.0              │
└──────────────────────────────┘

逐步：5% → 25% → 50% → 100%
每一步观察指标（错误率、延迟）
```

### 5.3 Argo Rollouts

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: myapp
spec:
  replicas: 10
  strategy:
    canary:
      steps:
        - setWeight: 5
        - pause: {duration: 5m}
        - setWeight: 25
        - pause: {duration: 10m}
        - analysis:
            templates:
              - templateName: error-rate
            args:
              - name: service-name
                value: myapp
        - setWeight: 50
        - pause: {duration: 10m}
        - setWeight: 100
      trafficRouting:
        istio:
          virtualService:
            name: myapp
```

配合 Prometheus AnalysisTemplate，指标不达标自动回滚。

### 5.4 Feature Flags

```javascript
import { useFlag } from '@openfeature/react-sdk';

function MyComponent() {
    const newCheckout = useFlag('new-checkout', false);
    return newCheckout ? <NewCheckout /> : <OldCheckout />;
}
```

**价值**：部署 ≠ 发布。代码上线了，功能可以灰度、A/B、紧急关闭。

主流工具：
- **LaunchDarkly**（商业）
- **Unleash**（开源）
- **OpenFeature**（CNCF 标准）
- **Flagsmith**（开源商业）

## 6. 环境策略

```
推荐：
├─ dev       开发分支自动部署
├─ staging   main 分支自动部署
├─ canary    生产 5% 流量
└─ production 剩余流量

反模式：
├─ 只有 dev 和 prod
├─ staging 和 prod 配置差异大
└─ 手动切数据库
```

## 7. 秘密管理

```
GitHub Actions：
├─ Organization Secrets：跨仓库
├─ Repository Secrets：单仓库
├─ Environment Secrets：按环境（可加审批）
└─ OIDC 换云凭证（不用长期 Key）

OIDC 示例（AWS）：
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::xxx:role/github-actions
    aws-region: us-east-1
# 没有 AWS_ACCESS_KEY_ID，自动颁发临时 Token
```

## 8. 缓存优化

```yaml
- uses: actions/cache@v4
  with:
    path: |
      ~/.cache/pip
      node_modules
      /root/.m2
      ~/.gradle/caches
    key: ${{ runner.os }}-${{ hashFiles('**/package-lock.json', '**/pom.xml') }}

# Docker Buildx 缓存
- uses: docker/build-push-action@v6
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max

# Go Module cache
- uses: actions/setup-go@v5
  with:
    cache: true
    cache-dependency-path: go.sum
```

## 9. Monorepo 策略

```yaml
# 只跑受影响的项目
- uses: dorny/paths-filter@v3
  id: filter
  with:
    filters: |
      frontend: ['apps/frontend/**']
      backend:  ['apps/backend/**']

- if: steps.filter.outputs.frontend == 'true'
  run: cd apps/frontend && npm test

- if: steps.filter.outputs.backend == 'true'
  run: cd apps/backend && go test ./...
```

专用工具：**Turborepo**、**Nx**、**Bazel**、**Moon**。

## 10. 典型反模式

```
❌ 大型 jobs 顺序执行
   → 能并行的没并行
   ✅ 用 needs 建 DAG

❌ 每个 PR 都跑 E2E 30 分钟
   → PR 反馈慢
   ✅ 单元 + 集成 < 5 分钟，E2E 走 nightly 或 canary

❌ 部署到生产无审批
   → 重大变更应该人工批
   ✅ GitHub Environment + approvers

❌ 发布只有"全部" 
   → 问题影响全用户
   ✅ 金丝雀 + Feature Flags

❌ 回滚流程只在文档里
   → 紧急时找不到
   ✅ 一键回滚脚本 / Argo CD UI 回滚

❌ 部署后不监控
   → 问题被用户发现
   ✅ 部署后 5 分钟强制看指标

❌ CI 不缓存
   → 每次 10 分钟
   ✅ 缓存 + Docker layer cache
```

## 11. 生产检查清单

```
☐ 所有 PR 都跑 lint / test / security scan
☐ main 保护：require PR + checks pass
☐ 生产部署有人工审批
☐ Pipeline < 15 分钟（反馈快）
☐ 缓存 + 并行 + matrix
☐ Secrets 走 OIDC，不用长期 Key
☐ SHA pin 第三方 Action
☐ 镜像扫描 + SBOM + 签名
☐ 金丝雀 / Progressive Delivery
☐ Feature Flag 分离"部署"和"发布"
☐ 自动回滚配置（基于指标）
☐ 部署后监控窗口（smoke test + golden signals）
☐ 部署日志 + 审计
```

## 12. DORA 指标对应

```
Deployment Frequency（部署频率）
  → CI/CD 自动化 + Feature Flags 加速

Lead Time for Changes（提交到上线时间）
  → Pipeline 要快（< 15 分钟）

Change Failure Rate（变更失败率）
  → 测试覆盖 + Canary + Rollback

MTTR（恢复时间）
  → 自动回滚 + GitOps 一键回滚 + 好的监控
```

## 📖 参考资料

- [DORA 指标](https://dora.dev/)
- [Trunk-Based Development](https://trunkbaseddevelopment.com/)
- [Feature Flags - Martin Fowler](https://martinfowler.com/articles/feature-toggles.html)
- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Argo Rollouts](https://argoproj.github.io/argo-rollouts/)
- [OpenFeature](https://openfeature.dev/)
