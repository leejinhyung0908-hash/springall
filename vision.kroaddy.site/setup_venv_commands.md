# Python 3.12 + PyTorch 2.4+ + CUDA 12.4 + YOLO11 가상환경 설정

## Windows (PowerShell)

```powershell
# 1. Python 3.12로 venv 생성
python3.12 -m venv venv

# 2. venv 활성화
.\venv\Scripts\Activate.ps1

# 3. pip 업그레이드
python -m pip install --upgrade pip

# 4. PyTorch 설치 (CUDA 12.4 지원, PyTorch 2.4+)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 5. YOLO11 (ultralytics 최신 버전) 설치
pip install ultralytics

# 6. 추가 유용한 패키지들 (선택사항)
pip install numpy opencv-python pillow matplotlib
```

## Linux/Mac

```bash
# 1. Python 3.12로 venv 생성
python3.12 -m venv venv

# 2. venv 활성화
source venv/bin/activate

# 3. pip 업그레이드
pip install --upgrade pip

# 4. PyTorch 설치 (CUDA 12.4 지원, PyTorch 2.4+)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# 5. YOLO11 (ultralytics 최신 버전) 설치
pip install ultralytics

# 6. 추가 유용한 패키지들 (선택사항)
pip install numpy opencv-python pillow matplotlib
```

## CUDA 12.1을 사용하는 경우

CUDA 12.1을 사용해야 한다면 PyTorch 설치 명령어를 다음과 같이 변경:

```bash
# CUDA 12.1용 PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

## 설치 확인

```python
import torch
import ultralytics

print(f"PyTorch 버전: {torch.__version__}")
print(f"CUDA 사용 가능: {torch.cuda.is_available()}")
print(f"CUDA 버전: {torch.version.cuda if torch.cuda.is_available() else 'N/A'}")
print(f"Ultralytics 버전: {ultralytics.__version__}")
```

## 참고사항

- Python 3.12가 시스템에 설치되어 있어야 합니다.
- CUDA 12.1 또는 12.4가 시스템에 설치되어 있어야 GPU를 사용할 수 있습니다.
- CPU만 사용하는 경우 PyTorch 설치 명령어를 다음과 같이 변경:
  ```bash
  pip install torch torchvision torchaudio
  ```

