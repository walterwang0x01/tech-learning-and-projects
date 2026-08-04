# Express 与 Koa 框架
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. Express

```javascript
import express from 'express';
import cors from 'cors';

const app = express();

// 中间件
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));
app.use(express.static('public'));

// 路由
app.get('/api/users', async (req, res) => {
  const { page = 1, limit = 10 } = req.query;
  const users = await User.find().skip((page - 1) * limit).limit(limit);
  res.json({ code: 0, data: users });
});

app.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  if (!user) return res.status(404).json({ code: 404, message: 'Not found' });
  res.json({ code: 0, data: user });
});

app.post('/api/users', async (req, res) => {
  const user = await User.create(req.body);
  res.status(201).json({ code: 0, data: user });
});

// 路由模块化
import { Router } from 'express';
const router = Router();
router.get('/', getUsers);
router.post('/', createUser);
app.use('/api/users', router);

// 错误处理中间件（4个参数）
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(err.status || 500).json({
    code: err.status || 500,
    message: err.message || 'Internal Server Error',
  });
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

## 2. Koa

> ⚠️ **注意**：Koa 3.x 已发布（2024），要求 Node.js 18+。以下代码兼容 Koa 2.x 和 3.x。

```javascript
import Koa from 'koa';
import Router from '@koa/router';
import bodyParser from 'koa-bodyparser';

const app = new Koa();
const router = new Router();

// 洋葱模型中间件
app.use(async (ctx, next) => {
  const start = Date.now();
  await next();
  const ms = Date.now() - start;
  ctx.set('X-Response-Time', `${ms}ms`);
});

app.use(bodyParser());

// 路由
router.get('/api/users', async (ctx) => {
  ctx.body = { code: 0, data: await User.find() };
});

router.post('/api/users', async (ctx) => {
  const user = await User.create(ctx.request.body);
  ctx.status = 201;
  ctx.body = { code: 0, data: user };
});

app.use(router.routes());
app.use(router.allowedMethods());

// 错误处理
app.on('error', (err, ctx) => {
  console.error('Server error:', err);
});

app.listen(3000);
```

## 3. NestJS（简介）

```typescript
// NestJS：基于装饰器的 Node.js 框架，类似 Spring Boot
@Controller('users')
export class UsersController {
  constructor(private readonly usersService: UsersService) {}

  @Get()
  findAll(): Promise<User[]> {
    return this.usersService.findAll();
  }

  @Post()
  create(@Body() createUserDto: CreateUserDto): Promise<User> {
    return this.usersService.create(createUserDto);
  }
}

@Injectable()
export class UsersService {
  constructor(@InjectRepository(User) private repo: Repository<User>) {}
  findAll() { return this.repo.find(); }
  create(dto: CreateUserDto) { return this.repo.save(dto); }
}
```
## 4. Express 5.1 与 NestJS 11 版本演进

> 🔄 更新于 2026-04-30

<!-- version-check: Express 5.1.0, NestJS 11.1.28, Koa 3.1.x, Fastify 5.10.x, Hono 4.12.x, checked 2026-07-10 -->
<!-- 修复于 2026-07-10: NestJS 11.1.19 → 11.1.28（2026-07-08）；Fastify 5.6.x → 5.10.x；补充 NestJS 12 预览已上线 @next 标签 -->

### 4.1 Express 5.1（npm 默认版本）

Express 5.1.0 于 2025-03-31 成为 npm `latest` 标签的默认版本，结束了 Express 4 长达 10 年的统治。这是 Express 历史上首次引入 LTS 支持计划。

**核心变化**：

| 特性 | Express 4.x | Express 5.x |
|------|------------|------------|
| async 错误处理 | 需要 try/catch | 自动转发 rejected Promise |
| 路径匹配 | 宽松正则 | 严格 path-to-regexp v8 |
| npm 默认 | ✅（已 EOL 计划中） | ✅（5.1.0 起） |
| LTS 支持 | 社区维护 | 首次官方 LTS 计划 |
| body-parser | 内置 v1 | 升级到 v2.2.0（移除 Brotli 遗留检查） |
| router | 内置 v1 | 升级到 v2.2.0（移除 setImmediate 遗留检查） |

```javascript
// Express 5 自动 async 错误处理（无需 try/catch）
import express from 'express';
const app = express();

