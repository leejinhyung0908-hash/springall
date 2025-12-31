#!/bin/bash

# Python 3.12로 venv 생성
python3.12 -m venv venv

# venv 활성화
source venv/bin/activate  # Linux/Mac
# 또는
# venv\Scripts\activate  # Windows

# pip 업그레이드
pip install --upgrade pip

# PyTorch 설치 (CUDA 12.4 지원, PyTorch 2.4+)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# YOLO11 (ultralytics 최신 버전) 설치
pip install ultralytics

# 추가 유용한 패키지들 (선택사항)
pip install numpy opencv-python pillow matplotlib

echo "가상환경 설정이 완료되었습니다!"

