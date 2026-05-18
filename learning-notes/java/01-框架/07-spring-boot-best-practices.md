# Spring Boot 最佳实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 本文档总结了 Spring Boot 开发中的最佳实践和常见模式

## 1. 项目结构

### 推荐的项目结构
```
project/
├── common-lib/          # 公共库
├── user-service/        # 业务服务
├── order-service/
└── api-gateway/
```

### 包结构
```
com.example.service/
├── controller/         # 控制器层
├── service/           # 业务逻辑层
├── repository/        # 数据访问层
├── entity/            # 实体类
└── dto/               # 数据传输对象
```

## 2. 统一异常处理

使用 `@RestControllerAdvice` 统一处理异常：

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    @ExceptionHandler(BusinessException.class)
    public ResponseEntity<ErrorResponse> handleBusinessException(BusinessException e) {
        // 统一异常响应格式
    }
}
```

## 3. 统一响应格式

定义标准的 API 响应格式：

```java
@Data
@Builder
public class ApiResponse<T> {
    private Integer code;
    private String message;
    private T data;
    private LocalDateTime timestamp;
}
```

## 4. 全链路追踪

使用 TraceId 实现全链路追踪：

```java
@Component
public class TraceIdFilter extends OncePerRequestFilter {
    @Override
    protected void doFilterInternal(...) {
        String traceId = UUID.randomUUID().toString();
        MDC.put("traceId", traceId);
        // ...
    }
}
```

## 5. 配置管理

### 使用环境变量
```yaml
spring:
  datasource:
    url: ${DATASOURCE_URL:jdbc:postgresql://localhost:5432/db}
    username: ${DATASOURCE_USERNAME:postgres}
    password: ${DATASOURCE_PASSWORD:postgres}
```

### 配置文件分离
- `application.yml` - 基础配置
- `application-local.yml` - 本地开发（不提交）
- `application-prod.yml` - 生产环境（不提交）

## 6. 测试

### 单元测试
```java
@ExtendWith(MockitoExtension.class)
class UserServiceTest {
    @Mock
    private UserRepository userRepository;
    
    @Test
    void testCreateUser() {
        // 测试逻辑
    }
}
```

### 集成测试
```java
@SpringBootTest
@AutoConfigureMockMvc
class UserControllerTest {
    @Autowired
    private MockMvc mockMvc;
    
    @Test
    void testCreateUser() throws Exception {
        // 测试逻辑
    }
}
```

## 7. 日志规范

### 日志级别
- ERROR: 系统错误，需要立即处理
- WARN: 警告信息，可能的问题
- INFO: 重要业务流程
- DEBUG: 调试信息（开发环境）

### 日志格式
```yaml
logging:
  pattern:
    console: "%d{yyyy-MM-dd HH:mm:ss} [%thread] %-5level [%X{traceId}] %logger{36} - %msg%n"
```

## 8. 事件驱动架构

使用 Kafka 实现事件驱动：

```java
@Service
public class UserService {
    private final KafkaTemplate<String, Object> kafkaTemplate;
    
    public void createUser(User user) {
        // 创建用户
        userRepository.save(user);
        // 发送事件
        kafkaTemplate.send("user-created", user.getId().toString(), user);
    }
}
```

## 9. 监控和健康检查

### Actuator 配置
```yaml
management:
  endpoints:
    web:
      exposure:
        include: health,info,prometheus
```

### 自定义健康检查
```java
@Component
public class CustomHealthIndicator implements HealthIndicator {
    @Override
    public Health health() {
        // 检查逻辑
        return Health.up().build();
    }
}
```

## 10. 容器化部署

### Dockerfile
```dockerfile
FROM maven:3.9-eclipse-temurin-17 AS build
WORKDIR /app
COPY . .
RUN mvn clean package -DskipTests

FROM eclipse-temurin:17-jre-alpine
COPY --from=build /app/target/*.jar app.jar
ENTRYPOINT ["java", "-jar", "app.jar"]
```

## 11. Spring Boot 版本演进

> 🔄 更新于 2026-04-18

<!-- version-check: Spring Boot 4.0.0, checked 2026-04-18 -->

### Spring Boot 3.x 重大变化（2022-11 至 2025-05）

Spring Boot 3.0 是自 2.x 以来最大的版本升级：

| 变化 | 说明 |
|------|------|
| **Java 17 基线** | 最低要求 Java 17，推荐 Java 21 |
| **Jakarta EE 10** | `javax.*` → `jakarta.*` 命名空间迁移 |
| **GraalVM 原生镜像** | 一等公民支持，启动时间 < 100ms |
| **可观测性** | Micrometer Observation API + OpenTelemetry 集成 |
| **Virtual Threads** | 3.2+ 支持 `spring.threads.virtual.enabled=true` |
| **HTTP Interface Client** | 声明式 HTTP 客户端（类似 Feign） |
| **RestClient** | 3.2+ 新增，替代 RestTemplate 的现代 API |

```yaml
# Spring Boot 3.2+ 启用虚拟线程
spring:
  threads:
    virtual:
      enabled: true
```

```java
// RestClient（Spring Boot 3.2+，替代 RestTemplate）
@Configuration
public class RestClientConfig {
    @Bean
    RestClient restClient(RestClient.Builder builder) {
        return builder
            .baseUrl("https://api.example.com")
            .defaultHeader("Accept", "application/json")
            .build();
    }
}

// 使用 RestClient
@Service
public class UserService {
    private final RestClient restClient;

    public User getUser(Long id) {
        return restClient.get()
            .uri("/users/{id}", id)
            .retrieve()
            .body(User.class);
    }
}
```

### Spring Boot 4.0（2025-11-20）

> Spring Boot 4.0 基于 Spring Framework 7，是继 3.0 之后的又一次重大升级。
> 来源：[Spring Boot 4.0 Release Notes](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Release-Notes)

**核心变化：**

| 变化 | 说明 |
|------|------|
| **Spring Framework 7** | 底层框架大版本升级 |
| **Jakarta EE 11** | 从 Jakarta EE 10 升级 |
| **Jackson 3** | 默认序列化库升级到 Jackson 3 |
| **JSpecify Null-Safety** | 全面采用 JSpecify 空安全注解 |
| **原生 API 版本控制** | 内置 `spring.mvc.apiversion.*` 配置 |
| **HTTP Service Clients** | 自动配置声明式 HTTP 客户端 |
| **OpenTelemetry Starter** | 新增 `spring-boot-starter-opentelemetry` |
| **Gradle 9 支持** | 支持 Gradle 9，保留 Gradle 8.14+ 兼容 |

```java
// Spring Boot 4.0：HTTP Service Client（自动配置）
@HttpExchange(url = "https://api.example.com")
public interface UserService {

    @GetExchange("/users/{id}")
    User getUser(@PathVariable Long id);

    @PostExchange("/users")
    User createUser(@RequestBody User user);
}

// 直接注入使用，无需手动配置
@RestController
public class UserController {
    private final UserService userService;

    @GetMapping("/users/{id}")
    public User getUser(@PathVariable Long id) {
        return userService.getUser(id);
    }
}
```

```java
// Spring Boot 4.0：API 版本控制（原生支持）
@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping(produces = "application/vnd.api.v1+json")
    public List<UserV1> getUsersV1() { /* ... */ }

    @GetMapping(produces = "application/vnd.api.v2+json")
    public List<UserV2> getUsersV2() { /* ... */ }
}
```

### 版本选择建议

```
┌─────────────────────────────────────────────────────┐
│            Spring Boot 版本选择指南                   │
├─────────────────────────────────────────────────────┤
│                                                     │
│  新项目（2026 年）                                   │
│  ├── 保守选择 → Spring Boot 3.5.x + Java 21        │
│  └── 前沿选择 → Spring Boot 4.0.x + Java 21        │
│                                                     │
│  现有项目迁移路径                                    │
│  ├── 2.x → 先升级到 3.5.x → 再升级到 4.0           │
│  └── 3.x → 升级到 3.5.x → 再升级到 4.0             │
│                                                     │
│  ⚠️ Spring Boot 3.5 是 3.x 最后一个 minor 版本     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Dockerfile 更新

