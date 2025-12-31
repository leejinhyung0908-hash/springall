"""
Agent 서비스 - LLM API 및 SLLM 관리
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from .llm_api import LLMAPI
from .sllm_db import SLLMDB
import logging
import hashlib

logger = logging.getLogger(__name__)

# Agent 라우터
agent_router = APIRouter(prefix="/agent", tags=["agent"])

# LLM API 및 SLLM DB 초기화
llm_api = LLMAPI()
sllm_db = SLLMDB()

# ============================================================================
# 요청/응답 모델
# ============================================================================

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    model: Optional[str] = "gpt-3.5-turbo"
    provider: Optional[str] = "openai"
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = None
    use_cache: Optional[bool] = True

class ChatResponse(BaseModel):
    response: str
    model: str
    provider: str
    cached: bool = False

class ModelRegisterRequest(BaseModel):
    name: str
    model_type: str
    model_path: str
    config: Optional[Dict[str, Any]] = None

class ConversationRequest(BaseModel):
    session_id: str
    limit: Optional[int] = 100

# ============================================================================
# API 엔드포인트
# ============================================================================

@agent_router.get("/")
async def agent_root():
    """Agent 서비스 상태"""
    return {
        "service": "Agent Service",
        "status": "running",
        "llm_api_ready": True,
        "sllm_db_ready": True
    }

@agent_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """LLM API를 통한 채팅"""
    try:
        # 캐시 확인
        if request.use_cache:
            prompt_text = str(request.messages)
            prompt_hash = hashlib.md5(prompt_text.encode()).hexdigest()
            cached_response = sllm_db.get_cached_response(prompt_hash)
            
            if cached_response:
                logger.info("캐시된 응답 사용")
                return ChatResponse(
                    response=cached_response,
                    model=request.model,
                    provider=request.provider,
                    cached=True
                )
        
        # LLM API 호출
        result = await llm_api.chat_completion(
            messages=request.messages,
            model=request.model,
            provider=request.provider,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        # 응답 추출
        if request.provider == "openai":
            response_text = result["choices"][0]["message"]["content"]
        elif request.provider == "anthropic":
            response_text = result["content"][0]["text"]
        else:
            response_text = str(result)
        
        # 캐시 저장
        if request.use_cache:
            prompt_hash = hashlib.md5(str(request.messages).encode()).hexdigest()
            sllm_db.cache_response(prompt_hash, response_text, request.model)
        
        # 대화 기록 저장
        if request.messages:
            last_message = request.messages[-1]
            if last_message.get("role") == "user":
                session_id = hashlib.md5(str(request.messages).encode()).hexdigest()[:16]
                sllm_db.save_conversation(
                    session_id=session_id,
                    user_message=last_message["content"],
                    model_response=response_text,
                    model_name=request.model,
                    metadata={"provider": request.provider}
                )
        
        return ChatResponse(
            response=response_text,
            model=request.model,
            provider=request.provider,
            cached=False
        )
    
    except Exception as e:
        logger.error(f"채팅 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@agent_router.post("/models/register")
async def register_model(request: ModelRegisterRequest):
    """SLLM 모델 등록"""
    try:
        model_id = sllm_db.register_model(
            name=request.name,
            model_type=request.model_type,
            model_path=request.model_path,
            config=request.config
        )
        return {
            "success": True,
            "model_id": model_id,
            "message": f"모델 '{request.name}'이 등록되었습니다."
        }
    except Exception as e:
        logger.error(f"모델 등록 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@agent_router.get("/models")
async def list_models():
    """등록된 모델 목록 조회"""
    try:
        models = sllm_db.list_models()
        return {
            "success": True,
            "models": models,
            "count": len(models)
        }
    except Exception as e:
        logger.error(f"모델 목록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@agent_router.get("/models/{model_name}")
async def get_model(model_name: str):
    """특정 모델 정보 조회"""
    try:
        model = sllm_db.get_model(model_name)
        if not model:
            raise HTTPException(status_code=404, detail=f"모델 '{model_name}'을 찾을 수 없습니다.")
        return {
            "success": True,
            "model": model
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"모델 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@agent_router.get("/conversations")
async def get_conversations(session_id: Optional[str] = None, limit: int = 100):
    """대화 기록 조회"""
    try:
        conversations = sllm_db.get_conversations(session_id=session_id, limit=limit)
        return {
            "success": True,
            "conversations": conversations,
            "count": len(conversations)
        }
    except Exception as e:
        logger.error(f"대화 기록 조회 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

