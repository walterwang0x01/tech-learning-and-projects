# Java集合框架
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 集合框架概述

### 1.1 集合框架结构

Java集合框架主要分为两大类：

- **Collection接口**：单列集合
  - List：有序、可重复
  - Set：无序、不可重复
  - Queue：队列
- **Map接口**：双列集合，键值对

### 1.2 集合框架层次结构

```
Collection
├── List
│   ├── ArrayList
│   ├── LinkedList
│   └── Vector
├── Set
│   ├── HashSet
│   ├── LinkedHashSet
│   └── TreeSet
└── Queue
    ├── PriorityQueue
    └── Deque
        └── ArrayDeque

Map
├── HashMap
├── LinkedHashMap
├── TreeMap
└── Hashtable
```

## 2. List接口

### 2.1 ArrayList

#### 2.1.1 特点

- **底层实现**：动态数组
- **特点**：
  - 有序、可重复
  - 支持随机访问，通过索引访问元素
  - 插入和删除效率较低（需要移动元素）
  - 线程不安全

#### 2.1.2 常用方法

```java
List<String> list = new ArrayList<>();
list.add("元素1");           // 添加元素
list.get(0);                 // 获取元素
list.remove(0);              // 删除元素
list.size();                 // 获取大小
list.contains("元素1");      // 判断是否包含
list.isEmpty();              // 判断是否为空
```

#### 2.1.3 扩容机制

- **初始容量**：10
- **扩容时机**：当元素个数超过当前容量时
- **扩容大小**：原容量的1.5倍

### 2.2 LinkedList

#### 2.2.1 特点

- **底层实现**：双向链表
- **特点**：
  - 有序、可重复
  - 不支持随机访问
  - 插入和删除效率高（只需修改指针）
  - 线程不安全

#### 2.2.2 常用方法

```java
List<String> list = new LinkedList<>();
list.add("元素1");
list.addFirst("头部元素");
list.addLast("尾部元素");
list.removeFirst();
list.removeLast();
```

### 2.3 Vector

#### 2.3.1 特点

- **底层实现**：动态数组
- **特点**：
  - 线程安全（方法使用synchronized修饰）
  - 性能较低
  - 不推荐使用

### 2.4 ArrayList vs LinkedList

| 特性 | ArrayList | LinkedList |
|------|-----------|------------|
| 底层实现 | 动态数组 | 双向链表 |
| 随机访问 | 快(O(1)) | 慢(O(n)) |
| 插入删除 | 慢(O(n)) | 快(O(1)) |
| 内存占用 | 较小 | 较大 |
| 适用场景 | 查询多、增删少 | 增删多、查询少 |

## 3. Set接口

### 3.1 HashSet

#### 3.1.1 特点

- **底层实现**：HashMap（使用HashMap的key存储元素）
- **特点**：
  - 无序、不可重复
  - 允许null值
  - 线程不安全
  - 查找效率高

#### 3.1.2 常用方法

```java
Set<String> set = new HashSet<>();
set.add("元素1");
set.remove("元素1");
set.contains("元素1");
set.size();
```

### 3.2 LinkedHashSet

#### 3.2.1 特点

- **底层实现**：LinkedHashMap
- **特点**：
  - 有序（插入顺序）、不可重复
  - 性能略低于HashSet
  - 线程不安全

### 3.3 TreeSet

#### 3.3.1 特点

- **底层实现**：TreeMap（红黑树）
- **特点**：
  - 有序（自然排序或自定义排序）、不可重复
  - 不允许null值
  - 线程不安全
  - 查找、插入、删除时间复杂度为O(log n)

#### 3.3.2 使用示例

```java
Set<String> set = new TreeSet<>();
set.add("c");
set.add("a");
set.add("b");
// 输出：[a, b, c]，自动排序
```

## 4. Map接口

### 4.1 HashMap

#### 4.1.1 特点

- **底层实现**：数组 + 链表 + 红黑树（JDK 1.8）
- **特点**：
  - 无序、键不可重复
  - 允许null键和null值
  - 线程不安全
  - 查找、插入、删除效率高（平均O(1)）

#### 4.1.2 数据结构

- **JDK 1.7**：数组 + 链表
- **JDK 1.8**：数组 + 链表 + 红黑树
  - 当链表长度超过8时，转换为红黑树
  - 当红黑树节点数小于6时，转换为链表

#### 4.1.3 常用方法

```java
Map<String, Object> map = new HashMap<>();
map.put("key1", "value1");    // 添加键值对
map.get("key1");              // 获取值
map.remove("key1");           // 删除键值对
map.containsKey("key1");      // 判断是否包含键
map.containsValue("value1"); // 判断是否包含值
map.size();                   // 获取大小
```

#### 4.1.4 扩容机制

- **初始容量**：16
- **负载因子**：0.75
- **扩容时机**：当元素个数 > 容量 × 负载因子时
- **扩容大小**：原容量的2倍

#### 4.1.5 线程安全问题

HashMap是线程不安全的，在多线程环境下可能出现：
- 数据丢失
- 死循环（JDK 1.7）
- 数据不一致

**解决方案**：
- 使用ConcurrentHashMap
- 使用Collections.synchronizedMap()
- 使用Hashtable（不推荐）

