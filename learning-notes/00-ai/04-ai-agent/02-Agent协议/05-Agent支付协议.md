# Agent 支付协议
‍‍​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌​​​​​​​​​​​‌‌‌​‌​​​​​​​​​​​‌‌​​‌​‌​​​​​​​​​‌‌‌​​‌​​​​​​​​​​​‌​​​​​​​​​​​​​​‌​‌​‌‌‌​​​​​​​​​‌‌​​​​‌​​​​​​​​​‌‌​‌‌‌​​​​​​​​​​‌‌​​‌‌‌‍‍
> Author: Walter Wang

## 1. 概述

随着 AI Agent 从"对话助手"演进为"能执行任务的自主代理"，Agent 需要代替用户完成购买、支付、订阅等商业行为。2025 年，Agent 支付协议成为新兴领域，OpenAI、Google、Mastercard 等巨头纷纷入局。

```
┌─────────────── Agent 支付生态全景 ───────────────┐
│                                                    │
│  ┌──────┐    ┌──────────┐    ┌──────────┐         │
│  │ 用户  │ →  │ AI Agent │ →  │ 支付协议  │         │
│  │"帮我买"│    │ 代理执行  │    │ 安全结算  │         │
│  └──────┘    └──────────┘    └─────┬────┘         │
│                                     │              │
│              ┌──────────────────────┼──────┐       │
│              │                      │      │       │
│         ┌────┴────┐  ┌─────────┐  ┌┴─────┐       │
│         │ 商家/API │  │ 支付网络 │  │ 银行  │       │
│         │ Merchant │  │ Stripe  │  │ Bank  │       │
│         └─────────┘  │ PayPal  │  └──────┘       │
│                      │ Alipay  │                  │
│                      └─────────┘                  │
│                                                    │
│  四大协议：                                        │
│  ├─ ACP (OpenAI+Stripe) — 结账流程标准化           │
│  ├─ AP2 (Google)         — A2A 扩展，多支付方式    │
│  ├─ Mastercard Agent Pay — 代理令牌化支付          │
│  └─ x402               — HTTP 原生微支付           │
└────────────────────────────────────────────────────┘
```

## 2. Agent Commerce Protocol (ACP) — OpenAI + Stripe

2025 年 9 月发布，Apache 2.0 开源。为 Agent 提供标准化的结账流程。

```
核心设计：
├─ 4 个 RESTful 端点：Create / Update / Complete / Cancel
├─ 商家保持客户关系（Agent 不接触支付凭证）
├─ Stripe 集成（首选支付处理商）
├─ 驱动 ChatGPT 的 Instant Checkout 功能
└─ 开源协议，任何 Agent 平台可接入
```

### 支付流程架构

```
┌─────────── ACP 支付流程 ───────────┐
│                                     │
│  1. 用户: "帮我买一双 Nike 跑鞋"    │
│     ↓                               │
│  2. Agent 调用商家 API 搜索商品      │
│     ↓                               │
│  3. Agent → 商家: POST /checkout    │
│     (创建结账会话)                   │
│     ↓                               │
│  4. 商家返回: checkout_url +        │
│     商品详情 + 价格                  │
│     ↓                               │
│  5. Agent 展示给用户确认             │
│     "Nike Air Max, ¥899, 确认购买？"│
│     ↓                               │
│  6. 用户确认 → Agent 调用           │
│     POST /checkout/{id}/complete    │
│     ↓                               │
│  7. Stripe 处理支付                  │
│     ↓                               │
│  8. 商家确认订单，返回订单号         │
│                                     │
│  关键：Agent 不接触信用卡信息        │
│  支付在 Stripe 安全环境中完成        │
└─────────────────────────────────────┘
```

### 代码示例：商家接入 ACP

