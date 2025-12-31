"""
얼굴 인식 기능 모듈
"""
import os
import cv2
import numpy as np
import base64
import shutil
import tempfile
from pathlib import Path


# YOLO 모델 전역 변수
_yolo_model = None
_yolo_model_path = None

# YOLO 모듈 import (순환 참조 방지를 위해 함수 내부에서 import)
YOLO_MODULES_AVAILABLE = True


# Cascade 파일을 영문 경로로 복사하여 로드 (한글 경로 문제 해결)
_cascade_temp_path = None


def get_cascade_classifier(cascade_path: Path):
    """Cascade 파일을 영문 경로로 복사하여 로드"""
    global _cascade_temp_path
    
    if not cascade_path.exists():
        print(f"⚠️ Cascade 파일을 찾을 수 없습니다: {cascade_path}")
        return None
    
    try:
        # 이미 로드된 경우 재사용
        if _cascade_temp_path and Path(_cascade_temp_path).exists():
            cascade = cv2.CascadeClassifier(_cascade_temp_path)
            if not cascade.empty():
                return cascade
        
        # 임시 디렉토리에 영문 경로로 복사
        temp_dir = Path(tempfile.gettempdir())
        _cascade_temp_path = str(temp_dir / "haarcascade_frontalface_alt.xml")
        
        # Cascade 파일 복사
        shutil.copy2(cascade_path, _cascade_temp_path)
        
        # Cascade 로드
        cascade = cv2.CascadeClassifier(_cascade_temp_path)
        if cascade.empty():
            print(f"⚠️ Cascade 파일 로드 실패: {_cascade_temp_path}")
            return None
        
        print(f"✅ Cascade 파일 로드 성공: {_cascade_temp_path}")
        return cascade
    
    except Exception as e:
        print(f"⚠️ Cascade 파일 로드 중 오류: {e}")
        import traceback
        traceback.print_exc()
        return None


def rotate_image(image, angle):
    """이미지를 주어진 각도로 회전"""
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated, M


def rotate_rect(rect, angle, center):
    """회전된 이미지의 사각형 좌표를 원본 이미지 좌표로 변환"""
    x, y, w, h = rect
    # 회전된 이미지의 4개 모서리 점
    points = np.array([
        [x, y],
        [x + w, y],
        [x + w, y + h],
        [x, y + h]
    ], dtype=np.float32)
    
    # 역회전 변환 행렬
    M_inv = cv2.getRotationMatrix2D(center, -angle, 1.0)
    # 역변환 적용
    points_transformed = cv2.transform(points.reshape(1, -1, 2), M_inv).reshape(-1, 2)
    
    # 바운딩 박스 계산
    x_min = max(0, int(np.min(points_transformed[:, 0])))
    y_min = max(0, int(np.min(points_transformed[:, 1])))
    x_max = int(np.max(points_transformed[:, 0]))
    y_max = int(np.max(points_transformed[:, 1]))
    
    return (x_min, y_min, x_max - x_min, y_max - y_min)


def calculate_overlap(rect1, rect2):
    """두 사각형의 겹침 비율 계산"""
    x1, y1, w1, h1 = rect1
    x2, y2, w2, h2 = rect2
    
    # 교집합 영역 계산
    left = max(x1, x2)
    top = max(y1, y2)
    right = min(x1 + w1, x2 + w2)
    bottom = min(y1 + h1, y2 + h2)
    
    if right < left or bottom < top:
        return 0
    
    intersection = (right - left) * (bottom - top)
    area1 = w1 * h1
    area2 = w2 * h2
    union = area1 + area2 - intersection
    
    return intersection / union if union > 0 else 0


