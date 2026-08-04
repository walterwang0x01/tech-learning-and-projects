"""
x402 卖方服务（API 提供者）- Python 版

这是一个 FastAPI 服务，加了 x402 付费墙中间件。
未付费的请求会收到 HTTP 402，付费后返回数据。

用法：python seller.py
"""

import os
from datetime import datetime, timezone

from dotenv import load_dotenv
from fastapi import FastAPI

from x402 import x402ResourceServer
from x402.http import HTTPFacilitatorClient
from x402.http.middleware.fastapi import payment_middleware
from x402.mechanisms.evm.exact.register import register_exact_evm_server

# 加载环境变量
load_dotenv()

# 卖方收款地址（从 .env 读取）
seller_address = os.getenv("SELLER_WALLET_ADDRESS")
PORT = int(os.getenv("PORT", "4402"))

if not seller_address:
    print("❌ 请先在 .env 中设置 SELLER_WALLET_ADDRESS")
    print("   运行 python setup_wallet.py 生成钱包")
    exit(1)

# Facilitator 地址（测试网用 x402.org 的免费服务）
facilitator_url = "https://x402.org/facilitator"

app = FastAPI(title="x402 Python Demo - 天气 API")

# === 创建 x402 资源服务器 ===
facilitator = HTTPFacilitatorClient({"url": facilitator_url})
server = x402ResourceServer(facilitator)
register_exact_evm_server(server)  # 注册 EVM 支付方案

# === 路由配置 ===
routes = {
    "GET /api/weather": {
        "accepts": {
            "scheme": "exact",
            "price": "$0.001",
            "network": "eip155:84532",  # Base Sepolia 测试网
            "payTo": seller_address,
        },
        "description": "天气数据 API",
    },
}

# 应用 x402 付费墙中间件
app.middleware("http")(payment_middleware(routes, server))


# === 付费 API 路由 ===
@app.get("/api/weather")
async def get_weather():
    """天气数据 - 需要付费"""
    print("✅ 收到付费请求，返回天气数据")
    return {
        "city": "上海",
        "temperature": "26°C",
        "weather": "晴天",
        "humidity": "65%",
        "wind": "东南风 3 级",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "message": "🎉 你成功通过 x402 协议付费获取了这条数据！（Python 版）",
    }


# === 免费路由 ===
@app.get("/")
async def root():
    """服务状态 - 免费"""
    return {
        "service": "x402 Python Demo - 天气 API",
        "status": "running",
        "endpoints": {
            "/": "免费 - 服务状态（你现在看到的）",
            "/api/weather": "付费 - 天气数据（$0.001 USDC/次）",
        },
        "network": "Base Sepolia（测试网）",
    }


if __name__ == "__main__":
    import uvicorn

    print()
    print("🏪 x402 卖方服务已启动（Python 版）")
    print(f"   地址：http://localhost:{PORT}")
    print(f"   收款钱包：{seller_address}")
    print(f"   Facilitator：{facilitator_url}")
    print()
    print("📡 路由：")
    print(f"   GET http://localhost:{PORT}/          → 免费（服务状态）")
    print(f"   GET http://localhost:{PORT}/api/weather → 付费（$0.001 USDC）")
    print()
    print("等待买方请求...")
    print()

    uvicorn.run(app, host="0.0.0.0", port=PORT, log_level="info")