```python
"""商家端：接入 ACP 协议，支持 Agent 结账"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import stripe
import uuid

app = FastAPI()
stripe.api_key = "sk_xxx"

# ─── 数据模型 ───
class CreateCheckoutRequest(BaseModel):
    items: list[dict]          # [{"product_id": "xxx", "quantity": 1}]
    customer_context: dict     # Agent 传递的用户上下文
    agent_id: str              # 发起请求的 Agent 标识

class CheckoutSession(BaseModel):
    checkout_id: str
    status: str                # pending | completed | cancelled
    items: list[dict]
    total_amount: int          # 分为单位
    currency: str
    checkout_url: str          # Stripe 支付页面
    expires_at: str

# 内存存储（生产环境用数据库）
sessions: dict[str, dict] = {}

# ─── ACP 端点 1: 创建结账 ───
@app.post("/acp/v1/checkout")
async def create_checkout(req: CreateCheckoutRequest) -> CheckoutSession:
    """Agent 调用：创建结账会话"""
    # 查询商品信息
    items_with_price = []
    total = 0
    for item in req.items:
        product = get_product(item["product_id"])  # 查数据库
        price = product["price"] * item["quantity"]
        total += price
        items_with_price.append({
            "product_id": item["product_id"],
            "name": product["name"],
            "price": product["price"],
            "quantity": item["quantity"],
            "image_url": product["image_url"],
        })

    # 创建 Stripe Checkout Session
    stripe_session = stripe.checkout.Session.create(
        payment_method_types=["card", "alipay", "wechat_pay"],
        line_items=[{
            "price_data": {
                "currency": "cny",
                "product_data": {"name": item["name"]},
                "unit_amount": item["price"],
            },
            "quantity": item["quantity"],
        } for item in items_with_price],
        mode="payment",
        success_url="https://myshop.com/success?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="https://myshop.com/cancel",
        metadata={"agent_id": req.agent_id},
    )

    checkout_id = str(uuid.uuid4())
    session_data = {
        "checkout_id": checkout_id,
        "stripe_session_id": stripe_session.id,
        "status": "pending",
        "items": items_with_price,
        "total_amount": total,
        "currency": "cny",
        "checkout_url": stripe_session.url,
    }
    sessions[checkout_id] = session_data

    return CheckoutSession(**session_data, expires_at="2025-08-15T12:00:00Z")

# ─── ACP 端点 2: 更新结账 ───
@app.put("/acp/v1/checkout/{checkout_id}")
async def update_checkout(checkout_id: str, updates: dict):
    """Agent 调用：更新结账信息（修改数量、地址等）"""
    if checkout_id not in sessions:
        raise HTTPException(404, "Checkout not found")
    sessions[checkout_id].update(updates)
    return sessions[checkout_id]

# ─── ACP 端点 3: 完成结账 ───
@app.post("/acp/v1/checkout/{checkout_id}/complete")
async def complete_checkout(checkout_id: str):
    """Agent 调用：用户确认后完成支付"""
    session = sessions.get(checkout_id)
    if not session:
        raise HTTPException(404, "Checkout not found")

    # 检查 Stripe 支付状态
    stripe_session = stripe.checkout.Session.retrieve(session["stripe_session_id"])
    if stripe_session.payment_status == "paid":
        session["status"] = "completed"
        order_id = create_order(session)  # 创建订单
        return {"status": "completed", "order_id": order_id}
    return {"status": "payment_pending", "checkout_url": session["checkout_url"]}

# ─── ACP 端点 4: 取消结账 ───
@app.delete("/acp/v1/checkout/{checkout_id}")
async def cancel_checkout(checkout_id: str):
    """Agent 调用：取消结账"""
    if checkout_id in sessions:
        sessions[checkout_id]["status"] = "cancelled"
    return {"status": "cancelled"}
```

### Agent 端调用 ACP

```python
"""Agent 端：调用商家 ACP 接口完成购买"""

import httpx

async def agent_purchase(user_request: str):
    """Agent 代理用户完成购买"""
    async with httpx.AsyncClient() as client:
        # 1. 创建结账
        resp = await client.post(
            "https://merchant.com/acp/v1/checkout",
            json={
                "items": [{"product_id": "nike-air-max-001", "quantity": 1}],
                "customer_context": {"user_id": "user-123"},
                "agent_id": "chatgpt-agent-456",
            }
        )
        checkout = resp.json()

        # 2. 展示给用户确认
        confirmation = await ask_user(
            f"找到商品：{checkout['items'][0]['name']}\n"
            f"价格：¥{checkout['total_amount'] / 100}\n"
            f"确认购买吗？"
        )

        if confirmation:
            # 3. 引导用户完成支付（打开 Stripe 页面）
            await show_payment_link(checkout["checkout_url"])

            # 4. 支付完成后确认
            result = await client.post(
                f"https://merchant.com/acp/v1/checkout/{checkout['checkout_id']}/complete"
            )
            return result.json()
        else:
            # 取消
            await client.delete(
                f"https://merchant.com/acp/v1/checkout/{checkout['checkout_id']}"
            )
            return {"status": "cancelled"}
```

## 3. Agent Payments Protocol (AP2) — Google

