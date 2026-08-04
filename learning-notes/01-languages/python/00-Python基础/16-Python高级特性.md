# Python高级特性
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 生成器（Generator）

生成器是一种特殊的迭代器，可以使用函数的方式来创建。生成器使用`yield`关键字返回值，每次调用`next()`时会执行到下一个`yield`语句。

### 1.1 生成器函数

```python
def fibonacci(n):
    """生成斐波那契数列"""
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# 使用生成器
for num in fibonacci(10):
    print(num)
```

### 1.2 生成器表达式

生成器表达式类似于列表推导式，但使用圆括号。

```python
# 列表推导式（立即生成所有元素）
squares_list = [x**2 for x in range(10)]

# 生成器表达式（按需生成元素）
squares_gen = (x**2 for x in range(10))
for square in squares_gen:
    print(square)
```

### 1.3 生成器的优势

1. **内存效率**：生成器按需生成元素，不需要一次性生成所有元素
2. **惰性求值**：只有在需要时才计算下一个值
3. **适合大数据**：处理大量数据时节省内存

## 2. 迭代器（Iterator）

迭代器是实现了迭代器协议的对象，可以使用`iter()`函数和`next()`函数进行操作。

### 2.1 迭代器协议

一个对象要实现迭代器协议，需要实现`__iter__()`和`__next__()`方法。

```python
class CountDown:
    """倒计时迭代器"""
    
    def __init__(self, start):
        self.current = start
    
    def __iter__(self):
        return self
    
    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        self.current -= 1
        return self.current + 1

# 使用迭代器
counter = CountDown(5)
for num in counter:
    print(num)  # 5, 4, 3, 2, 1
```

### 2.2 可迭代对象

实现了`__iter__()`方法的对象是可迭代对象，可以用于`for`循环。

```python
class MyRange:
    """自定义范围类"""
    
    def __init__(self, start, end):
        self.start = start
        self.end = end
    
    def __iter__(self):
        return iter(range(self.start, self.end))

# 使用可迭代对象
for num in MyRange(1, 5):
    print(num)  # 1, 2, 3, 4
```

## 3. 上下文管理器（Context Manager）

上下文管理器是实现了上下文管理器协议的对象，可以使用`with`语句。

### 3.1 __enter__和__exit__方法

```python
class FileManager:
    """文件管理器"""
    
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
        return False  # 不抑制异常

# 使用上下文管理器
with FileManager('test.txt', 'w') as f:
    f.write('Hello, World!')
```

### 3.2 contextlib模块

使用`contextlib.contextmanager`装饰器可以更方便地创建上下文管理器。

```python
from contextlib import contextmanager

@contextmanager
def file_manager(filename, mode):
    """文件管理器（使用contextmanager装饰器）"""
    file = open(filename, mode)
    try:
        yield file
    finally:
        file.close()

# 使用上下文管理器
with file_manager('test.txt', 'w') as f:
    f.write('Hello, World!')
```

## 4. 装饰器进阶

### 4.1 参数化装饰器

装饰器可以接受参数，返回一个装饰器函数。

```python
from functools import wraps
from time import time

def record(output):
    """可以参数化的装饰器"""
    
    def decorate(func):
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time()
            result = func(*args, **kwargs)
            output(func.__name__, time() - start)
            return result
            
        return wrapper
    
    return decorate

# 使用参数化装饰器
def log(name, elapsed):
    print(f'{name}执行了{elapsed:.2f}秒')

@record(log)
def my_function():
    pass
```

### 4.2 类装饰器

可以使用类来实现装饰器。

```python
from functools import wraps
from time import time

class Record:
    """通过定义类的方式定义装饰器"""

    def __init__(self, output):
        self.output = output

    def __call__(self, func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            start = time()
            result = func(*args, **kwargs)
            self.output(func.__name__, time() - start)
            return result

        return wrapper

@Record(log)
def my_function():
    pass
```

### 4.3 装饰器实现单例模式

```python
from functools import wraps

def singleton(cls):
    """装饰类的装饰器"""
    instances = {}

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper

@singleton
class President:
    """总统(单例类)"""
    pass
```

### 4.4 线程安全的单例装饰器

```python
from functools import wraps
from threading import RLock

def singleton(cls):
    """线程安全的单例装饰器"""
    instances = {}
    locker = RLock()

    @wraps(cls)
    def wrapper(*args, **kwargs):
        if cls not in instances:
            with locker:
                if cls not in instances:
                    instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return wrapper
```

## 5. 闭包（Closure）

闭包是指在一个函数内部定义的函数，它可以访问外部函数的变量。

