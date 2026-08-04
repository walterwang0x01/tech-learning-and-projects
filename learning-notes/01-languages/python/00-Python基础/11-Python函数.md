# Python函数
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 函数概述

在编程语言中，函数是一段可重复使用的代码块，它接受输入（参数），执行特定的操作，并返回结果。Python 中可以使用`def`关键字来定义函数。

## 2. 定义函数

### 2.1 基本语法

```python
def function_name(parameters):
    """函数的文档字符串"""
    # 函数体
    return value
```

### 2.2 简单示例

```python
"""
输入m和n，计算组合数C(m,n)的值

Version: 1.1
Author: 骆昊
"""
def fac(num):
    """求阶乘"""
    result = 1
    for n in range(2, num + 1):
        result *= n
    return result

m = int(input('m = '))
n = int(input('n = '))
print(fac(m) // fac(n) // fac(m - n))
```

**说明**：
- 函数名命名规则跟变量命名规则相同
- 函数名后面的圆括号中可以设置函数的参数
- 函数执行完成后，通过`return`关键字来返回函数的执行结果
- 如果函数中没有`return`语句，那么函数会返回代表空值的`None`

## 3. 函数的参数

### 3.1 位置参数

位置参数是最常见的参数类型，在调用函数时通常按照从左到右的顺序依次传入。

```python
def make_judgement(a, b, c):
    """判断三条边的长度能否构成三角形"""
    return a + b > c and b + c > a and a + c > b

print(make_judgement(1, 2, 3))  # False
print(make_judgement(4, 5, 6))  # True
```

### 3.2 关键字参数

如果不想按照从左到右的顺序依次给出参数的值，也可以使用关键字参数，通过"参数名=参数值"的形式为函数传入参数。

```python
print(make_judgement(b=2, c=3, a=1))  # False
print(make_judgement(c=6, b=4, a=5))  # True
```

### 3.3 强制位置参数（Python 3.8+）

在定义函数时，可以在参数列表中用`/`设置**强制位置参数**（positional-only arguments），调用函数时只能按照参数位置来接收参数值。

```python
# /前面的参数是强制位置参数
def make_judgement(a, b, c, /):
    """判断三条边的长度能否构成三角形"""
    return a + b > c and b + c > a and a + c > b

# 下面的代码会产生TypeError错误
# print(make_judgement(b=2, c=3, a=1))  # TypeError
```

### 3.4 命名关键字参数

在参数列表中用`*`设置**命名关键字参数**，命名关键字参数只能通过"参数名=参数值"的方式来传递和接收参数。

```python
# *后面的参数是命名关键字参数
def make_judgement(*, a, b, c):
    """判断三条边的长度能否构成三角形"""
    return a + b > c and b + c > a and a + c > b

# 下面的代码会产生TypeError错误
# print(make_judgement(1, 2, 3))  # TypeError
```

### 3.5 参数的默认值

Python 中允许函数的参数拥有默认值。

```python
from random import randrange

def roll_dice(n=2):
    """摇色子的函数"""
    total = 0
    for _ in range(n):
        total += randrange(1, 7)
    return total

# 如果没有指定参数，那么n使用默认值2
print(roll_dice())
# 传入参数3，变量n被赋值为3
print(roll_dice(3))
```

**注意**：**带默认值的参数必须放在不带默认值的参数之后**，否则将产生`SyntaxError`错误。

```python
def add(a=0, b=0, c=0):
    """三个数相加求和"""
    return a + b + c

print(add())         # 0
print(add(1))        # 1
print(add(1, 2))     # 3
print(add(1, 2, 3))  # 6
```

### 3.6 可变参数

Python 语言中可以通过星号表达式语法让函数支持可变参数。

#### 可变位置参数（*args）

```python
def add(*args):
    """对任意多个数求和"""
    total = 0
    for val in args:
        if type(val) in (int, float):
            total += val
    return total

print(add())                    # 0
print(add(1))                   # 1
print(add(1, 2, 3))             # 6
print(add(1, 2, 'hello', 3.45, 6))  # 12.45
```

**说明**：
- `*args`可以接收0个或任意多个位置参数
- 调用函数时传入的参数会保存到一个元组

#### 可变关键字参数（**kwargs）

