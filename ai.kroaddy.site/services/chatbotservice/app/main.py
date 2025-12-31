"""
Chatbot Service - FastAPI 애플리케이션
가격 분석 챗봇 서비스
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from app.price_analyzer import chatbot, simple_chat, analyze_price
import logging
import os
from pathlib import Path
from dotenv import load_dotenv

# 로깅 설정 (먼저 설정)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 루트 디렉토리의 .env 파일 로드
# 프로젝트 루트까지 상위로 이동하여 .env 파일 찾기
current_dir = Path(__file__).parent
root_dir = current_dir
env_loaded = False
for _ in range(5):  # 최대 5단계까지 상위 디렉토리 탐색
    env_file = root_dir / ".env"
    if env_file.exists():
        load_dotenv(env_file)
        logger.info(f"✓ .env 파일 로드 완료: {env_file}")
        env_loaded = True
        break
    parent = root_dir.parent
    if parent == root_dir:  # 더 이상 상위 디렉토리가 없으면 중단
        break
    root_dir = parent

if not env_loaded:
    # .env 파일을 찾지 못한 경우 현재 디렉토리와 상위 디렉토리에서 시도
    load_dotenv()  # 기본적으로 현재 디렉토리와 상위 디렉토리에서 .env 찾기
    logger.info("기본 경로에서 .env 파일 로드 시도")

app = FastAPI(title="Chatbot Service", version="1.0.0")

# CORS 설정 제거 (게이트웨이를 통해서만 접근하므로 게이트웨이에서 CORS 처리)
# 게이트웨이를 통하지 않고 직접 접근하는 경우를 위한 최소한의 CORS 설정
# 하지만 게이트웨이를 통해서만 접근하므로 주석 처리
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# ============================================================================
# 요청/응답 모델
# ============================================================================

class ChatRequest(BaseModel):
    """챗봇 대화 요청"""
    message: str
    conversation_history: Optional[List[Dict[str, str]]] = None
    user_profile: Optional[Dict[str, str]] = None  # Onboarding 데이터
    context_info: Optional[Dict] = None  # 현재 위치 및 날씨 정보

class ChatResponse(BaseModel):
    """챗봇 대화 응답"""
    response: str

class PriceAnalysisRequest(BaseModel):
    """가격 분석 요청"""
    product_name: str
    price: Optional[float] = None
    context: Optional[str] = None

class PriceAnalysisResponse(BaseModel):
    """가격 분석 응답"""
    analysis: str

# ============================================================================
# API 엔드포인트
# ============================================================================

@app.get("/")
async def root():
    """서비스 상태 확인"""
    return {
        "service": "Chatbot Service",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "chatbot_ready": True
    }

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    챗봇과 대화
    
    Args:
        request: 대화 요청 (메시지, 대화 이력)
    
    Returns:
        챗봇 응답
    """
    try:
        logger.info(f"챗봇 요청 수신: {request.message}")
        logger.info(f"대화 이력 길이: {len(request.conversation_history) if request.conversation_history else 0}")
        
        # 대화 이력 검증 및 정리
        cleaned_history = None
        if request.conversation_history:
            cleaned_history = []
            for msg in request.conversation_history:
                if isinstance(msg, dict) and "role" in msg and "content" in msg:
                    # role이 유효한지 확인
                    if msg["role"] in ["user", "assistant", "system"]:
                        cleaned_history.append({
                            "role": msg["role"],
                            "content": str(msg["content"])
                        })
                    else:
                        logger.warning(f"유효하지 않은 role: {msg['role']}")
                else:
                    logger.warning(f"잘못된 메시지 형식: {msg}")
            
            logger.info(f"정리된 대화 이력 길이: {len(cleaned_history)}")
        
        # 사용자 프로필 정보 로깅
        if request.user_profile:
            logger.info(f"사용자 프로필 정보: {request.user_profile}")
        
        # 컨텍스트 정보 로깅
        if request.context_info:
            logger.info(f"컨텍스트 정보 (위치/날씨): {request.context_info}")
        
        if cleaned_history and len(cleaned_history) > 0:
            # 대화 이력이 있으면 전달
            response = chatbot.chat(
                request.message,
                conversation_history=cleaned_history,
                user_profile=request.user_profile,
                context_info=request.context_info
            )
        else:
            # 대화 이력이 없으면 간단한 호출 (사용자 프로필 및 컨텍스트는 전달)
            if request.user_profile or request.context_info:
                # simple_chat은 user_profile과 context_info를 받지 않으므로 직접 chatbot.chat 호출
                response = chatbot.chat(
                    request.message,
                    conversation_history=None,
                    user_profile=request.user_profile,
                    context_info=request.context_info
                )
            else:
                response = simple_chat(request.message)
        
        logger.info(f"챗봇 응답 생성 완료 (길이: {len(response)} 문자)")
        return ChatResponse(response=response)
        
    except Exception as e:
        logger.error(f"챗봇 호출 실패: {e}", exc_info=True)
        import traceback
        logger.error(f"에러 상세: {traceback.format_exc()}")
        
        # 에러 메시지를 사용자에게 전달하되, 상세 정보는 숨김
        error_str = str(e)
        error_detail = "일시적인 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        
        if "invalid_api_key" in error_str.lower() or "incorrect api key" in error_str.lower() or "401" in error_str:
            error_detail = "OpenAI API 키 설정 오류가 발생했습니다. 관리자에게 문의해주세요."
        elif "rate limit" in error_str.lower() or "429" in error_str:
            error_detail = "요청 한도 초과. 잠시 후 다시 시도해주세요."
        
        raise HTTPException(status_code=500, detail=error_detail)

@app.post("/analyze-price", response_model=PriceAnalysisResponse)
async def analyze_price_endpoint(request: PriceAnalysisRequest):
    """
    가격 분석 요청
    
    Args:
        request: 가격 분석 요청 (상품명, 가격, 컨텍스트)
    
    Returns:
        가격 분석 결과
    """
    try:
        logger.info(f"가격 분석 요청: {request.product_name}, 가격: {request.price}")
        
        analysis = analyze_price(
            request.product_name,
            request.price,
            request.context
        )
        
        logger.info("가격 분석 완료")
        return PriceAnalysisResponse(analysis=analysis)
        
    except Exception as e:
        logger.error(f"가격 분석 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9004)