Google 联合 60+ 合作伙伴（PayPal、Mastercard、Amex、Adyen、Alipay）推出，作为 A2A 协议的支付扩展。

```
核心特性：
├─ A2A 扩展：基于 Agent-to-Agent 协议
├─ 多支付方式：信用卡/借记卡、稳定币、实时银行转账
├─ 加密验证：可验证凭证（Verifiable Credentials）
├─ DID 身份：去中心化标识符，Agent 身份认证
├─ 60+ 合作伙伴：PayPal, Mastercard, Amex, Adyen, Alipay, Stripe
└─ 开放标准：任何 Agent 框架可接入
```

### AP2 架构

```
┌─────────── AP2 支付架构 ───────────┐
│                                     │
│  ┌──────────┐    A2A 协议           │
│  │ 买方 Agent│ ←──────────→         │
│  │ (用户侧)  │              ┌──────┐│
│  └─────┬────┘              │卖方   ││
│        │                   │Agent  ││
│  ┌─────┴────┐              └──┬───┘│
│  │ DID 身份  │                 │     │
│  │ 验证凭证  │                 │     │
│  └─────┬────┘              ┌──┴───┐│
│        │                   │支付   ││
│  ┌─────┴────────────┐     │处理商 ││
│  │ 支付方式选择       │     │PayPal││
│  │ ├─ 信用卡/借记卡  │     │Stripe││
│  │ ├─ PayPal        │     │Adyen ││
│  │ ├─ 稳定币 (USDC) │     └──────┘│
│  │ ├─ 银行转账      │              │
│  │ └─ Alipay/微信   │              │
│  └──────────────────┘              │
│                                     │
│  DID 身份验证流程：                  │
│  Agent → 出示 DID → 验证凭证 →     │
│  支付授权 → 交易完成                 │
└─────────────────────────────────────┘
```

### AP2 与 A2A 集成示例

```python
"""AP2 支付流程（概念示例）"""

# Agent Card 中声明支付能力
agent_card = {
    "name": "ShopAgent",
    "description": "电商购物 Agent",
    "capabilities": {
        "payment": {
            "protocol": "ap2",
            "supported_methods": ["card", "paypal", "alipay", "usdc"],
            "currencies": ["USD", "CNY", "EUR"],
        }
    },
    "authentication": {
        "type": "did",
        "did": "did:web:shop-agent.example.com",
        "verifiable_credentials": ["payment_processor", "merchant"],
    }
}

# 支付请求（通过 A2A Task）
payment_task = {
    "type": "payment_request",
    "amount": {
        "value": "89.99",
        "currency": "USD",
    },
    "merchant": {
        "did": "did:web:merchant.example.com",
        "name": "Example Store",
    },
    "items": [
        {"name": "Wireless Headphones", "quantity": 1, "price": "89.99"}
    ],
    "payment_methods": ["card", "paypal"],  # 可选支付方式
    "verification": {
        "type": "verifiable_credential",
        "credential": "eyJhbGciOiJFZDI1NTE5...",  # JWT 格式凭证
    }
}
```

## 4. Mastercard Agent Pay

Mastercard 推出的 Agent 专用令牌化支付方案，已与 Citi、US Bank 上线。

```
核心特性：
├─ Agentic Tokens：不同于普通卡令牌的 Agent 专用令牌
│   ├─ 绑定特定 Agent（不可跨 Agent 使用）
│   ├─ 可设置消费限额和有效期
│   ├─ 可随时撤销
│   └─ 交易可追溯到具体 Agent
├─ 已上线：Citi Bank, US Bank
├─ 集成：ChatGPT, Microsoft Copilot
└─ 安全：Agent 不接触真实卡号
```

```
┌─────── Mastercard Agent Pay 流程 ───────┐
│                                          │
│  1. 用户在银行 App 中授权                 │
│     "允许 ChatGPT 使用我的 Mastercard"   │
│     ↓                                    │
│  2. 银行生成 Agentic Token               │
│     (绑定 Agent ID + 消费限额)           │
│     ↓                                    │
│  3. Token 存储在 Agent 安全环境           │
│     ↓                                    │
│  4. Agent 购物时使用 Token 支付           │
│     (商家只看到 Token，不看到真实卡号)    │
│     ↓                                    │
│  5. Mastercard 网络验证 Token             │
│     检查：Agent ID 匹配？限额内？有效期？ │
│     ↓                                    │
│  6. 交易完成，用户收到通知               │
│                                          │
│  与普通令牌的区别：                       │
│  普通令牌：绑定设备/商家                  │
│  Agent 令牌：绑定 Agent + 限额 + 可撤销  │
└──────────────────────────────────────────┘
```

