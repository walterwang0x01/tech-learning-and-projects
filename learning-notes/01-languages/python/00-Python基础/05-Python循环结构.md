# Python循环结构
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 循环结构概述

我们在写程序的时候，极有可能遇到需要重复执行某条或某些指令的场景，例如我们需要每隔1秒钟在屏幕上输出一次"hello, world"并持续输出一个小时。为了应对上述场景中的问题，我们可以在 Python 程序中使用循环结构。所谓循环结构，就是程序中控制某条或某些指令重复执行的结构。

在 Python 语言中构造循环结构有两种做法，一种是`for-in`循环，另一种是`while`循环。

## 2. for-in循环

如果明确知道循环执行的次数，我们推荐使用`for-in`循环。

### 2.1 基本用法

```python
"""
每隔1秒输出一次"hello, world"，持续1小时

Author: 骆昊
Version: 1.0
"""
import time

for i in range(3600):
    print('hello, world')
    time.sleep(1)
```

**说明**：
- `range(3600)`可以构造出一个从`0`到`3599`的范围
- 当我们把这样一个范围放到`for-in`循环中，就可以通过前面的循环变量`i`依次取出从`0`到`3599`的整数
- 被`for-in`循环控制的代码块也是通过缩进的方式来构造

### 2.2 range函数的用法

`range`函数的用法非常灵活：

- `range(101)`：可以用来产生`0`到`100`范围的整数，需要注意的是取不到`101`
- `range(1, 101)`：可以用来产生`1`到`100`范围的整数，相当于是左闭右开的设定，即`[1, 101)`
- `range(1, 101, 2)`：可以用来产生`1`到`100`的奇数，其中`2`是步长（跨度），即每次递增的值，`101`取不到
- `range(100, 0, -2)`：可以用来产生`100`到`1`的偶数，其中`-2`是步长（跨度），即每次递减的值，`0`取不到

### 2.3 不需要循环变量的情况

对于不需要用到循环变量的`for-in`循环结构，按照 Python 的编程惯例，我们通常把循环变量命名为`_`：

```python
"""
每隔1秒输出一次"hello, world"，持续1小时

Author: 骆昊
Version: 1.1
"""
import time

for _ in range(3600):
    print('hello, world')
    time.sleep(1)
```

### 2.4 从1到100的整数求和

```python
"""
从1到100的整数求和

Version: 1.0
Author: 骆昊
"""
total = 0
for i in range(1, 101):
    total += i
print(total)  # 5050
```

### 2.5 从1到100的偶数求和

方法一：使用条件判断

```python
"""
从1到100的偶数求和

Version: 1.0
Author: 骆昊
"""
total = 0
for i in range(1, 101):
    if i % 2 == 0:
        total += i
print(total)
```

方法二：修改range参数

```python
"""
从1到100的偶数求和

Version: 1.1
Author: 骆昊
"""
total = 0
for i in range(2, 101, 2):
    total += i
print(total)
```

方法三：使用内置函数

```python
"""
从1到100的偶数求和

Version: 1.2
Author: 骆昊
"""
print(sum(range(2, 101, 2)))
```

## 3. while循环

如果要构造循环结构但是又不能确定循环重复的次数，我们推荐使用`while`循环。`while`循环通过布尔值或能产生布尔值的表达式来控制循环，当布尔值或表达式的值为`True`时，循环体中的语句就会被重复执行，当表达式的值为`False`时，结束循环。

### 3.1 基本用法

```python
"""
从1到100的整数求和

Version: 1.1
Author: 骆昊
"""
total = 0
i = 1
while i <= 100:
    total += i
    i += 1
print(total)  # 5050
```

### 3.2 从1到100的偶数求和

```python
"""
从1到100的偶数求和

Version: 1.3
Author: 骆昊
"""
total = 0
i = 2
while i <= 100:
    total += i
    i += 2
print(total)
```

## 4. break和continue

### 4.1 break关键字

`break`关键字的作用是终止循环结构的执行。

```python
"""
从1到100的偶数求和

Version: 1.4
Author: 骆昊
"""
total = 0
i = 2
while True:
    total += i
    i += 2
    if i > 100:
        break
print(total)
```

**注意**：`break`只能终止它所在的那个循环，这一点在使用嵌套循环结构时需要引起注意。

### 4.2 continue关键字

`continue`关键字可以用来放弃本次循环后续的代码直接让循环进入下一轮。

```python
"""
从1到100的偶数求和

Version: 1.5
Author: 骆昊
"""
total = 0
for i in range(1, 101):
    if i % 2 != 0:
        continue
    total += i
print(total)
```

## 5. 嵌套的循环结构

和分支结构一样，循环结构也是可以嵌套的，也就是说在循环结构中还可以构造循环结构。

### 5.1 打印乘法口诀表

```python
"""
打印乘法口诀表

Version: 1.0
Author: 骆昊
"""
for i in range(1, 10):
    for j in range(1, i + 1):
        print(f'{i}×{j}={i * j}', end='\t')
    print()
```

