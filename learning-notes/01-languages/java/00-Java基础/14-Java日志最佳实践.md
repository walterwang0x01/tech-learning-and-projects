# Java 日志最佳实践
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 日志框架演进

| 框架 | 特点 | 推荐度 |
|------|------|--------|
| JUL | JDK 自带，API 笨拙 | ⭐ |
| Log4j 1.x | 已 EOL，有安全漏洞 | ❌ |
| Logback | SLF4J 原生实现，Spring Boot 默认 | ⭐⭐⭐⭐ |
| Log4j2 | 异步性能最强，支持 Lambda 延迟求值 | ⭐⭐⭐⭐⭐ |

## 2. SLF4J 门面模式

```java
// 应用代码只依赖 SLF4J API，底层实现可替换（Logback / Log4j2）
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

public class UserService {
    private static final Logger log = LoggerFactory.getLogger(UserService.class);

    public User findById(Long id) {
        log.debug("查询用户: id={}", id);
        return userRepo.findById(id).orElseThrow();
    }
}
```

## 3. Logback 配置

```xml
<!-- logback-spring.xml -->
<configuration>
    <appender name="CONSOLE" class="ch.qos.logback.core.ConsoleAppender">
        <encoder><pattern>%d{HH:mm:ss.SSS} [%thread] %-5level %logger{36} - %msg%n</pattern></encoder>
    </appender>
    <appender name="FILE" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>logs/app.log</file>
        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <fileNamePattern>logs/app.%d{yyyy-MM-dd}.%i.log.gz</fileNamePattern>
            <maxFileSize>100MB</maxFileSize>
            <maxHistory>30</maxHistory>
            <totalSizeCap>3GB</totalSizeCap>
        </rollingPolicy>
    </appender>
    <!-- 异步 Appender：提升吞吐量 -->
    <appender name="ASYNC" class="ch.qos.logback.classic.AsyncAppender">
        <queueSize>1024</queueSize>
        <appender-ref ref="FILE"/>
    </appender>
    <root level="INFO">
        <appender-ref ref="CONSOLE"/>
        <appender-ref ref="ASYNC"/>
    </root>
</configuration>
```

## 4. Log4j2 配置对比

```xml
<!-- log4j2-spring.xml：原生异步性能优于 Logback -->
<Configuration>
    <Appenders>
        <RollingRandomAccessFile name="File" fileName="logs/app.log"
            filePattern="logs/app-%d{yyyy-MM-dd}-%i.log.gz">
            <PatternLayout pattern="%d [%t] %-5level %logger{36} - %msg%n"/>
            <Policies><SizeBasedTriggeringPolicy size="100MB"/></Policies>
        </RollingRandomAccessFile>
    </Appenders>
    <!-- 全局异步：-Dlog4j2.contextSelector=org.apache.logging.log4j.core.async.AsyncLoggerContextSelector -->
    <Loggers><Root level="info"><AppenderRef ref="File"/></Root></Loggers>
</Configuration>
```

## 5. 结构化日志（JSON）

```xml
<!-- logstash-logback-encoder：JSON 输出，便于 ELK 采集 -->
<appender name="JSON" class="ch.qos.logback.core.rolling.RollingFileAppender">
    <encoder class="net.logstash.logback.encoder.LogstashEncoder">
        <customFields>{"service":"user-service","env":"prod"}</customFields>
    </encoder>
</appender>
<!-- 输出: {"@timestamp":"2024-01-15T10:30:00","level":"INFO","message":"用户登录","traceId":"abc123"} -->
```

## 6. MDC 链路追踪

```java
import org.slf4j.MDC;

@Component
public class TraceFilter implements Filter {
    @Override
    public void doFilter(ServletRequest req, ServletResponse res, FilterChain chain)
            throws IOException, ServletException {
        try {
            MDC.put("traceId", UUID.randomUUID().toString().replace("-", ""));
            MDC.put("userId", getCurrentUserId());
            chain.doFilter(req, res);
        } finally {
            MDC.clear(); // 必须清理，防止线程池复用导致数据污染
        }
    }
}
// logback pattern 引用: %d [%X{traceId}] [%X{userId}] %-5level %logger{36} - %msg%n
```

## 7. Spring Boot 日志配置

```yaml
logging:
  level:
    root: INFO
    com.example.app: DEBUG
    org.springframework.web: WARN
    org.hibernate.SQL: DEBUG
  file:
    name: logs/app.log
  logback:
    rollingpolicy:
      max-file-size: 100MB
      max-history: 30
```

## 8. 日志级别使用规范

| 级别 | 场景 | 示例 |
|------|------|------|
| TRACE | 方法入参出参 | `log.trace("enter method, args={}", args)` |
| DEBUG | 开发调试 | `log.debug("查询到 {} 条记录", list.size())` |
| INFO | 关键业务流程 | `log.info("用户 {} 下单成功, orderId={}", userId, orderId)` |
| WARN | 可恢复异常、降级 | `log.warn("缓存未命中，回源数据库: key={}", key)` |
| ERROR | 不可恢复错误 | `log.error("支付回调失败, orderId={}", orderId, e)` |

## 9. 性能优化与脱敏

```java
// ✅ 参数化日志：不会提前拼接字符串
log.debug("用户 {} 查询订单 {}", userId, orderId);
// ❌ 字符串拼接：即使 debug 关闭也会执行拼接
log.debug("用户 " + userId + " 查询订单 " + orderId);
// ✅ 昂贵操作用 isEnabled 守卫
if (log.isDebugEnabled()) { log.debug("对象: {}", expensiveToString(obj)); }
// ✅ Log4j2 Lambda 延迟求值
log.debug("结果: {}", () -> expensiveComputation());

// 敏感信息脱敏
public static String maskPhone(String phone) {
    return phone.substring(0, 3) + "****" + phone.substring(7); // 138****5678
}
log.info("手机: {}", maskPhone(phone));
```

## 10. 常见反模式

```java
// ❌ catch 里吞掉异常
try { riskyOp(); } catch (Exception e) { /* 空 */ }
// ❌ 只打 message 不打堆栈
log.error("失败: " + e.getMessage());
// ✅ 异常对象作为最后一个参数（自动打印堆栈）
log.error("操作失败, orderId={}", orderId, e);
// ❌ 循环里打大量日志
for (Item item : items) { log.info("处理: {}", item); }
// ✅ 汇总
log.info("批量处理完成, total={}, success={}, fail={}", total, success, fail);
// ❌ ERROR 级别滥用
log.error("用户输入参数错误"); // 应该用 WARN
```
