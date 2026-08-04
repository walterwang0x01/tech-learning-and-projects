# Python数据结构-字典
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 字典概述

Python 程序中的字典跟现实生活中的字典很像，它以键值对（键和值的组合）的方式把数据组织到一起，我们可以通过键找到与之对应的值并进行操作。就像《新华字典》中，每个字（键）都有与它对应的解释（值）一样，每个字和它的解释合在一起就是字典中的一个条目，而字典中通常包含了很多个这样的条目。

## 2. 创建和使用字典

### 2.1 使用字面量语法

Python 中创建字典可以使用`{}`字面量语法，字典的`{}`中的元素是以键值对的形式存在的，每个元素由`:`分隔的两个值构成，`:`前面是键，`:`后面是值。

```python
person = {
    'name': '王大锤',
    'age': 55,
    'height': 168,
    'weight': 60,
    'addr': '成都市武侯区科华北路62号1栋101', 
    'tel': '13122334455',
    'emergence contact': '13800998877'
}
print(person)
```

### 2.2 使用dict函数

```python
# dict函数(构造器)中的每一组参数就是字典中的一组键值对
person = dict(name='王大锤', age=55, height=168, weight=60)
print(person)  # {'name': '王大锤', 'age': 55, 'height': 168, 'weight': 60}

# 可以通过Python内置函数zip压缩两个序列并创建字典
items1 = dict(zip('ABCDE', '12345'))
print(items1)  # {'A': '1', 'B': '2', 'C': '3', 'D': '4', 'E': '5'}
```

### 2.3 字典生成式

```python
# 用字典生成式语法创建字典
items3 = {x: x ** 3 for x in range(1, 6)}
print(items3)  # {1: 1, 2: 8, 3: 27, 4: 64, 5: 125}
```

### 2.4 获取字典信息

```python
person = {
    'name': '王大锤',
    'age': 55,
    'height': 168,
    'weight': 60,
    'addr': '成都市武侯区科华北路62号1栋101'
}
print(len(person))  # 5
```

## 3. 字典的运算

### 3.1 成员运算

成员运算可以判定指定的键在不在字典中。

```python
person = {'name': '王大锤', 'age': 55, 'height': 168}
print('name' in person)  # True
print('tel' in person)   # False
```

### 3.2 索引运算

字典的索引不同于列表的索引，列表中的元素因为有属于自己有序号，所以列表的索引是一个整数；字典中因为保存的是键值对，所以字典需要用键去索引对应的值。

```python
person = {'name': '王大锤', 'age': 55, 'height': 168, 'weight': 60}
print(person['name'])  # 王大锤
print(person['age'])   # 55

# 修改值
person['age'] = 25
person['height'] = 178

# 添加新的键值对
person['tel'] = '13122334455'
```

**重要**：
- **字典中的键必须是不可变类型**，例如整数（`int`）、浮点数（`float`）、字符串（`str`）、元组（`tuple`）等类型
- 列表（`list`）和集合（`set`）不能作为字典中的键
- 字典类型本身也不能再作为字典中的键
- 但是列表、集合、字典都可以作为字典中的值

**注意**：在通过索引运算获取字典中的值时，如指定的键没有在字典中，将会引发`KeyError`异常。

### 3.3 嵌套字典

字典的值可以是任何类型，包括字典本身。

```python
person = {
    'name': '王大锤',
    'age': 55,
    'addr': ['成都市武侯区科华北路62号1栋101', '北京市西城区百万庄大街1号'],
    'car': {
        'brand': 'BMW X7',
        'maxSpeed': '250',
        'length': 5170,
        'width': 2000,
        'height': 1835,
        'displacement': 3.0
    }
}
print(person['car']['brand'])  # BMW X7
```

## 4. 字典的方法

### 4.1 get方法

`get`方法可以通过键来获取对应的值。跟索引运算不同的是，`get`方法在字典中没有指定的键时不会产生异常，而是返回`None`或指定的默认值。

```python
person = {'name': '王大锤', 'age': 25, 'height': 178}
print(person.get('name'))       # 王大锤
print(person.get('sex'))        # None
print(person.get('sex', True))  # True
```

### 4.2 keys、values和items方法

- `keys()`方法：获取字典中所有的键
- `values()`方法：获取字典中所有的值
- `items()`方法：将键和值组装成二元组

