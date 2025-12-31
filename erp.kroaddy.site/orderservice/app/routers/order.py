"""
주문 관련 라우터
"""
from fastapi import APIRouter
from common.utils import create_response

router = APIRouter(prefix="/order", tags=["order"])


@router.get("/")
async def order_root():
    """주문 서비스 루트"""
    return create_response(
        data={"service": "orderservice", "status": "running"},
        message="Order Service is running"
    )


@router.get("/health")
async def health_check():
    """헬스 체크"""
    return create_response(
        data={"status": "healthy", "service": "orderservice"},
        message="Service is healthy"
    )

