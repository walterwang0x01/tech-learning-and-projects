# Java反射与注解
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 反射(Reflection)

### 1.1 反射概述

反射是Java语言的一个特性，它允许程序在运行时获取类的信息并操作类的属性、方法和构造函数。

### 1.2 反射的作用

1. **运行时获取类的信息**：类名、方法、字段、构造函数等
2. **动态创建对象**：在运行时创建类的实例
3. **动态调用方法**：在运行时调用对象的方法
4. **访问私有成员**：可以访问私有字段和方法（需要设置访问权限）

### 1.3 反射的优缺点

**优点**：
- 灵活性高，可以在运行时动态操作
- 框架开发的基础（Spring、MyBatis等）

**缺点**：
- 性能较低（比直接调用慢）
- 代码可读性差
- 安全性问题（可以访问私有成员）

## 2. Class类

### 2.1 获取Class对象

#### 方式一：通过类名.class

```java
Class<?> clazz = String.class;
```

#### 方式二：通过对象.getClass()

```java
String str = "hello";
Class<?> clazz = str.getClass();
```

#### 方式三：通过Class.forName()

```java
Class<?> clazz = Class.forName("java.lang.String");
```

### 2.2 Class类的常用方法

```java
Class<?> clazz = String.class;

// 获取类名
String name = clazz.getName();              // 全限定名：java.lang.String
String simpleName = clazz.getSimpleName();  // 简单名：String

// 获取包名
Package pkg = clazz.getPackage();

// 获取父类
Class<?> superClass = clazz.getSuperclass();

// 获取接口
Class<?>[] interfaces = clazz.getInterfaces();

// 判断类型
boolean isInterface = clazz.isInterface();
boolean isArray = clazz.isArray();
boolean isPrimitive = clazz.isPrimitive();
```

## 3. 反射操作字段(Field)

### 3.1 获取字段

```java
Class<?> clazz = User.class;

// 获取所有public字段（包括父类）
Field[] fields = clazz.getFields();

// 获取所有字段（包括private，不包括父类）
Field[] declaredFields = clazz.getDeclaredFields();

// 获取指定字段
Field field = clazz.getField("name");              // public字段
Field declaredField = clazz.getDeclaredField("id"); // 包括private
```

### 3.2 操作字段

```java
User user = new User();

// 获取字段
Field field = clazz.getDeclaredField("name");

// 设置访问权限（访问private字段需要）
field.setAccessible(true);

// 获取字段值
Object value = field.get(user);

// 设置字段值
field.set(user, "新值");

// 获取字段类型
Class<?> type = field.getType();

// 获取字段名
String fieldName = field.getName();
```

## 4. 反射操作方法(Method)

### 4.1 获取方法

```java
Class<?> clazz = User.class;

// 获取所有public方法（包括父类）
Method[] methods = clazz.getMethods();

// 获取所有方法（包括private，不包括父类）
Method[] declaredMethods = clazz.getDeclaredMethods();

// 获取指定方法
Method method = clazz.getMethod("getName");                    // 无参方法
Method method2 = clazz.getMethod("setName", String.class);     // 有参方法
```

### 4.2 调用方法

```java
User user = new User();

// 获取方法
Method method = clazz.getMethod("setName", String.class);

// 调用方法
method.invoke(user, "新名字");

// 调用静态方法
Method staticMethod = clazz.getMethod("staticMethod");
staticMethod.invoke(null);  // 静态方法第一个参数为null
```

### 4.3 方法信息

```java
Method method = clazz.getMethod("getName");

// 获取方法名
String methodName = method.getName();

// 获取返回类型
Class<?> returnType = method.getReturnType();

// 获取参数类型
Class<?>[] paramTypes = method.getParameterTypes();

// 获取异常类型
Class<?>[] exceptionTypes = method.getExceptionTypes();

// 获取方法修饰符
int modifiers = method.getModifiers();
boolean isPublic = Modifier.isPublic(modifiers);
boolean isStatic = Modifier.isStatic(modifiers);
```

## 5. 反射操作构造函数(Constructor)

### 5.1 获取构造函数

```java
Class<?> clazz = User.class;

// 获取所有public构造函数
Constructor<?>[] constructors = clazz.getConstructors();

// 获取所有构造函数（包括private）
Constructor<?>[] declaredConstructors = clazz.getDeclaredConstructors();

// 获取指定构造函数
Constructor<?> constructor = clazz.getConstructor();                    // 无参构造
Constructor<?> constructor2 = clazz.getConstructor(String.class);     // 有参构造
```

### 5.2 创建对象

```java
// 方式一：使用newInstance()（已废弃）
User user = (User) clazz.newInstance();

// 方式二：使用Constructor
Constructor<?> constructor = clazz.getConstructor();
User user = (User) constructor.newInstance();

// 使用有参构造
Constructor<?> constructor2 = clazz.getConstructor(String.class);
User user2 = (User) constructor2.newInstance("参数");
```

## 6. 反射应用示例

### 6.1 动态创建对象并调用方法

```java
public class ReflectionExample {
    public static void main(String[] args) throws Exception {
        // 获取Class对象
        Class<?> clazz = Class.forName("com.example.User");
        
        // 创建对象
        Object obj = clazz.newInstance();
        
        // 获取方法
        Method setNameMethod = clazz.getMethod("setName", String.class);
        Method getNameMethod = clazz.getMethod("getName");
        
        // 调用方法
        setNameMethod.invoke(obj, "张三");
        String name = (String) getNameMethod.invoke(obj);
        
        System.out.println(name);  // 输出：张三
    }
}
```

### 6.2 访问私有成员

