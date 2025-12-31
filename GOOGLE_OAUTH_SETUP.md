# Google OAuth 설정 가이드

## 문제

Google 로그인 시 "Missing required parameter: client_id" 오류가 발생합니다.

## 원인

`GOOGLE_CLIENT_ID` 환경 변수가 설정되지 않았거나 빈 값입니다.

## 해결 방법

### 1. Google Cloud Console에서 OAuth 2.0 클라이언트 ID 생성

1. [Google Cloud Console](https://console.cloud.google.com/) 접속
2. 프로젝트 선택 또는 생성
3. **API 및 서비스** > **사용자 인증 정보** 이동
4. **사용자 인증 정보 만들기** > **OAuth 클라이언트 ID** 선택
5. 애플리케이션 유형: **웹 애플리케이션**
6. 승인된 리디렉션 URI 추가:
   - `http://localhost:8080/api/auth/google/callback` (로컬 개발)
   - `https://yourdomain.com/api/auth/google/callback` (프로덕션)
7. 클라이언트 ID와 클라이언트 보안 비밀번호 복사

### 2. 환경 변수 설정

#### 방법 A: .env 파일 사용 (권장)

프로젝트 루트 디렉토리에 `.env` 파일 생성:

```bash
# Google OAuth 설정
GOOGLE_CLIENT_ID=your-google-client-id-here.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret-here
GOOGLE_REDIRECT_URI=http://localhost:8080/api/auth/google/callback

# 다른 소셜 로그인 (선택사항)
KAKAO_REST_API_KEY=your-kakao-api-key
NAVER_CLIENT_ID=your-naver-client-id
NAVER_CLIENT_SECRET=your-naver-client-secret

# JWT 설정
JWT_SECRET=your-secret-key-min-32-characters-long

# 프론트엔드 설정
FRONT_LOGIN_CALLBACK_URL=http://localhost:3000
```

#### 방법 B: 환경 변수 직접 설정

**Windows PowerShell:**
```powershell
$env:GOOGLE_CLIENT_ID = "your-google-client-id-here.apps.googleusercontent.com"
$env:GOOGLE_CLIENT_SECRET = "your-google-client-secret-here"
$env:GOOGLE_REDIRECT_URI = "http://localhost:8080/api/auth/google/callback"
```

**Linux/Mac:**
```bash
export GOOGLE_CLIENT_ID="your-google-client-id-here.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="your-google-client-secret-here"
export GOOGLE_REDIRECT_URI="http://localhost:8080/api/auth/google/callback"
```

### 3. Auth Service 재시작

환경 변수를 설정한 후 auth-service를 재시작하세요:

```powershell
# Windows
.\scripts\start-auth-service.ps1
```

```bash
# Linux/Mac
./scripts/start-auth-service.sh
```

## 확인

### 1. 환경 변수 확인

**Windows PowerShell:**
```powershell
echo $env:GOOGLE_CLIENT_ID
```

**Linux/Mac:**
```bash
echo $GOOGLE_CLIENT_ID
```

### 2. Auth API 테스트

```bash
# Google 로그인 URL 가져오기
curl http://localhost:8081/api/auth/google/login

# 또는 Gateway를 통한 접근
curl http://localhost:8080/api/auth/google/login
```

응답 예시:
```json
{
  "authUrl": "https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_CLIENT_ID&redirect_uri=..."
}
```

### 3. 브라우저에서 테스트

1. `http://localhost:8080/api/auth/google/login` 접속
2. `authUrl` 값을 복사하여 브라우저에서 열기
3. Google 로그인 화면이 정상적으로 표시되는지 확인

## 문제 해결

### client_id가 여전히 누락되는 경우

1. **환경 변수가 제대로 로드되었는지 확인**
   ```powershell
   # auth-service 실행 전에 환경 변수 확인
   echo $env:GOOGLE_CLIENT_ID
   ```

2. **application.yaml 확인**
   - `service.kroaddy.site/auth-service/src/main/resources/application.yaml`
   - `google.client-id: ${GOOGLE_CLIENT_ID:}` 형식 확인

3. **auth-service 재시작**
   - 환경 변수를 변경한 후 반드시 재시작

4. **로그 확인**
   - auth-service 로그에서 오류 메시지 확인
   - `googleClientId` 값이 null이거나 빈 문자열인지 확인

### 리디렉션 URI 불일치 오류

Google Cloud Console에서 설정한 리디렉션 URI와 `GOOGLE_REDIRECT_URI` 환경 변수가 정확히 일치해야 합니다:

- ✅ `http://localhost:8080/api/auth/google/callback`
- ❌ `http://localhost:8080/api/auth/google/callback/` (끝에 슬래시)
- ❌ `http://127.0.0.1:8080/api/auth/google/callback` (localhost와 다름)

## 보안 주의사항

1. **`.env` 파일을 Git에 커밋하지 마세요**
   - `.gitignore`에 `.env` 추가 확인

2. **프로덕션 환경**
   - 환경 변수를 안전하게 관리 (AWS Secrets Manager, Azure Key Vault 등)
   - `COOKIE_SECURE=true` 설정
   - HTTPS 사용 필수

## 참고

- [Google OAuth 2.0 문서](https://developers.google.com/identity/protocols/oauth2)
- [Spring Boot 환경 변수 설정](https://docs.spring.io/spring-boot/docs/current/reference/html/features.html#features.external-config)

---

**작성일**: 2025년 1월

