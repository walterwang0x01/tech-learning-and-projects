"""
客户相关工具
"""
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class CustomerTools:
    """客户工具类"""
    
    def get_tools(self) -> Dict[str, Dict]:
        """获取客户相关工具定义"""
        return {
            "get_customer_info": {
                "description": "获取客户信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "客户ID"
                        }
                    },
                    "required": ["customer_id"]
                },
                "handler": self.get_customer_info
            },
            "update_customer_info": {
                "description": "更新客户信息",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "客户ID"
                        },
                        "field": {
                            "type": "string",
                            "description": "要更新的字段",
                            "enum": ["name", "email", "phone", "address"]
                        },
                        "value": {
                            "type": "string",
                            "description": "新值"
                        }
                    },
                    "required": ["customer_id", "field", "value"]
                },
                "handler": self.update_customer_info
            },
            "get_customer_orders": {
                "description": "获取客户的订单列表",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "customer_id": {
                            "type": "string",
                            "description": "客户ID"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "返回数量限制（默认10）",
                            "default": 10
                        }
                    },
                    "required": ["customer_id"]
                },
                "handler": self.get_customer_orders
            }
        }
    
    async def get_customer_info(self, customer_id: str) -> Dict[str, Any]:
        """获取客户信息"""
        logger.info(f"获取客户信息: customer_id={customer_id}")
        return {
            "customer_id": customer_id,
            "name": "测试客户",
            "email": "customer@example.com",
            "phone": "13800138000",
            "address": "上海市浦东新区",
            "vip_level": "gold"
        }
    
    async def update_customer_info(self, customer_id: str, field: str, value: str) -> Dict[str, Any]:
        """更新客户信息"""
        logger.info(f"更新客户信息: customer_id={customer_id}, field={field}, value={value}")
        return {
            "customer_id": customer_id,
            "field": field,
            "old_value": "旧值",
            "new_value": value,
            "message": "客户信息更新成功"
        }
    
    async def get_customer_orders(self, customer_id: str, limit: int = 10) -> Dict[str, Any]:
        """获取客户订单"""
        logger.info(f"获取客户订单: customer_id={customer_id}, limit={limit}")
        return {
            "customer_id": customer_id,
            "orders": [
                {"order_id": "ORD-001", "status": "completed", "amount": 100.0},
                {"order_id": "ORD-002", "status": "processing", "amount": 200.0}
            ],
            "total": 2
        }

