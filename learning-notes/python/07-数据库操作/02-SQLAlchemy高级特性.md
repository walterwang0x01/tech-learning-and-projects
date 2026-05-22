# SQLAlchemy 高级特性
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

> SQLAlchemy ORM 的高级用法和优化技巧

<!-- version-check: SQLAlchemy 2.0.49, checked 2026-05-22 -->

> 💡 **风格说明**：本文示例使用 SQLAlchemy 1.x 经典风格（`Column()`、`session.query()`），便于初学者过渡。新项目应优先使用 2.0 推荐的 `DeclarativeBase` + `Mapped[]` + `select()` 风格，详见 [SQLAlchemy 2.0 迁移指南](https://docs.sqlalchemy.org/en/20/changelog/migration_20.html) 和 `01-Python数据库操作.md` 第 10 节。

## 1. 关系映射

### 1.1 一对多关系

```python
# <!-- 修复于 2026-05-22: 移除不存在的 Relationship 导入（应为 relationship 小写） -->
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    orders = relationship("Order", back_populates="user")

class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="orders")
```

### 1.2 多对多关系

```python
from sqlalchemy import Table, Column, Integer, ForeignKey

association_table = Table('user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    roles = relationship("Role", secondary=association_table, back_populates="users")

class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    users = relationship("User", secondary=association_table, back_populates="roles")
```

## 2. 查询优化

### 2.1 预加载（Eager Loading）

```python
from sqlalchemy.orm import joinedload, selectinload

# joinedload（JOIN查询）
users = session.query(User).options(joinedload(User.orders)).all()

# selectinload（子查询）
users = session.query(User).options(selectinload(User.orders)).all()
```

### 2.2 延迟加载控制

```python
from sqlalchemy.orm import lazyload, raiseload

# 延迟加载
users = session.query(User).options(lazyload(User.orders)).all()

# 禁止延迟加载（访问时抛出异常）
users = session.query(User).options(raiseload(User.orders)).all()
```

## 3. 查询构建

### 3.1 复杂查询

```python
from sqlalchemy import and_, or_, not_

# 组合条件
query = session.query(User).filter(
    and_(
        User.age >= 18,
        User.age <= 65,
        or_(
            User.status == 'active',
            User.status == 'pending'
        )
    )
)
```

### 3.2 子查询

```python
from sqlalchemy import func

# 标量子查询
subquery = session.query(func.count(Order.id)).filter(
    Order.user_id == User.id
).label('order_count')

users = session.query(User, subquery).all()

# 存在子查询
subquery = session.query(Order).filter(Order.user_id == User.id).exists()
users = session.query(User).filter(subquery).all()
```

## 4. 事件监听

### 4.1 模型事件

```python
from sqlalchemy import event

@event.listens_for(User, 'before_insert')
def receive_before_insert(mapper, connection, target):
    target.created_at = datetime.now()

@event.listens_for(User, 'after_update')
def receive_after_update(mapper, connection, target):
    print(f"用户 {target.id} 已更新")
```

## 5. 混合属性

### 5.1 计算属性

```python
from sqlalchemy.ext.hybrid import hybrid_property

class User(Base):
    first_name = Column(String(50))
    last_name = Column(String(50))
    
    @hybrid_property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @full_name.expression
    def full_name(cls):
        return func.concat(cls.first_name, ' ', cls.last_name)
```

## 6. 总结

SQLAlchemy高级特性：
- **关系映射**：一对多、多对多
- **查询优化**：预加载、延迟加载
- **复杂查询**：子查询、组合条件
- **事件监听**：模型事件处理
- **混合属性**：计算属性、表达式

这些高级特性提高开发效率和查询性能。

