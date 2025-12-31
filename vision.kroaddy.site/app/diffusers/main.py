# FastAPI 엔트리 + 정적 파일 서빙(/outputs/...) 
# + 라우팅 등록입니다.
import os

# OpenMP 중복 라이브러리 오류 해결
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from api.v1.routes.generate import router as generate_router
from core.config import OUTPUTS_DIR

app = FastAPI(title="Diffusers API", version="1.0.0")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 개발 환경에서는 모든 origin 허용 (프로덕션에서는 특정 origin만 허용)
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메서드 허용 (GET, POST, OPTIONS 등)
    allow_headers=["*"],  # 모든 헤더 허용
)

# outputs 디렉토리 자동 생성
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

# outputs 정적 서빙 (로컬 개발/단독 서버에서 편리)
app.mount("/outputs", StaticFiles(directory=str(OUTPUTS_DIR)), name="outputs")

app.include_router(generate_router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"ok": True}