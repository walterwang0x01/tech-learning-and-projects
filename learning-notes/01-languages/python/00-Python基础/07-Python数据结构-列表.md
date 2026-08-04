# Python数据结构-列表
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 列表概述

在 Python 中，**列表是由一系列元素按特定顺序构成的数据序列**，这就意味着如果我们定义一个列表类型的变量，**可以用它来保存多个数据**。

## 2. 创建列表

### 2.1 使用字面量语法

在 Python 中，可以使用`[]`字面量语法来定义列表，列表中的多个元素用逗号进行分隔。

```python
items1 = [35, 12, 99, 68, 55, 35, 87]
items2 = ['Python', 'Java', 'Go', 'Kotlin']
items3 = [100, 12.3, 'Python', True]
print(items1)  # [35, 12, 99, 68, 55, 35, 87]
print(items2)  # ['Python', 'Java', 'Go', 'Kotlin']
print(items3)  # [100, 12.3, 'Python', True]
```

**说明**：
- 列表中可以有重复元素，例如`items1`中的`35`
- 列表中可以有不同类型的元素，例如`items3`中有`int`类型、`float`类型、`str`类型和`bool`类型的元素
- 但是我们通常并不建议将不同类型的元素放在同一个列表中，主要是操作起来极为不便

### 2.2 使用list函数

还可以通过 Python 内置的`list`函数将其他序列变成列表。

```python
items4 = list(range(1, 10))
items5 = list('hello')
print(items4)  # [1, 2, 3, 4, 5, 6, 7, 8, 9]
print(items5)  # ['h', 'e', 'l', 'l', 'o']
```

## 3. 列表的运算

### 3.1 拼接运算

我们可以使用`+`运算符实现两个列表的拼接。

```python
items5 = [35, 12, 99, 45, 66]
items6 = [45, 58, 29]
items7 = ['Python', 'Java', 'JavaScript']
print(items5 + items6)  # [35, 12, 99, 45, 66, 45, 58, 29]
print(items6 + items7)  # [45, 58, 29, 'Python', 'Java', 'JavaScript']
items5 += items6
print(items5)  # [35, 12, 99, 45, 66, 45, 58, 29]
```

### 3.2 重复运算

我们可以使用`*`运算符实现列表的重复运算。

```python
print(items6 * 3)  # [45, 58, 29, 45, 58, 29, 45, 58, 29]
print(items7 * 2)  # ['Python', 'Java', 'JavaScript', 'Python', 'Java', 'JavaScript']
```

### 3.3 成员运算

我们可以使用`in`或`not in`运算符判断一个元素在不在列表中。

```python
print(29 in items6)  # True
print(99 in items6)  # False
print('C++' not in items7)     # True
print('Python' not in items7)  # False
```

## 4. 索引和切片

### 4.1 索引运算

由于列表中有多个元素，而且元素是按照特定顺序放在列表中的，所以当我们想操作列表中的某个元素时，可以使用`[]`运算符，通过在`[]`中指定元素的位置来访问该元素。

```python
items8 = ['apple', 'waxberry', 'pitaya', 'peach', 'watermelon']
print(items8[0])   # apple
print(items8[2])   # pitaya
print(items8[4])   # watermelon
items8[2] = 'durian'
print(items8)      # ['apple', 'waxberry', 'durian', 'peach', 'watermelon']
print(items8[-5])  # 'apple'
print(items8[-4])  # 'waxberry'
print(items8[-1])  # watermelon
```

**说明**：
- `[]`的元素位置可以是`0`到`N - 1`的整数，也可以是`-1`到`-N`的整数，分别称为正向索引和反向索引
- 对于正向索引，`[0]`可以访问列表中的第一个元素，`[N - 1]`可以访问最后一个元素
- 对于反向索引，`[-1]`可以访问列表中的最后一个元素，`[-N]`可以访问第一个元素
- 在使用索引运算的时候要避免出现索引越界的情况，否则会引发`IndexError`错误

