# CORS 및 에러 수정 가이드

## 수정 사항

### 1. CORS 문제 해결
- Gateway 프록시 응답에 CORS 헤더 명시적 추가
- 모든 프록시 라우터에 적용

### 2. 답변 잘림 문제 해결
- `max_tokens`를 300에서 1000으로 증가
- 더 긴 답변을 받을 수 있음

### 3. 에러 처리 개선
- 상세한 로깅 추가
- 대화 이력 검증 로직 추가
- 에러 추적 정보 추가

## 재시작 방법

```powershell
cd ai.kroaddy.site

# 컨테이너 재시작
docker compose restart gateway chatbotservice

# 또는 재빌드
docker compose up --build -d gateway chatbotservice

# 로그 확인
docker compose logs -f chatbotservice
```

## 확인 사항

1. CORS 에러가 해결되었는지 확인
2. 긴 답변이 잘리지 않는지 확인
3. 두 번째 요청이 정상적으로 작동하는지 확인

