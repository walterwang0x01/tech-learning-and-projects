# NoSQL 数据库深入
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> Python NoSQL 数据库应用和最佳实践

<!-- version-check: pymongo 4.16.0, redis-py 5.x, cassandra-driver 3.x, elasticsearch-py 8.x, checked 2026-05-22 -->

> 💡 **MongoDB 异步驱动选择**（2026-05-22）：原 Motor 库已被 PyMongo 4.16+ 内置的 `AsyncMongoClient` 替代，Motor 将于 2026-05-14 EOL。本文示例使用同步 PyMongo API，异步用法请参见 `01-Python数据库操作.md` 第 12 节。

## 1. MongoDB 深入

### 1.1 聚合管道

```python
from pymongo import MongoClient
from bson import ObjectId

client = MongoClient('mongodb://localhost:27017/')
db = client['mydb']
collection = db['users']

# 聚合查询
pipeline = [
    {'$match': {'age': {'$gte': 18}}},
    {'$group': {
        '_id': '$city',
        'avg_age': {'$avg': '$age'},
        'count': {'$sum': 1}
    }},
    {'$sort': {'count': -1}},
    {'$limit': 10}
]

results = collection.aggregate(pipeline)
```

### 1.2 索引优化

```python
# 创建索引
collection.create_index([('username', 1)], unique=True)
collection.create_index([('email', 1)])
collection.create_index([('age', 1), ('city', 1)])  # 复合索引

# 查看索引
indexes = collection.list_indexes()
for index in indexes:
    print(index)

# 文本索引
collection.create_index([('description', 'text')])
```

### 1.3 事务处理

```python
from pymongo import MongoClient
from pymongo.errors import OperationFailure

client = MongoClient('mongodb://localhost:27017/')
db = client['mydb']

# 事务
with client.start_session() as session:
    with session.start_transaction():
        try:
            db.accounts.update_one(
                {'_id': 'account1'},
                {'$inc': {'balance': -100}},
                session=session
            )
            db.accounts.update_one(
                {'_id': 'account2'},
                {'$inc': {'balance': 100}},
                session=session
            )
            session.commit_transaction()
        except Exception as e:
            session.abort_transaction()
            raise
```

## 2. Redis 深入

### 2.1 数据结构应用

```python
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

# 字符串
r.set('key', 'value', ex=3600)  # 设置过期时间
value = r.get('key')

# 哈希
r.hset('user:1', mapping={'name': 'John', 'age': 30})
user = r.hgetall('user:1')

# 列表
r.lpush('tasks', 'task1', 'task2', 'task3')
task = r.rpop('tasks')

# 集合
r.sadd('tags', 'python', 'redis', 'database')
tags = r.smembers('tags')

# 有序集合
r.zadd('leaderboard', {'player1': 100, 'player2': 200})
top_players = r.zrevrange('leaderboard', 0, 9, withscores=True)
```

### 2.2 发布订阅

```python
import redis
import threading

# 发布者
def publisher():
    r = redis.Redis()
    for i in range(10):
        r.publish('channel', f'message {i}')

# 订阅者
def subscriber():
    r = redis.Redis()
    pubsub = r.pubsub()
    pubsub.subscribe('channel')
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            print(f"Received: {message['data']}")

# 运行
threading.Thread(target=subscriber).start()
threading.Thread(target=publisher).start()
```

### 2.3 Redis Streams

```python
# 生产者
r.xadd('stream', {'field1': 'value1', 'field2': 'value2'})

# 消费者组
r.xgroup_create('stream', 'mygroup', id='0', mkstream=True)

# 消费消息
messages = r.xreadgroup(
    'mygroup', 'consumer1',
    {'stream': '0'},
    count=10,
    block=1000
)
```

## 3. Cassandra 应用

### 3.1 连接和查询

```python
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

cluster = Cluster(['127.0.0.1'])
session = cluster.connect('mykeyspace')

# 插入数据
session.execute(
    "INSERT INTO users (id, name, email) VALUES (?, ?, ?)",
    (1, 'John', 'john@example.com')
)

# 查询数据
rows = session.execute("SELECT * FROM users WHERE id = %s", (1,))
for row in rows:
    print(row.name, row.email)
```

### 3.2 批量操作

```python
from cassandra.query import BatchStatement

batch = BatchStatement()
batch.add("INSERT INTO users (id, name) VALUES (?, ?)", (1, 'John'))
batch.add("INSERT INTO users (id, name) VALUES (?, ?)", (2, 'Jane'))
session.execute(batch)
```

## 4. Elasticsearch 应用

### 4.1 索引和搜索

```python
from elasticsearch import Elasticsearch

es = Elasticsearch(['localhost:9200'])

# 创建索引
es.indices.create(
    index='users',
    body={
        'mappings': {
            'properties': {
                'name': {'type': 'text'},
                'age': {'type': 'integer'},
                'email': {'type': 'keyword'}
            }
        }
    }
)

# 索引文档
es.index(
    index='users',
    id=1,
    body={'name': 'John', 'age': 30, 'email': 'john@example.com'}
)

# 搜索
result = es.search(
    index='users',
    body={
        'query': {
            'match': {'name': 'John'}
        }
    }
)
```

## 5. 总结

NoSQL数据库深入要点：
- **MongoDB深入**：聚合管道、索引优化、事务处理
- **Redis深入**：数据结构应用、发布订阅、Redis Streams
- **Cassandra应用**：连接查询、批量操作
- **Elasticsearch应用**：索引创建、文档索引、搜索查询

NoSQL数据库适用于不同场景的数据存储需求。

