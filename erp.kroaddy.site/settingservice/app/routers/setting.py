"""
설정 관련 라우터
"""
from fastapi import APIRouter
from common.utils import create_response

router = APIRouter(prefix="/setting", tags=["setting"])


@router.get("/")
async def setting_root():
    """설정 서비스 루트"""
    return create_response(
        data={"service": "settingservice", "status": "running"},
        message="Setting Service is running"
    )


@router.get("/health")
async def health_check():
    """헬스 체크"""
    return create_response(
        data={"status": "healthy", "service": "settingservice"},
        message="Service is healthy"
    )

