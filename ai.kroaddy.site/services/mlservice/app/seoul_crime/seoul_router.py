"""
서울시 범죄 데이터 관련 라우터
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# 공통 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.seoul_crime.seoul_service import SeoulService
import logging

# common.utils가 없을 경우를 대비한 fallback
try:
    from common.utils import create_response, create_error_response
except ImportError:
    # common.utils가 없을 경우 기본 함수 사용
    def create_response(data: Any, message: str = "Success"):
        return {"status": "success", "message": message, "data": data}
    
    def create_error_response(message: str, status_code: int = 400):
        return {"status": "error", "message": message}

logger = logging.getLogger(__name__)

router = APIRouter(tags=["seoul"])

# 서비스 인스턴스 생성 (싱글톤 패턴)
_service_instance: Optional[SeoulService] = None


def get_service() -> SeoulService:
    """SeoulService 싱글톤 인스턴스 반환"""
    global _service_instance
    if _service_instance is None:
        _service_instance = SeoulService()
    return _service_instance


@router.get("/")
async def seoul_root():
    """서울시 범죄 데이터 서비스 루트"""
    return create_response(
        data={"service": "mlservice", "module": "seoul", "status": "running"},
        message="Seoul Service is running"
    )

@router.get("/preprocess")
async def preprocess_data():
    """
    서울시 범죄 데이터 전처리 실행
    - CCTV, 범죄, 인구 데이터 로드 및 병합
    - 데이터 전처리 파이프라인 실행
    """
    try:
        service = get_service()
        result = service.preprocess()
        return create_response(
            data=result,
            message="데이터 전처리가 완료되었습니다"
        )
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=f"데이터 파일을 찾을 수 없습니다: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"전처리 중 오류가 발생했습니다: {str(e)}"
        )