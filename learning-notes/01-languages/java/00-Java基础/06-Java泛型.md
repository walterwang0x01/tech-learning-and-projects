# Java泛型
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 泛型概述

### 1.1 什么是泛型

泛型是Java 5引入的特性，它允许在定义类、接口和方法时使用类型参数，在使用时指定具体的类型。

### 1.2 泛型的作用

1. **类型安全**：在编译时检查类型，避免类型转换异常
2. **消除强制类型转换**：不需要手动进行类型转换
3. **提高代码可读性**：代码更加清晰，意图更明确
4. **代码复用**：可以编写更通用的代码

### 1.3 泛型的使用场景

- 集合类（List、Set、Map等）
- 自定义类和方法
- 接口定义

## 2. 泛型类

### 2.1 定义泛型类

```java
public class Box<T> {
    private T item;
    
    public void setItem(T item) {
        this.item = item;
    }
    
    public T getItem() {
        return item;
    }
}
```

### 2.2 使用泛型类

```java
Box<String> stringBox = new Box<>();
stringBox.setItem("Hello");
String value = stringBox.getItem();  // 不需要类型转换

Box<Integer> intBox = new Box<>();
intBox.setItem(100);
Integer num = intBox.getItem();
```

### 2.3 多个类型参数

```java
public class Pair<K, V> {
    private K key;
    private V value;
    
    public Pair(K key, V value) {
        this.key = key;
        this.value = value;
    }
    
    public K getKey() {
        return key;
    }
    
    public V getValue() {
        return value;
    }
}

// 使用
Pair<String, Integer> pair = new Pair<>("age", 25);
```

## 3. 泛型方法

### 3.1 定义泛型方法

```java
public class Util {
    public static <T> T getMiddle(T[] array) {
        return array[array.length / 2];
    }
    
    public static <T> void swap(List<T> list, int i, int j) {
        T temp = list.get(i);
        list.set(i, list.get(j));
        list.set(j, temp);
    }
}
```

### 3.2 使用泛型方法

```java
String[] strings = {"a", "b", "c"};
String middle = Util.getMiddle(strings);

List<String> list = Arrays.asList("a", "b", "c");
Util.swap(list, 0, 2);
```

### 3.3 泛型方法与泛型类的区别

- **泛型类**：整个类都是泛型的
- **泛型方法**：只有方法是泛型的，可以定义在普通类中

```java
public class GenericMethod {
    // 泛型方法
    public <T> void print(T item) {
        System.out.println(item);
    }
    
    // 普通方法
    public void printString(String str) {
        System.out.println(str);
    }
}
```

## 4. 泛型接口

### 4.1 定义泛型接口

```java
public interface Comparable<T> {
    int compareTo(T other);
}
```

### 4.2 实现泛型接口

```java
public class Student implements Comparable<Student> {
    private String name;
    private int age;
    
    @Override
    public int compareTo(Student other) {
        return this.age - other.age;
    }
}
```

## 5. 类型通配符

### 5.1 无界通配符（?）

```java
public void printList(List<?> list) {
    for (Object item : list) {
        System.out.println(item);
    }
}
```

**特点**：
- 可以接受任何类型的List
- 只能读取，不能写入（除了null）

### 5.2 上界通配符（? extends T）

```java
public void processNumbers(List<? extends Number> list) {
    for (Number num : list) {
        System.out.println(num.doubleValue());
    }
}
```

**特点**：
- 可以接受T及其子类型的List
- 只能读取，不能写入（除了null）
- 适用于"生产者"场景

**使用示例：**
```java
List<Integer> intList = Arrays.asList(1, 2, 3);
List<Double> doubleList = Arrays.asList(1.1, 2.2, 3.3);

processNumbers(intList);     // 可以
processNumbers(doubleList);  // 可以
```

### 5.3 下界通配符（? super T）

```java
public void addNumbers(List<? super Integer> list) {
    list.add(1);
    list.add(2);
    list.add(3);
}
```

**特点**：
- 可以接受T及其父类型的List
- 可以写入T类型的元素
- 只能读取为Object类型
- 适用于"消费者"场景

**使用示例：**
```java
List<Number> numberList = new ArrayList<>();
List<Object> objectList = new ArrayList<>();

addNumbers(numberList);   // 可以
addNumbers(objectList);   // 可以
```

### 5.4 PECS原则

