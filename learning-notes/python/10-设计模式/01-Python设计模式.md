# Python设计模式
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 设计模式概述

设计模式是解决特定问题的可重用解决方案。Python作为动态语言，实现设计模式的方式与静态语言有所不同，通常更加简洁和灵活。

## 2. 创建型模式

### 2.1 单例模式（Singleton）

确保一个类只有一个实例。

```python
class Singleton:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

# 使用装饰器实现
def singleton(cls):
    instances = {}
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return get_instance

@singleton
class Database:
    def __init__(self):
        print('数据库连接')

# 使用元类实现
class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]

class Logger(metaclass=SingletonMeta):
    def __init__(self):
        print('日志初始化')
```

### 2.2 工厂模式（Factory）

通过工厂类创建对象，而不是直接实例化。

```python
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow!"

class AnimalFactory:
    @staticmethod
    def create_animal(animal_type):
        if animal_type == "dog":
            return Dog()
        elif animal_type == "cat":
            return Cat()
        else:
            raise ValueError(f"Unknown animal type: {animal_type}")

# 使用
factory = AnimalFactory()
dog = factory.create_animal("dog")
print(dog.speak())
```

### 2.3 建造者模式（Builder）

逐步构建复杂对象。

```python
class Pizza:
    def __init__(self):
        self.size = None
        self.cheese = False
        self.pepperoni = False
        self.bacon = False
    
    def __str__(self):
        return f"Pizza(size={self.size}, cheese={self.cheese}, pepperoni={self.pepperoni}, bacon={self.bacon})"

class PizzaBuilder:
    def __init__(self):
        self.pizza = Pizza()
    
    def set_size(self, size):
        self.pizza.size = size
        return self
    
    def add_cheese(self):
        self.pizza.cheese = True
        return self
    
    def add_pepperoni(self):
        self.pizza.pepperoni = True
        return self
    
    def add_bacon(self):
        self.pizza.bacon = True
        return self
    
    def build(self):
        return self.pizza

# 使用
pizza = PizzaBuilder().set_size("large").add_cheese().add_pepperoni().build()
print(pizza)
```

### 2.4 原型模式（Prototype）

通过克隆现有对象来创建新对象。

```python
import copy

class Prototype:
    def clone(self):
        return copy.deepcopy(self)

class Document(Prototype):
    def __init__(self, content):
        self.content = content
    
    def clone(self):
        return copy.deepcopy(self)

# 使用
original = Document("原始文档")
copy_doc = original.clone()
copy_doc.content = "复制的文档"
```

## 3. 结构型模式

### 3.1 适配器模式（Adapter）

使不兼容的接口能够协同工作。

```python
class OldSystem:
    def old_method(self):
        return "旧系统方法"

class NewSystem:
    def new_method(self):
        return "新系统方法"

class Adapter:
    def __init__(self, system):
        self.system = system
    
    def request(self):
        if isinstance(self.system, OldSystem):
            return self.system.old_method()
        elif isinstance(self.system, NewSystem):
            return self.system.new_method()

# 使用
old = OldSystem()
adapter = Adapter(old)
print(adapter.request())
```

### 3.2 装饰器模式（Decorator）

动态地给对象添加新功能。

```python
class Component:
    def operation(self):
        return "组件操作"

class Decorator(Component):
    def __init__(self, component):
        self.component = component
    
    def operation(self):
        return self.component.operation()

class ConcreteDecoratorA(Decorator):
    def operation(self):
        return f"装饰器A({self.component.operation()})"

class ConcreteDecoratorB(Decorator):
    def operation(self):
        return f"装饰器B({self.component.operation()})"

# 使用
component = Component()
decorated = ConcreteDecoratorA(ConcreteDecoratorB(component))
print(decorated.operation())
```

### 3.3 外观模式（Facade）

为复杂子系统提供简单接口。

