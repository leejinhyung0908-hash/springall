# bs_demo/kakao/crawler.py
"""
카카오맵 API를 사용한 통합 크롤링 모듈
장소 검색부터 메뉴 가격 추출까지 처리
"""
from typing import List, Dict, Optional
import logging
from .search_kakao import search_kakao_places, fetch_kakao_place_detail

logger = logging.getLogger(__name__)


def crawl_place_with_menu(
    place_name: str,
    lat: Optional[float] = None,
    lng: Optional[float] = None,
    limit: int = 5,
    auto_select: bool = True
) -> List[Dict]:
    """
    장소 이름으로 검색하고 메뉴 정보까지 추출하는 통합 크롤링 함수
    
    Args:
        place_name: 검색할 장소 이름
        lat: 위도 (선택사항)
        lng: 경도 (선택사항)
        limit: 최대 검색 결과 개수
        auto_select: True면 첫 번째 결과 자동 선택, False면 모든 결과 반환
    
    Returns:
        장소 및 메뉴 정보 리스트 [{
            "kakao_place_id": str,
            "name": str,
            "address": str,
            "lat": float,
            "lng": float,
            "category": str,
            "phone": str,
            "menus": List[Dict]  # [{"name": str, "price": int}]
        }]
    """
    try:
        # 1. 장소 검색
        logger.info(f"카카오맵에서 '{place_name}' 검색 중...")
        places = search_kakao_places(place_name, lat=lat, lng=lng, size=limit)
        
        if not places:
            logger.warning(f"'{place_name}' 검색 결과 없음")
            return []
        
        # 2. auto_select가 True면 첫 번째 결과만 처리
        if auto_select:
            places = places[:1]
        
        # 3. 각 장소의 메뉴 정보 추출
        results = []
        for place in places:
            try:
                place_id = place.get("kakao_place_id")
                if not place_id:
                    continue
                
                logger.info(f"장소 상세 정보 및 메뉴 추출 중: {place.get('name')} ({place_id})")
                
                # 메뉴 정보 추출
                detail_data = fetch_kakao_place_detail(place_id)
                
                # 결과 통합
                result = {
                    **place,
                    "menus": detail_data.get("menus", [])
                }
                
                results.append(result)
                
                logger.info(f"완료: {place.get('name')} -> {len(result['menus'])}개 메뉴")
                
            except Exception as e:
                logger.error(f"장소 메뉴 추출 실패 ({place.get('name')}): {e}")
                # 메뉴 추출 실패해도 기본 정보는 포함
                results.append({
                    **place,
                    "menus": []
                })
        
        logger.info(f"크롤링 완료: {len(results)}개 장소 처리")
        return results
        
    except Exception as e:
        logger.error(f"크롤링 중 오류 발생: {e}")
        return []


def crawl_place_by_id(kakao_place_id: str) -> Optional[Dict]:
    """
    카카오 place ID로 직접 크롤링
    
    Args:
        kakao_place_id: 카카오 place ID
    
    Returns:
        장소 및 메뉴 정보 딕셔너리
    """
    try:
        # 메뉴 정보 추출
        detail_data = fetch_kakao_place_detail(kakao_place_id)
        
        logger.info(f"크롤링 완료: {kakao_place_id} -> {len(detail_data.get('menus', []))}개 메뉴")
        return detail_data
        
    except Exception as e:
        logger.error(f"크롤링 실패 ({kakao_place_id}): {e}")
        return None


def batch_crawl_places(place_names: List[str]) -> List[Dict]:
    """
    여러 장소를 일괄 크롤링
    
    Args:
        place_names: 장소 이름 리스트
    
    Returns:
        모든 장소의 크롤링 결과 리스트
    """
    all_results = []
    
    for place_name in place_names:
        try:
            results = crawl_place_with_menu(place_name, auto_select=True)
            all_results.extend(results)
        except Exception as e:
            logger.error(f"일괄 크롤링 중 오류 ({place_name}): {e}")
            continue
    
    logger.info(f"일괄 크롤링 완료: {len(all_results)}개 장소")
    return all_results

