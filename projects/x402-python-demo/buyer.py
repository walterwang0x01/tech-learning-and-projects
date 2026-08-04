"""
x402 买方 Agent（API 调用方）- Python 版

这个脚本模拟一个 AI Agent 调用付费 API 的过程：
1. 发请求 → 收到 402
2. 自动用钱包签名支付
3. 带签名重新请求 → 拿到数据

用法：python buyer.py（确保卖方服务已启动）
"""

import asyncio
import os

import httpx
from dotenv import load_dotenv
from eth_account import Account

from x402 import x402Client
from x402.http import x402HTTPClient
from x402.http.clients import x402HttpxClient
from x402.mechanisms.evm import EthAccountSigner
from x402.mechanisms.evm.exact.register import register_exact_evm_client

# 加载环境变量
load_dotenv()

# === 配置 ===
PORT = os.getenv("PORT", "4402")
SELLER_URL = f"http://localhost:{PORT}/api/weather"
BUYER_PRIVATE_KEY = os.getenv("BUYER_PRIVATE_KEY")

if not BUYER_PRIVATE_KEY:
    print("❌ 请先在 .env 中设置 BUYER_PRIVATE_KEY")
    print("   运行 python setup_wallet.py 生成钱包")
    exit(1)


async def main():
    # === 创建钱包账户 ===
    account = Account.from_key(BUYER_PRIVATE_KEY)

    print()
    print("🤖 x402 买方 Agent 启动（Python 版）")
    print(f"   钱包地址：{account.address}")
    print(f"   目标 API：{SELLER_URL}")
    print()

    # === 第一步：先用普通 httpx 看看会收到什么 ===
    print("📡 第一步：发送普通请求（不带支付）...")
    async with httpx.AsyncClient() as plain_client:
        first_response = await plain_client.get(SELLER_URL)
        print(f"   响应状态：{first_response.status_code}")

    if first_response.status_code == 402:
        print("   💰 收到 HTTP 402 - 需要付费！")

        # 打印支付要求
        payment_header = first_response.headers.get("payment-required")
        if payment_header:
            import base64
            import json

            try:
                payment_info = json.loads(base64.b64decode(payment_header))
                accepts = payment_info.get("accepts", [{}])
                if accepts:
                    opt = accepts[0]
                    amount = int(opt.get("amount", 0))
                    print("   支付要求：")
                    print(f"     金额：{amount} 最小单位")
                    print(f"     折合：{amount / 1_000_000} USDC")
                    print(f"     收款地址：{opt.get('payTo', '未知')}")
                    print(f"     网络：{opt.get('network', '未知')}")
            except Exception:
                print(f"   支付信息：{payment_header[:100]}...")
        print()

        # === 第二步：使用 x402 客户端自动处理支付 ===
        print("🔐 第二步：使用 x402 自动支付并重新请求...")
        print("   （Agent 自动完成：解析 402 → 签名 → 重新请求）")
        print()

        # 创建 x402 客户端，注册 EVM 支付方案
        client = x402Client()
        signer = EthAccountSigner(account)
        register_exact_evm_client(client, signer)

        # 创建 HTTP 客户端辅助工具（用于提取支付响应）
        http_client = x402HTTPClient(client)

        try:
            # x402HttpxClient 会自动处理 402 响应：
            # 1. 发送请求 → 收到 402
            # 2. 解析支付要求
            # 3. 用钱包签名 EIP-712 支付授权
            # 4. 带签名重新请求
            async with x402HttpxClient(client) as http:
                paid_response = await http.get(SELLER_URL)
                await paid_response.aread()

                if paid_response.is_success:
                    data = paid_response.json()
                    print("✅ 第三步：支付成功，收到数据！")
                    print()
                    print("📊 天气数据：")
                    print(f"   城市：{data['city']}")
                    print(f"   温度：{data['temperature']}")
                    print(f"   天气：{data['weather']}")
                    print(f"   湿度：{data['humidity']}")
                    print(f"   风力：{data['wind']}")
                    print(f"   时间：{data['timestamp']}")
                    print()
                    print(f"   {data['message']}")

                    # 提取支付结算信息
                    try:
                        settle_response = http_client.get_payment_settle_response(
                            lambda name: paid_response.headers.get(name)
                        )
                        print()
                        print(f"   💳 结算信息：{settle_response.model_dump_json(indent=2)}")
                    except ValueError:
                        pass
                else:
                    print(f"❌ 支付后请求失败：{paid_response.status_code}")
                    print(f"   错误信息：{paid_response.text}")

        except Exception as error:
            print("❌ 支付过程出错：")
            print(f"   {error}")
            print()

            error_msg = str(error)
            if "insufficient" in error_msg.lower():
                print("💡 可能原因：买方钱包 USDC 余额不足")
                print("   解决：去 https://faucet.circle.com 领取测试 USDC")
                print(f"   买方地址：{account.address}")

    elif first_response.status_code == 200:
        data = first_response.json()
        print("   ⚠️ 请求直接成功了（没有触发 402），数据：")
        print(data)
    else:
        print(f"   ❌ 意外的响应状态：{first_response.status_code}")

    print()
    print("=== Demo 结束 ===")


if __name__ == "__main__":
    asyncio.run(main())
