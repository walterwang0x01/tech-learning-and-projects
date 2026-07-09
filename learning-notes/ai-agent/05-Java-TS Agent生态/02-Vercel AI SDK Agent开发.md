# Vercel AI SDK Agent 开发
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

<!-- version-check: Vercel AI SDK 7.0.18, checked 2026-07-09 -->
<!-- 修复于 2026-07-09: AI SDK 6 → 7.0.18（npm 实测最新） -->

> 🔄 更新于 2026-04-18

使用 Vercel AI SDK（TypeScript）构建 AI Agent，核心模式：`generateText` + `tools` + `maxSteps` 实现 Agent 循环。

**AI SDK 7 重大更新**（2000万+ 月下载量）：
- **Agent 抽象**：一等公民 `Agent` 类，定义可复用的 Agent（模型 + 指令 + 工具）
- **MCP 集成**：原生支持 MCP Server 连接和工具发现
- **工具执行审批**：Human-in-the-loop 工具调用审批机制
- **AI DevTools**：内置调试工具，追踪 Agent 执行步骤
- **AI Gateway**：统一端点访问 500+ AI 模型

> 来源：[AI SDK 6 发布公告](https://vercel.com/blog/ai-sdk-6)、[AI SDK 文档](https://ai-sdk.dev/docs)

```
┌─────────────────────────────────────────┐
│           Agent 循环                     │
│                                          │
│  User Input                              │
│      ↓                                   │
│  ┌──────────┐                            │
│  │generateText│←──────────────┐          │
│  │+ tools    │               │          │
│  └─────┬────┘               │          │
│        ↓                     │          │
│  需要工具？──→ YES → 执行工具 ─┘          │
│        │                                 │
│        NO                                │
│        ↓                                 │
│  返回最终结果                              │
│  (maxSteps 控制最大循环次数)               │
└─────────────────────────────────────────┘
```

## 2. 基础 Agent 模式

```typescript
import { generateText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

// 定义工具集
const tools = {
  searchWeb: tool({
    description: '搜索互联网获取最新信息',
    parameters: z.object({
      query: z.string().describe('搜索关键词'),
    }),
    execute: async ({ query }) => {
      const response = await fetch(`https://api.tavily.com/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ api_key: process.env.TAVILY_KEY, query }),
      });
      const data = await response.json();
      return data.results.map((r: any) => r.content).join('\n');
    },
  }),

  runCode: tool({
    description: '执行 JavaScript 代码并返回结果',
    parameters: z.object({
      code: z.string().describe('要执行的 JavaScript 代码'),
    }),
    execute: async ({ code }) => {
      try {
        const result = eval(code);
        return String(result);
      } catch (e: any) {
        return `Error: ${e.message}`;
      }
    },
  }),

  writeFile: tool({
    description: '写入文件',
    parameters: z.object({
      path: z.string(),
      content: z.string(),
    }),
    execute: async ({ path, content }) => {
      const fs = await import('fs/promises');
      await fs.writeFile(path, content);
      return `文件已写入: ${path}`;
    },
  }),
};

// Agent 执行
const { text, steps } = await generateText({
  model: openai('gpt-4o'),
  system: '你是全能助手。使用工具完成任务，可以搜索、执行代码、写文件。',
  prompt: '搜索 2025 年最流行的 AI 框架，整理成表格写入 report.md',
  tools,
  maxSteps: 10,
});

