# Java字符串
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. String概述

### 1.1 String的特性

- **不可变性（Immutable）**：String对象一旦创建，其值就不能被改变
- **字符串常量池（String Pool）**：Java为了优化字符串操作，维护了一个字符串常量池
- **final类**：String类被声明为final，不能被继承

### 1.2 String的不可变性

```java
String str = "Hello";
str = str + " World";  // 创建了新的String对象，原对象不变
```

**为什么String是不可变的？**
- 安全性：作为参数传递时不会被修改
- 线程安全：多线程环境下可以安全共享
- 缓存优化：可以缓存hashCode
- 字符串常量池：可以复用字符串

## 2. 字符串创建方式

### 2.1 字面量方式

```java
String str1 = "Hello";
String str2 = "Hello";
System.out.println(str1 == str2);  // true，指向同一个对象
```

### 2.2 new关键字方式

```java
String str1 = new String("Hello");
String str2 = new String("Hello");
System.out.println(str1 == str2);  // false，创建了不同的对象
```

### 2.3 字符串常量池

```java
String s1 = "Hello";
String s2 = "Hello";
String s3 = new String("Hello");
String s4 = new String("Hello").intern();

System.out.println(s1 == s2);  // true，都在常量池中
System.out.println(s1 == s3);  // false，s3在堆中
System.out.println(s1 == s4);  // true，intern()返回常量池中的引用
```

### 2.4 intern()方法

将字符串添加到常量池中，如果已存在则返回常量池中的引用。

```java
String s1 = new String("Hello");
String s2 = s1.intern();
String s3 = "Hello";

System.out.println(s1 == s2);  // false
System.out.println(s2 == s3);  // true
```

## 3. String常用方法

### 3.1 字符串比较

```java
String s1 = "Hello";
String s2 = "hello";

// equals：区分大小写
s1.equals(s2);  // false

// equalsIgnoreCase：不区分大小写
s1.equalsIgnoreCase(s2);  // true

// compareTo：按字典序比较
s1.compareTo(s2);  // 负数（s1 < s2）
```

### 3.2 字符串查找

```java
String str = "Hello World";

// 查找字符
str.indexOf('o');           // 4
str.lastIndexOf('o');      // 7

// 查找字符串
str.indexOf("World");       // 6
str.contains("World");      // true
str.startsWith("Hello");    // true
str.endsWith("World");      // true
```

### 3.3 字符串截取

```java
String str = "Hello World";

// substring
str.substring(6);           // "World"
str.substring(0, 5);        // "Hello"

// split
String[] parts = str.split(" ");  // ["Hello", "World"]
```

### 3.4 字符串转换

```java
String str = "Hello World";

// 大小写转换
str.toUpperCase();           // "HELLO WORLD"
str.toLowerCase();           // "hello world"

// 去除空格
"  Hello  ".trim();         // "Hello"

// 替换
str.replace("World", "Java");  // "Hello Java"
str.replaceAll("l", "L");      // "HeLLo WorLd"
```

### 3.5 其他常用方法

```java
String str = "Hello World";

str.length();               // 11
str.charAt(0);              // 'H'
str.isEmpty();              // false
str.concat("!");            // "Hello World!"
```

## 4. StringBuilder

### 4.1 StringBuilder概述

- **可变字符串**：可以修改内容
- **非线程安全**：性能更高
- **适用于**：频繁修改字符串的场景

### 4.2 StringBuilder使用

```java
StringBuilder sb = new StringBuilder();
sb.append("Hello");
sb.append(" ");
sb.append("World");
String result = sb.toString();  // "Hello World"

// 链式调用
StringBuilder sb = new StringBuilder()
    .append("Hello")
    .append(" ")
    .append("World");
```

### 4.3 StringBuilder常用方法

```java
StringBuilder sb = new StringBuilder("Hello");

sb.append(" World");         // "Hello World"
sb.insert(5, ",");          // "Hello, World"
sb.delete(5, 6);            // "Hello World"
sb.replace(0, 5, "Hi");     // "Hi World"
sb.reverse();               // "dlroW iH"
sb.length();                // 8
sb.capacity();              // 容量
```

## 5. StringBuffer

### 5.1 StringBuffer概述

- **可变字符串**：可以修改内容
- **线程安全**：方法使用synchronized修饰
- **性能较低**：由于同步机制，性能低于StringBuilder

### 5.2 StringBuffer使用

```java
StringBuffer sb = new StringBuffer();
sb.append("Hello");
sb.append(" World");
String result = sb.toString();
```

### 5.3 StringBuffer vs StringBuilder

| 特性 | StringBuffer | StringBuilder |
|------|--------------|---------------|
| 线程安全 | 是（synchronized） | 否 |
| 性能 | 较低 | 较高 |
| 适用场景 | 多线程环境 | 单线程环境 |