```python
def foo(*args, **kwargs):
    """演示可变位置参数和可变关键字参数"""
    print(args)
    print(kwargs)

foo(3, 2.1, True, name='骆昊', age=43, gpa=4.95)
```

输出：
```
(3, 2.1, True)
{'name': '骆昊', 'age': 43, 'gpa': 4.95}
```

**说明**：
- `**kwargs`可以接收0个或任意多个关键字参数
- 调用函数时传入的关键字参数会组装成一个字典

## 4. 用模块管理函数

### 4.1 命名冲突问题

如果项目是团队协作多人开发的时候，团队中可能有多个程序员都定义了同名函数，这种情况下怎么解决命名冲突呢？答案是通过模块。

### 4.2 导入模块

```python
# 导入整个模块
import module1
import module2

module1.foo()  # hello, world!
module2.foo()  # goodbye, world!
```

### 4.3 导入特定函数

```python
# 从模块导入特定函数
from module1 import foo
from module2 import foo as foo2

foo()   # hello, world!
foo2()  # goodbye, world!
```

### 4.4 使用别名

```python
# 导入函数并使用别名
from math import factorial as f

print(f(5))  # 120
```

## 5. 高阶函数

Python 中的函数是"一等函数"，所谓"一等函数"指的就是函数可以赋值给变量，函数可以作为函数的参数，函数也可以作为函数的返回值。

### 5.1 函数作为参数

```python
def calc(init_value, op_func, *args, **kwargs):
    """高阶函数示例"""
    items = list(args) + list(kwargs.values())
    result = init_value
    for item in items:
        if type(item) in (int, float):
            result = op_func(result, item)
    return result

def add(x, y):
    return x + y

def mul(x, y):
    return x * y

print(calc(0, add, 1, 2, 3, 4, 5))  # 15
print(calc(1, mul, 1, 2, 3, 4, 5))  # 120
```

### 5.2 内置高阶函数

#### filter函数

`filter`函数可以实现对序列中元素的过滤。

```python
def is_even(num):
    """判断num是不是偶数"""
    return num % 2 == 0

old_nums = [35, 12, 8, 99, 60, 52]
new_nums = list(filter(is_even, old_nums))
print(new_nums)  # [12, 8, 60, 52]
```

#### map函数

`map`函数可以实现对序列中元素的映射。

```python
def square(num):
    """求平方"""
    return num ** 2

old_nums = [35, 12, 8, 99, 60, 52]
new_nums = list(map(square, old_nums))
print(new_nums)  # [1225, 144, 64, 9801, 3600, 2704]
```

#### sorted函数

`sorted`函数可以自定义排序规则。

```python
old_strings = ['in', 'apple', 'zoo', 'waxberry', 'pear']
# 按字母表顺序排序
new_strings = sorted(old_strings)
print(new_strings)  # ['apple', 'in', 'pear', 'waxberry', 'zoo']

# 按字符串长度排序
new_strings = sorted(old_strings, key=len)
print(new_strings)  # ['in', 'zoo', 'pear', 'apple', 'waxberry']
```

## 6. Lambda函数

Lambda 函数是没有名字的函数，所以很多人也把它叫做**匿名函数**。Lambda 函数只能有一行代码，代码中的表达式产生的运算结果就是这个匿名函数的返回值。

### 6.1 基本语法

```python
lambda parameters: expression
```

### 6.2 使用示例

```python
old_nums = [35, 12, 8, 99, 60, 52]
new_nums = list(map(lambda x: x ** 2, filter(lambda x: x % 2 == 0, old_nums)))
print(new_nums)  # [144, 64, 3600, 2704]
```

### 6.3 Lambda函数赋值

Lambda 函数也可以赋值给变量。

```python
import functools
import operator

# 用一行代码实现计算阶乘的函数
fac = lambda n: functools.reduce(operator.mul, range(2, n + 1), 1)

# 用一行代码实现判断素数的函数
is_prime = lambda x: all(map(lambda f: x % f, range(2, int(x ** 0.5) + 1)))

print(fac(6))        # 720
print(is_prime(37))  # True
```

## 7. 偏函数

偏函数是指固定函数的某些参数，生成一个新的函数，这样就无需在每次调用函数时都传递相同的参数。

