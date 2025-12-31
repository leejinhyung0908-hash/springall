import os
import requests
import logging
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class KakaoMapSingleton:
    """카카오맵 API 싱글톤 클래스"""
    _instance = None  # 싱글톤 인스턴스를 저장할 클래스 변수

    def __new__(cls):
        if cls._instance is None:  # 인스턴스가 없으면 생성
            cls._instance = super(KakaoMapSingleton, cls).__new__(cls)
            cls._instance._api_key = cls._instance._retrieve_api_key()  # API 키 가져오기
            cls._instance._base_url = "https://dapi.kakao.com/v2/local"
        return cls._instance  # 기존 인스턴스 반환

    def _retrieve_api_key(self) -> str:
        """API 키를 환경 변수에서 가져오는 내부 메서드"""
        api_key = os.getenv("KAKAO_REST_API_KEY", "").strip()  # 공백 제거
        if not api_key:
            logger.warning("KAKAO_REST_API_KEY 환경 변수가 설정되지 않았습니다.")
        else:
            # API 키 앞 4자리만 로깅 (보안)
            logger.info(f"KAKAO_REST_API_KEY 로드 완료 (키 길이: {len(api_key)}, 앞 4자리: {api_key[:4]}...)")
        return api_key

    def get_api_key(self) -> str:
        """저장된 API 키 반환"""
        return self._api_key

    def _get_headers(self) -> Dict[str, str]:
        """API 요청 헤더 생성"""
        return {
            "Authorization": f"KakaoAK {self._api_key}"
        }

    def geocode(self, query: str, language: str = 'ko') -> List[Dict[str, Any]]:
        """
        주소 또는 장소명을 위도, 경도로 변환하는 메서드 (키워드 검색)
        
        Args:
            query: 검색할 주소 또는 장소명
            language: 응답 언어 (기본값: 'ko')
        
        Returns:
            검색 결과 리스트 (Google Maps API와 유사한 형식으로 변환)
        """
        if not self._api_key:
            raise ValueError("KAKAO_REST_API_KEY가 설정되지 않았습니다.")
        
        url = f"{self._base_url}/search/keyword.json"
        params = {
            "query": query,
            "size": 1  # 첫 번째 결과만
        }
        
        try:
            headers = self._get_headers()
            # 디버깅: 헤더 확인 (API 키는 마스킹)
            logger.info(f"카카오맵 API 요청: {url}?query={query}")
            logger.info(f"API 키 길이: {len(self._api_key)}, 앞 4자리: {self._api_key[:4]}...")
            
            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=5
            )
            
            # 403 에러인 경우 상세 정보 로깅
            if response.status_code == 403:
                logger.error(f"403 Forbidden 에러 발생!")
                logger.error(f"요청 URL: {url}")
                logger.error(f"요청 파라미터: {params}")
                logger.error(f"응답 본문: {response.text}")
                try:
                    error_json = response.json()
                    logger.error(f"에러 상세: {error_json}")
                except:
                    pass
            
            response.raise_for_status()
            
            data = response.json()
            
            # Google Maps API 형식과 유사하게 변환
            if data.get("documents") and len(data["documents"]) > 0:
                doc = data["documents"][0]
                return [{
                    "formatted_address": doc.get("address_name", "") or doc.get("place_name", ""),
                    "geometry": {
                        "location": {
                            "lat": float(doc.get("y", 0)),  # 카카오는 y가 위도
                            "lng": float(doc.get("x", 0))   # 카카오는 x가 경도
                        }
                    },
                    "place_name": doc.get("place_name", ""),
                    "address_name": doc.get("address_name", ""),
                    "road_address_name": doc.get("road_address_name", "")
                }]
            else:
                logger.warning(f"'{query}'에 대한 검색 결과가 없습니다.")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"카카오맵 API 요청 실패: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"카카오맵 지오코딩 오류: {str(e)}")
            raise

    def geocode_address(self, address: str) -> List[Dict[str, Any]]:
        """
        주소를 위도, 경도로 변환하는 메서드 (주소 검색)
        
        Args:
            address: 검색할 주소
        
        Returns:
            검색 결과 리스트
        """
        if not self._api_key:
            raise ValueError("KAKAO_REST_API_KEY가 설정되지 않았습니다.")
        
        url = f"{self._base_url}/search/address.json"
        params = {
            "query": address
        }
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                params=params,
                timeout=5
            )
            response.raise_for_status()
            
            data = response.json()
            
            # Google Maps API 형식과 유사하게 변환
            if data.get("documents") and len(data["documents"]) > 0:
                doc = data["documents"][0]
                return [{
                    "formatted_address": doc.get("address_name", ""),
                    "geometry": {
                        "location": {
                            "lat": float(doc.get("y", 0)),  # 카카오는 y가 위도
                            "lng": float(doc.get("x", 0))   # 카카오는 x가 경도
                        }
                    },
                    "address_name": doc.get("address_name", ""),
                    "road_address_name": doc.get("road_address_name", "")
                }]
            else:
                logger.warning(f"'{address}'에 대한 주소 검색 결과가 없습니다.")
                return []
                
        except requests.exceptions.RequestException as e:
            logger.error(f"카카오맵 API 요청 실패: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"카카오맵 주소 검색 오류: {str(e)}")
            raise

