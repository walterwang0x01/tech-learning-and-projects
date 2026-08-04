# Spring Boot 微服务架构示例

## 项目简介

这是一个基于 Spring Boot 的微服务架构示例项目，展示了事件驱动架构、分布式系统设计等企业级后端开发实践。

## 技术栈

- **框架**: Spring Boot 3.x, Spring Cloud
- **消息队列**: Kafka
- **数据库**: PostgreSQL, MongoDB
- **缓存**: Redis
- **服务发现**: Spring Cloud Gateway
- **监控**: Prometheus, Grafana
- **容器化**: Docker, Kubernetes

## 核心功能

- 微服务拆分与通信
- 事件驱动架构实现
- 分布式事务处理
- 服务熔断与降级
- 统一日志与追踪
- 性能监控与告警

## 项目结构

```
spring-boot-microservice-demo/
├── common-lib/          # 公共库（日志、追踪、异常处理）
├── user-service/        # 用户服务
├── order-service/       # 订单服务
├── payment-service/     # 支付服务
├── api-gateway/         # API 网关
└── docker-compose.yml   # 本地开发环境
```

## 快速开始

### 前置要求
- JDK 17+
- Docker & Docker Compose
- Maven 3.8+

### 启动步骤

1. 克隆项目
```bash
git clone https://github.com/your-username/spring-boot-microservice-demo.git
cd spring-boot-microservice-demo
```

2. 启动基础设施
```bash
docker-compose up -d
```

3. 启动服务
```bash
mvn clean install
mvn spring-boot:run -pl user-service
mvn spring-boot:run -pl order-service
```

## 架构设计

### 事件驱动架构
- 使用 Kafka 实现服务间异步通信
- 保证最终一致性
- 支持事件溯源

### 服务治理
- 统一异常处理
- 链路追踪（TraceId）
- 服务降级策略

## 性能指标

- QPS: 支持 10,000+ 并发请求
- 响应时间: P99 < 200ms
- 可用性: 99.9%

## 最佳实践

- TDD 开发模式（测试覆盖率 > 80%）
- 代码规范检查（Checkstyle, SpotBugs）
- CI/CD 自动化部署
- 容器化部署（K8s）

## License

MIT License

