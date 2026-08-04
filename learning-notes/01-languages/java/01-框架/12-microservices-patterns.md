# 微服务架构模式
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 从 private-notes 提取的技术学习笔记

## 微服务架构概述

微服务架构是一种将单一应用程序开发为一组小型服务的方法，每个服务运行在自己的进程中，并通过轻量级机制（通常是 HTTP RESTful API）进行通信。

## 核心模式

### 1. 服务拆分

**拆分原则**：
- 按业务领域拆分
- 单一职责原则
- 高内聚、低耦合

**拆分策略**：
- 按功能拆分
- 按数据拆分
- 按团队拆分

### 2. 服务通信

**同步通信**：
- REST API
- gRPC
- GraphQL

**异步通信**：
- 消息队列（Kafka、RabbitMQ）
- 事件驱动

### 3. 服务发现

**服务注册中心**：
- Eureka
- Consul
- Nacos

### 4. 配置管理

**配置中心**：
- Spring Cloud Config
- Nacos Config
- Apollo

### 5. 负载均衡

**负载均衡算法**：
- 轮询（Round Robin）
- 随机（Random）
- 加权轮询（Weighted Round Robin）
- 最少连接（Least Connections）

### 6. 熔断降级

**熔断器模式**：
- Hystrix
- Sentinel
- Resilience4j

### 7. 分布式事务

**解决方案**：
- 2PC（两阶段提交）
- TCC（Try-Confirm-Cancel）
- Saga 模式
- 最终一致性

## 最佳实践

1. **API 设计**：遵循 RESTful 规范
2. **数据管理**：每个服务独立数据库
3. **监控**：全链路追踪和监控
4. **测试**：单元测试、集成测试、契约测试
5. **部署**：容器化、CI/CD

## 技术栈

> 🔄 更新于 2026-07-08

<!-- version-check: Spring Boot 4.1.0, Spring Cloud 2025.1.2, checked 2026-07-08 -->

### 当前推荐技术栈（2026-07）

- **服务框架**：Spring Boot **4.1.x**（推荐）/ 4.0.7（维护线）
- **服务发现**：Nacos 2.x（国内首选）、Consul
- **配置中心**：Nacos Config、Spring Cloud Config
- **网关**：Spring Cloud Gateway
- **负载均衡**：Spring Cloud LoadBalancer（替代 Ribbon）
- **熔断降级**：Sentinel（国内首选）、Resilience4j
- **消息队列**：Kafka、RabbitMQ
- **监控**：Prometheus + Grafana、OpenTelemetry、Micrometer
- **链路追踪**：Micrometer Tracing（替代 Sleuth）+ Zipkin/Jaeger
- **HTTP 客户端**：RestClient / HTTP Interface Client（替代 RestTemplate/Feign）
- **gRPC**：Spring gRPC 1.1.0（Boot 4.1 内置 starter）

### 已废弃/不推荐的技术

| 旧技术 | 替代方案 | 说明 |
|--------|---------|------|
| Eureka | Nacos / Consul | Netflix OSS 已停止维护 |
| Ribbon | Spring Cloud LoadBalancer | Ribbon 已进入维护模式 |
| Hystrix | Sentinel / Resilience4j | Hystrix 已停止维护 |
| Zuul | Spring Cloud Gateway | Zuul 1.x 已停止维护 |
| Sleuth | Micrometer Tracing | Sleuth 已合并到 Micrometer |
| RestTemplate | RestClient | RestTemplate 进入维护模式 |
| OpenFeign | HTTP Interface Client | Spring Cloud 2025.1 中 OpenFeign 支持已移除 |

### Spring Cloud 版本对应关系

| Spring Cloud | Spring Boot | 代号 | 状态 |
|-------------|-------------|------|------|
| 2025.1.2 | 4.0.7 / 4.1.0 | Oakwood | 最新（2026-06-11） |
| 2024.0 | 3.4.x | Moorgate | 稳定 |
| 2023.0 | 3.2.x/3.3.x | Leyton | 维护中 |
| 2022.0 | 3.0.x/3.1.x | Kilburn | EOL |
| Hoxton | 2.2.x/2.3.x | — | EOL |

