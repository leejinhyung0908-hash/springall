"""
Order Service 설정
"""
from common.config import BaseServiceConfig


class OrderServiceConfig(BaseServiceConfig):
    """주문 서비스 설정"""
    service_name: str = "orderservice"
    service_version: str = "1.0.0"
    port: int = 9007
    
    class Config:
        env_file = ".env"
        case_sensitive = False

