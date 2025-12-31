# Auth Service 포트 문제 해결

## 문제

auth-service가 포트 8080에서 시작하려고 하지만, 이미 Gateway가 포트 8080을 사용 중입니다.

## 해결 방법

### 방법 1: 실행 시 포트 지정 (권장)

```powershell
# Windows
cd service.kroaddy.site
$env:SERVER_PORT = "8081"
.\gradlew.bat :auth-service:bootRun --args='--server.port=8081'
```

```bash
# Linux/Mac
cd service.kroaddy.site
export SERVER_PORT=8081
./gradlew :auth-service:bootRun --args='--server.port=8081'
```

### 방법 2: 스크립트 사용

```powershell
# Windows
.\scripts\start-auth-service.ps1
```

```bash
# Linux/Mac
./scripts/start-auth-service.sh
```

### 방법 3: application.yaml 확인

`service.kroaddy.site/auth-service/src/main/resources/application.yaml` 파일에서:

```yaml
spring:
  server:
    port: 8081  # 이 값이 8081인지 확인
```

### 방법 4: 환경 변수 설정

`.env` 파일이나 환경 변수에:

```bash
SERVER_PORT=8081
```

## 확인

서비스가 정상적으로 시작되면:

```bash
# Health Check
curl http://localhost:8081/actuator/health

# Auth API
curl http://localhost:8081/api/auth/kakao/login
```

## 참고

- Gateway는 포트 8080 사용
- Auth Service는 포트 8081 사용
- 두 서비스가 동시에 실행 가능합니다

