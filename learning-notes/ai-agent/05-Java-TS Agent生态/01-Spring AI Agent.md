# Spring AI Agent
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

<!-- version-check: Spring AI 2.0.0 GA (实际发布 2026-06-12，非计划的 05-28), Spring Boot 4.1.0, MCP SDK 2.0.0, checked 2026-07-10 -->
<!-- 修复于 2026-07-09: 2.0.0-M8 → 2.0.0 GA（与 java/01-框架 对齐） -->
<!-- 修复于 2026-07-10: GA 实际日期纠偏 05-28 → 06-12 -->

> 🔄 更新于 2026-04-18

Spring AI 是 Spring 生态的 AI 框架，为 Java/Kotlin 开发者提供统一的 AI 模型接口、工具调用、RAG、MCP 客户端等能力。

最新版本：
- **Spring AI 2.0.0-M4**（2026-03-26）— 19 项改进、29 个 Bug 修复、3 个安全升级
- **Spring AI 1.1.4**（2026-03-26）— 稳定版维护更新
- **MCP Streamable HTTP**：替代 SSE 传输，支持 MCP Server Boot Starter
- **Bedrock AgentCore SDK GA**：Spring AI SDK for Amazon Bedrock AgentCore 正式可用

> 来源：[Spring AI 2.0.0-M4 发布公告](https://spring.io/blog/2026/03/26/spring-ai-2-0-0-M4-and-1-1-4-and-1-0-5-available)、[AWS Bedrock AgentCore GA](https://aws.amazon.com/blogs/machine-learning/spring-ai-sdk-for-amazon-bedrock-agentcore-is-now-generally-available/)

> 🔄 更新于 2026-05-22

### 1.1 Spring AI 2.0 GA 路线图

| 里程碑 | 时间 | 重点变更 |
|-------|------|---------|
| 2.0.0-M5 | 2026-04-27 | 5 处 Bug 修复、4 处文档更新、2 项依赖升级、3 项构建更新 |
| **2.0.0-M6** | **2026-05-08** | **Breaking Change：Chat Memory Advisor 必须显式传入 conversation ID**（不再使用隐式默认值）；同步发布 1.1.6 / 1.0.7 维护版本 |
| 2.0.0-M7 | 2026-05-23 | MCP Streamable HTTP 成为默认服务端协议，SSE 传输被标记 deprecated；同步 1.1.7 / 1.0.8 |
| 2.0.0-M8 | 2026-05-27 | GA 候选版本，团队明确表示后续将基于该版本继续构建增强能力 |
| 2.0.0 GA | **2026-05-28**（计划，可能微调） | 配合 Spring Boot 4.1（6 月初发布）一起上线 |

> 🔄 更新于 2026-05-28
>
> M7/M8 在 GA 节点前一周内连续发布两个里程碑，反映了 GA 计划可能从 5-28 微调至 5 月底或 6 月初。版本号锁定建议：生产环境暂时锁定 **1.1.7**（与 Spring Boot 3.5.x 兼容）等待 2.0 GA 公告，避免直接拉取 2.0.0-M8 进入生产。

**关键 Breaking Change（M6）**：

```java
// ❌ 旧写法（M5 及以前）：会使用隐式默认 conversation ID，可能导致跨会话记忆串号
ChatClient.builder(chatModel)
    .defaultAdvisors(new MessageChatMemoryAdvisor(chatMemory))
    .build();

// ✅ 新写法（M6 起）：必须显式传入 conversation ID
ChatClient.builder(chatModel)
    .defaultAdvisors(MessageChatMemoryAdvisor.builder(chatMemory)
        .conversationId(userSessionId)  // 必填
        .build())
    .build();
```

**升级注意事项**：

- Spring AI 2.0 要求 **Spring Boot 4.0+**，3.x 项目需先完成 Boot 4.0 迁移（Jakarta EE 11、Java 17+）
- 若仍在 Spring Boot 3.x，可继续使用 Spring AI **1.1.x**（2026 年内仍维护，与 Boot 3.5 兼容）
- 1.0.x 进入 LTS 维护，仅修 critical 缺陷
- **MCP 传输层变化（M7 起）**：Streamable HTTP 成为默认服务端协议，SSE 传输被标记 deprecated。新项目应直接使用 Streamable HTTP；老项目保留 SSE 至少到 1.1.x EOL

来源：[Spring AI 2.0.0-M6 发布公告](https://spring.io/blog/2026/05/08/spring-ai-1-0-7-1-1-6-2-0-0-M6-available-now)、[Spring AI 2.0.0-M7 发布公告](https://spring.io/blog/2026/05/23/spring-ai-1-0-8-1-1-7-2-0-0-M7-available-now)、[Spring AI 2.0.0-M8 发布公告](https://spring.io/blog/2026/05/27/spring-ai-2-0-0-M8-available-now)、[HeroDevs - Spring AI 2.0 GA Schedule](https://www.herodevs.com/blog-posts/spring-ai-2-0-is-coming-may-28-here-is-why-that-makes-the-june-30-deadline-more-urgent-not-less)

### 1.2 GA 日期纠偏 + Composable Tool Calling 架构（2026-07-10 更新）

> 更新于 2026-07-10

<!-- version-check: Spring AI 2.0.0 GA 实际发布于 2026-06-12（非此前预计的 05-28）, MCP SDK 2.0.0, checked 2026-07-10 -->

**日期纠偏**：**Spring AI 2.0.0 实际 GA 日期是 2026-06-12**，比 M8 阶段预计的 "2026-05-28" 晚了约两周（[Spring AI 2.0.0 GA Available Now](https://spring.io/blog/2026/06/12/spring-ai-2-0-0-GA-available-now/)）。GA 版本确认基线为 **Spring Boot 4.0/4.1 + Spring Framework 7.0**，硬性要求 Java 17+，仍在 Spring Boot 3.x 的团队必须先完成 Boot 4 迁移才能使用 2.0。

**GA 版本的关键结构性变化**（超出 M6-M8 milestone 已记录的内容）：

- **JSON 迁移到 Jackson 3**：新增 `JsonHelper` 类用于自定义序列化行为
- **JSpecify null-safety 注解**全面覆盖代码库，配合 IDE/静态分析在编译期捕获可选值 vs 必填值的错误
- **Composable Tool Calling 架构**：工具执行逻辑从各个 ChatModel 内部抽出，成为独立的 **`ToolCallingAdvisor`**。循环机制：收集 `@Tool` 注解方法 / `java.util.Function` 实现 / `ToolCallback` bean → 把完整对话历史发给 LLM → 通过 `ToolCallingManager` 执行模型请求的工具 → 结果追加进对话历史 → 重新进入循环。阻塞式 `.call()` 和流式 `.stream()` 均完整支持，也为需要审批网关（human-in-the-loop）的场景提供了介入点
- **MCP Java SDK 升级到 2.0.0**，新增 `@McpTool`、`@McpResource`、`@McpPrompt` 注解驱动的 Server 开发方式；Streamable HTTP 保持默认传输（与 M7 一致）

```java
// GA 版本：ToolCallingAdvisor 作为独立组件注入，而非绑定在具体 ChatModel 内部
ChatClient.builder(chatModel)
    .defaultAdvisors(
        ToolCallingAdvisor.builder()
            .toolCallingManager(toolCallingManager)
            .build(),
        MessageChatMemoryAdvisor.builder(chatMemory)
            .conversationId(userSessionId)
            .build())
    .build();
```

来源：[Spring AI 2.0.0 GA Available Now](https://spring.io/blog/2026/06/12/spring-ai-2-0-0-GA-available-now/)、[JavaRubberDuck: Spring AI 2.0 GA and Composable Tool Calling](https://javarubberduck.com/java/news-2026-06-29-spring/)

```
┌─────────────────────────────────────────────┐
│            Spring Boot 应用                   │
├─────────────────────────────────────────────┤
│              Spring AI                       │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │ChatClient│ │Tool Call │ │RAG         │  │
│  │统一对话   │ │工具调用   │ │检索增强     │  │
│  └──────────┘ └──────────┘ └────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │Advisor   │ │MCP Client│ │VectorStore │  │
│  │中间件     │ │MCP 客户端│ │向量存储     │  │
│  └──────────┘ └──────────┘ └────────────┘  │
├──────┬──────┬──────┬──────┬────────────────┤
│OpenAI│Claude│Gemini│Ollama│ Bedrock 等     │
└──────┴──────┴──────┴──────┴────────────────┘
```

## 2. 快速开始

```xml
<!-- pom.xml -->
<dependency>
    <groupId>org.springframework.ai</groupId>
    <artifactId>spring-ai-openai-spring-boot-starter</artifactId>
</dependency>
```

```yaml
# application.yml
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
      chat:
        options:
          model: gpt-4o
          temperature: 0.7
```

```java
@RestController
public class ChatController {

    private final ChatClient chatClient;

    public ChatController(ChatClient.Builder builder) {
        this.chatClient = builder
            .defaultSystem("你是一个友好的 AI 助手")
            .build();
    }

    @GetMapping("/chat")
    public String chat(@RequestParam String message) {
        return chatClient.prompt()
            .user(message)
            .call()
            .content();
    }

    // 流式响应
    @GetMapping(value = "/stream", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
    public Flux<String> stream(@RequestParam String message) {
        return chatClient.prompt()
            .user(message)
            .stream()
            .content();
    }
}
```

## 3. 工具调用（Function Calling）

```java
// 定义工具
@Component
public class WeatherTools {

    @Tool(description = "获取指定城市的天气信息")
    public WeatherInfo getWeather(@ToolParam(description = "城市名称") String city) {
        // 调用天气 API
        return new WeatherInfo(city, 28, "晴");
    }

    @Tool(description = "获取城市的空气质量指数")
    public AqiInfo getAqi(@ToolParam(description = "城市名称") String city) {
        return new AqiInfo(city, 45, "优");
    }

    record WeatherInfo(String city, int temperature, String condition) {}
    record AqiInfo(String city, int aqi, String level) {}
}

// 在 ChatClient 中使用工具
@RestController
public class AgentController {

    private final ChatClient chatClient;

    public AgentController(ChatClient.Builder builder, WeatherTools weatherTools) {
        this.chatClient = builder
            .defaultSystem("你是天气助手，使用工具查询天气信息")
            .defaultTools(weatherTools)  // 注册工具
            .build();
    }

    @GetMapping("/agent")
    public String agent(@RequestParam String query) {
        return chatClient.prompt()
            .user(query)
            .call()
            .content();
        // 模型自动决定是否调用工具
    }
}
```

## 4. Advisor 模式（中间件）

```java
// Advisor = AI 调用的中间件，类似 Spring MVC 的 Interceptor
@Component
public class LoggingAdvisor implements CallAroundAdvisor {

    @Override
    public AdvisedResponse aroundCall(AdvisedRequest request, CallAroundAdvisorChain chain) {
        // 请求前
        long start = System.currentTimeMillis();
        log.info("AI 请求: {}", request.userText());

        // 执行调用
        AdvisedResponse response = chain.nextAroundCall(request);

        // 请求后
        long duration = System.currentTimeMillis() - start;
        log.info("AI 响应: {} ({}ms)", response.response().getResult().getOutput().getText(), duration);

        return response;
    }

    @Override
    public int getOrder() { return 0; }
}

// 使用 Advisor
ChatClient chatClient = builder
    .defaultAdvisors(
        new LoggingAdvisor(),
        new MessageChatMemoryAdvisor(chatMemory),  // 内置记忆 Advisor
        new SafeGuardAdvisor("不要讨论政治话题")     // 护栏 Advisor
    )
    .build();
```

## 5. RAG 实现

```java
@Configuration
public class RagConfig {

    @Bean
    public VectorStore vectorStore(EmbeddingModel embeddingModel) {
        return new PgVectorStore(jdbcTemplate, embeddingModel);
    }
}

@Service
public class RagService {

    private final ChatClient chatClient;
    private final VectorStore vectorStore;

    public RagService(ChatClient.Builder builder, VectorStore vectorStore) {
        this.vectorStore = vectorStore;
        this.chatClient = builder
            .defaultAdvisors(
                new QuestionAnswerAdvisor(vectorStore, SearchRequest.builder()
                    .similarityThreshold(0.7)
                    .topK(5)
                    .build())
            )
            .build();
    }

    // 文档导入
    public void ingestDocuments(List<Document> documents) {
        vectorStore.add(documents);
    }

    // RAG 查询
    public String query(String question) {
        return chatClient.prompt()
            .user(question)
            .call()
            .content();
    }
}
```

## 6. MCP 客户端

```yaml
# application.yml
spring:
  ai:
    mcp:
      client:
        stdio:
          servers:
            filesystem:
              command: npx
              args: ["-y", "@modelcontextprotocol/server-filesystem", "/workspace"]
            github:
              command: npx
              args: ["-y", "@modelcontextprotocol/server-github"]
              env:
                GITHUB_TOKEN: ${GITHUB_TOKEN}
```

```java
@RestController
public class McpAgentController {

    private final ChatClient chatClient;

    public McpAgentController(ChatClient.Builder builder, ToolCallbackProvider mcpTools) {
        this.chatClient = builder
            .defaultSystem("你是开发助手，可以操作文件系统和 GitHub")
            .defaultTools(mcpTools)  // MCP 工具自动注册
            .build();
    }

    @GetMapping("/mcp-agent")
    public String mcpAgent(@RequestParam String task) {
        return chatClient.prompt()
            .user(task)
            .call()
            .content();
    }
}
```

## 7. 结构化输出

```java
// 定义输出结构
record CodeReview(
    int score,
    List<Issue> issues,
    String summary
) {
    record Issue(String severity, int line, String description) {}
}

@GetMapping("/review")
public CodeReview reviewCode(@RequestParam String code) {
    return chatClient.prompt()
        .user("审查以下代码：\n" + code)
        .call()
        .entity(CodeReview.class);  // 自动解析为 Java 对象
}
```

## 8. 实现 Anthropic Agent 模式

```java
// Evaluator-Optimizer 模式
@Service
public class EvalOptimizeAgent {

    private final ChatClient chatClient;

    public String generate(String task, int maxIterations) {
        String output = chatClient.prompt()
            .user("完成任务：" + task)
            .call().content();

        for (int i = 0; i < maxIterations; i++) {
            // 评估
            EvalResult eval = chatClient.prompt()
                .user("评估输出质量(1-10)并给建议：\n" + output)
                .call()
                .entity(EvalResult.class);

            if (eval.score() >= 8) break;

            // 优化
            output = chatClient.prompt()
                .user("改进输出：\n原文：" + output + "\n建议：" + eval.feedback())
                .call().content();
        }
        return output;
    }

    record EvalResult(int score, String feedback) {}
}
```

## 9. 多模型切换

```yaml
# application.yml — 配置多个模型
spring:
  ai:
    openai:
      api-key: ${OPENAI_API_KEY}
    anthropic:
      api-key: ${ANTHROPIC_API_KEY}
    ollama:
      base-url: http://localhost:11434
```

```java
@Service
public class MultiModelService {

    @Qualifier("openAiChatModel")
    private final ChatModel openai;

    @Qualifier("anthropicChatModel")
    private final ChatModel claude;

    public String routeByComplexity(String query, String complexity) {
        ChatModel model = switch (complexity) {
            case "high" -> openai;    // 复杂任务用 GPT-4o
            case "low" -> claude;     // 简单任务用 Claude Haiku
            default -> openai;
        };

        return ChatClient.create(model).prompt()
            .user(query)
            .call()
            .content();
    }
}
```
## 🎬 推荐视频资源

### 🌐 YouTube
- [Spring - Spring AI Introduction](https://www.youtube.com/watch?v=9SGDpanrc8U) — Spring AI官方介绍
- [Dan Vega - Spring AI Tutorial](https://www.youtube.com/watch?v=pHksBVqH7uI) — Spring AI实战教程

### 📺 B站
- [Spring AI中文教程](https://www.bilibili.com/video/BV1Es4y1q7Bf) — Spring AI中文实战

### 📖 官方文档
- [Spring AI Docs](https://docs.spring.io/spring-ai/reference/) — Spring AI官方文档
- [Baeldung - Spring AI](https://www.baeldung.com/spring-ai) — Spring AI教程