```python
class CPU:
    def start(self):
        return "CPU启动"

class Memory:
    def load(self):
        return "内存加载"

class HardDrive:
    def read(self):
        return "硬盘读取"

class ComputerFacade:
    def __init__(self):
        self.cpu = CPU()
        self.memory = Memory()
        self.hard_drive = HardDrive()
    
    def start_computer(self):
        results = []
        results.append(self.cpu.start())
        results.append(self.memory.load())
        results.append(self.hard_drive.read())
        return " | ".join(results)

# 使用
computer = ComputerFacade()
print(computer.start_computer())
```

### 3.4 代理模式（Proxy）

为其他对象提供代理以控制访问。

```python
class Subject:
    def request(self):
        pass

class RealSubject(Subject):
    def request(self):
        return "真实对象请求"

class Proxy(Subject):
    def __init__(self):
        self._real_subject = None
    
    def request(self):
        if self._real_subject is None:
            self._real_subject = RealSubject()
        return f"代理: {self._real_subject.request()}"

# 使用
proxy = Proxy()
print(proxy.request())
```

## 4. 行为型模式

### 4.1 观察者模式（Observer）

定义对象间一对多的依赖关系。

```python
class Observer:
    def update(self, message):
        pass

class Subject:
    def __init__(self):
        self._observers = []
    
    def attach(self, observer):
        self._observers.append(observer)
    
    def detach(self, observer):
        self._observers.remove(observer)
    
    def notify(self, message):
        for observer in self._observers:
            observer.update(message)

class ConcreteObserver(Observer):
    def __init__(self, name):
        self.name = name
    
    def update(self, message):
        print(f"{self.name} 收到消息: {message}")

# 使用
subject = Subject()
observer1 = ConcreteObserver("观察者1")
observer2 = ConcreteObserver("观察者2")

subject.attach(observer1)
subject.attach(observer2)
subject.notify("状态更新")
```

### 4.2 策略模式（Strategy）

定义一系列算法，使它们可以互换。

```python
class Strategy:
    def execute(self, data):
        pass

class QuickSort(Strategy):
    def execute(self, data):
        return sorted(data)

class BubbleSort(Strategy):
    def execute(self, data):
        data = data.copy()
        n = len(data)
        for i in range(n):
            for j in range(0, n - i - 1):
                if data[j] > data[j + 1]:
                    data[j], data[j + 1] = data[j + 1], data[j]
        return data

class Context:
    def __init__(self, strategy):
        self.strategy = strategy
    
    def execute_strategy(self, data):
        return self.strategy.execute(data)

# 使用
data = [3, 1, 4, 1, 5, 9, 2, 6]
context = Context(QuickSort())
print(context.execute_strategy(data))
```

### 4.3 命令模式（Command）

将请求封装为对象。

```python
class Command:
    def execute(self):
        pass

class Light:
    def on(self):
        return "灯打开"
    
    def off(self):
        return "灯关闭"

class LightOnCommand(Command):
    def __init__(self, light):
        self.light = light
    
    def execute(self):
        return self.light.on()

class LightOffCommand(Command):
    def __init__(self, light):
        self.light = light
    
    def execute(self):
        return self.light.off()

class RemoteControl:
    def __init__(self):
        self.command = None
    
    def set_command(self, command):
        self.command = command
    
    def press_button(self):
        return self.command.execute()

# 使用
light = Light()
light_on = LightOnCommand(light)
remote = RemoteControl()
remote.set_command(light_on)
print(remote.press_button())
```

### 4.4 责任链模式（Chain of Responsibility）

将请求沿着处理者链传递。

```python
class Handler:
    def __init__(self):
        self._next = None
    
    def set_next(self, handler):
        self._next = handler
        return handler
    
    def handle(self, request):
        if self._next:
            return self._next.handle(request)
        return None

class ConcreteHandler1(Handler):
    def handle(self, request):
        if request == "请求1":
            return "处理者1处理了请求"
        return super().handle(request)

class ConcreteHandler2(Handler):
    def handle(self, request):
        if request == "请求2":
            return "处理者2处理了请求"
        return super().handle(request)

# 使用
handler1 = ConcreteHandler1()
handler2 = ConcreteHandler2()
handler1.set_next(handler2)

print(handler1.handle("请求1"))
print(handler1.handle("请求2"))
```