## 5. x402 协议 — HTTP 原生微支付

基于 HTTP 402 状态码的微支付协议，专为 Agent 间自动支付设计。

```
核心特性：
├─ HTTP 原生：利用 402 Payment Required 状态码
├─ 微支付：适合小额 Agent 间交易（API 调用计费）
├─ 加密货币：基于稳定币（USDC）支付
├─ 无需注册：Agent 自动完成支付
└─ 去中心化：无中心化支付处理商
```

### x402 工作流程

```
┌─────────── x402 支付流程 ───────────┐
│                                      │
│  Agent A                  Agent B    │
│  (调用方)                 (服务方)    │
│                                      │
│  1. GET /api/data                    │
│     ↓                                │
│  2. 402 Payment Required             │
│     Headers:                         │
│       X-Payment-Amount: 0.001        │
│       X-Payment-Currency: USDC       │
│       X-Payment-Address: 0xABC...    │
│       X-Payment-Network: base        │
│     ↓                                │
│  3. Agent A 自动发起链上支付          │
│     USDC 转账: 0.001 → 0xABC...     │
│     ↓                                │
│  4. GET /api/data                    │
│     Headers:                         │
│       X-Payment-Proof: 0xTxHash...   │
│     ↓                                │
│  5. 200 OK + 数据返回                │
│                                      │
│  整个过程自动完成，无需人工干预        │
└──────────────────────────────────────┘
```

```python
"""x402 协议 — Agent 自动微支付示例"""

import httpx
from web3 import Web3

class X402PaymentAgent:
    """支持 x402 自动支付的 HTTP 客户端"""

    def __init__(self, wallet_private_key: str):
        self.w3 = Web3(Web3.HTTPProvider("https://mainnet.base.org"))
        self.wallet = self.w3.eth.account.from_key(wallet_private_key)
        self.usdc_contract = self.w3.eth.contract(
            address="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # Base USDC
            abi=USDC_ABI,
        )

    async def request_with_payment(self, url: str) -> dict:
        """发起请求，遇到 402 自动支付"""
        async with httpx.AsyncClient() as client:
            # 第一次请求
            resp = await client.get(url)

            if resp.status_code == 402:
                # 解析支付要求
                amount = float(resp.headers["X-Payment-Amount"])
                address = resp.headers["X-Payment-Address"]
                currency = resp.headers["X-Payment-Currency"]

                print(f"💰 需要支付: {amount} {currency} → {address}")

                # 执行链上支付
                tx_hash = await self._pay_usdc(address, amount)

                # 带支付证明重新请求
                resp = await client.get(url, headers={
                    "X-Payment-Proof": tx_hash,
                })

            return resp.json()

    async def _pay_usdc(self, to_address: str, amount: float) -> str:
        """发送 USDC 支付"""
        amount_wei = int(amount * 10**6)  # USDC 6 位小数
        tx = self.usdc_contract.functions.transfer(
            to_address, amount_wei
        ).build_transaction({
            "from": self.wallet.address,
            "nonce": self.w3.eth.get_transaction_count(self.wallet.address),
        })
        signed = self.w3.eth.account.sign_transaction(tx, self.wallet.key)
        tx_hash = self.w3.eth.send_raw_transaction(signed.raw_transaction)
        return tx_hash.hex()
```

## 6. 协议对比表

| 特性 | ACP (OpenAI+Stripe) | AP2 (Google) | Mastercard Agent Pay | x402 |
|------|---------------------|--------------|---------------------|------|
| 发起方 | OpenAI + Stripe | Google + 60 伙伴 | Mastercard | 社区 |
| 合作伙伴 | Stripe 生态 | PayPal, Amex, Adyen, Alipay | Citi, US Bank | 加密社区 |
| 支付方式 | 信用卡/Alipay/微信 | 卡/PayPal/稳定币/银行转账 | Mastercard 卡 | 稳定币 (USDC) |
| 开源 | ✅ Apache 2.0 | 开放标准 | ❌ 专有 | ✅ 开源 |
| 状态 | 已上线 (ChatGPT) | 已发布 | 已上线 (Citi/US Bank) | 早期 |
| 身份验证 | Agent ID | DID + 可验证凭证 | Agentic Token | 钱包地址 |
| 最佳场景 | 电商结账 | 跨平台 Agent 支付 | 银行卡 Agent 支付 | Agent 间微支付 |
| 用户确认 | ✅ 必须确认 | ✅ 可配置 | ✅ 银行授权 | ❌ 自动支付 |
| 金额范围 | 任意 | 任意 | 有限额 | 微支付为主 |
| 地域 | 全球 (Stripe 覆盖) | 全球 | 美国为主 | 全球 (链上) |

