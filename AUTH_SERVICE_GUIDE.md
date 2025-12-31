# Auth Service 실행 가이드

## 개요

Auth Service는 **인증(auth)**과 **로그(log)** 기능을 모두 제공하는 단일 서비스입니다.
- **포트**: 8081
- **Auth API**: `/api/auth/**`
- **Log API**: `/api/log/**`

## 빠른 시작

### 방법 1: 스크립트 사용 (권장)

**Windows:**
```powershell
.\scripts\start-auth-service.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/start-auth-service.sh
./scripts/start-auth-service.sh
```

### 방법 2: 수동 실행

**루트 프로젝트에서:**
```bash
cd service.kroaddy.site
./gradlew :auth-service:bootRun
```

**Windows:**
```powershell
cd service.kroaddy.site
.\gradlew.bat :auth-service:bootRun
```

**auth-service 디렉토리에서 직접:**
```bash
cd service.kroaddy.site/auth-service
./gradlew bootRun
```

**Windows:**
```powershell
cd service.kroaddy.site\auth-service
.\gradlew.bat bootRun
```

## 서비스 확인

### 1. 서비스 상태 확인

```bash
# Health Check
curl http://localhost:8081/actuator/health

# 또는 브라우저에서
# http://localhost:8081/actuator/health
```

### 2. Auth API 테스트

```bash
# 카카오 로그인 URL 가져오기
curl http://localhost:8081/api/auth/kakao/login

# 네이버 로그인 URL 가져오기
curl http://localhost:8081/api/auth/naver/login

# 구글 로그인 URL 가져오기
curl http://localhost:8081/api/auth/google/login
```

### 3. Log API 테스트

```bash
# 로그인 로그 기록
curl -X POST http://localhost:8081/api/log/login \
  -H "Content-Type: application/json" \
  -d '{"userId": "test-user", "loginType": "kakao", "timestamp": "2025-01-01T00:00:00Z"}'
```

### 4. Gateway를 통한 접근

Gateway가 실행 중이면:

```bash
# Auth API (Gateway 경유)
curl http://localhost:8080/api/auth/kakao/login

# Log API (Gateway 경유)
curl -X POST http://localhost:8080/api/log/login \
  -H "Content-Type: application/json" \
  -d '{"userId": "test-user", "loginType": "kakao"}'
```

## 환경 변수 설정

### 필수 환경 변수

`.env` 파일에 다음 변수들을 설정하세요:

```bash
# JWT 설정
JWT_SECRET=your-secret-key-min-32-characters-long

# 소셜 로그인 API 키
KAKAO_REST_API_KEY=your_kakao_api_key
KAKAO_REDIRECT_URI=http://localhost:8080/api/auth/kakao/callback

NAVER_CLIENT_ID=your_naver_client_id
NAVER_CLIENT_SECRET=your_naver_client_secret
NAVER_REDIRECT_URI=http://localhost:8080/api/auth/naver/callback

GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8080/api/auth/google/callback

# 프론트엔드 설정
FRONT_LOGIN_CALLBACK_URL=http://localhost:3000
```

### 선택적 환경 변수

```bash
# JWT 만료 시간 (기본값: 24시간)
JWT_EXPIRATION=86400000

# Refresh Token 만료 시간 (기본값: 7일)
JWT_REFRESH_EXPIRATION=604800000

# 쿠키 설정
COOKIE_SECURE=false  # 개발: false, 프로덕션: true
COOKIE_SAME_SITE=Lax  # Lax, Strict, None
```

## API 엔드포인트

### Auth API (`/api/auth/**`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| GET | `/api/auth/kakao/login` | 카카오 로그인 URL 반환 |
| GET | `/api/auth/kakao/callback` | 카카오 로그인 콜백 처리 |
| GET | `/api/auth/naver/login` | 네이버 로그인 URL 반환 |
| GET | `/api/auth/naver/callback` | 네이버 로그인 콜백 처리 |
| GET | `/api/auth/google/login` | 구글 로그인 URL 반환 |
| GET | `/api/auth/google/callback` | 구글 로그인 콜백 처리 |
| POST | `/api/auth/logout` | 로그아웃 |

### Log API (`/api/log/**`)

| 메서드 | 경로 | 설명 |
|--------|------|------|
| POST | `/api/log/login` | 로그인 로그 기록 |

## 문제 해결

### 포트 충돌

```bash
# Windows
netstat -ano | findstr :8081
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8081 | xargs kill -9
```

### 빌드 오류

```bash
# Gradle 캐시 정리
cd service.kroaddy.site
./gradlew clean

# 다시 빌드
./gradlew :auth-service:build
```

### 환경 변수 오류

- `.env` 파일이 루트 디렉토리에 있는지 확인
- 환경 변수 이름이 정확한지 확인
- 필수 환경 변수가 설정되어 있는지 확인

## 참고사항

1. **Auth Service = Auth + Log**
   - 별도의 log-service가 없습니다
   - auth-service 하나로 auth와 log 기능을 모두 제공합니다

2. **포트 8081**
   - auth-service와 log-service는 같은 포트(8081)를 사용합니다
   - Gateway 설정에서 둘 다 `http://localhost:8081`로 라우팅됩니다

3. **멀티 프로젝트 구조**
   - `service.kroaddy.site`는 루트 프로젝트입니다
   - `auth-service`는 서브프로젝트입니다
   - 루트에서 `:auth-service:bootRun`으로 실행합니다

---

**작성일**: 2025년 1월

