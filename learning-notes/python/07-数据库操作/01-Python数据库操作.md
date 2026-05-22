# Python数据库操作
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 数据库操作概述

Python提供了多种数据库操作方式：
- **SQLAlchemy**：Python最流行的ORM框架
- **pymongo**：MongoDB的Python驱动
- **redis-py**：Redis的Python客户端
- **pymysql/psycopg2**：MySQL/PostgreSQL的原生驱动

## 2. SQLAlchemy ORM

### 2.1 安装

```bash
pip install sqlalchemy
# MySQL
pip install pymysql
# PostgreSQL
pip install psycopg2-binary
```

### 2.2 连接数据库

```python
from sqlalchemy import create_engine

# MySQL
engine = create_engine('mysql+pymysql://user:password@localhost/dbname')

# PostgreSQL
engine = create_engine('postgresql://user:password@localhost/dbname')

# SQLite
engine = create_engine('sqlite:///database.db')
```

### 2.3 定义模型

> 💡 **SQLAlchemy 2.0 风格说明**：以下示例使用 1.x 经典风格，便于初学者理解。**新项目推荐使用 2.0 的 `DeclarativeBase` + `Mapped[]` 类型注解风格**（详见第 10 节）。

```python
# <!-- 修复于 2026-05-22: 兼容 1.x 经典风格示例，新项目应参考第 10 节使用 DeclarativeBase + Mapped[] -->
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# SQLAlchemy 2.0+ 推荐从 sqlalchemy.orm 导入 declarative_base
# 旧路径 from sqlalchemy.ext.declarative import declarative_base 仍兼容但已废弃
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<User(username='{self.username}', email='{self.email}')>"

# 创建表
Base.metadata.create_all(engine)
```

### 2.4 基本操作

```python
# 创建会话
Session = sessionmaker(bind=engine)
session = Session()

# 添加记录
user = User(username='john', email='john@example.com')
session.add(user)
session.commit()

# 查询记录
# 查询所有
users = session.query(User).all()

# 查询单个
user = session.query(User).filter_by(username='john').first()

# 条件查询
users = session.query(User).filter(User.email.like('%@example.com')).all()

# 更新记录
user = session.query(User).filter_by(username='john').first()
user.email = 'newemail@example.com'
session.commit()

# 删除记录
user = session.query(User).filter_by(username='john').first()
session.delete(user)
session.commit()

# 关闭会话
session.close()
```

### 2.5 关系映射

```python
# <!-- 修复于 2026-05-22: 修正 Relationship 大写错误（应为 relationship 小写） -->
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class Post(Base):
    __tablename__ = 'posts'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(String(1000))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    # 定义关系
    user = relationship('User', backref='posts')

# 使用关系
user = session.query(User).first()
posts = user.posts  # 获取用户的所有文章

post = session.query(Post).first()
author = post.user  # 获取文章作者
```

### 2.6 查询进阶

```python
from sqlalchemy import and_, or_, func

# 多条件查询
users = session.query(User).filter(
    and_(User.username.like('j%'), User.email.isnot(None))
).all()

# 排序
users = session.query(User).order_by(User.created_at.desc()).all()

# 限制和偏移
users = session.query(User).limit(10).offset(20).all()

# 聚合函数
count = session.query(func.count(User.id)).scalar()
avg = session.query(func.avg(User.id)).scalar()

# 分组
from sqlalchemy import func
result = session.query(
    User.username,
    func.count(Post.id).label('post_count')
).join(Post).group_by(User.username).all()
```

## 3. MongoDB操作

> 💡 **异步驱动选择**（2026-05-22）：从 2025-05-14 起 Motor 库已被 [PyMongo Async](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/) 替代（Motor 将于 2026-05-14 EOL）。新项目使用 PyMongo 4.16+ 内置的 `AsyncMongoClient`，现有 Motor 代码应尽快迁移。

### 3.1 安装

```bash
pip install pymongo  # 4.16.x，同时包含同步和异步 API
# <!-- 修复于 2026-05-22: 移除 motor 推荐，PyMongo Async 已 GA 替代 motor -->
```

### 3.2 连接MongoDB

```python
from pymongo import MongoClient

# 连接MongoDB
client = MongoClient('mongodb://localhost:27017/')

# 选择数据库
db = client['mydatabase']

# 选择集合
collection = db['users']
```

### 3.3 基本操作

