"""
钱包生成脚本

运行这个脚本会生成两个测试钱包（买方 + 卖方），
并输出你需要填入 .env 的配置。

用法：python setup_wallet.py
"""

from eth_account import Account

print("=== x402 Python Demo 钱包生成工具 ===\n")

# 生成买方钱包（Agent，需要私钥来签名支付）
buyer = Account.create()
# 生成卖方钱包（API 提供者，只需要地址来收款）
seller = Account.create()

print("📦 买方钱包（Agent）：")
print(f"   地址：{buyer.address}")
print(f"   私钥：{buyer.key.hex()}")
print()

print("🏪 卖方钱包（API 服务）：")
print(f"   地址：{seller.address}")
print(f"   私钥：{seller.key.hex()}（卖方不需要用到私钥，但留着备用）")
print()

print("=== 接下来你需要做的 ===\n")

print("1️⃣  复制 .env.example 为 .env，填入以下内容：")
print(f"   SELLER_WALLET_ADDRESS={seller.address}")
print(f"   BUYER_PRIVATE_KEY={buyer.key.hex()}")
print()

print("2️⃣  去 Circle Faucet 给买方钱包充测试 USDC：")
print("   https://faucet.circle.com")
print(f"   选择 Base Sepolia 网络，输入买方地址：{buyer.address}")
print()

print("3️⃣  启动卖方服务：python seller.py")
print("4️⃣  运行买方脚本：python buyer.py")
