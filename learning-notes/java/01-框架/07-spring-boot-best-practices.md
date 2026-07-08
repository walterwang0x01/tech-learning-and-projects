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

<!-- version-check: Spring Boot 4.1.0, Spring Framework 7.0.8, checked 2026-07-08 -->

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
│            Spring Boot 版本选择指南（2026-07）        │
├─────────────────────────────────────────────────────┤
│                                                     │
│  新项目（2026 年下半年）                             │
│  ├── 推荐 → Spring Boot 4.1.x + Java 21            │
│  └── 保守 → Spring Boot 4.0.7 + Java 21            │
│                                                     │
│  现有项目迁移路径                                    │
│  ├── 2.x → 3.5.16（最终补丁）→ 4.0.7 → 4.1.0       │
│  └── 3.x → 4.0.7 → 4.1.0                           │
│                                                     │
│  ⚠️ Spring Boot 3.5 OSS 支持已于 2026-06-30 结束   │
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


<!-- 历史 version-check 已合并至第 9 节，见 9.1 -->

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

> 🔄 更新于 2026-07-08

| 版本 | OSS 支持截止 | 状态 |
|------|-------------|------|
| Spring Boot 3.5.x | **2026-06-30** | ❌ OSS 已结束（最终补丁 3.5.16，2026-06-25） |
| Spring Boot 4.0.x | 2026-12 | ✅ 维护中（最新 4.0.7） |
| Spring Boot 4.1.x | ~2027-07 | ✅ **当前推荐**（4.1.0 GA，2026-06-10） |

