# Java内部类
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 内部类概述

### 1.1 什么是内部类

定义在另一个类内部的类称为内部类（Inner Class）。

### 1.2 内部类的分类

- **成员内部类（Member Inner Class）**
- **静态内部类（Static Nested Class）**
- **局部内部类（Local Inner Class）**
- **匿名内部类（Anonymous Inner Class）**

### 1.3 为什么使用内部类

1. **逻辑分组**：将只在一个地方使用的类组织在一起
2. **访问控制**：内部类可以访问外部类的私有成员
3. **代码封装**：隐藏实现细节
4. **回调机制**：实现回调接口

## 2. 成员内部类

### 2.1 定义成员内部类

```java
public class Outer {
    private int outerField = 10;
    
    // 成员内部类
    class Inner {
        private int innerField = 20;
        
        public void display() {
            // 可以访问外部类的私有成员
            System.out.println("外部类字段：" + outerField);
            System.out.println("内部类字段：" + innerField);
        }
    }
}
```

### 2.2 创建成员内部类对象

```java
// 方式1：通过外部类对象创建
Outer outer = new Outer();
Outer.Inner inner = outer.new Inner();

// 方式2：在外部类中创建
public class Outer {
    class Inner {}
    
    public Inner createInner() {
        return new Inner();
    }
}
```

### 2.3 成员内部类的特点

- 可以访问外部类的所有成员（包括私有成员）
- 不能定义静态成员（除非是编译时常量）
- 需要外部类实例才能创建

### 2.4 外部类访问内部类

```java
public class Outer {
    private int outerField = 10;
    
    class Inner {
        private int innerField = 20;
    }
    
    public void accessInner() {
        Inner inner = new Inner();
        System.out.println(inner.innerField);  // 可以访问
    }
}
```

## 3. 静态内部类

### 3.1 定义静态内部类

```java
public class Outer {
    private static int staticField = 10;
    private int instanceField = 20;
    
    // 静态内部类
    static class StaticInner {
        public void display() {
            // 只能访问外部类的静态成员
            System.out.println("静态字段：" + staticField);
            // System.out.println(instanceField);  // 编译错误
        }
        
        public static void staticMethod() {
            System.out.println("静态方法");
        }
    }
}
```

### 3.2 创建静态内部类对象

```java
// 不需要外部类实例
Outer.StaticInner staticInner = new Outer.StaticInner();

// 调用静态方法
Outer.StaticInner.staticMethod();
```

### 3.3 静态内部类的特点

- 可以定义静态成员
- 只能访问外部类的静态成员
- 不需要外部类实例就可以创建
- 不能访问外部类的实例成员

## 4. 局部内部类

### 4.1 定义局部内部类

```java
public class Outer {
    public void method() {
        final int localVar = 10;  // 必须是final或effectively final
        
        // 局部内部类
        class LocalInner {
            public void display() {
                System.out.println("局部变量：" + localVar);
            }
        }
        
        LocalInner inner = new LocalInner();
        inner.display();
    }
}
```

### 4.2 局部内部类的特点

- 定义在方法或代码块中
- 只能访问final或effectively final的局部变量
- 作用域仅限于定义它的方法或代码块
- 不能有访问修饰符

### 4.3 为什么局部变量必须是final？

```java
public void method() {
    int localVar = 10;
    
    class LocalInner {
        public void display() {
            // 如果localVar不是final，这里访问的是副本
            // 而外部方法可能已经修改了localVar
            System.out.println(localVar);
        }
    }
    
    // localVar = 20;  // 如果允许修改，会导致内部类访问不一致
}
```

## 5. 匿名内部类

### 5.1 定义匿名内部类

```java
// 实现接口
interface MyInterface {
    void method();
}

MyInterface obj = new MyInterface() {
    @Override
    public void method() {
        System.out.println("匿名内部类实现");
    }
};

// 继承类
abstract class MyAbstractClass {
    abstract void method();
}

MyAbstractClass obj = new MyAbstractClass() {
    @Override
    void method() {
        System.out.println("匿名内部类实现");
    }
};
```

### 5.2 匿名内部类的特点

- 没有类名
- 必须继承一个类或实现一个接口
- 只能创建一个实例
- 常用于事件监听器、回调函数等

### 5.3 Lambda表达式替代

```java
// 匿名内部类
Runnable r1 = new Runnable() {
    @Override
    public void run() {
        System.out.println("匿名内部类");
    }
};

// Lambda表达式（Java 8+）
Runnable r2 = () -> System.out.println("Lambda表达式");
```

## 6. 内部类的访问规则

### 6.1 内部类访问外部类

