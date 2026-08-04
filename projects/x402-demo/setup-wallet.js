/**
 * 钱包生成脚本
 *
 * 运行这个脚本会生成两个测试钱包（买方 + 卖方），
 * 并输出你需要填入 .env 的配置。
 *
 * 用法：node setup-wallet.js
 */

import { generatePrivateKey, privateKeyToAccount } from "viem/accounts";

console.log("=== x402 Demo 钱包生成工具 ===\n");

// 生成买方钱包（Agent，需要私钥来签名支付）
const buyerPrivateKey = generatePrivateKey();
const buyerAccount = privateKeyToAccount(buyerPrivateKey);

// 生成卖方钱包（API 提供者，只需要地址来收款）
const sellerPrivateKey = generatePrivateKey();
const sellerAccount = privateKeyToAccount(sellerPrivateKey);

console.log("📦 买方钱包（Agent）：");
console.log(`   地址：${buyerAccount.address}`);
console.log(`   私钥：${buyerPrivateKey}`);
console.log("");

console.log("🏪 卖方钱包（API 服务）：");
console.log(`   地址：${sellerAccount.address}`);
console.log(`   私钥：${sellerPrivateKey}（卖方不需要用到私钥，但留着备用）`);
console.log("");

console.log("=== 接下来你需要做的 ===\n");

console.log("1️⃣  复制 .env.example 为 .env，填入以下内容：");
console.log(`   SELLER_WALLET_ADDRESS=${sellerAccount.address}`);
console.log(`   BUYER_PRIVATE_KEY=${buyerPrivateKey}`);
console.log("");

console.log("2️⃣  去 Circle Faucet 给买方钱包充测试 USDC：");
console.log("   https://faucet.circle.com");
console.log(`   选择 Base Sepolia 网络，输入买方地址：${buyerAccount.address}`);
console.log("");

console.log("3️⃣  启动卖方服务：npm run seller");
console.log("4️⃣  运行买方脚本：npm run buyer");
