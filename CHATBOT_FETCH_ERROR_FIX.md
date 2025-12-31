# Chatbot "Failed to fetch" 오류 해결 가이드

## 문제

프론트엔드에서 "Failed to fetch" 오류 발생:
- `TypeError: Failed to fetch`
- `app/home/page.tsx (719:7) @ handleSendMessage`

## 원인 분석

"Failed to fetch" 오류는 일반적으로 다음 원인으로 발생합니다:

1. **네트워크 연결 문제**
   - 게이트웨이가 실행되지 않음
   - chatbot-service가 실행되지 않음
   - 방화벽 또는 네트워크 설정 문제

2. **CORS 문제**
   - 게이트웨이의 CORS 설정이 프론트엔드 Origin을 허용하지 않음

3. **URL 설정 문제**
   - 잘못된 API URL
   - 환경 변수 설정 오류

## 해결 방법

### 1. 서비스 실행 확인

다음 서비스들이 모두 실행 중인지 확인:

```powershell
# 게이트웨이 (포트 8080)
# 새 터미널에서
.\scripts\start-java-gateway.ps1

# chatbot-service (포트 9004)
# 새 터미널에서
cd ai.kroaddy.site/services/chatbotservice
python -m uvicorn app.main:app --host 0.0.0.0 --port 9004
```

### 2. 서비스 상태 확인

브라우저에서 직접 확인:

```bash
# 게이트웨이 확인
http://localhost:8080/docs

# chatbot-service 직접 확인
http://localhost:9004/health

# 게이트웨이를 통한 chatbot 확인
http://localhost:8080/api/chatbot/health
```

### 3. 프론트엔드 환경 변수 설정

`www.kroaddy.site/.env.local` 파일 생성 (없는 경우):

```env
NEXT_PUBLIC_CHATBOT_API_URL=http://localhost:8080/api/chatbot
NEXT_PUBLIC_API_BASE_URL=http://localhost:8080
```

**중요**: Next.js는 `.env.local` 파일을 자동으로 로드합니다. 파일을 생성한 후 **Next.js 개발 서버를 재시작**해야 합니다.

### 4. 브라우저 콘솔 확인

브라우저 개발자 도구(F12)의 콘솔에서 다음 로그를 확인:

```
Chatbot API 호출: http://localhost:8080/api/chatbot/chat
```

이 로그가 출력되지 않으면 코드가 실행되지 않은 것입니다.

### 5. 네트워크 탭 확인

브라우저 개발자 도구의 Network 탭에서:
- 요청이 전송되는지 확인
- 요청 URL이 올바른지 확인
- 응답 상태 코드 확인 (404, 500, CORS 오류 등)

## 수정 사항

1. **에러 핸들링 개선**: 더 자세한 에러 로그 추가
2. **디버깅 로그 추가**: API 호출 URL 로그 출력
3. **CORS 설정 확인**: `credentials: 'include'` 추가

## 다음 단계

1. **Next.js 개발 서버 재시작**:
   ```powershell
   # Next.js 서버 중지 후 재시작
   cd www.kroaddy.site
   npm run dev
   ```

2. **브라우저 콘솔 확인**:
   - F12 → Console 탭
   - "Chatbot API 호출" 로그 확인
   - 에러 메시지 확인

3. **Network 탭 확인**:
   - F12 → Network 탭
   - `/api/chatbot/chat` 요청 확인
   - 요청 상태 및 응답 확인

## 문제가 계속되면

1. **게이트웨이 로그 확인**: 게이트웨이 터미널에서 요청 로그 확인
2. **chatbot-service 로그 확인**: chatbot-service 터미널에서 요청 로그 확인
3. **직접 테스트**: 브라우저에서 `http://localhost:8080/api/chatbot/health` 직접 접속

---

**작성일**: 2025년 12월

