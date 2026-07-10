# Docker 基础与实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 从 private-notes 提取的技术学习笔记

## Docker 简介

Docker 是一个开源的应用容器引擎，让开发者可以打包他们的应用以及依赖包到一个可移植的镜像中。

## 核心概念

### 1. 镜像（Image）

镜像是一个只读的模板，用于创建容器。

### 2. 容器（Container）

容器是镜像的运行实例，可以被创建、启动、停止、删除。

### 3. 仓库（Repository）

仓库是集中存放镜像的地方。

## Docker 解决的问题

### 依赖兼容问题

- 将应用的 Libs、Deps、配置与应用一起打包
- 将每个应用放到一个隔离容器去运行

### 操作系统环境差异

- 共享操作系统内核
- 每个容器拥有自己的文件系统、CPU、内存、进程空间

## 常用命令

```bash
# 镜像操作
docker images              # 查看镜像
docker pull <image>        # 拉取镜像
docker build -t <name> .  # 构建镜像
docker rmi <image>         # 删除镜像

# 容器操作
docker ps                  # 查看运行中的容器
docker ps -a               # 查看所有容器
docker run <image>         # 运行容器
docker stop <container>    # 停止容器
docker rm <container>      # 删除容器

# Docker Compose（v2 插件语法，无短横线；docker-compose v1 已于 2023-07 EOL）
# <!-- 修复于 2026-07-10: docker-compose → docker compose -->
docker compose up          # 启动服务
docker compose down        # 停止服务
docker compose ps          # 查看服务状态
```

## Dockerfile 示例

```dockerfile
FROM openjdk:17-jre-slim
WORKDIR /app
COPY target/*.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

## 最佳实践

1. **多阶段构建**：减小镜像大小
2. **使用 .dockerignore**：排除不需要的文件
3. **非 root 用户运行**：提高安全性
4. **健康检查**：添加 HEALTHCHECK
5. **合理使用缓存**：优化构建速度

## 参考资料

- [Docker 官方文档](https://docs.docker.com/)
- [Docker 最佳实践](https://docs.docker.com/develop/dev-best-practices/)



## Docker 版本演进（2025-2026）

<!-- version-check: Docker Engine 29.6.1（2026-06-26）, Docker Desktop 4.81.0（2026-07-06）, checked 2026-07-10 -->
<!-- 修复于 2026-07-10: 补充当前具体补丁版本号，内容结论未变 -->

> 🔄 更新于 2026-07-10

### Docker Engine 28（2025-02）

**核心变化**：容器网络安全加固
- 默认隔离未发布端口，防止外部直接访问容器内部端口
- Docker Desktop 用户不受影响（内部网络已有保护）

> 来源：[Docker Engine v28](https://www.docker.com/blog/docker-engine-28-hardening-container-networking-by-default/)

### Docker Engine 29（2026-03）

**三个向后不兼容的变化**：

| 变化 | 影响 | 受影响用户 |
|------|------|-----------|
| 最低 API 版本提升至 1.44 | Docker v24 及更早版本的客户端被拒绝 | 使用旧版 Docker CLI/SDK 的用户 |
| containerd 镜像存储成为默认 | 镜像由 containerd 管理，替代 Docker 传统存储 | 从 v27 及更早版本升级的用户 |
| nftables 支持（可选） | Docker 可使用 nftables 替代 iptables | 有自定义 iptables 规则的用户 |

**升级前检查**：

```bash
# 检查当前 Docker 版本
docker version --format '{{.Server.Version}}'
# 如果是 24.x 或更低，API 版本变化会导致问题

# 检查镜像存储驱动
docker info --format '{{.Driver}}'
# 如果是 overlay2，升级后新拉取的镜像使用 containerd 存储

# 检查防火墙规则
sudo iptables -L DOCKER-USER -n 2>/dev/null | head -20
# 如果有自定义规则，需要验证 nftables 兼容性
```

> 来源：[Docker v29 Migration Guide](https://blog.canadianwebhosting.com/docker-v29-migration-guide-self-hosters/)

### Docker 2026 年新方向

- **Docker Sandboxes**（2026-04，Docker Desktop 4.50+）：基于 MicroVM 的 Agent 隔离环境，让 AI Agent 安全地自主执行代码。超过 25% 的生产代码已由 AI 编写，使用 Agent 的开发者合并 PR 数量增加约 60%
- **Docker AI Agent（Gordon）**：Docker Desktop 4.61+ 内置 AI Agent，具备 Shell 访问、Docker CLI 访问、文件系统访问和 Docker 最佳实践知识
- **Docker MCP Gateway**：300+ 预构建容器化 MCP Server，一键部署，支持 Claude Code 等 Coding Agent 集成
- **Docker Offload GA**（2026-01）：将 Docker Engine 运行在云端，本地 Docker Desktop 命令透明代理到远程引擎
- **Docker Hardened Images**：安全加固的官方镜像，减少 CVE 攻击面

> 🔄 更新于 2026-05-04

```bash
# Docker Sandboxes：在隔离 MicroVM 中运行 AI Agent
docker sandbox run --image node:22 -- npx claude-code

# Docker MCP Gateway：一键启动 MCP Server
# 在 Docker Desktop 设置中启用 MCP Toolkit（Beta）
```

> 来源：[Docker Sandboxes](https://www.docker.com/blog/docker-desktop-4-50/) | [Gordon AI Agent](https://www.docker.com/blog/gordon-dockers-ai-agent-just-got-an-update/) | [Docker Offload GA](https://www.docker.com/blog/docker-offload-now-generally-available-the-full-power-of-docker-for-every-developer-everywhere/) | [Docker MCP](https://www.docker.com/blog/run-claude-code-with-docker/)

### 版本选择建议（2026）

| 场景 | 推荐版本 | 说明 |
|------|---------|------|
| 生产环境 | Docker Engine 29.x | 当前稳定版，containerd 存储更高效 |
| CI/CD | Docker Engine 29.x | GitHub Actions 已默认使用 |
| 开发环境 | Docker Desktop 最新版 | 包含 AI Agent、Model Runner 等新功能 |
| 旧项目维护 | Docker Engine 28.x | 如果无法立即迁移 API 版本 |
