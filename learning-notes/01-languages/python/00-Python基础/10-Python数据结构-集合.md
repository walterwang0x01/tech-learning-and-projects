# Python数据结构-集合
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 集合概述

在学习了列表和元组之后，我们再来学习一种容器型的数据类型，它的名字叫集合（set）。Python 程序中的集合跟数学上的集合没有什么本质区别。

集合需要满足以下要求：

1. **无序性**：一个集合中，每个元素的地位都是相同的，元素之间是无序的
2. **互异性**：一个集合中，任何两个元素都是不相同的，即元素在集合中只能出现一次
3. **确定性**：给定一个集合和一个任意元素，该元素要么属这个集合，要么不属于这个集合，二者必居其一

**集合的成员运算在性能上要优于列表的成员运算**，这是集合的底层存储特性决定的。

## 2. 创建集合

### 2.1 使用字面量语法

在 Python 中，创建集合可以使用`{}`字面量语法，`{}`中需要至少有一个元素，因为没有元素的`{}`并不是空集合而是一个空字典。

```python
set1 = {1, 2, 3, 3, 3, 2}
print(set1)  # {1, 2, 3}（重复元素会被自动去除）

set2 = {'banana', 'pitaya', 'apple', 'apple', 'banana', 'grape'}
print(set2)  # {'banana', 'pitaya', 'apple', 'grape'}
```

### 2.2 使用set函数

可以使用 Python 内置函数`set`来创建一个集合。

```python
set3 = set('hello')
print(set3)  # {'h', 'e', 'l', 'o'}（重复的字符'l'只会在集合中出现一次）

set4 = set([1, 2, 2, 3, 3, 3, 2, 1])
print(set4)  # {1, 2, 3}

# 创建空集合
empty_set = set()
print(empty_set)  # set()
```

### 2.3 集合生成式

还可以使用生成式语法来创建集合。

```python
set5 = {num for num in range(1, 20) if num % 3 == 0 or num % 7 == 0}
print(set5)  # {3, 6, 7, 9, 12, 14, 15, 18}
```

### 2.4 hashable类型要求

集合中的元素必须是`hashable`类型，所谓`hashable`类型指的是能够计算出哈希码的数据类型。

- **hashable类型**：整数（`int`）、浮点小数（`float`）、布尔值（`bool`）、字符串（`str`）、元组（`tuple`）等
- **非hashable类型**：列表（`list`）、集合（`set`）、字典（`dict`）等可变类型

```python
# 正确：使用hashable类型
set1 = {1, 2, 3, 'hello', (1, 2, 3)}

# 错误：不能使用可变类型
# set2 = {[1, 2, 3]}  # TypeError: unhashable type: 'list'
# set3 = {{1, 2, 3}}  # TypeError: unhashable type: 'set'
```

## 3. 元素的遍历

我们可以通过`len`函数来获得集合中有多少个元素，但是我们不能通过索引运算来遍历集合中的元素，因为集合元素并没有特定的顺序。

```python
set1 = {'Python', 'C++', 'Java', 'Kotlin', 'Swift'}
for elem in set1:
    print(elem)
```

**注意**：通过输出顺序体会一下集合的无序性。

## 4. 集合的运算

### 4.1 成员运算

可以通过成员运算`in`和`not in`检查元素是否在集合中。

```python
set1 = {11, 12, 13, 14, 15}
print(10 in set1)      # False
print(15 in set1)      # True

set2 = {'Python', 'Java', 'C++', 'Swift'}
print('Ruby' in set2)  # False
print('Java' in set2)  # True
```

### 4.2 二元运算

集合的二元运算主要指集合的交集、并集、差集、对称差等运算，这些运算可以通过运算符来实现，也可以通过集合类型的方法来实现。

```python
set1 = {1, 2, 3, 4, 5, 6, 7}
set2 = {2, 4, 6, 8, 10}

# 交集
print(set1 & set2)                      # {2, 4, 6}
print(set1.intersection(set2))          # {2, 4, 6}

# 并集
print(set1 | set2)                      # {1, 2, 3, 4, 5, 6, 7, 8, 10}
print(set1.union(set2))                 # {1, 2, 3, 4, 5, 6, 7, 8, 10}

# 差集
print(set1 - set2)                      # {1, 3, 5, 7}
print(set1.difference(set2))            # {1, 3, 5, 7}

# 对称差
print(set1 ^ set2)                      # {1, 3, 5, 7, 8, 10}
print(set1.symmetric_difference(set2))  # {1, 3, 5, 7, 8, 10}
```

### 4.3 复合赋值运算

集合的二元运算还可以跟赋值运算一起构成复合赋值运算。

