# x402 协议最小可运行 Demo

这个 Demo 演示了 x402 协议的完整支付流程：Agent（买方）调用付费 API（卖方），自动完成签名支付。

## 前置知识

如果你不熟悉区块链，先阅读：
- `../learning-notes/ai-agent/20-Agent支付/00-X402开发者区块链最小知识.md`

## 架构

```text
买方 Agent (buyer.js)          卖方 API (seller.js)         Facilitator (x402.org)
     │                              │                            │
     │  GET /api/weather            │                            │
     │ ───────────────────────────→ │                            │
     │                              │                            │
     │  HTTP 402 + 支付要求          │                            │
     │ ←─────────────────────────── │                            │
     │                              │                            │
     │  签名支付（本地，免费）        │                            │
     │                              │                            │
     │  GET /api/weather + 签名      │                            │
     │ ───────────────────────────→ │  验证签名 + 链上结算         │
     │                              │ ─────────────────────────→ │
     │                              │                            │
     │                              │  结算成功                   │
     │                              │ ←───────────────────────── │
     │  HTTP 200 + 天气数据          │                            │
     │ ←─────────────────────────── │                            │
```

## 快速开始

### 1. 安装依赖

```bash
cd x402-demo
npm install
```

### 2. 生成测试钱包

```bash
npm run setup
```

这会生成两个钱包（买方 + 卖方），按提示把信息填入 `.env` 文件。

### 3. 获取测试 USDC

访问 [Circle Faucet](https://faucet.circle.com)：
- 选择 **Base Sepolia** 网络
- 输入买方钱包地址
- 领取测试 USDC（免费）

### 4. 启动卖方服务

```bash
npm run seller
```

### 5. 运行买方 Agent（新开一个终端）

```bash
npm run buyer
```

你会看到完整的 x402 支付流程：
1. 买方发请求 → 收到 HTTP 402
2. 买方自动签名支付
3. 买方带签名重新请求 → 收到天气数据 🎉

## 文件说明

| 文件 | 说明 |
|------|------|
| `setup-wallet.js` | 生成测试钱包的工具脚本 |
| `seller.js` | 卖方服务：Express + x402 付费墙中间件（使用 `@x402/express`） |
| `buyer.js` | 买方 Agent：使用 `@x402/fetch` 自动处理 402 支付的客户端 |
| `.env.example` | 环境变量模板 |

## 使用的网络和服务

| 项目 | 值 | 说明 |
|------|-----|------|
| 区块链网络 | Base Sepolia | 测试网，免费 |
| 网络标识 | eip155:84532 | x402 v2 协议使用的 CAIP-2 格式 |
| 支付代币 | 测试 USDC | 从 Circle Faucet 免费获取 |
| Facilitator | x402.org | 免费测试网 Facilitator |
| 每次调用价格 | $0.001 USDC | 测试用，不花真钱 |

## 常见问题

**Q: 买方报 "insufficient" 错误？**
A: 买方钱包没有测试 USDC。去 https://faucet.circle.com 领取。

**Q: 卖方启动报 "SELLER_WALLET_ADDRESS" 错误？**
A: 先运行 `npm run setup` 生成钱包，再把地址填入 `.env`。

**Q: 想改价格怎么办？**
A: 修改 `seller.js` 中 `price` 的值，如 `"$0.01"` 表示每次调用 $0.01 USDC。