### 5.1 闭包示例

```python
def outer_func(x):
    """外部函数"""
    
    def inner_func(y):
        """内部函数（闭包）"""
        return x + y
    
    return inner_func

# 创建闭包
closure = outer_func(10)
print(closure(5))  # 15
```

### 5.2 闭包的应用

```python
def make_multiplier(n):
    """创建一个乘法函数"""
    def multiplier(x):
        return x * n
    return multiplier

# 创建不同的乘法函数
double = make_multiplier(2)
triple = make_multiplier(3)

print(double(5))  # 10
print(triple(5))  # 15
```

## 6. 作用域和命名空间

### 6.1 LEGB规则

Python 搜索变量的顺序：
- **L**ocal（局部作用域）
- **E**nclosed（嵌套作用域）
- **G**lobal（全局作用域）
- **B**uilt-in（内置作用域）

### 6.2 global和nonlocal关键字

```python
x = 100  # 全局变量

def outer():
    y = 200  # 嵌套作用域变量
    
    def inner():
        global x
        nonlocal y
        x = 300  # 修改全局变量
        y = 400  # 修改嵌套作用域变量
    
    inner()
    print(y)  # 400

outer()
print(x)  # 300
```

## 7. 元类（Metaclass）

元类是创建类的类，Python 中一切都是对象，类也是对象。

### 7.1 使用type创建类

```python
# 使用type动态创建类
MyClass = type('MyClass', (object,), {'x': 100})

obj = MyClass()
print(obj.x)  # 100
```

### 7.2 自定义元类

```python
class MyMeta(type):
    """自定义元类"""
    
    def __new__(mcs, name, bases, namespace):
        namespace['created_by'] = 'MyMeta'
        return super().__new__(mcs, name, bases, namespace)

class MyClass(metaclass=MyMeta):
    pass

print(MyClass.created_by)  # MyMeta
```

## 8. 抽象基类（ABC）

抽象基类用于定义接口，不能直接实例化。

### 8.1 使用ABC定义抽象类

```python
from abc import ABCMeta, abstractmethod

class Employee(metaclass=ABCMeta):
    """员工(抽象类)"""

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def get_salary(self):
        """结算月薪(抽象方法)"""
        pass

class Manager(Employee):
    """部门经理"""

    def get_salary(self):
        return 15000.0

# employee = Employee('张三')  # TypeError: Can't instantiate abstract class
manager = Manager('李四')
print(manager.get_salary())  # 15000.0
```

## 9. 描述符（Descriptor）

描述符是一个实现了`__get__`、`__set__`或`__delete__`方法的类。

### 9.1 属性描述符

```python
class Descriptor:
    """属性描述符"""
    
    def __init__(self, name):
        self.name = name
    
    def __get__(self, instance, owner):
        print(f'Getting {self.name}')
        return instance.__dict__[self.name]
    
    def __set__(self, instance, value):
        print(f'Setting {self.name} to {value}')
        instance.__dict__[self.name] = value

class MyClass:
    x = Descriptor('x')
    y = Descriptor('y')

obj = MyClass()
obj.x = 100  # Setting x to 100
print(obj.x)  # Getting x, 100
```

## 10. 协程（Coroutine）

协程是一种轻量级的线程，可以在函数执行过程中暂停和恢复。

### 10.1 使用yield实现协程

```python
def coroutine():
    """简单的协程示例"""
    while True:
        value = yield
        print(f'Received: {value}')

# 创建协程
co = coroutine()
next(co)  # 启动协程
co.send('Hello')  # Received: Hello
co.send('World')  # Received: World
```

### 10.2 async/await（Python 3.5+）

```python
import asyncio

async def async_function():
    """异步函数"""
    print('开始执行')
    await asyncio.sleep(1)
    print('执行完成')

# 运行异步函数
asyncio.run(async_function())
```

## 11. 数据类（Dataclass，Python 3.7+）

数据类是一个装饰器，可以自动生成`__init__`、`__repr__`等方法。

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: float
    y: float
    
    def distance_to_origin(self):
        return (self.x**2 + self.y**2)**0.5

p = Point(3.0, 4.0)
print(p)  # Point(x=3.0, y=4.0)
print(p.distance_to_origin())  # 5.0
```

## 12. 类型提示（Type Hints）

Python 3.5+ 支持类型提示，提高代码可读性和IDE支持。

```python
from typing import List, Dict, Optional

def greet(name: str) -> str:
    """类型提示示例"""
    return f'Hello, {name}!'

def process_items(items: List[int]) -> Dict[str, int]:
    """处理列表并返回字典"""
    return {'count': len(items), 'sum': sum(items)}

