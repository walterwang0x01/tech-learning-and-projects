# Python数据结构-字符串
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 字符串概述

所谓**字符串**，就是**由零个或多个字符组成的有限序列**，一般记为：

$$s = a_1a_2 \cdots a_n \,\,\,\,\, (0 \le n \le \infty)$$

在 Python 程序中，我们把单个或多个字符用单引号或者双引号包围起来，就可以表示一个字符串。

## 2. 字符串的定义

```python
s1 = 'hello, world!'
s2 = "你好，世界！❤️"
s3 = '''hello,
wonderful
world!'''
print(s1)
print(s2)
print(s3)
```

### 2.1 转义字符

我们可以在字符串中使用`\`（反斜杠）来表示转义，也就是说`\`后面的字符不再是它原来的意义。

```python
s1 = '\'hello, world!\''  # 输出: 'hello, world!'
s2 = '\\hello, world!\\'  # 输出: \hello, world!\
print(s1)
print(s2)
```

常用的转义字符：
- `\n`：换行符
- `\t`：制表符
- `\r`：回车符
- `\\`：反斜杠
- `\'`：单引号
- `\"`：双引号

### 2.2 原始字符串

Python 中有一种以`r`或`R`开头的字符串，这种字符串被称为原始字符串，意思是字符串中的每个字符都是它本来的含义，没有所谓的转义字符。

```python
s1 = '\it \is \time \to \read \now'
s2 = r'\it \is \time \to \read \now'
print(s1)  # 转义字符会被解释
print(s2)  # 原始字符串，所有字符保持原样
```

### 2.3 字符的特殊表示

Python 中还允许在`\`后面还可以跟一个八进制或者十六进制数来表示字符。

```python
s1 = '\141\142\143\x61\x62\x63'  # abcabc（八进制和十六进制）
s2 = '\u9a86\u660a'  # 骆昊（Unicode字符编码）
print(s1)
print(s2)
```

## 3. 字符串的运算

### 3.1 拼接和重复

```python
s1 = 'hello' + ', ' + 'world'
print(s1)    # hello, world

s2 = '!' * 3
print(s2)    # !!!

s1 += s2
print(s1)    # hello, world!!!

s1 *= 2
print(s1)    # hello, world!!!hello, world!!!
```

### 3.2 比较运算

对于两个字符串类型的变量，可以直接使用比较运算符来判断两个字符串的相等性或比较大小。

```python
s1 = 'a whole new world'
s2 = 'hello world'
print(s1 == s2)             # False
print(s1 < s2)              # True
print(s2 == 'hello world')  # True
print(s2 != 'Hello world')  # True
```

**说明**：字符串的大小比较比的是每个字符对应的编码的大小。

### 3.3 成员运算

Python 中可以用`in`和`not in`判断一个字符串中是否包含另外一个字符或字符串。

```python
s1 = 'hello, world'
s2 = 'goodbye, world'
print('wo' in s1)      # True
print('wo' not in s2)  # False
print(s2 in s1)        # False
```

### 3.4 获取字符串长度

```python
s = 'hello, world'
print(len(s))                 # 12
print(len('goodbye, world'))  # 14
```

### 3.5 索引和切片

字符串的索引和切片操作跟列表、元组几乎没有区别，因为字符串也是一种有序序列。

```python
s = 'abc123456'
n = len(s)
print(s[0], s[-n])    # a a
print(s[n-1], s[-1])  # 6 6
print(s[2], s[-7])    # c c
print(s[5], s[-4])    # 3 3
print(s[2:5])         # c12
print(s[-7:-4])       # c12
print(s[2:])          # c123456
print(s[:2])          # ab
print(s[::2])         # ac246
print(s[::-1])        # 654321cba
```

**注意**：因为**字符串是不可变类型**，所以**不能通过索引运算修改字符串中的字符**。

## 4. 字符的遍历

如果希望遍历字符串中的每个字符，可以使用`for-in`循环。

```python
s = 'hello'
# 方式一：通过索引遍历
for i in range(len(s)):
    print(s[i])

