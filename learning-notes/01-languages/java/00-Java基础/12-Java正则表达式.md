# Java正则表达式
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 正则表达式概述

### 1.1 什么是正则表达式

正则表达式（Regular Expression）是一种用于描述字符串匹配模式的工具，可以用来检查、查找、替换字符串。

### 1.2 Java中的正则表达式

Java通过`java.util.regex`包提供正则表达式支持，主要包含：
- **Pattern**：正则表达式的编译表示
- **Matcher**：匹配器，用于匹配字符串
- **PatternSyntaxException**：正则表达式语法异常

## 2. Pattern类

### 2.1 创建Pattern对象

```java
// 方式1：使用compile()方法
Pattern pattern = Pattern.compile("\\d+");

// 方式2：使用静态方法（简单匹配）
boolean matches = Pattern.matches("\\d+", "123");  // true
```

### 2.2 Pattern常用方法

```java
Pattern pattern = Pattern.compile("\\d+");

// 创建Matcher
Matcher matcher = pattern.matcher("123abc456");

// 检查是否匹配
boolean matches = pattern.matcher("123").matches();  // true

// 分割字符串
String[] parts = pattern.split("a1b2c3");  // ["a", "b", "c", ""]
```

## 3. Matcher类

### 3.1 创建Matcher对象

```java
Pattern pattern = Pattern.compile("\\d+");
Matcher matcher = pattern.matcher("123abc456");
```

### 3.2 Matcher常用方法

#### 查找方法

```java
Pattern pattern = Pattern.compile("\\d+");
Matcher matcher = pattern.matcher("123abc456");

// find()：查找下一个匹配
while (matcher.find()) {
    System.out.println(matcher.group());  // "123", "456"
}

// lookingAt()：从开头开始匹配
boolean lookingAt = matcher.lookingAt();  // true

// matches()：完全匹配
boolean matches = matcher.matches();  // false（不是完全匹配）
```

#### 获取匹配结果

```java
Pattern pattern = Pattern.compile("(\\d+)([a-z]+)");
Matcher matcher = pattern.matcher("123abc456def");

while (matcher.find()) {
    System.out.println("完整匹配：" + matcher.group());      // "123abc"
    System.out.println("组1：" + matcher.group(1));         // "123"
    System.out.println("组2：" + matcher.group(2));         // "abc"
    System.out.println("起始位置：" + matcher.start());      // 0
    System.out.println("结束位置：" + matcher.end());        // 6
}
```

#### 替换方法

```java
Pattern pattern = Pattern.compile("\\d+");
Matcher matcher = pattern.matcher("123abc456");

// replaceAll()：替换所有匹配
String result1 = matcher.replaceAll("X");  // "XabcX"

// replaceFirst()：替换第一个匹配
String result2 = matcher.replaceFirst("X");  // "Xabc456"

// appendReplacement()和appendTail()：自定义替换
StringBuffer sb = new StringBuffer();
while (matcher.find()) {
    matcher.appendReplacement(sb, "X");
}
matcher.appendTail(sb);
String result3 = sb.toString();
```

## 4. 正则表达式语法

### 4.1 字符类

```java
// 单个字符
"a"          // 匹配字符'a'
"\\."        // 匹配点号（需要转义）

// 字符类
"[abc]"      // 匹配a、b或c
"[a-z]"      // 匹配a到z的任意字符
"[^abc]"     // 匹配除a、b、c外的任意字符
"[a-zA-Z0-9]" // 匹配字母或数字

// 预定义字符类
"\\d"        // 数字，等价于[0-9]
"\\D"        // 非数字，等价于[^0-9]
"\\s"        // 空白字符
"\\S"        // 非空白字符
"\\w"        // 单词字符，等价于[a-zA-Z0-9_]
"\\W"        // 非单词字符
"."          // 任意字符（除换行符）
```

### 4.2 量词

```java
// 贪婪量词（默认）
"a*"         // 0个或多个a
"a+"         // 1个或多个a
"a?"         // 0个或1个a
"a{3}"       // 恰好3个a
"a{3,}"      // 3个或更多a
"a{3,5}"     // 3到5个a

// 非贪婪量词（在量词后加?）
"a*?"        // 非贪婪匹配0个或多个a
"a+?"        // 非贪婪匹配1个或多个a
"a??"        // 非贪婪匹配0个或1个a
```

### 4.3 边界匹配

```java
"^abc"       // 以abc开头
"abc$"       // 以abc结尾
"\\bword\\b" // 单词边界
"\\Bword\\B" // 非单词边界
```

### 4.4 分组和捕获

```java
// 分组
"(abc)"      // 捕获组
"(?:abc)"    // 非捕获组
"(?<name>abc)" // 命名捕获组

// 使用分组
Pattern pattern = Pattern.compile("(\\d{4})-(\\d{2})-(\\d{2})");
Matcher matcher = pattern.matcher("2024-01-01");
if (matcher.matches()) {
    System.out.println(matcher.group(1));  // "2024"
    System.out.println(matcher.group(2));  // "01"
    System.out.println(matcher.group(3));  // "01"
}
```

### 4.5 反向引用

```java
// 引用前面的捕获组
"(\\d)\\1"   // 匹配两个相同的数字，如"11", "22"

// 命名组的反向引用
"(?<digit>\\d)\\k<digit>"  // 使用命名组
```

### 4.6 零宽断言

```java
// 前瞻断言
"abc(?=def)"  // abc后面跟着def
"abc(?!def)"  // abc后面不跟着def

// 后顾断言
"(?<=abc)def" // def前面是abc
"(?<!abc)def" // def前面不是abc
```

