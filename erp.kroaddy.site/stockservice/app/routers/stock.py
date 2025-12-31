"""
재고 관련 라우터
"""
from fastapi import APIRouter
from common.utils import create_response

router = APIRouter(prefix="/stock", tags=["stock"])


@router.get("/")
async def stock_root():
    """재고 서비스 루트"""
    return create_response(
        data={"service": "stockservice", "status": "running"},
        message="Stock Service is running"
    )


@router.get("/health")
async def health_check():
    """헬스 체크"""
    return create_response(
        data={"status": "healthy", "service": "stockservice"},
        message="Service is healthy"
    )