# 方式二：直接遍历字符
for char in s:
    print(char)
```

## 5. 字符串的方法

### 5.1 大小写相关操作

```python
s1 = 'hello, world!'
# 字符串首字母大写
print(s1.capitalize())  # Hello, world!
# 字符串每个单词首字母大写
print(s1.title())       # Hello, World!
# 字符串变大写
print(s1.upper())       # HELLO, WORLD!

s2 = 'GOODBYE'
# 字符串变小写
print(s2.lower())       # goodbye
```

**说明**：由于字符串是不可变类型，使用字符串的方法对字符串进行操作会产生新的字符串，但是原来变量的值并没有发生变化。

### 5.2 查找操作

可以使用字符串的`find`或`index`方法查找子字符串。

```python
s = 'hello, world!'
print(s.find('or'))      # 8
print(s.find('or', 9))   # -1（找不到返回-1）
print(s.find('of'))      # -1

print(s.index('or'))     # 8
# print(s.index('or', 9))  # ValueError: substring not found（找不到会报错）
```

**说明**：
- `find`方法找不到指定的字符串会返回`-1`
- `index`方法找不到指定的字符串会引发`ValueError`错误

### 5.3 逆向查找

`find`和`index`方法还有逆向查找（从后向前查找）的版本，分别是`rfind`和`rindex`。

```python
s = 'hello world!'
print(s.find('o'))       # 4
print(s.rfind('o'))      # 7
print(s.rindex('o'))     # 7
```

### 5.4 性质判断

可以通过字符串的`startswith`、`endswith`来判断字符串是否以某个字符串开头和结尾；还可以用`is`开头的方法判断字符串的特征。

```python
s1 = 'hello, world!'
print(s1.startswith('He'))   # False
print(s1.startswith('hel'))  # True
print(s1.endswith('!'))      # True

s2 = 'abc123456'
print(s2.isdigit())  # False（不完全由数字构成）
print(s2.isalpha())  # False（不完全由字母构成）
print(s2.isalnum())  # True（由字母和数字构成）
```

常用判断方法：
- `isdigit()`：判断字符串是不是完全由数字构成
- `isalpha()`：判断字符串是不是完全由字母构成
- `isalnum()`：判断字符串是不是由字母和数字构成
- `isspace()`：判断字符串是不是完全由空白字符构成
- `islower()`：判断字符串是否全为小写
- `isupper()`：判断字符串是否全为大写

### 5.5 格式化

字符串类型可以通过`center`、`ljust`、`rjust`方法做居中、左对齐和右对齐的处理。

```python
s = 'hello, world'
print(s.center(20, '*'))  # ****hello, world****
print(s.rjust(20))        #         hello, world
print(s.ljust(20, '~'))   # hello, world~~~~~~~~
print('33'.zfill(5))      # 00033
print('-33'.zfill(5))     # -0033
```

### 5.6 字符串格式化方法

#### %格式化

```python
a = 321
b = 123
print('%d * %d = %d' % (a, b, a * b))
```

#### format方法

```python
a = 321
b = 123
print('{0} * {1} = {2}'.format(a, b, a * b))
```

#### f-string（推荐）

从 Python 3.6 开始，格式化字符串还有更为简洁的书写方式，就是在字符串前加上`f`来格式化字符串。

```python
a = 321
b = 123
print(f'{a} * {b} = {a * b}')
```

#### 格式化控制

| 变量值      | 占位符     | 格式化结果    | 说明 |
| ----------- | ---------- | ------------- | ---- |
| `3.1415926` | `{:.2f}`   | `'3.14'`      | 保留小数点后两位 |
| `3.1415926` | `{:+.2f}`  | `'+3.14'`     | 带符号保留小数点后两位 |
| `-1`        | `{:+.2f}`  | `'-1.00'`     | 带符号保留小数点后两位 |
| `3.1415926` | `{:.0f}`   | `'3'`         | 不带小数 |
| `123`       | `{:0>10d}` | `'0000000123'`| 左边补`0`，补够10位 |
| `123`       | `{:x<10d}` | `'123xxxxxxx'`| 右边补`x`，补够10位 |
| `123`       | `{:>10d}`  | `'       123'`| 左边补空格，补够10位 |
| `123`       | `{:<10d}`  | `'123       '`| 右边补空格，补够10位 |
| `123456789` | `{:,}`     | `'123,456,789'`| 逗号分隔格式 |
| `0.123`     | `{:.2%}`   | `'12.30%'`    | 百分比格式 |
| `123456789` | `{:.2e}`   | `'1.23e+08'`  | 科学计数法格式 |

### 5.7 修剪操作

字符串的`strip`方法可以帮我们获得将原字符串修剪掉左右两端指定字符之后的字符串，默认是修剪空格字符。

```python
s1 = '   jackfrued@126.com  '
print(s1.strip())      # jackfrued@126.com