```dockerfile
# Spring Boot 4.0 推荐 Dockerfile（Java 21）
FROM maven:3.9-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:go-offline
COPY src ./src
RUN mvn clean package -DskipTests

FROM eclipse-temurin:21-jre-alpine
COPY --from=build /app/target/*.jar app.jar
# 启用虚拟线程和 ZGC
ENTRYPOINT ["java", "-XX:+UseZGC", "-jar", "app.jar"]
```

## 参考资料

- [Spring Boot 官方文档](https://spring.io/projects/spring-boot)
- [Spring Boot 4.0 Release Notes](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.0-Release-Notes)
- [Spring Boot 3.5 Release Notes](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-3.5-Release-Notes)
- [Spring Cloud 文档](https://spring.io/projects/spring-cloud)
- [微服务最佳实践](https://microservices.io/)


<!-- version-check: Spring Boot 4.0.4, checked 2026-04-22 -->

> 🔄 更新于 2026-04-22

## 8. Spring Boot 4.0.x 补丁版本追踪

### 8.1 版本发布时间线

| 版本 | 发布日期 | 重点 |
|------|---------|------|
| 4.0.0 GA | 2025-11-20 | 首个正式版 |
| 4.0.1 | 2026-01 | Bug 修复 |
| 4.0.2 | 2026-02 | Bug 修复 |
| 4.0.4 | 2026-03-19 | **安全修复**（CVE-2026-22731、CVE-2026-22733） |

### 8.2 CVE-2026-22731 与 CVE-2026-22733

Spring Boot 4.0.4 修复了两个 Actuator 相关的认证绕过漏洞：

- **CVE-2026-22731**：Actuator Health groups 路径下的认证绕过
- **CVE-2026-22733**：Actuator CloudFoundry 端点的认证绕过

**影响范围**：使用 Spring Boot Actuator 且暴露了 Health groups 或 CloudFoundry 端点的应用

**建议**：所有生产环境应立即升级到 4.0.4+

来源：[Spring Boot 4.0.4 发布公告](https://spring.io/blog/2026/03/19/spring-boot-4-0-4-available-now) | [CVE-2026-22733](https://nvd.nist.gov/vuln/detail/CVE-2026-22733)

### 8.3 Spring Boot 3.x EOL 提醒

| 版本 | OSS 支持截止 | 状态 |
|------|-------------|------|
| Spring Boot 3.5.x | 2026-06 | ⚠️ 即将 EOL |
| Spring Boot 4.0.x | 2026-12 | ✅ 当前推荐 |

迁移路径：3.x → 3.5.x → 4.0.x（参考 [Spring Boot 3 EOL 升级指南](https://loiane.com/2026/04/spring-boot-3-eol-to-4-upgrade-playbook-jackson-3/)）

关键迁移注意事项：
- Jackson 2 → Jackson 3（Spring Boot 4.0 默认）
- `javax.*` → `jakarta.*`（如果从 2.x 直接升级）
- RestTemplate → RestClient（推荐）
- OpenFeign → HTTP Interface Client（Spring Cloud 2025.1）

## 9. Spring Boot 4.0.x 补丁版本（持续更新）

> 🔄 更新于 2026-05-07（2026-05-18 增补 May Train 时间表调整）

<!-- version-check: Spring Boot 4.0.6, 4.1.0-RC1, May Train shifted to June 1-5 2026, checked 2026-05-18 -->

### 9.1 最新版本时间线

| 版本 | 发布日期 | 重点 |
|------|---------|------|
| 4.0.4 | 2026-03-19 | **安全修复**（CVE-2026-22731、CVE-2026-22733） |
| 4.0.5 | 2026-03-26 | 17 个 Bug 修复和依赖升级 |
| 4.0.6 | 2026-04-23 | 65 个 Bug 修复、文档改进、依赖升级 |
| 4.1.0-RC1 | 2026-04-23 | 113 项增强、文档改进、依赖升级、Bug 修复 |
| 4.0.7 / 4.1.0 GA（计划） | **2026-06-01 至 06-05** | May Release Train 推迟到 6 月初 |

> 🔄 **2026-05-18 更新**：Spring 团队在 [May Release Train Date Changes](https://spring.io/blog/2026/05/11/may-train-shift) 中宣布，原计划 5 月 11-22 日的整个发布列车（含 **Spring Boot 4.1 GA**）整体推迟到 **6 月 1-5 日**，覆盖 Spring Framework / Boot / Cloud / Security / Data 全部子项目。生产排期预算需要相应顺延 2 周。

来源：[Spring Boot 4.0.5 发布](https://spring.io/blog/2026/03/26/spring-boot-4-0-5-available-now) | [Spring Boot 4.0.6 发布](https://spring.io/blog/2026/04/23/spring-boot-4-0-6-available-now) | [Spring Boot 4.1.0-RC1 发布](https://spring.io/blog/2026/04/23/spring-boot-4-1-0-RC1-available-now/) | [May Train Shift](https://spring.io/blog/2026/05/11/may-train-shift)

### 9.2 Spring 4 月生态同步迭代

2026 年 4 月第三周，Spring 生态多个子项目同步发布首个 RC，为 Spring Boot 4.1 GA 做准备：

```
Spring 4 月 RC 浪潮（2026-04-20 当周）：
├─ Spring Boot 4.1.0-RC1
├─ Spring Security 首个 RC
├─ Spring Integration 首个 RC
├─ Spring Modulith 首个 RC
├─ Spring AMQP 首个 RC
├─ Spring for Apache Kafka 首个 RC
└─ Spring Vault 首个 RC
```

> 这波 RC 意味着 Spring Boot 4.1 GA 预计在 2026 年 5-6 月发布。

来源：[InfoQ: Spring News Roundup Apr 20, 2026](https://www.infoq.com/news/2026/04/spring-news-roundup-apr20-2026/)

### 9.3 生产环境升级建议

- **立即升级**：还在 4.0.3 及以下的 Actuator 应用（CVE-2026-22731/22733）
- **推荐升级到 4.0.6**：合并了 65 个 Bug 修复，是 4.0.x 系列的稳定收敛版
- **评估 4.1.0 RC**：新特性较多，生产环境建议等 GA
- **Java 版本**：4.0.x 要求 Java 17+，4.1.x 可能进一步提升基线（建议 Java 21 或 25）

### 9.4 Spring Boot 4.1 关键新特性预览

> 🔄 更新于 2026-05-18

<!-- version-check: Spring Boot 4.1.0-M3 / 4.1.0-RC1, checked 2026-05-18 -->

Spring Boot 4.1 在 RC1（2026-04-23）之前已经过 M1 / M2 / M3 三个里程碑迭代，核心方向是 **Spring gRPC 内置支持** 和 **可观测性 / 日志能力增强**。

```yaml
# application.yml — Spring Boot 4.1 内置 gRPC 支持
# 不再需要第三方 grpc-spring-boot-starter
spring:
  grpc:
    server:
      port: 9090
      reflection:
        enabled: true   # 开发环境启用 grpcurl 反射调用
    client:
      channels:
        order-service:
          address: "static://localhost:9091"
          negotiation-type: PLAINTEXT
```

**4.1 主要改进**：

- **`spring-boot-starter-grpc`**：Spring gRPC 1.0.x 通过 starter 直接暴露，自动配置 server / client / health probe
- **日志文件轮转**：`logging.file.name` 支持基于大小/时间的滚动配置，无需自带 `logback-spring.xml`
- **HTTP Service Client AOT 友好化**：`@HttpExchange` 接口在原生镜像下的反射注册全部由 AOT 处理
- **Micrometer Tracing 1.6**：默认集成 OTel 1.50+，与 Collector v0.150 的 snake_case 命名对齐

来源：[Spring Boot 4.1.0-M3 Released — gRPC & 日志轮转](https://docs.bswen.com/blog/2026-03-25-spring-boot-4-1-grpc)、[Spring Boot 4.1 Release Notes Wiki](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.1-Release-Notes)

### 9.5 Spring AI 2.0 GA（2026-05-28 计划）

> 🔄 更新于 2026-05-18

<!-- version-check: Spring AI 1.0.6, 1.1.5, 2.0.0-M5 (2026-04-27), 2.0.0 GA scheduled 2026-05-28 -->

Spring AI 团队已确认 **Spring AI 2.0.0 GA 计划于 2026-05-28 发布**，对齐 Spring Boot 4.0 / Spring Framework 7.0 / Jakarta EE 11 基线。来源：[HeroDevs: Spring AI 2.0 Is Coming May 28](https://www.herodevs.com/blog-posts/spring-ai-2-0-is-coming-may-28-here-is-why-that-makes-the-june-30-deadline-more-urgent-not-less)、[Spring AI 1.0.6 / 1.1.5 / 2.0.0-M5 发布说明](https://spring.io/blog/2026/04/27/spring-ai-1-0-6-1-1-5-2-0-0-M5-available-now)

**2.0 重点能力**：

- **JSpecify null-safety**：整个代码库迁移到 JSpecify 注解，与 Spring 6.2+ 一致
- **MCP Boot Starters 一等公民**：`spring-ai-mcp-server-boot-starter` 与 `spring-ai-mcp-client-boot-starter` 直接配套 Spring AI 2.0
- **A2A 协议集成**：基于 Spring AI 1.1.x 已实现的 Agent2Agent Protocol 模块，2.0 中作为标准依赖暴露
- **自定义结构化输出 / 会话历史**：`StructuredOutputConverter` 升级，会话历史可作为 first-class bean 注入

```java
// Spring AI 2.0 风格：MCP + A2A 同时启用
@SpringBootApplication
public class AiApp {
    public static void main(String[] args) {
        SpringApplication.run(AiApp.class, args);
    }
}
```

```yaml
# application.yml
spring:
  ai:
    mcp:
      client:
        servers:
          - id: filesystem
            transport: stdio
            command: "uvx mcp-server-filesystem"
    a2a:
      enabled: true
      base-url: "https://my-agent.example.com"
      capabilities:
        - "research"
        - "summarization"
```

**升级时机**：

| 场景 | 建议 |
|------|------|
| 新项目（2026-Q3 上线） | 等 2.0 GA（5-28），与 Spring Boot 4.1 GA（6-1 至 6-5）配套 |
| 已在 1.0.x | 先升级到 1.0.6（最新补丁），等 2.0 稳定 1-2 个月后再迁 |
| 已在 1.1.x | 1.1.5 是当前推荐稳定线，可作为 2.0 之前的过渡版本 |
| 重度依赖 MCP / A2A | 直接基于 2.0.0-M5 验证，GA 后无 Breaking 切换 |
