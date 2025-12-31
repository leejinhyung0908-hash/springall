"""
Titanic Service - FastAPI 애플리케이션
"""
import sys
import csv
import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# 공통 모듈 경로 추가 (최우선)
current_file = Path(__file__).resolve()
base_dir = current_file.parent.parent  # /app (Docker) 또는 mlservice (로컬)

# 경로 추가
base_path_str = str(base_dir)
if base_path_str not in sys.path:
    sys.path.insert(0, base_path_str)

# Docker 환경 확인 및 /app 경로 추가
if os.path.exists("/app"):
    if "/app" not in sys.path:
        sys.path.insert(0, "/app")

# 라우터 import (경로 설정 후)
try:
    from app.seoul_crime.seoul_router import router as seoul_router
except ImportError as e:
    seoul_router = None
    import traceback
    print(f"Warning: seoul_router import failed: {e}")
    traceback.print_exc()

try:
    from app.us_unemployment.router import router as usa_router
except ImportError as e:
    usa_router = None
    import traceback
    print(f"Warning: usa_router import failed: {e}")
    traceback.print_exc()

try:
    from app.nltk.nltk_router import router as nltk_router
except ImportError as e:
    nltk_router = None
    import traceback
    print(f"Warning: nltk_router import failed: {e}")
    traceback.print_exc()

try:
    from app.nlp.nlp_router import router as nlp_router
except ImportError as e:
    nlp_router = None
    import traceback
    print(f"Warning: nlp_router import failed: {e}")
    traceback.print_exc()

# 설정 로드 (경로 설정 후)
try:
    from app.config import TitanicServiceConfig
    config = TitanicServiceConfig()
except Exception as e:
    # config.py를 찾을 수 없는 경우 기본값 사용
    class Config:
        service_name = "mlservice"
        service_version = "1.0.0"
        port = 9010
    config = Config()

# 라우터 및 공통 모듈 import
LoggingMiddleware = None
try:
    from app.titanic.titanic_router import router as titanic_router
    from common.middleware import LoggingMiddleware
    from common.utils import setup_logging
except ImportError as e:
    # 모듈을 찾을 수 없는 경우 기본값 사용
    from fastapi import APIRouter
    titanic_router = APIRouter()
    def setup_logging(name):
        import logging
        return logging.getLogger(name)

# 로깅 설정
logger = setup_logging(config.service_name)

