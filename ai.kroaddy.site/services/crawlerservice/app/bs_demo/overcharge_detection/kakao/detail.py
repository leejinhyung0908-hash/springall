# bs_demo/kakao/detail.py
"""
카카오맵에서 장소 상세 정보 및 메뉴 가격 추출
"""
from typing import Dict
import logging
from .search_kakao import fetch_kakao_place_detail

logger = logging.getLogger(__name__)


def fetch_place_detail(kakao_place_id: str) -> Dict:
    """
    카카오 place 상세 정보 및 메뉴 정보 추출
    
    Args:
        kakao_place_id: 카카오 place ID
    
    Returns:
        {
            "kakao_place_id": str,
            "menus": List[Dict]  # [{"name": str, "price": int}]
        }
    """
    try:
        result = fetch_kakao_place_detail(kakao_place_id)
        
        logger.info(f"카카오 place 상세 정보 추출 완료: {kakao_place_id} -> {len(result.get('menus', []))}개 메뉴")
        
        return {
            "kakao_place_id": kakao_place_id,
            "menus": result.get("menus", [])
        }
        
    except Exception as e:
        logger.error(f"카카오 place 상세 정보 처리 중 오류 ({kakao_place_id}): {e}")
        return {
            "kakao_place_id": kakao_place_id,
            "menus": []
        }