```java
public class ReflectionExample {
    public static void main(String[] args) throws Exception {
        User user = new User();
        Class<?> clazz = user.getClass();
        
        // 获取私有字段
        Field privateField = clazz.getDeclaredField("privateField");
        
        // 设置访问权限
        privateField.setAccessible(true);
        
        // 访问私有字段
        Object value = privateField.get(user);
        privateField.set(user, "新值");
    }
}
```

## 7. 注解(Annotation)

### 7.1 注解概述

注解是Java 5引入的一种元数据机制，用于为程序元素（类、方法、字段等）提供信息。

### 7.2 内置注解

#### 7.2.1 @Override

```java
@Override
public String toString() {
    return "User";
}
```

#### 7.2.2 @Deprecated

```java
@Deprecated
public void oldMethod() {
    // 已废弃的方法
}
```

#### 7.2.3 @SuppressWarnings

```java
@SuppressWarnings("unchecked")
public void method() {
    // 抑制警告
}
```

#### 7.2.4 @SafeVarargs

```java
@SafeVarargs
public static <T> void method(T... args) {
    // 可变参数方法
}
```

#### 7.2.5 @FunctionalInterface

```java
@FunctionalInterface
public interface MyInterface {
    void method();
}
```

### 7.3 元注解

#### 7.3.1 @Target

指定注解可以应用的元素类型：

```java
@Target(ElementType.METHOD)  // 只能用于方法
public @interface MyAnnotation {
}
```

**ElementType取值**：
- TYPE：类、接口、枚举
- FIELD：字段
- METHOD：方法
- PARAMETER：参数
- CONSTRUCTOR：构造函数
- LOCAL_VARIABLE：局部变量
- ANNOTATION_TYPE：注解
- PACKAGE：包

#### 7.3.2 @Retention

指定注解的保留策略：

```java
@Retention(RetentionPolicy.RUNTIME)  // 运行时保留
public @interface MyAnnotation {
}
```

**RetentionPolicy取值**：
- SOURCE：源码级别，编译后丢弃
- CLASS：类文件级别，运行时不可获取
- RUNTIME：运行时保留，可以通过反射获取

#### 7.3.3 @Documented

指定注解是否包含在JavaDoc中：

```java
@Documented
public @interface MyAnnotation {
}
```

#### 7.3.4 @Inherited

指定注解是否可以被继承：

```java
@Inherited
public @interface MyAnnotation {
}
```

#### 7.3.5 @Repeatable

指定注解可以重复使用：

```java
@Repeatable(MyAnnotations.class)
public @interface MyAnnotation {
    String value();
}
```

### 7.4 自定义注解

#### 7.4.1 定义注解

```java
@Target(ElementType.METHOD)
@Retention(RetentionPolicy.RUNTIME)
public @interface MyAnnotation {
    String value() default "默认值";
    int count() default 0;
    String[] tags() default {};
}
```

#### 7.4.2 使用注解

```java
public class User {
    @MyAnnotation(value = "测试", count = 5, tags = {"tag1", "tag2"})
    public void method() {
        // 方法体
    }
}
```

### 7.5 注解处理器

#### 7.5.1 通过反射获取注解

```java
public class AnnotationProcessor {
    public static void process(Object obj) throws Exception {
        Class<?> clazz = obj.getClass();
        
        // 获取类上的注解
        MyAnnotation classAnnotation = clazz.getAnnotation(MyAnnotation.class);
        if (classAnnotation != null) {
            System.out.println("类注解值：" + classAnnotation.value());
        }
        
        // 获取方法上的注解
        Method[] methods = clazz.getMethods();
        for (Method method : methods) {
            MyAnnotation methodAnnotation = method.getAnnotation(MyAnnotation.class);
            if (methodAnnotation != null) {
                System.out.println("方法：" + method.getName());
                System.out.println("注解值：" + methodAnnotation.value());
                System.out.println("计数：" + methodAnnotation.count());
            }
        }
    }
}
```

#### 7.5.2 获取所有注解

```java
// 获取类上的所有注解
Annotation[] annotations = clazz.getAnnotations();

// 获取方法上的所有注解
Method method = clazz.getMethod("methodName");
Annotation[] methodAnnotations = method.getAnnotations();
```

## 8. 反射与注解的应用

### 8.1 Spring框架

- **依赖注入**：通过反射创建对象并注入依赖
- **AOP**：通过反射和代理实现切面编程
- **注解驱动**：通过注解和反射实现配置

### 8.2 MyBatis框架

- **Mapper接口**：通过动态代理和反射实现接口方法调用
- **结果映射**：通过反射将查询结果映射到对象

### 8.3 序列化框架

- **JSON序列化**：通过反射获取对象字段并序列化
- **对象克隆**：通过反射实现深拷贝

## 9. 性能优化

### 9.1 缓存Class对象

```java
private static final Class<?> CLAZZ = User.class;
```

### 9.2 缓存Method对象

```java
private static final Method METHOD = clazz.getMethod("methodName");
```

### 9.3 使用MethodHandle（JDK 7+）

```java
MethodHandles.Lookup lookup = MethodHandles.lookup();
MethodHandle handle = lookup.findVirtual(clazz, "methodName", 
    MethodType.methodType(void.class));
handle.invoke(obj);
```

## 10. 最佳实践

1. **谨慎使用反射**：反射性能较低，只在必要时使用
2. **缓存反射对象**：Class、Method、Field等对象可以缓存
3. **合理使用注解**：注解可以简化配置，但不要过度使用
4. **注意安全性**：反射可以访问私有成员，注意安全性
5. **使用工具类**：使用Apache Commons、Spring等工具类简化反射操作

