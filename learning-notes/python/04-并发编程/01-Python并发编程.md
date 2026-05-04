# Python并发编程
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 并发编程概述

并发编程是指在同一时间段内执行多个任务，Python提供了多种并发编程的方式：
- **多线程（threading）**：适合I/O密集型任务
- **多进程（multiprocessing）**：适合CPU密集型任务
- **异步编程（asyncio）**：适合高并发I/O操作

## 2. 多线程编程

### 2.1 线程基础

```python
import threading
import time

def worker(name):
    print(f'线程 {name} 开始执行')
    time.sleep(2)
    print(f'线程 {name} 执行完成')

# 创建线程
t1 = threading.Thread(target=worker, args=('A',))
t2 = threading.Thread(target=worker, args=('B',))

# 启动线程
t1.start()
t2.start()

# 等待线程完成
t1.join()
t2.join()
```

### 2.2 线程类

```python
class MyThread(threading.Thread):
    def __init__(self, name):
        super().__init__()
        self.name = name
    
    def run(self):
        print(f'线程 {self.name} 开始执行')
        time.sleep(2)
        print(f'线程 {self.name} 执行完成')

# 使用
t = MyThread('Worker')
t.start()
t.join()
```

### 2.3 线程同步

#### 锁（Lock）

```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100000):
        lock.acquire()
        counter += 1
        lock.release()

# 使用with语句
def increment_safe():
    global counter
    for _ in range(100000):
        with lock:
            counter += 1

t1 = threading.Thread(target=increment_safe)
t2 = threading.Thread(target=increment_safe)
t1.start()
t2.start()
t1.join()
t2.join()
print(f'Counter: {counter}')
```

#### 可重入锁（RLock）

```python
rlock = threading.RLock()

def recursive_function(count):
    with rlock:
        if count > 0:
            print(f'Count: {count}')
            recursive_function(count - 1)
```

#### 信号量（Semaphore）

```python
semaphore = threading.Semaphore(3)  # 最多3个线程同时执行

def worker():
    with semaphore:
        print(f'{threading.current_thread().name} 开始工作')
        time.sleep(2)
        print(f'{threading.current_thread().name} 完成工作')

for i in range(10):
    t = threading.Thread(target=worker)
    t.start()
```

#### 事件（Event）

```python
event = threading.Event()

def waiter():
    print('等待事件...')
    event.wait()
    print('事件已触发')

def setter():
    time.sleep(3)
    print('设置事件')
    event.set()

t1 = threading.Thread(target=waiter)
t2 = threading.Thread(target=setter)
t1.start()
t2.start()
```

#### 条件变量（Condition）

```python
condition = threading.Condition()
items = []

def consumer():
    with condition:
        while len(items) == 0:
            condition.wait()
        item = items.pop(0)
        print(f'消费: {item}')

def producer():
    with condition:
        items.append('item')
        condition.notify()

t1 = threading.Thread(target=consumer)
t2 = threading.Thread(target=producer)
t1.start()
t2.start()
```

### 2.4 线程池

```python
from concurrent.futures import ThreadPoolExecutor
import time

def task(n):
    print(f'任务 {n} 开始')
    time.sleep(1)
    return n * 2

# 使用线程池
with ThreadPoolExecutor(max_workers=3) as executor:
    futures = [executor.submit(task, i) for i in range(5)]
    results = [f.result() for f in futures]
    print(results)
```

### 2.5 线程本地存储

```python
thread_local = threading.local()

def worker():
    thread_local.value = threading.current_thread().name
    print(f'线程本地值: {thread_local.value}')

t1 = threading.Thread(target=worker)
t2 = threading.Thread(target=worker)
t1.start()
t2.start()
```

## 3. 多进程编程

### 3.1 进程基础

```python
import multiprocessing
import time

def worker(name):
    print(f'进程 {name} 开始执行')
    time.sleep(2)
    print(f'进程 {name} 执行完成')

if __name__ == '__main__':
    p1 = multiprocessing.Process(target=worker, args=('A',))
    p2 = multiprocessing.Process(target=worker, args=('B',))
    
    p1.start()
    p2.start()
    
    p1.join()
    p2.join()
```

### 3.2 进程间通信

#### 队列（Queue）

```python
from multiprocessing import Process, Queue

def producer(q):
    for i in range(5):
        q.put(i)
        print(f'生产: {i}')

def consumer(q):
    while True:
        item = q.get()
        if item is None:
            break
        print(f'消费: {item}')

if __name__ == '__main__':
    q = Queue()
    p1 = Process(target=producer, args=(q,))
    p2 = Process(target=consumer, args=(q,))
    
    p1.start()
    p2.start()
    
    p1.join()
    q.put(None)  # 结束信号
    p2.join()
```

#### 管道（Pipe）