### 4.2 LinkedHashMap

#### 4.2.1 特点

- **底层实现**：HashMap + 双向链表
- **特点**：
  - 有序（插入顺序或访问顺序）
  - 线程不安全
  - 性能略低于HashMap

### 4.3 TreeMap

#### 4.3.1 特点

- **底层实现**：红黑树
- **特点**：
  - 有序（自然排序或自定义排序）
  - 不允许null键
  - 线程不安全
  - 查找、插入、删除时间复杂度为O(log n)

### 4.4 Hashtable

#### 4.4.1 特点

- **底层实现**：数组 + 链表
- **特点**：
  - 线程安全（方法使用synchronized修饰）
  - 不允许null键和null值
  - 性能较低
  - 不推荐使用

### 4.5 ConcurrentHashMap

#### 4.5.1 特点

- **JDK 1.7**：分段锁（Segment）
- **JDK 1.8**：CAS + synchronized
- **特点**：
  - 线程安全
  - 性能高
  - 推荐使用

## 5. Queue接口

### 5.1 PriorityQueue

#### 5.1.1 特点

- **底层实现**：堆（完全二叉树）
- **特点**：
  - 优先级队列
  - 元素按照优先级排序
  - 线程不安全

#### 5.1.2 使用示例

```java
Queue<Integer> queue = new PriorityQueue<>();
queue.offer(3);
queue.offer(1);
queue.offer(2);
// 输出：1, 2, 3（按优先级排序）
```

### 5.2 ArrayDeque

#### 5.2.1 特点

- **底层实现**：循环数组
- **特点**：
  - 双端队列
  - 可以作为栈或队列使用
  - 线程不安全
  - 性能优于Stack和LinkedList

## 6. 集合遍历

### 6.1 增强for循环

```java
for (String item : list) {
    System.out.println(item);
}
```

### 6.2 迭代器

```java
Iterator<String> iterator = list.iterator();
while (iterator.hasNext()) {
    String item = iterator.next();
    System.out.println(item);
}
```

### 6.3 Lambda表达式

```java
list.forEach(item -> System.out.println(item));
```

### 6.4 Stream API

```java
list.stream()
    .filter(item -> item.startsWith("a"))
    .forEach(System.out::println);
```

## 7. 集合工具类

### 7.1 Collections

#### 7.1.1 排序

```java
Collections.sort(list);
Collections.sort(list, Comparator.reverseOrder());
```

#### 7.1.2 查找

```java
int index = Collections.binarySearch(list, "元素");
```

#### 7.1.3 同步包装

```java
List<String> syncList = Collections.synchronizedList(list);
Map<String, Object> syncMap = Collections.synchronizedMap(map);
```

#### 7.1.4 其他常用方法

```java
Collections.reverse(list);        // 反转
Collections.shuffle(list);         // 随机打乱
Collections.max(list);             // 最大值
Collections.min(list);             // 最小值
Collections.fill(list, "值");      // 填充
```

### 7.2 Arrays

#### 7.2.1 常用方法

```java
Arrays.sort(array);                // 排序
Arrays.binarySearch(array, value); // 二分查找
Arrays.asList(array);              // 转换为List
Arrays.toString(array);            // 转字符串
```

## 8. 集合选择指南

### 8.1 List选择

- **需要随机访问**：ArrayList
- **需要频繁插入删除**：LinkedList
- **需要线程安全**：CopyOnWriteArrayList或Collections.synchronizedList()

### 8.2 Set选择

- **需要快速查找，不关心顺序**：HashSet
- **需要保持插入顺序**：LinkedHashSet
- **需要排序**：TreeSet

### 8.3 Map选择

- **一般情况**：HashMap
- **需要保持插入顺序**：LinkedHashMap
- **需要排序**：TreeMap
- **需要线程安全**：ConcurrentHashMap

## 9. 性能对比

### 9.1 时间复杂度

| 操作 | ArrayList | LinkedList | HashMap | TreeMap |
|------|-----------|------------|---------|---------|
| 查找 | O(1) | O(n) | O(1) | O(log n) |
| 插入 | O(n) | O(1) | O(1) | O(log n) |
| 删除 | O(n) | O(1) | O(1) | O(log n) |

### 9.2 空间复杂度

- **ArrayList**：O(n)
- **LinkedList**：O(n)
- **HashMap**：O(n)
- **TreeMap**：O(n)

## 10. 最佳实践

1. **选择合适的集合类型**：根据使用场景选择最合适的集合
2. **初始化容量**：如果知道大概容量，初始化时指定容量，避免频繁扩容
3. **使用泛型**：明确指定集合的泛型类型
4. **避免在遍历时修改集合**：使用迭代器的remove()方法或使用CopyOnWriteArrayList
5. **线程安全**：多线程环境下使用并发集合
6. **合理使用Stream API**：简化集合操作代码
7. **注意null值**：某些集合不允许null值，使用时注意
## 🎬 推荐视频资源

- [Java Brains - Java Collections](https://www.youtube.com/watch?v=GdAon80-0KA) — Java集合框架详解
- [Coding with John - Java Collections](https://www.youtube.com/watch?v=viTainYWwbI) — 集合框架实战