```java
public class Outer {
    private int outerField = 10;
    private static int staticField = 20;
    
    class Inner {
        public void accessOuter() {
            // 访问外部类实例成员
            System.out.println(outerField);
            
            // 访问外部类静态成员
            System.out.println(staticField);
            
            // 访问外部类方法
            outerMethod();
        }
    }
    
    public void outerMethod() {
        System.out.println("外部类方法");
    }
}
```

### 6.2 外部类访问内部类

```java
public class Outer {
    class Inner {
        private int innerField = 10;
    }
    
    public void accessInner() {
        Inner inner = new Inner();
        System.out.println(inner.innerField);
    }
}
```

### 6.3 内部类之间的访问

```java
public class Outer {
    class Inner1 {
        public void method() {
            Inner2 inner2 = new Inner2();  // 可以访问
        }
    }
    
    class Inner2 {
        public void method() {
            Inner1 inner1 = new Inner1();  // 可以访问
        }
    }
}
```

## 7. 内部类的应用场景

### 7.1 实现多重继承

```java
class A {
    void methodA() {}
}

class B {
    void methodB() {}
}

class C {
    class InnerA extends A {
        // 可以访问C的成员
    }
    
    class InnerB extends B {
        // 可以访问C的成员
    }
    
    // 通过内部类实现多重继承的效果
}
```

### 7.2 事件监听器

```java
button.addActionListener(new ActionListener() {
    @Override
    public void actionPerformed(ActionEvent e) {
        System.out.println("按钮被点击");
    }
});
```

### 7.3 迭代器模式

```java
public class MyList {
    private int[] data = {1, 2, 3, 4, 5};
    
    class MyIterator implements Iterator<Integer> {
        private int index = 0;
        
        @Override
        public boolean hasNext() {
            return index < data.length;
        }
        
        @Override
        public Integer next() {
            return data[index++];
        }
    }
    
    public Iterator<Integer> iterator() {
        return new MyIterator();
    }
}
```

### 7.4 回调机制

```java
interface Callback {
    void onComplete(String result);
}

class Processor {
    void process(Callback callback) {
        // 处理逻辑
        callback.onComplete("处理完成");
    }
}

// 使用
Processor processor = new Processor();
processor.process(new Callback() {
    @Override
    public void onComplete(String result) {
        System.out.println(result);
    }
});
```

## 8. 内部类的编译

### 8.1 编译后的文件

```java
// Outer.java
public class Outer {
    class Inner {}
}

// 编译后生成：
// Outer.class
// Outer$Inner.class
```

### 8.2 内部类如何访问外部类

```java
// 编译后的内部类会持有外部类的引用
class Outer$Inner {
    final Outer this$0;  // 外部类引用
    
    Outer$Inner(Outer outer) {
        this$0 = outer;
    }
}
```

## 9. 内部类与外部类的关系

### 9.1 成员内部类

- 持有外部类实例的引用
- 可以访问外部类的所有成员
- 与外部类实例绑定

### 9.2 静态内部类

- 不持有外部类实例的引用
- 只能访问外部类的静态成员
- 独立于外部类实例

### 9.3 局部内部类

- 可以访问外部类的成员
- 可以访问final局部变量
- 作用域受限

### 9.4 匿名内部类

- 没有类名
- 必须继承或实现
- 只能创建一次实例

## 10. 最佳实践

1. **优先使用静态内部类**：如果不需要访问外部类实例成员
2. **合理使用成员内部类**：需要访问外部类实例成员时使用
3. **局部内部类用于局部逻辑**：只在方法内使用的类
4. **Lambda替代匿名内部类**：Java 8+优先使用Lambda
5. **避免过度嵌套**：内部类嵌套不要超过2层

## 11. 常见问题

### 11.1 内部类可以继承其他类吗？

可以，内部类可以继承其他类，同时也可以实现接口。

### 11.2 外部类可以访问内部类的私有成员吗？

可以，外部类可以访问内部类的所有成员，包括私有成员。

### 11.3 内部类可以有静态成员吗？

- 成员内部类：不能有静态成员（除非是编译时常量）
- 静态内部类：可以有静态成员
- 局部内部类：不能有静态成员
- 匿名内部类：不能有静态成员

### 11.4 内部类可以访问外部类的静态成员吗？

- 成员内部类：可以
- 静态内部类：可以
- 局部内部类：可以
- 匿名内部类：可以

## 12. 总结

- 内部类提供了更好的代码组织和封装
- 不同类型的内部类有不同的访问规则
- 合理使用内部类可以提高代码的可读性和维护性
- Java 8+的Lambda表达式可以替代部分匿名内部类

