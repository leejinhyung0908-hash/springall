"""Pydantic 모델 정의."""
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """채팅 요청 모델."""

    question: str = Field(..., description="사용자의 질문", min_length=1)
    mode: str = Field(
        default="rag_openai",
        description=(
            "응답 모드: "
            "'rag' (RAG만), "
            "'openai' (OpenAI만), "
            "'rag_openai' (RAG+OpenAI), "
            "'rag_local' (RAG+로컬 LLM), "
            "'local' (로컬 LLM만)"
        ),
    )
    top_k: int = Field(default=3, description="검색할 문서 개수", ge=1, le=10)


class ChatResponse(BaseModel):
    """채팅 응답 모델."""

    answer: str = Field(..., description="생성된 답변")
    retrieved_docs: list[str] | None = Field(
        default=None, description="검색된 문서 목록 (RAG 모드일 때만)"
    )
    mode: str = Field(..., description="사용된 응답 모드")
    top_k: int = Field(default=3, description="검색된 문서 개수")


class HealthResponse(BaseModel):
    """헬스 체크 응답 모델."""

    status: str = Field(default="ok", description="서버 상태")
    database: str = Field(default="unknown", description="데이터베이스 연결 상태")


class QLoRARequest(BaseModel):
    """QLoRA 채팅 요청 모델."""

    prompt: str = Field(..., description="입력 프롬프트", min_length=1)
    max_new_tokens: int = Field(
        default=512, description="생성할 최대 토큰 수", ge=1, le=2048
    )
    temperature: float = Field(
        default=0.7, description="생성 온도", ge=0.0, le=2.0
    )
    top_p: float = Field(default=0.9, description="top-p 샘플링", ge=0.0, le=1.0)


class QLoRAResponse(BaseModel):
    """QLoRA 채팅 응답 모델."""

    response: str = Field(..., description="생성된 응답")
