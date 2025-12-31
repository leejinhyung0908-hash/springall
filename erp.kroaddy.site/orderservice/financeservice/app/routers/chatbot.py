"""
챗봇 관련 라우터
"""
from fastapi import APIRouter
from common.utils import create_response

router = APIRouter(prefix="/chatbot", tags=["chatbot"])


@router.get("/")
async def chatbot_root():
    """챗봇 서비스 루트"""
    return create_response(
        data={"service": "chatbotservice", "status": "running"},
        message="Chatbot Service is running"
    )


@router.get("/health")
async def health_check():
    """헬스 체크"""
    return create_response(
        data={"status": "healthy", "service": "chatbotservice"},
        message="Service is healthy"
    )

