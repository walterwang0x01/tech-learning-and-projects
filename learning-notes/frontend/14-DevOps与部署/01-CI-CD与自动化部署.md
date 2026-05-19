# CI/CD 与自动化部署
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. GitHub Actions

<!-- version-check: actions/checkout v5/v6, setup-node v5, Node.js 22 LTS, checked 2026-05-19 -->
<!-- 修复于 2026-05-19: 基础示例升级 actions 版本 v4 → v5（v6 已 GA），Node 20 → 22（20 即将进入维护期） -->

```yaml
# .github/workflows/ci.yml
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: pnpm/action-setup@v4
        with: { version: 10 }
      - uses: actions/setup-node@v5
        with:
          node-version: 22
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm test -- --run
      - run: pnpm build

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: pnpm/action-setup@v4
        with: { version: 10 }
      - uses: actions/setup-node@v5
        with: { node-version: 22, cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
      # 部署到服务器 / CDN / Vercel / Netlify 等
```

## 2. Docker 构建推送

```yaml
  docker:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v5
      - uses: docker/setup-buildx-action@v3
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/build-push-action@v6
        with:
          push: true
          tags: ghcr.io/${{ github.repository }}:latest
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## 3. 版本管理（Changesets）

```bash
# 安装
pnpm add -D @changesets/cli
npx changeset init

# 添加变更记录
npx changeset
# 选择包 → 选择版本类型（patch/minor/major）→ 写变更描述

# 发布
npx changeset version  # 更新版本号和 CHANGELOG
npx changeset publish  # 发布到 npm
```

## 4. 部署平台

```
Vercel：
- 零配置部署 Next.js / React / Vue
- 自动 Preview 部署（PR 预览）
- Edge Functions

Netlify：
- 静态站点部署
- Serverless Functions
- 表单处理

自建服务器：
- Docker + Nginx
- PM2 + Node.js
- Kubernetes
```

## 5. GitHub Actions 2026 安全与定价变化

<!-- version-check: GitHub Actions 2026 security roadmap, pricing changes, checked 2026-04-28 -->

> 🔄 更新于 2026-04-28

### 5.1 2026 安全路线图

GitHub 于 2026-03-26 发布了 Actions 安全路线图，针对 tj-actions/changed-files、Nx、trivy-action 等供应链攻击事件，从三个层面加固安全：

**层面一：生态系统 — 工作流依赖锁定**

即将推出 `dependencies:` 段，锁定所有直接和间接依赖的 commit SHA，类似 Go 的 `go.mod + go.sum`。公开预览 3-6 个月内，GA 6 个月内。

**层面二：攻击面 — 策略控制与安全默认值**

- Action 允许列表（Allowlisting）已扩展到所有计划层级
- 不可变发布（Immutable Releases）已 GA
- 更细粒度的 Secret 作用域和权限控制

**层面三：基础设施 — Runner 可观测性与网络边界**

- 实时 Runner 遥测和审计日志
- 可强制执行的出站网络控制（Egress Controls）

**当前最佳实践（2026）：**

```yaml
# ✅ 推荐：使用 commit SHA 固定依赖
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2

# ❌ 避免：使用可变标签
- uses: actions/checkout@v4

# ✅ 推荐：最小权限
permissions:
  contents: read
  packages: write
```

> 来源：[GitHub Blog - Actions 2026 Security Roadmap](https://github.blog/security/supply-chain-security/whats-coming-to-our-github-actions-2026-security-roadmap/)、[Wiz - Hardening GitHub Actions](https://www.wiz.io/blog/github-actions-security-guide)

### 5.2 定价变化（2026 年 3 月生效）

| 变化 | 详情 |
|------|------|
| 托管 Runner 降价 | 最高降低 39% |
| 自托管 Runner 新增费用 | $0.002/分钟（Actions 云平台费） |
| 公共仓库 | 仍然免费 |
| 影响范围 | GitHub 称 96% 用户账单不变 |

> 来源：[GitHub - Pricing Changes for GitHub Actions](https://resources.github.com/actions/2026-pricing-changes-for-github-actions/)

### 5.3 2026 年推荐 CI/CD 配置

```yaml
# .github/workflows/ci.yml — 2026 年推荐配置
name: CI/CD

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

# 全局最小权限
permissions:
  contents: read

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      # 使用 SHA 固定依赖（防止供应链攻击）
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4.2.2
      - uses: pnpm/action-setup@a7487c7e89a18df77bba2c740b5837da1ba4f305 # v4.1.0
        with: { version: 10 }
      - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020 # v4.4.0
        with:
          node-version: 22
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint
      - run: pnpm test -- --run
      - run: pnpm build

  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683
      - uses: pnpm/action-setup@a7487c7e89a18df77bba2c740b5837da1ba4f305
        with: { version: 10 }
      - uses: actions/setup-node@49933ea5288caeca8642d1e84afbd3f7d6820020
        with: { node-version: 22, cache: 'pnpm' }
      - run: pnpm install --frozen-lockfile
      - run: pnpm build
```
