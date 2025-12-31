"""
포트폴리오 파일을 app/data/yolo 폴더에 저장하고 얼굴 인식을 수행하는 FastAPI 서버
"""
import os
import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uvicorn
import cv2
import numpy as np
import base64
from io import BytesIO
from yolo_detection import detect_faces, image_to_base64, auto_detect_on_upload, apply_yolo_inference

app = FastAPI(title="Portfolio Upload API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용하도록 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 현재 스크립트의 위치 기준으로 상대 경로 설정
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
target_dir = project_root / 'app' / 'data' / 'yolo'
cascade_path = project_root / 'app' / 'data' / 'opencv' / 'haarcascade_frontalface_alt.xml'

# 대상 디렉토리가 없으면 생성
target_dir.mkdir(parents=True, exist_ok=True)


# detect 관련 함수는 yolo_detection.py에서 import


@app.post("/api/portfolio/detect")
async def detect_faces_api(
    image: UploadFile = File(..., description="얼굴 인식을 수행할 이미지 파일 (multipart/form-data)")
):
    """
    이미지에서 얼굴을 인식하고 detect된 이미지를 base64로 반환
    multipart/form-data 형식으로 이미지 파일을 받습니다.
    """
    try:
        # 임시 파일로 저장
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(image.filename)[1]) as tmp_file:
            shutil.copyfileobj(image.file, tmp_file)
            tmp_path = Path(tmp_file.name)
        
        try:
            # 얼굴 인식 수행
            detected_img, face_count, face_coords = detect_faces(tmp_path, cascade_path)
            
            if detected_img is not None and face_count > 0:
                # YOLO 추론 적용
                try:
                    current_dir = Path(__file__).parent
                    yolo_model_path = current_dir / 'data' / 'yolo11n.pt'
                    detected_img = apply_yolo_inference(detected_img, yolo_model_path)
                    print(f"✅ YOLO 추론 적용 완료")
                except Exception as e:
                    print(f"⚠️ YOLO 추론 적용 중 오류 (얼굴 인식 결과는 반환): {e}")
                
                # detect된 이미지를 base64로 변환
                detected_base64 = image_to_base64(detected_img)
                
                return {
                    "success": True,
                    "detected": True,
                    "face_count": face_count,
                    "face_coordinates": face_coords,
                    "detected_image": detected_base64
                }
            else:
                # 얼굴이 없으면 원본 이미지를 base64로 변환
                try:
                    with open(tmp_path, 'rb') as f:
                        img_data = np.frombuffer(f.read(), np.uint8)
                        original_img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
                except Exception as e:
                    print(f"⚠️ 이미지 읽기 오류: {e}")
                    original_img = cv2.imread(str(tmp_path))
                
                if original_img is not None:
                    original_base64 = image_to_base64(original_img)
                    return {
                        "success": True,
                        "detected": False,
                        "face_count": 0,
                        "face_coordinates": [],
                        "detected_image": original_base64
                    }
                else:
                    return {
                        "success": False,
                        "message": "이미지를 읽을 수 없습니다."
                    }
        finally:
            # 임시 파일 삭제
            if tmp_path.exists():
                tmp_path.unlink()
    
    except Exception as e:
        print(f"❌ 얼굴 인식 API 오류: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"얼굴 인식 중 오류가 발생했습니다: {str(e)}"
        }


@app.post("/api/portfolio/upload")
async def upload_portfolio(
    title: str = Form(..., description="포트폴리오 제목"),
    description: str = Form("", description="포트폴리오 설명"),
    tags: str = Form("", description="포트폴리오 태그 (쉼표로 구분)"),
    images: List[UploadFile] = File(..., description="업로드할 이미지 파일들 (multipart/form-data)")
):
    """
    포트폴리오 파일을 업로드하고 app/data/yolo 폴더에 저장
    multipart/form-data 형식으로 제목, 설명, 태그, 이미지 파일들을 받습니다.
    """
    try:
        saved_files = []
        
        # 파일이 없으면 에러
        if not images or len(images) == 0:
            return {
                "success": False,
                "message": "업로드할 파일이 없습니다."
            }
        
        for image in images:
            # 파일명 안전하게 처리 (경로 조작 방지)
            safe_filename = os.path.basename(image.filename)
            
            # 파일이 이미 존재하는 경우 타임스탬프 추가
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(safe_filename)
            
            # 원본 파일명 (타임스탬프 포함)
            original_filename = f"{name}_{timestamp}{ext}"
            
            # 임시 파일로 저장 (원본은 저장하지 않음)
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp_file:
                tmp_path = Path(tmp_file.name)
                shutil.copyfileobj(image.file, tmp_file)
            
            try:
                # 파일 정보 초기화
                file_info = {
                    "filename": original_filename,
                    "path": None,  # 원본 파일은 저장하지 않음
                    "size": tmp_path.stat().st_size,
                    "detected": False,
                    "face_count": 0,
                    "face_coordinates": [],
                    "detected_image_path": None
                }
                
                # 이미지 파일 확장자 확인
                image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']
                if any(original_filename.lower().endswith(ext) for ext in image_extensions):
                    # 이미지 업로드 시 자동으로 얼굴 인식 및 YOLO 추론 수행
                    # 저장은 하지 않고 처리된 이미지만 base64로 반환
                    detect_result = auto_detect_on_upload(tmp_path, cascade_path, target_dir, original_filename)
                    
                    # detect 결과를 file_info에 반영
                    file_info.update(detect_result)
                    
                    # detected_image_base64가 있으면 추가
                    if detect_result.get('detected_image_base64'):
                        file_info['detected_image_base64'] = detect_result['detected_image_base64']
                        file_info['detected'] = True
                else:
                    # 이미지가 아닌 파일은 저장하지 않음
                    pass
            
            finally:
                # 임시 파일 삭제
                if tmp_path.exists():
                    try:
                        tmp_path.unlink()
                        print(f"✅ 임시 파일 삭제: {tmp_path}")
                    except Exception as e:
                        print(f"⚠️ 임시 파일 삭제 실패: {e}")
            
            saved_files.append(file_info)
        
        return {
            "success": True,
            "message": f"{len(saved_files)}개의 파일이 성공적으로 저장되었습니다.",
            "title": title,
            "description": description,
            "tags": tags,
            "files": saved_files
        }
    
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"파일 저장 중 오류가 발생했습니다: {str(e)}"
        }


