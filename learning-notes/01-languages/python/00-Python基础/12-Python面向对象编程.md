# Python面向对象编程
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 面向对象编程概述

面向对象编程是一种非常流行的**编程范式**（programming paradigm），所谓编程范式就是**程序设计的方法论**。

### 1.1 核心概念

> **面向对象编程**：把一组数据和处理数据的方法组成**对象**，把行为相同的对象归纳为**类**，通过**封装**隐藏对象的内部细节，通过**继承**实现类的特化和泛化，通过**多态**实现基于对象类型的动态分派。

**关键词**：
- **对象**（object）
- **类**（class）
- **封装**（encapsulation）
- **继承**（inheritance）
- **多态**（polymorphism）

### 1.2 类和对象

- **类**：是一个抽象的概念，是对象的蓝图和模板
- **对象**：是一个具体的概念，是类的实例，是可以接受消息的实体
- **关系**：类是对象的模板，对象是类的实例

## 2. 定义类

在 Python 语言中，我们可以使用`class`关键字加上类名来定义类。

```python
class Student:
    """学生类"""

    def study(self, course_name):
        """学习"""
        print(f'学生正在学习{course_name}.')

    def play(self):
        """玩耍"""
        print(f'学生正在玩游戏.')
```

**说明**：
- 写在类里面的函数通常称之为**方法**
- 方法的第一个参数通常都是`self`，它代表了接收这个消息的对象本身

## 3. 创建和使用对象

### 3.1 创建对象

```python
stu1 = Student()
stu2 = Student()
print(stu1)    # <__main__.Student object at 0x10ad5ac50>
print(stu2)    # <__main__.Student object at 0x10ad5acd0>
```

### 3.2 调用方法

Python中，给对象发消息有两种方式：

```python
# 方式一：通过"类.方法"调用方法
Student.study(stu1, 'Python程序设计')    # 学生正在学习Python程序设计.

# 方式二：通过"对象.方法"调用方法（推荐）
stu1.study('Python程序设计')             # 学生正在学习Python程序设计.
```

## 4. 初始化方法

在我们调用`Student`类的构造器创建对象时，首先会在内存中获得保存学生对象所需的内存空间，然后通过自动执行`__init__`方法，完成对内存的初始化操作。

```python
class Student:
    """学生"""

    def __init__(self, name, age):
        """初始化方法"""
        self.name = name
        self.age = age

    def study(self, course_name):
        """学习"""
        print(f'{self.name}正在学习{course_name}.')

    def play(self):
        """玩耍"""
        print(f'{self.name}正在玩游戏.')

# 调用Student类的构造器创建对象并传入初始化参数
stu1 = Student('骆昊', 44)
stu2 = Student('王大锤', 25)
stu1.study('Python程序设计')    # 骆昊正在学习Python程序设计.
stu2.play()                    # 王大锤正在玩游戏.
```

## 5. 面向对象的支柱

### 5.1 封装

**封装**：隐藏一切可以隐藏的实现细节，只向外界暴露简单的调用接口。

```python
class Student:
    def __init__(self, name, age):
        self.name = name  # 公有属性
        self._age = age   # 受保护属性（约定，单下划线）
        self.__id = 123   # 私有属性（约定，双下划线）

stu = Student('张三', 20)
print(stu.name)      # 可以直接访问
print(stu._age)      # 可以访问但不推荐
# print(stu.__id)    # 访问私有属性会报错（实际上是名称改写）
```

**说明**：Python 并没有真正的私有属性，双下划线只是触发了名称改写（name mangling）。

### 5.2 继承

**继承**：在已有类的基础上创建新类，从而减少重复代码的编写。