> 来源：[Spring Cloud 官方](https://spring.io/projects/spring-cloud/)

## 2026 微服务架构新增维度：Agent 化能力

> 🔄 更新于 2026-07-08

<!-- version-check: Spring AI 2.0.0 GA, Spring Boot 4.1.0, MCP SDK 2.0.0, A2A v1.0, checked 2026-07-08 -->

随着 **Spring AI 2.0.0 GA（2026-06-12）**、**Spring Boot 4.1.0 GA（2026-06-10）** 以及 **A2A v1.0 / MCP Streamable HTTP** 协议的成熟，微服务架构需要新增"Agent 化能力"这一层。Agent 服务不再是独立技术栈，而是和传统微服务并列的运行单元。来源：[Spring AI 2.0.0 GA](https://spring.io/blog/2026/06/12/spring-ai-2-0-0-GA-available-now)、[Spring AI A2A 集成](https://spring.io/blog/2026/01/29/spring-ai-agentic-patterns-a2a-integration)、[Spring AI MCP 总览](https://docs.spring.io/spring-ai/reference/api/mcp/mcp-overview.html)

### 增强后的架构分层

```
                    ┌────────────────────────┐
                    │     User / Client      │
                    └───────────┬────────────┘
                                │
                    ┌───────────▼────────────┐
                    │  Spring Cloud Gateway  │  ← 同时处理 REST + A2A
                    └───────────┬────────────┘
                                │
            ┌───────────────────┼───────────────────────┐
            │                   │                       │
   ┌────────▼────────┐  ┌──────▼─────────┐   ┌─────────▼─────────┐
   │ 业务微服务       │  │ Agent 微服务    │   │ MCP Server 集群    │
   │ (Spring Boot)   │  │ (Spring AI 2.0)│   │ (工具/数据源)      │
   └────────┬────────┘  └──────┬─────────┘   └─────────┬─────────┘
            │                   │                       │
            └───── Nacos 服务注册 / Sentinel 治理 ────────┘
```

### 服务类型对照（2026）

| 服务类型 | 协议 | 注册发现 | 容错 | 典型框架 |
|---------|------|----------|------|----------|
| 业务微服务 | REST / gRPC | Nacos | Sentinel | Spring Boot **4.1** + Spring Cloud 2025.1.2 |
| **Agent 微服务** | **A2A v1.0** | Nacos + Agent Card | Sentinel + 工具审批 | **Spring AI 2.0.0** |
| **MCP 工具服务** | **MCP Streamable HTTP** | 显式 manifest | OAuth 2.1 + Tool RBAC | **Spring AI MCP Server Boot Starter** |
| 数据服务 | gRPC / SQL | Nacos | Resilience4j | Spring Data 2026.0 |

### 引入 Agent 化能力的最小改动

```yaml
# 同一份 Spring Boot 4.1 应用同时提供 REST + MCP + A2A
spring:
  cloud:
    nacos:
      discovery:
        server-addr: nacos.example.com:8848
  ai:
    mcp:
      server:
        enabled: true
        protocol: STREAMABLE   # 2.0 默认传输，替代废弃的 SSE
    a2a:
      enabled: true
      base-url: "https://orders-agent.example.com"
      capabilities: ["order-query", "order-refund"]
```

### 与传统模式的关键差异

1. **服务发现需要 Agent Card**：A2A v1.0 要求每个 Agent 暴露 `.well-known/agent.json`，Nacos 3.2+ 已支持把 Agent Card 作为元数据写入注册中心
2. **熔断需要工具粒度**：MCP 工具调用的失败/超时要按工具维度统计，Sentinel 1.8.8 已经增加 `mcp.tool` 资源类型
3. **认证需要 OAuth 2.1 + PKCE**：MCP Streamable HTTP 强制要求，传统的 API Key 仅用于内网
4. **工具调用统一走 Advisor 链**：Spring AI 2.0 的 `ToolCallingAdvisor` 将工具循环从各 ChatModel 实现中抽出，跨 OpenAI / Anthropic / Google GenAI 行为一致
5. **Agent 微服务对应 Spring AI 2.0.0**：原来用 LangChain4j / langchain-java 的项目可迁移到 Spring 原生方案；复杂 Agent 编排可关注 2.1 的 `spring-ai-agent` 模块（2026-11 目标）

### 选型建议

- **传统业务系统**：保持 Spring Boot 4.1 + Spring Cloud 2025.1.2，**不必为引入 AI 而推翻架构**
- **新建 Agent 服务**：**Spring Boot 4.1.0 + Spring AI 2.0.0**，避免 1.x API 摇摆
- **仍在 Boot 3.5.x**：Spring AI **1.1.8**（最终维护线），但须规划向 Boot 4.x 迁移（3.5 OSS 已于 2026-06-30 结束）
- **遗留 RestTemplate / Feign 项目**：先迁到 RestClient + HTTP Interface Client，再考虑 Agent 化

## 参考资料

- [微服务架构模式](https://microservices.io/patterns/)
- [Spring Cloud 官方文档](https://spring.io/projects/spring-cloud)
- [Spring Boot 4.0 Release Highlights](https://spring.io/projects/release-highlights)
- [Spring AI 2.0.0 GA 发布公告](https://spring.io/blog/2026/06/12/spring-ai-2-0-0-GA-available-now)
- [Spring AI MCP Overview](https://docs.spring.io/spring-ai/reference/api/mcp/mcp-overview.html)
- [Building Interoperable Agents with A2A — Spring Blog](https://spring.io/blog/2026/01/29/spring-ai-agentic-patterns-a2a-integration)

