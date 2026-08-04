# Python正则表达式
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 正则表达式概述

在编写处理字符串的程序时，经常会遇到在一段文本中查找符合某些规则的字符串的需求，正则表达式就是用于描述这些规则的工具。我们可以使用正则表达式来定义字符串的匹配模式，即如何检查一个字符串是否有跟某种模式匹配的部分或者从一个字符串中将与模式匹配的部分提取出来或者替换掉。

Python 通过标准库中的`re`模块来支持正则表达式操作。

## 2. 正则表达式语法

### 2.1 基本符号

| 符号           | 解释                             | 示例               | 说明                                                         |
| -------------- | -------------------------------- | ------------------ | ------------------------------------------------------------ |
| `.`            | 匹配任意字符                     | `b.t`              | 可以匹配bat / but / b#t / b1t等                              |
| `\w`           | 匹配字母/数字/下划线             | `b\wt`             | 可以匹配bat / b1t / b_t等<br>但不能匹配b#t                   |
| `\s`           | 匹配空白字符（包括\r、\n、\t等） | `love\syou`        | 可以匹配love you                                             |
| `\d`           | 匹配数字                         | `\d\d`             | 可以匹配01 / 23 / 99等                                       |
| `\b`           | 匹配单词的边界                   | `\bThe\b`          |                                                              |
| `^`            | 匹配字符串的开始                 | `^The`             | 可以匹配The开头的字符串                                      |
| `$`            | 匹配字符串的结束                 | `.exe$`            | 可以匹配.exe结尾的字符串                                     |
| `\W`           | 匹配非字母/数字/下划线           | `b\Wt`             | 可以匹配b#t / b@t等<br>但不能匹配but / b1t / b_t等           |
| `\S`           | 匹配非空白字符                   | `love\Syou`        | 可以匹配love#you等<br>但不能匹配love you                     |
| `\D`           | 匹配非数字                       | `\d\D`             | 可以匹配9a / 3# / 0F等                                       |
| `\B`           | 匹配非单词边界                   | `\Bio\B`           |                                                              |

### 2.2 字符集

| 符号  | 解释                             | 示例       | 说明                         |
| ----- | -------------------------------- | ---------- | ---------------------------- |
| `[]`  | 匹配来自字符集的任意单一字符     | `[aeiou]`  | 可以匹配任一元音字母字符     |
| `[^]` | 匹配不在字符集中的任意单一字符   | `[^aeiou]` | 可以匹配任一非元音字母字符   |

### 2.3 量词

| 符号      | 解释                   | 示例     | 说明       |
| --------- | ---------------------- | -------- | ---------- |
| `*`       | 匹配0次或多次          | `\w*`    |            |
| `+`       | 匹配1次或多次          | `\w+`    |            |
| `?`       | 匹配0次或1次           | `\w?`    |            |
| `{N}`     | 匹配N次                | `\w{3}`  |            |
| `{M,}`    | 匹配至少M次            | `\w{3,}` |            |
| `{M,N}`   | 匹配至少M次至多N次     | `\w{3,6}` |            |
| `*?`      | 重复任意次，但尽可能少 | `a.*?b`  | 非贪婪匹配 |
| `+?`      | 重复1次或多次，但尽可能少 |        |            |
| `??`      | 重复0次或1次，但尽可能少 |        |            |
| `{M,N}?`  | 重复M到N次，但尽可能少 |          |            |

### 2.4 分组和捕获

| 符号           | 解释                             | 示例               | 说明                                                         |
| -------------- | -------------------------------- | ------------------ | ------------------------------------------------------------ |
| `\|`            | 分支                             | `foo\|bar`          | 可以匹配foo或者bar                                           |
| `(exp)`        | 匹配exp并捕获到自动命名的组中    |                    |                                                              |
| `(?<name>exp)` | 匹配exp并捕获到名为name的组中    |                    |                                                              |
| `(?:exp)`      | 匹配exp但是不捕获匹配的文本      |                    |                                                              |
| `(?=exp)`      | 匹配exp前面的位置                | `\b\w+(?=ing)`     | 可以匹配I'm dancing中的danc                                  |
| `(?<=exp)`     | 匹配exp后面的位置                | `(?<=\bdanc)\w+\b` | 前瞻断言                                                     |
| `(?!exp)`      | 匹配后面不是exp的位置            |                    | 负向前瞻断言                                                 |
| `(?<!exp)`     | 匹配前面不是exp的位置            |                    | 负向后瞻断言                                                 |

