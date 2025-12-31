# 빠른 시작 가이드

## 로컬 환경에서 실행하기

### 1단계: Python 서비스들 시작

**Windows (PowerShell):**
```powershell
.\scripts\start-python-services.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/*.sh
./scripts/start-python-services.sh
```

또는 수동으로:

```bash
# Agent Service (9000)
cd ai.kroaddy.site/gateway
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload

# RAG Service (9002) - 새 터미널
cd ai.kroaddy.site/services/chatbotservice/rag.kroaddy.site
uvicorn app.main:app --host 0.0.0.0 --port 9002 --reload

# Feed Service (9003) - 새 터미널
cd ai.kroaddy.site/services/crawlerservice/feed.kroaddy.site
uvicorn app.main:app --host 0.0.0.0 --port 9003 --reload

# Chatbot Service (9004) - 새 터미널
cd ai.kroaddy.site/services/chatbotservice
uvicorn app.main:app --host 0.0.0.0 --port 9004 --reload

# ML Service (9010) - 새 터미널
cd ai.kroaddy.site/services/mlservice
uvicorn app.main:app --host 0.0.0.0 --port 9010 --reload
```

### 2단계: Java Gateway 시작

**Windows (PowerShell):**
```powershell
.\scripts\start-java-gateway.ps1
```

**Linux/Mac:**
```bash
./scripts/start-java-gateway.sh
```

또는 수동으로:

```bash
# 루트 프로젝트에서 실행 (멀티 프로젝트 구조)
cd api.kroaddy.site
./gradlew :gateway:bootRun --args='--spring.profiles.active=local'

# 또는 gateway 디렉토리에서 직접 실행 (플러그인 설정 필요)
cd api.kroaddy.site/gateway
./gradlew bootRun --args='--spring.profiles.active=local'
```

### 3단계: 서비스 확인

브라우저에서 접속:
- **Gateway**: http://localhost:8080/docs (Swagger UI)
- **Agent Service**: http://localhost:9000/
- **RAG Service**: http://localhost:9002/
- **Feed Service**: http://localhost:9003/
- **Chatbot Service**: http://localhost:9004/
- **ML Service**: http://localhost:9010/

### 4단계: Gateway를 통한 API 호출 테스트

```bash
# Agent Service (Gateway 경유)
curl http://localhost:8080/api/agent/

# Feed Service (Gateway 경유)
curl http://localhost:8080/api/feed/

# RAG Service (Gateway 경유)
curl http://localhost:8080/api/rag/

# Chatbot Service (Gateway 경유)
curl http://localhost:8080/api/chatbot/

# ML Service (Gateway 경유)
curl http://localhost:8080/api/ml/
```

## 문제 해결

### 포트가 이미 사용 중인 경우

**Windows:**
```powershell
# 포트 사용 중인 프로세스 확인
netstat -ano | findstr :9000

# 프로세스 종료
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
# 포트 사용 중인 프로세스 확인 및 종료
lsof -ti:9000 | xargs kill -9
```

### 서비스가 시작되지 않는 경우

1. **Python 의존성 확인**
   ```bash
   pip install -r requirements.txt
   ```

2. **Java/Gradle 확인**
   ```bash
   cd api.kroaddy.site/gateway
   ./gradlew --version
   ```

3. **환경 변수 확인**
   - `.env` 파일이 있는지 확인
   - 필요한 API 키가 설정되어 있는지 확인

### Gateway가 서비스를 찾지 못하는 경우

1. **서비스가 실행 중인지 확인**
   ```bash
   curl http://localhost:9000/health
   ```

2. **application-local.yaml 확인**
   - 서비스 URL이 `http://localhost:포트`로 설정되어 있는지 확인

3. **Spring Profile 확인**
   ```bash
   # 로컬 프로파일로 실행 중인지 확인
   echo $SPRING_PROFILES_ACTIVE
   # 또는
   # --spring.profiles.active=local 플래그 확인
   ```

## 서비스 중지

**Python 서비스 중지:**
```powershell
# Windows
.\scripts\stop-python-services.ps1
```

```bash
# Linux/Mac
./scripts/stop-python-services.sh
```

**Java Gateway 중지:**
- 실행 중인 터미널에서 `Ctrl+C`

## 다음 단계

더 자세한 내용은 `LOCAL_DEVELOPMENT_GUIDE.md`를 참고하세요.