def find_user(user_id: int) -> Optional[str]:
    """可能返回None的函数"""
    if user_id > 0:
        return f'User_{user_id}'
    return None
```

## 13. 枚举（Enum）

枚举用于定义常量集合。

```python
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

print(Color.RED)      # Color.RED
print(Color.RED.name) # RED
print(Color.RED.value) # 1
```

## 14. 总结

Python 提供了许多高级特性，包括生成器、迭代器、上下文管理器、装饰器、闭包、元类等。这些特性让 Python 代码更加优雅、高效和灵活。掌握这些高级特性可以帮助你写出更专业的 Python 代码。

> 🔄 更新于 2026-04-18

## 15. Python 3.14 新增高级特性

<!-- version-check: Python 3.14 t-strings, checked 2026-04-18 -->

### 15.1 模板字符串（t-strings，PEP 750）

Python 3.14 引入了 t-string（模板字符串），使用 `t` 前缀。与 f-string 不同，t-string 不会立即求值为字符串，而是返回一个 `Template` 对象，允许你在组装前拦截和处理插值。

```python
from string.templatelib import Template, Interpolation

# f-string：立即求值为 str
name = "Alice"
greeting_f = f"Hello, {name}!"  # "Hello, Alice!"

# t-string：返回 Template 对象
greeting_t = t"Hello, {name}!"  # Template 对象，包含字面量和插值

# Template 对象可以自定义处理
def html_escape(template: Template) -> str:
    """安全的 HTML 模板处理"""
    parts = []
    for item in template:
        if isinstance(item, Interpolation):
            # 对插值进行 HTML 转义
            import html
            parts.append(html.escape(str(item.value)))
        else:
            parts.append(item)
    return "".join(parts)

user_input = "<script>alert('xss')</script>"
safe_html = html_escape(t"<p>用户输入: {user_input}</p>")
# "<p>用户输入: &lt;script&gt;alert('xss')&lt;/script&gt;</p>"
```

**t-string 的典型应用场景**：
- **安全的 HTML 模板**：自动转义用户输入
- **SQL 查询构建**：防止 SQL 注入
- **国际化（i18n）**：延迟翻译处理
- **日志格式化**：结构化日志

### 15.2 延迟注解求值（PEP 649）

Python 3.14 默认启用延迟注解求值，不再需要 `from __future__ import annotations`：

```python
# Python 3.14 之前需要这行来支持前向引用
# from __future__ import annotations

# Python 3.14 默认延迟求值
class TreeNode:
    value: int
    left: "TreeNode | None" = None   # 前向引用自然工作
    right: "TreeNode | None" = None

# 运行时获取注解
import typing
hints = typing.get_type_hints(TreeNode)
```

### 15.3 Free-threaded Python（无 GIL）

Python 3.14 的 free-threaded 构建不再是实验性的，可以在生产环境中使用：

```python
import threading
import time

# 在 free-threaded Python 3.14t 中，这些线程真正并行执行
def cpu_intensive(n):
    """CPU 密集型任务"""
    total = 0
    for i in range(n):
        total += i * i
    return total

