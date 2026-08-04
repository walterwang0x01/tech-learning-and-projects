# Python变量与数据类型
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 变量概述

### 1.1 什么是变量

在编程语言中，**变量是数据的载体**，简单的说就是一块用来保存数据的内存空间，**变量的值可以被读取和修改**，这是所有运算和控制的基础。

### 1.2 变量的使用

```python
"""
使用变量保存数据并进行加减乘除运算

Version: 1.0
Author: 骆昊
"""
a = 45        # 定义变量a，赋值45
b = 12        # 定义变量b，赋值12
print(a, b)   # 45 12
print(a + b)  # 57
print(a - b)  # 33
print(a * b)  # 540
print(a / b)  # 3.75
```

## 2. 基本数据类型

### 2.1 整型（int）

Python 中可以处理任意大小的整数，而且支持二进制、八进制、十进制和十六进制的表示法。

```python
print(0b100)  # 二进制整数，输出4
print(0o100)  # 八进制整数，输出64
print(100)    # 十进制整数，输出100
print(0x100)  # 十六进制整数，输出256
```

### 2.2 浮点型（float）

浮点数也就是小数，除了数学写法之外还支持科学计数法。

```python
print(123.456)    # 数学写法
print(1.23456e2)  # 科学计数法，表示1.23456 × 10²
```

### 2.3 字符串型（str）

字符串是以单引号或双引号包裹起来的任意文本。

```python
s1 = 'hello'
s2 = "world"
s3 = '''多行
字符串'''
```

### 2.4 布尔型（bool）

布尔型只有`True`、`False`两种值。

```python
flag1 = True
flag2 = False
```

## 3. 变量命名

### 3.1 命名规则

- **规则1**：变量名由**字母**、**数字**和**下划线**构成，数字不能开头
- **规则2**：Python 是**大小写敏感**的编程语言
- **规则3**：变量名**不要跟 Python 的关键字重名**，**尽可能避开 Python 的保留字**

### 3.2 命名惯例

- **惯例1**：变量名通常使用**小写英文字母**，**多个单词用下划线进行连接**
- **惯例2**：受保护的变量用单个下划线开头（`_name`）
- **惯例3**：私有的变量用两个下划线开头（`__name`）

### 3.3 关键字

Python 的关键字包括：`and`、`as`、`assert`、`break`、`class`、`continue`、`def`、`del`、`elif`、`else`、`except`、`finally`、`for`、`from`、`global`、`if`、`import`、`in`、`is`、`lambda`、`nonlocal`、`not`、`or`、`pass`、`raise`、`return`、`try`、`while`、`with`、`yield`等。

## 4. 类型检查

### 4.1 type()函数

在 Python 中可以使用`type`函数对变量的类型进行检查。

```python
"""
使用type函数检查变量的类型

Version: 1.0
Author: 骆昊
"""
a = 100
b = 123.45
c = 'hello, world'
d = True
print(type(a))  # <class 'int'>
print(type(b))  # <class 'float'>
print(type(c))  # <class 'str'>
print(type(d))  # <class 'bool'>
```

### 4.2 isinstance()函数

`isinstance()`函数用于判断一个对象是否是一个已知的类型。

```python
a = 100
print(isinstance(a, int))      # True
print(isinstance(a, (int, float)))  # True
```

## 5. 类型转换

### 5.1 常用类型转换函数

- `int()`：将一个数值或字符串转换成整数，可以指定进制
- `float()`：将一个字符串（在可能的情况下）转换成浮点数
- `str()`：将指定的对象转换成字符串形式
- `chr()`：将整数（字符编码）转换成对应的（一个字符的）字符串
- `ord()`：将（一个字符的）字符串转换成对应的整数（字符编码）
- `bool()`：将其他类型转换为布尔值

### 5.2 类型转换示例

```python
"""
变量的类型转换操作

Version: 1.0
Author: 骆昊
"""
a = 100
b = 123.45
c = '123'
d = '100'
e = '123.45'
f = 'hello, world'
g = True

print(float(a))         # int类型的100转成float，输出100.0
print(int(b))           # float类型的123.45转成int，输出123
print(int(c))           # str类型的'123'转成int，输出123
print(int(c, base=16))  # str类型的'123'按十六进制转成int，输出291
print(int(d, base=2))   # str类型的'100'按二进制转成int，输出4
print(float(e))         # str类型的'123.45'转成float，输出123.45
print(bool(f))          # str类型的'hello, world'转成bool，输出True
print(int(g))           # bool类型的True转成int，输出1
print(chr(a))           # int类型的100转成str，输出'd'
print(ord('d'))         # str类型的'd'转成int，输出100
```

### 5.3 类型转换注意事项

- `str`类型转`int`类型时可以通过`base`参数来指定进制
- `str`类型转成`bool`类型时，只要字符串有内容，不是`''`或`""`，对应的布尔值都是`True`
- `bool`类型转`int`类型时，`True`会变成`1`，`False`会变成`0`
- 空字符串、空列表、空字典、`None`等转换为布尔值时都是`False`

## 6. 变量赋值

### 6.1 单个变量赋值

```python
a = 100
name = 'Python'
```

### 6.2 多个变量赋值

```python
# 同时给多个变量赋相同的值
a = b = c = 100

# 同时给多个变量赋不同的值
x, y, z = 1, 2, 3
```

### 6.3 变量交换

```python
a, b = 10, 20
a, b = b, a  # 交换a和b的值
print(a, b)  # 20 10
```

## 7. 常量

Python 中没有真正的常量，但按照惯例，常量通常使用全大写字母命名。

```python
PI = 3.14159
MAX_SIZE = 1000
```

## 8. 变量作用域

### 8.1 局部变量

在函数内部定义的变量是局部变量。

```python
def func():
    x = 10  # 局部变量
    print(x)

func()
# print(x)  # NameError: name 'x' is not defined
```

### 8.2 全局变量

在函数外部定义的变量是全局变量。

```python
x = 100  # 全局变量

def func():
    print(x)  # 可以访问全局变量

func()
```

### 8.3 global关键字

在函数内部修改全局变量需要使用`global`关键字。

```python
x = 100

def func():
    global x
    x = 200  # 修改全局变量

func()
print(x)  # 200
```

## 9. 变量命名最佳实践

1. **见名知意**：变量名应该清楚地表达变量的用途
2. **使用有意义的名称**：避免使用`a`、`b`、`x`等无意义的名称
3. **遵循命名惯例**：使用小写字母和下划线
4. **避免缩写**：除非是广泛认可的缩写（如`id`、`url`）
5. **不要使用保留字**：避免与Python关键字冲突

## 10. 常见问题

### 10.1 变量未定义

```python
# NameError: name 'x' is not defined
print(x)
```

### 10.2 类型错误

```python
# TypeError: can only concatenate str (not "int") to str
result = "Hello" + 123
```

### 10.3 变量命名冲突

```python
# 不要使用关键字作为变量名
# int = 100  # 不推荐，会覆盖内置函数
```

## 11. 总结

1. 变量是数据的载体，用于保存数据
2. Python 有丰富的数据类型：int、float、str、bool等
3. 变量命名需要遵循规则和惯例
4. 可以使用`type()`和`isinstance()`检查类型
5. 可以使用类型转换函数进行类型转换
6. 注意变量的作用域和生命周期
## 🎬 推荐视频资源

- [Corey Schafer - Python Data Types](https://www.youtube.com/watch?v=khKv-8q7YmY) — Python数据类型详解
- [Programming with Mosh - Python Tutorial](https://www.youtube.com/watch?v=_uQrJ0TkZlc) — 包含变量与类型章节