s2 = '~你好，世界~'
print(s2.lstrip('~'))  # 你好，世界~
print(s2.rstrip('~'))  # ~你好，世界
```

- `strip()`：去除左右两端的指定字符（默认是空格）
- `lstrip()`：去除左端的指定字符
- `rstrip()`：去除右端的指定字符

### 5.8 替换操作

如果希望用新的内容替换字符串中指定的内容，可以使用`replace`方法。

```python
s = 'hello, good world'
print(s.replace('o', '@'))     # hell@, g@@d w@rld（全部替换）
print(s.replace('o', '@', 1))  # hell@, good world（只替换一次）
```

### 5.9 拆分与合并

可以使用字符串的`split`方法将一个字符串拆分为多个字符串（放在一个列表中），也可以使用字符串的`join`方法将列表中的多个字符串连接成一个字符串。

```python
s = 'I love you'
words = s.split()
print(words)            # ['I', 'love', 'you']
print('~'.join(words))  # I~love~you
```

**说明**：`split`方法默认使用空格进行拆分，我们也可以指定其他的字符来拆分字符串，而且还可以指定最大拆分次数来控制拆分的效果。

```python
s = 'I#love#you#so#much'
words = s.split('#')
print(words)  # ['I', 'love', 'you', 'so', 'much']

words = s.split('#', 2)
print(words)  # ['I', 'love', 'you#so#much']
```

### 5.10 编码和解码

Python 中除了字符串`str`类型外，还有一种表示二进制数据的字节串类型（`bytes`）。所谓字节串，就是**由零个或多个字节组成的有限序列**。

```python
a = '骆昊'
b = a.encode('utf-8')
c = a.encode('gbk')
print(b)                  # b'\xe9\xaa\x86\xe6\x98\x8a'
print(c)                  # b'\xc2\xe6\xea\xbb'
print(b.decode('utf-8'))  # 骆昊
print(c.decode('gbk'))    # 骆昊
```

**注意**：如果编码和解码的方式不一致，会导致乱码问题（无法再现原始的内容）或引发`UnicodeDecodeError`错误，导致程序崩溃。

## 6. 字符串的特点

1. **不可变性**：字符串一旦创建，不能修改其内容
2. **有序性**：字符串中的字符按照特定顺序排列
3. **可重复**：字符串中可以包含重复的字符

## 7. 字符串的应用

字符串是 Python 中最常用的数据类型之一，在文本处理、数据解析、格式化输出等场景中都有广泛应用。

## 8. 总结

知道如何表示和操作字符串对程序员来说是非常重要的，因为我们经常需要处理文本信息。Python 中操作字符串可以用拼接、索引、切片等运算符，也可以使用字符串类型提供的非常丰富的方法。