迁移路径：3.x → 3.5.16（最终补丁）→ 4.0.7 → 4.1.0（参考 [Spring Boot 3 EOL 升级指南](https://loiane.com/2026/04/spring-boot-3-eol-to-4-upgrade-playbook-jackson-3/)）

来源：[HeroDevs: Spring Boot Versions July 2026](https://www.herodevs.com/blog-posts/spring-boot-versions-eol-dates-and-latest-releases-april-2026)

关键迁移注意事项：
- Jackson 2 → Jackson 3（Spring Boot 4.0 默认）
- `javax.*` → `jakarta.*`（如果从 2.x 直接升级）
- RestTemplate → RestClient（推荐）
- OpenFeign → HTTP Interface Client（Spring Cloud 2025.1）

## 9. Spring Boot 4.0.x / 4.1.x 版本追踪（持续更新）

> 🔄 更新于 2026-07-08

<!-- version-check: Spring Boot 4.0.7, 4.1.0, Spring Framework 7.0.8, checked 2026-07-08 -->

### 9.1 最新版本时间线

| 版本 | 发布日期 | 重点 |
|------|---------|------|
| 4.0.6 | 2026-04-23 | 65 个 Bug 修复、文档改进、依赖升级 |
| 4.1.0-RC1 | 2026-04-23 | 113 项增强、文档改进、依赖升级、Bug 修复 |
| **4.0.7 / 4.1.0 GA** | **2026-06-10** | June Release Train 落地；4.1 基于 Spring Framework 7.0.8 |
| 3.5.16（最终补丁） | 2026-06-25 | 3.x 线最后一个 OSS 补丁 |
| 4.1.1（预期） | 2026-11（约） | 按半年节奏，下一 minor 为 4.2 |

> **2026-07 状态**：4.1.0 是当前稳定版，4.1.1 尚未发布。仍在 4.0.x 的团队应升级到 **4.0.7**；新项目直接上 **4.1.0**。

来源：[Spring Boot 4.1.0 Release](https://github.com/spring-projects/spring-boot/releases/tag/v4.1.0) | [Spring Boot 4.0.6 发布](https://spring.io/blog/2026/04/23/spring-boot-4-0-6-available-now) | [InfoQ: Spring Boot 4.1](https://www.infoq.com/news/2026/06/spring-boot-4-1/) | [HeroDevs July 2026](https://www.herodevs.com/blog-posts/spring-boot-versions-eol-dates-and-latest-releases-april-2026)

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
- **4.0.x 维护线**：升级到 **4.0.7**（2026-06-10 发布）
- **新项目 / 主动升级**：直接上 **4.1.0**（gRPC 自动配置、HTTP 客户端 SSRF 缓解、懒加载数据源、@Async 上下文传播）
- **Java 版本**：4.0.x / 4.1.x 最低 Java 17；4.1 支持 Java 17–26，jOOQ 3.20 需 Java 21
- **3.x 遗留系统**：3.5.16 是最终 OSS 补丁，须规划向 4.x 迁移

### 9.4 Spring Boot 4.1 关键新特性（GA）

> 🔄 更新于 2026-07-08

<!-- version-check: Spring Boot 4.1.0 GA, Spring gRPC 1.1.0, checked 2026-07-08 -->

Spring Boot 4.1.0 已于 **2026-06-10** GA，基于 Spring Framework 7.0.8，核心方向是 **Spring gRPC 一等公民**、**出站 HTTP SSRF 缓解** 和 **可观测性增强**。

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

- **`spring-boot-starter-grpc`**：内置 Spring gRPC **1.1.0**，支持 Netty / Servlet HTTP/2、`@GrpcAdvice` 统一异常处理
- **HTTP 客户端 SSRF 缓解**：出站 HTTP 调用增加服务端请求伪造防护
- **懒加载数据源连接**：减少启动期数据库连接压力
- **@Async 异步上下文传播**：可观测性与安全上下文可跨异步边界传递
- **Kotlin 2.3 + Kotlin Serialization 1.11**：Kotlin 项目同步升级
- **日志文件轮转**：`logging.file.name` 支持基于大小/时间的滚动配置
- **OpenTelemetry 增强**：trace / metrics / logs 集成改进

来源：[Spring Boot 4.1 Release Notes Wiki](https://github.com/spring-projects/spring-boot/wiki/Spring-Boot-4.1-Release-Notes) | [InfoQ: Spring Boot 4.1](https://www.infoq.com/news/2026/06/spring-boot-4-1/)

### 9.5 Spring AI 2.0.0 GA（2026-06-12）

> 🔄 更新于 2026-07-08

<!-- version-check: Spring AI 2.0.0, 1.1.8, 1.0.9, MCP SDK 2.0.0, checked 2026-07-08 -->

**Spring AI 2.0.0** 已于 **2026-06-12** 发布至 Maven Central，基线为 **Spring Boot 4.0 / 4.1 + Spring Framework 7.0 + Jackson 3**。同日发布的 **1.1.8 / 1.0.9** 面向仍停留在 Boot 3.5.x 的维护线（含 CVE-2026-47835 安全修复）。来源：[Spring AI 2.0.0 GA](https://spring.io/blog/2026/06/12/spring-ai-2-0-0-GA-available-now) | [Spring AI 1.1.8 / 1.0.9](https://spring.io/blog/2026/06/12/spring-ai-1-1-8-1-0-9-avaialble-now) | [Upgrade Notes](https://docs.spring.io/spring-ai/reference/upgrade-notes.html)

**2.0 架构级变化**：

| 领域 | 变化 |
|------|------|
| **工具调用** | `ToolCallingAdvisor` 提升到 Advisor 链一等公民，各 ChatModel 内嵌 loop 已移除 |
| **结构化输出** | `StructuredOutputValidationAdvisor` 校验失败时自动自纠正 |
| **大规模工具** | `ToolSearchToolCallingAdvisor` 支持渐进式工具披露（数百工具场景） |
| **MCP** | MCP Java SDK **2.0.0**；`@McpTool` / `@McpResource` / `@McpPrompt` 注解驱动；**Streamable HTTP** 为默认传输 |
| **空安全** | 全库 JSpecify 注解；Options 改为不可变 Builder 模式 |
| **模型集成** | OpenAI / Anthropic / Google GenAI 各收敛为单一官方 SDK 实现 |

```java
// Spring AI 2.0：ChatClient + ToolCallingAdvisor（自动注册）
@Configuration
public class AiConfig {
    @Bean
    CommandLineRunner demo(ChatClient.Builder builder) {
        return args -> {
            ChatClient client = builder
                .defaultSystem("You are a helpful assistant.")
                .build();
            String answer = client.prompt("What is Spring AI 2.0?")
                .call()
                .content();
            System.out.println(answer);
        };
    }
}
```

```yaml
# application.yml — MCP Streamable HTTP（生产默认传输）
spring:
  ai:
    mcp:
      server:
        enabled: true
        protocol: STREAMABLE   # 替代已废弃的 SSE
      client:
        streamable-http:
          connections:
            filesystem:
              url: http://mcp-server:8080/mcp
```

**版本线选择（2026-07）**：

| 场景 | 建议 |
|------|------|
| 新项目 + Boot 4.1 | **Spring AI 2.0.0** + Boot 4.1.0 |
| 仍在 Boot 3.5.x | **Spring AI 1.1.8**（最终维护线，Boot 3.5.15） |
| 从 1.x 迁移到 2.0 | 先读 [Upgrade Notes](https://docs.spring.io/spring-ai/reference/upgrade-notes.html)，重点检查 MCP SDK 2.0 Breaking Changes |
| 会话记忆 | 2.0 内置 `ChatMemory`；长期方案关注社区项目 `spring-ai-session`（计划 2.1 纳入核心） |

### 9.6 Spring AI 2.1 路线图（Spring I/O 2026）

> 🔄 更新于 2026-07-08

Spring I/O 2026 Keynote 公布了 **Spring AI 2.1**（目标 **2026-11**）方向，核心是从 ChatClient 工具层向 **Agent 一等抽象** 演进：

- **`spring-ai-agent` 模块**：高层 Agent 注解与编程模型，支持有状态工作流编排
- **Session API 毕业**：`spring-ai-session` 社区项目的会话感知记忆将纳入核心（替代现有 `ChatMemory`）
- **Stateful AI API**：除 Completion API 外，增加 Response / Interaction 等有状态 API 集成
- **工作流引擎集成**：初步对接 Temporal、Dapr 等成熟编排引擎
- **统一流式 API**：结合 Spring Framework 虚拟线程，统一 imperative / reactive 编程模型

> 2.1 目前无 Milestone 发布；生产环境仍以 **2.0.0 GA** 为准，Agent 复杂编排可先用 `spring-ai-agent-utils` 社区扩展验证。

来源：[Spring I/O 2026 Keynote](https://www.youtube.com/watch?v=pYDMhBVspIY) | [Agents Capability Roadmap Discussion #5965](https://github.com/spring-projects/spring-ai/discussions/5965)