输出：

```
1×1=1	
2×1=2	2×2=4	
3×1=3	3×2=6	3×3=9	
4×1=4	4×2=8	4×3=12	4×4=16	
5×1=5	5×2=10	5×3=15	5×4=20	5×5=25	
6×1=6	6×2=12	6×3=18	6×4=24	6×5=30	6×6=36	
7×1=7	7×2=14	7×3=21	7×4=28	7×5=35	7×6=42	7×7=49	
8×1=8	8×2=16	8×3=24	8×4=32	8×5=40	8×6=48	8×7=56	8×8=64	
9×1=9	9×2=18	9×3=27	9×4=36	9×5=45	9×6=54	9×7=63	9×8=72	9×9=81
```

## 6. 循环结构的应用

### 6.1 判断素数

要求：输入一个大于 1 的正整数，判断它是不是素数。

**提示**：素数指的是只能被 1 和自身整除的大于 1 的整数。例如对于正整数 $n$，我们可以通过在 2 到 $n - 1$ 之间寻找有没有 $n$ 的因子，来判断它到底是不是一个素数。当然，循环不用从 2 开始到 $n - 1$ 结束，因为对于大于 1 的正整数，因子应该都是成对出现的，所以循环到 $\sqrt{n}$ 就可以结束了。

```python
"""
输入一个大于1的正整数判断它是不是素数

Version: 1.0
Author: 骆昊
"""
num = int(input('请输入一个正整数: '))
end = int(num ** 0.5)
is_prime = True
for i in range(2, end + 1):
    if num % i == 0:
        is_prime = False
        break
if is_prime:
    print(f'{num}是素数')
else:
    print(f'{num}不是素数')
```

### 6.2 最大公约数

要求：输入两个大于 0 的正整数，求两个数的最大公约数。

**提示**：两个数的最大公约数是两个数的公共因子中最大的那个数。

方法一：暴力枚举

```python
"""
输入两个正整数求它们的最大公约数

Version: 1.0
Author: 骆昊
"""
x = int(input('x = '))
y = int(input('y = '))
for i in range(x, 0, -1):
    if x % i == 0 and y % i == 0:
        print(f'最大公约数: {i}')
        break
```

方法二：欧几里得算法（推荐）

```python
"""
输入两个正整数求它们的最大公约数

Version: 1.1
Author: 骆昊
"""
x = int(input('x = '))
y = int(input('y = '))
while y % x != 0:
    x, y = y % x, x
print(f'最大公约数: {x}')
```

### 6.3 猜数字游戏

要求：计算机出一个 1 到 100 之间的随机数，玩家输入自己猜的数字，计算机给出对应的提示信息"大一点"、"小一点"或"猜对了"，如果玩家猜中了数字，计算机提示用户一共猜了多少次，游戏结束，否则游戏继续。

```python
"""
猜数字小游戏

Version: 1.0
Author: 骆昊
"""
import random

answer = random.randrange(1, 101)
counter = 0
while True:
    counter += 1
    num = int(input('请输入: '))
    if num < answer:
        print('大一点.')
    elif num > answer:
        print('小一点.')
    else:
        print('猜对了.')
        break
print(f'你一共猜了{counter}次.')
```

## 7. for-in循环遍历序列

`for-in`循环不仅可以遍历数字范围，还可以遍历任何序列类型（列表、元组、字符串等）。

```python
# 遍历列表
languages = ['Python', 'Java', 'C++', 'Kotlin']
for language in languages:
    print(language)

# 遍历字符串
s = 'hello'
for char in s:
    print(char)

# 遍历元组
t = (1, 2, 3, 4, 5)
for num in t:
    print(num)
```

## 8. 循环与else子句

Python 的循环语句可以有一个`else`子句，它在循环正常结束时执行（不是通过`break`终止）。

```python
"""
查找列表中的元素

Version: 1.0
Author: 骆昊
"""
items = [1, 2, 3, 4, 5]
target = 6

for item in items:
    if item == target:
        print(f'找到了 {target}')
        break
else:
    print(f'没有找到 {target}')
```

## 9. 最佳实践

1. **选择合适的循环**：如果事先知道循环结构重复的次数，通常使用`for`循环；如果循环结构的重复次数不能确定，可以用`while`循环
2. **避免死循环**：使用`while True`时要确保有`break`条件
3. **合理使用break和continue**：不要过度使用，保持代码可读性
4. **注意循环变量**：不需要循环变量时使用`_`

## 10. 总结

学会了 Python 中的分支结构和循环结构，我们就可以解决很多实际的问题了。通过这节课的学习，大家应该已经知道了可以用`for`和`while`关键字来构造循环结构。**如果事先知道循环结构重复的次数，我们通常使用**`for`**循环**；**如果循环结构的重复次数不能确定，可以用**`while`**循环**。此外，我们可以在循环结构中**使用**`break`**终止循环**，**也可以在循环结构中使用**`continue`**关键字让循环结构直接进入下一轮次**。