**说明**：如果需要匹配的字符是正则表达式中的特殊字符，那么可以使用`\`进行转义处理，例如想匹配小数点可以写成`\.`，想匹配圆括号必须写成`\(`和`\)`。

## 3. re模块函数

Python 提供了`re`模块来支持正则表达式相关操作，下面是`re`模块中的核心函数。

| 函数                                           | 说明                                                         |
| ---------------------------------------------- | ------------------------------------------------------------ |
| `compile(pattern, flags=0)`                    | 编译正则表达式返回正则表达式对象                             |
| `match(pattern, string, flags=0)`              | 用正则表达式匹配字符串 成功返回匹配对象 否则返回`None`       |
| `search(pattern, string, flags=0)`             | 搜索字符串中第一次出现正则表达式的模式 成功返回匹配对象 否则返回`None` |
| `split(pattern, string, maxsplit=0, flags=0)`  | 用正则表达式指定的模式分隔符拆分字符串 返回列表              |
| `sub(pattern, repl, string, count=0, flags=0)` | 用指定的字符串替换原字符串中与正则表达式匹配的模式 可以用`count`指定替换的次数 |
| `fullmatch(pattern, string, flags=0)`          | `match`函数的完全匹配（从字符串开头到结尾）版本              |
| `findall(pattern, string, flags=0)`            | 查找字符串所有与正则表达式匹配的模式 返回字符串的列表        |
| `finditer(pattern, string, flags=0)`           | 查找字符串所有与正则表达式匹配的模式 返回一个迭代器          |
| `purge()`                                      | 清除隐式编译的正则表达式的缓存                               |

### 3.1 常用标志（flags）

| 标志                        | 说明             |
| --------------------------- | ---------------- |
| `re.I` / `re.IGNORECASE`    | 忽略大小写匹配标记 |
| `re.M` / `re.MULTILINE`     | 多行匹配标记     |
| `re.S` / `re.DOTALL`        | 让`.`匹配包括换行符在内的所有字符 |

## 4. 使用原始字符串

在书写正则表达式时使用了"原始字符串"的写法（在字符串前面加上了`r`），所谓"原始字符串"就是字符串中的每个字符都是它原始的意义。

```python
import re

# 使用原始字符串（推荐）
pattern = r'\d+'

# 不使用原始字符串（不推荐）
pattern = '\\d+'
```

## 5. 正则表达式应用示例

### 5.1 验证用户名和QQ号

```python
"""
要求：用户名必须由字母、数字或下划线构成且长度在6~20个字符之间，QQ号是5~12的数字且首位不能为0
"""
import re

username = input('请输入用户名: ')
qq = input('请输入QQ号: ')

# match函数的第一个参数是正则表达式字符串或正则表达式对象
# match函数的第二个参数是要跟正则表达式做匹配的字符串对象
m1 = re.match(r'^[0-9a-zA-Z_]{6,20}$', username)
if not m1:
    print('请输入有效的用户名.')

# fullmatch函数要求字符串和正则表达式完全匹配
m2 = re.fullmatch(r'[1-9]\d{4,11}', qq)
if not m2:
    print('请输入有效的QQ号.')

if m1 and m2:
    print('你输入的信息是有效的!')
```

### 5.2 提取手机号码

```python
import re

# 创建正则表达式对象，使用了前瞻和回顾来保证手机号前后不应该再出现数字
pattern = re.compile(r'(?<=\D)1[34578]\d{9}(?=\D)')
sentence = '''重要的事情说8130123456789遍，我的手机号是13512346789这个靓号，
不是15600998765，也不是110或119，王大锤的手机号才是15600998765。'''

# 方法一：查找所有匹配并保存到一个列表中
tels_list = re.findall(pattern, sentence)
for tel in tels_list:
    print(tel)

# 方法二：通过迭代器取出匹配对象并获得匹配的内容
for temp in pattern.finditer(sentence):
    print(temp.group())

