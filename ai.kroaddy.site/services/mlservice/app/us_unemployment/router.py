"""
미국 실업률 데이터 시각화 관련 라우터
"""
from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import HTMLResponse, FileResponse
from typing import List, Dict, Any, Optional
from pathlib import Path
import sys
import os

# 공통 모듈 경로 추가
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from app.us_unemployment.service import USUnemploymentService
import logging

# common.utils가 없을 경우를 대비한 fallback
try:
    from common.utils import create_response, create_error_response
except ImportError:
    # common.utils가 없을 경우 기본 함수 사용
    def create_response(data: Any, message: str = "Success"):
        return {"status": "success", "message": message, "data": data}
    
    def create_error_response(message: str, status_code: int = 400):
        return {"status": "error", "message": message}

logger = logging.getLogger(__name__)

router = APIRouter(tags=["usa"])

# 서비스 인스턴스 생성 (싱글톤 패턴)
_service_instance: Optional[USUnemploymentService] = None


def get_service() -> USUnemploymentService:
    """USUnemploymentService 싱글톤 인스턴스 반환"""
    global _service_instance
    if _service_instance is None:
        _service_instance = USUnemploymentService()
    return _service_instance


@router.get("/")
async def usa_root():
    """미국 실업률 데이터 서비스 루트"""
    return create_response(
        data={
            "service": "mlservice",
            "module": "us_unemployment",
            "status": "running",
            "endpoints": {
                "map": "/api/ml/usa/map",
                "data": "/api/ml/usa/data"
            }
        },
        message="US Unemployment Service is running"
    )


@router.get("/data")
async def get_unemployment_data():
    """
    미국 실업률 데이터 조회
    - GeoJSON 및 실업률 데이터를 로드하여 반환
    """
    try:
        service = get_service()
        service.load_data()
        
        # 데이터 요약 정보 반환
        data_summary = {
            "states_count": len(service.state_data) if service.state_data is not None else 0,
            "columns": service.state_data.columns.tolist() if service.state_data is not None else [],
            "sample_data": service.state_data.head(10).to_dict(orient="records") if service.state_data is not None else []
        }
        
        return create_response(
            data=data_summary,
            message="미국 실업률 데이터를 성공적으로 로드했습니다"
        )
    except Exception as e:
        logger.error(f"데이터 로드 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"데이터 로드 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/map")
async def create_unemployment_map(
    fill_color: str = Query("YlGn", description="색상맵 (예: YlGn, YlOrRd, RdPu)"),
    fill_opacity: float = Query(0.7, ge=0.0, le=1.0, description="채우기 투명도"),
    line_opacity: float = Query(0.2, ge=0.0, le=1.0, description="테두리 투명도"),
    save: bool = Query(False, description="HTML 파일로 저장 여부")
):
    """
    미국 실업률 Choropleth 맵 생성
    
    Args:
        fill_color: 색상맵 (기본값: "YlGn")
        fill_opacity: 채우기 투명도 (0.0 ~ 1.0, 기본값: 0.7)
        line_opacity: 테두리 투명도 (0.0 ~ 1.0, 기본값: 0.2)
        save: HTML 파일로 저장 여부 (기본값: False)
    
    Returns:
        HTML 응답 또는 저장된 파일 경로
    """
    try:
        service = get_service()
        service.load_data()
        map_obj = service.create_map(
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            line_opacity=line_opacity
        )
        
        if save:
            # 저장 디렉토리 확인
            save_dir = Path(__file__).parent.parent / "save"
            save_dir.mkdir(exist_ok=True)
            output_path = save_dir / "us_unemployment_map.html"
            
            service.save_map(str(output_path))
            
            return create_response(
                data={"file_path": str(output_path)},
                message="지도가 성공적으로 저장되었습니다"
            )
        else:
            # 임시 파일로 저장 후 HTML 반환
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as tmp_file:
                map_obj.save(tmp_file.name)
                with open(tmp_file.name, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                os.unlink(tmp_file.name)  # 임시 파일 삭제
            
            return HTMLResponse(content=html_content)
            
    except Exception as e:
        logger.error(f"지도 생성 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"지도 생성 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/map/download")
async def download_map(
    fill_color: str = Query("YlGn", description="색상맵"),
    fill_opacity: float = Query(0.7, ge=0.0, le=1.0, description="채우기 투명도"),
    line_opacity: float = Query(0.2, ge=0.0, le=1.0, description="테두리 투명도")
):
    """
    미국 실업률 지도를 HTML 파일로 다운로드
    
    Args:
        fill_color: 색상맵 (기본값: "YlGn")
        fill_opacity: 채우기 투명도 (기본값: 0.7)
        line_opacity: 테두리 투명도 (기본값: 0.2)
    
    Returns:
        HTML 파일 다운로드
    """
    try:
        service = get_service()
        service.load_data()
        map_obj = service.create_map(
            fill_color=fill_color,
            fill_opacity=fill_opacity,
            line_opacity=line_opacity
        )
        
        # 저장 디렉토리 확인
        save_dir = Path(__file__).parent.parent / "save"
        save_dir.mkdir(exist_ok=True)
        output_path = save_dir / "us_unemployment_map.html"
        
        service.save_map(str(output_path))
        
        return FileResponse(
            path=str(output_path),
            filename="us_unemployment_map.html",
            media_type="text/html"
        )
        
    except Exception as e:
        logger.error(f"지도 다운로드 실패: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"지도 다운로드 중 오류가 발생했습니다: {str(e)}"
        )