```python
import functools

int2 = functools.partial(int, base=2)
int8 = functools.partial(int, base=8)
int16 = functools.partial(int, base=16)

print(int('1001'))    # 1001
print(int2('1001'))   # 9
print(int8('1001'))   # 513
print(int16('1001'))  # 4097
```

## 8. 装饰器

装饰器是"**用一个函数装饰另外一个函数并为其提供额外的能力**"的语法现象。装饰器本身是一个函数，它的参数是被装饰的函数，它的返回值是一个带有装饰功能的函数。

### 8.1 装饰器示例

```python
import time
from functools import wraps

def record_time(func):
    """记录函数执行时间的装饰器"""
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f'{func.__name__}执行时间: {end - start:.2f}秒')
        return result
    
    return wrapper

@record_time
def download(filename):
    """下载文件"""
    print(f'开始下载{filename}.')
    time.sleep(1)
    print(f'{filename}下载完成.')

download('test.txt')
```

### 8.2 装饰器语法糖

使用装饰器的两种方式：

```python
# 方式一：直接调用装饰器函数
download = record_time(download)

# 方式二：使用装饰器语法糖（推荐）
@record_time
def download(filename):
    pass
```

### 8.3 保留原函数

使用`functools.wraps`可以保留被装饰之前的函数，通过`__wrapped__`属性可以访问原函数。

```python
# 取消装饰器的作用
download.__wrapped__('test.txt')
```

## 9. 递归调用

函数自己调用自己称为递归调用。递归调用适用于递归定义的问题。

### 9.1 递归求阶乘

```python
def fac(num):
    """求阶乘（递归版本）"""
    if num in (0, 1):
        return 1
    return num * fac(num - 1)

print(fac(5))  # 120
```

**说明**：
- 递归的收敛条件：什么时候要结束函数的递归调用
- 递归公式：问题的递归定义

### 9.2 递归的执行过程

```python
# 递归调用函数入栈
# 5 * fac(4)
# 5 * (4 * fac(3))
# 5 * (4 * (3 * fac(2)))
# 5 * (4 * (3 * (2 * fac(1))))
# 停止递归函数出栈
# 5 * (4 * (3 * (2 * 1)))
# 5 * (4 * (3 * 2))
# 5 * (4 * 6)
# 5 * 24
# 120
```

### 9.3 递归的注意事项

1. **必须有递归终止条件**：否则会导致无限递归
2. **递归深度限制**：Python 默认的递归深度限制是1000
3. **性能考虑**：递归可能会消耗更多的内存和执行时间

## 10. 函数的作用域

### 10.1 局部变量和全局变量

```python
x = 100  # 全局变量

def func():
    x = 200  # 局部变量
    print(x)  # 200

func()
print(x)  # 100
```

### 10.2 global关键字

在函数内部修改全局变量需要使用`global`关键字。

```python
x = 100

def func():
    global x
    x = 200  # 修改全局变量

func()
print(x)  # 200
```

## 11. 函数文档字符串

```python
def add(a, b):
    """计算两个数的和
    
    Args:
        a: 第一个数
        b: 第二个数
    
    Returns:
        两个数的和
    """
    return a + b

print(add.__doc__)  # 查看函数文档
help(add)  # 查看函数帮助
```

## 12. 函数的最佳实践

1. **单一职责原则**：每个函数应该只做一件事
2. **函数命名**：使用有意义的函数名
3. **参数设计**：合理使用默认参数和可变参数
4. **文档字符串**：为函数编写清晰的文档
5. **避免副作用**：尽量让函数只返回结果，不修改外部状态

## 13. 总结

函数是 Python 编程的核心概念之一。Python 中的函数是一等函数，可以赋值给变量，也可以作为函数的参数和返回值，这也就意味着我们可以在 Python 中使用高阶函数。掌握函数的定义、参数类型、Lambda 函数、装饰器和递归调用对于 Python 编程非常重要。
## 🎬 推荐视频资源

- [Corey Schafer - Python Functions](https://www.youtube.com/watch?v=9Os0o3wzS_I) — Python函数详解
- [Corey Schafer - Decorators](https://www.youtube.com/watch?v=FsAPt_9Bf3U) — 装饰器深入讲解