```python
person = {'name': '王大锤', 'age': 25, 'height': 178}
print(person.keys())    # dict_keys(['name', 'age', 'height'])
print(person.values())  # dict_values(['王大锤', 25, 178])
print(person.items())   # dict_items([('name', '王大锤'), ('age', 25), ('height', 178)])

# 遍历字典
for key in person:
    print(f'{key}:\t{person[key]}')

# 使用items方法遍历
for key, value in person.items():
    print(f'{key}:\t{value}')
```

### 4.3 update方法

`update`方法实现两个字典的合并操作。当执行`x.update(y)`操作时，`x`跟`y`相同的键对应的值会被`y`中的值更新，而`y`中有但`x`中没有的键值对会直接添加到`x`中。

```python
person1 = {'name': '王大锤', 'age': 55, 'height': 178}
person2 = {'age': 25, 'addr': '成都市武侯区科华北路62号1栋101'}
person1.update(person2)
print(person1)  # {'name': '王大锤', 'age': 25, 'height': 178, 'addr': '成都市武侯区科华北路62号1栋101'}
```

**Python 3.9+**：也可以使用`|`运算符来完成同样的操作。

```python
person1 = {'name': '王大锤', 'age': 55, 'height': 178}
person2 = {'age': 25, 'addr': '成都市武侯区科华北路62号1栋101'}
person1 |= person2
print(person1)  # {'name': '王大锤', 'age': 25, 'height': 178, 'addr': '成都市武侯区科华北路62号1栋101'}
```

### 4.4 pop和popitem方法

- `pop(key)`：删除指定键的键值对，返回对应的值
- `popitem()`：删除并返回字典中的最后一对键值对（Python 3.7+保证是插入顺序）

```python
person = {'name': '王大锤', 'age': 25, 'height': 178, 'addr': '成都市武侯区科华北路62号1栋101'}
print(person.pop('age'))  # 25
print(person)             # {'name': '王大锤', 'height': 178, 'addr': '成都市武侯区科华北路62号1栋101'}

print(person.popitem())   # ('addr', '成都市武侯区科华北路62号1栋101')
print(person)             # {'name': '王大锤', 'height': 178}
```

### 4.5 clear方法

`clear`方法会清空字典中所有的键值对。

```python
person.clear()
print(person)  # {}
```

### 4.6 del关键字

从字典中删除元素也可以使用`del`关键字。

```python
person = {'name': '王大锤', 'age': 25, 'height': 178}
del person['age']
print(person)  # {'name': '王大锤', 'height': 178}
```

## 5. 字典的应用

### 5.1 统计字符出现次数

```python
sentence = input('请输入一段话: ')
counter = {}
for ch in sentence:
    if 'A' <= ch <= 'Z' or 'a' <= ch <= 'z':
        counter[ch] = counter.get(ch, 0) + 1

sorted_keys = sorted(counter, key=counter.get, reverse=True)
for key in sorted_keys:
    print(f'{key} 出现了 {counter[key]} 次.')
```

### 5.2 字典生成式应用

在一个字典中保存了股票的代码和价格，找出股价大于100元的股票并创建一个新的字典。

```python
stocks = {
    'AAPL': 191.88,
    'GOOG': 1186.96,
    'IBM': 149.24,
    'ORCL': 48.44,
    'ACN': 166.89,
    'FB': 208.09,
    'SYMC': 21.29
}

# 使用字典生成式
stocks2 = {key: value for key, value in stocks.items() if value > 100}
print(stocks2)  # {'AAPL': 191.88, 'GOOG': 1186.96, 'IBM': 149.24, 'ACN': 166.89, 'FB': 208.09}
```

## 6. 字典的特点

1. **键的唯一性**：字典中的键必须是唯一的
2. **键的不可变性**：字典中的键必须是不可变类型
3. **值的可变性**：字典中的值可以是任何类型
4. **无序性（Python 3.7之前）**：Python 3.7之前字典是无序的，Python 3.7+保证插入顺序

## 7. 字典性能说明

字典底层使用了哈希表（散列表）实现，所以：
- 查找、插入、删除操作的平均时间复杂度为O(1)
- 字典的成员运算在性能上要优于列表的成员运算

## 8. 总结

字典是 Python 中非常重要的数据结构，它以键值对的方式组织数据，非常适合用来表示具有映射关系的数据。字典的键必须是不可变类型，值可以是任何类型。掌握字典的创建、操作和方法对于 Python 编程非常重要。
