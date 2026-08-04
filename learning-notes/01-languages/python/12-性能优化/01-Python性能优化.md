# Python性能优化
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 性能优化概述

Python性能优化可以从多个方面入手：
- **算法优化**：选择合适的数据结构和算法
- **代码优化**：避免不必要的计算和内存分配
- **并发优化**：使用多线程、多进程、异步编程
- **工具优化**：使用性能分析工具找出瓶颈

## 2. 算法和数据结构优化

### 2.1 选择合适的数据结构

```python
# 列表 vs 集合：查找操作
# 列表：O(n)
items_list = [1, 2, 3, 4, 5]
if 5 in items_list:  # O(n)
    pass

# 集合：O(1)
items_set = {1, 2, 3, 4, 5}
if 5 in items_set:  # O(1)
    pass

# 字典 vs 列表：键值对查找
# 字典：O(1)
data_dict = {'key': 'value'}
value = data_dict.get('key')

# 列表：需要遍历
data_list = [('key', 'value')]
for k, v in data_list:
    if k == 'key':
        value = v
        break
```

### 2.2 使用生成器

```python
# 不好的做法：创建完整列表
def get_numbers():
    return [i for i in range(1000000)]

# 好的做法：使用生成器
def get_numbers():
    for i in range(1000000):
        yield i

# 使用
for num in get_numbers():
    process(num)
```

### 2.3 列表推导式 vs 循环

```python
# 列表推导式通常更快
# 循环方式
result = []
for i in range(1000):
    if i % 2 == 0:
        result.append(i * 2)

# 列表推导式
result = [i * 2 for i in range(1000) if i % 2 == 0]
```

## 3. 代码优化技巧

### 3.1 避免重复计算

```python
# 不好的做法
for i in range(len(data)):
    result = expensive_function(data[i]) * len(data)

# 好的做法
length = len(data)
for i in range(length):
    result = expensive_function(data[i]) * length
```

### 3.2 使用局部变量

```python
# 局部变量访问更快
def process_data(data):
    # 将全局函数赋值给局部变量
    append = list.append
    result = []
    for item in data:
        append(result, process(item))
    return result
```

### 3.3 字符串拼接优化

```python
# 不好的做法：使用+拼接
result = ""
for item in items:
    result += item

# 好的做法：使用join
result = "".join(items)

# 或者使用列表
parts = []
for item in items:
    parts.append(item)
result = "".join(parts)
```

### 3.4 使用内置函数

```python
# 使用内置函数通常更快
# 不好的做法
total = 0
for num in numbers:
    total += num

# 好的做法
total = sum(numbers)

# 不好的做法
max_val = numbers[0]
for num in numbers:
    if num > max_val:
        max_val = num

# 好的做法
max_val = max(numbers)
```

## 4. 内存优化

### 4.1 使用__slots__

```python
# 普通类
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

# 使用__slots__减少内存占用
class Point:
    __slots__ = ['x', 'y']
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
```

### 4.2 及时释放大对象

```python
# 使用后及时删除
large_data = load_large_data()
process(large_data)
del large_data  # 释放内存
```

### 4.3 使用生成器表达式

```python
# 列表：占用内存
squares = [x**2 for x in range(1000000)]

# 生成器表达式：不占用内存
squares = (x**2 for x in range(1000000))
```

## 5. NumPy优化

### 5.1 向量化操作

```python
import numpy as np

# 不好的做法：循环
result = []
for i in range(len(array1)):
    result.append(array1[i] + array2[i])

# 好的做法：向量化
result = array1 + array2
```

### 5.2 避免Python循环

```python
import numpy as np

# 不好的做法
result = []
for x in array:
    result.append(np.sin(x))

# 好的做法
result = np.sin(array)
```

## 6. 并发优化

### 6.1 多线程（I/O密集型）

```python
from concurrent.futures import ThreadPoolExecutor
import requests

def fetch_url(url):
    return requests.get(url).text

urls = ['http://example.com'] * 100

# 串行
results = [fetch_url(url) for url in urls]

# 并行
with ThreadPoolExecutor(max_workers=10) as executor:
    results = list(executor.map(fetch_url, urls))
```

### 6.2 多进程（CPU密集型）

