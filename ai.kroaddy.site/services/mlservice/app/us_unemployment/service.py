"""
미국 실업률 데이터 시각화 서비스
Folium을 사용하여 미국 주별 실업률을 Choropleth 맵으로 시각화합니다.
"""
import requests
import pandas as pd
import folium
from typing import Optional, Dict, Any
import logging

# 로깅 설정
logger = logging.getLogger("us_unemployment_service")
if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    )
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


class USUnemploymentService:
    """미국 실업률 데이터 시각화 서비스 클래스"""
    
    # 기본 URL 설정
    GEO_JSON_URL = "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_states.json"
    UNEMPLOYMENT_DATA_URL = "https://raw.githubusercontent.com/python-visualization/folium-example-data/main/us_unemployment_oct_2012.csv"
    
    # 지도 기본 설정
    DEFAULT_LOCATION = [48, -102]  # 미국 중심 좌표
    DEFAULT_ZOOM_START = 3
    
    def __init__(
        self,
        geo_json_url: Optional[str] = None,
        data_url: Optional[str] = None,
        location: Optional[list] = None,
        zoom_start: Optional[int] = None
    ):
        """
        서비스 초기화
        
        Args:
            geo_json_url: GeoJSON 데이터 URL (기본값 사용 시 None)
            data_url: 실업률 데이터 CSV URL (기본값 사용 시 None)
            location: 지도 중심 좌표 [위도, 경도] (기본값 사용 시 None)
            zoom_start: 지도 초기 줌 레벨 (기본값 사용 시 None)
        """
        self.geo_json_url = geo_json_url or self.GEO_JSON_URL
        self.data_url = data_url or self.UNEMPLOYMENT_DATA_URL
        self.location = location or self.DEFAULT_LOCATION
        self.zoom_start = zoom_start or self.DEFAULT_ZOOM_START
        
        # 데이터 저장용
        self.state_geo: Optional[Dict[str, Any]] = None
        self.state_data: Optional[pd.DataFrame] = None
        self.map: Optional[folium.Map] = None
        
        logger.info("USUnemploymentService 초기화 완료")
    
    def load_geo_data(self) -> Dict[str, Any]:
        """
        GeoJSON 데이터를 로드합니다.
        
        Returns:
            GeoJSON 데이터 딕셔너리
            
        Raises:
            requests.RequestException: 데이터 로드 실패 시
        """
        try:
            logger.info(f"GeoJSON 데이터 로드 중: {self.geo_json_url}")
            response = requests.get(self.geo_json_url)
            response.raise_for_status()
            self.state_geo = response.json()
            logger.info("GeoJSON 데이터 로드 완료")
            return self.state_geo
        except requests.RequestException as e:
            logger.error(f"GeoJSON 데이터 로드 실패: {str(e)}")
            raise
    
    def load_unemployment_data(self) -> pd.DataFrame:
        """
        실업률 데이터를 로드합니다.
        
        Returns:
            실업률 데이터 DataFrame
            
        Raises:
            Exception: 데이터 로드 실패 시
        """
        try:
            logger.info(f"실업률 데이터 로드 중: {self.data_url}")
            self.state_data = pd.read_csv(self.data_url)
            logger.info(f"실업률 데이터 로드 완료: {len(self.state_data)}개 주")
            return self.state_data
        except Exception as e:
            logger.error(f"실업률 데이터 로드 실패: {str(e)}")
            raise
    
    def load_data(self) -> None:
        """
        모든 데이터를 로드합니다.
        """
        self.load_geo_data()
        self.load_unemployment_data()
    
    def create_map(
        self,
        fill_color: str = "YlGn",
        fill_opacity: float = 0.7,
        line_opacity: float = 0.2,
        legend_name: str = "Unemployment Rate (%)",
        add_layer_control: bool = True
    ) -> folium.Map:
        """
        Choropleth 맵을 생성합니다.
        
        Args:
            fill_color: 색상맵 (기본값: "YlGn")
            fill_opacity: 채우기 투명도 (기본값: 0.7)
            line_opacity: 테두리 투명도 (기본값: 0.2)
            legend_name: 범례 이름 (기본값: "Unemployment Rate (%)")
            add_layer_control: 레이어 컨트롤 추가 여부 (기본값: True)
            
        Returns:
            생성된 Folium Map 객체
            
        Raises:
            ValueError: 데이터가 로드되지 않은 경우
        """
        if self.state_geo is None or self.state_data is None:
            logger.warning("데이터가 로드되지 않았습니다. 자동으로 로드합니다.")
            self.load_data()
        
        logger.info("Choropleth 맵 생성 중...")
        
        # 지도 생성
        self.map = folium.Map(
            location=self.location,
            zoom_start=self.zoom_start
        )
        
        # Choropleth 레이어 추가
        folium.Choropleth(
            geo_data=self.state_geo,
            name="choropleth",
            data=self.state_data,
            columns=["State", "Unemployment"],
            key_on="feature.id",
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            line_opacity=line_opacity,
            legend_name=legend_name,
        ).add_to(self.map)
        
        # 레이어 컨트롤 추가
        if add_layer_control:
            folium.LayerControl().add_to(self.map)
        
        logger.info("Choropleth 맵 생성 완료")
        return self.map
    
    def save_map(self, output_path: str) -> None:
        """
        지도를 HTML 파일로 저장합니다.
        
        Args:
            output_path: 저장할 파일 경로
            
        Raises:
            ValueError: 지도가 생성되지 않은 경우
        """
        if self.map is None:
            raise ValueError("지도가 생성되지 않았습니다. create_map()을 먼저 호출하세요.")
        
        logger.info(f"지도 저장 중: {output_path}")
        self.map.save(output_path)
        logger.info(f"지도 저장 완료: {output_path}")
    
    def get_map(self) -> Optional[folium.Map]:
        """
        생성된 지도 객체를 반환합니다.
        
        Returns:
            Folium Map 객체 (생성되지 않은 경우 None)
        """
        return self.map


# 사용 예제
if __name__ == "__main__":
    from pathlib import Path
    
    # 서비스 인스턴스 생성
    service = USUnemploymentService()
    
    # 데이터 로드 및 지도 생성
    print("데이터 로딩 중...")
    service.load_data()
    
    print("지도 생성 중...")
    map_obj = service.create_map()
    
    # HTML 파일로 저장
    script_dir = Path(__file__).parent
    output_path = script_dir / "us_unemployment_map.html"
    service.save_map(str(output_path))
    
    print(f"\n지도가 저장되었습니다: {output_path}")
    print(f"파일 경로: {output_path.absolute()}")