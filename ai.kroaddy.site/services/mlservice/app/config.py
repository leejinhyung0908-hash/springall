"""
ML Service 설정
타이타닉 및 Place(화장실) 서비스 설정
"""
from common.config import BaseServiceConfig


class MLServiceConfig(BaseServiceConfig):
    """ML 서비스 설정 (타이타닉 + Place)"""
    service_name: str = "mlservice"
    service_version: str = "1.0.0"
    port: int = 9010
    
    # 타이타닉 서비스 설정
    titanic_csv_path: str = "app/titanic/train.csv"
    
    # Place 서비스 설정
    place_csv_path: str = "app/place/toilet.csv"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

