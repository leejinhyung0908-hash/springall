# ML Service 실행 가이드

## 방법 1: Docker Compose 사용 (권장)

### 1. Docker Desktop 실행 확인
- Docker Desktop이 실행 중이어야 합니다.

### 2. 서비스 시작
```bash
# 프로젝트 루트 디렉토리에서 실행
cd C:\Users\hi\Desktop\test3\kroaddy_project_dacon

# ML 서비스만 실행 (백그라운드)
docker-compose --profile ai up ml-service -d

# ML 서비스만 실행 (포그라운드 - 로그 확인)
docker-compose --profile ai up ml-service

# 모든 AI 서비스 실행
docker-compose --profile ai up -d
```

### 3. 서비스 확인
```bash
# 서비스 상태 확인
docker-compose --profile ai ps ml-service

# 로그 확인
docker-compose --profile ai logs -f ml-service

# 서비스 중지
docker-compose --profile ai stop ml-service

# 서비스 재시작
docker-compose --profile ai restart ml-service

# 서비스 중지 및 컨테이너 제거
docker-compose --profile ai down ml-service
```

### 4. 접속 URL
- 서비스 URL: `http://localhost:9010`
- API 문서: `http://localhost:9010/docs`
- NLTK 서비스: `http://localhost:9010/nltk/`
- API Gateway를 통한 접속: `http://localhost:8080/api/ml/nltk/`

---

## 방법 2: 직접 Python으로 실행 (개발용)

### 1. 가상환경 활성화 (선택사항)
```bash
# conda 환경 사용 시
conda activate torch313

# 또는 venv 사용 시
# python -m venv venv
# venv\Scripts\activate  # Windows
```

### 2. 의존성 설치 확인
```bash
cd ai.kroaddy.site/services/mlservice
pip install -r requirements.txt
```

### 3. 서비스 실행
```bash
# 방법 A: uvicorn 직접 실행
cd ai.kroaddy.site/services/mlservice
uvicorn app.main:app --host 0.0.0.0 --port 9010 --reload

# 방법 B: Python 스크립트 실행
cd ai.kroaddy.site/services/mlservice
python -m app.main

# 방법 C: main.py 직접 실행
cd ai.kroaddy.site/services/mlservice/app
python main.py
```

### 4. 접속 URL
- 서비스 URL: `http://localhost:9010`
- API 문서: `http://localhost:9010/docs`
- NLTK 서비스: `http://localhost:9010/nltk/`

---

## 방법 3: 코드 변경 후 재시작

### Docker Compose 사용 시:
```bash
# 코드 변경 후 재빌드 및 재시작
docker-compose --profile ai up ml-service --build -d

# 또는 완전히 재빌드
docker-compose --profile ai build --no-cache ml-service
docker-compose --profile ai up ml-service -d
```

### Python 직접 실행 시:
- `--reload` 옵션을 사용하면 코드 변경 시 자동 재시작됩니다.
- 또는 서비스를 중지(Ctrl+C) 후 다시 실행하세요.

---

## 서비스 확인

### 1. 헬스 체크
```bash
# 브라우저에서
http://localhost:9010/

# 또는 curl 사용
curl http://localhost:9010/
```

### 2. API 문서 확인
```bash
# Swagger UI
http://localhost:9010/docs

# ReDoc
http://localhost:9010/redoc
```

### 3. NLTK 서비스 테스트
```bash
# 서비스 상태 확인
curl http://localhost:9010/nltk/

# 말뭉치 파일 목록 조회
curl http://localhost:9010/nltk/corpus/fileids
```

---

## 문제 해결

### 포트가 이미 사용 중인 경우
```bash
# Windows에서 포트 사용 확인
netstat -ano | findstr :9010

# 프로세스 종료 (PID 확인 후)
taskkill /PID <PID> /F
```

### Docker 컨테이너 로그 확인
```bash
docker-compose --profile ai logs -f ml-service
```

### 컨테이너 내부 접속
```bash
docker-compose --profile ai exec ml-service bash
```

