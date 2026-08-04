# Java枚举
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 枚举概述

### 1.1 什么是枚举

枚举（Enum）是Java 5引入的一种特殊类，用于定义一组固定的常量。

### 1.2 为什么使用枚举

- **类型安全**：编译时检查，避免使用错误的常量值
- **代码可读性**：使用有意义的名称而不是数字
- **功能强大**：可以定义方法、实现接口等
- **单例模式**：每个枚举常量都是单例

### 1.3 枚举 vs 常量类

#### 常量类方式（不推荐）

```java
public class Color {
    public static final int RED = 1;
    public static final int GREEN = 2;
    public static final int BLUE = 3;
}
```

**问题**：
- 类型不安全
- 没有命名空间
- 无法限制值的范围

#### 枚举方式（推荐）

```java
public enum Color {
    RED, GREEN, BLUE
}
```

## 2. 枚举的基本使用

### 2.1 定义枚举

```java
public enum Season {
    SPRING, SUMMER, AUTUMN, WINTER
}
```

### 2.2 使用枚举

```java
Season season = Season.SPRING;

// 比较
if (season == Season.SPRING) {
    System.out.println("春天");
}

// switch语句
switch (season) {
    case SPRING:
        System.out.println("春天");
        break;
    case SUMMER:
        System.out.println("夏天");
        break;
    // ...
}
```

### 2.3 枚举的常用方法

```java
Season season = Season.SPRING;

// 获取枚举名称
String name = season.name();  // "SPRING"

// 获取枚举序号
int ordinal = season.ordinal();  // 0

// 转换为字符串
String str = season.toString();  // "SPRING"

// 根据名称获取枚举
Season s = Season.valueOf("SPRING");

// 获取所有枚举值
Season[] values = Season.values();
```

## 3. 枚举的高级特性

### 3.1 枚举的构造函数和方法

```java
public enum Planet {
    MERCURY(3.303e+23, 2.4397e6),
    VENUS(4.869e+24, 6.0518e6),
    EARTH(5.976e+24, 6.37814e6),
    MARS(6.421e+23, 3.3972e6);
    
    private final double mass;      // 质量
    private final double radius;   // 半径
    
    Planet(double mass, double radius) {
        this.mass = mass;
        this.radius = radius;
    }
    
    public double getMass() {
        return mass;
    }
    
    public double getRadius() {
        return radius;
    }
    
    public double surfaceGravity() {
        double G = 6.67300E-11;
        return G * mass / (radius * radius);
    }
}
```

### 3.2 枚举实现接口

```java
public interface Operation {
    double apply(double x, double y);
}

public enum Calculator implements Operation {
    PLUS {
        @Override
        public double apply(double x, double y) {
            return x + y;
        }
    },
    MINUS {
        @Override
        public double apply(double x, double y) {
            return x - y;
        }
    },
    MULTIPLY {
        @Override
        public double apply(double x, double y) {
            return x * y;
        }
    },
    DIVIDE {
        @Override
        public double apply(double x, double y) {
            return x / y;
        }
    };
}

// 使用
double result = Calculator.PLUS.apply(10, 5);  // 15.0
```

### 3.3 枚举中的抽象方法

```java
public enum Operation {
    PLUS {
        @Override
        public double apply(double x, double y) {
            return x + y;
        }
    },
    MINUS {
        @Override
        public double apply(double x, double y) {
            return x - y;
        }
    };
    
    public abstract double apply(double x, double y);
}
```

## 4. 枚举与switch语句

### 4.1 switch中使用枚举

```java
public enum Day {
    MONDAY, TUESDAY, WEDNESDAY, THURSDAY, FRIDAY, SATURDAY, SUNDAY
}

Day day = Day.MONDAY;

switch (day) {
    case MONDAY:
    case FRIDAY:
        System.out.println("工作日");
        break;
    case SATURDAY:
    case SUNDAY:
        System.out.println("周末");
        break;
    default:
        System.out.println("其他");
}
```

### 4.2 Java 14+ switch表达式

