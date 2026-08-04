# Python分支结构
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 分支结构概述

迄今为止，我们写的 Python 程序都是一条一条语句按顺序向下执行的，这种代码结构叫做**顺序结构**。然而仅有顺序结构并不能解决所有的问题，比如我们设计一个游戏，游戏第一关的过关条件是玩家获得 1000 分，那么在第一关完成后，我们要根据玩家得到的分数来决定是进入第二关，还是告诉玩家"Game Over"（游戏结束）。在这种场景下，我们的代码就会产生两个分支，而且只有一个会被执行。我们将这种结构称之为"分支结构"或"选择结构"。

## 2. 使用if和else构造分支结构

在 Python 中，构造分支结构最常用的是`if`、`elif`和`else`三个关键字。

### 2.1 基本if语句

```python
"""
BMI计算器

Version: 1.0
Author: 骆昊
"""
height = float(input('身高(cm)：'))
weight = float(input('体重(kg)：'))
bmi = weight / (height / 100) ** 2
print(f'{bmi = :.1f}')
if 18.5 <= bmi < 24:
    print('你的身材很棒！')
```

**注意**：
- `if`语句的最后面有一个`:`，它是用英文输入法输入的冒号
- 程序中输入的`'`、`"`、`=`、`(`、`)`等特殊字符，都是在英文输入法状态下输入的
- Python 中使用**缩进的方式来表示代码的层次结构**，通常使用4个空格
- 如果`if`条件成立的情况下需要执行多条语句，只要保持多条语句具有相同的缩进就可以了

### 2.2 if-else语句

```python
"""
BMI计算器

Version: 1.1
Author: 骆昊
"""
height = float(input('身高(cm)：'))
weight = float(input('体重(kg)：'))
bmi = weight / (height / 100) ** 2
print(f'{bmi = :.1f}')
if 18.5 <= bmi < 24:
    print('你的身材很棒！')
else:
    print('你的身材不够标准哟！')
```

### 2.3 if-elif-else语句

```python
"""
BMI计算器

Version: 1.2
Author: 骆昊
"""
height = float(input('身高(cm)：'))
weight = float(input('体重(kg)：'))
bmi = weight / (height / 100) ** 2
print(f'{bmi = :.1f}')
if bmi < 18.5:
    print('你的体重过轻！')
elif bmi < 24:
    print('你的身材很棒！')
elif bmi < 27:
    print('你的体重过重！')
elif bmi < 30:
    print('你已轻度肥胖！')
elif bmi < 35:
    print('你已中度肥胖！')
else:
    print('你已重度肥胖！')
```

## 3. 使用match和case构造分支结构（Python 3.10+）

Python 3.10 中增加了一种新的构造分支结构的方式，通过使用`match`和`case`关键字，我们可以轻松的构造出多分支结构。

### 3.1 基本用法

```python
status_code = int(input('响应状态码: '))
match status_code:
    case 400: description = 'Bad Request'
    case 401: description = 'Unauthorized'
    case 403: description = 'Forbidden'
    case 404: description = 'Not Found'
    case 405: description = 'Method Not Allowed'
    case 418: description = 'I am a teapot'
    case 429: description = 'Too many requests'
    case _: description = 'Unknown Status Code'
print('状态码描述:', description)
```

**说明**：
- 带有`_`的`case`语句在代码中起到通配符的作用，如果前面的分支都没有匹配上，代码就会来到`case _`
- `case _`是可选的，并非每种分支结构都要给出通配符选项
- 如果分支中出现了`case _`，它只能放在分支结构的最后面

### 3.2 合并模式

```python
status_code = int(input('响应状态码: '))
match status_code:
    case 400 | 405: description = 'Invalid Request'
    case 401 | 403 | 404: description = 'Not Allowed'
    case 418: description = 'I am a teapot'
    case 429: description = 'Too many requests'
    case _: description = 'Unknown Status Code'
print('状态码描述:', description)
```

## 4. 嵌套的分支结构

根据实际开发的需要，分支结构是可以嵌套的，也就是说在分支结构的`if`、`elif`或`else`代码块中还可以再次引入分支结构。

