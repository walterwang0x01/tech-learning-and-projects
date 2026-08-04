"""MCP 工具测试"""

from app.mcp_servers.db_server import query_users, query_orders
from app.mcp_servers.file_server import list_files


def test_query_users_all():
    result = query_users.invoke({})
    assert "张三" in result
    assert "李四" in result


def test_query_users_by_name():
    result = query_users.invoke({"name": "张三"})
    assert "张三" in result
    assert "李四" not in result


def test_query_orders_by_status():
    result = query_orders.invoke({"status": "completed"})
    assert "笔记本电脑" in result


def test_list_files():
    result = list_files.invoke({})
    assert isinstance(result, str)