## 5. 常用正则表达式示例

### 5.1 验证邮箱

```java
String emailRegex = "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$";
Pattern pattern = Pattern.compile(emailRegex);
boolean isValid = pattern.matcher("user@example.com").matches();
```

### 5.2 验证手机号

```java
String phoneRegex = "^1[3-9]\\d{9}$";
Pattern pattern = Pattern.compile(phoneRegex);
boolean isValid = pattern.matcher("13812345678").matches();
```

### 5.3 验证身份证号

```java
String idCardRegex = "^[1-9]\\d{5}(18|19|20)\\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\\d|3[01])\\d{3}[0-9Xx]$";
Pattern pattern = Pattern.compile(idCardRegex);
boolean isValid = pattern.matcher("110101199001011234").matches();
```

### 5.4 提取数字

```java
Pattern pattern = Pattern.compile("\\d+");
Matcher matcher = pattern.matcher("abc123def456");
while (matcher.find()) {
    System.out.println(matcher.group());  // "123", "456"
}
```

### 5.5 替换字符串

```java
String text = "Hello 123 World 456";
String result = text.replaceAll("\\d+", "X");  // "Hello X World X"
```

## 6. String类中的正则表达式方法

### 6.1 matches()

```java
String str = "123";
boolean matches = str.matches("\\d+");  // true
```

### 6.2 split()

```java
String str = "a,b,c";
String[] parts = str.split(",");  // ["a", "b", "c"]

// 使用正则表达式
String str2 = "a1b2c3";
String[] parts2 = str2.split("\\d+");  // ["a", "b", "c"]
```

### 6.3 replaceAll() / replaceFirst()

```java
String str = "abc123def456";

// 替换所有匹配
String result1 = str.replaceAll("\\d+", "X");  // "abcXdefX"

// 替换第一个匹配
String result2 = str.replaceFirst("\\d+", "X");  // "abcXdef456"
```

## 7. 正则表达式标志

### 7.1 常用标志

```java
// CASE_INSENSITIVE：忽略大小写
Pattern pattern = Pattern.compile("abc", Pattern.CASE_INSENSITIVE);
boolean matches = pattern.matcher("ABC").matches();  // true

// MULTILINE：多行模式
Pattern pattern = Pattern.compile("^abc", Pattern.MULTILINE);

// DOTALL：点号匹配所有字符（包括换行符）
Pattern pattern = Pattern.compile("a.b", Pattern.DOTALL);

// 组合使用
Pattern pattern = Pattern.compile("abc", 
    Pattern.CASE_INSENSITIVE | Pattern.MULTILINE);
```

### 7.2 内联标志

```java
// (?i)：忽略大小写
Pattern pattern = Pattern.compile("(?i)abc");

// (?m)：多行模式
Pattern pattern = Pattern.compile("(?m)^abc");

// (?s)：点号匹配所有字符
Pattern pattern = Pattern.compile("(?s)a.b");
```

## 8. 性能优化

### 8.1 编译Pattern对象

```java
// 不好的做法：每次都编译
for (int i = 0; i < 1000; i++) {
    boolean matches = Pattern.matches("\\d+", str);
}

// 好的做法：编译一次，重复使用
Pattern pattern = Pattern.compile("\\d+");
for (int i = 0; i < 1000; i++) {
    boolean matches = pattern.matcher(str).matches();
}
```

### 8.2 使用非捕获组

```java
// 捕获组（会保存匹配结果）
Pattern pattern1 = Pattern.compile("(abc)(def)");

// 非捕获组（不保存匹配结果，性能更好）
Pattern pattern2 = Pattern.compile("(?:abc)(?:def)");
```

## 9. 常见问题

### 9.1 转义字符

```java
// 在Java字符串中，需要双重转义
String regex = "\\d+";  // 匹配数字

// 或者使用原始字符串（Java 13+）
String regex = """
    \\d+
    """;
```

### 9.2 贪婪 vs 非贪婪

```java
String text = "abc123def456";

// 贪婪匹配（默认）
Pattern pattern1 = Pattern.compile("\\d+");
Matcher matcher1 = pattern1.matcher(text);
matcher1.find();
System.out.println(matcher1.group());  // "123456"（匹配所有数字）

// 非贪婪匹配
Pattern pattern2 = Pattern.compile("\\d+?");
Matcher matcher2 = pattern2.matcher(text);
matcher2.find();
System.out.println(matcher2.group());  // "1"（只匹配一个数字）
```

### 9.3 分组和反向引用

```java
// 查找重复的单词
Pattern pattern = Pattern.compile("\\b(\\w+)\\s+\\1\\b");
Matcher matcher = pattern.matcher("hello hello world");
while (matcher.find()) {
    System.out.println(matcher.group());  // "hello hello"
}
```

## 10. 最佳实践

1. **编译Pattern对象**：如果正则表达式需要重复使用，先编译
2. **使用非捕获组**：不需要捕获结果时使用`(?:...)`
3. **避免过度复杂的正则**：复杂的正则表达式难以维护
4. **测试正则表达式**：使用工具测试正则表达式的正确性
5. **处理异常**：捕获`PatternSyntaxException`

## 11. 工具推荐

- **在线测试工具**：regex101.com、regexr.com
- **Java正则表达式测试**：使用单元测试验证正则表达式

## 12. 总结

- 正则表达式是强大的字符串匹配工具
- Pattern和Matcher是Java中处理正则表达式的核心类
- 合理使用正则表达式可以提高代码效率
- 注意转义字符和性能优化

