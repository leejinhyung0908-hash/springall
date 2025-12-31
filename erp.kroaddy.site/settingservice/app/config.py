"""
Setting Service 설정
"""
from common.config import BaseServiceConfig


class SettingServiceConfig(BaseServiceConfig):
    """설정 서비스 설정"""
    service_name: str = "settingservice"
    service_version: str = "1.0.0"
    port: int = 9005
    
    class Config:
        env_file = ".env"
        case_sensitive = False