// Express 5：rejected Promise 自动转发到错误中间件
app.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id); // 抛出异常会自动被捕获
  if (!user) throw new NotFoundError('用户不存在');
  res.json({ data: user });
});

// 错误中间件照常工作
app.use((err, req, res, next) => {
  res.status(err.status || 500).json({ error: err.message });
});
```

**迁移工具**：官方提供 codemod 包自动化 v4→v5 迁移，但路径匹配语法变化需要手动修改。

> 来源：[Express 5.1 Release](https://expressjs.com/2025/03/31/v5-1-latest-release.html)

### 4.2 NestJS 11（当前 v11.1.28）

NestJS 11 于 2025-01 发布，v12 计划 2026 Q3 发布（ESM 原生支持）。v12 预览包已于 2026-06 发布到 npm `next` 标签（`@nestjs/core@12.0.0-alpha.x`），可用 `npx @nestjs/cli@next new` 提前体验。

**核心新特性**：

- **内置 JSON 日志**：`ConsoleLogger` 原生支持 JSON 格式输出，无需 Pino 等第三方库
- **CacheModule 升级**：使用 cache-manager v6 + Keyv 统一接口，支持 Redis/MongoDB/内存等多后端
- **日志增强**：深层嵌套对象格式化、Map/Set 支持、自定义日志前缀

```typescript
// NestJS 11 内置 JSON 日志
import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

const app = await NestFactory.create(AppModule, {
  logger: console, // 或使用内置 JSON 格式
});

// NestJS 11 CacheModule（cache-manager v6 + Keyv）
import { CacheModule } from '@nestjs/cache-manager';
import KeyvRedis from '@keyv/redis';

@Module({
  imports: [
    CacheModule.registerAsync({
      useFactory: () => ({
        stores: [new KeyvRedis('redis://localhost:6379')],
      }),
    }),
  ],
})
export class AppModule {}
```

**NestJS 12 预览**（2026 Q3 GA，预览包已上线）：全面迁移到 ESM（`nest new` 时可选择 CJS/ESM）、测试框架由 Jest 切换为 Vitest、ESLint 切换为 oxlint、Monorepo 默认构建工具切换为 Rspack（Webpack 已废弃）、路由装饰器支持 Standard Schema（可直接用 Zod/Valibot 替代 class-validator）。

> 来源：[NestJS 11 Announcement](https://trilon.io/blog/announcing-nestjs-11-whats-new)、[NestJS v12 PR](https://github.com/nestjs/nest/pull/16391)

### 4.3 2026 年 Node.js 后端框架选型

| 框架 | 定位 | 适用场景 | 当前版本 |
|------|------|---------|---------|
| Express 5.1 | 极简、灵活 | 小型 API、微服务、快速原型 | 5.1.0 |
| Koa | 现代中间件 | 需要精细控制的中间件场景 | 3.1.x |
| NestJS 11 | 企业级、装饰器 | 大型项目、团队协作、微服务 | 11.1.x |
| Fastify | 高性能 | 高吞吐量 API、性能敏感场景 | 5.10.x |
| Hono | 超轻量、多运行时 | Edge/Serverless、Cloudflare Workers | 4.12.x |

## 🎬 推荐视频资源

- [Traversy Media - Express Crash Course](https://www.youtube.com/watch?v=SccSCuHhOw0) — Express速成
- [freeCodeCamp - Express.js Full Course](https://www.youtube.com/watch?v=G8uL0lFFoN0) — Express完整课程
