# Node.js 数据库操作
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

<!-- version-check: Prisma 7.8.0, Mongoose 9.7.3, ioredis deprecated → node-redis, Drizzle ORM 0.44.x, checked 2026-07-10 -->
<!-- 修复于 2026-07-10: Prisma 7.7.x → 7.8.0（2026-04-22）；Mongoose 9.6.1 → 9.7.3（2026-06-26） -->

## 1. Prisma ORM（推荐）

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        Int      @id @default(autoincrement())
  email     String   @unique
  name      String?
  posts     Post[]
  createdAt DateTime @default(now())
}

model Post {
  id       Int    @id @default(autoincrement())
  title    String
  content  String?
  author   User   @relation(fields: [authorId], references: [id])
  authorId Int
}
```

```javascript
import { PrismaClient } from '@prisma/client';
const prisma = new PrismaClient();

// CRUD
const user = await prisma.user.create({
  data: { email: 'test@example.com', name: '张三' },
});

const users = await prisma.user.findMany({
  where: { name: { contains: '张' } },
  include: { posts: true },
  orderBy: { createdAt: 'desc' },
  skip: 0,
  take: 10,
});

await prisma.user.update({
  where: { id: 1 },
  data: { name: '李四' },
});

await prisma.user.delete({ where: { id: 1 } });

// 事务
await prisma.$transaction([
  prisma.user.create({ data: { email: 'a@b.com' } }),
  prisma.post.create({ data: { title: 'Hello', authorId: 1 } }),
]);
```

## 2. MongoDB（Mongoose）

```javascript
import mongoose from 'mongoose';

await mongoose.connect(process.env.MONGODB_URI);

const userSchema = new mongoose.Schema({
  name: { type: String, required: true },
  email: { type: String, unique: true },
  age: { type: Number, min: 0 },
  createdAt: { type: Date, default: Date.now },
});

const User = mongoose.model('User', userSchema);

// CRUD
const user = await User.create({ name: '张三', email: 'test@example.com' });
const users = await User.find({ age: { $gte: 18 } }).sort({ createdAt: -1 }).limit(10);
await User.findByIdAndUpdate(id, { name: '李四' });
await User.findByIdAndDelete(id);
```

## 3. Redis（ioredis）

```javascript
import Redis from 'ioredis';
const redis = new Redis(process.env.REDIS_URL);

// 基本操作
await redis.set('key', 'value', 'EX', 3600); // 1小时过期
const value = await redis.get('key');

// Hash
await redis.hset('user:1', { name: '张三', age: '25' });
const user = await redis.hgetall('user:1');

// 缓存模式
async function getCachedUser(id) {
  const cached = await redis.get(`user:${id}`);
  if (cached) return JSON.parse(cached);

  const user = await prisma.user.findUnique({ where: { id } });
  await redis.set(`user:${id}`, JSON.stringify(user), 'EX', 300);
  return user;
}
```


## 4. Drizzle ORM（SQL-first 替代方案）

> 🔄 更新于 2026-05-02

Drizzle ORM 是 2026 年增长最快的 TypeScript ORM，采用 SQL-first 设计理念，Schema 即 TypeScript，查询接近原生 SQL。

```typescript
// drizzle/schema.ts — Schema 就是 TypeScript
import { pgTable, serial, text, timestamp, integer } from 'drizzle-orm/pg-core';

export const users = pgTable('users', {
  id: serial('id').primaryKey(),
  email: text('email').notNull().unique(),
  name: text('name'),
  createdAt: timestamp('created_at').defaultNow(),
});

export const posts = pgTable('posts', {
  id: serial('id').primaryKey(),
  title: text('title').notNull(),
  content: text('content'),
  authorId: integer('author_id').references(() => users.id),
});
```

```typescript
import { drizzle } from 'drizzle-orm/node-postgres';
import { eq, like, desc } from 'drizzle-orm';
import { users, posts } from './schema';

const db = drizzle(process.env.DATABASE_URL!);

// CRUD — 查询接近原生 SQL
const user = await db.insert(users)
  .values({ email: 'test@example.com', name: '张三' })
  .returning();

const result = await db.select()
  .from(users)
  .where(like(users.name, '%张%'))
  .orderBy(desc(users.createdAt))
  .limit(10);

await db.update(users)
  .set({ name: '李四' })
  .where(eq(users.id, 1));

await db.delete(users).where(eq(users.id, 1));

// 关联查询
const usersWithPosts = await db.select()
  .from(users)
  .leftJoin(posts, eq(users.id, posts.authorId));
