"""
RAG Service - FastAPI 애플리케이션
"""
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from langchain.schema import Document
from app.rag_engine import RAGEngine
from app.vector_store import VectorStore
import logging
import os

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Service", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# RAG 엔진 초기화
logger.info("RAG 엔진 초기화 중...")
try:
    rag_engine = RAGEngine()
    vector_store = VectorStore()
    logger.info("RAG 엔진 초기화 완료")
except Exception as e:
    logger.error(f"RAG 엔진 초기화 실패: {e}")
    rag_engine = None
    vector_store = None

# ============================================================================
# 요청/응답 모델
# ============================================================================

class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[dict]

class SearchRequest(BaseModel):
    query: str
    top_k: Optional[int] = None

class SearchResponse(BaseModel):
    results: List[dict]

class DocumentRequest(BaseModel):
    text: str
    metadata: Optional[dict] = None

class DocumentResponse(BaseModel):
    message: str
    document_count: int

# ============================================================================
# API 엔드포인트
# ============================================================================

@app.get("/")
async def root():
    """서비스 상태 확인"""
    return {
        "service": "RAG Service",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "rag_engine_ready": rag_engine is not None,
        "vector_store_ready": vector_store is not None
    }

@app.post("/query", response_model=QueryResponse)
async def query(request: QueryRequest):
    """질문에 대한 답변 생성 (RAG)"""
    if rag_engine is None:
        raise HTTPException(status_code=503, detail="RAG 엔진이 초기화되지 않았습니다.")
    
    try:
        logger.info(f"질문 수신: {request.question}")
        result = rag_engine.query(request.question)
        logger.info(f"답변 생성 완료")
        return QueryResponse(**result)
    except Exception as e:
        logger.error(f"질문 처리 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search", response_model=SearchResponse)
async def search(request: SearchRequest):
    """문서 검색 (생성 없음)"""
    if vector_store is None:
        raise HTTPException(status_code=503, detail="벡터 저장소가 초기화되지 않았습니다.")
    
    try:
        logger.info(f"검색 쿼리: {request.query}")
        results = rag_engine.search_only(request.query, k=request.top_k)
        logger.info(f"검색 결과: {len(results)}개")
        return SearchResponse(results=results)
    except Exception as e:
        logger.error(f"검색 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents", response_model=DocumentResponse)
async def add_document(request: DocumentRequest):
    """문서 추가"""
    if vector_store is None:
        raise HTTPException(status_code=503, detail="벡터 저장소가 초기화되지 않았습니다.")
    
    try:
        logger.info(f"문서 추가: {len(request.text)}자")
        document = Document(
            page_content=request.text,
            metadata=request.metadata or {}
        )
        vector_store.add_documents([document])
        logger.info("문서 추가 완료")
        return DocumentResponse(
            message="문서가 성공적으로 추가되었습니다.",
            document_count=1
        )
    except Exception as e:
        logger.error(f"문서 추가 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/batch", response_model=DocumentResponse)
async def add_documents_batch(documents: List[DocumentRequest]):
    """여러 문서 일괄 추가"""
    if vector_store is None:
        raise HTTPException(status_code=503, detail="벡터 저장소가 초기화되지 않았습니다.")
    
    try:
        logger.info(f"일괄 문서 추가: {len(documents)}개")
        docs = [
            Document(
                page_content=doc.text,
                metadata=doc.metadata or {}
            )
            for doc in documents
        ]
        vector_store.add_documents(docs)
        logger.info(f"{len(documents)}개 문서 추가 완료")
        return DocumentResponse(
            message=f"{len(documents)}개 문서가 성공적으로 추가되었습니다.",
            document_count=len(documents)
        )
    except Exception as e:
        logger.error(f"문서 일괄 추가 실패: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    from app.config import HOST, PORT
    uvicorn.run(app, host=HOST, port=PORT)