```python
set1 = {1, 3, 5, 7}
set2 = {2, 4, 6}
set1 |= set2  # 相当于 set1 = set1 | set2
# set1.update(set2)  # 等同效果
print(set1)  # {1, 2, 3, 4, 5, 6, 7}

set3 = {3, 6, 9}
set1 &= set3  # 相当于 set1 = set1 & set3
# set1.intersection_update(set3)  # 等同效果
print(set1)  # {3, 6}

set2 -= set1  # 相当于 set2 = set2 - set1
# set2.difference_update(set1)  # 等同效果
print(set2)  # {2, 4}
```

### 4.4 比较运算

两个集合可以用`==`和`!=`进行相等性判断，还可以判断子集和超集关系。

```python
set1 = {1, 3, 5}
set2 = {1, 2, 3, 4, 5}
set3 = {5, 4, 3, 2, 1}

print(set1 < set2)   # True（set1是set2的真子集）
print(set1 <= set2)  # True（set1是set2的子集）
print(set2 < set3)   # False（set2不是set3的真子集）
print(set2 <= set3)  # True（set2是set3的子集）
print(set2 > set1)   # True（set2是set1的超集）
print(set2 == set3)  # True（两个集合元素相同）

print(set1.issubset(set2))    # True
print(set2.issuperset(set1))  # True
```

## 5. 集合的方法

### 5.1 添加和删除元素

```python
set1 = {1, 10, 100}

# 添加元素
set1.add(1000)
set1.add(10000)
print(set1)  # {1, 100, 1000, 10, 10000}

# 删除元素
set1.discard(10)  # 如果元素不存在，不会报错
if 100 in set1:
    set1.remove(100)  # 如果元素不存在，会引发KeyError
print(set1)  # {1, 1000, 10000}

# pop方法：随机删除一个元素并返回
element = set1.pop()
print(element)  # 随机返回一个元素
print(set1)

# 清空元素
set1.clear()
print(set1)  # set()
```

**说明**：
- `remove`方法在元素不存在时会引发`KeyError`错误
- `discard`方法在元素不存在时不会报错
- `pop`方法可以从集合中随机删除一个元素，该方法在删除元素的同时会返回被删除的元素

### 5.2 isdisjoint方法

`isdisjoint`方法可以判断两个集合有没有相同的元素，如果没有相同元素，该方法返回`True`，否则该方法返回`False`。

```python
set1 = {'Java', 'Python', 'C++', 'Kotlin'}
set2 = {'Kotlin', 'Swift', 'Java', 'Dart'}
set3 = {'HTML', 'CSS', 'JavaScript'}

print(set1.isdisjoint(set2))  # False（有相同元素）
print(set1.isdisjoint(set3))  # True（没有相同元素）
```

## 6. 不可变集合（frozenset）

Python 中还有一种不可变类型的集合，名字叫`frozenset`。`set`跟`frozenset`的区别就如同`list`跟`tuple`的区别，`frozenset`由于是不可变类型，能够计算出哈希码，因此它可以作为`set`中的元素。

```python
fset1 = frozenset({1, 3, 5, 7})
fset2 = frozenset(range(1, 6))
print(fset1)          # frozenset({1, 3, 5, 7})
print(fset2)          # frozenset({1, 2, 3, 4, 5})
print(fset1 & fset2)  # frozenset({1, 3, 5})
print(fset1 | fset2)  # frozenset({1, 2, 3, 4, 5, 7})
print(fset1 - fset2)  # frozenset({7})
print(fset1 < fset2)  # False

# frozenset可以作为set的元素
set_with_fset = {fset1, fset2}
print(set_with_fset)
```

**注意**：除了不能添加和删除元素，`frozenset`在其他方面跟`set`是一样的。

## 7. 集合的应用场景

1. **去重**：快速去除列表中的重复元素
2. **成员测试**：快速判断元素是否在集合中
3. **集合运算**：进行交集、并集、差集等数学运算
4. **作为字典的键**：不可变的`frozenset`可以作为字典的键

### 7.1 去重示例

```python
# 列表去重
numbers = [1, 2, 2, 3, 3, 3, 4, 4, 4, 4]
unique_numbers = list(set(numbers))
print(unique_numbers)  # [1, 2, 3, 4]
```

## 8. 集合的特点

1. **无序性**：集合中的元素没有顺序
2. **互异性**：集合中不能有重复元素
3. **确定性**：元素要么属于集合，要么不属于集合
4. **不支持索引**：集合不支持索引运算
5. **hashable要求**：集合中的元素必须是hashable类型

## 9. 性能说明

集合底层使用了哈希存储（散列存储），所以：
- 成员运算的平均时间复杂度为O(1)
- 集合的成员运算在性能上要优于列表的成员运算
- 集合的插入、删除操作的平均时间复杂度为O(1)

## 10. 总结

Python 中的**集合类型是一种无序容器**，**不允许有重复元素**，由于底层使用了哈希存储，集合中的元素必须是`hashable`类型。集合与列表最大的区别在于**集合中的元素没有顺序**、所以**不能够通过索引运算访问元素**、但是集合可以执行交集、并集、差集等二元运算，也可以通过关系运算符检查两个集合是否存在超集、子集等关系。
