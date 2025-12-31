"""
LLM API 모듈
외부 LLM API (OpenAI, Anthropic 등)와 통신
"""
import os
import httpx
from typing import Optional, Dict, Any
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class LLMAPI:
    """LLM API 클라이언트"""
    
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
        self.anthropic_base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1")
    
    async def chat_completion(
        self,
        messages: list[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        provider: str = "openai",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        LLM API를 호출하여 채팅 완성
        
        Args:
            messages: 메시지 리스트 [{"role": "user", "content": "..."}]
            model: 모델 이름
            provider: "openai" 또는 "anthropic"
            temperature: 온도 파라미터
            max_tokens: 최대 토큰 수
        
        Returns:
            API 응답 딕셔너리
        """
        try:
            if provider == "openai":
                return await self._openai_chat(messages, model, temperature, max_tokens)
            elif provider == "anthropic":
                return await self._anthropic_chat(messages, model, temperature, max_tokens)
            else:
                raise ValueError(f"지원하지 않는 provider: {provider}")
        except Exception as e:
            logger.error(f"LLM API 호출 실패: {e}")
            raise
    
    async def _openai_chat(
        self,
        messages: list[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """OpenAI API 호출"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY가 설정되지 않았습니다.")
        
        url = f"{self.openai_base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        if max_tokens:
            payload["max_tokens"] = max_tokens
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()
    
    async def _anthropic_chat(
        self,
        messages: list[Dict[str, str]],
        model: str,
        temperature: float,
        max_tokens: Optional[int]
    ) -> Dict[str, Any]:
        """Anthropic API 호출"""
        if not self.anthropic_api_key:
            raise ValueError("ANTHROPIC_API_KEY가 설정되지 않았습니다.")
        
        url = f"{self.anthropic_base_url}/messages"
        headers = {
            "x-api-key": self.anthropic_api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        # Anthropic 형식으로 메시지 변환
        system_message = None
        conversation_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                conversation_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        payload = {
            "model": model,
            "messages": conversation_messages,
            "temperature": temperature,
            "max_tokens": max_tokens or 1024
        }
        
        if system_message:
            payload["system"] = system_message
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()
            return response.json()

