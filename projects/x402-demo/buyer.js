/**
 * x402 买方 Agent（API 调用方）
 *
 * 这个脚本模拟一个 AI Agent 调用付费 API 的过程：
 * 1. 发请求 → 收到 402
 * 2. 自动用钱包签名支付
 * 3. 带签名重新请求 → 拿到数据
 *
 * 用法：npm run buyer（确保卖方服务已启动）
 */

import { wrapFetchWithPaymentFromConfig } from "@x402/fetch";
import { ExactEvmScheme } from "@x402/evm";
import { privateKeyToAccount } from "viem/accounts";
import dotenv from "dotenv";

dotenv.config();

// === 配置 ===
const SELLER_URL = `http://localhost:${process.env.PORT || 4402}/api/weather`;
const BUYER_PRIVATE_KEY = process.env.BUYER_PRIVATE_KEY;

if (!BUYER_PRIVATE_KEY) {
  console.error("❌ 请先在 .env 中设置 BUYER_PRIVATE_KEY");
  console.error("   运行 node setup-wallet.js 生成钱包");
  process.exit(1);
}

// === 创建钱包账户 ===
// 用买方的私钥创建一个账户，用于签名支付
const account = privateKeyToAccount(BUYER_PRIVATE_KEY);

// === 创建带支付功能的 fetch ===
// wrapFetchWithPaymentFromConfig 会自动处理 402 响应：
// 1. 发送请求 → 收到 402
// 2. 解析支付要求
// 3. 用钱包签名 EIP-712 支付授权
// 4. 带签名重新请求
const fetchWithPayment = wrapFetchWithPaymentFromConfig(fetch, {
  schemes: [
    {
      network: "eip155:84532",  // Base Sepolia 测试网
      client: new ExactEvmScheme(account),
    },
  ],
});

async function main() {
  console.log("");
  console.log("🤖 x402 买方 Agent 启动");
  console.log(`   钱包地址：${account.address}`);
  console.log(`   目标 API：${SELLER_URL}`);
  console.log("");

  // === 第一步：先用普通 fetch 看看会收到什么 ===
  console.log("📡 第一步：发送普通请求（不带支付）...");
  const firstResponse = await fetch(SELLER_URL);
  console.log(`   响应状态：${firstResponse.status}`);

  if (firstResponse.status === 402) {
    console.log("   💰 收到 HTTP 402 - 需要付费！");

    // 打印支付要求
    const paymentHeader = firstResponse.headers.get("x-payment");
    if (paymentHeader) {
      try {
        const paymentInfo = JSON.parse(paymentHeader);
        console.log("   支付要求：");
        console.log(`     价格：${paymentInfo.accepts?.[0]?.price || paymentInfo.maxAmountRequired || "未知"}`);
        console.log(`     收款地址：${paymentInfo.accepts?.[0]?.payTo || paymentInfo.payTo || "未知"}`);
        console.log(`     网络：${paymentInfo.accepts?.[0]?.network || paymentInfo.network || "未知"}`);
      } catch {
        console.log(`   支付信息：${paymentHeader.substring(0, 200)}...`);
      }
    }
    console.log("");

    // === 第二步：使用带支付功能的 fetch 自动处理 ===
    console.log("🔐 第二步：使用 x402 自动支付并重新请求...");
    console.log("   （Agent 自动完成：解析 402 → 签名 → 重新请求）");
    console.log("");

    try {
      const paidResponse = await fetchWithPayment(SELLER_URL, {
        method: "GET",
      });

      if (paidResponse.ok) {
        const data = await paidResponse.json();
        console.log("✅ 第三步：支付成功，收到数据！");
        console.log("");
        console.log("📊 天气数据：");
        console.log(`   城市：${data.city}`);
        console.log(`   温度：${data.temperature}`);
        console.log(`   天气：${data.weather}`);
        console.log(`   湿度：${data.humidity}`);
        console.log(`   风力：${data.wind}`);
        console.log(`   时间：${data.timestamp}`);
        console.log("");
        console.log(`   ${data.message}`);
      } else {
        console.error(`❌ 支付后请求失败：${paidResponse.status}`);
        const errorText = await paidResponse.text();
        console.error(`   错误信息：${errorText}`);
      }
    } catch (error) {
      console.error("❌ 支付过程出错：");
      console.error(`   ${error.message}`);
      console.error("");

      // 常见错误提示
      if (error.message.includes("insufficient")) {
        console.error("💡 可能原因：买方钱包 USDC 余额不足");
        console.error("   解决：去 https://faucet.circle.com 领取测试 USDC");
        console.error(`   买方地址：${account.address}`);
      }
    }
  } else if (firstResponse.ok) {
    const data = await firstResponse.json();
    console.log("   ⚠️ 请求直接成功了（没有触发 402），数据：");
    console.log(data);
  } else {
    console.error(`   ❌ 意外的响应状态：${firstResponse.status}`);
  }

  console.log("");
  console.log("=== Demo 结束 ===");
}

main().catch(console.error);
