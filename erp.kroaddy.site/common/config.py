"""
공통 설정 관리
"""
from pydantic_settings import BaseSettings
from typing import Optional


class BaseServiceConfig(BaseSettings):
    """서비스 기본 설정"""
    service_name: str
    service_version: str = "1.0.0"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class DatabaseConfig(BaseSettings):
    """데이터베이스 설정 (필요시 사용)"""
    database_url: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False


class RedisConfig(BaseSettings):
    """Redis 설정 (필요시 사용)"""
    redis_host: str = "redis"
    redis_port: int = 6379
    redis_password: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = False

