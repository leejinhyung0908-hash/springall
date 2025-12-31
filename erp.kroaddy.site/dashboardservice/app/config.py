"""
Dashboard Service 설정
"""
from common.config import BaseServiceConfig


class DashboardServiceConfig(BaseServiceConfig):
    """대시보드 서비스 설정"""
    service_name: str = "dashboardservice"
    service_version: str = "1.0.0"
    port: int = 9008
    
    class Config:
        env_file = ".env"
        case_sensitive = False

