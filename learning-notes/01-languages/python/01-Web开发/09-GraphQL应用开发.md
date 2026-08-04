# GraphQL 应用开发
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> 使用 Python 开发 GraphQL API

## 1. GraphQL 概述

GraphQL 特点：
- 单一端点
- 客户端指定查询字段
- 强类型系统
- 实时订阅

## 2. Graphene 框架

### 2.1 安装

```bash
pip install graphene graphene-django
```

### 2.2 基础 Schema

```python
import graphene

class Query(graphene.ObjectType):
    hello = graphene.String(name=graphene.String(default_value="World"))
    
    def resolve_hello(self, info, name):
        return f"Hello {name}"

schema = graphene.Schema(query=Query)

# 查询
query = """
    {
        hello(name: "GraphQL")
    }
"""
result = schema.execute(query)
print(result.data)  # {'hello': 'Hello GraphQL'}
```

## 3. 对象类型

### 3.1 定义类型

```python
class User(graphene.ObjectType):
    id = graphene.ID()
    username = graphene.String()
    email = graphene.String()
    posts = graphene.List('Post')

class Post(graphene.ObjectType):
    id = graphene.ID()
    title = graphene.String()
    content = graphene.String()
    author = graphene.Field(User)

class Query(graphene.ObjectType):
    users = graphene.List(User)
    user = graphene.Field(User, id=graphene.ID())
    
    def resolve_users(self, info):
        return get_all_users()
    
    def resolve_user(self, info, id):
        return get_user_by_id(id)
```

## 4. 变更（Mutations）

### 4.1 创建变更

```python
class CreateUser(graphene.Mutation):
    class Arguments:
        username = graphene.String(required=True)
        email = graphene.String(required=True)
    
    user = graphene.Field(User)
    success = graphene.Boolean()
    
    def mutate(self, info, username, email):
        user = create_user(username=username, email=email)
        return CreateUser(user=user, success=True)

class Mutation(graphene.ObjectType):
    create_user = CreateUser.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)
```

## 5. FastAPI + GraphQL

### 5.1 集成

```python
from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import strawberry

@strawberry.type
class User:
    id: int
    username: str
    email: str

@strawberry.type
class Query:
    @strawberry.field
    def user(self, id: int) -> User:
        return get_user(id)

@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_user(self, username: str, email: str) -> User:
        return create_user(username, email)

schema = strawberry.Schema(query=Query, mutation=Mutation)
graphql_app = GraphQLRouter(schema)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")
```

## 6. 订阅（Subscriptions）

### 6.1 实时订阅

```python
import asyncio
from strawberry.fastapi import GraphQLRouter
import strawberry

@strawberry.type
class Message:
    content: str
    timestamp: str

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def message_stream(self) -> Message:
        for i in range(10):
            yield Message(
                content=f"Message {i}",
                timestamp=str(i)
            )
            await asyncio.sleep(1)

schema = strawberry.Schema(subscription=Subscription)
```

## 7. 数据加载器

### 7.1 批量加载

```python
from promise import Promise
from promise.dataloader import DataLoader

class UserLoader(DataLoader):
    def batch_load_fn(self, keys):
        users = get_users_by_ids(keys)
        user_dict = {user.id: user for user in users}
        return [user_dict.get(key) for key in keys]

user_loader = UserLoader()

class Query(graphene.ObjectType):
    user = graphene.Field(User, id=graphene.ID())
    
    def resolve_user(self, info, id):
        return user_loader.load(id)
```

## 8. 总结

GraphQL应用开发要点：
- **Graphene框架**：Schema定义、对象类型
- **查询和变更**：Query、Mutation
- **FastAPI集成**：Strawberry GraphQL
- **订阅**：实时数据推送
- **数据加载器**：批量加载优化

GraphQL提供灵活的API查询方式。

