"""
YOLO Classification 기능 모듈
이미지 분류를 수행합니다.
"""
import cv2
import numpy as np
from pathlib import Path
import tempfile

# YOLO Classification 모델 전역 변수
_yolo_class_model = None
_yolo_class_model_path = None


def get_yolo_class_model(model_path: Path = None):
    """YOLO Classification 모델 로드 (싱글톤 패턴)"""
    global _yolo_class_model, _yolo_class_model_path
    
    try:
        from ultralytics import YOLO
    except ImportError:
        print("⚠️ Ultralytics가 설치되지 않았습니다. YOLO Classification을 사용할 수 없습니다.")
        return None
    
    # 모델 경로 설정
    if model_path is None:
        # 기본 모델 경로: 현재 스크립트의 data 폴더
        current_dir = Path(__file__).parent
        model_path = current_dir / 'data' / 'yolo11n-cls.pt'
    
    # 이미 로드된 모델이 있고 경로가 같으면 재사용
    if _yolo_class_model is not None and _yolo_class_model_path == str(model_path):
        return _yolo_class_model
    
    # 모델 파일 확인
    if not model_path.exists():
        print(f"⚠️ YOLO Classification 모델 파일을 찾을 수 없습니다: {model_path}")
        print("   기본 모델을 다운로드합니다...")
        try:
            _yolo_class_model = YOLO('yolo11n-cls.pt')
            _yolo_class_model_path = 'yolo11n-cls.pt'
            print("✅ YOLO Classification 모델 로드 완료 (기본 모델)")
            return _yolo_class_model
        except Exception as e:
            print(f"⚠️ YOLO Classification 모델 로드 실패: {e}")
            return None
    
    try:
        _yolo_class_model = YOLO(str(model_path))
        _yolo_class_model_path = str(model_path)
        print(f"✅ YOLO Classification 모델 로드 완료: {model_path}")
        return _yolo_class_model
    except Exception as e:
        print(f"⚠️ YOLO Classification 모델 로드 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def apply_yolo_classification_to_objects(image: np.ndarray, detected_objects: list, model_path: Path = None, top_k: int = 3) -> tuple:
    """
    감지된 각 객체에 대해 YOLO Classification을 적용하여 분류 결과 반환
    
    Args:
        image: OpenCV 이미지 (numpy array, BGR 형식)
        detected_objects: 감지된 객체 리스트 [{"bbox": {"x1": int, "y1": int, "x2": int, "y2": int}, "class": str, "confidence": float}, ...]
        model_path: YOLO 모델 경로 (None이면 기본 경로 사용)
        top_k: 상위 k개 분류 결과 반환
    
    Returns:
        tuple: (result_image, all_classifications)
            - result_image: 분류 결과가 표시된 이미지 (BGR 형식)
            - all_classifications: 각 객체별 분류 결과 리스트
    """
    try:
        model = get_yolo_class_model(model_path)
        if model is None:
            print("⚠️ YOLO Classification 모델을 사용할 수 없어 원본 이미지를 반환합니다.")
            return image, []
        
        # 원본 이미지 복사
        result_image = image.copy()
        all_classifications = []
        
        # 각 객체에 대해 classification 수행
        for obj_idx, obj in enumerate(detected_objects):
            if "bbox" not in obj:
                continue
            
            bbox = obj["bbox"]
            x1, y1, x2, y2 = bbox["x1"], bbox["y1"], bbox["x2"], bbox["y2"]
            
            # 이미지 경계 확인
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(image.shape[1], x2)
            y2 = min(image.shape[0], y2)
            
            if x2 <= x1 or y2 <= y1:
                continue
            
            # 객체 영역 잘라내기
            obj_crop = image[y1:y2, x1:x2]
            
            if obj_crop.size == 0:
                continue
            
            # 잘라낸 영역에 대해 classification 수행
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
                tmp_path = Path(tmp_file.name)
                try:
                    cv2.imwrite(str(tmp_path), obj_crop)
                    results = model(str(tmp_path))
                    
                    classifications = []
                    
                    if results and len(results) > 0:
                        result = results[0]
                        
                        if hasattr(result, 'probs') and result.probs is not None:
                            top_indices = result.probs.top5[:top_k] if hasattr(result.probs, 'top5') else []
                            top_confidences = result.probs.top5conf[:top_k] if hasattr(result.probs, 'top5conf') else []
                            
                            class_names = model.names
                            for idx, conf in zip(top_indices, top_confidences):
                                class_name = class_names[int(idx)]
                                classifications.append({
                                    "class": class_name,
                                    "confidence": float(conf)
                                })
                            
                            # 객체 옆에 분류 결과 표시
                            # 바운딩 박스 위쪽에 표시
                            y_offset = y1 - 10
                            if y_offset < 30:
                                y_offset = y2 + 30
                            
                            for i, cls_info in enumerate(classifications):
                                label = f"{i+1}. {cls_info['class']}: {cls_info['confidence']:.2%}"
                                
                                # 텍스트 배경
                                (text_width, text_height), baseline = cv2.getTextSize(
                                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                                )
                                
                                # 바운딩 박스 색상과 일치하는 색상 사용
                                colors = [
                                    (0, 255, 0),    # 녹색
                                    (255, 0, 0),    # 파란색
                                    (0, 0, 255),    # 빨간색
                                    (255, 255, 0),  # 청록색
                                    (255, 0, 255),  # 자홍색
                                    (0, 255, 255),  # 노란색
                                ]
                                color = colors[obj_idx % len(colors)]
                                
                                cv2.rectangle(
                                    result_image,
                                    (x1, y_offset - text_height - 5),
                                    (x1 + text_width + 10, y_offset + 5),
                                    (0, 0, 0),  # 검은색 배경
                                    -1
                                )
                                
                                # 텍스트
                                cv2.putText(
                                    result_image,
                                    label,
                                    (x1 + 5, y_offset),
                                    cv2.FONT_HERSHEY_SIMPLEX,
                                    0.5,
                                    (255, 255, 255),  # 흰색 텍스트
                                    1
                                )
                                
                                y_offset += 25
                            
                            print(f"  ✅ 객체 {obj_idx+1} ({obj.get('class', 'unknown')}): {len(classifications)}개 분류 결과")
                    
                    all_classifications.append({
                        "object_index": obj_idx,
                        "object_class": obj.get("class", "unknown"),
                        "classifications": classifications
                    })
                    
                finally:
                    if tmp_path.exists():
                        try:
                            tmp_path.unlink()
                        except:
                            pass
        
        return result_image, all_classifications
    
    except Exception as e:
        print(f"⚠️ 객체별 YOLO Classification 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return image, []


def apply_yolo_classification(image: np.ndarray, model_path: Path = None, top_k: int = 5) -> tuple:
    """
    이미지에 YOLO Classification을 적용하여 분류 결과 반환
    
    Args:
        image: OpenCV 이미지 (numpy array, BGR 형식)
        model_path: YOLO 모델 경로 (None이면 기본 경로 사용)
        top_k: 상위 k개 분류 결과 반환
    
    Returns:
        tuple: (result_image, classifications)
            - result_image: 분류 결과가 표시된 이미지 (BGR 형식)
            - classifications: 분류 결과 리스트 [{"class": str, "confidence": float}, ...]
    """
    try:
        model = get_yolo_class_model(model_path)
        if model is None:
            print("⚠️ YOLO Classification 모델을 사용할 수 없어 원본 이미지를 반환합니다.")
            return image, []
        
        # 원본 이미지 복사
        result_image = image.copy()
        
        # YOLO Classification 실행
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            try:
                # 이미지를 임시 파일로 저장
                cv2.imwrite(str(tmp_path), image)
                
                # YOLO Classification 실행
                results = model(str(tmp_path))
                
                classifications = []
                
                # 결과 처리
                if results and len(results) > 0:
                    result = results[0]
                    
                    # Classification 결과 가져오기
                    if hasattr(result, 'probs') and result.probs is not None:
                        # 상위 k개 클래스 가져오기
                        top_indices = result.probs.top5[:top_k] if hasattr(result.probs, 'top5') else []
                        top_confidences = result.probs.top5conf[:top_k] if hasattr(result.probs, 'top5conf') else []
                        
                        # 클래스 이름과 신뢰도 매핑
                        class_names = model.names
                        for idx, conf in zip(top_indices, top_confidences):
                            class_name = class_names[int(idx)]
                            classifications.append({
                                "class": class_name,
                                "confidence": float(conf)
                            })
                        
                        # 이미지에 분류 결과 텍스트로 표시
                        y_offset = 30
                        for i, cls_info in enumerate(classifications):
                            label = f"{i+1}. {cls_info['class']}: {cls_info['confidence']:.2%}"
                            
                            # 텍스트 배경
                            (text_width, text_height), baseline = cv2.getTextSize(
                                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
                            )
                            cv2.rectangle(
                                result_image,
                                (10, y_offset - text_height - 5),
                                (10 + text_width + 10, y_offset + 5),
                                (0, 0, 0),
                                -1
                            )
                            
                            # 텍스트
                            cv2.putText(
                                result_image,
                                label,
                                (15, y_offset),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6,
                                (255, 255, 255),
                                2
                            )
                            y_offset += 35
                        
                        print(f"✅ YOLO Classification: {len(classifications)}개 클래스 검출")
                
                return result_image, classifications
            finally:
                # 임시 파일 삭제
                if tmp_path.exists():
                    try:
                        tmp_path.unlink()
                    except:
                        pass
    
    except Exception as e:
        print(f"⚠️ YOLO Classification 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return image, []


def classify_image(image_path: Path, model_path: Path = None, top_k: int = 5) -> dict:
    """
    이미지 파일에 YOLO Classification을 적용
    
    Args:
        image_path: 이미지 파일 경로
        model_path: YOLO 모델 경로
        top_k: 상위 k개 분류 결과 반환
    
    Returns:
        dict: 분류 결과
            - success: bool
            - classifications: list
            - top_class: str (가장 높은 신뢰도 클래스)
    """
    try:
        # 이미지 읽기
        img = cv2.imread(str(image_path))
        if img is None:
            # 한글 경로 지원
            with open(image_path, 'rb') as f:
                img_data = np.frombuffer(f.read(), np.uint8)
                img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
        
        if img is None:
            return {
                "success": False,
                "message": "이미지를 읽을 수 없습니다.",
                "classifications": []
            }
        
        # Classification 적용
        result_image, classifications = apply_yolo_classification(img, model_path, top_k)
        
        return {
            "success": True,
            "classifications": classifications,
            "top_class": classifications[0]["class"] if classifications else None,
            "top_confidence": classifications[0]["confidence"] if classifications else None
        }
    
    except Exception as e:
        print(f"⚠️ 이미지 분류 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": str(e),
            "classifications": []
        }

