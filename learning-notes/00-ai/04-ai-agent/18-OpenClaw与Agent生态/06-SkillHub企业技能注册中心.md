# SkillHub 企业技能注册中心
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

[SkillHub](https://github.com/iflytek/skillhub) 是科大讯飞（iFLYTEK）开源的企业级 Agent 技能注册中心，定位类似于"私有的技能包 npm registry"。团队可以在组织内部发布、发现和管理可复用的 Agent 技能包，支持自托管部署在企业防火墙内。

```
┌──────────────────── SkillHub 定位 ────────────────────┐
│                                                        │
│  npm registry  ←→  JavaScript 包管理                    │
│  PyPI          ←→  Python 包管理                        │
│  ClawHub       ←→  OpenClaw 公共技能市场                 │
│  SkillHub      ←→  企业私有 Agent 技能注册中心            │
│                                                        │
└────────────────────────────────────────────────────────┘
```

## 2. 核心特性

| 特性 | 说明 |
|------|------|
| 自托管 & 私有 | 部署在自有基础设施，数据不出防火墙，完全数据主权 |
| 发布与版本管理 | 语义化版本、自定义标签（beta/stable）、自动 latest 追踪 |
| 全文搜索 | 按命名空间、下载量、评分、时间过滤，可见性权限控制 |
| 团队命名空间 | 按团队/全局组织技能，每个命名空间有 Owner/Admin/Member 角色 |
| 审核与治理 | 命名空间内审核 + 全局推广审批，操作审计日志 |
| 社交功能 | Star、评分、下载量统计 |
| API Token | 生成作用域 Token，前缀哈希安全存储 |
| CLI 优先 | 原生 REST API + ClawHub 兼容层 |
| 可插拔存储 | 开发用本地文件系统，生产用 S3/MinIO |
| 国际化 | 基于 i18next 的多语言支持 |

## 3. 架构

```
┌─────────────┐     ┌─────────────┐     ┌──────────────┐
│   Web UI    │     │  CLI Tools  │     │  REST API    │
│  (React 19) │     │  (clawhub)  │     │              │
└──────┬──────┘     └──────┬──────┘     └──────┬───────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           │
                    ┌──────▼──────┐
                    │   Nginx     │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │ Spring Boot │  Auth · RBAC · Core Services
                    │  (Java 21)  │  OAuth2 · API Tokens · Audit
                    └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
       ┌──────▼───┐  ┌─────▼────┐  ┌────▼────┐
       │PostgreSQL│  │  Redis   │  │ Storage │
       │    16    │  │    7     │  │ S3/MinIO│
       └──────────┘  └──────────┘  └─────────┘
```

技术栈：
- 后端：Spring Boot 3.2.3 + Java 21，多模块 Maven（app/domain/auth/search/storage/infra）
- 前端：React 19 + TypeScript + Vite + TanStack Router/Query + Tailwind CSS + Radix UI
- 数据库：PostgreSQL 16（Flyway 迁移）
- 缓存：Redis 7（会话管理）
- 存储：S3/MinIO（技能包文件）
- 监控：Prometheus + Grafana

## 4. 快速部署

### 一键启动（Docker）

```bash
# 清理并启动
rm -rf /tmp/skillhub-runtime
curl -fsSL https://imageless.oss-cn-beijing.aliyuncs.com/runtime.sh | sh -s -- up

# 配置公网 URL（生产推荐）
curl -fsSL https://imageless.oss-cn-beijing.aliyuncs.com/runtime.sh | sh -s -- up \
  --public-url https://skillhub.your-company.com

# 国内用户（阿里云镜像）
curl -fsSL https://imageless.oss-cn-beijing.aliyuncs.com/runtime.sh | sh -s -- up \
  --aliyun --public-url https://skillhub.your-company.com
```

### 部署参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--public-url` | 公网访问地址（推荐） | `--public-url https://skill.example.com` |
| `--version` | 指定镜像版本 | `--version v0.2.0` |
| `--aliyun` | 使用阿里云镜像 | `--aliyun` |
| `--home` | 运行时目录 | `--home /opt/skillhub` |
| `--no-scanner` | 禁用安全扫描 | `--no-scanner` |

### 本地开发

```bash
# 启动完整开发环境
make dev-all

# 访问
# Web UI:      http://localhost:3000
# Backend API: http://localhost:8080

# 默认账户
# 普通用户: local-user（通过 X-Mock-User-Id header）
# 管理员:   local-admin（SUPER_ADMIN 角色）
# Bootstrap 管理员: admin / ChangeMe!2026
```

### Kubernetes 部署

```bash
kubectl apply -f deploy/k8s/configmap.yaml
kubectl apply -f deploy/k8s/secret.yaml
kubectl apply -f deploy/k8s/backend-deployment.yaml
kubectl apply -f deploy/k8s/frontend-deployment.yaml
kubectl apply -f deploy/k8s/services.yaml
kubectl apply -f deploy/k8s/ingress.yaml
```

## 5. 与 Agent 平台集成

SkillHub 作为技能注册后端，支持多个 Agent 平台的客户端接入。

### OpenClaw CLI

```bash
# 配置 SkillHub 为注册中心
export CLAWHUB_REGISTRY=https://skillhub.your-company.com

# 认证
clawhub login --token YOUR_API_TOKEN

# 搜索和安装技能
npx clawhub search email
npx clawhub install my-skill
npx clawhub install my-namespace--my-skill

# 发布技能
npx clawhub publish ./my-skill

# 也可以指定安装目录，适用于其他 Coding Agent
npx clawhub --dir ~/.claude/skills install my-skill
```

### AstronClaw

AstronClaw 是基于 OpenClaw 的云端 AI 助手，支持企业微信、钉钉、飞书等平台。连接 SkillHub 后可实现一键安装技能、对话式自动安装、组织内自定义技能管理。

### Loomy

Loomy 是桌面端 AI 工作伙伴，深度集成本地文件和系统工具。连接 SkillHub 可发现和安装组织特定技能，增强本地桌面自动化。

### astron-agent

astron-agent 是讯飞星辰 Agent 框架，SkillHub 中的技能可被 astron-agent 引用和加载，实现从开发到生产的版本化技能生命周期管理。

## 6. 治理模型

```
┌─────────────────── 技能治理流程 ───────────────────┐
│                                                     │
│  开发者发布技能                                       │
│       ↓                                             │
│  团队命名空间审核（Team Admin）                        │
│       ↓                                             │
│  命名空间内可见                                       │
│       ↓                                             │
│  申请推广到全局（Platform Admin 审批）                  │
│       ↓                                             │
│  全组织可见                                           │
│                                                     │
│  所有操作 → 审计日志（合规追溯）                        │
└─────────────────────────────────────────────────────┘

角色体系：
├─ Owner    — 命名空间所有者，完全控制
├─ Admin    — 管理成员、审核技能发布
├─ Member   — 发布和安装技能
└─ Platform Admin — 全局推广审批、系统管理
```

## 7. 与 ClawHub 对比

| 维度 | ClawHub | SkillHub |
|------|---------|----------|
| 定位 | 公共技能市场 | 企业私有注册中心 |
| 部署 | 云端托管 | 自托管（Docker/K8s） |
| 数据主权 | 公开 | 完全私有 |
| 命名空间 | 用户级 | 团队级 + 全局级 |
| 审核机制 | 社区驱动 | 多级审批（团队→全局） |
| RBAC | 基础 | 企业级（Owner/Admin/Member） |
| 审计日志 | ❌ | ✅ 完整审计 |
| 账户合并 | ❌ | ✅ 多 OAuth 身份合并 |
| 存储 | 云端 | 可插拔（本地/S3/MinIO） |
| 监控 | ❌ | ✅ Prometheus + Grafana |
| 适用场景 | 开源社区共享 | 企业内部技能治理 |

## 8. 生产部署建议

```
生产环境检查清单：
├─ 设置 SKILLHUB_PUBLIC_BASE_URL 为最终 HTTPS 入口
├─ PostgreSQL / Redis 绑定 127.0.0.1
├─ 使用外部 S3/OSS（SKILLHUB_STORAGE_S3_*）
├─ 修改 BOOTSTRAP_ADMIN_PASSWORD（默认密码会被拒绝）
├─ 初始设置后轮换或禁用 bootstrap admin
├─ 部署前运行 make validate-release-config
└─ 配置 Prometheus + Grafana 监控
```

## 9. 在 Agent Skills 生态中的位置

```
Agent Skills 生态全景：

公共市场：
├─ ClawHub        — OpenClaw 公共技能市场
├─ MCP Server 目录 — 1000+ MCP 工具
├─ LangChain Hub  — Chains/Tools
├─ Coze 插件商店   — Bot 插件
└─ Dify 工具市场   — 工作流工具

企业私有：
├─ SkillHub ★     — 讯飞开源，企业级技能注册中心
├─ 企业内部 MCP Server — 自建 MCP 服务
└─ 私有 PyPI/npm   — 传统包管理方式

SkillHub 填补了 Agent 技能生态中"企业私有注册中心"的空白，
类似于 npm → Verdaccio、PyPI → devpi 的关系。
```

## 🎬 推荐资源

### 📖 官方文档
- [SkillHub GitHub](https://github.com/iflytek/skillhub) — 开源仓库
- [用户指南](https://github.com/iflytek/skillhub/tree/main/docs) — 技能发布、搜索、CLI 使用
- [开发者文档](https://github.com/iflytek/skillhub/tree/main/docs) — 架构、API、本地开发、部署运维

### 🔗 相关项目
- [astron-agent](https://github.com/iflytek/astron-agent) — 讯飞星辰 Agent 框架
- [OpenClaw](https://github.com/openclaw/openclaw) — 开源 Agent 编排平台
- [ifly-workflow-mcp-server](https://github.com/iflytek/ifly-workflow-mcp-server) — 讯飞工作流 MCP Server
