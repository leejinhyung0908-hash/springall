"""
NLP 관련 라우터
Emma 워드클라우드, Samsung 워드클라우드, KoELECTRA 감성 분석
"""
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Query, Body, Depends
from pydantic import BaseModel, Field

# 서비스 Import
from .emma.emma_wordcloud import EmmaWordCloudService
from .samsung.samsung_wordcloud import SamsungWordCloudService
from .review.emotion_inference import EmotionInference, SentimentResult

# 공통 유틸리티 함수
try:
    from common.utils import create_response, create_error_response
except ImportError:
    # common.utils가 없을 경우 기본 함수 사용
    def create_response(data: Any, message: str = "Success"):
        return {"status": "success", "message": message, "data": data}
    
    def create_error_response(message: str, status_code: int = 400):
        return {"status": "error", "message": message}

logger = logging.getLogger(__name__)

router = APIRouter(tags=["nlp"])

# 서비스 인스턴스 생성 (싱글톤 패턴)
_emma_service_instance: Optional[EmmaWordCloudService] = None
_samsung_service_instance: Optional[SamsungWordCloudService] = None
_emotion_inference_instance: Optional[EmotionInference] = None


def get_emma_service() -> EmmaWordCloudService:
    """EmmaWordCloudService 싱글톤 인스턴스 반환"""
    global _emma_service_instance
    if _emma_service_instance is None:
        _emma_service_instance = EmmaWordCloudService()
    return _emma_service_instance


def get_samsung_service() -> SamsungWordCloudService:
    """SamsungWordCloudService 싱글톤 인스턴스 반환"""
    global _samsung_service_instance
    if _samsung_service_instance is None:
        _samsung_service_instance = SamsungWordCloudService()
    return _samsung_service_instance


def get_emotion_inference_service() -> EmotionInference:
    """EmotionInference 싱글톤 인스턴스 반환 및 로드 체크"""
    global _emotion_inference_instance
    if _emotion_inference_instance is None:
        try:
            _emotion_inference_instance = EmotionInference()
        except Exception as e:
            logger.error(f"KoELECTRA 모델 로드 실패: {e}")
            raise HTTPException(status_code=503, detail="KoELECTRA Sentiment Model is not available.")
    # 로드 성공했으나 내부적으로 에러 상태일 경우도 체크 (예: self.model이 None인 경우)
    if _emotion_inference_instance.model is None:
        raise HTTPException(status_code=503, detail="KoELECTRA Sentiment Model is not fully initialized.")
    return _emotion_inference_instance


# ---------------------------------------------------
# KoELECTRA 감성 분석 API 엔드포인트
# ---------------------------------------------------

class SentimentRequest(BaseModel):
    text: str = Field(..., description="감성 분석을 수행할 한국어 문장", example="정말 재미있는 영화였어요. 배우들 연기가 최고예요!")


@router.post("/sentiment", response_model=Dict[str, Any])
async def analyze_sentiment(
    request: SentimentRequest,
    engine: EmotionInference = Depends(get_emotion_inference_service)
):
    """
    KoELECTRA 모델을 사용하여 입력된 한국어 문장의 감성을 분석합니다.
    (긍정: 1, 부정: 0)
    """
    try:
        # engine.classify() 호출
        result = engine.classify(request.text)
        
        # SentimentResult(dataclass)를 반환하므로, 이를 create_response에 전달
        return create_response(
            data=result,
            message="감성 분석을 성공적으로 완료했습니다."
        )
        
    except HTTPException:
        # HTTPException은 여기서 다시 발생시켜 FastAPI가 처리하도록 함
        raise
    except Exception as e:
        logger.error(f"감성 분석 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"감성 분석 처리 중 오류가 발생했습니다: {str(e)}"
        )


# ---------------------------------------------------
# Emma 워드클라우드 API 엔드포인트
# ---------------------------------------------------

@router.get("/")
async def nlp_root():
    """NLP 서비스 루트"""
    return create_response(
        data={"service": "mlservice", "module": "nlp", "status": "running"},
        message="NLP Service is running"
    )