```python
class Person:
    """人"""

    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def eat(self):
        """吃饭"""
        print(f'{self.name}正在吃饭.')
    
    def sleep(self):
        """睡觉"""
        print(f'{self.name}正在睡觉.')


class Student(Person):
    """学生"""
    
    def __init__(self, name, age):
        super().__init__(name, age)  # 调用父类初始化方法
    
    def study(self, course_name):
        """学习"""
        print(f'{self.name}正在学习{course_name}.')


class Teacher(Person):
    """老师"""

    def __init__(self, name, age, title):
        super().__init__(name, age)
        self.title = title
    
    def teach(self, course_name):
        """教学"""
        print(f'{self.name}{self.title}正在讲授{course_name}.')


stu = Student('白元芳', 21)
tea = Teacher('武则天', 35, '副教授')
stu.eat()    # 白元芳正在吃饭.
stu.study('Python程序设计')  # 白元芳正在学习Python程序设计.
tea.teach('Python程序设计')  # 武则天副教授正在讲授Python程序设计.
```

**说明**：
- 继承的语法是在定义类的时候，在类名后的圆括号中指定当前类的父类
- 如果定义一个类的时候没有指定它的父类是谁，那么默认的父类是`object`类
- 在子类的初始化方法中，可以通过`super().__init__()`来调用父类初始化方法

### 5.3 多态

**多态**：不同的子类可以对父类的同一个方法给出不同的实现版本，这样的方法在程序运行时就会表现出多态行为。

```python
class Animal:
    def make_sound(self):
        pass


class Dog(Animal):
    def make_sound(self):
        print('汪汪汪')


class Cat(Animal):
    def make_sound(self):
        print('喵喵喵')


def animal_sound(animal):
    animal.make_sound()  # 多态调用

dog = Dog()
cat = Cat()
animal_sound(dog)  # 汪汪汪
animal_sound(cat)  # 喵喵喵
```

## 6. 类的方法类型

### 6.1 实例方法

实例方法是对象的方法，第一个参数是`self`。

```python
class Student:
    def study(self, course_name):
        print(f'正在学习{course_name}')
```

### 6.2 类方法

类方法是发给类的消息，使用`@classmethod`装饰器定义，第一个参数是`cls`。

```python
class Student:
    count = 0  # 类属性

    @classmethod
    def get_count(cls):
        return cls.count
```

### 6.3 静态方法

静态方法也是发给类的消息，使用`@staticmethod`装饰器定义，不需要`self`或`cls`参数。

```python
class Triangle:
    @staticmethod
    def is_valid(a, b, c):
        """判断三条边长能否构成三角形"""
        return a + b > c and b + c > a and a + c > b
```

## 7. 属性装饰器

使用`@property`装饰器可以将方法转换为属性。

```python
class Triangle:
    def __init__(self, a, b, c):
        self.a = a
        self.b = b
        self.c = c

    @property
    def perimeter(self):
        """计算周长"""
        return self.a + self.b + self.c

    @property
    def area(self):
        """计算面积"""
        p = self.perimeter / 2
        return (p * (p - self.a) * (p - self.b) * (p - self.c)) ** 0.5

t = Triangle(3, 4, 5)
print(t.perimeter)  # 12（作为属性访问，不是方法调用）
print(t.area)       # 6.0
```

## 8. 特殊方法（魔术方法）

Python 中有很多特殊方法，它们以双下划线开头和结尾，用于实现特定的功能。

### 8.1 __str__和__repr__

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        """返回对象的字符串表示（用户友好）"""
        return f'({self.x}, {self.y})'

    def __repr__(self):
        """返回对象的字符串表示（开发者友好）"""
        return f'Point({self.x}, {self.y})'

p = Point(3, 5)
print(p)        # (3, 5)（调用__str__）
print(repr(p))  # Point(3, 5)（调用__repr__）
```

### 8.2 __len__

```python
class MyList:
    def __init__(self, items):
        self.items = items

    def __len__(self):
        return len(self.items)

my_list = MyList([1, 2, 3, 4, 5])
print(len(my_list))  # 5
```

### 8.3 __getitem__和__setitem__

```python
class MyList:
    def __init__(self, items):
        self.items = items

    def __getitem__(self, index):
        return self.items[index]

    def __setitem__(self, index, value):
        self.items[index] = value