```python
from multiprocessing import Process, Pipe

def sender(conn):
    conn.send('Hello')
    conn.close()

def receiver(conn):
    msg = conn.recv()
    print(f'收到: {msg}')
    conn.close()

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p1 = Process(target=sender, args=(child_conn,))
    p2 = Process(target=receiver, args=(parent_conn,))
    
    p1.start()
    p2.start()
    p1.join()
    p2.join()
```

#### 共享内存

```python
from multiprocessing import Process, Value, Array

def increment(n, arr):
    n.value += 1
    for i in range(len(arr)):
        arr[i] += 1

if __name__ == '__main__':
    num = Value('i', 0)
    arr = Array('i', [1, 2, 3])
    
    p1 = Process(target=increment, args=(num, arr))
    p2 = Process(target=increment, args=(num, arr))
    
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    
    print(f'Num: {num.value}')
    print(f'Arr: {list(arr)}')
```

### 3.3 进程池

```python
from multiprocessing import Pool
import time

def task(n):
    print(f'任务 {n} 开始')
    time.sleep(1)
    return n * 2

if __name__ == '__main__':
    with Pool(processes=3) as pool:
        results = pool.map(task, range(5))
        print(results)
```

### 3.4 进程锁

```python
from multiprocessing import Process, Lock

def worker(lock, counter):
    for _ in range(100000):
        with lock:
            counter.value += 1

if __name__ == '__main__':
    lock = Lock()
    counter = multiprocessing.Value('i', 0)
    
    p1 = Process(target=worker, args=(lock, counter))
    p2 = Process(target=worker, args=(lock, counter))
    
    p1.start()
    p2.start()
    p1.join()
    p2.join()
    
    print(f'Counter: {counter.value}')
```

## 4. 异步编程（asyncio）

### 4.1 协程基础

```python
import asyncio

async def hello():
    print('Hello')
    await asyncio.sleep(1)
    print('World')

# 运行协程
asyncio.run(hello())
```

### 4.2 并发执行

```python
import asyncio

async def task(name, delay):
    print(f'任务 {name} 开始')
    await asyncio.sleep(delay)
    print(f'任务 {name} 完成')
    return f'任务 {name} 结果'

async def main():
    # 并发执行多个任务
    results = await asyncio.gather(
        task('A', 2),
        task('B', 1),
        task('C', 3)
    )
    print(results)

asyncio.run(main())
```

### 4.3 任务管理

```python
import asyncio

async def long_task():
    await asyncio.sleep(5)
    return '完成'

async def main():
    # 创建任务
    task1 = asyncio.create_task(long_task())
    task2 = asyncio.create_task(long_task())
    
    # 等待任务完成
    results = await asyncio.gather(task1, task2)
    print(results)

asyncio.run(main())
```

### 4.4 异步锁

```python
import asyncio

async def worker(lock, name):
    async with lock:
        print(f'{name} 开始工作')
        await asyncio.sleep(1)
        print(f'{name} 完成工作')

async def main():
    lock = asyncio.Lock()
    await asyncio.gather(
        worker(lock, 'A'),
        worker(lock, 'B'),
        worker(lock, 'C')
    )

asyncio.run(main())
```

### 4.5 异步队列

```python
import asyncio

async def producer(queue):
    for i in range(5):
        await queue.put(i)
        print(f'生产: {i}')
        await asyncio.sleep(0.5)

async def consumer(queue):
    while True:
        item = await queue.get()
        if item is None:
            break
        print(f'消费: {item}')
        queue.task_done()

async def main():
    queue = asyncio.Queue()
    
    # 创建生产者和消费者
    prod = asyncio.create_task(producer(queue))
    cons = asyncio.create_task(consumer(queue))
    
    await prod
    await queue.put(None)  # 结束信号
    await cons

asyncio.run(main())
```

### 4.6 异步HTTP请求

```python
import asyncio
import aiohttp

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()

async def main():
    urls = [
        'https://www.example.com',
        'https://www.python.org',
        'https://www.github.com'
    ]
    
    tasks = [fetch(url) for url in urls]
    results = await asyncio.gather(*tasks)
    print(results)

asyncio.run(main())
```

## 5. 选择合适的方式

### 5.1 I/O密集型任务

适合使用**多线程**或**异步编程**：

```python
# 多线程方式
import threading
import requests

def fetch_url(url):
    response = requests.get(url)
    return response.status_code

threads = []
for url in urls:
    t = threading.Thread(target=fetch_url, args=(url,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

# 异步方式（更高效）
import asyncio
import aiohttp

async def fetch_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return response.status

async def main():
    tasks = [fetch_url(url) for url in urls]
    results = await asyncio.gather(*tasks)
    return results
```

### 5.2 CPU密集型任务

适合使用**多进程**：

