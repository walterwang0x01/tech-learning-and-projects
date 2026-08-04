"""
LLM 客户端（支持 Amazon Bedrock 和 OpenAI）
"""
import logging
from typing import Optional, List, Dict, AsyncGenerator
import boto3
from botocore.exceptions import ClientError
from openai import AsyncOpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)


class LLMClient:
    """LLM 客户端"""
    
    def __init__(self):
        self.bedrock_client = None
        self.openai_client = None
        
        # 初始化 Bedrock 客户端
        if settings.AWS_ACCESS_KEY_ID and settings.AWS_SECRET_ACCESS_KEY:
            try:
                self.bedrock_client = boto3.client(
                    'bedrock-runtime',
                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                    region_name=settings.AWS_REGION
                )
                logger.info("Bedrock 客户端初始化成功")
            except Exception as e:
                logger.warning(f"Bedrock 客户端初始化失败: {str(e)}")
        
        # 初始化 OpenAI 客户端
        if settings.OPENAI_API_KEY:
            self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            logger.info("OpenAI 客户端初始化成功")
    
    async def chat(
        self,
        message: str,
        context: str = "",
        tools: Optional[List[Dict]] = None,
        tool_results: Optional[List[Dict]] = None,
        conversation_id: Optional[str] = None,
        stream: bool = False
    ) -> Dict:
        """
        调用 LLM 进行对话
        
        Args:
            message: 用户消息
            context: RAG 检索的上下文
            tools: 可用工具列表
            tool_results: 工具执行结果
            conversation_id: 会话ID
            stream: 是否流式输出
            
        Returns:
            LLM 响应
        """
        # 构建提示词
        prompt = self._build_prompt(message, context)
        
        # 优先使用 Bedrock
        if self.bedrock_client:
            return await self._chat_with_bedrock(prompt, tools, tool_results)
        elif self.openai_client:
            return await self._chat_with_openai(prompt, tools, tool_results, stream)
        else:
            raise ValueError("未配置 LLM 客户端")
    
    async def chat_stream(
        self,
        message: str,
        context: str = "",
        tools: Optional[List[Dict]] = None,
        conversation_id: Optional[str] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        流式对话
        
        Yields:
            内容块
        """
        prompt = self._build_prompt(message, context)
        
        if self.openai_client:
            async for chunk in self._chat_stream_openai(prompt, tools):
                yield chunk
        else:
            # Bedrock 流式输出实现
            response = await self._chat_with_bedrock(prompt, tools)
            # 模拟流式输出
            for char in response["content"]:
                yield {"content": char, "done": False}
            yield {"content": "", "done": True}
    
    def _build_prompt(self, message: str, context: str) -> str:
        """构建提示词"""
        parts = []
        
        if context:
            parts.append(f"上下文信息：\n{context}\n")
        
        parts.append(f"用户问题：{message}\n")
        parts.append("请基于上下文信息回答用户问题，如果上下文不包含相关信息，请说明。")
        
        return "\n".join(parts)
    
    async def _chat_with_bedrock(self, prompt: str, tools: Optional[List], tool_results: Optional[List]) -> Dict:
        """使用 Bedrock 调用"""
        try:
            import json
            body = json.dumps({
                "prompt": prompt,
                "max_tokens_to_sample": 4096,
                "temperature": 0.7
            })
            
            response = self.bedrock_client.invoke_model(
                modelId=settings.BEDROCK_MODEL_ID,
                body=body
            )
            
            # 解析响应
            response_body = json.loads(response['body'].read())
            result = response_body.get('completion', '')
            
            return {
                "content": result,
                "tool_calls": None
            }
        except Exception as e:
            logger.error(f"Bedrock 调用失败: {str(e)}")
            raise
    
    async def _chat_with_openai(self, prompt: str, tools: Optional[List], tool_results: Optional[List], stream: bool) -> Dict:
        """使用 OpenAI 调用"""
        messages = [{"role": "user", "content": prompt}]
        
        response = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            stream=stream
        )
        
        if stream:
            content = ""
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content += chunk.choices[0].delta.content
            return {"content": content, "tool_calls": None}
        else:
            return {
                "content": response.choices[0].message.content,
                "tool_calls": response.choices[0].message.tool_calls
            }
    
    async def _chat_stream_openai(self, prompt: str, tools: Optional[List]) -> AsyncGenerator[Dict, None]:
        """OpenAI 流式输出"""
        messages = [{"role": "user", "content": prompt}]
        
        stream = await self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=messages,
            tools=tools,
            stream=True
        )
        
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield {
                    "content": chunk.choices[0].delta.content,
                    "done": False
                }
        
        yield {"content": "", "done": True}