console.log(`执行了 ${steps.length} 步`);
console.log(text);
```

## 3. 流式 Agent

```typescript
import { streamText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

// 流式 Agent — 实时输出思考过程
const result = streamText({
  model: openai('gpt-4o'),
  system: '你是研究助手。先搜索信息，再综合回答。',
  prompt: 'LangGraph 和 CrewAI 哪个更适合生产环境？',
  tools: {
    search: tool({
      description: '搜索技术信息',
      parameters: z.object({ query: z.string() }),
      execute: async ({ query }) => `搜索结果: ${query} 相关信息...`,
    }),
  },
  maxSteps: 5,
  onStepFinish: ({ stepType, toolCalls, toolResults, text }) => {
    if (stepType === 'tool-result') {
      console.log(`🔧 工具调用: ${toolCalls?.map(tc => tc.toolName).join(', ')}`);
    }
  },
});

// 流式输出
for await (const chunk of result.textStream) {
  process.stdout.write(chunk);
}
```

## 4. 结构化输出 Agent

```typescript
import { generateObject, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

// 输出结构化数据的 Agent
const { object } = await generateObject({
  model: openai('gpt-4o'),
  schema: z.object({
    analysis: z.object({
      topic: z.string(),
      summary: z.string(),
      keyFindings: z.array(z.object({
        finding: z.string(),
        confidence: z.number().min(0).max(1),
        source: z.string(),
      })),
      recommendation: z.string(),
    }),
  }),
  prompt: '分析 2025 年 AI Agent 框架市场格局',
});

console.log(object.analysis.keyFindings);
```

## 5. MCP 集成

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';
import { experimental_createMCPClient as createMCPClient } from 'ai';
import { Experimental_StdioMCPTransport as StdioTransport } from 'ai/mcp-stdio';

// 连接多个 MCP Server
const fsClient = await createMCPClient({
  transport: new StdioTransport({
    command: 'npx',
    args: ['-y', '@modelcontextprotocol/server-filesystem', '/workspace'],
  }),
});

const githubClient = await createMCPClient({
  transport: new StdioTransport({
    command: 'npx',
    args: ['-y', '@modelcontextprotocol/server-github'],
    env: { GITHUB_TOKEN: process.env.GITHUB_TOKEN! },
  }),
});

// 合并所有 MCP 工具
const tools = {
  ...(await fsClient.tools()),
  ...(await githubClient.tools()),
};

const { text } = await generateText({
  model: openai('gpt-4o'),
  system: '你是开发助手，可以操作文件和 GitHub。',
  prompt: '读取 /workspace/README.md 的内容，然后在 GitHub 创建一个 issue 总结项目',
  tools,
  maxSteps: 10,
});

// 清理
await fsClient.close();
await githubClient.close();
```

## 6. React Hooks 构建聊天 Agent

```typescript
// app/api/chat/route.ts
import { streamText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

export async function POST(req: Request) {
  const { messages } = await req.json();

  const result = streamText({
    model: openai('gpt-4o'),
    system: '你是智能助手，可以搜索信息和执行计算。',
    messages,
    tools: {
      calculate: tool({
        description: '数学计算',
        parameters: z.object({ expression: z.string() }),
        execute: async ({ expression }) => String(eval(expression)),
      }),
    },
    maxSteps: 5,
  });

  return result.toDataStreamResponse();
}

// app/page.tsx
'use client';
import { useChat } from '@ai-sdk/react';

export default function AgentChat() {
  const { messages, input, handleInputChange, handleSubmit, isLoading } = useChat({
    maxSteps: 5,  // 客户端也需要设置
  });

  return (
    <div className="flex flex-col h-screen p-4">
      <div className="flex-1 overflow-y-auto space-y-4">
        {messages.map(m => (
          <div key={m.id} className={m.role === 'user' ? 'text-right' : 'text-left'}>
            <span className="font-bold">{m.role === 'user' ? '你' : 'Agent'}: </span>
            {m.content}
            {/* 显示工具调用 */}
            {m.toolInvocations?.map((ti, i) => (
              <div key={i} className="text-sm text-gray-500 mt-1">
                🔧 {ti.toolName}: {JSON.stringify(ti.result).slice(0, 100)}
              </div>
            ))}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="flex gap-2 mt-4">
        <input
          value={input}
          onChange={handleInputChange}
          className="flex-1 border rounded p-2"
          placeholder="输入消息..."
        />
        <button type="submit" disabled={isLoading} className="bg-blue-500 text-white px-4 rounded">
          {isLoading ? '思考中...' : '发送'}
        </button>
      </form>
    </div>
  );
}
```

## 7. 多 Agent 协作

```typescript
import { generateText, tool } from 'ai';
import { openai } from '@ai-sdk/openai';
import { z } from 'zod';

// 研究 Agent
async function researchAgent(topic: string): Promise<string> {
  const { text } = await generateText({
    model: openai('gpt-4o'),
    system: '你是研究员，深入调研给定主题。',
    prompt: topic,
    tools: {
      search: tool({
        description: '搜索信息',
        parameters: z.object({ query: z.string() }),
        execute: async ({ query }) => `搜索结果: ${query}...`,
      }),
    },
    maxSteps: 5,
  });
  return text;
}

// 写作 Agent
async function writerAgent(research: string, topic: string): Promise<string> {
  const { text } = await generateText({
    model: openai('gpt-4o'),
    system: '你是技术作者，基于调研材料撰写高质量文章。',
    prompt: `主题: ${topic}\n调研材料:\n${research}\n\n请撰写文章。`,
  });
  return text;
}

// 编排
async function contentPipeline(topic: string) {
  const research = await researchAgent(topic);
  const article = await writerAgent(research, topic);
  return article;
}

const article = await contentPipeline('AI Agent 2025 趋势');
```

## 8. 错误处理与重试

```typescript
import { generateText } from 'ai';
import { openai } from '@ai-sdk/openai';

// 带重试的 Agent
async function resilientAgent(prompt: string, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const { text } = await generateText({
        model: openai('gpt-4o'),
        prompt,
        maxSteps: 10,
        abortSignal: AbortSignal.timeout(30000), // 30s 超时
      });
      return text;
    } catch (error: any) {
      console.error(`尝试 ${i + 1} 失败: ${error.message}`);
      if (i === maxRetries - 1) throw error;
      await new Promise(r => setTimeout(r, 1000 * (i + 1))); // 退避重试
    }
  }
}
```
## 🎬 推荐视频资源

### 🌐 YouTube
- [Vercel - AI SDK Agent Tutorial](https://www.youtube.com/watch?v=LDB4uaJ87e0) — AI SDK Agent教程
- [Lee Robinson - Building AI Apps](https://www.youtube.com/watch?v=DHjqpvDnNGE) — AI应用构建

### 📖 官方文档
- [Vercel AI SDK Docs](https://sdk.vercel.ai/docs) — 官方文档