## 7. 安全考量

```
Agent 支付安全要点：
│
├─ 身份验证
│   ├─ Agent 身份：谁在发起支付？
│   │   ├─ ACP: Agent ID 绑定
│   │   ├─ AP2: DID 去中心化身份
│   │   └─ Mastercard: Agentic Token
│   └─ 用户授权：用户是否同意？
│       ├─ 明确确认（ACP 要求用户点击确认）
│       ├─ 预授权（Mastercard 预设限额）
│       └─ 自动授权（x402 钱包自动支付）
│
├─ 交易安全
│   ├─ Agent 不接触真实支付凭证（ACP/Mastercard）
│   ├─ 加密传输（TLS/HTTPS）
│   ├─ 交易签名（AP2 可验证凭证）
│   └─ 链上不可篡改（x402）
│
├─ 风控措施
│   ├─ 单笔限额
│   ├─ 日/月累计限额
│   ├─ 异常交易检测
│   ├─ 地域限制
│   └─ 商家白名单
│
└─ 可撤销性
    ├─ ACP: 可取消未完成的结账
    ├─ Mastercard: 可随时撤销 Token
    ├─ AP2: 支持退款流程
    └─ x402: 链上交易不可逆（需注意）
```

## 8. 为什么 Agent 需要"钱包"

```
┌─────────── Agent 钱包的未来 ───────────┐
│                                         │
│  当前：Agent 代理用户支付                │
│  ┌──────┐  授权  ┌──────┐  支付        │
│  │ 用户  │ ────→ │ Agent │ ────→ 商家   │
│  │ 钱包  │       │ 代理  │              │
│  └──────┘       └──────┘              │
│                                         │
│  未来：Agent 拥有自己的钱包              │
│  ┌──────┐  充值  ┌──────────┐          │
│  │ 用户  │ ────→ │ Agent 钱包│          │
│  └──────┘       │ (预算制)  │          │
│                  └─────┬────┘          │
│                        │ 自主支付       │
│              ┌─────────┼─────────┐     │
│              ↓         ↓         ↓     │
│           API 调用   购买商品   订阅服务 │
│                                         │
│  Agent 钱包需要：                        │
│  ├─ 预算控制（每日/每月上限）            │
│  ├─ 审计日志（每笔交易可追溯）           │
│  ├─ 授权范围（只能买特定类别）           │
│  ├─ 紧急冻结（用户随时停止）             │
│  └─ 多签机制（大额需多方确认）           │
└─────────────────────────────────────────┘
```

## 9. 选型建议

```
你的场景是什么？
│
├─ 电商/零售 Agent 购物
│   └─ ACP (OpenAI+Stripe) — 最成熟，Stripe 生态
│
├─ 跨平台 Agent 协作支付
│   └─ AP2 (Google) — A2A 集成，多支付方式
│
├─ 银行/金融 Agent
│   └─ Mastercard Agent Pay — 合规，银行集成
│
├─ Agent 间 API 调用计费
│   └─ x402 — HTTP 原生，自动微支付
│
├─ 中国市场
│   ├─ ACP + Alipay/微信支付
│   └─ AP2 (Alipay 是合作伙伴)
│
└─ 不确定？
    └─ 先用 ACP（最简单，Stripe 全球覆盖）
```

## 10. 相关文档

- Agent 协议全景 → `Agent协议全景图.md`（本目录，协议关系图）
- A2A 协议 → `A2A Agent间通信协议.md`（AP2 的基础协议）
- Agent 安全 → `15-Agent安全与治理/01-Agent身份与权限.md`
- Agent 治理 → `15-Agent安全与治理/02-Agent治理框架.md`
- MCP 协议 → `MCP模型上下文协议.md`（工具调用基础）
- Agent 支付深度学习 → `20-Agent支付/`（支付基础、术语字典、行业全景、AgentToken 产品分析）
## 🎬 推荐视频资源

### 🌐 YouTube
- [a16z - AI Agent Payments](https://www.youtube.com/watch?v=JhCl-GeT4jw) — AI Agent支付未来趋势
- [Stripe - AI Payment Integration](https://www.youtube.com/watch?v=F8NKVhkZZWI) — AI支付集成方案