- **Producer Extends**：生产者使用extends
- **Consumer Super**：消费者使用super

```java
// 生产者：从集合中读取数据
public void copy(List<? extends T> src, List<? super T> dest) {
    for (T item : src) {
        dest.add(item);
    }
}
```

## 6. 类型擦除

### 6.1 什么是类型擦除

Java的泛型是通过类型擦除实现的，在编译时擦除类型信息，运行时只保留原始类型。

### 6.2 类型擦除示例

```java
// 编译前
List<String> list = new ArrayList<>();
list.add("hello");

// 编译后（类型擦除）
List list = new ArrayList();
list.add("hello");
```

### 6.3 类型擦除的影响

#### 不能使用instanceof

```java
// 编译错误
if (list instanceof List<String>) {
    // ...
}
```

#### 不能创建泛型数组

```java
// 编译错误
List<String>[] array = new List<String>[10];

// 可以这样
List<String>[] array = (List<String>[]) new List[10];
```

#### 不能重载

```java
// 编译错误：方法签名相同
public void method(List<String> list) {}
public void method(List<Integer> list) {}
```

## 7. 泛型限制

### 7.1 不能使用基本类型

```java
// 错误
List<int> list = new ArrayList<>();

// 正确
List<Integer> list = new ArrayList<>();
```

### 7.2 不能实例化类型参数

```java
// 错误
public <T> void method() {
    T obj = new T();  // 编译错误
}

// 可以通过反射实现
public <T> T createInstance(Class<T> clazz) throws Exception {
    return clazz.newInstance();
}
```

### 7.3 不能使用静态类型参数

```java
public class Box<T> {
    // 错误：不能在静态上下文中使用类型参数
    private static T staticField;
    
    // 错误
    public static T staticMethod() {
        // ...
    }
}
```

### 7.4 不能捕获泛型异常

```java
// 错误
public <T extends Exception> void method() {
    try {
        // ...
    } catch (T e) {  // 编译错误
        // ...
    }
}
```

## 8. 泛型与反射

### 8.1 获取泛型类型信息

```java
public class GenericTypeExample {
    private List<String> stringList;
    
    public static void main(String[] args) throws Exception {
        Field field = GenericTypeExample.class.getDeclaredField("stringList");
        Type type = field.getGenericType();
        
        if (type instanceof ParameterizedType) {
            ParameterizedType pType = (ParameterizedType) type;
            Type[] actualTypes = pType.getActualTypeArguments();
            System.out.println(actualTypes[0]);  // class java.lang.String
        }
    }
}
```

### 8.2 TypeReference的使用

```java
// 使用TypeReference保留泛型信息
TypeReference<List<String>> typeRef = new TypeReference<List<String>>() {};
Type type = typeRef.getType();
```

## 9. 实际应用

### 9.1 集合框架中的泛型

```java
List<String> list = new ArrayList<>();
Map<String, Integer> map = new HashMap<>();
Set<Student> set = new HashSet<>();
```

### 9.2 工具类中的泛型

```java
public class CollectionUtils {
    public static <T> boolean isEmpty(Collection<T> collection) {
        return collection == null || collection.isEmpty();
    }
    
    public static <T> T getFirst(List<T> list) {
        return list != null && !list.isEmpty() ? list.get(0) : null;
    }
}
```

### 9.3 工厂模式中的泛型

```java
public interface Factory<T> {
    T create();
}

public class StringFactory implements Factory<String> {
    @Override
    public String create() {
        return new String();
    }
}
```

## 10. 最佳实践

1. **使用有意义的类型参数名**：T、E、K、V等
2. **优先使用泛型方法**：如果只有方法需要泛型，使用泛型方法而不是泛型类
3. **理解类型擦除**：了解泛型的实现机制
4. **合理使用通配符**：遵循PECS原则
5. **避免原始类型**：不要使用不带类型参数的泛型类型
6. **使用@SuppressWarnings**：在确实需要时使用，并添加注释说明原因

## 11. 常见问题

### 11.1 为什么需要泛型？

- 提供类型安全
- 消除强制类型转换
- 提高代码可读性

### 11.2 泛型与Object的区别？

- 泛型在编译时进行类型检查
- Object需要运行时类型转换，容易出错

### 11.3 如何获取泛型的实际类型？

- 通过反射获取ParameterizedType
- 使用TypeReference保留泛型信息

