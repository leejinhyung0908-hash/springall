# bs_demo/overcharge_detection/kakao/router.py
"""
카카오맵 크롤링 API 라우터
"""
import logging
from typing import List, Dict, Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from .search_kakao import search_kakao_places, fetch_kakao_place_detail

logger = logging.getLogger(__name__)

# 카카오 전용 prefix
router = APIRouter(prefix="/kakao", tags=["카카오 지도 크롤링"])


class PlaceSearchRequest(BaseModel):
    place_name: str = Field(..., description="검색할 장소 이름", example="강남역 맛집")
    lat: Optional[float] = Field(None, description="위도 (선택사항)")
    lng: Optional[float] = Field(None, description="경도 (선택사항)")
    limit: int = Field(5, description="최대 검색 결과 개수", ge=1, le=20)


@router.get("/search", response_model=Dict)
async def kakao_search(
    place_name: str = Query(..., description="검색할 장소 이름", example="강남역 맛집"),
    lat: Optional[float] = Query(None, description="위도"),
    lng: Optional[float] = Query(None, description="경도"),
    radius: int = Query(1000, description="검색 반경(m)", ge=1, le=20000),
    limit: int = Query(5, description="최대 검색 결과 개수", ge=1, le=15),
):
    """카카오 로컬 검색 API로 place 목록 조회"""
    try:
        results = search_kakao_places(place_name, lat=lat, lng=lng, radius=radius, size=limit)
        return {"success": True, "data": results, "count": len(results)}
    except Exception as e:
        logger.error(f"카카오 검색 실패: {e}")
        raise HTTPException(status_code=500, detail=f"카카오 검색 중 오류: {str(e)}")


@router.get("/crawl/{place_id}", response_model=Dict)
async def kakao_crawl_by_id(place_id: str):
    """카카오 place_id로 기본정보+메뉴 추출"""
    try:
        result = fetch_kakao_place_detail(place_id)
        if not result:
            raise HTTPException(status_code=404, detail="장소를 찾을 수 없습니다.")
        return {"success": True, "data": result, "menu_count": len(result.get("menus", []))}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"카카오 크롤링 실패 ({place_id}): {e}")
        raise HTTPException(status_code=500, detail=f"카카오 크롤링 중 오류: {str(e)}")


@router.post("/crawl", response_model=Dict)
async def kakao_crawl_by_name(request: PlaceSearchRequest):
    """카카오에서 키워드 검색 후 첫 결과의 메뉴/가격까지 추출"""
    try:
        places = search_kakao_places(
            request.place_name,
            lat=request.lat,
            lng=request.lng,
            size=request.limit,
        )
        if not places:
            return {"success": True, "data": [], "count": 0}

        target = places[0]
        place_id = target.get("kakao_place_id")
        if not place_id:
            return {"success": True, "data": [], "count": 0}

        detail = fetch_kakao_place_detail(place_id)
        merged = {**target, **detail, "menus": detail.get("menus", [])}
        return {"success": True, "data": merged, "menu_count": len(merged.get("menus", []))}
    except Exception as e:
        logger.error(f"카카오 통합 크롤링 실패: {e}")
        raise HTTPException(status_code=500, detail=f"카카오 크롤링 중 오류: {str(e)}")


@router.get("/menu/{place_id}", response_model=Dict)
async def kakao_menu_only(place_id: str):
    """카카오 place_id로 메뉴만 추출"""
    try:
        detail = fetch_kakao_place_detail(place_id)
        return {
            "success": True,
            "data": {"kakao_place_id": place_id, "menus": detail.get("menus", [])},
            "menu_count": len(detail.get("menus", [])),
        }
    except Exception as e:
        logger.error(f"카카오 메뉴 추출 실패 ({place_id}): {e}")
        raise HTTPException(status_code=500, detail=f"카카오 메뉴 추출 중 오류: {str(e)}")

