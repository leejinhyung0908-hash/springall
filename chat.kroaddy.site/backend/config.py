"""애플리케이션 설정 관리."""
import os
from typing import Optional

from dotenv import load_dotenv

# 프로젝트 루트의 .env 파일을 로드한다.
load_dotenv()


class Settings:
    """애플리케이션 설정."""

    # 데이터베이스 설정 (동기 psycopg용)
    # Neon DB URL을 .env 파일에서 가져옴 (기본값 없음 - 필수)
    DATABASE_URL: str

    # LangChain PGEngine / asyncpg용 연결 문자열
    PGENGINE_URL: str

    # OpenAI 설정
    OPENAI_API_KEY: Optional[str]
    OPENAI_MODEL: str

    # 벡터 임베딩 설정
    EMBED_DIM: int

    # API 설정
    API_TITLE: str
    API_VERSION: str
    API_DESCRIPTION: str

    # CORS 설정
    CORS_ORIGINS: list[str]

    # 서버 설정
    HOST: str
    PORT: int

    # LLM 모델 설정
    MODEL_BASE_PATH: str
    DEFAULT_MODEL_TYPE: str
    DEFAULT_MODEL_NAME: str

    def __init__(self):
        """설정 초기화 및 검증."""
        # 데이터베이스 설정 (Neon DB URL 필수)
        self.DATABASE_URL = os.getenv("DATABASE_URL") or ""
        if not self.DATABASE_URL:
            raise ValueError(
                "DATABASE_URL 환경 변수가 설정되지 않았습니다. "
                ".env 파일에 Neon DB URL을 설정해주세요. "
                "예: DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST.neon.tech/DBNAME?sslmode=require"
            )

        # LangChain PGEngine / asyncpg용 연결 문자열
        # Neon DB URL을 기반으로 asyncpg 형식으로 자동 변환
        pg_url = self.DATABASE_URL.replace("postgresql+psycopg://", "postgresql+asyncpg://")
        self.PGENGINE_URL = os.getenv("PGENGINE_URL", pg_url)

        # OpenAI 설정
        self.OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
        self.OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        # 벡터 임베딩 설정
        self.EMBED_DIM = int(os.getenv("EMBED_DIM", "8"))

        # API 설정
        self.API_TITLE = "LangChain RAG API"
        self.API_VERSION = "0.1.0"
        self.API_DESCRIPTION = "LangChain과 pgvector를 사용한 RAG 시스템 API"

        # CORS 설정
        cors_origins_env = os.getenv("CORS_ORIGINS")
        if cors_origins_env:
            # 환경 변수가 있으면 사용
            self.CORS_ORIGINS = cors_origins_env.split(",")
        else:
            # 기본값: 프로덕션 도메인
            self.CORS_ORIGINS = [
                "https://leejinhyung.shop",
                "https://www.leejinhyung.shop",
            ]

        # 서버 설정
        self.HOST = os.getenv("HOST", "0.0.0.0")
        self.PORT = int(os.getenv("PORT", "8000"))

        # LLM 모델 설정
        self.MODEL_BASE_PATH = os.getenv("MODEL_BASE_PATH", "./model")
        self.DEFAULT_MODEL_TYPE = os.getenv("DEFAULT_MODEL_TYPE", "midm")
        self.DEFAULT_MODEL_NAME = os.getenv("DEFAULT_MODEL_NAME", "midm")


settings = Settings()
