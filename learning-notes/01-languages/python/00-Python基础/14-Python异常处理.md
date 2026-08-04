# Python异常处理
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 异常概述

程序在运行时可能遭遇无法预料的异常状况，为了让代码具有健壮性和容错性，我们可以使用 Python 的异常机制对可能在运行时发生状况的代码进行适当的处理。

## 2. 异常处理关键字

Python 中和异常相关的关键字有五个：
- `try`：尝试执行可能出错的代码
- `except`：捕获和处理异常
- `else`：没有异常时执行的代码
- `finally`：无论是否有异常都会执行的代码
- `raise`：抛出异常

## 3. try-except语句

### 3.1 基本用法

```python
try:
    # 可能出错的代码
    result = 10 / 0
except ZeroDivisionError:
    # 处理异常
    print('除数不能为0')
```

### 3.2 捕获多个异常

```python
try:
    file = open('致橡树.txt', 'r', encoding='utf-8')
    print(file.read())
except FileNotFoundError:
    print('无法打开指定的文件!')
except LookupError:
    print('指定了未知的编码!')
except UnicodeDecodeError:
    print('读取文件时解码错误!')
```

### 3.3 捕获异常信息

```python
try:
    result = 10 / 0
except ZeroDivisionError as e:
    print(f'错误信息: {e}')  # 错误信息: division by zero
```

### 3.4 捕获所有异常

```python
try:
    # 可能出错的代码
    result = 10 / 0
except Exception as e:
    print(f'发生异常: {e}')
```

**注意**：不建议在不清楚逻辑的情况下捕获所有异常，这可能会掩盖程序中严重的问题。

## 4. try-except-else语句

`else`代码块中的代码只有在`try`块中没有异常时才会执行，而且`else`中的代码不会再进行异常捕获。

```python
try:
    result = 10 / 2
    print(f'结果是: {result}')
except ZeroDivisionError:
    print('除数不能为0')
else:
    print('计算成功完成')
```

## 5. try-except-finally语句

`finally`块的代码不论程序正常还是异常都会执行，甚至是调用了`sys`模块的`exit`函数终止 Python 程序，`finally`块中的代码仍然会被执行。

```python
file = None
try:
    file = open('test.txt', 'r', encoding='utf-8')
    print(file.read())
except FileNotFoundError:
    print('无法打开指定的文件!')
finally:
    if file:
        file.close()  # 确保文件被关闭
    print('资源清理完成')
```

## 6. with语句（上下文管理器）

对于`open`函数返回的文件对象，还可以使用`with`上下文管理器语法在文件操作完成后自动执行文件对象的`close`方法。

```python
try:
    with open('致橡树.txt', 'r', encoding='utf-8') as file:
        print(file.read())
except FileNotFoundError:
    print('无法打开指定的文件!')
except LookupError:
    print('指定了未知的编码!')
except UnicodeDecodeError:
    print('读取文件时解码错误!')
```

**说明**：`with`语句会自动处理资源的获取和释放，即使发生异常也能正确关闭文件。

## 7. 异常类型

Python 中内置了大量的异常类型，常见的异常类型包括：

### 7.1 常见异常类型

- `ZeroDivisionError`：除数为零
- `FileNotFoundError`：文件不存在
- `ValueError`：值错误
- `TypeError`：类型错误
- `IndexError`：索引错误
- `KeyError`：键错误
- `AttributeError`：属性错误
- `NameError`：名称错误
- `SyntaxError`：语法错误

### 7.2 异常继承结构

```
BaseException
 +-- SystemExit
 +-- KeyboardInterrupt
 +-- GeneratorExit
 +-- Exception
      +-- ArithmeticError
      |    +-- ZeroDivisionError
      +-- AttributeError
      +-- EOFError
      +-- ImportError
      |    +-- ModuleNotFoundError
      +-- LookupError
      |    +-- IndexError
      |    +-- KeyError
      +-- NameError
      +-- OSError
      |    +-- FileNotFoundError
      +-- RuntimeError
      +-- SyntaxError
      +-- TypeError
      +-- ValueError
```

## 8. 抛出异常

### 8.1 raise语句

可以使用`raise`关键字来引发异常（抛出异常对象）。

```python
def divide(a, b):
    if b == 0:
        raise ZeroDivisionError('除数不能为0')
    return a / b

try:
    result = divide(10, 0)
except ZeroDivisionError as e:
    print(e)
```

### 8.2 自定义异常

如果 Python 内置的异常类型不能满足应用程序的需要，我们可以自定义异常类型。

```python
class InputError(ValueError):
    """自定义异常类型"""
    pass

def fac(num):
    """求阶乘"""
    if num < 0:
        raise InputError('只能计算非负整数的阶乘')
    if num in (0, 1):
        return 1
    return num * fac(num - 1)

flag = True
while flag:
    num = int(input('n = '))
    try:
        print(f'{num}! = {fac(num)}')
        flag = False
    except InputError as err:
        print(err)
```

**说明**：自定义的异常类型应该直接或间接继承自`Exception`类。

## 9. 异常处理最佳实践

### 9.1 不要滥用异常

**不要使用异常机制来处理正常业务逻辑或控制程序流程**，这是初学者常犯的错误。

```python
# 不好的做法
def check_positive(num):
    try:
        assert num > 0
        return True
    except AssertionError:
        return False

# 好的做法
def check_positive(num):
    return num > 0
```

### 9.2 具体异常优于通用异常

尽量捕获具体的异常类型，而不是捕获所有异常。

```python
# 不好的做法
try:
    result = 10 / 0
except Exception:
    pass

# 好的做法
try:
    result = 10 / 0
except ZeroDivisionError:
    print('除数不能为0')
```

### 9.3 异常处理顺序

多个`except`语句会按照书写的顺序依次匹配指定的异常，如果异常已经处理就不会再进入后续的`except`语句。

```python
try:
    # 代码
    pass
except ValueError:
    # 先捕获更具体的异常
    pass
except Exception:
    # 再捕获更通用的异常
    pass
```

### 9.4 使用finally清理资源

使用`finally`确保资源（如文件、网络连接等）被正确释放。

```python
file = None
try:
    file = open('test.txt', 'r')
    # 处理文件
except Exception:
    pass
finally:
    if file:
        file.close()
```

## 10. 异常处理总结

1. **try-except**：捕获和处理异常
2. **try-except-else**：没有异常时执行else块
3. **try-except-finally**：无论是否有异常都执行finally块
4. **with语句**：自动管理资源，推荐使用
5. **raise语句**：抛出异常
6. **自定义异常**：继承Exception类

**重要提示**：
- `try`后面的`except`语句不是必须的，`finally`语句也不是必须的，但是二者必须要有一个
- `except`语句可以有一个或多个
- `except`语句中还可以通过元组同时指定多个异常类型进行捕获
- 捕获异常后可以使用`raise`再次抛出，但是不建议捕获并抛出同一个异常
- 不要使用异常机制来处理正常业务逻辑或控制程序流程

## 11. 总结

异常处理是编写健壮程序的重要手段。Python 提供了完善的异常处理机制，包括`try-except-else-finally`结构和`with`语句。合理使用异常处理可以让程序更加稳定可靠，但要避免滥用异常机制。
