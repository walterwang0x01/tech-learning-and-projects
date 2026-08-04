# Java包装类与自动装箱拆箱
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 包装类概述

### 1.1 什么是包装类

Java为8种基本数据类型提供了对应的包装类，使基本类型可以像对象一样使用。

### 1.2 基本类型与包装类对应关系

| 基本类型 | 包装类 | 大小 |
|---------|--------|------|
| byte | Byte | 1字节 |
| short | Short | 2字节 |
| int | Integer | 4字节 |
| long | Long | 8字节 |
| float | Float | 4字节 |
| double | Double | 8字节 |
| char | Character | 2字节 |
| boolean | Boolean | 1位 |

### 1.3 为什么需要包装类

1. **集合框架**：集合只能存储对象，不能存储基本类型
2. **泛型**：泛型只能使用对象类型
3. **null值**：包装类可以表示null，基本类型不能
4. **方法调用**：某些方法需要对象参数

## 2. 包装类的使用

### 2.1 创建包装类对象

```java
// 方式1：使用构造方法（已废弃，不推荐）
Integer i1 = new Integer(100);

// 方式2：使用valueOf()方法（推荐）
Integer i2 = Integer.valueOf(100);

// 方式3：自动装箱
Integer i3 = 100;
```

### 2.2 基本类型与包装类转换

```java
// 基本类型转包装类（装箱）
int num = 100;
Integer integer = Integer.valueOf(num);

// 包装类转基本类型（拆箱）
Integer integer = Integer.valueOf(100);
int num = integer.intValue();
```

## 3. 自动装箱（Autoboxing）

### 3.1 什么是自动装箱

自动将基本类型转换为对应的包装类对象。

```java
// 自动装箱
Integer i = 100;  // 编译器自动转换为 Integer.valueOf(100)

// 等价于
Integer i = Integer.valueOf(100);
```

### 3.2 自动装箱示例

```java
// 赋值时自动装箱
Integer i1 = 100;
Double d1 = 3.14;
Boolean b1 = true;

// 方法调用时自动装箱
List<Integer> list = new ArrayList<>();
list.add(100);  // 自动装箱为Integer

// 返回值自动装箱
Integer getValue() {
    return 100;  // 自动装箱
}
```

## 4. 自动拆箱（Unboxing）

### 4.1 什么是自动拆箱

自动将包装类对象转换为对应的基本类型。

```java
// 自动拆箱
Integer i = Integer.valueOf(100);
int num = i;  // 编译器自动转换为 i.intValue()

// 等价于
int num = i.intValue();
```

### 4.2 自动拆箱示例

```java
Integer i = Integer.valueOf(100);

// 赋值时自动拆箱
int num = i;

// 运算时自动拆箱
int result = i + 10;  // i自动拆箱

// 方法调用时自动拆箱
printInt(i);  // i自动拆箱为int

void printInt(int num) {
    System.out.println(num);
}
```

## 5. 包装类的缓存机制

### 5.1 Integer缓存

Integer类缓存了-128到127之间的值。

```java
Integer i1 = 127;
Integer i2 = 127;
System.out.println(i1 == i2);  // true，使用缓存

Integer i3 = 128;
Integer i4 = 128;
System.out.println(i3 == i4);  // false，超出缓存范围
```

### 5.2 缓存范围

- **Byte**：-128 到 127（全部缓存）
- **Short**：-128 到 127
- **Integer**：-128 到 127（可通过JVM参数调整）
- **Long**：-128 到 127
- **Character**：0 到 127
- **Boolean**：true 和 false（全部缓存）
- **Float和Double**：没有缓存

### 5.3 缓存实现原理

```java
// Integer.valueOf()源码
public static Integer valueOf(int i) {
    if (i >= IntegerCache.low && i <= IntegerCache.high)
        return IntegerCache.cache[i + (-IntegerCache.low)];
    return new Integer(i);
}
```

## 6. 包装类的常用方法

### 6.1 类型转换

```java
// 字符串转基本类型
int num = Integer.parseInt("100");
double d = Double.parseDouble("3.14");
boolean b = Boolean.parseBoolean("true");

// 字符串转包装类
Integer i = Integer.valueOf("100");
Double d = Double.valueOf("3.14");

// 基本类型转字符串
String s1 = Integer.toString(100);
String s2 = String.valueOf(100);
String s3 = 100 + "";  // 不推荐
```

### 6.2 进制转换

