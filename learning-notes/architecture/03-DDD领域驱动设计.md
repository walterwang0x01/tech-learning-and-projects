# DDD 领域驱动设计
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

<!-- version-check: DDD 设计模式, checked 2026-04-21 -->
<!-- version-check: DDD × LLM/Agent context engineering, checked 2026-05-11 -->

## 1. 概述

DDD（Domain-Driven Design）是一种以业务领域为核心的软件设计方法论。核心思想：软件的复杂性来自业务本身，代码结构应该反映业务结构。

```
┌──────────── DDD 分层架构 ────────────┐
│                                       │
│  ┌─────────────────────────────────┐ │
│  │  Interface Layer（接口层）        │ │
│  │  Controller / API / DTO          │ │
│  └──────────────┬──────────────────┘ │
│  ┌──────────────┴──────────────────┐ │
│  │  Application Layer（应用层）      │ │
│  │  Service / Command / Query       │ │
│  │  编排领域对象，不含业务逻辑        │ │
│  └──────────────┬──────────────────┘ │
│  ┌──────────────┴──────────────────┐ │
│  │  Domain Layer（领域层）⭐ 核心    │ │
│  │  Entity / Value Object /         │ │
│  │  Aggregate / Domain Service /    │ │
│  │  Domain Event / Repository       │ │
│  └──────────────┬──────────────────┘ │
│  ┌──────────────┴──────────────────┐ │
│  │  Infrastructure Layer（基础设施） │ │
│  │  DB / MQ / Cache / External API  │ │
│  └─────────────────────────────────┘ │
└───────────────────────────────────────┘
```

## 2. 战略设计

### 2.1 限界上下文（Bounded Context）

```
┌─────────── 电商系统限界上下文 ───────────┐
│                                           │
│  ┌──────────┐  ┌──────────┐  ┌─────────┐│
│  │ 用户上下文 │  │ 订单上下文 │  │ 支付上下文││
│  │           │  │           │  │          ││
│  │ User      │  │ Order     │  │ Payment  ││
│  │ Address   │  │ OrderItem │  │ Refund   ││
│  │ Profile   │  │ Shipping  │  │ Account  ││
│  └─────┬────┘  └─────┬────┘  └────┬─────┘│
│        │              │             │      │
│        └──── 上下文映射（Context Map）────┘ │
│                                           │
│  同一个概念在不同上下文中含义不同：          │
│  "User" 在用户上下文 = 完整用户信息         │
│  "User" 在订单上下文 = 只有 userId + name  │
│  "User" 在支付上下文 = 只有 payerId        │
└───────────────────────────────────────────┘
```

### 2.2 上下文映射关系

```
上下文间的协作模式：
├─ 合作关系（Partnership）
│   两个团队紧密合作，共同演进
├─ 共享内核（Shared Kernel）
│   共享一小部分模型代码
├─ 客户-供应商（Customer-Supplier）
│   上游提供，下游消费，上游优先
├─ 防腐层（Anti-Corruption Layer, ACL）⭐
│   下游通过适配器隔离上游模型变化
├─ 开放主机服务（Open Host Service）
│   上游提供标准化 API
└─ 发布语言（Published Language）
    用标准格式（JSON Schema / Protobuf）通信
```

```python
# 防腐层示例：隔离外部支付系统的模型变化
class PaymentACL:
    """防腐层：将外部支付系统的模型转换为领域模型"""

    def __init__(self, external_client):
        self.client = external_client

    def create_payment(self, order: Order) -> Payment:
        # 外部系统的数据结构
        external_result = self.client.charge({
            "merchant_id": "xxx",
            "amount_cents": order.total_amount.cents,
            "currency": "CNY",
            "reference": str(order.id),
        })

        # 转换为领域模型
        return Payment(
            payment_id=PaymentId(external_result["txn_id"]),
            order_id=order.id,
            amount=Money(external_result["amount_cents"], Currency.CNY),
            status=self._map_status(external_result["status"]),
        )

    def _map_status(self, external_status: str) -> PaymentStatus:
        mapping = {
            "succeeded": PaymentStatus.COMPLETED,
            "pending": PaymentStatus.PROCESSING,
            "failed": PaymentStatus.FAILED,
        }
        return mapping.get(external_status, PaymentStatus.UNKNOWN)
```