```

## 5. Prisma 7.x 版本演进

> 🔄 更新于 2026-05-02

Prisma 7.0 是一个结构性版本，聚焦长期架构而非表面功能。当前稳定版为 **7.8.0**（2026-04-22 发布）。来源：[Prisma 7 AMA](https://www.prisma.io/blog/prisma-7-ama-clearing-up-the-why-behind-the-changes)

### 5.1 Prisma 7 核心变化

```prisma
// Prisma 7 推荐的 generator 配置
generator client {
  // 新的 provider 名称（v7 推荐）
  provider = "prisma-client"
  // 推荐显式指定输出路径
  output   = "../src/generated/prisma"
}
```

**关键 Breaking Changes：**

| 变化 | v6 | v7 |
|------|----|----|
| Generator provider | `prisma-client-js` | `prisma-client`（推荐） |
| 包体积 | 标准 | 减少 ~90% |
| 查询性能 | 基准 | ~3x 提升 |
| Node.js 最低版本 | 16.x | 18.x |
| TypeScript 最低版本 | 4.7 | 5.1 |
| `prisma bootstrap` | 无 | 新增（一键初始化 Prisma Postgres） |
| TypedSQL | Preview | 稳定 |

### 5.2 Prisma Next 路线图

Prisma Next 是 Prisma ORM 的下一代重写，2026-03-04 公开仓库。来源：[Prisma Next Roadmap](https://www.prisma.io/blog/prisma-next-roadmap)

核心新特性：
- **全新查询 API** — 自定义集合方法、流式查询结果
- **类型安全 SQL 查询构建器** — 复杂 SQL 的逃生舱
- **扩展系统** — 安装新行为和数据类型（如 pgvector）
- **TypeScript Schema** — 可选替代 `.prisma` 文件
- **MongoDB 原生支持** — 多态模型、嵌入集合

```
Prisma Next 时间线：
├─ 2026-04：开放外部贡献（扩展点 API 稳定）
├─ 2026-05：Early Access（Postgres + SQLite）
├─ 2026-06~07：Postgres GA
└─ Prisma 7 继续长期支持
```

### 5.3 版本选择建议

| 场景 | 推荐 |
|------|------|
| 新项目 | Prisma 7.x（稳定，性能提升 3x） |
| 现有 v5/v6 项目 | 升级到 7.x（参考迁移指南） |
| Edge/Serverless | 考虑 Drizzle ORM（更小包体积） |
| 想尝鲜 | Prisma Next EA（2026-05 开放） |

## 6. Mongoose 9.x 版本演进

> 🔄 更新于 2026-05-02

Mongoose 9 于 2025-11-21 发布，当前稳定版为 **9.7.3**（2026-06-26 发布）。来源：[Mongoose Version Support](https://mongoosejs.com/docs/version-support.html)

### 6.1 Mongoose 9 Breaking Changes

```javascript
// ❌ Mongoose 8.x — pre 中间件使用 next()
schema.pre('save', function(next) {
  // 异步操作
  next();
});

// ✅ Mongoose 9.x — 必须使用 async/await
schema.pre('save', async function() {
  // 异步操作
});
```

**关键变化：**

| 变化 | Mongoose 8 | Mongoose 9 |
|------|-----------|-----------|
| pre 中间件 | 支持 `next()` 回调 | 仅 async/await |
| `doValidate()` | 回调模式 | 返回 Promise |
| Update Pipeline | 默认允许 | 默认禁止（需 `updatePipeline: true`） |
| `isValidObjectId(6)` | `true` | `false` |
| 索引 `background` 选项 | 支持 | 已移除 |

### 6.2 版本选择

| 场景 | 推荐 |
|------|------|
| 新 MongoDB 项目 | Mongoose 9.x |
| 现有 Mongoose 8.x | 评估迁移（主要改 pre 中间件） |
| TypeScript 优先 | 考虑 Prisma + MongoDB 或 Drizzle |

## 7. Redis 客户端：ioredis → node-redis 迁移

> 🔄 更新于 2026-05-02

**重要变化：ioredis 已进入维护模式**，官方推荐新项目使用 [node-redis](https://redis.io/docs/latest/develop/clients/nodejs/)。来源：[ioredis npm](https://www.npmjs.com/package/ioredis)

```javascript
// node-redis — 2026 年推荐的 Node.js Redis 客户端
import { createClient } from 'redis';

const client = createClient({ url: process.env.REDIS_URL });
await client.connect();

// 基本操作
await client.set('key', 'value', { EX: 3600 });
const value = await client.get('key');

// Hash
await client.hSet('user:1', { name: '张三', age: '25' });
const user = await client.hGetAll('user:1');

// 支持 Redis 8 新特性（Hash Field Expiration、JSON、Search 等）
// ioredis 不支持这些新特性

await client.disconnect();
```

**node-redis vs ioredis 对比：**

| 特性 | node-redis | ioredis |
|------|-----------|---------|
| 维护状态 | 活跃开发 | 维护模式 |
| Redis 8 支持 | ✅ 完整 | ❌ 不支持新命令 |
| JSON/Search/TimeSeries | ✅ 原生 | ❌ 不支持 |
| TypeScript | ✅ 内置类型 | ✅ 内置类型 |
| Cluster | ✅ | ✅ |
| 推荐场景 | 新项目 | 现有项目维护 |

## 8. 2026 年 Node.js ORM/数据库选型

> 🔄 更新于 2026-05-02

| 场景 | 推荐方案 | 理由 |
|------|---------|------|
| 全栈应用（PostgreSQL） | **Prisma 7.x** | 类型安全、迁移工具成熟、生态最大 |
| Edge/Serverless | **Drizzle ORM** | 零依赖、包体积小、SQL-first |
| MongoDB 项目 | **Mongoose 9.x** | MongoDB 生态标准、Schema 验证 |
| 高性能 SQL | **Drizzle ORM** | 查询接近原生 SQL、无运行时开销 |
| Redis 缓存 | **node-redis** | 官方推荐、支持 Redis 8 新特性 |
| 快速原型 | **Prisma 7.x** | Prisma Studio、自动迁移、开发体验好 |
| 复杂 SQL 查询 | **Drizzle ORM** 或 **Prisma TypedSQL** | SQL-first 设计或类型安全原生 SQL |

来源：[Prisma vs Drizzle vs ZenStack 2026](https://zenstack.dev/blog/orm-2026)