# 方法三：通过search函数指定搜索位置找出所有匹配
m = pattern.search(sentence)
while m:
    print(m.group())
    m = pattern.search(sentence, m.end())
```

### 5.3 替换字符串

```python
import re

sentence = 'Oh, shit! 你是傻逼吗? Fuck you.'
purified = re.sub('fuck|shit|[傻煞沙][比笔逼叉缺吊碉雕]',
                  '*', sentence, flags=re.IGNORECASE)
print(purified)  # Oh, *! 你是*吗? * you.
```

### 5.4 拆分字符串

```python
import re

poem = '窗前明月光，疑是地上霜。举头望明月，低头思故乡。'
sentences_list = re.split(r'[，。]', poem)
sentences_list = [sentence for sentence in sentences_list if sentence]
for sentence in sentences_list:
    print(sentence)
```

### 5.5 提取邮箱地址

```python
import re

text = '联系我们：email@example.com 或 admin@test.cn'
pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
emails = re.findall(pattern, text)
for email in emails:
    print(email)
```

## 6. Pattern对象和Match对象

### 6.1 Pattern对象

如果正则表达式需要重复使用，应该先通过`compile`函数编译正则表达式并创建出正则表达式对象。

```python
import re

# 编译正则表达式
pattern = re.compile(r'\d+')

# 使用Pattern对象的方法
result = pattern.search('abc123def456')
print(result.group())  # 123
```

### 6.2 Match对象

`match`、`search`等方法成功匹配后会返回`Match`对象。

```python
import re

pattern = re.compile(r'(\d+)-(\d+)-(\d+)')
match = pattern.search('2023-12-16')
if match:
    print(match.group())      # 2023-12-16（完整匹配）
    print(match.group(1))     # 2023（第一个分组）
    print(match.group(2))     # 12（第二个分组）
    print(match.group(3))     # 16（第三个分组）
    print(match.groups())     # ('2023', '12', '16')（所有分组）
```

## 7. 分组和命名分组

### 7.1 普通分组

```python
import re

pattern = re.compile(r'(\d{4})-(\d{2})-(\d{2})')
match = pattern.search('日期是2023-12-16')
if match:
    year, month, day = match.groups()
    print(f'年份：{year}，月份：{month}，日期：{day}')
```

### 7.2 命名分组

```python
import re

pattern = re.compile(r'(?P<year>\d{4})-(?P<month>\d{2})-(?P<day>\d{2})')
match = pattern.search('日期是2023-12-16')
if match:
    print(match.group('year'))   # 2023
    print(match.group('month'))  # 12
    print(match.group('day'))    # 16
```

## 8. 常用正则表达式示例

### 8.1 匹配IP地址

```python
import re

ip_pattern = r'^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(25[0-5]|2[0-4]\d|[01]?\d\d?)$'
ip = '192.168.1.1'
if re.match(ip_pattern, ip):
    print('有效的IP地址')
```

### 8.2 匹配URL

```python
import re

url_pattern = r'https?://(?:[-\w.])+(?:[:\d]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:#(?:\w)*)?)?'
url = 'https://www.example.com/path?param=value'
if re.match(url_pattern, url):
    print('有效的URL')
```

### 8.3 匹配日期

```python
import re

date_pattern = r'\d{4}-\d{2}-\d{2}'
text = '今天是2023-12-16，明天是2023-12-17'
dates = re.findall(date_pattern, text)
print(dates)  # ['2023-12-16', '2023-12-17']
```

## 9. 正则表达式最佳实践

1. **使用原始字符串**：在正则表达式字符串前加`r`
2. **预编译正则表达式**：如果正则表达式需要重复使用，使用`re.compile()`预编译
3. **使用非贪婪匹配**：使用`*?`、`+?`、`??`等非贪婪匹配符
4. **合理使用分组**：使用分组提取需要的信息
5. **测试正则表达式**：使用在线工具测试正则表达式的正确性

## 10. 总结

正则表达式在字符串的处理和匹配上非常强大，是处理文本数据的利器。Python 的`re`模块提供了完整的正则表达式支持，包括匹配、搜索、替换、拆分等功能。掌握正则表达式的基本语法和`re`模块的使用方法，可以大大提高文本处理的效率。

