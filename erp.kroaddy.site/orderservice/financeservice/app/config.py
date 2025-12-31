"""
Chatbot Service 설정
"""
from common.config import BaseServiceConfig


class ChatbotServiceConfig(BaseServiceConfig):
    """챗봇 서비스 설정"""
    service_name: str = "chatbotservice"
    service_version: str = "1.0.0"
    port: int = 9003
    
    class Config:
        env_file = ".env"
        case_sensitive = False

