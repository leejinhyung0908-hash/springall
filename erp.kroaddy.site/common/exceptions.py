"""
공통 예외 클래스
"""
from fastapi import HTTPException, status


class ServiceException(HTTPException):
    """서비스 공통 예외"""
    def __init__(self, detail: str, status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR):
        super().__init__(status_code=status_code, detail=detail)


class NotFoundException(ServiceException):
    """리소스를 찾을 수 없음"""
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail=detail, status_code=status.HTTP_404_NOT_FOUND)


class ValidationException(ServiceException):
    """유효성 검증 실패"""
    def __init__(self, detail: str = "Validation failed"):
        super().__init__(detail=detail, status_code=status.HTTP_400_BAD_REQUEST)