### 4.5 状态模式（State）

允许对象在内部状态改变时改变行为。

```python
class State:
    def handle(self, context):
        pass

class ConcreteStateA(State):
    def handle(self, context):
        print("状态A处理")
        context.state = ConcreteStateB()

class ConcreteStateB(State):
    def handle(self, context):
        print("状态B处理")
        context.state = ConcreteStateA()

class Context:
    def __init__(self):
        self.state = ConcreteStateA()
    
    def request(self):
        self.state.handle(self)

# 使用
context = Context()
context.request()
context.request()
```

### 4.6 模板方法模式（Template Method）

定义算法骨架，子类实现具体步骤。

```python
class AbstractClass:
    def template_method(self):
        self.step1()
        self.step2()
        self.step3()
    
    def step1(self):
        pass
    
    def step2(self):
        pass
    
    def step3(self):
        pass

class ConcreteClass(AbstractClass):
    def step1(self):
        print("步骤1")
    
    def step2(self):
        print("步骤2")
    
    def step3(self):
        print("步骤3")

# 使用
concrete = ConcreteClass()
concrete.template_method()
```

## 5. Python特有的模式

### 5.1 上下文管理器模式

```python
class FileManager:
    def __init__(self, filename, mode):
        self.filename = filename
        self.mode = mode
        self.file = None
    
    def __enter__(self):
        self.file = open(self.filename, self.mode)
        return self.file
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.file:
            self.file.close()
        return False

# 使用
with FileManager('test.txt', 'w') as f:
    f.write('Hello, World!')
```

### 5.2 描述符模式

```python
class Descriptor:
    def __init__(self, name):
        self.name = name
    
    def __get__(self, instance, owner):
        return instance.__dict__[self.name]
    
    def __set__(self, instance, value):
        if value < 0:
            raise ValueError("值不能为负数")
        instance.__dict__[self.name] = value

class MyClass:
    value = Descriptor('value')
    
    def __init__(self, value):
        self.value = value

# 使用
obj = MyClass(10)
print(obj.value)
```

## 6. 最佳实践

1. **优先使用Python特性**：利用Python的动态特性简化设计模式
2. **避免过度设计**：简单问题不需要复杂模式
3. **理解模式本质**：理解模式解决的问题，而不是机械套用
4. **组合使用**：多个模式可以组合使用

## 7. 总结

设计模式提供了解决常见问题的模板，但在Python中实现通常更加简洁。理解模式的核心思想比记住具体实现更重要。


## 8. Python 3.14 / 3.15 设计模式新范式

> 🔄 更新于 2026-05-09
>
> <!-- version-check: Python 3.14.4 / 3.15 alpha 8, checked 2026-05-09 -->

Python 3.14 和 3.15 带来了多项新特性，让若干经典设计模式拥有了更 Pythonic 的现代实现。本节聚焦这些模式的 "2026 写法"。

### 8.1 Protocol + dataclass：结构化鸭子类型（替代抽象基类）

传统 Python 的策略模式、命令模式依赖 `abc.ABC + @abstractmethod`。Python 3.8 引入的 `typing.Protocol` 让 "按形状匹配" 成为一等公民，3.14 的 `runtime_checkable` 与 `@dataclass` 组合是更现代的写法。

```python
# 2026 年推荐：Protocol 替代 ABC 定义策略接口
from typing import Protocol, runtime_checkable
from dataclasses import dataclass

@runtime_checkable
class PaymentStrategy(Protocol):
    """支付策略协议（结构化接口，无需继承）"""
    def pay(self, amount: float) -> bool: ...


@dataclass(slots=True, frozen=True)
class AlipayStrategy:
    account: str

    def pay(self, amount: float) -> bool:
        # 不需要 extends/implements，只要方法签名匹配即可
        print(f"支付宝 {self.account} 支付 {amount}")
        return True


@dataclass(slots=True, frozen=True)
class WeChatStrategy:
    openid: str

    def pay(self, amount: float) -> bool:
        print(f"微信 {self.openid} 支付 {amount}")
        return True


def checkout(strategy: PaymentStrategy, amount: float) -> bool:
    # isinstance 检查 Protocol（runtime_checkable 支持）
    assert isinstance(strategy, PaymentStrategy)
    return strategy.pay(amount)


checkout(AlipayStrategy("user@example.com"), 100.0)
checkout(WeChatStrategy("ox_123"), 50.0)
```

