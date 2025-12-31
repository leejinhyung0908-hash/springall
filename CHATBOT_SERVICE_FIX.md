# Chatbot Service 404 오류 해결

## 문제

프론트엔드에서 OpenAI 응답 시 404 오류 발생:
- `HTTP 에러 응답: 404 "{\"detail\":\"Not Found\"}"`

## 원인

1. **프론트엔드가 게이트웨이를 거치지 않고 직접 호출**
   - 기존: `http://localhost:9000/chatbot/chat`
   - 수정: `http://localhost:8080/api/chatbot/chat` (게이트웨이를 통해)

2. **chatbot-service가 실행되지 않음**
   - 게이트웨이는 `/api/chatbot/**` → `http://localhost:9004`로 라우팅
   - chatbot-service(포트 9004)가 실행되지 않으면 404 오류 발생

## 해결 방법

### 1. 프론트엔드 코드 수정 (완료)

`www.kroaddy.site/app/home/page.tsx`:
```typescript
// 수정 전
const CHATBOT_API_URL = process.env.NEXT_PUBLIC_CHATBOT_API_URL || 'http://localhost:9000/chatbot';

// 수정 후
const CHATBOT_API_URL = process.env.NEXT_PUBLIC_CHATBOT_API_URL || 'http://localhost:8080/api/chatbot';
```

### 2. Chatbot Service 실행

chatbot-service를 실행해야 합니다:

```powershell
# Python 서비스 실행 스크립트 사용
.\scripts\start-python-services.ps1

# 또는 직접 실행
cd ai.kroaddy.site/services/chatbotservice
python -m uvicorn app.main:app --host 0.0.0.0 --port 9004
```

### 3. 요청 흐름 확인

1. **프론트엔드**: `http://localhost:8080/api/chatbot/chat` 호출
2. **게이트웨이**: `/api/chatbot/chat` → StripPrefix(2) → `/chat`만 남음
3. **chatbot-service**: `http://localhost:9004/chat`으로 전달

## 확인 방법

1. **게이트웨이 실행 확인**:
   ```bash
   curl http://localhost:8080/api/chatbot/health
   ```

2. **chatbot-service 직접 확인**:
   ```bash
   curl http://localhost:9004/health
   ```

3. **게이트웨이를 통한 호출 확인**:
   ```bash
   curl -X POST http://localhost:8080/api/chatbot/chat \
     -H "Content-Type: application/json" \
     -d '{"message": "안녕하세요"}'
   ```

## 환경 변수 설정 (선택)

프론트엔드 `.env.local` 파일에 설정:
```env
NEXT_PUBLIC_CHATBOT_API_URL=http://localhost:8080/api/chatbot
```

---

**작성일**: 2025년 12월