```python
"""
分段函数求值

Version: 1.1
Author: 骆昊
"""
x = float(input('x = '))
if x > 1:
    y = 3 * x - 5
else:
    if x >= -1:
        y = x + 2
    else:
        y = 5 * x + 3
print(f'{y = }')
```

**注意**：在"Python 之禅"中有这么一句话："**Flat is better than nested**"。之所以认为"扁平化"的代码更好，是因为代码嵌套的层次如果很多，会严重的影响代码的可读性。所以，更推荐使用扁平化的写法：

```python
"""
分段函数求值

Version: 1.0
Author: 骆昊
"""
x = float(input('x = '))
if x > 1:
    y = 3 * x - 5
elif x >= -1:
    y = x + 2
else:
    y = 5 * x + 3
print(f'{y = }')
```

## 5. 分支结构的应用

### 5.1 分段函数求值

有如下所示的分段函数，要求输入`x`，计算出`y`。

$$
y = \begin{cases} 3x - 5, & (x \gt 1) \\ x + 2, & (-1 \le x \le 1) \\ 5x + 3, & (x \lt -1) \end{cases}
$$

```python
"""
分段函数求值

Version: 1.0
Author: 骆昊
"""
x = float(input('x = '))
if x > 1:
    y = 3 * x - 5
elif x >= -1:
    y = x + 2
else:
    y = 5 * x + 3
print(f'{y = }')
```

### 5.2 百分制成绩转换成等级

要求：如果输入的成绩在90分以上（含90分），则输出`A`；输入的成绩在80分到90分之间（不含90分），则输出`B`；输入的成绩在70分到80分之间（不含80分），则输出`C`；输入的成绩在60分到70分之间（不含70分），则输出`D`；输入的成绩在60分以下，则输出`E`。

```python
"""
百分制成绩转换为等级制成绩

Version: 1.0
Author: 骆昊
"""
score = float(input('请输入成绩: '))
if score >= 90:
    grade = 'A'
elif score >= 80:
    grade = 'B'
elif score >= 70:
    grade = 'C'
elif score >= 60:
    grade = 'D'
else:
    grade = 'E'
print(f'{grade = }')
```

### 5.3 计算三角形的周长和面积

要求：输入三条边的长度，如果能构成三角形就计算周长和面积；否则给出"不能构成三角形"的提示。

```python
"""
计算三角形的周长和面积

Version: 1.0
Author: 骆昊
"""
a = float(input('a = '))
b = float(input('b = '))
c = float(input('c = '))
if a + b > c and a + c > b and b + c > a:
    perimeter = a + b + c
    print(f'周长: {perimeter}')
    s = perimeter / 2
    area = (s * (s - a) * (s - b) * (s - c)) ** 0.5
    print(f'面积: {area}')
else:
    print('不能构成三角形')
```

**说明**：
- 上面的`if`条件表示任意两边之和大于第三边，这是构成三角形的必要条件
- 计算三角形面积的公式叫做海伦公式，假设有一个三角形，边长分别为 $a$、$b$、$c$，那么三角形的面积 $A$ 可以由公式 $A = \sqrt{s(s-a)(s-b)(s-c)}$ 得到，其中，$s=\frac{a + b + c}{2}$ 表示半周长

## 6. 三元运算符

Python 支持三元运算符（条件表达式），可以在一行中完成简单的条件判断。

```python
# 基本语法：value_if_true if condition else value_if_false
a = 10
b = 20
max_value = a if a > b else b
print(max_value)  # 20

# 嵌套使用
score = 85
grade = 'A' if score >= 90 else ('B' if score >= 80 else ('C' if score >= 70 else 'D'))
print(grade)  # B
```

## 7. 最佳实践

1. **避免深层嵌套**：尽量使用`elif`而不是嵌套的`if-else`
2. **使用match-case**：Python 3.10+可以使用`match-case`简化多分支结构
3. **保持代码简洁**：简单的条件判断可以使用三元运算符
4. **合理使用括号**：复杂的条件表达式使用括号明确优先级

## 8. 总结

学会了 Python 中的分支结构和循环结构，我们就可以解决很多实际的问题了。这一节课相信已经帮助大家掌握了构造分支结构的方法，下一节课我们为大家介绍循环结构。

