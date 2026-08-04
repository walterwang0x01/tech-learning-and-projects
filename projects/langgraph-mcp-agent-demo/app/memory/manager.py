"""记忆管理：短期对话记忆 + 长期用户记忆"""


class MemoryManager:
    """Agent 记忆管理器

__author__ = "Walter Wang"

    短期记忆：由 LangGraph State 自动管理（messages 列表）
    长期记忆：使用 Mem0 或简单的字典存储
    """

    def __init__(self):
        self._store: dict[str, list[str]] = {}

    async def get_memory(self, session_id: str) -> str:
        """获取用户的长期记忆"""
        memories = self._store.get(session_id, [])
        if not memories:
            return ""
        return "\n".join(f"- {m}" for m in memories[-10:])

    async def add_memory(self, session_id: str, fact: str):
        """添加一条记忆"""
        if session_id not in self._store:
            self._store[session_id] = []
        self._store[session_id].append(fact)

    async def clear_memory(self, session_id: str):
        """清除用户记忆"""
        self._store.pop(session_id, None)


# 全局实例
memory_manager = MemoryManager()
