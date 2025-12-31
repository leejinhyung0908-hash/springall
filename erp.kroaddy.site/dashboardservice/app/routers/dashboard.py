"""
대시보드 관련 라우터
"""
from fastapi import APIRouter
from common.utils import create_response

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/")
async def dashboard_root():
    """대시보드 서비스 루트"""
    return create_response(
        data={"service": "dashboardservice", "status": "running"},
        message="Dashboard Service is running"
    )


@router.get("/health")
async def health_check():
    """헬스 체크"""
    return create_response(
        data={"status": "healthy", "service": "dashboardservice"},
        message="Service is healthy"
    )

