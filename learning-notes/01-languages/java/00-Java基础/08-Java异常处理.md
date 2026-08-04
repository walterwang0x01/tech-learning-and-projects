# Java异常处理
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 异常概述

### 1.1 什么是异常

异常是程序在运行过程中出现的错误或意外情况，它会中断程序的正常执行流程。

### 1.2 异常的分类

Java中的异常分为两大类：

- **Error（错误）**：系统级错误，程序无法处理，如OutOfMemoryError、StackOverflowError
- **Exception（异常）**：程序可以处理的异常
  - **RuntimeException（运行时异常）**：非检查异常，不需要在方法签名中声明
  - **Checked Exception（检查异常）**：必须在方法签名中声明或处理

### 1.3 异常类层次结构

```
Throwable
├── Error
│   ├── OutOfMemoryError
│   ├── StackOverflowError
│   └── ...
└── Exception
    ├── RuntimeException（运行时异常）
    │   ├── NullPointerException
    │   ├── IllegalArgumentException
    │   ├── ArrayIndexOutOfBoundsException
    │   └── ...
    └── Checked Exception（检查异常）
        ├── IOException
        ├── SQLException
        └── ...
```

## 2. 异常处理机制

### 2.1 try-catch-finally

#### 基本语法

```java
try {
    // 可能抛出异常的代码
} catch (ExceptionType1 e1) {
    // 处理ExceptionType1类型的异常
} catch (ExceptionType2 e2) {
    // 处理ExceptionType2类型的异常
} finally {
    // 无论是否发生异常都会执行的代码
}
```

#### 示例

```java
try {
    int result = 10 / 0;
} catch (ArithmeticException e) {
    System.out.println("除零异常：" + e.getMessage());
} finally {
    System.out.println("finally块执行");
}
```

### 2.2 多重catch块

```java
try {
    // 可能抛出多种异常的代码
} catch (NullPointerException e) {
    // 处理空指针异常
} catch (ArrayIndexOutOfBoundsException e) {
    // 处理数组越界异常
} catch (Exception e) {
    // 处理其他所有异常（必须放在最后）
}
```

**注意**：catch块的顺序很重要，子类异常必须放在父类异常之前。

### 2.3 finally块

- **作用**：无论是否发生异常，finally块中的代码都会执行
- **用途**：释放资源，如关闭文件、数据库连接等
- **特点**：
  - finally块在try或catch块执行后执行
  - 即使try或catch块中有return语句，finally块也会执行
  - 如果finally块中有return语句，会覆盖try或catch块中的return

```java
try {
    return 1;
} catch (Exception e) {
    return 2;
} finally {
    return 3;  // 最终返回3
}
```

### 2.4 try-with-resources（JDK 7+）

自动关闭实现了`AutoCloseable`接口的资源。

```java
// 旧写法
FileInputStream fis = null;
try {
    fis = new FileInputStream("file.txt");
    // 使用fis
} catch (IOException e) {
    e.printStackTrace();
} finally {
    if (fis != null) {
        try {
            fis.close();
        } catch (IOException e) {
            e.printStackTrace();
        }
    }
}

// try-with-resources写法
try (FileInputStream fis = new FileInputStream("file.txt")) {
    // 使用fis
} catch (IOException e) {
    e.printStackTrace();
}
// fis会自动关闭
```

**多个资源：**

```java
try (FileInputStream fis = new FileInputStream("input.txt");
     FileOutputStream fos = new FileOutputStream("output.txt")) {
    // 使用资源
}
```

## 3. 抛出异常

### 3.1 throw关键字

手动抛出异常。

```java
public void checkAge(int age) {
    if (age < 0) {
        throw new IllegalArgumentException("年龄不能为负数");
    }
}
```

### 3.2 throws关键字

在方法签名中声明可能抛出的异常。

```java
public void readFile(String filename) throws IOException {
    FileInputStream fis = new FileInputStream(filename);
    // ...
}
```

### 3.3 throw vs throws

- **throw**：在方法体内抛出异常对象
- **throws**：在方法签名中声明可能抛出的异常类型

## 4. 常见异常类型

### 4.1 NullPointerException（空指针异常）

```java
String str = null;
int length = str.length();  // 抛出NullPointerException
```

**预防：**
```java
if (str != null) {
    int length = str.length();
}
```

### 4.2 ArrayIndexOutOfBoundsException（数组越界异常）