**优势**：

- `slots=True` 减少内存占用（~40%）
- `frozen=True` 天然实现值对象的不可变性
- `Protocol` 无侵入：第三方类只要结构匹配就能注入，无需修改源码继承

来源：[TheLinuxCode - Dataclass vs Namedtuple vs Object 2026 Guidance](https://thelinuxcode.com/dataclass-vs-namedtuple-vs-object-in-python-practical-differences-trade-offs-and-2026-guidance/)

### 8.2 异步上下文管理器：现代资源管理模式

单例、资源池等需要生命周期管理的模式，在 asyncio 场景下应优先使用 `async with` + `@asynccontextmanager`：

```python
# 2026 年推荐：asynccontextmanager 替代自写 __aenter__ / __aexit__
from contextlib import asynccontextmanager
import httpx


@asynccontextmanager
async def http_client_pool(base_url: str):
    """可复用的异步 HTTP 客户端池（资源池模式）"""
    client = httpx.AsyncClient(base_url=base_url, timeout=10.0)
    try:
        yield client
    finally:
        # 异步资源清理，保证在取消/异常/超时下也会执行
        await client.aclose()


async def fetch_user(user_id: str):
    async with http_client_pool("https://api.example.com") as client:
        resp = await client.get(f"/users/{user_id}")
        return resp.json()
```

**关键洞察**：`async with` 在协程被取消时仍保证 `finally` 执行，而自写的 `try/finally` 在 `await` 处被取消时可能跳过 finally（具体取决于 asyncio 版本）。

来源：[Async context management for Python AI services](https://www.learnwithparam.com/blog/async-context-management-python-ai-services)

### 8.3 TaskGroup：结构化并发替代手动 gather（Python 3.11+）

传统的"主从模式（Master-Worker）"在 Python 中常用 `asyncio.gather` 实现，但异常处理和资源清理不直观。`asyncio.TaskGroup`（Python 3.11+）是结构化并发的标准写法：

```python
# 2026 年推荐：TaskGroup 替代 gather 的主从模式
import asyncio


async def fetch(url: str) -> dict:
    await asyncio.sleep(0.1)  # 模拟网络请求
    return {"url": url, "data": "..."}


async def aggregate_master(urls: list[str]) -> list[dict]:
    """结构化并发的主节点：所有子任务共享一个 TaskGroup 作用域"""
    results: list[dict] = []

    # TaskGroup 保证：任一子任务抛异常 → 所有兄弟任务自动取消
    async with asyncio.TaskGroup() as tg:
        tasks = [tg.create_task(fetch(url)) for url in urls]

    # 退出上下文后所有任务已完成，直接取 .result()
    results = [t.result() for t in tasks]
    return results


# Python 3.15 新增：TaskGroup.cancel() 支持外部取消整个组
async def aggregate_with_timeout(urls: list[str], timeout: float):
    async with asyncio.timeout(timeout):
        return await aggregate_master(urls)
```

**对比 gather**：

| 维度 | `asyncio.gather` | `TaskGroup` |
| ---- | ---------------- | ----------- |
| 异常传播 | 首个异常之后的结果被丢弃，其余任务不一定被取消 | 自动取消兄弟任务 + `ExceptionGroup` 聚合 |
| 作用域清晰性 | 需手动 try/except | `async with` 天然划定边界 |
| Python 版本 | 3.0+ | 3.11+（3.15 新增 `.cancel()`） |

来源：[Python asyncio Patterns 2026](https://techbytes.app/posts/python-asyncio-patterns-2026-complete-reference/)

### 8.4 frozendict + sentinel：替代"魔数默认值"模式

Python 3.15 alpha 引入了内置 `frozendict`（PEP 814）和 `sentinel` 类型（PEP 661），让单例模式、空对象模式、备忘录模式有更优写法：

```python
# Python 3.15：frozendict 作为配置的不可变默认值
from frozendict import frozendict  # Python 3.15 内置；3.14 使用 pip install frozendict

DEFAULT_CONFIG = frozendict(
    timeout=30,
    retries=3,
    backoff=1.5,
)


def call_api(url: str, config: frozendict = DEFAULT_CONFIG):
    # 默认值可以直接是 frozendict，无需 copy.deepcopy 防污染
    effective = frozendict({**config, "url": url})
    return effective


# Python 3.15：sentinel 用于区分 "未提供" 和 "None"
from sentinel import Sentinel  # Python 3.15 内置

_MISSING = Sentinel("_MISSING")


def get_value(key: str, default=_MISSING):
    value = lookup(key)
    if value is None:
        if default is _MISSING:
            raise KeyError(key)  # "未提供默认值" → 抛异常
        return default            # "显式提供了 None 或其他值" → 返回之
    return value
```

**模式定位**：这两个特性解决了 "Python 历史上用 `object()` 做哨兵 + 只读字典不存在" 的问题，让空对象模式、默认值模式代码更简洁。

来源：[Python 3.15 What's New](https://docs.python.org/3.15/whatsnew/3.15.html)

### 8.5 Free-threaded Python 下的模式变化

Python 3.14 的 Free-threaded 构建让 "生产者-消费者"、"主从模式" 等并发模式可以使用真正的多线程实现。但需要注意：

- **单例模式要加锁**：Free-threaded 下 `__new__` 不再天然线程安全，必须显式 `threading.Lock`
- **观察者模式注意竞态**：listener 列表修改必须用锁保护或使用 `queue.Queue` 中转
- **工厂模式更安全**：无共享状态的工厂方法天然线程安全，是 Free-threaded 首选

```python
# Free-threaded 安全的单例模式
import threading
import sys


class Singleton:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        # 双检锁（Double-checked locking）
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance


# 检测是否运行在 Free-threaded 模式
if hasattr(sys, "_is_gil_enabled"):
    print(f"GIL enabled: {sys._is_gil_enabled()}")
    # False → Free-threaded build (python3.14t)
```

来源：[Python Free-Threading Guide](https://py-free-threading.github.io/)

### 8.6 2026 年 Python 设计模式工具箱

| 经典模式 | 2026 推荐实现 | 替代原因 |
| -------- | ------------ | -------- |
| 策略模式 | `Protocol` + `@dataclass(slots=True)` | 无侵入 + 内存友好 |
| 命令模式 | `dataclass` + dispatcher 函数 / `match` 语句 | 比类继承更轻量 |
| 观察者模式 | `asyncio.Queue` / `dispatcher` 库 | 天然处理异步与并发 |
| 单例模式 | 模块级变量 + `functools.cache` | 模块天然单例，无需特殊实现 |
| 空对象模式 | `Sentinel` 类型（3.15+）或 `typing.Never` | 类型安全 |
| 资源池 / 工厂 | `@asynccontextmanager` + Protocol 工厂 | 统一异步资源生命周期 |
| 主从模式 | `asyncio.TaskGroup`（3.11+） | 结构化并发 + 自动异常处理 |
| 备忘录模式 | `frozendict`（3.15+）+ `functools.cache` | 不可变键天然可哈希 |

---

**参考链接**：

- [Python 3.14.4 Documentation - dataclasses](https://docs.python.org/3/library/dataclasses.html)
- [Python 3.15 What's New](https://docs.python.org/3.15/whatsnew/3.15.html)
- [contextlib — Utilities for with-statement contexts](https://docs.python.org/3/library/contextlib.html)
- [Python Free-Threading Guide](https://py-free-threading.github.io/)
- [TheLinuxCode - Dataclass 2026 Guidance](https://thelinuxcode.com/dataclass-vs-namedtuple-vs-object-in-python-practical-differences-trade-offs-and-2026-guidance/)

> 内容经改写总结，不直接逐字摘录官方文档与博客。