# 多线程真正利用多核
threads = []
for _ in range(4):
    t = threading.Thread(target=cpu_intensive, args=(10_000_000,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
# 在 3.14t 上，4 线程接近 4x 加速
# 在传统 Python 上，受 GIL 限制无法并行
```

> 来源：[Python 3.14 Release](https://iscinumpy.dev/post/python-314/)、[PEP 750 - Template Strings](https://peps.python.org/pep-0750/)、[Real Python - T-Strings](https://realpython.com/python-t-strings/)

## 16. Python 3.15 新增高级特性

> 🔄 更新于 2026-05-14

<!-- version-check: Python 3.15.0b1 feature freeze, checked 2026-05-14 -->

Python 3.15.0b1 于 2026-05-07 发布，标志着特性冻结。以下是对高级开发者最有影响的新特性。

### 16.1 显式惰性导入（PEP 810）

`import defer` 语法让模块在首次使用时才加载，显著加速应用启动时间：

```python
# 传统导入：应用启动时立即加载所有模块
import pandas as pd          # 立即加载（~200ms）
import matplotlib.pyplot as plt  # 立即加载（~150ms）

# PEP 810：显式惰性导入 — 首次使用时才加载
import defer pandas as pd
import defer matplotlib.pyplot as plt

# 此时 pandas 和 matplotlib 尚未加载
# 只有在实际使用时才触发导入
def analyze_data(data):
    df = pd.DataFrame(data)  # 此处触发 pandas 导入
    return df.describe()

# 适用场景：CLI 工具、大型应用、条件性使用的重量级库
# 效果：启动时间可减少 50-80%（取决于延迟导入的模块数量）
```

### 16.2 frozendict 内置类型（PEP 814）

不可变字典成为内置类型，无需第三方库：

```python
# 创建不可变字典
config = frozendict({"host": "localhost", "port": 8080, "debug": False})

# 可以读取
print(config["host"])  # "localhost"
print(config.get("port"))  # 8080

# 不可修改
# config["host"] = "remote"  # TypeError: 'frozendict' object does not support item assignment
# del config["debug"]        # TypeError

# 可以作为字典的 key（因为是 hashable 的）
cache = {config: "cached_result"}

# 创建修改后的副本
new_config = frozendict({**config, "debug": True})

# 适用场景：
# - 配置对象（防止意外修改）
# - 字典作为 set 元素或 dict key
# - 函数默认参数（替代 None 哨兵模式）
# - 多线程共享数据（天然线程安全）
```

### 16.3 sentinel 内置类型（PEP 661）

标准化的哨兵值，替代 `object()` 和 `None` 的滥用：

```python
from builtins import sentinel

# 创建命名哨兵
MISSING = sentinel("MISSING")
NOT_SET = sentinel("NOT_SET")

# 替代 None 作为"未提供"标记
def get_config(key: str, default=MISSING):
    value = _config.get(key, MISSING)
    if value is MISSING:
        if default is MISSING:
            raise KeyError(f"Config key '{key}' not found")
        return default
    return value

# 哨兵有清晰的 repr
print(MISSING)  # <MISSING>
print(NOT_SET)  # <NOT_SET>

# 类型注解友好
from typing import Union
def process(value: Union[str, type[MISSING]]) -> str: ...
```

### 16.4 推导式中的解包（PEP 798）

列表/集合/字典推导式中支持 `*` 和 `**` 解包：

```python
# 列表推导式中的 * 解包
nested = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
flat = [*sublist for sublist in nested]
# [1, 2, 3, 4, 5, 6, 7, 8, 9]

# 等价于（但更简洁）：
# flat = [item for sublist in nested for item in sublist]

# 字典推导式中的 ** 解包
configs = [{"a": 1}, {"b": 2}, {"c": 3}]
merged = {**d for d in configs}
# {"a": 1, "b": 2, "c": 3}

# 条件解包
data = [[1, 2], [], [3, 4, 5], []]
non_empty_flat = [*lst for lst in data if lst]
# [1, 2, 3, 4, 5]
```

### 16.5 JIT 编译器升级

Python 3.15 的 JIT 编译器实现了显著的性能提升：

```python
# JIT 性能提升数据（相比标准解释器）：
# - x86-64 Linux：几何平均 8-9% 提升
# - AArch64 macOS：12-13% 提升
# - Windows 64-bit：使用 tail-calling interpreter

# JIT 对以下场景效果最明显：
# - 紧密循环
# - 数值计算
# - 频繁调用的小函数

# 无需任何代码修改，升级到 3.15 即可自动获得性能提升
# JIT 默认启用，可通过环境变量控制：
# PYTHON_JIT=0 python3.15 script.py  # 禁用 JIT
```

### 16.6 UTF-8 默认编码（PEP 686）

Python 3.15 将 UTF-8 设为默认编码，不再依赖系统 locale：

```python
# Python 3.14 及之前：默认编码取决于系统 locale
# Windows 上可能是 cp1252、gbk 等
# 需要显式指定 encoding="utf-8"

# Python 3.15：UTF-8 成为默认
# open() 默认使用 UTF-8，无需显式指定
with open("data.txt") as f:  # 默认 UTF-8
    content = f.read()

# 如果需要其他编码，仍然可以显式指定
with open("legacy.txt", encoding="gbk") as f:
    content = f.read()

# 这消除了跨平台编码不一致的问题
# 不再需要 PYTHONUTF8=1 环境变量
```

> 来源：[Python 3.15.0 beta 1 发布公告](https://blog.python.org/2026/05/python-3150-beta-1/)、[PEP 810](https://peps.python.org/pep-0810/)、[PEP 814](https://peps.python.org/pep-0814/)

## 🎬 推荐视频资源

- [Corey Schafer - Generators](https://www.youtube.com/watch?v=bD05uGo_sVI) — 生成器详解
- [Corey Schafer - Context Managers](https://www.youtube.com/watch?v=-aKFBoZpiqA) — 上下文管理器
- [mCoding - Python Expert Tips](https://www.youtube.com/c/mCodingWithJamesMurphy) — Python高级技巧频道
