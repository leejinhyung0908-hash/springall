"""채팅 라우터."""
from fastapi import APIRouter, Depends, HTTPException
import psycopg

from backend.dependencies import get_db_connection, get_llm, get_qlora_service
from backend.models import ChatRequest, ChatResponse, QLoRARequest, QLoRAResponse
from backend.services.database import search_similar
from backend.services.rag import (
    local_only,
    openai_only,
    rag_answer,
    rag_with_llm,
    rag_with_local_llm,
)
from backend.config import settings

router = APIRouter(prefix="/api", tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    request: ChatRequest, conn: psycopg.Connection = Depends(get_db_connection)
) -> ChatResponse:
    """챗봇 엔드포인트. mode에 따라 RAG/OpenAI/둘 다 사용 가능.

    mode 옵션:
    - "rag": RAG만 사용 (규칙 기반, OpenAI 없이)
    - "openai": OpenAI만 사용 (RAG 없이)
    - "rag_openai": RAG + OpenAI (기본값)
    - "rag_local": RAG + 로컬 LLM (backend.llm)
    - "local": 로컬 LLM만 사용 (RAG 없이, backend.llm)
    """
    try:
        question = request.question.strip()
        if not question:
            raise HTTPException(status_code=400, detail="질문이 비어있습니다.")

        mode = request.mode.lower()
        if mode not in ("rag", "openai", "rag_openai", "rag_local", "local"):
            raise HTTPException(
                status_code=400,
                detail='mode는 "rag", "openai", "rag_openai", "rag_local", "local" 중 하나여야 합니다.',
            )

        answer: str
        retrieved_docs: list[str] | None = None

        if mode == "openai":
            # OpenAI만 사용 (RAG 없이)
            if not settings.OPENAI_API_KEY:
                raise HTTPException(
                    status_code=400,
                    detail="OPENAI_API_KEY가 설정되지 않아 OpenAI 모드를 사용할 수 없습니다.",
                )
            answer = openai_only(question)

        elif mode == "local":
            # 로컬 LLM만 사용 (RAG 없이, backend.llm)
            llm = get_llm()
            if not llm.is_loaded():
                llm.load()
            answer = local_only(question, llm)

        elif mode == "rag":
            # RAG만 사용 (규칙 기반, OpenAI 없이)
            results = search_similar(conn, question, top_k=request.top_k)
            retrieved_docs = [content for content, _ in results]
            answer = rag_answer(question, retrieved_docs)

        elif mode == "rag_openai":
            # RAG + OpenAI
            results = search_similar(conn, question, top_k=request.top_k)
            retrieved_docs = [content for content, _ in results]

            if settings.OPENAI_API_KEY:
                answer = rag_with_llm(question, retrieved_docs)
            else:
                # OpenAI 키가 없으면 RAG만 사용
                answer = rag_answer(question, retrieved_docs)

        else:  # mode == "rag_local"
            # RAG + 로컬 LLM (backend.llm)
            results = search_similar(conn, question, top_k=request.top_k)
            retrieved_docs = [content for content, _ in results]

            llm = get_llm()
            if not llm.is_loaded():
                llm.load()
            answer = rag_with_local_llm(question, retrieved_docs, llm)

        return ChatResponse(
            answer=answer, retrieved_docs=retrieved_docs, mode=mode, top_k=request.top_k
        )
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        print(f"[FastAPI] /chat 오류: {exc}", flush=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(exc)}")


@router.post("/chat/qlora", response_model=QLoRAResponse)
async def qlora_chat_endpoint(
    request: QLoRARequest,
    qlora_service=Depends(get_qlora_service),
) -> QLoRAResponse:
    """QLoRA 모델을 사용한 채팅 엔드포인트.

    LoRA 어댑터가 적용된 모델을 사용하여 텍스트를 생성합니다.
    """
    try:
        prompt = request.prompt.strip()
        if not prompt:
            raise HTTPException(status_code=400, detail="프롬프트가 비어있습니다.")

        # 모델이 로드되지 않았으면 로드
        if not qlora_service.is_loaded():
            qlora_service.load()

        # 텍스트 생성
        response_text = qlora_service.generate(
            prompt=prompt,
            max_new_tokens=request.max_new_tokens,
            temperature=request.temperature,
            top_p=request.top_p,
        )

        return QLoRAResponse(response=response_text)

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        print(f"[FastAPI] /chat/qlora 오류: {exc}", flush=True)
        raise HTTPException(status_code=500, detail=f"서버 오류: {str(exc)}")