## 3. 战术设计

### 3.1 实体（Entity）

有唯一标识，生命周期内标识不变。

```python
from dataclasses import dataclass, field
from uuid import uuid4

@dataclass
class Order:
    """订单实体：有唯一标识，包含业务逻辑"""
    id: str = field(default_factory=lambda: str(uuid4()))
    user_id: str = ""
    items: list = field(default_factory=list)
    status: str = "draft"

    def add_item(self, product_id: str, quantity: int, price: int):
        """业务逻辑在实体内部"""
        if self.status != "draft":
            raise DomainError("只有草稿状态的订单可以添加商品")
        if quantity <= 0:
            raise DomainError("数量必须大于 0")
        self.items.append(OrderItem(product_id, quantity, price))

    def place(self) -> list:
        """下单：返回领域事件"""
        if not self.items:
            raise DomainError("订单不能为空")
        self.status = "placed"
        return [OrderPlaced(order_id=self.id, items=self.items)]

    @property
    def total_amount(self) -> int:
        return sum(item.quantity * item.price for item in self.items)
```

### 3.2 值对象（Value Object）

无唯一标识，通过属性值判断相等，不可变。

```python
from dataclasses import dataclass

@dataclass(frozen=True)  # frozen=True 保证不可变
class Money:
    """值对象：通过值判断相等"""
    amount: int       # 分为单位
    currency: str

    def __post_init__(self):
        if self.amount < 0:
            raise ValueError("金额不能为负")

    def add(self, other: "Money") -> "Money":
        if self.currency != other.currency:
            raise ValueError("币种不同不能相加")
        return Money(self.amount + other.amount, self.currency)

# 值对象通过值比较
assert Money(100, "CNY") == Money(100, "CNY")  # True
assert Money(100, "CNY") != Money(200, "CNY")  # True

@dataclass(frozen=True)
class Address:
    """地址值对象"""
    province: str
    city: str
    district: str
    street: str
    zip_code: str
```

### 3.3 聚合与聚合根（Aggregate & Aggregate Root）

```
┌─────────── 聚合边界 ───────────┐
│                                 │
│  Order（聚合根）                 │
│  ├─ OrderItem（实体）           │
│  ├─ OrderItem（实体）           │
│  └─ ShippingAddress（值对象）   │
│                                 │
│  规则：                          │
│  ├─ 外部只能引用聚合根           │
│  ├─ 聚合内保证事务一致性         │
│  ├─ 聚合间通过领域事件通信       │
│  └─ 聚合尽量小                  │
└─────────────────────────────────┘
```

```python
class OrderRepository:
    """仓储：只对聚合根操作"""

    def save(self, order: Order):
        """保存整个聚合（订单 + 订单项 + 地址）"""
        self.db.orders.upsert(order.to_dict())

    def find_by_id(self, order_id: str) -> Order:
        """加载整个聚合"""
        data = self.db.orders.find_one({"id": order_id})
        return Order.from_dict(data)

    # ❌ 错误：不应该直接操作聚合内部的实体
    # def save_order_item(self, item: OrderItem): ...
```

### 3.4 领域事件（Domain Event）

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class DomainEvent:
    """领域事件基类"""
    event_id: str = field(default_factory=lambda: str(uuid4()))
    occurred_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

@dataclass
class OrderPlaced(DomainEvent):
    """订单已下单事件"""
    order_id: str = ""
    user_id: str = ""
    total_amount: int = 0

@dataclass
class PaymentCompleted(DomainEvent):
    """支付完成事件"""
    payment_id: str = ""
    order_id: str = ""
    amount: int = 0

# 领域事件处理
class OrderPlacedHandler:
    def handle(self, event: OrderPlaced):
        # 触发下游动作
        self.inventory_service.reserve(event.order_id)
        self.notification_service.send_confirmation(event.user_id)