### 4.2 切片运算

如果希望一次性访问列表中的多个元素，我们可以使用切片运算。切片运算是形如`[start:end:stride]`的运算符。

```python
print(items8[1:3:1])     # ['strawberry', 'durian']
print(items8[0:3:1])      # ['apple', 'strawberry', 'durian']
print(items8[0:5:2])     # ['apple', 'durian', 'watermelon']
print(items8[-4:-2:1])   # ['strawberry', 'durian']
print(items8[-2:-6:-1])  # ['peach', 'durian', 'strawberry', 'apple']
```

**简化写法**：
- 如果`start`值等于`0`，可以省略
- 如果`end`值等于列表长度，可以省略
- 如果`stride`值等于`1`，可以省略

```python
print(items8[1:3])     # ['strawberry', 'durian']
print(items8[:3])      # ['apple', 'strawberry', 'durian']
print(items8[::2])     # ['apple', 'durian', 'watermelon']
print(items8[-4:-2])   # ['strawberry', 'durian']
print(items8[-2::-1])  # ['peach', 'durian', 'strawberry', 'apple']
```

### 4.3 通过切片修改元素

我们还可以通过切片操作修改列表中的元素。

```python
items8[1:3] = ['x', 'o']
print(items8)  # ['apple', 'x', 'o', 'peach', 'watermelon']
```

## 5. 列表的方法

### 5.1 添加和删除元素

#### append方法

使用列表的`append`方法向列表中追加元素（将元素添加到列表的末尾）。

```python
languages = ['Python', 'Java', 'C++']
languages.append('JavaScript')
print(languages)  # ['Python', 'Java', 'C++', 'JavaScript']
```

#### insert方法

使用`insert`方法向列表中插入元素（在指定的位置添加新元素）。

```python
languages.insert(1, 'SQL')
print(languages)  # ['Python', 'SQL', 'Java', 'C++', 'JavaScript']
```

#### remove方法

使用列表的`remove`方法从列表中删除指定元素。

```python
languages = ['Python', 'SQL', 'Java', 'C++', 'JavaScript']
if 'Java' in languages:
    languages.remove('Java')
print(languages)  # ['Python', 'SQL', 'C++', 'JavaScript']
```

**注意**：
- 如果要删除的元素并不在列表中，会引发`ValueError`错误
- 如果列表中有多个相同的元素，`remove`方法只会删除第一个

#### pop方法

使用`pop`方法从列表中删除元素，`pop`方法默认删除列表中的最后一个元素，当然也可以给一个位置，删除指定位置的元素。

```python
languages = ['Python', 'SQL', 'Java', 'C++', 'JavaScript']
languages.pop()  # 删除最后一个元素
temp = languages.pop(1)  # 删除索引为1的元素并返回
print(temp)       # SQL
print(languages)  # ['Python', 'Java', 'C++']
```

#### clear方法

列表的`clear`方法可以清空列表中的元素。

```python
languages.clear()
print(languages)  # []
```

#### del关键字

从列表中删除元素还可以使用`del`关键字。

```python
items = ['Python', 'Java', 'C++']
del items[1]
print(items)  # ['Python', 'C++']
```

### 5.2 元素位置和频次

#### index方法

列表的`index`方法可以查找某个元素在列表中的索引位置。

```python
items = ['Python', 'Java', 'Java', 'C++', 'Kotlin', 'Python']
print(items.index('Python'))     # 0
print(items.index('Python', 1))  # 5（从索引位置1开始查找）
```

**注意**：如果找不到指定的元素，`index`方法会引发`ValueError`错误。

#### count方法

列表的`count`方法可以统计一个元素在列表中出现的次数。

```python
print(items.count('Python'))     # 2
print(items.count('Kotlin'))     # 1
print(items.count('Swift'))      # 0
```

### 5.3 元素排序和反转

#### sort方法

列表的`sort`操作可以实现列表元素的排序。

