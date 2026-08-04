"""
Function Calling 工具管理器
支持 30+ 业务工具
"""
import logging
from typing import Dict, List, Any
from app.tools.order_tools import OrderTools
from app.tools.price_tools import PriceTools
from app.tools.inventory_tools import InventoryTools
from app.tools.customer_tools import CustomerTools

logger = logging.getLogger(__name__)


class ToolManager:
    """工具管理器"""
    
    def __init__(self):
        self.tools = {}
        self._register_tools()
    
    def _register_tools(self):
        """注册所有工具"""
        # 注册订单相关工具
        order_tools = OrderTools()
        self.tools.update(order_tools.get_tools())
        
        # 注册价格相关工具
        price_tools = PriceTools()
        self.tools.update(price_tools.get_tools())
        
        # 注册库存相关工具
        inventory_tools = InventoryTools()
        self.tools.update(inventory_tools.get_tools())
        
        # 注册客户相关工具
        customer_tools = CustomerTools()
        self.tools.update(customer_tools.get_tools())
        
        logger.info(f"已注册 {len(self.tools)} 个工具")
    
    def get_available_tools(self) -> List[Dict]:
        """
        获取可用工具列表（用于 Function Calling）
        
        Returns:
            OpenAI Function Calling 格式的工具列表
        """
        return [
            {
                "type": "function",
                "function": {
                    "name": name,
                    "description": tool["description"],
                    "parameters": tool["parameters"]
                }
            }
            for name, tool in self.tools.items()
        ]
    
    async def execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        执行工具
        
        Args:
            tool_name: 工具名称
            arguments: 工具参数
            
        Returns:
            工具执行结果
        """
        if tool_name not in self.tools:
            raise ValueError(f"工具不存在: {tool_name}")
        
        tool = self.tools[tool_name]
        handler = tool["handler"]
        
        try:
            result = await handler(**arguments)
            logger.info(f"工具执行成功: {tool_name}, 参数: {arguments}")
            return result
        except Exception as e:
            logger.error(f"工具执行失败: {tool_name}, 错误: {str(e)}")
            raise