```

### 3.5 领域服务（Domain Service）

当业务逻辑不属于任何一个实体时，放在领域服务中。

```python
class PricingService:
    """定价领域服务：跨多个实体的业务逻辑"""

    def calculate_discount(self, order: Order, user: User) -> Money:
        """计算折扣：涉及订单和用户两个聚合"""
        discount = Money(0, "CNY")

        # VIP 用户 9 折
        if user.is_vip:
            discount = discount.add(
                Money(int(order.total_amount * 0.1), "CNY")
            )

        # 满 500 减 50
        if order.total_amount >= 50000:
            discount = discount.add(Money(5000, "CNY"))

        return discount
```

## 4. 项目结构示例

```
order-service/
├── interfaces/              # 接口层
│   ├── rest/
│   │   ├── order_controller.py
│   │   └── dto.py           # 数据传输对象
│   └── event/
│       └── order_event_consumer.py
├── application/             # 应用层
│   ├── order_service.py     # 应用服务（编排）
│   ├── commands.py          # 命令对象
│   └── queries.py           # 查询对象
├── domain/                  # 领域层 ⭐
│   ├── model/
│   │   ├── order.py         # 聚合根
│   │   ├── order_item.py    # 实体
│   │   └── money.py         # 值对象
│   ├── event/
│   │   └── order_events.py  # 领域事件
│   ├── service/
│   │   └── pricing_service.py
│   └── repository/
│       └── order_repository.py  # 仓储接口
└── infrastructure/          # 基础设施层
    ├── persistence/
    │   └── order_repository_impl.py  # 仓储实现
    ├── messaging/
    │   └── kafka_publisher.py
    └── external/
        └── payment_acl.py   # 防腐层
```

## 5. DDD vs 传统三层架构

| 维度 | 传统三层 | DDD |
|------|---------|-----|
| 核心 | 数据库表结构 | 业务领域模型 |
| 业务逻辑 | Service 层（贫血模型） | Entity/Domain Service（充血模型） |
| 数据模型 | 一个全局模型 | 每个上下文独立模型 |
| 复杂度管理 | 靠经验 | 限界上下文 + 聚合 |
| 适用场景 | CRUD 为主 | 复杂业务逻辑 |
| 学习成本 | 低 | 高 |

```
什么时候用 DDD：
├─ 业务逻辑复杂（不是简单 CRUD）
├─ 团队需要统一语言（业务和技术对齐）
├─ 系统需要长期演进
└─ 微服务拆分需要指导

什么时候不用：
├─ 简单 CRUD 应用
├─ 原型 / MVP
├─ 团队对 DDD 不熟悉且项目紧急
└─ 业务逻辑简单明确
```

## 6. 与现有笔记的关联

```
DDD 涉及的知识点：
├─ 微服务拆分 → 本目录/02-微服务架构模式.md
├─ 事件驱动 → 本目录/01-事件驱动架构.md
├─ CQRS → 本目录/04-CQRS与事件溯源.md
├─ Agent 多系统设计 → ai-agent/09-多Agent系统/
└─ Spring Boot 实现 → java/Spring Boot/
```

## 📖 参考资料

- [Eric Evans - Domain-Driven Design](https://www.domainlanguage.com/ddd/)
- [Vaughn Vernon - Implementing Domain-Driven Design](https://www.informit.com/store/implementing-domain-driven-design-9780321834577)
- [Martin Fowler - Bounded Context](https://martinfowler.com/bliki/BoundedContext.html)

## 7. DDD 与 AI Agent / LLM 协作（2026 新趋势）

> 🔄 更新于 2026-05-11

<!-- version-check: DDD × LLM/Agent context engineering, checked 2026-05-11 -->

2026 年 DDD 社区出现一个显著的新议题：**限界上下文不仅是服务边界，也是 LLM 的"上下文消费边界"**。DDD Europe 2026 专门设立了 "The Curse of Unbounded Contexts: Using Domains as LLM Consumers" 议题。来源：[DDD Europe 2026](https://2026.dddeurope.com/program/the-curse-of-unbounded-contexts-using-domains-as-llm-consumers/)

### 7.1 为什么 DDD 在 LLM 时代重新变热

```
┌─────────── 问题场景 ───────────┐
│  单体代码库 + LLM：             │
│                                 │
│  LLM 加载整库 → 上下文爆炸     │
│         ↓                       │
│  推理分散 → 生成的代码不贴合业务│
│         ↓                       │
│  领域专家发现：不是他们想要的    │
└─────────────────────────────────┘

         ┌─── 解决思路 ───┐
         │  限界上下文 =  │
         │  LLM 工作边界  │
         └────────────────┘

 Order Context    User Context    Payment Context
   ↓ 只喂 LLM      ↓ 只喂 LLM       ↓ 只喂 LLM
  Order/Item     User/Profile    Payment/Refund
