/**
 * x402 卖方服务（API 提供者）
 *
 * 这是一个普通的 Express API 服务，加了 x402 付费墙中间件。
 * 未付费的请求会收到 HTTP 402，付费后返回数据。
 *
 * 用法：npm run seller
 */

import express from "express";
import { paymentMiddleware, x402ResourceServer } from "@x402/express";
import { ExactEvmScheme } from "@x402/evm/exact/server";
import { HTTPFacilitatorClient } from "@x402/core/server";
import dotenv from "dotenv";

dotenv.config();

const app = express();
const PORT = process.env.PORT || 4402;

// 卖方收款地址（从 .env 读取）
const sellerAddress = process.env.SELLER_WALLET_ADDRESS;

if (!sellerAddress) {
  console.error("❌ 请先在 .env 中设置 SELLER_WALLET_ADDRESS");
  console.error("   运行 node setup-wallet.js 生成钱包");
  process.exit(1);
}

// Facilitator 地址（测试网用 x402.org 的免费服务）
const facilitatorUrl = "https://x402.org/facilitator";

// === 创建 x402 资源服务器 ===
const facilitatorClient = new HTTPFacilitatorClient({ url: facilitatorUrl });
const resourceServer = new x402ResourceServer(facilitatorClient)
  .register("eip155:84532", new ExactEvmScheme()); // Base Sepolia 测试网

// === 路由配置 ===
// 定义哪些路由需要付费，以及价格
const routes = {
  "GET /api/weather": {
    accepts: {
      scheme: "exact",
      price: "$0.001",              // 每次调用 $0.001 USDC
      network: "eip155:84532",      // Base Sepolia 测试网
      payTo: sellerAddress,         // 收款地址
    },
    description: "天气数据 API",
  },
};

// 应用 x402 付费墙中间件
app.use(paymentMiddleware(routes, resourceServer));

// === 付费 API 路由 ===
// 支付验证通过后，执行业务逻辑
app.get("/api/weather", (req, res) => {
  console.log("✅ 收到付费请求，返回天气数据");
  res.json({
    city: "上海",
    temperature: "26°C",
    weather: "晴天",
    humidity: "65%",
    wind: "东南风 3 级",
    timestamp: new Date().toISOString(),
    message: "🎉 你成功通过 x402 协议付费获取了这条数据！",
  });
});

// 免费路由（用于测试服务是否正常运行）
app.get("/", (req, res) => {
  res.json({
    service: "x402 Demo - 天气 API",
    status: "running",
    endpoints: {
      "/": "免费 - 服务状态（你现在看到的）",
      "/api/weather": "付费 - 天气数据（$0.001 USDC/次）",
    },
    network: "Base Sepolia（测试网）",
  });
});

app.listen(PORT, () => {
  console.log("");
  console.log("🏪 x402 卖方服务已启动");
  console.log(`   地址：http://localhost:${PORT}`);
  console.log(`   收款钱包：${sellerAddress}`);
  console.log(`   Facilitator：${facilitatorUrl}`);
  console.log("");
  console.log("📡 路由：");
  console.log(`   GET http://localhost:${PORT}/          → 免费（服务状态）`);
  console.log(`   GET http://localhost:${PORT}/api/weather → 付费（$0.001 USDC）`);
  console.log("");
  console.log("等待买方请求...");
});
