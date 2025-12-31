"""
Report Service 설정
"""
from common.config import BaseServiceConfig


class ReportServiceConfig(BaseServiceConfig):
    """리포트 서비스 설정"""
    service_name: str = "reportservice"
    service_version: str = "1.0.0"
    port: int = 9006
    
    class Config:
        env_file = ".env"
        case_sensitive = False