```python
from multiprocessing import Pool

def cpu_intensive_task(n):
    result = 0
    for i in range(n):
        result += i ** 2
    return result

if __name__ == '__main__':
    with Pool() as pool:
        results = pool.map(cpu_intensive_task, [1000000] * 4)
```

## 6. 最佳实践

1. **避免全局解释器锁（GIL）的影响**：对于CPU密集型任务，使用多进程
2. **合理使用线程池和进程池**：避免创建过多线程/进程
3. **注意线程安全**：使用锁保护共享资源
4. **异步编程的优势**：对于高并发I/O操作，异步编程性能更好
5. **避免死锁**：注意锁的获取顺序

## 7. 总结

Python提供了多种并发编程方式：
- **多线程**：适合I/O密集型任务，但受GIL限制
- **多进程**：适合CPU密集型任务，可以充分利用多核CPU
- **异步编程**：适合高并发I/O操作，性能优异

选择合适的并发方式可以显著提高程序性能。
## 🎬 推荐视频资源

- [Corey Schafer - Threading Tutorial](https://www.youtube.com/watch?v=IEEhzQoKtQU) — Python多线程教程
- [Corey Schafer - Multiprocessing](https://www.youtube.com/watch?v=fKl2JW_qrso) — Python多进程教程
- [ArjanCodes - Async Python](https://www.youtube.com/watch?v=2IW-ZEui4h4) — Python异步编程

> 🔄 更新于 2026-05-04

<!-- version-check: Python 3.14.4 free-threaded, Python 3.15.0a8, checked 2026-05-04 -->

## 8. Free-threaded Python 3.14：GIL 的终结

Python 3.14（2025-10 发布）是 Free-threaded Python 进入 **Phase II（正式支持）** 的第一个版本（PEP 779）。这意味着无 GIL 构建不再是实验性的，而是官方支持的可选构建。

### 8.1 什么是 Free-threaded Python

Free-threaded Python 移除了全局解释器锁（GIL），使多线程可以真正并行执行 CPU 密集型任务。

```python
import sys
import threading
import time

# 检查当前是否运行在 Free-threaded 模式
print(f"GIL 是否启用: {sys._is_gil_enabled()}")
# Free-threaded 构建输出: False
# 标准构建输出: True
```

### 8.2 安装 Free-threaded Python

```bash
# macOS
brew install python-freethreading

# Linux (Ubuntu)
sudo apt-get install python3.14-nogil

# 使用 uv（推荐）
uv venv --python 3.14t

# conda-forge
conda create -n nogil -c conda-forge python-freethreading
```

### 8.3 真正的多线程并行

```python
import threading
import time

def cpu_intensive(n):
    """CPU 密集型任务：计算素数"""
    count = 0
    for i in range(2, n):
        if all(i % j != 0 for j in range(2, int(i**0.5) + 1)):
            count += 1
    return count

# 在标准 Python 中，多线程无法加速 CPU 密集任务（GIL 限制）
# 在 Free-threaded Python 3.14t 中，多线程可以真正并行

start = time.perf_counter()
threads = []
for _ in range(4):
    t = threading.Thread(target=cpu_intensive, args=(50000,))
    t.start()
    threads.append(t)
for t in threads:
    t.join()
elapsed = time.perf_counter() - start

print(f"4 线程耗时: {elapsed:.2f}s")
# Free-threaded: 接近线性加速（约 1/4 单线程时间）
# 标准 Python: 与单线程几乎相同（GIL 阻止并行）
```

### 8.4 性能代价与权衡

Free-threaded 模式有明确的性能代价：

| 指标 | 标准 Python 3.15 | Free-threaded 3.15 |
|------|------------------|---------------------|
| 单线程性能 | 基准 | 慢 6-9%（macOS ARM64 约 6%，Linux x86_64 约 9%） |
| 内存占用 | 基准 | 多 15-20%（PyObject 从 16 字节增至约 32 字节） |
| 多线程 CPU 密集 | 无加速（GIL） | 接近线性加速 |
| GC 机制 | 分代 GC（3 代） | 非分代 GC（单代 + stop-the-world 暂停） |
| 内存分配器 | pymalloc | mimalloc |

来源：[Meta free-threading-benchmarking](https://github.com/nicovank/free-threading-benchmarking)（pyperformance 基准，2026-04）

### 8.5 生态系统支持状态

| 包 | 首个支持版本 | 状态 |
|----|-------------|------|
| NumPy | 2.1.0 | ✅ 可用 |
| SciPy | 1.15.0 | ✅ 可用 |
| pandas | 2.2.3 | ✅ 可用 |
| PyTorch | 2.6.0 | ✅ 可用 |
| scikit-learn | 1.6.0 | ✅ 可用 |
| Cython | 3.1.0 | ✅ 关键依赖 |
| pydantic | 2.11.0 | ✅ 可用 |
| Pillow | 11.0.0 | ✅ 可用 |
| FastAPI | 0.136.0 | ✅ 可用 |
| OpenCV | — | ❌ 未发布 |
| grpcio | — | ❌ 未发布 |
| vLLM | — | 🔄 开发中 |

> ⚠️ 关键陷阱：导入一个不支持 Free-threaded 的 C 扩展会**静默重新启用 GIL**。你的程序可能在不知不觉中回到了 GIL 模式。使用 `sys._is_gil_enabled()` 验证。

来源：[Python Free-Threading Guide](https://py-free-threading.github.io/) | [Free-threading Compatibility Tracker](https://py-free-threading.github.io/tracking/)

### 8.6 数据竞争风险

GIL 的移除暴露了之前被掩盖的数据竞争 bug：

```python
import threading

# 在标准 Python 中，GIL 掩盖了这个竞争条件
# 在 Free-threaded Python 中，可能产生错误结果
shared_dict = {}

def writer(key, value):
    for _ in range(10000):
        shared_dict[key] = value  # 并发写入可能产生不一致

# 正确做法：使用锁保护共享可变状态
lock = threading.Lock()

def safe_writer(key, value):
    for _ in range(10000):
        with lock:
            shared_dict[key] = value
```

### 8.7 2026 年并发方案选型指南（更新版）

| 场景 | 标准 Python | Free-threaded Python 3.14t |
|------|------------|---------------------------|
| I/O 密集（网络、数据库） | asyncio + async/await | asyncio（Free-threaded 无额外收益） |
| CPU 密集 | multiprocessing | **threading**（真正并行，无进程开销） |
| 混合场景 | asyncio + ProcessPoolExecutor | asyncio + **ThreadPoolExecutor** |
| Web 框架 | FastAPI（async） | FastAPI（支持 3.14t，线程工作者真正并行） |
| 科学计算 | NumPy/SciPy + multiprocessing | NumPy/SciPy + **threading** |
| 新项目（5 年规划） | 标准构建 | 开始测试 Free-threaded 兼容性 |

### 8.8 迁移建议

**现在应该做的**：
- 在 CI 中添加 Free-threaded Python 测试（`uv venv --python 3.14t`）
- 审查共享可变状态，添加必要的锁
- 验证依赖树中所有 C 扩展的兼容性

**暂时不要做的**：
- 不要在生产环境部署 Free-threaded 构建
- 不要假设所有库都支持 Free-threaded 模式

**Phase III（Free-threaded 成为默认）** 目前没有 PEP 和时间表，现实估计在 2028-2029 年。

来源：[Python's Free-Threading Mode: Is It Time to Care?](https://www.nandann.com/blog/python-free-threading-2026)

## 9. Python 3.15 并发相关新特性预览

Python 3.15（当前 alpha 8，beta 1 预计 2026-05-05）引入了多项与并发相关的改进。

### 9.1 threading 新增并发安全迭代器

```python
import threading

# Python 3.15 新增：线程安全的迭代器工具
# serialize_iterator：序列化访问迭代器
# synchronized_iterator：同步迭代器
# concurrent_tee：并发安全的 tee

# 示例：多线程安全地消费同一个生成器
def data_generator():
    for i in range(100):
        yield i

gen = data_generator()
safe_iter = threading.serialize_iterator(gen)

def consumer(name, iterator):
    for item in iterator:
        print(f"{name}: {item}")

# 多个线程可以安全地从同一个迭代器消费
t1 = threading.Thread(target=consumer, args=("A", safe_iter))
t2 = threading.Thread(target=consumer, args=("B", safe_iter))
t1.start()
t2.start()
```

### 9.2 abi3t：Free-threaded 稳定 ABI

PEP 803 引入了 `abi3t`，为 Free-threaded 构建提供稳定 ABI。这意味着 C 扩展可以编译一次，在多个 Free-threaded Python 版本上运行，大幅降低了生态系统适配成本。

### 9.3 asyncio.TaskGroup.cancel

```python
import asyncio

async def search(query: str) -> str:
    await asyncio.sleep(1)
    return f"结果: {query}"

async def main():
    # Python 3.15 新增：TaskGroup.cancel() 支持提前终止
    async with asyncio.TaskGroup() as tg:
        task1 = tg.create_task(search("query1"))
        task2 = tg.create_task(search("query2"))

        # 当第一个结果满足条件时，取消整个 TaskGroup
        # 之前需要复杂的异常机制，现在一行搞定
        # tg.cancel()  # 取消所有未完成的任务

asyncio.run(main())
```

来源：[Python 3.15 What's New](https://docs.python.org/3.15/whatsnew/3.15.html)
