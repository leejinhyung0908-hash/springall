"""
고객 관련 라우터
"""
from fastapi import APIRouter
from common.utils import create_response

router = APIRouter(prefix="/customer", tags=["customer"])


@router.get("/")
async def customer_root():
    """고객 서비스 루트"""
    return create_response(
        data={"service": "customerservice", "status": "running"},
        message="Customer Service is running"
    )


@router.get("/health")
async def health_check():
    """헬스 체크"""
    return create_response(
        data={"status": "healthy", "service": "customerservice"},
        message="Service is healthy"
    )

