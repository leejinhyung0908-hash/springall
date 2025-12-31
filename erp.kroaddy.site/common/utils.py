"""
공통 유틸리티 함수
"""
import logging
from typing import Any, Dict
from datetime import datetime


def setup_logging(service_name: str, level: str = "INFO") -> logging.Logger:
    """로깅 설정"""
    logger = logging.getLogger(service_name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def create_response(data: Any, message: str = "Success", status: str = "success") -> Dict:
    """표준 응답 형식 생성"""
    return {
        "status": status,
        "message": message,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    }


def create_error_response(message: str, error_code: str = "UNKNOWN_ERROR") -> Dict:
    """에러 응답 형식 생성"""
    return {
        "status": "error",
        "message": message,
        "error_code": error_code,
        "timestamp": datetime.utcnow().isoformat()
    }

