"""FastAPI 메인 애플리케이션."""
import os
import sys
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.dependencies import connect_db, setup_schema, get_global_db_connection
from backend.routers import chat, health
from backend.services.database import reset_demo_data
from backend.services.embedding import simple_embed
from backend.services.database import search_similar
from backend.services.rag import rag_answer, rag_with_llm, openai_only
from backend.llm.register_models import register_all_models
import backend.dependencies as deps


@asynccontextmanager
async def lifespan(app: FastAPI):
    """애플리케이션 생명주기 관리."""
    # 시작 시
    print("[FastAPI] 서버 시작 중...", flush=True)

    # 모델 타입 등록
    register_all_models()

    try:
        deps._db_conn = connect_db(settings.DATABASE_URL)
        setup_schema(deps._db_conn)
        reset_demo_data(deps._db_conn)
        print("[FastAPI] DB 연결 및 스키마 초기화 완료", flush=True)
    except Exception as exc:
        print(f"[FastAPI] DB 초기화 실패: {exc}", flush=True)
        raise

    yield

    # 종료 시
    conn = get_global_db_connection()
    if conn and not conn.closed:
        conn.close()
        print("[FastAPI] DB 연결 종료", flush=True)


# FastAPI 앱 생성
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(health.router)
app.include_router(chat.router)


@app.get("/")
async def root():
    """루트 엔드포인트."""
    return {
        "message": "LangChain RAG API",
        "version": settings.API_VERSION,
        "docs": "/docs",
    }


# CLI 모드 함수들 (기존 app.py와의 호환성 유지)
def demo_once() -> None:
    """한 번의 질의에 대해 전체 파이프라인을 실행한다."""

    database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    print("=== LangChain + pgvector 데모 시작 ===")
    print(f"[설정] DATABASE_URL = {database_url}")

    conn = connect_db(database_url)
    print("[DB] Postgres 연결 완료")

    setup_schema(conn)
    print("[DB] pgvector 확장 및 documents 테이블 준비 완료")

    reset_demo_data(conn)
    print("[DB] 데모 문서 4건 삽입 완료")

    question = "LangChain과 pgvector가 무엇인지 설명해 줘"
    print(f"\n[질문] {question}")

    results = search_similar(conn, question, top_k=3)
    print("\n[벡터 검색 결과] (가까운 순)")
    for i, (content, distance) in enumerate(results, start=1):
        print(f"{i}. distance={distance:.4f} | content={content}")

    retrieved_docs = [c for c, _ in results]

    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key:
        print("\n[정보] OPENAI_API_KEY가 설정되어 있어 LLM 기반 RAG를 사용합니다.")
        answer = rag_with_llm(question, retrieved_docs)
    else:
        print("\n[정보] OPENAI_API_KEY가 없어 간단한 규칙 기반 RAG 응답을 사용합니다.")
        answer = rag_answer(question, retrieved_docs)

    print("\n[RAG 응답]")
    print(answer)

    conn.close()


def chat_loop() -> None:
    """대화형 모드: 사용자의 질문을 반복적으로 받고 RAG로 답변한다.

    - 터미널이 TTY가 아닐 경우(예: docker compose up 로그)에는 실행하지 않고 안내 메시지만 출력.
    """

    if not sys.stdin.isatty():
        print(
            "\n[대화형 모드 안내] 이 환경에서는 표준 입력이 TTY가 아니어서 "
            "`docker compose up` 로그에서는 실시간 입력을 받을 수 없습니다.\n"
            "대화형 모드를 사용하려면 아래처럼 실행해 주세요:\n"
            "  docker compose run --rm backend python -m backend.main\n"
        )
        return

    database_url = os.getenv("DATABASE_URL", settings.DATABASE_URL)
    conn = connect_db(database_url)
    setup_schema(conn)
    reset_demo_data(conn)

    print("\n=== 대화형 RAG 모드 ===")
    print("질문을 입력하면 pgvector 유사도 검색 + RAG로 답을 생성합니다.")
    print("종료하려면 'exit' 또는 'quit' 을 입력하세요.\n")

    openai_key = os.getenv("OPENAI_API_KEY")

    try:
        while True:
            question = input("질문> ").strip()
            if question.lower() in {"exit", "quit"}:
                print("대화형 모드를 종료합니다.")
                break

            results = search_similar(conn, question, top_k=3)
            print("\n[벡터 검색 결과]")
            for i, (content, distance) in enumerate(results, start=1):
                print(f"{i}. distance={distance:.4f} | content={content}")

            retrieved_docs = [c for c, _ in results]

            if openai_key:
                answer = rag_with_llm(question, retrieved_docs)
            else:
                answer = rag_answer(question, retrieved_docs)

            print("\n[RAG 응답]")
            print(answer)
            print("-" * 60)
    finally:
        conn.close()


def main() -> None:
    """앱 진입점.

    --server 플래그가 있으면 FastAPI 서버를 실행하고,
    없으면 기존 CLI 모드(데모 + 대화형)를 실행한다.
    """

    if "--server" in sys.argv:
        # FastAPI 서버 모드
        import uvicorn

        print("[FastAPI] 서버 모드로 시작합니다.", flush=True)
        uvicorn.run(
            "backend.main:app",
            host=settings.HOST,
            port=settings.PORT,
            log_level="info",
            reload=False,
        )
    else:
        # CLI 모드 (기존 동작)
        demo_once()

        print("\n=== 데모 완료 ===")
        print("위 로그에서 다음 기능이 모두 실행되었습니다:")
        print("1) 벡터 검색 (pgvector 유사도 검색)")
        print("2) RAG 시스템 (검색 문서를 기반으로 한 응답 생성)")
        print("3) 대화형 모드 진입 방법 안내")
        print("4) OpenAI API 키 유무에 따른 유연한 설정")

        chat_loop()

        print("\n컨테이너를 유지하기 위해 대기 중입니다. Ctrl+C 또는 docker stop 으로 종료하세요.")
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            print("\n종료 신호를 받아 컨테이너를 종료합니다.")


if __name__ == "__main__":
    main()

