# Python文件操作
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 文件操作概述

实际开发中常常会遇到对数据进行持久化的场景，所谓持久化是指将数据从无法长久保存数据的存储介质（通常是内存）转移到可以长久保存数据的存储介质（通常是硬盘）中。实现数据持久化最直接简单的方式就是通过**文件系统**将数据保存到**文件**中。

## 2. 打开和关闭文件

### 2.1 open函数

我们可以使用 Python 内置的`open`函数来打开文件。

```python
file = open('filename.txt', 'r', encoding='utf-8')
# 处理文件
file.close()
```

### 2.2 文件操作模式

| 操作模式 | 具体含义                         |
| -------- | -------------------------------- |
| `'r'`    | 读取（默认）                     |
| `'w'`    | 写入（会先截断之前的内容）       |
| `'x'`    | 写入，如果文件已经存在会产生异常 |
| `'a'`    | 追加，将内容写入到已有文件的末尾 |
| `'b'`    | 二进制模式                       |
| `'t'`    | 文本模式（默认）                 |
| `'+'`    | 更新（既可以读又可以写）         |

## 3. 读写文本文件

### 3.1 读取文本文件

```python
# 方法一：read()方法读取全部内容
file = open('致橡树.txt', 'r', encoding='utf-8')
content = file.read()
print(content)
file.close()

# 方法二：逐行读取
file = open('致橡树.txt', 'r', encoding='utf-8')
for line in file:
    print(line, end='')
file.close()

# 方法三：readlines()方法读取所有行
file = open('致橡树.txt', 'r', encoding='utf-8')
lines = file.readlines()
for line in lines:
    print(line, end='')
file.close()
```

### 3.2 写入文本文件

```python
# 写入模式（会覆盖原有内容）
file = open('致橡树.txt', 'w', encoding='utf-8')
file.write('标题：《致橡树》\n')
file.write('作者：舒婷\n')
file.write('时间：1977年3月\n')
file.close()

# 追加模式
file = open('致橡树.txt', 'a', encoding='utf-8')
file.write('\n这是一首爱情诗')
file.close()
```

## 4. 使用with语句（推荐）

使用`with`语句可以自动关闭文件，即使发生异常也能正确关闭。

```python
# 基本用法
with open('致橡树.txt', 'r', encoding='utf-8') as file:
    print(file.read())

# 写入文件
with open('致橡树.txt', 'w', encoding='utf-8') as file:
    file.write('新的内容')

# 追加内容
with open('致橡树.txt', 'a', encoding='utf-8') as file:
    file.write('\n追加的内容')
```

## 5. 异常处理

文件操作可能会遇到各种异常，需要使用异常处理机制。

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

## 6. 读写二进制文件

读写二进制文件跟读写文本文件的操作类似，但是需要注意操作模式是`'rb'`或`'wb'`。

```python
# 读取二进制文件
try:
    with open('guido.jpg', 'rb') as file1:
        data = file1.read()
    with open('吉多.jpg', 'wb') as file2:
        file2.write(data)
except FileNotFoundError:
    print('指定的文件无法打开.')
except IOError:
    print('读写文件时出现错误.')
```

### 6.1 大文件处理

对于大文件，应该分块读取和写入，避免一次性加载到内存。

```python
try:
    with open('guido.jpg', 'rb') as file1, open('吉多.jpg', 'wb') as file2:
        data = file1.read(512)  # 每次读取512字节
        while data:
            file2.write(data)
            data = file1.read(512)
except FileNotFoundError:
    print('指定的文件无法打开.')
except IOError:
    print('读写文件时出现错误.')
```

## 7. 文件对象的方法

### 7.1 读取方法

- `read(size)`：读取指定字节数（文本模式）或字符数（文本模式），不指定则读取全部
- `readline()`：读取一行
- `readlines()`：读取所有行，返回列表

### 7.2 写入方法

- `write(text)`：写入文本
- `writelines(lines)`：写入多行（列表）

### 7.3 定位方法

- `tell()`：返回当前文件位置
- `seek(offset, whence)`：移动文件指针

```python
with open('test.txt', 'r', encoding='utf-8') as file:
    print(file.tell())      # 0（当前位置）
    content = file.read(10)  # 读取10个字符
    print(file.tell())      # 10（当前位置）
    file.seek(0)            # 回到文件开头
    print(file.tell())      # 0
```

## 8. 文件操作常见场景

### 8.1 读取CSV文件

```python
import csv

with open('data.csv', 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    for row in reader:
        print(row)
```

### 8.2 写入CSV文件

```python
import csv

data = [
    ['姓名', '年龄', '城市'],
    ['张三', '25', '北京'],
    ['李四', '30', '上海']
]

with open('data.csv', 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(data)
```

### 8.3 处理JSON文件

```python
import json

# 读取JSON文件
with open('data.json', 'r', encoding='utf-8') as file:
    data = json.load(file)
    print(data)

# 写入JSON文件
data = {'name': '张三', 'age': 25, 'city': '北京'}
with open('data.json', 'w', encoding='utf-8') as file:
    json.dump(data, file, ensure_ascii=False, indent=2)
```

## 9. 文件路径操作

### 9.1 os.path模块

```python
import os

# 获取文件路径
file_path = os.path.join('dir1', 'dir2', 'file.txt')
print(file_path)

# 检查文件是否存在
if os.path.exists('file.txt'):
    print('文件存在')

# 获取文件名
filename = os.path.basename('/path/to/file.txt')
print(filename)  # file.txt

# 获取目录名
dirname = os.path.dirname('/path/to/file.txt')
print(dirname)  # /path/to
```

### 9.2 pathlib模块（推荐）

```python
from pathlib import Path

# 创建路径对象
file_path = Path('dir1') / 'dir2' / 'file.txt'

# 检查文件是否存在
if file_path.exists():
    print('文件存在')

# 读取文件
content = file_path.read_text(encoding='utf-8')

# 写入文件
file_path.write_text('内容', encoding='utf-8')
```

## 10. 文件操作最佳实践

1. **使用with语句**：自动管理文件资源
2. **指定编码**：文本文件操作时明确指定编码（推荐utf-8）
3. **异常处理**：使用try-except处理可能的异常
4. **大文件处理**：分块读取和写入，避免一次性加载
5. **路径处理**：使用pathlib模块处理文件路径

## 11. 总结

文件操作是编程中常见的操作，Python 提供了简单易用的文件操作接口。使用`with`语句可以自动管理文件资源，使用异常处理可以提高代码的健壮性。掌握文本文件、二进制文件的读写操作，以及常见文件格式（CSV、JSON）的处理方法，对于 Python 编程非常重要。

