# Gateway 연결 상태

## ✅ 연결 완료

챗봇 서비스가 Gateway에 정상적으로 연결되었습니다.

## 🔗 연결 정보

### Gateway 프록시 경로
- **경로**: `/chatbot/*`
- **대상 서비스**: `http://chatbotservice:9004`
- **포트**: 9004

### 접근 URL

**개발 환경**:
- Gateway 경유: `http://localhost:9000/chatbot`
- 직접 접근: `http://localhost:9004`

**프로덕션 환경**:
- Gateway 경유: `https://api.kroaddy.site/chatbot` (예상)

## 📡 API 엔드포인트 (Gateway 경유)

### 1. 챗봇 대화
```http
POST http://localhost:9000/chatbot/chat
```

### 2. 가격 분석
```http
POST http://localhost:9000/chatbot/analyze-price
```

### 3. 헬스 체크
```http
GET http://localhost:9000/chatbot/health
```

## 🔧 설정 확인

### Gateway 설정 (`ai.kroaddy.site/gateway/app/main.py`)
- ✅ `CHATBOT_SERVICE_URL` 환경 변수 추가
- ✅ `chatbot_router` 프록시 라우터 추가
- ✅ `/chatbot` 경로로 라우팅 설정

### Docker Compose 설정 (`ai.kroaddy.site/docker-compose.yaml`)
- ✅ `chatbotservice` 서비스 추가
- ✅ 포트 매핑: `9004:9004`
- ✅ Gateway에 `depends_on` 추가
- ✅ 환경 변수 전달 설정

## 🧪 테스트

### Gateway 경유 테스트
```bash
# 챗봇 대화
curl -X POST "http://localhost:9000/chatbot/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "안녕, 오늘 날씨 어때?"
  }'

# 가격 분석
curl -X POST "http://localhost:9000/chatbot/analyze-price" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "아이폰 15",
    "price": 1200000,
    "context": "최신 스마트폰"
  }'
```

### 직접 접근 테스트
```bash
# 챗봇 대화
curl -X POST "http://localhost:9004/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "안녕, 오늘 날씨 어때?"
  }'
```

## 📝 프론트엔드 연동

프론트엔드는 Gateway 경유로 접근하는 것을 권장합니다:

```typescript
// .env.local
NEXT_PUBLIC_CHATBOT_API_URL=http://localhost:9000/chatbot

// 또는 프로덕션
NEXT_PUBLIC_CHATBOT_API_URL=https://api.kroaddy.site/chatbot
```

## ✅ 확인 사항

- [x] Gateway에 chatbotservice 프록시 추가
- [x] Docker Compose에 chatbotservice 추가
- [x] 환경 변수 설정
- [x] 포트 매핑 설정
- [x] 의존성 설정 (depends_on)

## 🚀 실행 방법

```bash
cd ai.kroaddy.site
docker compose up --build
```

모든 서비스가 함께 실행되며, Gateway를 통해 챗봇 서비스에 접근할 수 있습니다.

