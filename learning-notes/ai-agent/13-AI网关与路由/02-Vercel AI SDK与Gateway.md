# Vercel AI SDK 与 Gateway
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

> 🔄 更新于 2026-05-13
>
> **AI SDK 6**（2026-06 发布）：Vercel AI SDK 当前最新大版本，20M+ 月下载量。核心变化：Server Actions 替代 API Routes（`useChat` 直连 Server Action，无需 `/api/chat` 端点）；`StreamingTextResponse` 移除，改用 `toDataStreamResponse`/`toDataStream`；统一 `LanguageModelV1` 接口；原生 Zod 4 集成；Provider 包重构为独立 tree-shakeable 包。v5 API Routes 模式仍兼容（过渡期支持）。
> 来源：[Vercel Blog - AI SDK 6](https://vercel.com/blog/ai-sdk-6)

<!-- version-check: Vercel AI SDK 6.x, @ai-sdk/openai 2.0.x, checked 2026-05-13 -->

Vercel AI SDK 是 TypeScript 生态的 AI 开发工具包，提供统一的模型接口、流式响应、工具调用等能力。AI Gateway 提供集中式模型路由和管理。

```
┌─────────────────────────────────────────────┐
│           Next.js / React 应用               │
├─────────────────────────────────────────────┤
│              Vercel AI SDK                   │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │generateText│ │streamText│ │Tool Calling│  │
│  │结构化输出  │ │流式响应   │ │工具调用     │  │
│  └──────────┘ └──────────┘ └────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │useChat   │ │useObject │ │AI Gateway  │  │
│  │React Hook│ │结构化Hook│ │模型路由     │  │
│  └──────────┘ └──────────┘ └────────────┘  │
├──────┬──────┬──────┬──────┬────────────────┤
│OpenAI│Claude│Gemini│Llama │ 更多 Provider   │
└──────┴──────┴──────┴──────┴────────────────┘
```

## 2. 基础用法

```bash
npm install ai @ai-sdk/openai @ai-sdk/anthropic
```

```typescript
import { generateText, streamText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { anthropic } from '@ai-sdk/anthropic';

// 生成文本（非流式）
const { text } = await generateText({
  model: openai('gpt-5.2'),
  prompt: '解释什么是 AI Agent',
});

// 切换模型只需改一行
const { text: claudeText } = await generateText({
  model: anthropic('claude-sonnet-4-6-20260217'),
  prompt: '解释什么是 AI Agent',
});

// 流式输出
const result = streamText({
  model: openai('gpt-5.2'),
  prompt: '写一篇关于 AI Agent 的文章',
});

for await (const chunk of result.textStream) {
  process.stdout.write(chunk);
}
```

## 3. 工具调用（Function Calling）

```typescript
import { generateText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

const result = await generateText({
  model: openai('gpt-5.2'),
  prompt: '北京今天天气怎么样？',
  tools: {
    getWeather: tool({
      description: '获取城市天气',
      parameters: z.object({
        city: z.string().describe('城市名称'),
      }),
      execute: async ({ city }) => {
        // 实际调用天气 API
        return { city, temp: 28, condition: '晴' };
      },
    }),
    searchWeb: tool({
      description: '搜索互联网',
      parameters: z.object({
        query: z.string().describe('搜索关键词'),
      }),
      execute: async ({ query }) => {
        return { results: [`${query} 的搜索结果...`] };
      },
    }),
  },
  maxSteps: 5, // 允许多步工具调用
});

console.log(result.text);
console.log(result.steps); // 查看每一步的工具调用
```

## 4. Agent 循环模式

```typescript
import { generateText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

// maxSteps 实现 Agent 循环
const { text, steps } = await generateText({
  model: openai('gpt-5.2'),
  system: `你是研究助手。使用工具收集信息，然后综合回答。`,
  prompt: '对比 LangGraph 和 CrewAI 的优缺点',
  tools: {
    search: tool({
      description: '搜索技术文档和博客',
      parameters: z.object({ query: z.string() }),
      execute: async ({ query }) => `搜索结果: ${query}...`,
    }),
    readUrl: tool({
      description: '读取网页内容',
      parameters: z.object({ url: z.string() }),
      execute: async ({ url }) => `页面内容: ${url}...`,
    }),
  },
  maxSteps: 10,  // Agent 最多执行 10 步
  // 模型自动决定何时停止调用工具
});

console.log(`Agent 执行了 ${steps.length} 步`);
console.log(text);
```

## 5. 结构化输出

```typescript
import { generateObject } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

// 生成结构化数据
const { object } = await generateObject({
  model: openai('gpt-5.2'),
  schema: z.object({
    frameworks: z.array(z.object({
      name: z.string(),
      language: z.string(),
      stars: z.number(),
      pros: z.array(z.string()),
      cons: z.array(z.string()),
    })),
  }),
  prompt: '列出 2025 年 Top 5 AI Agent 框架',
});

console.log(object.frameworks);
```

## 6. React Hooks 集成

```typescript
// app/api/chat/route.ts — Next.js API Route
import { streamText } from 'ai';
import { openai } from '@ai-sdk/openai';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-5.2'),
    messages,
  });

  return result.toDataStreamResponse();
}

// app/page.tsx — React 组件
'use client';
import { useChat } from 'ai/react';

export default function Chat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat();

  return (
    <div>
      {messages.map(m => (
        <div key={m.id}>
          <strong>{m.role}:</strong> {m.content}
        </div>
      ))}
      <form onSubmit={handleSubmit}>
        <input value={input} onChange={handleInputChange} placeholder="输入消息..." />
        <button type="submit" disabled={isLoading}>发送</button>
      </form>
    </div>
  );
}
```

## 7. MCP 客户端集成

```typescript
import { experimental_createMCPClient as createMCPClient } from 'ai';
import { Experimental_StdioMCPTransport as StdioTransport } from 'ai/mcp-stdio';

// 连接 MCP Server
const mcpClient = await createMCPClient({
  transport: new StdioTransport({
    command: 'npx',
    args: ['-y', '@modelcontextprotocol/server-filesystem', '/workspace'],
  }),
});

// 获取 MCP 工具
const mcpTools = await mcpClient.tools();

// 在 Agent 中使用 MCP 工具
const result = await generateText({
  model: openai('gpt-5.2'),
  prompt: '列出 /workspace/src 目录下的所有文件',
  tools: mcpTools,
  maxSteps: 5,
});
```

## 8. AI Gateway

```
Vercel AI Gateway 功能：

┌─────────────────────────────────────┐
│          AI Gateway                  │
│  ┌──────────┐  ┌─────────────────┐ │
│  │模型路由    │  │自动 Fallback    │ │
│  │Model     │  │Primary → Backup│ │
│  │Routing   │  │                 │ │
│  └──────────┘  └─────────────────┘ │
│  ┌──────────┐  ┌─────────────────┐ │
│  │用量追踪   │  │模型切换          │ │
│  │Spend     │  │无需改代码        │ │
│  │Tracking  │  │                 │ │
│  └──────────┘  └─────────────────┘ │
└─────────────────────────────────────┘
```

```typescript
import { gateway } from '@ai-sdk/gateway';

// 通过 Gateway 路由模型
const result = await generateText({
  model: gateway('fast-model'),  // Gateway 中配置的模型别名
  prompt: 'Hello',
});

// Gateway 配置（Vercel Dashboard）：
// fast-model → gpt-5-mini (primary) → claude-haiku (fallback)
// smart-model → gpt-5.2 (primary) → claude-sonnet (fallback)
```

## 9. 与 LiteLLM 对比

| 特性         | Vercel AI SDK      | LiteLLM            |
|-------------|--------------------|--------------------|
| 语言         | TypeScript         | Python             |
| 定位         | 前端+全栈 AI 开发   | 后端 LLM 网关       |
| 流式支持     | ✅ 原生 + React    | ✅ 基础             |
| React Hooks | ✅ useChat 等      | ❌                  |
| 工具调用     | ✅ Zod Schema      | ✅ OpenAI 格式      |
| MCP 支持    | ✅ 客户端           | ❌                  |
| 结构化输出   | ✅ generateObject   | ✅ response_format  |
| 负载均衡     | ✅ Gateway         | ✅ Router           |
| 预算管理     | ✅ Gateway         | ✅ 细粒度           |
| 自托管       | ✅ SDK / ❌ Gateway| ✅ 完全自托管        |
| 适用场景     | Next.js/React 应用 | Python 后端/Agent   |
## 🎬 推荐视频资源

### 🌐 YouTube
- [Vercel - AI SDK Tutorial](https://www.youtube.com/watch?v=LDB4uaJ87e0) — Vercel AI SDK教程
- [Lee Robinson - AI SDK Demo](https://www.youtube.com/watch?v=DHjqpvDnNGE) — AI SDK实战演示

### 📖 官方文档
- [Vercel AI SDK Docs](https://sdk.vercel.ai/docs) — Vercel AI SDK官方文档