```java
String result = switch (day) {
    case MONDAY, FRIDAY -> "工作日";
    case SATURDAY, SUNDAY -> "周末";
    default -> "其他";
};
```

## 5. 枚举集合

### 5.1 EnumSet

专门为枚举设计的Set实现，性能优于HashSet。

```java
EnumSet<Day> weekdays = EnumSet.range(Day.MONDAY, Day.FRIDAY);
EnumSet<Day> weekends = EnumSet.of(Day.SATURDAY, Day.SUNDAY);
EnumSet<Day> allDays = EnumSet.allOf(Day.class);
```

### 5.2 EnumMap

专门为枚举设计的Map实现，性能优于HashMap。

```java
EnumMap<Day, String> schedule = new EnumMap<>(Day.class);
schedule.put(Day.MONDAY, "开会");
schedule.put(Day.TUESDAY, "编码");
```

## 6. 枚举的单例模式

枚举天然实现单例模式，线程安全且防止反射和序列化破坏。

```java
public enum Singleton {
    INSTANCE;
    
    public void doSomething() {
        System.out.println("单例方法");
    }
}

// 使用
Singleton.INSTANCE.doSomething();
```

## 7. 枚举的实际应用

### 7.1 状态机

```java
public enum OrderStatus {
    PENDING {
        @Override
        public OrderStatus next() {
            return PAID;
        }
    },
    PAID {
        @Override
        public OrderStatus next() {
            return SHIPPED;
        }
    },
    SHIPPED {
        @Override
        public OrderStatus next() {
            return DELIVERED;
        }
    },
    DELIVERED {
        @Override
        public OrderStatus next() {
            return this;  // 最终状态
        }
    };
    
    public abstract OrderStatus next();
}
```

### 7.2 策略模式

```java
public enum PaymentMethod {
    CREDIT_CARD {
        @Override
        public void pay(double amount) {
            System.out.println("使用信用卡支付：" + amount);
        }
    },
    ALIPAY {
        @Override
        public void pay(double amount) {
            System.out.println("使用支付宝支付：" + amount);
        }
    },
    WECHAT {
        @Override
        public void pay(double amount) {
            System.out.println("使用微信支付：" + amount);
        }
    };
    
    public abstract void pay(double amount);
}
```

### 7.3 错误码定义

```java
public enum ErrorCode {
    SUCCESS(200, "成功"),
    NOT_FOUND(404, "资源未找到"),
    SERVER_ERROR(500, "服务器错误");
    
    private final int code;
    private final String message;
    
    ErrorCode(int code, String message) {
        this.code = code;
        this.message = message;
    }
    
    public int getCode() {
        return code;
    }
    
    public String getMessage() {
        return message;
    }
}
```

## 8. 枚举的序列化

枚举的序列化是特殊的：
- 只序列化枚举的名称
- 反序列化时通过名称查找枚举常量
- 天然防止序列化破坏单例

```java
public enum Color implements Serializable {
    RED, GREEN, BLUE
}

// 序列化和反序列化都是安全的
```

## 9. 枚举的限制

1. **不能继承其他类**：枚举隐式继承Enum类
2. **不能创建实例**：枚举常量必须在枚举类内部定义
3. **不能是抽象的**：除非所有枚举常量都实现抽象方法

## 10. 最佳实践

1. **使用枚举代替常量**：提高类型安全性
2. **为枚举添加方法**：增强功能
3. **使用EnumSet和EnumMap**：提高性能
4. **枚举实现单例**：线程安全且简洁
5. **合理使用ordinal()**：注意枚举顺序变化的影响

## 11. 常见问题

### 11.1 枚举可以继承吗？

枚举不能继承其他类，但可以实现接口。

### 11.2 枚举是线程安全的吗？

是的，枚举常量是线程安全的。

### 11.3 枚举可以用于switch吗？

可以，而且比使用整数常量更安全。

### 11.4 如何遍历枚举？

```java
for (Day day : Day.values()) {
    System.out.println(day);
}
```