@app.post("/api/portfolio/save-detected")
async def save_detected_to_original_path(
    image: UploadFile = File(..., description="저장할 detect된 이미지 파일 (multipart/form-data)"),
    original_path: str = Form(..., description="원본 파일의 전체 경로")
):
    """
    detect된 이미지를 원본 파일 경로에 저장
    multipart/form-data 형식으로 이미지 파일과 경로를 받습니다.
    """
    try:
        # 원본 파일 경로 파싱
        original_path_obj = Path(original_path)
        
        # 경로가 존재하는지 확인
        if not original_path_obj.parent.exists():
            return {
                "success": False,
                "message": f"원본 파일 경로를 찾을 수 없습니다: {original_path_obj.parent}"
            }
        
        # 원본 파일명에서 확장자 추출
        name, ext = os.path.splitext(original_path_obj.name)
        if not ext:
            ext = os.path.splitext(image.filename)[1] if image.filename else '.jpg'
        
        # detect된 이미지 파일명 생성
        detected_filename = f"{name}_detected{ext}"
        detected_path = original_path_obj.parent / detected_filename
        
        # 파일명 중복 처리
        counter = 1
        while detected_path.exists():
            detected_filename = f"{name}_detected_{counter}{ext}"
            detected_path = original_path_obj.parent / detected_filename
            counter += 1
        
        # 이미지 파일 저장
        try:
            # 한글 경로 문제 해결: numpy로 파일을 읽은 후 decode
            with open(detected_path, 'wb') as f:
                shutil.copyfileobj(image.file, f)
        except Exception as e:
            print(f"⚠️ 이미지 저장 중 오류: {e}")
            return {
                "success": False,
                "message": f"파일 저장 중 오류가 발생했습니다: {str(e)}"
            }
        
        print(f"✅ Detect된 이미지 저장 완료: {detected_path}")
        
        return {
            "success": True,
            "message": "Detect된 이미지가 원본 파일 경로에 저장되었습니다.",
            "saved_path": str(detected_path),
            "filename": detected_filename
        }
    
    except Exception as e:
        print(f"❌ 저장 오류: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"저장 중 오류가 발생했습니다: {str(e)}"
        }


@app.post("/api/portfolio/save-detected-to-yolo")
async def save_detected_to_yolo(
    image: UploadFile = File(..., description="저장할 detect된 이미지 파일 (multipart/form-data)"),
    filename: str = Form(..., description="원본 파일명")
):
    """
    detect된 이미지를 app/data/yolo 폴더에 저장
    multipart/form-data 형식으로 이미지 파일과 파일명을 받습니다.
    """
    try:
        # 파일명에서 확장자 추출
        name, ext = os.path.splitext(filename)
        if not ext:
            ext = os.path.splitext(image.filename)[1] if image.filename else '.jpg'
        
        # detect된 이미지 파일명 생성
        detected_filename = f"{name}_detected{ext}"
        detected_path = target_dir / detected_filename
        
        # 파일명 중복 처리
        counter = 1
        while detected_path.exists():
            detected_filename = f"{name}_detected_{counter}{ext}"
            detected_path = target_dir / detected_filename
            counter += 1
        
        # 이미지 파일 저장
        try:
            with open(detected_path, 'wb') as f:
                shutil.copyfileobj(image.file, f)
        except Exception as e:
            print(f"⚠️ 이미지 저장 중 오류: {e}")
            return {
                "success": False,
                "message": f"파일 저장 중 오류가 발생했습니다: {str(e)}"
            }
        
        print(f"✅ Detect된 이미지 저장 완료: {detected_path}")
        
        return {
            "success": True,
            "message": "Detect된 이미지가 저장되었습니다.",
            "saved_path": str(detected_path),
            "filename": detected_filename
        }
    
    except Exception as e:
        print(f"❌ 저장 오류: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": f"저장 중 오류가 발생했습니다: {str(e)}"
        }


@app.get("/")
async def root():
    """헬스 체크 엔드포인트"""
    return {
        "message": "Portfolio Upload API",
        "status": "running",
        "target_directory": str(target_dir)
    }


if __name__ == "__main__":
    # 서버 실행 (포트는 환경 변수나 설정에서 가져올 수 있음)
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
