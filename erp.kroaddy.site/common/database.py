"""
ERP 서비스용 데이터베이스 연결 설정
Railway PostgreSQL 연동
"""
import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool
import redis
from typing import Generator

# 환경 변수에서 데이터베이스 설정 읽기
DATABASE_URL = os.getenv("DATABASE_URL")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "railway")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
REDIS_URL = os.getenv("REDIS_URL")

# PostgreSQL 연결 엔진 생성
if DATABASE_URL:
    # Railway에서 제공하는 DATABASE_URL 사용
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=True  # SQL 쿼리 로깅
    )
else:
    # 개별 환경 변수로 연결 문자열 구성
    database_url = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    engine = create_engine(
        database_url,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=300,
        echo=True
    )

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성
Base = declarative_base()

# 메타데이터 설정
metadata = MetaData()

# Upstash Redis 연결 (TLS 필수)
redis_client = None
REDIS_SSL_ENABLED = os.getenv("REDIS_SSL_ENABLED", "true").lower() == "true"

if REDIS_URL:
    try:
        # Upstash Redis는 TLS가 필수이므로 ssl_cert_reqs 설정
        if REDIS_SSL_ENABLED:
            import ssl
            redis_client = redis.from_url(
                REDIS_URL,
                decode_responses=True,
                ssl_cert_reqs=ssl.CERT_REQUIRED,
                ssl=True
            )
        else:
            redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        
        # 연결 테스트
        redis_client.ping()
        print("Upstash Redis 연결 성공")
    except Exception as e:
        print(f"Upstash Redis 연결 실패: {e}")
        redis_client = None

def get_db() -> Generator:
    """
    데이터베이스 세션 의존성
    FastAPI에서 Depends()로 사용
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_redis():
    """
    Redis 클라이언트 반환
    """
    return redis_client

def create_tables():
    """
    테이블 생성
    """
    Base.metadata.create_all(bind=engine)

def drop_tables():
    """
    테이블 삭제 (개발용)
    """
    Base.metadata.drop_all(bind=engine)

# 서비스별 스키마 설정
SCHEMAS = {
    "customer": "labzang_customer",
    "dashboard": "labzang_dashboard", 
    "order": "labzang_order",
    "report": "labzang_report",
    "setting": "labzang_setting",
    "stock": "labzang_stock",
}

def get_schema(service_name: str) -> str:
    """
    서비스명으로 스키마명 반환
    """
    return SCHEMAS.get(service_name, "public")

def create_schema_if_not_exists(schema_name: str):
    """
    스키마가 존재하지 않으면 생성
    """
    with engine.connect() as conn:
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")
        conn.commit()

# 애플리케이션 시작 시 스키마 생성
def init_schemas():
    """
    모든 ERP 서비스 스키마 초기화
    """
    for schema in SCHEMAS.values():
        create_schema_if_not_exists(schema)
    print("ERP 서비스 스키마 초기화 완료")

if __name__ == "__main__":
    # 테스트 실행
    print("데이터베이스 연결 테스트...")
    try:
        with engine.connect() as conn:
            result = conn.execute("SELECT version()")
            print(f"PostgreSQL 버전: {result.fetchone()[0]}")
        
        if redis_client:
            redis_client.set("test", "connection_ok")
            test_value = redis_client.get("test")
            print(f"Redis 테스트: {test_value}")
            redis_client.delete("test")
        
        init_schemas()
        print("데이터베이스 연결 및 설정 완료!")
        
    except Exception as e:
        print(f"데이터베이스 연결 실패: {e}")
