"""
工具管理器单元测试
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from app.tools.tool_manager import ToolManager
from app.tools.order_tools import OrderTools
from app.tools.price_tools import PriceTools


@pytest.fixture
def tool_manager():
    """创建工具管理器实例"""
    return ToolManager()


def test_get_available_tools(tool_manager):
    """测试获取可用工具列表"""
    tools = tool_manager.get_available_tools()
    
    assert len(tools) > 0
    assert all("type" in tool for tool in tools)
    assert all("function" in tool for tool in tools)
    assert all("name" in tool["function"] for tool in tools)


def test_tool_registration(tool_manager):
    """测试工具注册"""
    # 检查订单工具是否注册
    assert "create_order" in tool_manager.tools
    assert "update_order" in tool_manager.tools
    assert "get_order" in tool_manager.tools
    
    # 检查价格工具是否注册
    assert "update_price" in tool_manager.tools
    assert "get_price" in tool_manager.tools


@pytest.mark.asyncio
async def test_execute_tool_success(tool_manager):
    """测试工具执行成功"""
    result = await tool_manager.execute_tool(
        "create_order",
        {"customer_id": "123", "items": [{"product_id": "P1", "quantity": 2}]}
    )
    
    assert result is not None
    assert "order_id" in result or "message" in result


@pytest.mark.asyncio
async def test_execute_tool_not_found(tool_manager):
    """测试工具不存在的情况"""
    with pytest.raises(ValueError, match="工具不存在"):
        await tool_manager.execute_tool("non_existent_tool", {})

