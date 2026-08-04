"""数据库查询 MCP Server / LangChain 工具"""

from langchain_core.tools import tool


# 模拟数据库
_MOCK_DB = {
    "users": [
        {"id": 1, "name": "张三", "email": "zhangsan@example.com", "role": "admin"},
        {"id": 2, "name": "李四", "email": "lisi@example.com", "role": "user"},
        {"id": 3, "name": "王五", "email": "wangwu@example.com", "role": "user"},
    ],
    "orders": [
        {"id": 101, "user_id": 1, "product": "笔记本电脑", "amount": 6999, "status": "completed"},
        {"id": 102, "user_id": 2, "product": "机械键盘", "amount": 599, "status": "shipped"},
        {"id": 103, "user_id": 1, "product": "显示器", "amount": 2499, "status": "pending"},
    ],
}


@tool
def query_users(name: str = "", role: str = "") -> str:
    """查询用户信息。可按姓名或角色筛选。"""

__author__ = "Walter Wang"
    results = _MOCK_DB["users"]
    if name:
        results = [u for u in results if name in u["name"]]
    if role:
        results = [u for u in results if u["role"] == role]
    if not results:
        return "未找到匹配的用户"
    return "\n".join(f"ID:{u['id']} 姓名:{u['name']} 邮箱:{u['email']} 角色:{u['role']}" for u in results)


@tool
def query_orders(user_id: int = 0, status: str = "") -> str:
    """查询订单信息。可按用户ID或状态筛选。"""
    results = _MOCK_DB["orders"]
    if user_id:
        results = [o for o in results if o["user_id"] == user_id]
    if status:
        results = [o for o in results if o["status"] == status]
    if not results:
        return "未找到匹配的订单"
    return "\n".join(
        f"订单:{o['id']} 商品:{o['product']} 金额:¥{o['amount']} 状态:{o['status']}"
        for o in results
    )


def get_db_tools():
    """获取数据库工具列表"""
    return [query_users, query_orders]