# FastAPI 앱 생성
app = FastAPI(
    title="Titanic Service API",
    description="""
    ## 타이타닉 데이터 서비스 API
    
    머신러닝을 활용한 타이타닉 승객 데이터 분석 및 생존 예측 서비스입니다.
    
    ### 주요 기능
    - 승객 데이터 조회 및 통계 분석
    - 머신러닝 모델 훈련 (Random Forest)
    - 승객 생존 예측
    - 배치 예측 지원
    
    ### 기술 스택
    - **Framework**: FastAPI
    - **ML Library**: scikit-learn, pandas, numpy
    - **Model**: Random Forest Classifier
    
    ### API 문서
    - Swagger UI: `/docs`
    - ReDoc: `/redoc`
    - OpenAPI Schema: `/openapi.json`
    """,
    version=config.service_version,
    contact={
        "name": "ML Service Team",
        "email": "support@labzang.com",
    },
    license_info={
        "name": "MIT",
    },
    tags_metadata=[
        {
            "name": "titanic",
            "description": "타이타닉 승객 데이터 관련 API",
        },
        {
            "name": "seoul",
            "description": "서울시 범죄 데이터 관련 API - CCTV, 범죄, 인구 데이터 분석",
        },
        {
            "name": "usa",
            "description": "미국 실업률 데이터 시각화 API - Choropleth 맵 생성",
        },
        {
            "name": "nlp",
            "description": "NLP 자연어 처리 API - Emma 워드클라우드 생성",
        },
        {
            "name": "nltk",
            "description": "NLTK 자연어 처리 API - 토큰화, 형태소 분석, 품사 태깅, 워드클라우드",
        },
        {
            "name": "nlp",
            "description": "NLP 자연어 처리 API - Emma 워드클라우드 생성",
        },
    ],
    openapi_tags=[
        {
            "name": "titanic",
            "description": "타이타닉 승객 데이터 및 머신러닝 예측 기능",
        },
        {
            "name": "seoul",
            "description": "서울시 범죄 데이터 분석 및 CCTV 분배 예측 기능",
        },
        {
            "name": "usa",
            "description": "미국 실업률 데이터 시각화 및 Choropleth 맵 생성 기능",
        },
        {
            "name": "nlp",
            "description": "NLP 자연어 처리 기능 - Emma 소설 워드클라우드 생성",
        },
        {
            "name": "nltk",
            "description": "NLTK 자연어 처리 기능 - 토큰화, 형태소 분석, 품사 태깅, 워드클라우드 생성",
        },
        {
            "name": "nlp",
            "description": "NLP 자연어 처리 기능 - Emma 소설 워드클라우드 생성",
        },
    ],
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 미들웨어 추가
if LoggingMiddleware is not None:
    app.add_middleware(LoggingMiddleware)

# 라우터 등록
# titanic_router는 이미 prefix="/titanic"이 있으므로 중복하지 않음
try:
    app.include_router(titanic_router)
    logger.info(f"✅ Titanic router 등록 완료: {len(titanic_router.routes)} 개의 엔드포인트")
except Exception as e:
    logger.error(f"❌ Titanic router 등록 실패: {e}")
    import traceback
    logger.error(traceback.format_exc())

if seoul_router is not None:
    try:
        app.include_router(seoul_router, prefix="/seoul")
        logger.info(f"✅ Seoul router 등록 완료: {len(seoul_router.routes)} 개의 엔드포인트")
    except Exception as e:
        logger.error(f"❌ Seoul router 등록 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
else:
    logger.warning("⚠️ Seoul router가 None입니다. 엔드포인트가 등록되지 않습니다.")

if usa_router is not None:
    try:
        # API Gateway가 /api/ml을 제거하므로 /usa만 사용
        app.include_router(usa_router, prefix="/usa")
        logger.info(f"✅ USA router 등록 완료: {len(usa_router.routes)} 개의 엔드포인트")
    except Exception as e:
        logger.error(f"❌ USA router 등록 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
else:
    logger.warning("⚠️ USA router가 None입니다. 엔드포인트가 등록되지 않습니다.")

if nltk_router is not None:
    try:
        # API Gateway가 /api/ml을 제거하므로 /nltk만 사용
        app.include_router(nltk_router, prefix="/nltk")
        logger.info(f"✅ NLTK router 등록 완료: {len(nltk_router.routes)} 개의 엔드포인트")
    except Exception as e:
        logger.error(f"❌ NLTK router 등록 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
else:
    logger.warning("⚠️ NLTK router가 None입니다. 엔드포인트가 등록되지 않습니다.")

if nlp_router is not None:
    try:
        # API Gateway가 /api/ml을 제거하므로 /nlp만 사용
        app.include_router(nlp_router, prefix="/nlp")
        logger.info(f"✅ NLP router 등록 완료: {len(nlp_router.routes)} 개의 엔드포인트")
    except Exception as e:
        logger.error(f"❌ NLP router 등록 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
else:
    logger.warning("⚠️ NLP router가 None입니다. 엔드포인트가 등록되지 않습니다.")

@app.get("/")
async def root():
    """루트 엔드포인트"""
    return {
        "service": config.service_name,
        "version": config.service_version,
        "message": "Titanic Service API"
    }



@app.on_event("startup")
async def startup_event():
    """서비스 시작 시 실행"""
    logger.info(f"{config.service_name} v{config.service_version} started")
    # 시작 시 상위 10명 출력


@app.on_event("shutdown")
async def shutdown_event():
    """서비스 종료 시 실행"""
    logger.info(f"{config.service_name} shutting down")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=config.port)

