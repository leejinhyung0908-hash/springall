"""
Customer Service 설정
"""
from common.config import BaseServiceConfig


class CustomerServiceConfig(BaseServiceConfig):
    """고객 서비스 설정"""
    service_name: str = "customerservice"
    service_version: str = "1.0.0"
    port: int = 9009
    
    class Config:
        env_file = ".env"
        case_sensitive = False