```java
// 十进制转其他进制
String binary = Integer.toBinaryString(10);   // "1010"
String octal = Integer.toOctalString(10);     // "12"
String hex = Integer.toHexString(10);         // "a"

// 其他进制转十进制
int num1 = Integer.parseInt("1010", 2);       // 10
int num2 = Integer.parseInt("12", 8);        // 10
int num3 = Integer.parseInt("a", 16);        // 10
```

### 6.3 比较方法

```java
Integer i1 = 100;
Integer i2 = 200;

i1.compareTo(i2);        // -1（i1 < i2）
Integer.compare(i1, i2); // -1
```

### 6.4 其他常用方法

```java
Integer i = 100;

i.intValue();            // 拆箱为int
i.toString();            // 转字符串
i.hashCode();            // 哈希码
i.equals(100);           // 比较
Integer.max(10, 20);     // 最大值
Integer.min(10, 20);     // 最小值
```

## 7. 包装类的注意事项

### 7.1 == 和 equals()

```java
Integer i1 = 127;
Integer i2 = 127;
System.out.println(i1 == i2);        // true（缓存）
System.out.println(i1.equals(i2));   // true

Integer i3 = 128;
Integer i4 = 128;
System.out.println(i3 == i4);        // false（超出缓存）
System.out.println(i3.equals(i4));   // true（值相等）

// 推荐使用equals()比较包装类
```

### 7.2 null值处理

```java
Integer i = null;
int num = i;  // 抛出NullPointerException

// 安全处理
Integer i = null;
int num = (i != null) ? i : 0;  // 或使用Optional
```

### 7.3 性能考虑

```java
// 不好的做法：频繁装箱拆箱
Integer sum = 0;
for (int i = 0; i < 1000; i++) {
    sum += i;  // 每次循环都进行装箱和拆箱
}

// 好的做法：使用基本类型
int sum = 0;
for (int i = 0; i < 1000; i++) {
    sum += i;  // 直接使用基本类型，性能更好
}
```

### 7.4 集合中的使用

```java
// 自动装箱
List<Integer> list = new ArrayList<>();
list.add(100);  // 自动装箱为Integer

// 自动拆箱
int num = list.get(0);  // 自动拆箱为int
```

## 8. 包装类的应用场景

### 8.1 集合框架

```java
// 集合只能存储对象
List<Integer> list = new ArrayList<>();
list.add(100);  // 自动装箱

Map<String, Integer> map = new HashMap<>();
map.put("age", 25);  // 自动装箱
```

### 8.2 泛型

```java
// 泛型只能使用对象类型
class Box<T> {
    private T value;
}

Box<Integer> box = new Box<>();
box.setValue(100);  // 自动装箱
```

### 8.3 可空值

```java
// 包装类可以表示null
Integer age = getUserAge();  // 可能返回null
if (age != null) {
    System.out.println("年龄：" + age);
}
```

### 8.4 方法重载

```java
public void method(int i) {
    System.out.println("int");
}

public void method(Integer i) {
    System.out.println("Integer");
}

method(100);        // 调用int版本
method(Integer.valueOf(100));  // 调用Integer版本
```

## 9. 常见问题

### 9.1 为什么Integer缓存范围是-128到127？

- 这个范围覆盖了最常用的整数值
- 节省内存，提高性能
- 可以通过JVM参数`-XX:AutoBoxCacheMax`调整上限

### 9.2 自动装箱拆箱的性能影响

- 自动装箱会创建对象，有内存开销
- 频繁装箱拆箱会影响性能
- 在循环中应优先使用基本类型

### 9.3 包装类的equals()和==

```java
Integer i1 = 100;
Integer i2 = 100;
System.out.println(i1 == i2);        // true（缓存）
System.out.println(i1.equals(i2));  // true

Integer i3 = new Integer(100);
Integer i4 = new Integer(100);
System.out.println(i3 == i4);        // false（不同对象）
System.out.println(i3.equals(i4));  // true（值相等）

// 推荐：始终使用equals()比较包装类
```

## 10. 最佳实践

1. **优先使用基本类型**：在不需要对象特性的场景下使用基本类型
2. **使用equals()比较**：比较包装类时使用equals()而不是==
3. **注意null值**：使用包装类时注意null值检查
4. **避免频繁装箱拆箱**：在循环中优先使用基本类型
5. **理解缓存机制**：了解包装类的缓存范围，避免意外的比较结果

## 11. 总结

- 包装类提供了基本类型的对象表示
- 自动装箱拆箱简化了基本类型和包装类的转换
- 包装类有缓存机制，提高性能
- 注意==和equals()的区别
- 在性能敏感的场景下优先使用基本类型