```python
# 插入文档
user = {
    'username': 'john',
    'email': 'john@example.com',
    'age': 30
}
result = collection.insert_one(user)
print(result.inserted_id)

# 插入多个文档
users = [
    {'username': 'alice', 'email': 'alice@example.com', 'age': 25},
    {'username': 'bob', 'email': 'bob@example.com', 'age': 35}
]
result = collection.insert_many(users)

# 查询文档
# 查询单个
user = collection.find_one({'username': 'john'})

# 查询多个
users = collection.find({'age': {'$gt': 25}})
for user in users:
    print(user)

# 更新文档
collection.update_one(
    {'username': 'john'},
    {'$set': {'age': 31}}
)

# 更新多个文档
collection.update_many(
    {'age': {'$lt': 30}},
    {'$inc': {'age': 1}}
)

# 删除文档
collection.delete_one({'username': 'john'})
collection.delete_many({'age': {'$lt': 18}})
```

### 3.4 查询操作

```python
# 条件查询
users = collection.find({'age': {'$gt': 25, '$lt': 40}})

# 排序
users = collection.find().sort('age', -1)  # -1表示降序

# 限制和跳过
users = collection.find().limit(10).skip(20)

# 投影（选择字段）
users = collection.find({}, {'username': 1, 'email': 1})

# 聚合
pipeline = [
    {'$match': {'age': {'$gt': 25}}},
    {'$group': {'_id': None, 'avg_age': {'$avg': '$age'}}}
]
result = collection.aggregate(pipeline)
```

## 4. Redis操作

### 4.1 安装

```bash
pip install redis
```

### 4.2 连接Redis

```python
import redis

# 连接Redis
r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# 使用连接池
pool = redis.ConnectionPool(host='localhost', port=6379, db=0)
r = redis.Redis(connection_pool=pool, decode_responses=True)
```

### 4.3 字符串操作

```python
# 设置和获取
r.set('key', 'value')
value = r.get('key')

# 设置过期时间
r.setex('key', 60, 'value')  # 60秒后过期
r.set('key', 'value', ex=60)  # 另一种方式

# 自增和自减
r.incr('counter')
r.decr('counter')
r.incrby('counter', 10)
```

### 4.4 哈希操作

```python
# 设置和获取
r.hset('user:1', 'name', 'john')
r.hset('user:1', 'age', 30)
r.hset('user:1', mapping={'name': 'john', 'age': 30})

# 获取
name = r.hget('user:1', 'name')
user = r.hgetall('user:1')

# 获取多个字段
fields = r.hmget('user:1', 'name', 'age')
```

### 4.5 列表操作

```python
# 添加元素
r.lpush('list', 'item1', 'item2')
r.rpush('list', 'item3')

# 获取元素
item = r.lpop('list')
item = r.rpop('list')
items = r.lrange('list', 0, -1)  # 获取所有元素

# 获取长度
length = r.llen('list')
```

### 4.6 集合操作

```python
# 添加元素
r.sadd('set', 'item1', 'item2', 'item3')

# 获取所有元素
members = r.smembers('set')

# 判断元素是否存在
exists = r.sismember('set', 'item1')

# 集合运算
r.sunion('set1', 'set2')  # 并集
r.sinter('set1', 'set2')   # 交集
r.sdiff('set1', 'set2')    # 差集
```

### 4.7 有序集合操作

```python
# 添加元素
r.zadd('zset', {'item1': 10, 'item2': 20, 'item3': 15})

# 获取元素
items = r.zrange('zset', 0, -1, withscores=True)

# 获取排名
rank = r.zrank('zset', 'item1')

# 获取分数
score = r.zscore('zset', 'item1')
```

### 4.8 发布订阅

```python
import redis

# 发布者
pub = redis.Redis(host='localhost', port=6379, db=0)
pub.publish('channel', 'message')

# 订阅者
sub = redis.Redis(host='localhost', port=6379, db=0)
pubsub = sub.pubsub()
pubsub.subscribe('channel')

for message in pubsub.listen():
    if message['type'] == 'message':
        print(message['data'])
```

## 5. 原生SQL操作

### 5.1 MySQL (pymysql)

```python
import pymysql

# 连接数据库
conn = pymysql.connect(
    host='localhost',
    user='root',
    password='password',
    database='mydb',
    charset='utf8mb4'
)

# 创建游标
cursor = conn.cursor()

# 执行查询
cursor.execute('SELECT * FROM users WHERE age > %s', (25,))
results = cursor.fetchall()

# 执行插入
cursor.execute(
    'INSERT INTO users (username, email) VALUES (%s, %s)',
    ('john', 'john@example.com')
)
conn.commit()

# 关闭连接
cursor.close()
conn.close()
```

