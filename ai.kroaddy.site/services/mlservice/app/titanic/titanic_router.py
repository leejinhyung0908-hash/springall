"""
타이타닉 관련 라우터
"""
from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# 공통 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.titanic.titanic_service import TitanicService
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

router = APIRouter(prefix="/titanic", tags=["titanic"])

# 서비스 인스턴스 생성 (싱글톤 패턴)
_service_instance: Optional[TitanicService] = None


def get_service() -> TitanicService:
    """TitanicService 싱글톤 인스턴스 반환"""
    global _service_instance
    if _service_instance is None:
        _service_instance = TitanicService()
    return _service_instance


@router.get("/")
async def titanic_root():
    """타이타닉 서비스 루트"""
    return create_response(
        data={"service": "mlservice", "module": "titanic", "status": "running"},
        message="Titanic Service is running"
    )

@router.get("/preprocess")
async def preprocess_data():
    """
    타이타닉 데이터 전처리 실행
    - 피처 삭제, 인코딩, 결측치 처리 등 전체 전처리 파이프라인 실행
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
@router.get("/evaluate")
async def evaluate_model():
    """
    모델 평가 실행
    - 전처리, 모델링, 학습, 평가를 순차적으로 실행
    - 후 모델 평가 결과 반환
    """
    try:
        service = get_service()
        
        # 1. 전처리
        logger.info("전처리 실행 중...")
        service.preprocess()
        
        # 2. 평가 (K-Fold 교차 검증 사용, 별도 학습 불필요)
        logger.info("평가 실행 중...")
        result = service.evaluate()
        
        return create_response(
            data=result,
            message="모델 평가가 완료되었습니다"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"평가 중 오류가 발생했습니다: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"평가 중 오류가 발생했습니다: {str(e)}"
        )

@router.get("/submit")
async def submit_model():
    """
    제출 실행
    """        
    try:
        service = get_service()
        logger.info("제출 실행 중...")
        result = service.submit()
        return create_response(
            data=result,
            message="제출 파일이 생성되었습니다"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"제출 중 오류가 발생했습니다: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"제출 중 오류가 발생했습니다: {str(e)}"
        )
