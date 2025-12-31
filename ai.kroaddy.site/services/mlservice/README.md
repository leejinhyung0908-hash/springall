# ML Service

타이타닉 데이터를 활용한 머신러닝 서비스

## 빌드 및 실행

### Docker를 사용한 빌드

```bash
# 이미지 빌드
docker build -t mlservice:latest .

# 컨테이너 실행
docker run -d -p 9010:9010 --name mlservice mlservice:latest
```

### Docker Compose를 사용한 실행

```bash
# 서비스 시작
docker-compose up -d

# 서비스 중지
docker-compose down

# 로그 확인
docker-compose logs -f
```

## API 엔드포인트

- `GET /` - 서비스 상태 확인
- `GET /health` - 헬스 체크
- `GET /search` - 승객 검색 (GET 방식)
- `POST /search` - 승객 검색 (POST 방식)
- `GET /top/{n}` - 상위 N명의 승객 정보
- `GET /stats` - 통계 정보

## 환경 변수

- `PYTHONUNBUFFERED=1` - Python 출력 버퍼링 비활성화

## 포트

- `9010` - FastAPI 서비스 포트