```python
items = ['Python', 'Java', 'C++', 'Kotlin', 'Swift']
items.sort()
print(items)  # ['C++', 'Java', 'Kotlin', 'Python', 'Swift']
```

#### reverse方法

`reverse`操作可以实现元素的反转。

```python
items.reverse()
print(items)  # ['Swift', 'Python', 'Kotlin', 'Java', 'C++']
```

## 6. 列表生成式（列表推导式）

在 Python 中，列表还可以通过一种特殊的字面量语法来创建，这种语法叫做生成式（推导式）。

### 6.1 基本语法

```python
# 创建一个取值范围在1到99且能被3或者5整除的数字构成的列表
items = [i for i in range(1, 100) if i % 3 == 0 or i % 5 == 0]
print(items)
```

### 6.2 应用场景

**场景一**：对列表元素进行变换

```python
nums1 = [35, 12, 97, 64, 55]
nums2 = [num ** 2 for num in nums1]
print(nums2)  # [1225, 144, 9409, 4096, 3025]
```

**场景二**：过滤列表元素

```python
nums1 = [35, 12, 97, 64, 55]
nums2 = [num for num in nums1 if num > 50]
print(nums2)  # [97, 64, 55]
```

**场景三**：嵌套列表生成式

```python
import random

# 生成5个学生3门课程的成绩
scores = [[random.randrange(60, 101) for _ in range(3)] for _ in range(5)]
print(scores)
```

**优势**：
- 代码简单优雅
- 性能优于使用`for-in`循环和`append`方法
- 强烈建议用生成式语法来创建列表

## 7. 嵌套列表

Python 语言没有限定列表中的元素必须是相同的数据类型，也就是说一个列表中的元素可以是任意的数据类型，当然也包括列表本身。如果列表中的元素也是列表，那么我们可以称之为嵌套的列表。

```python
scores = [[95, 83, 92], [80, 75, 82], [92, 97, 90], [80, 78, 69], [65, 66, 89]]
print(scores[0])      # [95, 83, 92]
print(scores[0][1])   # 83
```

## 8. 元素的遍历

如果想逐个取出列表中的元素，可以使用`for-in`循环。

### 8.1 方法一：通过索引遍历

```python
languages = ['Python', 'Java', 'C++', 'Kotlin']
for index in range(len(languages)):
    print(languages[index])
```

### 8.2 方法二：直接遍历元素

```python
languages = ['Python', 'Java', 'C++', 'Kotlin']
for language in languages:
    print(language)
```

### 8.3 方法三：使用enumerate

```python
languages = ['Python', 'Java', 'C++', 'Kotlin']
for index, language in enumerate(languages):
    print(f'{index}: {language}')
```

## 9. 列表应用示例

### 9.1 掷色子统计

```python
"""
将一颗色子掷6000次，统计每种点数出现的次数

Author: 骆昊
Version: 1.1
"""
import random

counters = [0] * 6
# 模拟掷色子记录每种点数出现的次数
for _ in range(6000):
    face = random.randrange(1, 7)
    counters[face - 1] += 1
# 输出每种点数出现的次数
for face in range(1, 7):
    print(f'{face}点出现了{counters[face - 1]}次')
```

## 10. 列表的特点

1. **有序性**：列表中的元素按照特定顺序排列
2. **可变性**：可以修改列表中的元素
3. **可重复**：列表中可以包含重复的元素
4. **异构性**：列表中的元素可以是不同类型（但不推荐）

## 11. 列表性能说明

Python 中的列表底层是一个可以动态扩容的数组，列表元素在计算机内存中是连续存储的，所以可以实现随机访问（通过一个有效的索引获取对应的元素且操作时间与列表元素个数无关）。

## 12. 总结

列表是 Python 中最常用的数据结构之一，掌握列表的创建、操作和方法对于 Python 编程非常重要。使用列表生成式可以让我们写出更简洁、高效的代码。

