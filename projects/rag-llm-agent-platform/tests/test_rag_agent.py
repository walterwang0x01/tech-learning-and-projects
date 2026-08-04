"""
RAG Agent 单元测试
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from app.agents.rag_agent import RAGAgent


@pytest.fixture
def mock_vector_store():
    """模拟向量存储"""
    store = MagicMock()
    return store


@pytest.fixture
def mock_retriever(mock_vector_store):
    """模拟检索器"""
    retriever = MagicMock()
    retriever.retrieve = AsyncMock(return_value=[
        {"content": "测试文档1", "source": "doc1"},
        {"content": "测试文档2", "source": "doc2"}
    ])
    return retriever


@pytest.fixture
def mock_tool_manager():
    """模拟工具管理器"""
    manager = MagicMock()
    manager.get_available_tools = MagicMock(return_value=[])
    manager.execute_tool = AsyncMock(return_value={"result": "success"})
    return manager


@pytest.fixture
def mock_llm_client():
    """模拟 LLM 客户端"""
    client = MagicMock()
    client.chat = AsyncMock(return_value={
        "content": "这是测试响应",
        "tool_calls": None
    })
    client.chat_stream = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_chat_success(mock_retriever, mock_tool_manager, mock_llm_client):
    """测试聊天成功"""
    with patch('app.agents.rag_agent.VectorStore', return_value=MagicMock()), \
         patch('app.agents.rag_agent.Retriever', return_value=mock_retriever), \
         patch('app.agents.rag_agent.ToolManager', return_value=mock_tool_manager), \
         patch('app.agents.rag_agent.LLMClient', return_value=mock_llm_client):
        
        agent = RAGAgent()
        result = await agent.chat("测试问题")
        
        assert result is not None
        assert "response" in result
        assert "conversation_id" in result
        assert result["response"] == "这是测试响应"
        mock_retriever.retrieve.assert_called_once()


@pytest.mark.asyncio
async def test_chat_with_tool_calls(mock_retriever, mock_tool_manager, mock_llm_client):
    """测试带工具调用的聊天"""
    # 模拟第一次调用返回工具调用请求
    mock_llm_client.chat = AsyncMock(side_effect=[
        {
            "content": None,
            "tool_calls": [{"name": "create_order", "arguments": {"customer_id": "123"}}]
        },
        {
            "content": "订单创建成功",
            "tool_calls": None
        }
    ])
    
    with patch('app.agents.rag_agent.VectorStore', return_value=MagicMock()), \
         patch('app.agents.rag_agent.Retriever', return_value=mock_retriever), \
         patch('app.agents.rag_agent.ToolManager', return_value=mock_tool_manager), \
         patch('app.agents.rag_agent.LLMClient', return_value=mock_llm_client):
        
        agent = RAGAgent()
        result = await agent.chat("创建订单")
        
        assert result["response"] == "订单创建成功"
        mock_tool_manager.execute_tool.assert_called_once()


@pytest.mark.asyncio
async def test_chat_stream(mock_retriever, mock_tool_manager, mock_llm_client):
    """测试流式聊天"""
    async def mock_stream():
        yield {"content": "这是", "done": False}
        yield {"content": "流式", "done": False}
        yield {"content": "响应", "done": True}
    
    mock_llm_client.chat_stream = mock_stream
    
    with patch('app.agents.rag_agent.VectorStore', return_value=MagicMock()), \
         patch('app.agents.rag_agent.Retriever', return_value=mock_retriever), \
         patch('app.agents.rag_agent.ToolManager', return_value=mock_tool_manager), \
         patch('app.agents.rag_agent.LLMClient', return_value=mock_llm_client):
        
        agent = RAGAgent()
        chunks = []
        async for chunk in agent.chat_stream("测试问题"):
            chunks.append(chunk)
        
        assert len(chunks) > 0
        assert all("content" in chunk for chunk in chunks)