```java
int[] arr = {1, 2, 3};
int value = arr[5];  // 抛出ArrayIndexOutOfBoundsException
```

### 4.3 ClassCastException（类型转换异常）

```java
Object obj = "hello";
Integer num = (Integer) obj;  // 抛出ClassCastException
```

### 4.4 IllegalArgumentException（非法参数异常）

```java
public void setAge(int age) {
    if (age < 0) {
        throw new IllegalArgumentException("年龄不能为负数");
    }
}
```

### 4.5 NumberFormatException（数字格式异常）

```java
String str = "abc";
int num = Integer.parseInt(str);  // 抛出NumberFormatException
```

## 5. 自定义异常

### 5.1 创建自定义异常

#### 继承RuntimeException（运行时异常）

```java
public class BusinessException extends RuntimeException {
    private Integer code;
    
    public BusinessException(Integer code, String message) {
        super(message);
        this.code = code;
    }
    
    public BusinessException(Integer code, String message, Throwable cause) {
        super(message, cause);
        this.code = code;
    }
    
    public Integer getCode() {
        return code;
    }
}
```

#### 继承Exception（检查异常）

```java
public class CustomException extends Exception {
    public CustomException(String message) {
        super(message);
    }
    
    public CustomException(String message, Throwable cause) {
        super(message, cause);
    }
}
```

### 5.2 使用自定义异常

```java
public void transferMoney(double amount) {
    if (amount <= 0) {
        throw new BusinessException(400, "转账金额必须大于0");
    }
    if (amount > balance) {
        throw new BusinessException(400, "余额不足");
    }
    // 执行转账逻辑
}
```

## 6. 异常处理最佳实践

### 6.1 异常处理原则

1. **只捕获能处理的异常**：不要捕获异常后什么都不做
2. **具体异常优先**：捕获具体的异常类型，而不是通用的Exception
3. **不要忽略异常**：至少记录日志
4. **合理使用finally**：用于释放资源
5. **避免空的catch块**：空的catch块会隐藏问题

### 6.2 异常处理示例

#### 不好的做法

```java
try {
    // 代码
} catch (Exception e) {
    // 空的catch块，什么都不做
}
```

#### 好的做法

```java
try {
    // 代码
} catch (SpecificException e) {
    logger.error("处理特定异常", e);
    // 进行适当的处理或恢复
} catch (Exception e) {
    logger.error("处理未知异常", e);
    throw new BusinessException("操作失败", e);
}
```

### 6.3 异常链

保留原始异常信息。

```java
try {
    // 代码
} catch (IOException e) {
    throw new BusinessException("业务处理失败", e);  // 保留原始异常
}
```

### 6.4 异常信息

提供有意义的异常信息。

```java
// 不好的做法
throw new Exception("错误");

// 好的做法
throw new IllegalArgumentException("年龄不能为负数，当前值：" + age);
```

## 7. 异常处理在框架中的应用

### 7.1 Spring MVC异常处理

```java
@RestControllerAdvice
public class GlobalExceptionHandler {
    
    @ExceptionHandler(BusinessException.class)
    public Result handleBusinessException(BusinessException e) {
        return Result.error(e.getCode(), e.getMessage());
    }
    
    @ExceptionHandler(Exception.class)
    public Result handleException(Exception e) {
        logger.error("系统异常", e);
        return Result.error(500, "系统异常，请稍后重试");
    }
}
```

### 7.2 异常分类

- **业务异常（BusinessException）**：用户操作不当导致的异常
- **系统异常（SystemException）**：系统故障导致的异常
- **其他异常（Exception）**：未预期的异常

## 8. 常见问题

### 8.1 异常处理的性能影响

- 异常处理本身性能开销较小
- 但异常对象的创建和堆栈跟踪有一定开销
- 不要使用异常来控制程序流程

### 8.2 检查异常 vs 运行时异常

- **检查异常**：必须在方法签名中声明，调用者必须处理
- **运行时异常**：不需要声明，可以选择性处理

### 8.3 异常与返回值

- 异常用于处理异常情况
- 返回值用于正常的业务逻辑
- 不要用异常代替返回值

## 9. 总结

1. **理解异常分类**：Error、RuntimeException、Checked Exception
2. **正确使用try-catch-finally**：合理处理异常，释放资源
3. **使用try-with-resources**：简化资源管理
4. **创建自定义异常**：提供有意义的异常信息
5. **遵循最佳实践**：只捕获能处理的异常，记录日志，保留异常链

