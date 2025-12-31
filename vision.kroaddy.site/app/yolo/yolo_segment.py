"""
YOLO Segmentation 기능 모듈
이미지 세그멘테이션을 수행합니다.
"""
import cv2
import numpy as np
from pathlib import Path
import tempfile

# YOLO Segmentation 모델 전역 변수
_yolo_seg_model = None
_yolo_seg_model_path = None


def get_yolo_seg_model(model_path: Path = None):
    """YOLO Segmentation 모델 로드 (싱글톤 패턴)"""
    global _yolo_seg_model, _yolo_seg_model_path
    
    try:
        from ultralytics import YOLO
    except ImportError:
        print("⚠️ Ultralytics가 설치되지 않았습니다. YOLO Segmentation을 사용할 수 없습니다.")
        return None
    
    # 모델 경로 설정
    if model_path is None:
        # 기본 모델 경로: 현재 스크립트의 data 폴더
        current_dir = Path(__file__).parent
        model_path = current_dir / 'data' / 'yolo11n-seg.pt'
    
    # 이미 로드된 모델이 있고 경로가 같으면 재사용
    if _yolo_seg_model is not None and _yolo_seg_model_path == str(model_path):
        return _yolo_seg_model
    
    # 모델 파일 확인
    if not model_path.exists():
        print(f"⚠️ YOLO Segmentation 모델 파일을 찾을 수 없습니다: {model_path}")
        print("   기본 모델을 다운로드합니다...")
        try:
            _yolo_seg_model = YOLO('yolo11n-seg.pt')
            _yolo_seg_model_path = 'yolo11n-seg.pt'
            print("✅ YOLO Segmentation 모델 로드 완료 (기본 모델)")
            return _yolo_seg_model
        except Exception as e:
            print(f"⚠️ YOLO Segmentation 모델 로드 실패: {e}")
            return None
    
    try:
        _yolo_seg_model = YOLO(str(model_path))
        _yolo_seg_model_path = str(model_path)
        print(f"✅ YOLO Segmentation 모델 로드 완료: {model_path}")
        return _yolo_seg_model
    except Exception as e:
        print(f"⚠️ YOLO Segmentation 모델 로드 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def calculate_bbox_iou(bbox1: dict, bbox2: dict) -> float:
    """
    두 바운딩 박스의 IoU (Intersection over Union) 계산
    
    Args:
        bbox1: {"x1": int, "y1": int, "x2": int, "y2": int}
        bbox2: {"x1": int, "y1": int, "x2": int, "y2": int}
    
    Returns:
        float: IoU 값 (0.0 ~ 1.0)
    """
    x1_1, y1_1, x2_1, y2_1 = bbox1["x1"], bbox1["y1"], bbox1["x2"], bbox1["y2"]
    x1_2, y1_2, x2_2, y2_2 = bbox2["x1"], bbox2["y1"], bbox2["x2"], bbox2["y2"]
    
    # 교집합 영역 계산
    x1_inter = max(x1_1, x1_2)
    y1_inter = max(y1_1, y1_2)
    x2_inter = min(x2_1, x2_2)
    y2_inter = min(y2_1, y2_2)
    
    if x2_inter < x1_inter or y2_inter < y1_inter:
        return 0.0
    
    intersection = (x2_inter - x1_inter) * (y2_inter - y1_inter)
    area1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0.0


def apply_yolo_segmentation(image: np.ndarray, model_path: Path = None, alpha: float = 0.5, detected_objects: list = None) -> tuple:
    """
    이미지에 YOLO Segmentation을 적용하여 세그멘테이션 결과 반환
    detection으로 찾은 객체와 동일한 객체에만 segmentation을 적용합니다.
    원본 이미지의 색상을 유지하면서 마스크를 오버레이합니다.
    
    Args:
        image: OpenCV 이미지 (numpy array, BGR 형식)
        model_path: YOLO 모델 경로 (None이면 기본 경로 사용)
        alpha: 마스크 오버레이 투명도 (0.0 ~ 1.0)
        detected_objects: detection으로 찾은 객체 리스트 [{"bbox": {"x1": int, "y1": int, "x2": int, "y2": int}, "class": str, "confidence": float}, ...]
    
    Returns:
        tuple: (result_image, segments)
            - result_image: 세그멘테이션 결과가 그려진 이미지 (BGR 형식)
            - segments: 세그멘테이션 정보 리스트 [{"class": str, "confidence": float, "area": float, "area_percentage": float, "bbox": dict}, ...]
    """
    try:
        model = get_yolo_seg_model(model_path)
        if model is None:
            print("⚠️ YOLO Segmentation 모델을 사용할 수 없어 원본 이미지를 반환합니다.")
            return image, []
        
        # 원본 이미지 복사 (색상 유지)
        result_image = image.copy()
        
        # YOLO Segmentation 실행
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            try:
                # 이미지를 임시 파일로 저장
                cv2.imwrite(str(tmp_path), image)
                
                # YOLO Segmentation 추론 실행
                results = model(str(tmp_path))
                
                segments = []
                
                # 결과 처리
                if results and len(results) > 0:
                    result = results[0]
                    
                    # Masks 정보 가져오기
                    if hasattr(result, 'masks') and result.masks is not None:
                        masks_data = result.masks
                        class_names = model.names
                        
                        # boxes 정보 가져오기
                        boxes_data = None
                        num_boxes = 0
                        if hasattr(result, 'boxes') and result.boxes is not None:
                            boxes_data = result.boxes
                            num_boxes = len(boxes_data.data) if boxes_data.data is not None else 0
                        
                        # 마스크 개수 확인
                        num_masks = 0
                        if hasattr(masks_data, 'data') and masks_data.data is not None:
                            num_masks = len(masks_data.data)
                        elif hasattr(masks_data, 'xy') and masks_data.xy is not None:
                            num_masks = len(masks_data.xy)
                        
                        print(f"🔍 발견된 마스크 개수: {num_masks}, 박스 개수: {num_boxes}")
                        
                        # 마스크와 boxes를 함께 처리
                        # YOLO에서는 masks와 boxes의 인덱스가 일치합니다
                        for i in range(num_masks):
                            try:
                                # 마스크 가져오기
                                if hasattr(masks_data, 'data') and masks_data.data is not None:
                                    mask = masks_data.data[i]
                                else:
                                    print(f"⚠️ 마스크 {i}: data 속성을 찾을 수 없습니다")
                                    continue
                                
                                if mask is None:
                                    print(f"⚠️ 마스크 {i}: None입니다")
                                    continue
                                
                                # 마스크를 numpy 배열로 변환
                                try:
                                    mask_np = mask.cpu().numpy()
                                except:
                                    mask_np = np.array(mask)
                                
                                if mask_np.size == 0:
                                    print(f"⚠️ 마스크 {i}: 빈 배열입니다")
                                    continue
                                
                                print(f"  📦 마스크 {i} 형태: {mask_np.shape}, 크기: {mask_np.size}")
                                
                                # 마스크 형태 확인 및 리사이즈
                                mask_resized = None
                                
                                if len(mask_np.shape) == 2:
                                    # 2D 마스크: (H, W)
                                    mask_resized = cv2.resize(mask_np.astype(np.float32), 
                                                             (image.shape[1], image.shape[0]),
                                                             interpolation=cv2.INTER_LINEAR)
                                elif len(mask_np.shape) == 3:
                                    # 3D 마스크: (1, H, W) 또는 (H, W, 1) 또는 (C, H, W)
                                    if mask_np.shape[0] == 1:
                                        # (1, H, W)
                                        mask_resized = cv2.resize(mask_np[0].astype(np.float32),
                                                                 (image.shape[1], image.shape[0]),
                                                                 interpolation=cv2.INTER_LINEAR)
                                    elif mask_np.shape[2] == 1:
                                        # (H, W, 1)
                                        mask_resized = cv2.resize(mask_np[:, :, 0].astype(np.float32),
                                                                 (image.shape[1], image.shape[0]),
                                                                 interpolation=cv2.INTER_LINEAR)
                                    else:
                                        # (C, H, W) - 첫 번째 채널 사용
                                        mask_resized = cv2.resize(mask_np[0].astype(np.float32),
                                                                 (image.shape[1], image.shape[0]),
                                                                 interpolation=cv2.INTER_LINEAR)
                                else:
                                    print(f"⚠️ 마스크 {i}: 알 수 없는 형태 {mask_np.shape}")
                                    continue
                                
                                if mask_resized is None:
                                    print(f"⚠️ 마스크 {i}: 리사이즈 실패")
                                    continue
                                
                                # 마스크 정규화 (0~1 범위)
                                if mask_resized.max() > 1.0:
                                    mask_resized = mask_resized / 255.0
                                
                                # 마스크가 비어있는지 확인
                                if mask_resized.max() < 0.01:
                                    print(f"⚠️ 마스크 {i}: 거의 비어있음 (max={mask_resized.max()})")
                                    continue
                                
                                # 클래스 정보 가져오기
                                class_name = "unknown"
                                conf = 0.0
                                bbox = None
                                
                                if boxes_data is not None and i < num_boxes:
                                    try:
                                        box = boxes_data.data[i]
                                        if box is not None:
                                            box_np = box.cpu().numpy()
                                            
                                            # boxes.data는 [x1, y1, x2, y2, conf, cls] 형태
                                            if len(box_np) >= 6:
                                                x1, y1, x2, y2 = int(box_np[0]), int(box_np[1]), int(box_np[2]), int(box_np[3])
                                                conf = float(box_np[4])
                                                cls = int(box_np[5])
                                                class_name = class_names[cls] if cls < len(class_names) else "unknown"
                                                bbox = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
                                            elif len(box_np) >= 5:
                                                # [x1, y1, x2, y2, conf] 형태 (cls가 별도)
                                                x1, y1, x2, y2 = int(box_np[0]), int(box_np[1]), int(box_np[2]), int(box_np[3])
                                                conf = float(box_np[4])
                                                if hasattr(boxes_data, 'cls') and boxes_data.cls is not None and i < len(boxes_data.cls):
                                                    cls = int(boxes_data.cls[i].cpu().numpy())
                                                    class_name = class_names[cls] if cls < len(class_names) else "unknown"
                                                bbox = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
                                    except Exception as e:
                                        print(f"⚠️ 마스크 {i}: 박스 정보 가져오기 실패: {e}")
                                
                                print(f"  🏷️ 마스크 {i}: {class_name} (신뢰도: {conf:.2f})")
                                
                                # detection으로 찾은 객체와 매칭하여 동일한 객체에만 segmentation 적용
                                if detected_objects and len(detected_objects) > 0:
                                    # segmentation 결과의 바운딩 박스와 detection 결과의 바운딩 박스를 비교
                                    matched = False
                                    best_iou = 0.0
                                    matched_detected_obj = None
                                    
                                    for detected_obj in detected_objects:
                                        if "bbox" not in detected_obj:
                                            continue
                                        
                                        # 클래스가 일치하는지 확인
                                        if detected_obj.get("class", "").lower() != class_name.lower():
                                            continue
                                        
                                        # IoU 계산
                                        iou = calculate_bbox_iou(bbox, detected_obj["bbox"])
                                        
                                        if iou > best_iou and iou > 0.3:  # IoU 임계값: 0.3
                                            best_iou = iou
                                            matched_detected_obj = detected_obj
                                            matched = True
                                    
                                    if not matched:
                                        print(f"  ⏭️ 마스크 {i}: {class_name}은(는) detection 결과와 매칭되지 않아 건너뜁니다")
                                        continue
                                    
                                    print(f"  ✅ 마스크 {i}: {class_name}이(가) detection 결과와 매칭됨 (IoU: {best_iou:.2f})")
                                else:
                                    # detected_objects가 없으면 모든 객체에 segmentation 적용
                                    print(f"  ℹ️ 마스크 {i}: detected_objects가 없어 모든 객체에 segmentation 적용")
                                
                                # 색상 생성 (개는 녹색으로 표시)
                                color = (0, 255, 0)  # 녹색
                                
                                # 마스크 오버레이 (투명도 적용)
                                # 마스크 이진화 (임계값 조정 가능)
                                threshold = 0.3  # 임계값을 낮춰서 더 많은 영역 포함
                                mask_binary = (mask_resized > threshold).astype(np.uint8)
                                
                                # 마스크가 있는 영역 확인
                                mask_area = np.sum(mask_binary > 0)
                                if mask_area < 10:  # 너무 작은 마스크는 건너뛰기
                                    print(f"⚠️ 마스크 {i}: 영역이 너무 작음 ({mask_area} 픽셀)")
                                    continue
                                
                                # 색상이 적용된 마스크 생성
                                mask_colored = np.zeros_like(image)
                                mask_colored[mask_binary > 0] = color
                                
                                # 원본 이미지에 마스크 오버레이 (누적 적용)
                                # 각 마스크를 개별적으로 오버레이하여 모든 객체가 표시되도록
                                # 마스크가 있는 영역에만 색상을 적용
                                mask_3channel = np.stack([mask_binary, mask_binary, mask_binary], axis=2).astype(np.float32)
                                mask_3channel = mask_3channel / 255.0  # 0~1 범위로 정규화
                                
                                # 마스크 영역에만 오버레이 적용
                                result_image = result_image.astype(np.float32)
                                mask_colored_float = mask_colored.astype(np.float32)
                                
                                # 마스크가 있는 영역: 오버레이 적용, 없는 영역: 원본 유지
                                result_image = np.where(mask_3channel > 0,
                                                       result_image * (1.0 - alpha) + mask_colored_float * alpha,
                                                       result_image)
                                result_image = result_image.astype(np.uint8)
                                
                                # 마스크 윤곽선 그리기 (바운딩 박스와 레이블 제거, 마스크만 표시)
                                mask_binary_255 = mask_binary * 255
                                contours, _ = cv2.findContours(mask_binary_255, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                                if len(contours) > 0:
                                    # 윤곽선만 그리기 (바운딩 박스 제거)
                                    cv2.drawContours(result_image, contours, -1, color, 2)
                                
                                # 마스크 영역 계산
                                area = np.sum(mask_binary > 0)
                                
                                segments.append({
                                    "class": class_name,
                                    "confidence": conf,
                                    "area": float(area),
                                    "area_percentage": float(area / (image.shape[0] * image.shape[1]) * 100),
                                    "bbox": bbox
                                })
                                
                                print(f"  ✅ 객체 {i+1}: {class_name} (신뢰도: {conf:.2f}, 영역: {area} 픽셀)")
                            except Exception as e:
                                print(f"⚠️ 마스크 {i} 처리 중 오류: {e}")
                                import traceback
                                traceback.print_exc()
                                continue
                        
                        print(f"✅ YOLO Segmentation: {len(segments)}개 객체 세그멘테이션 완료")
                
                return result_image, segments
            finally:
                # 임시 파일 삭제
                if tmp_path.exists():
                    try:
                        tmp_path.unlink()
                    except:
                        pass
    
    except Exception as e:
        print(f"⚠️ YOLO Segmentation 추론 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return image, []


def segment_image(image_path: Path, model_path: Path = None, alpha: float = 0.5) -> dict:
    """
    이미지 파일에 YOLO Segmentation을 적용
    
    Args:
        image_path: 이미지 파일 경로
        model_path: YOLO 모델 경로
        alpha: 마스크 오버레이 투명도
    
    Returns:
        dict: 세그멘테이션 결과
            - success: bool
            - segments: list
            - object_count: int
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
                "segments": []
            }
        
        # Segmentation 적용
        result_image, segments = apply_yolo_segmentation(img, model_path, alpha)
        
        return {
            "success": True,
            "segments": segments,
            "object_count": len(segments)
        }
    
    except Exception as e:
        print(f"⚠️ 세그멘테이션 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": str(e),
            "segments": []
        }