def detect_faces(image_path: Path, cascade_path: Path) -> tuple:
    """
    이미지에서 얼굴을 인식하고 사각형으로 표시한 이미지를 반환
    다양한 각도와 파라미터 조합으로 시도하여 정확도를 높임
    
    Args:
        image_path: 이미지 파일 경로
        cascade_path: Cascade 파일 경로
    
    Returns:
        tuple: (detected_image, face_count, face_coordinates)
            - detected_image: 얼굴이 표시된 이미지 (numpy array)
            - face_count: 감지된 얼굴 개수
            - face_coordinates: 얼굴 좌표 리스트 [{"index": int, "x": int, "y": int, "w": int, "h": int}, ...]
    """
    try:
        # Haar Cascade 로드
        cascade = get_cascade_classifier(cascade_path)
        if cascade is None:
            return None, 0, []
        
        # 이미지 읽기 (한글 경로 지원)
        try:
            # 한글 경로 문제 해결: numpy로 파일을 읽은 후 decode
            with open(image_path, 'rb') as f:
                img_data = np.frombuffer(f.read(), np.uint8)
                img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
        except Exception as e:
            print(f"⚠️ 이미지를 읽는 중 오류 발생: {e}")
            # 대체 방법: 직접 경로 사용 시도
            img = cv2.imread(str(image_path))
        
        if img is None:
            print(f"⚠️ 이미지를 읽을 수 없습니다: {image_path}")
            return None, 0, []
        
        print(f"이미지 크기: {img.shape}")
        
        # 그레이스케일 변환
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        (h, w) = gray.shape[:2]
        center = (w // 2, h // 2)
        
        best_face = None
        best_angle = 0
        max_faces = 0
        
        # 다양한 각도로 회전하여 얼굴 인식 시도
        angles = [0, -15, -10, -5, 5, 10, 15, -20, 20, -25, 25, -30, 30]
        
        # 여러 파라미터 조합 시도
        param_combinations = [
            {'scaleFactor': 1.1, 'minNeighbors': 3, 'minSize': (20, 20)},
            {'scaleFactor': 1.05, 'minNeighbors': 2, 'minSize': (15, 15)},
            {'scaleFactor': 1.1, 'minNeighbors': 2, 'minSize': (25, 25)},
            {'scaleFactor': 1.03, 'minNeighbors': 1, 'minSize': (10, 10)},
            {'scaleFactor': 1.1, 'minNeighbors': 4, 'minSize': (30, 30)},
            {'scaleFactor': 1.05, 'minNeighbors': 3, 'minSize': (20, 20)},
        ]
        
        # 먼저 기본 파라미터로 시도 (빠른 처리)
        faces = cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=3, minSize=(20, 20))
        if len(faces) > 0:
            best_face = faces
            max_faces = len(faces)
            print(f"기본 파라미터로 {len(faces)}개의 얼굴을 찾았습니다!")
        else:
            # 기본 파라미터로 실패하면 회전 및 다양한 파라미터 시도
            for angle in angles:
                if max_faces >= 4:  # 충분한 얼굴을 찾으면 중단
                    break
                
                # 이미지 회전
                rotated_gray, _ = rotate_image(gray, angle)
                
                # 여러 파라미터 조합으로 시도
                for params in param_combinations:
                    face = cascade.detectMultiScale(rotated_gray, **params)
                    
                    if len(face) > max_faces:
                        max_faces = len(face)
                        best_angle = angle
                        print(f"각도 {angle}도에서 {len(face)}개의 얼굴을 찾았습니다! (파라미터: {params})")
                        
                        # 회전된 좌표를 원본 이미지 좌표로 변환
                        face_original = []
                        for (x, y, w, h) in face:
                            rect_original = rotate_rect((x, y, w, h), angle, center)
                            face_original.append(rect_original)
                        best_face = np.array(face_original)
                        
                        # 충분한 얼굴을 찾으면 중단
                        if max_faces >= 4:
                            break
                
                if max_faces >= 4:
                    break
        
        faces = best_face
        
        if faces is None or len(faces) == 0:
            print("모든 각도와 파라미터 조합에서 얼굴을 찾을 수 없습니다.")
            return None, 0, []
        
        # 중복 제거: 겹치는 사각형 제거
        filtered_faces = []
        for i, rect1 in enumerate(faces):
            is_duplicate = False
            for j, rect2 in enumerate(filtered_faces):
                overlap = calculate_overlap(rect1, rect2)
                if overlap > 0.5:  # 50% 이상 겹치면 중복으로 간주
                    is_duplicate = True
                    # 더 큰 사각형을 유지
                    if (rect1[2] * rect1[3]) > (rect2[2] * rect2[3]):
                        filtered_faces[j] = rect1
                    break
            if not is_duplicate:
                filtered_faces.append(rect1)
        
        faces = np.array(filtered_faces)
        print(f"얼굴 {len(faces)}개를 찾았습니다! (중복 제거 후)")
        
        # 얼굴이 감지된 경우 사각형 그리기
        face_coordinates = []
        detected_img = img.copy()
        
        for idx, (x, y, w, h) in enumerate(faces):
            print(f"얼굴인식 인덱스: {idx}")
            print(f"얼굴인식 좌표: {x}, {y}, {w}, {h}")
            # 빨간색 사각형으로 얼굴 표시
            cv2.rectangle(detected_img, (x, y), (x + w, y + h), (0, 0, 255), 2)
            face_coordinates.append({"index": idx, "x": int(x), "y": int(y), "w": int(w), "h": int(h)})
        
        return detected_img, len(faces), face_coordinates
    
    except Exception as e:
        print(f"❌ 얼굴 인식 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None, 0, []


def get_yolo_model(model_path: Path = None):
    """YOLO 모델 로드 (싱글톤 패턴)"""
    global _yolo_model, _yolo_model_path
    
    try:
        from ultralytics import YOLO
    except ImportError:
        print("⚠️ Ultralytics가 설치되지 않았습니다. YOLO 추론을 사용할 수 없습니다.")
        return None
    
    # 모델 경로 설정
    if model_path is None:
        # 기본 모델 경로: 현재 스크립트의 data 폴더
        current_dir = Path(__file__).parent
        model_path = current_dir / 'data' / 'yolo11n.pt'
    
    # 이미 로드된 모델이 있고 경로가 같으면 재사용
    if _yolo_model is not None and _yolo_model_path == str(model_path):
        return _yolo_model
    
    # 모델 파일 확인
    if not model_path.exists():
        print(f"⚠️ YOLO 모델 파일을 찾을 수 없습니다: {model_path}")
        print("   기본 모델을 다운로드합니다...")
        try:
            _yolo_model = YOLO('yolo11n.pt')
            _yolo_model_path = 'yolo11n.pt'
            print("✅ YOLO 모델 로드 완료 (기본 모델)")
            return _yolo_model
        except Exception as e:
            print(f"⚠️ YOLO 모델 로드 실패: {e}")
            return None
    
    try:
        _yolo_model = YOLO(str(model_path))
        _yolo_model_path = str(model_path)
        print(f"✅ YOLO 모델 로드 완료: {model_path}")
        return _yolo_model
    except Exception as e:
        print(f"⚠️ YOLO 모델 로드 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def apply_yolo_inference(image: np.ndarray, model_path: Path = None) -> tuple:
    """
    이미지에 YOLO 추론을 적용하여 객체 검출 결과를 그린 이미지 반환
    원본 이미지의 색상을 유지하면서 바운딩 박스와 레이블만 추가
    
    Args:
        image: OpenCV 이미지 (numpy array, BGR 형식)
        model_path: YOLO 모델 경로 (None이면 기본 경로 사용)
    
    Returns:
        tuple: (result_image, detected_objects)
            - result_image: YOLO 추론 결과가 그려진 이미지 (BGR 형식, 원본 색상 유지)
            - detected_objects: 감지된 객체 리스트 [{"bbox": {"x1": int, "y1": int, "x2": int, "y2": int}, "class": str, "confidence": float}, ...]
    """
    try:
        model = get_yolo_model(model_path)
        if model is None:
            print("⚠️ YOLO 모델을 사용할 수 없어 원본 이미지를 반환합니다.")
            return image, []
        
        # 원본 이미지 복사 (색상 유지)
        result_image = image.copy()
        detected_objects = []
        
        # YOLO 추론 실행
        # OpenCV 이미지를 임시 파일로 저장
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            try:
                # 이미지를 임시 파일로 저장
                cv2.imwrite(str(tmp_path), image)
                
                # YOLO 추론 실행
                results = model(str(tmp_path))
                
                # 결과 처리 - 원본 이미지에 직접 바운딩 박스 그리기
                if results and len(results) > 0:
                    result = results[0]
                    
                    # 바운딩 박스 정보 가져오기
                    if result.boxes is not None and len(result.boxes) > 0:
                        # 클래스 이름 가져오기
                        class_names = model.names
                        
                        # 각 검출된 객체에 대해 바운딩 박스 그리기
                        for box in result.boxes:
                            # 좌표 정보 (xyxy 형식: x1, y1, x2, y2)
                            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                            
                            # 신뢰도와 클래스
                            conf = float(box.conf[0].cpu().numpy())
                            cls = int(box.cls[0].cpu().numpy())
                            class_name = class_names[cls]
                            
                            # 바운딩 박스 색상 (BGR 형식)
                            # YOLO 기본 색상 팔레트 사용
                            colors = [
                                (0, 255, 0),    # 녹색
                                (255, 0, 0),    # 파란색
                                (0, 0, 255),    # 빨간색
                                (255, 255, 0),  # 청록색
                                (255, 0, 255),  # 자홍색
                                (0, 255, 255),  # 노란색
                            ]
                            color = colors[cls % len(colors)]
                            
                            # 바운딩 박스 그리기
                            cv2.rectangle(result_image, (x1, y1), (x2, y2), color, 2)
                            
                            # 레이블 텍스트 (바운딩 박스 우측 하단 구석에 표시)
                            label = f"{class_name} {conf:.2f}"
                            
                            # 텍스트 배경 크기 계산
                            (text_width, text_height), baseline = cv2.getTextSize(
                                label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1
                            )
                            
                            # 바운딩 박스 우측 하단 구석 위치 계산
                            label_x = x2 - text_width - 10
                            label_y = y2 - 5
                            
                            # 이미지 경계 확인
                            if label_x < x1:
                                label_x = x1 + 5
                            if label_y < y1 + text_height + baseline:
                                label_y = y1 + text_height + baseline + 5
                            
                            # 텍스트 배경 그리기 (바운딩 박스 우측 하단 구석)
                            cv2.rectangle(
                                result_image,
                                (label_x - 5, label_y - text_height - baseline - 5),
                                (label_x + text_width + 5, label_y),
                                color,
                                -1
                            )
                            
                            # 텍스트 그리기
                            cv2.putText(
                                result_image,
                                label,
                                (label_x, label_y - baseline - 2),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.5,
                                (255, 255, 255),  # 흰색 텍스트
                                1
                            )
                            
                            # 객체 정보 저장
                            detected_objects.append({
                                "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
                                "class": class_name,
                                "confidence": conf
                            })
                        
                        print(f"✅ YOLO 추론: {len(result.boxes)}개의 객체 검출")
                
                return result_image, detected_objects
            finally:
                # 임시 파일 삭제
                if tmp_path.exists():
                    try:
                        tmp_path.unlink()
                    except:
                        pass
    
    except Exception as e:
        print(f"⚠️ YOLO 추론 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return image, []


def image_to_base64(image: np.ndarray) -> str:
    """OpenCV 이미지를 base64 문자열로 변환"""
    try:
        _, buffer = cv2.imencode('.jpg', image)
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        return f"data:image/jpeg;base64,{img_base64}"
    except Exception as e:
        print(f"❌ Base64 변환 중 오류: {e}")
        return ""


def auto_detect_on_upload(image_path: Path, cascade_path: Path, target_dir: Path, original_filename: str) -> dict:
    """
    이미지 업로드 시 자동으로 YOLO 추론 (Detection, Classification, Pose, Segmentation)을 수행
    저장은 하지 않고 처리된 이미지를 base64로 반환 (저장은 다운로드 버튼 클릭 시 수행)
    
    Args:
        image_path: 업로드된 이미지 파일 경로
        cascade_path: Cascade 파일 경로 (현재 사용 안 함)
        target_dir: 결과를 저장할 디렉토리 (현재 사용 안 함, 다운로드 버튼 클릭 시 사용)
        original_filename: 원본 파일명
    
    Returns:
        dict: YOLO 추론 결과 정보
            - detected: bool - 객체가 감지되었는지 여부 (Detection 결과 기준)
            - face_count: int - 감지된 얼굴 개수 (현재 사용 안 함)
            - face_coordinates: list - 얼굴 좌표 리스트 (현재 사용 안 함)
            - detected_image_base64: str - 처리된 이미지의 base64 문자열
            - classifications: list - 분류 결과
            - top_class: str - 최상위 클래스
            - poses: list - 포즈 정보
            - person_count: int - 검출된 사람 수
            - segments: list - 세그멘테이션 정보
            - object_count: int - 검출된 객체 수 (Segmentation 결과 기준)
    """
    result = {
        "detected": False,
        "face_count": 0,
        "face_coordinates": [],
        "detected_image_base64": None,  # 저장하지 않고 base64로만 반환
        "classifications": [],
        "top_class": None,
        "poses": [],
        "person_count": 0,
        "segments": [],
        "object_count": 0
    }
    
    try:
        # 원본 이미지 읽기 (얼굴 인식 제거)
        try:
            with open(image_path, 'rb') as f:
                img_data = np.frombuffer(f.read(), np.uint8)
                final_img = cv2.imdecode(img_data, cv2.IMREAD_COLOR)
            if final_img is None:
                final_img = cv2.imread(str(image_path))
        except Exception as e:
            print(f"⚠️ 이미지 읽기 오류: {e}")
            final_img = cv2.imread(str(image_path))
        
        if final_img is None:
            print(f"⚠️ 이미지를 읽을 수 없습니다: {original_filename}")
            return result
        
        # 파일명에서 확장자 추출
        # original_filename에서 타임스탬프 부분 제거
        if '_' in original_filename:
            # 타임스탬프 형식: name_timestamp.ext
            parts = original_filename.rsplit('_', 1)
            if len(parts) == 2:
                name_with_ext = parts[0]
                name, ext = os.path.splitext(name_with_ext)
                if not ext:
                    ext = image_path.suffix or '.jpg'
            else:
                name, ext = os.path.splitext(original_filename)
        else:
            name, ext = os.path.splitext(original_filename)
        
        if not ext:
            ext = image_path.suffix or '.jpg'
        
        # YOLO 추론들 적용 (Detection, Classification, Pose, Segmentation)
        # 저장은 하지 않고 처리된 이미지만 반환
        current_dir = Path(__file__).parent
        
        # 1. YOLO Detection 적용 (바운딩 박스와 레이블 표시)
        detected_objects = []
        try:
            yolo_model_path = current_dir / 'data' / 'yolo11n.pt'
            
            # YOLO 추론 적용 (바운딩 박스와 레이블 그리기 + 객체 정보 반환)
            final_img, detected_objects = apply_yolo_inference(final_img, yolo_model_path)
            
            if detected_objects:
                print(f"✅ YOLO Detection 적용 완료: {len(detected_objects)}개 객체 검출")
            else:
                print(f"ℹ️ YOLO Detection: 감지된 객체가 없습니다")
        except Exception as e:
            print(f"⚠️ YOLO Detection 적용 중 오류: {e}")
            import traceback
            traceback.print_exc()
        
        # 2. YOLO Classification 적용 (각 객체별로)
        try:
            from yolo_class import apply_yolo_classification_to_objects
            
            if detected_objects:
                yolo_class_model_path = current_dir / 'data' / 'yolo11n-cls.pt'
                final_img, all_classifications = apply_yolo_classification_to_objects(
                    final_img, detected_objects, yolo_class_model_path, top_k=3
                )
                
                # 전체 classification 결과 저장
                if all_classifications:
                    result["classifications"] = all_classifications
                    # 첫 번째 객체의 첫 번째 분류 결과를 top_class로 저장
                    if all_classifications[0]["classifications"]:
                        result["top_class"] = all_classifications[0]["classifications"][0]["class"]
                
                print(f"✅ YOLO Classification 적용 완료 ({len(detected_objects)}개 객체)")
            else:
                print(f"ℹ️ YOLO Classification: 감지된 객체가 없습니다")
        except ImportError:
            print(f"⚠️ YOLO Classification 모듈을 사용할 수 없습니다.")
        except Exception as e:
            print(f"⚠️ YOLO Classification 적용 중 오류: {e}")
            import traceback
            traceback.print_exc()
        
        # 2. YOLO Pose Estimation 적용
        try:
            from yolo_pose import apply_yolo_pose
            yolo_pose_model_path = current_dir / 'data' / 'yolo11n-pose.pt'
            final_img, poses = apply_yolo_pose(final_img, yolo_pose_model_path)
            if poses:
                result["poses"] = poses
                result["person_count"] = len(poses)
            print(f"✅ YOLO Pose Estimation 적용 완료")
        except ImportError:
            print(f"⚠️ YOLO Pose 모듈을 사용할 수 없습니다.")
        except Exception as e:
            print(f"⚠️ YOLO Pose Estimation 적용 중 오류: {e}")
        
        # 3. YOLO Segmentation 적용 (detection 결과와 매칭)
        try:
            from yolo_segment import apply_yolo_segmentation
            yolo_seg_model_path = current_dir / 'data' / 'yolo11n-seg.pt'
            # detected_objects를 전달하여 동일한 객체에만 segmentation 적용
            final_img, segments = apply_yolo_segmentation(final_img, yolo_seg_model_path, alpha=0.3, detected_objects=detected_objects)
            if segments:
                result["segments"] = segments
                result["object_count"] = len(segments)
            print(f"✅ YOLO Segmentation 적용 완료")
        except ImportError:
            print(f"⚠️ YOLO Segmentation 모듈을 사용할 수 없습니다.")
        except Exception as e:
            print(f"⚠️ YOLO Segmentation 적용 중 오류: {e}")
        
        # 최종 이미지를 base64로 변환하여 반환 (저장하지 않음)
        # 저장은 다운로드 버튼을 눌렀을 때만 수행됨
        try:
            result["detected_image_base64"] = image_to_base64(final_img)
            result["detected"] = True
            print(f"✅ 최종 이미지 처리 완료 (저장은 다운로드 버튼 클릭 시 수행)")
        except Exception as e:
            print(f"⚠️ 이미지 base64 변환 중 오류: {e}")
            import traceback
            traceback.print_exc()
    
    except Exception as e:
        print(f"⚠️ 얼굴 인식 중 오류 발생 (계속 진행): {e}")
        import traceback
        traceback.print_exc()
    
    return result

