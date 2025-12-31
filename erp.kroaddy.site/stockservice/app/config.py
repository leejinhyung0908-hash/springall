"""
Stock Service 설정
"""
from common.config import BaseServiceConfig


class StockServiceConfig(BaseServiceConfig):
    """재고 서비스 설정"""
    service_name: str = "stockservice"
    service_version: str = "1.0.0"
    port: int = 9011
    
    class Config:
        env_file = ".env"
        case_sensitive = False