```python
from multiprocessing import Pool
import math

def compute(n):
    return sum(math.sqrt(i) for i in range(n))

numbers = [1000000] * 4

# 串行
results = [compute(n) for n in numbers]

# 并行
with Pool() as pool:
    results = pool.map(compute, numbers)
```

### 6.3 异步编程

```python
import asyncio
import aiohttp

async def fetch_url(session, url):
    async with session.get(url) as response:
        return await response.text()

async def main():
    urls = ['http://example.com'] * 100
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

asyncio.run(main())
```

## 7. 缓存优化

### 7.1 使用functools.lru_cache

```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_function(n):
    # 复杂计算
    return sum(i**2 for i in range(n))

# 第一次调用会计算
result1 = expensive_function(1000)

# 第二次调用直接返回缓存结果
result2 = expensive_function(1000)
```

### 7.2 使用functools.cache

```python
from functools import cache

@cache
def fibonacci(n):
    if n < 2:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
```

### 7.3 使用Redis缓存

```python
import redis
import json

r = redis.Redis(host='localhost', port=6379, db=0)

def get_data(key):
    # 先查缓存
    cached = r.get(key)
    if cached:
        return json.loads(cached)
    
    # 缓存未命中，查询数据库
    data = query_database(key)
    
    # 写入缓存
    r.setex(key, 3600, json.dumps(data))
    return data
```

## 8. 数据库优化

### 8.1 批量操作

```python
# 不好的做法：逐条插入
for item in items:
    db.execute("INSERT INTO table VALUES (?)", (item,))

# 好的做法：批量插入
db.executemany("INSERT INTO table VALUES (?)", items)
```

### 8.2 使用连接池

```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    'mysql+pymysql://user:pass@localhost/db',
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

### 8.3 使用索引

```python
# 确保数据库表有适当的索引
# CREATE INDEX idx_name ON table(column);
```

## 9. 性能分析工具

### 9.1 cProfile

```python
import cProfile
import pstats

def my_function():
    # 代码
    pass

profiler = cProfile.Profile()
profiler.enable()
my_function()
profiler.disable()

stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(10)  # 显示前10个最耗时的函数
```

### 9.2 line_profiler

```bash
pip install line_profiler
```

```python
@profile
def my_function():
    # 代码
    pass

# 运行：kernprof -l -v script.py
```

### 9.3 memory_profiler

```bash
pip install memory_profiler
```

```python
@profile
def my_function():
    # 代码
    pass

# 运行：python -m memory_profiler script.py
```

### 9.4 timeit

```python
import timeit

def test_function():
    # 代码
    pass

# 测量执行时间
time = timeit.timeit(test_function, number=1000)
print(f'平均时间: {time/1000}秒')
```

## 10. 编译优化

### 10.1 使用PyPy

```bash
# PyPy是Python的JIT实现，对某些代码有显著加速
pypy script.py
```

### 10.2 使用Cython

```python
# 将Python代码编译为C扩展
# setup.py
from setuptools import setup
from Cython.Build import cythonize

setup(
    ext_modules = cythonize("module.pyx")
)
```

### 10.3 使用Numba

```python
from numba import jit

@jit(nopython=True)
def fast_function(arr):
    total = 0
    for i in range(len(arr)):
        total += arr[i]
    return total
```

## 11. 最佳实践

1. **先测量再优化**：使用性能分析工具找出瓶颈
2. **算法优先**：选择合适的数据结构和算法
3. **避免过早优化**：先保证代码正确性
4. **使用内置函数**：内置函数通常经过优化
5. **合理使用缓存**：缓存可以显著提高性能
6. **并发优化**：根据任务类型选择合适的并发方式

## 12. 总结

Python性能优化需要综合考虑：
- **算法优化**：选择合适的数据结构和算法
- **代码优化**：避免不必要的计算
- **并发优化**：使用多线程、多进程、异步编程
- **工具优化**：使用性能分析工具找出瓶颈

合理的优化可以显著提高应用性能。



## 13. Python 3.14/3.15 性能新特性

> 🔄 更新于 2026-05-02

<!-- version-check: Python 3.14.4, Python 3.15 alpha JIT, Free-threaded build, checked 2026-05-02 -->

### 13.1 Free-threaded Python（无 GIL）

Python 3.14 是首个官方支持 Free-threaded 构建的版本（PEP 779）。移除 GIL 后，多线程可以真正并行执行 CPU 密集任务。来源：[Python Free-Threading Mode](https://www.nandann.com/blog/python-free-threading-2026)

```python
# 安装 free-threaded Python（使用 uv）
# uv python install 3.14t

