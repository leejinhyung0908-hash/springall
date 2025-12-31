"""
YOLO 설치 확인 및 Hello YOLO 테스트 코드
데이터 폴더의 이미지를 처리하고 결과를 save 폴더에 저장
"""
import os
from pathlib import Path

try:
    import ultralytics
    from ultralytics import YOLO
    import torch
    
    print("=" * 50)
    print("Hello YOLO!")
    print("=" * 50)
    
    # 버전 정보 출력
    print(f"Ultralytics 버전: {ultralytics.__version__}")
    print(f"PyTorch 버전: {torch.__version__}")
    print(f"CUDA 사용 가능: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"CUDA 버전: {torch.version.cuda}")
        print(f"GPU 디바이스: {torch.cuda.get_device_name(0)}")
    else:
        print("CUDA: CPU 모드로 실행됩니다.")
    
    print("=" * 50)
    print("YOLO가 성공적으로 설치되었습니다! 🎉")
    print("=" * 50)
    
    # 경로 설정
    current_dir = Path(__file__).parent
    data_dir = current_dir / 'data'
    save_dir = current_dir / 'save'
    
    # save 폴더가 없으면 생성
    save_dir.mkdir(exist_ok=True)
    
    # 모델 경로
    model_path = data_dir / 'yolo11n.pt'
    image_path = data_dir / 'bus.jpg'
    
    print(f"\n데이터 경로: {data_dir}")
    print(f"저장 경로: {save_dir}")
    print(f"모델 경로: {model_path}")
    print(f"이미지 경로: {image_path}")
    
    # 모델 로드
    if not model_path.exists():
        print(f"\n⚠️ 모델 파일을 찾을 수 없습니다: {model_path}")
        print("   기본 모델을 다운로드합니다...")
        model = YOLO('yolo11n.pt')
    else:
        print(f"\n✅ 모델 파일 로드 중: {model_path}")
        model = YOLO(str(model_path))
    
    print(f"모델 정보: {model.model_name}")
    
    # 이미지 처리
    if not image_path.exists():
        print(f"\n❌ 이미지 파일을 찾을 수 없습니다: {image_path}")
    else:
        print(f"\n🖼️ 이미지 처리 중: {image_path}")
        
        # YOLO 추론 실행 및 결과 저장
        results = model(str(image_path))
        
        # 결과 저장
        for i, result in enumerate(results):
            # 이미지에 바운딩 박스가 그려진 결과 저장
            output_path = save_dir / f'bus_result_{i}.jpg'
            result.save(str(output_path))
            print(f"✅ 결과 저장: {output_path}")
            
            # 검출된 객체 정보 출력
            if result.boxes is not None:
                print(f"\n검출된 객체 수: {len(result.boxes)}")
                for box in result.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    class_name = model.names[cls]
                    print(f"  - {class_name}: {conf:.2%} 신뢰도")
        
        print(f"\n✅ 모든 결과가 {save_dir} 폴더에 저장되었습니다!")
    
except ImportError as e:
    print("=" * 50)
    print("❌ YOLO가 설치되지 않았습니다!")
    print("=" * 50)
    print("설치 명령어:")
    print("  pip install ultralytics")
    print("=" * 50)
    print(f"오류 상세: {e}")
except Exception as e:
    print("=" * 50)
    print("❌ 오류가 발생했습니다!")
    print("=" * 50)
    print(f"오류 상세: {e}")
    import traceback
    traceback.print_exc()

