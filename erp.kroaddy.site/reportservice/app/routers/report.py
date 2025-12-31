"""
리포트 관련 라우터
"""
from fastapi import APIRouter
from common.utils import create_response

router = APIRouter(prefix="/report", tags=["report"])


@router.get("/")
async def report_root():
    """리포트 서비스 루트"""
    return create_response(
        data={"service": "reportservice", "status": "running"},
        message="Report Service is running"
    )


@router.get("/health")
async def health_check():
    """헬스 체크"""
    return create_response(
        data={"status": "healthy", "service": "reportservice"},
        message="Service is healthy"
    )

