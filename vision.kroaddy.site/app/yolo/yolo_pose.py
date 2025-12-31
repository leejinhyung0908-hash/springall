"""
YOLO Pose Estimation 기능 모듈
포즈 추정을 수행합니다.
"""
import cv2
import numpy as np
from pathlib import Path
import tempfile

# YOLO Pose 모델 전역 변수
_yolo_pose_model = None
_yolo_pose_model_path = None


def get_yolo_pose_model(model_path: Path = None):
    """YOLO Pose 모델 로드 (싱글톤 패턴)"""
    global _yolo_pose_model, _yolo_pose_model_path
    
    try:
        from ultralytics import YOLO
    except ImportError:
        print("⚠️ Ultralytics가 설치되지 않았습니다. YOLO Pose를 사용할 수 없습니다.")
        return None
    
    # 모델 경로 설정
    if model_path is None:
        # 기본 모델 경로: 현재 스크립트의 data 폴더
        current_dir = Path(__file__).parent
        model_path = current_dir / 'data' / 'yolo11n-pose.pt'
    
    # 이미 로드된 모델이 있고 경로가 같으면 재사용
    if _yolo_pose_model is not None and _yolo_pose_model_path == str(model_path):
        return _yolo_pose_model
    
    # 모델 파일 확인
    if not model_path.exists():
        print(f"⚠️ YOLO Pose 모델 파일을 찾을 수 없습니다: {model_path}")
        print("   기본 모델을 다운로드합니다...")
        try:
            _yolo_pose_model = YOLO('yolo11n-pose.pt')
            _yolo_pose_model_path = 'yolo11n-pose.pt'
            print("✅ YOLO Pose 모델 로드 완료 (기본 모델)")
            return _yolo_pose_model
        except Exception as e:
            print(f"⚠️ YOLO Pose 모델 로드 실패: {e}")
            return None
    
    try:
        _yolo_pose_model = YOLO(str(model_path))
        _yolo_pose_model_path = str(model_path)
        print(f"✅ YOLO Pose 모델 로드 완료: {model_path}")
        return _yolo_pose_model
    except Exception as e:
        print(f"⚠️ YOLO Pose 모델 로드 실패: {e}")
        import traceback
        traceback.print_exc()
        return None