## 6. String vs StringBuilder vs StringBuffer

### 6.1 性能对比

```java
// String拼接（性能差）
String result = "";
for (int i = 0; i < 1000; i++) {
    result += i;  // 每次都创建新对象
}

// StringBuilder（性能好）
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 1000; i++) {
    sb.append(i);  // 在同一个对象上操作
}
String result = sb.toString();
```

### 6.2 选择建议

- **String**：字符串内容不变，或少量拼接
- **StringBuilder**：单线程环境下频繁修改字符串
- **StringBuffer**：多线程环境下频繁修改字符串

## 7. 字符串拼接

### 7.1 + 运算符

```java
String s1 = "Hello";
String s2 = "World";
String result = s1 + " " + s2;  // 编译后使用StringBuilder
```

### 7.2 concat()方法

```java
String s1 = "Hello";
String s2 = "World";
String result = s1.concat(" ").concat(s2);
```

### 7.3 StringBuilder/StringBuffer

```java
StringBuilder sb = new StringBuilder();
sb.append("Hello").append(" ").append("World");
String result = sb.toString();
```

### 7.4 String.join()（Java 8+）

```java
String result = String.join(" ", "Hello", "World");
```

## 8. 字符串格式化

### 8.1 format()方法

```java
String name = "张三";
int age = 25;
String result = String.format("姓名：%s，年龄：%d", name, age);
```

### 8.2 格式化符号

- `%s`：字符串
- `%d`：整数
- `%f`：浮点数
- `%c`：字符
- `%b`：布尔值

### 8.3 System.out.printf()

```java
System.out.printf("姓名：%s，年龄：%d%n", name, age);
```

## 9. 字符串与基本类型转换

### 9.1 字符串转基本类型

```java
String str = "123";

int i = Integer.parseInt(str);
long l = Long.parseLong(str);
double d = Double.parseDouble(str);
float f = Float.parseFloat(str);
boolean b = Boolean.parseBoolean("true");
```

### 9.2 基本类型转字符串

```java
int i = 123;

String s1 = String.valueOf(i);
String s2 = Integer.toString(i);
String s3 = i + "";  // 不推荐
```

## 10. 字符串常见问题

### 10.1 == vs equals()

```java
String s1 = "Hello";
String s2 = "Hello";
String s3 = new String("Hello");

System.out.println(s1 == s2);        // true（常量池）
System.out.println(s1 == s3);        // false（不同对象）
System.out.println(s1.equals(s3));  // true（内容相同）
```

### 10.2 字符串不可变性的影响

```java
String str = "Hello";
modifyString(str);
System.out.println(str);  // 仍然是"Hello"，没有被修改

public void modifyString(String s) {
    s = s + " World";  // 只修改了局部变量
}
```

### 10.3 字符串拼接性能

```java
// 不好的做法
String result = "";
for (int i = 0; i < 10000; i++) {
    result += i;  // 每次都创建新对象，性能差
}

// 好的做法
StringBuilder sb = new StringBuilder();
for (int i = 0; i < 10000; i++) {
    sb.append(i);  // 在同一个对象上操作，性能好
}
String result = sb.toString();
```

## 11. Java 8+ 字符串新特性

### 11.1 String.join()

```java
List<String> list = Arrays.asList("a", "b", "c");
String result = String.join(",", list);  // "a,b,c"
```

### 11.2 String新增方法（Java 11+）

```java
String str = "  Hello World  ";

str.strip();              // 去除首尾空白（支持Unicode）
str.stripLeading();       // 去除开头空白
str.stripTrailing();     // 去除结尾空白
str.isBlank();           // 是否为空或只包含空白
str.repeat(3);           // 重复字符串
```

## 12. 最佳实践

1. **优先使用字面量**：`String s = "Hello"` 而不是 `new String("Hello")`
2. **频繁拼接使用StringBuilder**：避免使用`+`进行大量拼接
3. **多线程使用StringBuffer**：需要线程安全时使用StringBuffer
4. **使用equals()比较**：不要使用`==`比较字符串内容
5. **合理使用intern()**：在需要时使用intern()优化内存

## 13. 常见面试题

### 13.1 String s = new String("abc")创建了几个对象？

- 如果常量池中没有"abc"：创建2个对象（常量池中的"abc"和堆中的String对象）
- 如果常量池中已有"abc"：创建1个对象（堆中的String对象）

### 13.2 String为什么是不可变的？

- final类，不能被继承
- 字符数组是final的
- 没有提供修改字符数组的方法

### 13.3 StringBuilder和StringBuffer的区别？

- StringBuffer是线程安全的，StringBuilder不是
- StringBuilder性能更高
- 单线程用StringBuilder，多线程用StringBuffer