import threading
import time

# 在 3.14t 中，这些线程真正并行执行
def cpu_intensive(n):
    """CPU 密集任务"""
    total = 0
    for i in range(n):
        total += i * i
    return total

start = time.perf_counter()
threads = []
for _ in range(4):
    t = threading.Thread(target=cpu_intensive, args=(10_000_000,))
    threads.append(t)
    t.start()
for t in threads:
    t.join()
elapsed = time.perf_counter() - start
# 3.14t: ~0.8s（4 核并行）
# 3.14 (GIL): ~3.2s（串行）
```

**Free-threaded 性能数据：**

| 指标 | Python 3.13 | Python 3.14 | Python 3.14t |
|------|------------|------------|-------------|
| 单线程开销 | 基准 | 基准 | +5~10% |
| 4 线程 CPU 密集 | ~1x（GIL 限制） | ~1x | ~3.5x |
| I/O 密集 | 基准 | 基准 | 基准（无差异） |

来源：[Free-threaded mode improvements](https://gdevops.frama.io/python/versions/3.14.0/free-threaded-mode-improvements/)

**适用场景：**
- ✅ CPU 密集型并行计算（图像处理、数据转换）
- ✅ 科学计算（NumPy/Pandas 已支持 free-threaded）
- ❌ 不适合替代 asyncio 的 I/O 密集场景
- ⚠️ 第三方库需要适配（检查 `pip install --config-settings=free-threaded=true`）

### 13.2 JIT 编译器演进

Python 的 JIT 编译器经历了曲折的发展。来源：[Python's JIT Is Finally Fast](https://mathewsachin.github.io/blog/2026/03/18/python-jit-finally-fast.html)

```
JIT 演进时间线：
├─ Python 3.13：实验性 copy-and-patch JIT（经常比标准解释器更慢）
├─ Python 3.14：tail-calling 解释器（Windows x86-64 有问题）
└─ Python 3.15 alpha：新 JIT 终于达标
   ├─ macOS AArch64：比 tail-calling 解释器快 11-12%
   ├─ x86_64 Linux：比标准解释器快 5-6%
   └─ 范围：从 -20% 到 +100%（取决于工作负载）
```

来源：[Python 3.15's JIT is now back on track](https://blog.python.org/2026/03/jit-on-track)

**2026 年 Python 运行时选择：**

| 运行时 | 适用场景 | 性能特点 |
|--------|---------|---------|
| CPython 3.14 | 通用开发 | 基准，稳定可靠 |
| CPython 3.14t | CPU 并行 | 多线程真正并行，单线程 +5-10% 开销 |
| CPython 3.15 alpha | 尝鲜 | JIT 带来 5-12% 提升 |
| PyPy 7.3 | 长时间运行 | 某些工作负载 5-10x 提升 |
| Cython 3.x | 热点函数 | 接近 C 性能 |
| Numba | 数值计算 | GPU 加速，NumPy 兼容 |

来源：[CPython vs. PyPy JIT comparison](https://www.infoworld.com/article/4117428/which-python-runtime-does-jit-better-cpython-or-pypy.html)

### 13.3 2026 年性能优化决策树

```
性能瓶颈在哪里？
├─ I/O 密集（网络/文件）
│  └─ asyncio + aiohttp/httpx（首选）
│     └─ 3.14t + ThreadPoolExecutor（混合场景）
├─ CPU 密集（计算）
│  ├─ 纯 Python 代码
│  │  ├─ 3.14t free-threaded（多核并行）
│  │  ├─ multiprocessing（传统方案）
│  │  └─ PyPy（长时间运行）
│  └─ 数值计算
│     ├─ NumPy/Pandas 向量化（首选）
│     ├─ Numba @jit（热点函数）
│     └─ Cython（极致性能）
└─ 内存瓶颈
   ├─ 生成器替代列表
   ├─ __slots__ 减少对象开销
   └─ Scalene 定位内存热点
```