def apply_yolo_pose(image: np.ndarray, model_path: Path = None) -> tuple:
    """
    이미지에 YOLO Pose Estimation을 적용하여 포즈 추정 결과 반환
    원본 이미지의 색상을 유지하면서 키포인트와 스켈레톤만 그립니다.
    
    Args:
        image: OpenCV 이미지 (numpy array, BGR 형식)
        model_path: YOLO 모델 경로 (None이면 기본 경로 사용)
    
    Returns:
        tuple: (result_image, poses)
            - result_image: 포즈 추정 결과가 그려진 이미지 (BGR 형식, 원본 색상 유지)
            - poses: 포즈 정보 리스트 [{"person_id": int, "keypoints": [...], "confidence": float}, ...]
    """
    try:
        model = get_yolo_pose_model(model_path)
        if model is None:
            print("⚠️ YOLO Pose 모델을 사용할 수 없어 원본 이미지를 반환합니다.")
            return image, []
        
        # 원본 이미지 복사 (색상 유지)
        result_image = image.copy()
        
        # YOLO Pose 실행
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_file:
            tmp_path = Path(tmp_file.name)
            try:
                # 이미지를 임시 파일로 저장
                cv2.imwrite(str(tmp_path), image)
                
                # YOLO Pose 추론 실행
                results = model(str(tmp_path))
                
                poses = []
                
                # 결과 처리
                if results and len(results) > 0:
                    result = results[0]
                    
                    # Keypoints 정보 가져오기
                    if hasattr(result, 'keypoints') and result.keypoints is not None:
                        keypoints_data = result.keypoints
                        
                        # 키포인트 데이터 형태 확인 및 처리
                        if hasattr(keypoints_data, 'xy') and keypoints_data.xy is not None:
                            # xy: (num_persons, num_keypoints, 2) - x, y 좌표만
                            kpts_xy = keypoints_data.xy.cpu().numpy()  # (num_persons, num_keypoints, 2)
                            kpts_conf = keypoints_data.conf.cpu().numpy() if hasattr(keypoints_data, 'conf') and keypoints_data.conf is not None else None
                            
                            num_persons = kpts_xy.shape[0] if len(kpts_xy.shape) > 0 else 0
                            num_keypoints = kpts_xy.shape[1] if len(kpts_xy.shape) > 1 else 0
                            
                            # 스켈레톤 연결 정의 (COCO 포맷 기준)
                            skeleton_connections = [
                                (0, 1), (0, 2), (1, 3), (2, 4),  # 머리-목-어깨
                                (5, 6), (5, 7), (7, 9), (6, 8), (8, 10),  # 어깨-팔꿈치-손목
                                (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),  # 엉덩이-무릎-발목
                                (5, 11), (6, 12)  # 어깨-엉덩이
                            ]
                            
                            # 각 사람의 포즈 정보 추출
                            for person_id in range(num_persons):
                                kpts_xy_person = kpts_xy[person_id]  # (num_keypoints, 2)
                                kpts_conf_person = kpts_conf[person_id] if kpts_conf is not None else None  # (num_keypoints,)
                                
                                # 키포인트 그리기
                                keypoint_list = []
                                kpts = np.zeros((num_keypoints, 3))
                                
                                for i in range(num_keypoints):
                                    if i < kpts_xy_person.shape[0]:
                                        x = int(float(kpts_xy_person[i, 0]))
                                        y = int(float(kpts_xy_person[i, 1]))
                                        conf = float(kpts_conf_person[i]) if kpts_conf_person is not None and i < len(kpts_conf_person) else 0.0
                                        
                                        kpts[i, 0] = x
                                        kpts[i, 1] = y
                                        kpts[i, 2] = conf
                                        
                                        if conf > 0.5:  # 신뢰도 임계값
                                            keypoint_list.append({"x": x, "y": y, "confidence": conf})
                                            # 키포인트 그리기
                                            cv2.circle(result_image, (x, y), 5, (0, 255, 0), -1)
                                
                                # 스켈레톤 그리기
                                for start_idx, end_idx in skeleton_connections:
                                    if (start_idx < kpts.shape[0] and 
                                        end_idx < kpts.shape[0] and
                                        kpts[start_idx, 2] > 0.5 and 
                                        kpts[end_idx, 2] > 0.5):
                                        start_x = int(float(kpts[start_idx, 0]))
                                        start_y = int(float(kpts[start_idx, 1]))
                                        end_x = int(float(kpts[end_idx, 0]))
                                        end_y = int(float(kpts[end_idx, 1]))
                                        cv2.line(result_image, (start_x, start_y), (end_x, end_y), (255, 0, 0), 2)
                                
                                # 바운딩 박스 및 신뢰도 (있는 경우)
                                confidence = 0.0
                                bbox = None
                                if hasattr(result, 'boxes') and result.boxes is not None and person_id < len(result.boxes.data):
                                    box = result.boxes.data[person_id]
                                    if box is not None:
                                        box_np = box.cpu().numpy()
                                        if len(box_np) >= 4:
                                            x1 = int(float(box_np[0]))
                                            y1 = int(float(box_np[1]))
                                            x2 = int(float(box_np[2]))
                                            y2 = int(float(box_np[3]))
                                            cv2.rectangle(result_image, (x1, y1), (x2, y2), (0, 0, 255), 2)
                                            bbox = {"x1": x1, "y1": y1, "x2": x2, "y2": y2}
                                        if len(box_np) >= 5:
                                            confidence = float(box_np[4])
                                
                                poses.append({
                                    "person_id": person_id,
                                    "keypoints": keypoint_list,
                                    "keypoint_count": len(keypoint_list),
                                    "confidence": confidence,
                                    "bbox": bbox
                                })
                            
                            print(f"✅ YOLO Pose: {len(poses)}명의 사람 포즈 검출")
                
                return result_image, poses
            finally:
                # 임시 파일 삭제
                if tmp_path.exists():
                    try:
                        tmp_path.unlink()
                    except:
                        pass
    
    except Exception as e:
        print(f"⚠️ YOLO Pose 추론 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return image, []


def estimate_pose(image_path: Path, model_path: Path = None) -> dict:
    """
    이미지 파일에 YOLO Pose Estimation을 적용
    
    Args:
        image_path: 이미지 파일 경로
        model_path: YOLO 모델 경로
    
    Returns:
        dict: 포즈 추정 결과
            - success: bool
            - poses: list
            - person_count: int
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
                "poses": []
            }
        
        # Pose Estimation 적용
        result_image, poses = apply_yolo_pose(img, model_path)
        
        return {
            "success": True,
            "poses": poses,
            "person_count": len(poses)
        }
    
    except Exception as e:
        print(f"⚠️ 포즈 추정 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "message": str(e),
            "poses": []
        }