### 5.2 PostgreSQL (psycopg2)

```python
import psycopg2

# 连接数据库
conn = psycopg2.connect(
    host='localhost',
    user='postgres',
    password='password',
    database='mydb'
)

# 创建游标
cursor = conn.cursor()

# 执行查询
cursor.execute('SELECT * FROM users WHERE age > %s', (25,))
results = cursor.fetchall()

# 执行插入
cursor.execute(
    'INSERT INTO users (username, email) VALUES (%s, %s)',
    ('john', 'john@example.com')
)
conn.commit()

# 关闭连接
cursor.close()
conn.close()
```

## 6. 数据库连接池

### 6.1 SQLAlchemy连接池

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'mysql+pymysql://user:password@localhost/dbname',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_recycle=3600
)
```

### 6.2 Redis连接池

```python
import redis

pool = redis.ConnectionPool(
    host='localhost',
    port=6379,
    db=0,
    max_connections=50
)

r = redis.Redis(connection_pool=pool)
```

## 7. 事务处理

### 7.1 SQLAlchemy事务

```python
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
session = Session()

try:
    user = User(username='john', email='john@example.com')
    session.add(user)
    session.commit()
except Exception as e:
    session.rollback()
    print(f'Error: {e}')
finally:
    session.close()
```

### 7.2 Redis事务

```python
pipe = r.pipeline()
pipe.set('key1', 'value1')
pipe.set('key2', 'value2')
pipe.execute()
```

## 8. 最佳实践

1. **使用ORM**：对于关系型数据库，使用ORM可以简化代码
2. **连接池**：使用连接池管理数据库连接
3. **异常处理**：数据库操作可能失败，需要适当的异常处理
4. **事务管理**：确保数据一致性
5. **性能优化**：使用索引、批量操作、查询优化

## 9. 总结

Python数据库操作工具：
- **SQLAlchemy**：功能强大的ORM框架
- **pymongo**：MongoDB的Python驱动
- **redis-py**：Redis的Python客户端
- **pymysql/psycopg2**：关系型数据库的原生驱动

选择合适的工具可以高效地进行数据库操作。


<!-- version-check: SQLAlchemy 2.0.49, Pydantic 2.13.3, PyMongo 4.16.0, Motor 3.7.x（已废弃，2026-05-14 EOL）, checked 2026-05-22 -->

> 🔄 更新于 2026-05-22

## 10. SQLAlchemy 2.0.x 版本演进

### 10.1 当前版本

SQLAlchemy **2.0.49** 是当前最新稳定版（2026-05），2.1.x 仍处于 beta 阶段（最新 2.1.0b3）。生产环境继续使用 2.0.x。

### 10.2 SQLAlchemy 2.0 vs 1.x 关键变化

SQLAlchemy 2.0 是一次重大重写，如果文档中仍使用 1.x 风格代码，建议迁移：

```python
# ❌ 旧版 1.x 风格（已废弃）
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

# ✅ 新版 2.0 风格（推荐）
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    # 使用 Mapped 类型注解替代 Column()
    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True)
    email: Mapped[str] = mapped_column(unique=True)
    # Optional 字段
    bio: Mapped[str | None] = mapped_column(default=None)
```

### 10.3 2.0 风格查询

```python
from sqlalchemy import select
from sqlalchemy.orm import Session

# ❌ 旧版查询风格
# session.query(User).filter(User.username == 'john').first()

# ✅ 新版 select() 风格
with Session(engine) as session:
    # 查询单条
    stmt = select(User).where(User.username == 'john')
    user = session.scalars(stmt).first()

    # 查询多条
    stmt = select(User).where(User.email.like('%@example.com'))
    users = session.scalars(stmt).all()

    # 聚合查询
    from sqlalchemy import func
    stmt = select(func.count()).select_from(User)
    count = session.scalar(stmt)
```

### 10.4 异步支持

```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# 异步引擎（需要 asyncpg 或 aiomysql 驱动）
async_engine = create_async_engine('postgresql+asyncpg://user:pass@localhost/db')
AsyncSessionLocal = async_sessionmaker(async_engine, class_=AsyncSession)