my_list = MyList([1, 2, 3, 4, 5])
print(my_list[0])     # 1
my_list[0] = 10
print(my_list[0])     # 10
```

## 9. 动态属性

Python 语言属于动态语言，可以动态为对象添加属性。

```python
class Student:
    def __init__(self, name, age):
        self.name = name
        self.age = age

stu = Student('王大锤', 20)
stu.sex = '男'  # 动态添加属性
```

### 9.1 __slots__

如果不希望在使用对象时动态的为对象添加属性，可以使用`__slots__`。

```python
class Student:
    __slots__ = ('name', 'age')  # 限制只能有name和age属性

    def __init__(self, name, age):
        self.name = name
        self.age = age

stu = Student('王大锤', 20)
# stu.sex = '男'  # AttributeError: 'Student' object has no attribute 'sex'
```

## 10. 面向对象应用示例

### 10.1 时钟示例

```python
import time

class Clock:
    """数字时钟"""

    def __init__(self, hour=0, minute=0, second=0):
        """初始化方法"""
        self.hour = hour
        self.min = minute
        self.sec = second

    def run(self):
        """走字"""
        self.sec += 1
        if self.sec == 60:
            self.sec = 0
            self.min += 1
            if self.min == 60:
                self.min = 0
                self.hour += 1
                if self.hour == 24:
                    self.hour = 0

    def show(self):
        """显示时间"""
        return f'{self.hour:0>2d}:{self.min:0>2d}:{self.sec:0>2d}'

clock = Clock(23, 59, 58)
print(clock.show())  # 23:59:58
```

### 10.2 平面上的点示例

```python
class Point:
    """平面上的点"""

    def __init__(self, x=0, y=0):
        """初始化方法"""
        self.x, self.y = x, y

    def distance_to(self, other):
        """计算与另一个点的距离"""
        dx = self.x - other.x
        dy = self.y - other.y
        return (dx * dx + dy * dy) ** 0.5

    def __str__(self):
        return f'({self.x}, {self.y})'

p1 = Point(3, 5)
p2 = Point(6, 9)
print(p1)                  # (3, 5)
print(p1.distance_to(p2))  # 5.0
```

## 11. 多重继承

Python 支持多重继承，也就是说一个类可以有一个或多个父类。

```python
class A:
    def method(self):
        print('A method')

class B:
    def method(self):
        print('B method')

class C(A, B):
    pass

c = C()
c.method()  # A method（按照继承顺序，先找到A的方法）
```

## 12. 最佳实践

1. **单一职责原则**：每个类应该只有一个职责
2. **开放封闭原则**：对扩展开放，对修改封闭
3. **里氏替换原则**：子类对象可以替换父类对象
4. **接口隔离原则**：使用多个专门的接口，而不是使用单一的总接口
5. **依赖倒置原则**：依赖抽象而不是依赖具体

## 13. 总结

面向对象编程是一种非常流行的编程范式，它更符合人类正常的思维习惯。类是抽象的，对象是具体的，有了类就能创建对象，有了对象就可以接收消息，这就是面向对象编程的基础。掌握类的定义、对象的创建、继承、多态和特殊方法对于 Python 编程非常重要。
## 🎬 推荐视频资源

- [Corey Schafer - Python OOP Tutorial](https://www.youtube.com/playlist?list=PL-osiE80TeTsqhIuOqKhwlXsIBIdSeYtc) — Python OOP完整系列（6集）
- [Tech With Tim - Python OOP](https://www.youtube.com/watch?v=JeznW_7DlB0) — OOP快速入门
### 📺 B站（Bilibili）
- [黑马程序员 - Python面向对象](https://www.bilibili.com/video/BV1qW4y1a7fU) — 包含OOP完整章节
- [小甲鱼 - Python面向对象](https://www.bilibili.com/video/BV1c4411e77t) — OOP部分讲解清晰

### 🌐 其他平台
- [廖雪峰 - 面向对象编程](https://www.liaoxuefeng.com/wiki/1016959663602400/1017495723838528) — 中文OOP教程