```

LLM 在限界上下文内工作时：生成的 API、数据结构、业务规则更贴近领域语言。限界上下文内的**通用语言（Ubiquitous Language）**实际上就是 LLM 所需的"领域词汇表"。来源：[codecentric - Collaborative Modeling and LLMs](https://www.codecentric.de/en/knowledge-hub/blog/from-stories-to-code-how-domain-storytelling-and-eventstorming-give-llms-the-context-they-need)

### 7.2 Event Storming × AI：DDD 建模流程的 AI 辅助

Event Storming（事件风暴）是 DDD 的核心建模工作坊。2026 年社区验证了**"Event Storming 产物作为 LLM 上下文"**的高效模式：

```
Event Storming 产出物 → LLM Context 映射：
│
├─ Domain Events（领域事件）
│   → LLM 理解"业务时间线"
│
├─ Commands（命令）
│   → LLM 知道"可触发的操作"
│
├─ Aggregates（聚合）
│   → LLM 识别"事务一致性边界"
│
├─ Policies（策略）
│   → LLM 学习"业务自动化规则"
│
└─ Read Models（读模型）
    → LLM 了解"查询视角与数据形态"
```

来源：[AiOps School - Event Storming 2026 Guide](https://aiopsschool.com/blog/event-storming/)

### 7.3 DDD × LLM Agent：五步工作流

学术界提出了将 DDD 分解为 LLM Prompting Framework 的方案，将 DDD 流程抽象为 5 个顺序步骤：

```
┌─── DDD-LLM 五步工作流 ───┐
│                            │
│  1. 建立 Ubiquitous Language │
│     → LLM 提取业务术语        │
│                            │
│  2. 模拟 Event Storming     │
│     → LLM 生成领域事件候选    │
│                            │
│  3. 识别 Bounded Contexts   │
│     → LLM 聚类相关概念        │
│                            │
│  4. 设计 Aggregates        │
│     → LLM 分析一致性边界      │
│                            │
│  5. 映射到技术架构           │
│     → LLM 生成服务分解建议    │
└────────────────────────────┘
```

来源：[arxiv - DDD with LLM Prompting Framework](https://arxiv.org/html/2603.26244v1)

### 7.4 常见聚合设计错误（2026 总结）

随着 DDD 与 AI Agent 的结合，聚合设计中的老问题反而更容易被放大。社区总结了几个常见陷阱：

| 错误 | 表现 | 修复思路 |
| ---- | ---- | -------- |
| 混淆"数据关系"与"一致性需求" | 把所有相关实体塞到一个聚合 | 只保留"必须原子更新"的对象 |
| 聚合过大 | 加载/保存性能差、并发冲突多 | 拆分为多个小聚合，通过领域事件协作 |
| 跨聚合事务 | 分布式事务 + 锁竞争 | 使用最终一致性 + Saga |
| 聚合内引用其他聚合实体 | 越界操作，破坏封装 | 只持有 ID，不持有引用 |

来源：[Kinda Technical - Common Aggregate Design Mistakes](https://www.kindatechnical.com/domain-driven-design/lesson-44-common-aggregate-design-mistakes-and-how-to-fix-them.html)

### 7.5 2026 年 DDD 实践建议

1. **限界上下文优先于微服务拆分**：先画 Context Map，再决定服务边界，这比"按表分库"更贴近业务。
2. **Event Storming 是团队对齐的最高性价比工具**：一场 2 小时的工作坊往往比一周的需求评审更有效。
3. **通用语言要沉淀成代码词汇表**：类名、方法名、API 字段直接使用领域术语，供人和 LLM 共同消费。
4. **防腐层（ACL）在 AI 集成中同样适用**：对接外部 LLM 服务时，用 ACL 隔离 Prompt 格式和响应结构变化。
5. **限界上下文 = LLM 工作边界**：给 Coding Agent 提供单个上下文的代码和文档，生成质量显著高于全库投喂。

来源：[Understanding Data - DDD Bounded Contexts for LLMs](https://understandingdata.com/posts/ddd-bounded-contexts-for-llms/)

## 8. 2026-05 更新：DDD 与 LLM 编码的协同范式

> 🔄 更新于 2026-05-28

<!-- version-check: DDD bounded context for LLM code generation, DDD Europe 2026, checked 2026-05-28 -->

### 8.1 「为 LLM 代码生成而设计的限界上下文」

DDD 社区在 2026 年形成的新共识：限界上下文不仅是服务边界、团队边界，也是 **LLM 代码生成的「输入边界」**。`understandingdata.com` 等社区把这套实践总结为：

```
┌──── 限界上下文 × LLM 编码协同 ────┐
│                                    │
│  没有清晰边界：                      │
│  Prompt = 整个仓库 → token 爆炸 →   │
│           上下文混乱 → 生成质量差     │
│                                    │
│  有清晰边界：                        │
│  Prompt = 单个限界上下文 +           │
│           Ubiquitous Language 词典  │
│  → token 精准 → 生成贴合业务         │
└────────────────────────────────────┘
```

实践要点：
- 每个限界上下文配一个 `CONTEXT.md`，描述领域术语、聚合边界、对外契约
- LLM 提交 PR 时强制声明改动所属上下文，跨上下文改动必须经过领域事件或 API
- Context Map 直接喂给 Coding Agent，作为它的「世界模型」

来源：[Understanding Data - DDD Bounded Contexts for LLM Code Generation](https://understandingdata.com/posts/ddd-bounded-contexts-for-llms/)（内容已重写以符合许可）

### 8.2 DDD Europe 2026：Domains as LLM Consumers

DDD Europe 2026 议题 *The Curse of Unbounded Contexts: Using Domains as LLM Consumers* 引申出一个反向思考：**不是「把代码喂给 LLM」，而是「把领域作为 LLM 的消费者」**。具体含义：

| 视角 | 传统理解 | DDD-LLM 视角 |
| ---- | -------- | ------------ |
| LLM 角色 | 工具 / 助手 | 限界上下文里的「自动化角色」 |
| 上下文 | 输入数据 | 一种能力消费者，需要 ACL（防腐层）翻译 |
| 通用语言 | 团队共识 | 同时是 Prompt 词汇表，必须严格、稳定 |
| 失败模式 | LLM 幻觉 | 领域语言模糊导致的边界错位 |

**架构含义**：当 Agent 进入限界上下文，传统的 ACL（防腐层）模式被复用 —— Agent 暴露的「工具」就是上下文的对外契约，Agent 内部对模型/Prompt 的演化对上下文不可见。来源：[DDD Europe 2026 - The Curse of Unbounded Contexts](https://2026.dddeurope.com/program/the-curse-of-unbounded-contexts-using-domains-as-llm-consumers/)、[DDD Academy - Strategic Design with LLMs](https://ddd.academy/accelerate-your-strategic-design-with-llms)（内容已重写以符合许可）

### 8.3 把 DDD 工件作为 Coding Agent 的 Steering 文件

落地方式：

```
.kiro/steering/
├─ domain-glossary.md          # Ubiquitous Language 词典
├─ context-map.md              # Context Map + Relationship Patterns
└─ aggregate-rules.md          # 各聚合的不变量与一致性边界

.kiro/specs/{feature}/
├─ requirements.md             # 用 EARS 表达，词汇全部来自 glossary
└─ design.md                   # 引用具体限界上下文与聚合
```

效果：
- Coding Agent 生成的代码自然使用领域术语，命名一致性高
- 跨上下文改动会被显式拦截（防腐层 / API 契约）
- 新人 onboarding 和 Agent prompt 用同一份 steering，知识统一
