# 전체 서비스 실행 가이드

## 빠른 시작

### Windows (PowerShell)

```powershell
# 전체 서비스 시작
.\scripts\start-all-services.ps1

# 서비스 상태 확인
.\scripts\check-services.ps1

# 전체 서비스 중지
.\scripts\stop-all-services.ps1
```

### Linux/Mac (Bash)

```bash
# 실행 권한 부여 (최초 1회)
chmod +x scripts/*.sh

# 전체 서비스 시작
./scripts/start-all-services.sh

# 서비스 상태 확인
./scripts/check-services.sh

# Python 서비스만 중지
./scripts/stop-python-services.sh
```

## 실행 순서

스크립트는 다음 순서로 서비스를 시작합니다:

1. **Python 서비스들** (백그라운드)
   - Agent Service (포트 9000)
   - RAG Service (포트 9002)
   - Feed Service (포트 9003)
   - Chatbot Service (포트 9004)
   - ML Service (포트 9010)

2. **Auth Service** (새 창, 포트 8081)

3. **Java Gateway** (새 창, 포트 8080)

## 서비스 URL

| 서비스 | URL | 설명 |
|--------|-----|------|
| **Gateway** | http://localhost:8080 | 메인 API Gateway |
| **Gateway Docs** | http://localhost:8080/docs | Swagger UI |
| **Auth Service** | http://localhost:8081 | 인증 서비스 |
| **Agent Service** | http://localhost:9000 | LLM API |
| **RAG Service** | http://localhost:9002 | RAG 엔진 |
| **Feed Service** | http://localhost:9003 | Feed 크롤링 |
| **Chatbot Service** | http://localhost:9004 | 챗봇 서비스 |
| **ML Service** | http://localhost:9010 | 머신러닝 서비스 |

## 개별 서비스 실행

전체가 아닌 특정 서비스만 실행하려면:

### Python 서비스만
```powershell
.\scripts\start-python-services.ps1
```

### Auth Service만
```powershell
.\scripts\start-auth-service.ps1
```

### Java Gateway만
```powershell
.\scripts\start-java-gateway.ps1
```

## 서비스 중지

### 전체 중지
```powershell
.\scripts\stop-all-services.ps1
```

### Python 서비스만 중지
```powershell
.\scripts\stop-python-services.ps1
```

### Java 서비스 중지
각 서비스가 실행 중인 창에서 `Ctrl+C`로 중지

## 서비스 상태 확인

```powershell
.\scripts\check-services.ps1
```

이 스크립트는 모든 서비스의 헬스 체크를 수행합니다.

## 문제 해결

### 포트 충돌

포트가 이미 사용 중인 경우:

```powershell
# 포트 사용 중인 프로세스 확인
netstat -ano | findstr :8080
netstat -ano | findstr :8081
netstat -ano | findstr :9000

# 프로세스 중지 (PID는 위 명령어 결과에서 확인)
taskkill /PID <PID> /F
```

### 서비스가 시작되지 않는 경우

1. **로그 확인**:
   ```powershell
   # Python 서비스 로그
   Get-Content logs\*.log -Wait
   ```

2. **환경 변수 확인**:
   - `.env` 파일이 프로젝트 루트에 있는지 확인
   - 필요한 환경 변수가 설정되어 있는지 확인

3. **의존성 확인**:
   - Java 21 설치 확인
   - Python 3.11+ 설치 확인
   - Python 패키지 설치 확인

## 주의사항

1. **순서 중요**: Gateway는 다른 서비스들이 실행된 후 시작해야 합니다.
2. **환경 변수**: `.env` 파일이 프로젝트 루트에 있어야 합니다.
3. **포트 충돌**: 다른 애플리케이션이 같은 포트를 사용하지 않는지 확인하세요.

---

**작성일**: 2025년 12월