@router.post("/emma")
async def create_emma_wordcloud(
    text_length: Optional[int] = Body(None, description="텍스트 길이 제한"),
    stopwords: Optional[list] = Body(None, description="제외할 불용어 리스트"),
    width: int = Body(1000, description="워드클라우드 너비"),
    height: int = Body(600, description="워드클라우드 높이"),
    background_color: str = Body("white", description="배경색"),
    return_image: bool = Body(True, description="이미지 반환 여부"),
    service: EmmaWordCloudService = Depends(get_emma_service)
):
    """Emma 소설 워드클라우드 생성"""
    try:
        result = service.process_emma_full(
            text_length=text_length,
            stopwords=stopwords,
            width=width,
            height=height,
            background_color=background_color
        )
        
        if not return_image:
            result.pop("wordcloud", None)
        
        return create_response(
            data=result,
            message="Emma 소설 처리 및 워드클라우드 생성 완료"
        )
    except Exception as e:
        logger.error(f"Emma 워드클라우드 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"워드클라우드 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/emma/wordcloud")
async def get_emma_wordcloud_image(
    width: int = Query(1000, description="워드클라우드 너비"),
    height: int = Query(600, description="워드클라우드 높이"),
    background_color: str = Query("white", description="배경색"),
    text_length: Optional[int] = Query(None, description="텍스트 길이 제한"),
    service: EmmaWordCloudService = Depends(get_emma_service)
):
    """Emma 워드클라우드 이미지 반환 (PNG)"""
    try:
        from fastapi.responses import Response
        import base64
        
        result = service.process_emma_full(
            text_length=text_length,
            width=width,
            height=height,
            background_color=background_color
        )
        
        image_base64 = result.get("wordcloud", {}).get("image_base64", "")
        if not image_base64:
            raise HTTPException(status_code=500, detail="워드클라우드 이미지를 생성할 수 없습니다.")
        
        image_bytes = base64.b64decode(image_base64)
        return Response(content=image_bytes, media_type="image/png")
    except Exception as e:
        logger.error(f"Emma 워드클라우드 이미지 반환 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"워드클라우드 이미지 반환 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/emma/stats")
async def get_emma_stats(
    text_length: Optional[int] = Query(None, description="텍스트 길이 제한"),
    service: EmmaWordCloudService = Depends(get_emma_service)
):
    """Emma 빈도 분포 통계 조회"""
    try:
        emma_raw = service.load_emma_text(text_length)
        tokens = service.tokenize_text(emma_raw, method="regex")
        text_obj = service.create_text_object(tokens)
        proper_nouns = service.extract_proper_nouns(tokens)
        freq_dist = service.get_freq_dist(proper_nouns)
        stats = service.get_freq_stats(freq_dist)
        
        return create_response(
            data=stats,
            message="Emma 통계 조회 완료"
        )
    except Exception as e:
        logger.error(f"Emma 통계 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"통계 조회 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/emma/text")
async def get_emma_text(
    length: Optional[int] = Query(None, description="반환할 문자 수"),
    service: EmmaWordCloudService = Depends(get_emma_service)
):
    """Emma 원문 조회"""
    try:
        text = service.load_emma_text(length)
        return create_response(
            data={"text": text, "length": len(text)},
            message="Emma 원문 조회 완료"
        )
    except Exception as e:
        logger.error(f"Emma 원문 조회 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"원문 조회 중 오류가 발생했습니다: {str(e)}"
        )


# ---------------------------------------------------
# Samsung 워드클라우드 API 엔드포인트
# ---------------------------------------------------

@router.post("/samsung")
async def create_samsung_wordcloud(
    file_path: Optional[str] = Body(None, description="텍스트 파일 경로"),
    stopwords: Optional[list] = Body(None, description="제외할 불용어 리스트"),
    width: int = Body(1000, description="워드클라우드 너비"),
    height: int = Body(600, description="워드클라우드 높이"),
    background_color: str = Body("white", description="배경색"),
    return_image: bool = Body(True, description="이미지 반환 여부"),
    service: SamsungWordCloudService = Depends(get_samsung_service)
):
    """Samsung 워드클라우드 생성"""
    try:
        result = service.process_samsung_full(
            file_path=file_path,
            stopwords=stopwords,
            width=width,
            height=height,
            background_color=background_color
        )
        
        if not return_image:
            result.pop("wordcloud", None)
        
        return create_response(
            data=result,
            message="Samsung 워드클라우드 생성 완료"
        )
    except Exception as e:
        logger.error(f"Samsung 워드클라우드 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"워드클라우드 생성 중 오류가 발생했습니다: {str(e)}"
        )