async def get_user(user_id: int):
    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.id == user_id)
        result = await session.scalars(stmt)
        return result.first()
```

### 10.5 安装推荐

```bash
# 使用 uv（2026 年推荐）
uv add sqlalchemy[asyncio]
uv add asyncpg  # PostgreSQL 异步驱动
uv add aiomysql  # MySQL 异步驱动

# 使用 pip
pip install sqlalchemy[asyncio] asyncpg
```

来源：[SQLAlchemy 官方博客](https://www.sqlalchemy.org/blog/)

## 11. Pydantic v2.13 新特性（2026-04-13）

Pydantic v2.13 是数据验证库的最新版本，与 SQLAlchemy 配合使用时非常强大。

### 11.1 多态序列化

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str

class UserLogin(User):
    password: str

class OuterModel(BaseModel):
    user: User

outer = OuterModel(user=UserLogin(name='test', password='secret'))

# 默认行为：只序列化声明类型的字段
print(outer.model_dump())
# {'user': {'name': 'test'}}

# 新增：多态序列化，包含子类的所有字段
print(outer.model_dump(polymorphic_serialization=True))
# {'user': {'name': 'test', 'password': 'secret'}}
```

### 11.2 计算字段的 exclude_if

```python
from pydantic import BaseModel, computed_field

class Order(BaseModel):
    cash: int
    card: int

    @computed_field(exclude_if=lambda v: v == 0)
    def total(self) -> int:
        return self.cash + self.card

order = Order(cash=0, card=0)
order.model_dump()
# {'cash': 0, 'card': 0}  ← total 为 0 时自动排除
```

### 11.3 私有属性的 validated data

```python
from pydantic import BaseModel, PrivateAttr

class Model(BaseModel):
    foo: int
    _priv1: int = PrivateAttr(default=2)
    # default_factory 可以访问已验证的数据
    _priv2: int = PrivateAttr(
        default_factory=lambda data: data['foo'] + data['_priv1']
    )

m = Model(foo=1)
m._priv2  # 3
```

来源：[Pydantic v2.13 发布公告](https://pydantic.dev/articles/pydantic-v2-13-release)

## 12. PyMongo Async — 异步 MongoDB 驱动

<!-- 修复于 2026-05-22: 补充 PyMongo 4.16+ Async API，替代已废弃的 Motor -->

PyMongo 4.16+ 内置 `AsyncMongoClient`，原 Motor 库的功能现在通过统一的 PyMongo 包提供。

### 12.1 异步基本使用

```python
import asyncio
from pymongo import AsyncMongoClient

async def main():
    # 异步客户端
    client = AsyncMongoClient('mongodb://localhost:27017/')
    db = client['mydb']
    collection = db['users']

    # 异步插入
    await collection.insert_one({'username': 'john', 'age': 30})

    # 异步查询单条
    user = await collection.find_one({'username': 'john'})
    print(user)

    # 异步遍历查询结果
    async for doc in collection.find({'age': {'$gte': 18}}):
        print(doc)

    # 异步聚合
    pipeline = [{'$group': {'_id': '$city', 'count': {'$sum': 1}}}]
    async for result in await collection.aggregate(pipeline):
        print(result)

    await client.close()

asyncio.run(main())
```

### 12.2 与 FastAPI 集成

```python
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pymongo import AsyncMongoClient

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mongo = AsyncMongoClient('mongodb://localhost:27017/')
    yield
    await app.state.mongo.close()

app = FastAPI(lifespan=lifespan)

@app.get("/users/{username}")
async def get_user(username: str):
    db = app.state.mongo['mydb']
    user = await db.users.find_one({'username': username})
    return user
```

### 12.3 Motor 迁移要点

| Motor (旧) | PyMongo Async (新) |
|------------|--------------------|
| `from motor.motor_asyncio import AsyncIOMotorClient` | `from pymongo import AsyncMongoClient` |
| `AsyncIOMotorClient(...)` | `AsyncMongoClient(...)` |
| `await collection.find_one(...)` | `await collection.find_one(...)`（一致） |
| `cursor = collection.find(...)` | `cursor = collection.find(...)`（一致） |
| `async for doc in cursor` | `async for doc in cursor`（一致） |

来源：[PyMongo 异步迁移指南](https://www.mongodb.com/docs/languages/python/pymongo-driver/current/reference/migration/) / [Motor 废弃公告](https://pypi.org/project/motor/)
