# 환경 변수 디버깅 가이드

## 문제

`.env` 파일이 있지만 Spring Boot가 환경 변수를 읽지 못하는 경우

## 확인 방법

### 1. .env 파일 위치 확인

`.env` 파일이 **프로젝트 루트 디렉토리**에 있어야 합니다:

```
kroaddy_project_dacon/
├── .env                    ← 여기에 있어야 함
├── docker-compose.yaml
├── api.kroaddy.site/
├── service.kroaddy.site/
└── ...
```

### 2. .env 파일 형식 확인

`.env` 파일 형식이 올바른지 확인:

```bash
# 올바른 형식
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# 잘못된 형식 (공백 주의)
GOOGLE_CLIENT_ID = your-client-id  # 공백 있으면 안됨
GOOGLE_CLIENT_ID="your-client-id"  # 따옴표는 제거됨 (괜찮음)
```

### 3. 환경 변수 로드 확인

스크립트 실행 시 환경 변수가 로드되는지 확인:

```powershell
# 스크립트 실행 후 출력 확인
.\scripts\start-auth-service.ps1

# 출력 예시:
# .env 파일 발견, 환경 변수 로드 중...
#   GOOGLE_CLIENT_ID = your-client-id...
# 환경 변수 로드 완료
# GOOGLE_CLIENT_ID 설정됨: your-client-id...
```

### 4. 수동으로 환경 변수 확인

**PowerShell:**
```powershell
# .env 파일 수동 로드
Get-Content .env | ForEach-Object {
    if ($_ -and $_ -notmatch '^\s*#' -and $_ -match '^([^=]+)=(.*)$') {
        $key = $matches[1].Trim()
        $value = $matches[2].Trim()
        if ($value -match '^["''](.*)["'']$') {
            $value = $matches[1]
        }
        [Environment]::SetEnvironmentVariable($key, $value, 'Process')
    }
}

# 확인
echo $env:GOOGLE_CLIENT_ID
```

**Linux/Mac:**
```bash
# .env 파일 수동 로드
export $(cat .env | grep -v '^#' | xargs)

# 확인
echo $GOOGLE_CLIENT_ID
```

## 해결 방법

### 방법 1: 스크립트 사용 (권장)

업데이트된 스크립트가 자동으로 `.env` 파일을 읽습니다:

```powershell
.\scripts\start-auth-service.ps1
```

### 방법 2: 환경 변수 직접 설정

스크립트 없이 직접 실행하는 경우:

```powershell
# 환경 변수 설정
$env:GOOGLE_CLIENT_ID = "your-client-id.apps.googleusercontent.com"
$env:GOOGLE_CLIENT_SECRET = "your-client-secret"
$env:GOOGLE_REDIRECT_URI = "http://localhost:8080/api/auth/google/callback"

# Auth Service 실행
cd service.kroaddy.site
.\gradlew.bat :auth-service:bootRun --args='--server.port=8081'
```

### 방법 3: application.yaml에 직접 설정 (개발용만)

**주의**: 보안상 프로덕션에서는 사용하지 마세요!

```yaml
google:
  client-id: your-client-id.apps.googleusercontent.com
  client-secret: your-client-secret
  redirect-uri: http://localhost:8080/api/auth/google/callback
```

## 문제 해결 체크리스트

- [ ] `.env` 파일이 프로젝트 루트에 있는가?
- [ ] `.env` 파일 형식이 올바른가? (KEY=VALUE, 공백 없음)
- [ ] `GOOGLE_CLIENT_ID` 값이 비어있지 않은가?
- [ ] 스크립트 실행 시 "환경 변수 로드 완료" 메시지가 나오는가?
- [ ] `echo $env:GOOGLE_CLIENT_ID`로 값이 출력되는가?
- [ ] Auth Service 재시작했는가?

## 디버깅 로그

Auth Service 시작 시 다음 로그를 확인하세요:

```
⚠️  경고: GOOGLE_CLIENT_ID가 설정되지 않았습니다!
   .env 파일에 GOOGLE_CLIENT_ID를 설정하세요.
```

이 메시지가 나오면 환경 변수가 제대로 로드되지 않은 것입니다.

---

**작성일**: 2025년 1월

