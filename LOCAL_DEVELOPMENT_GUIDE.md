# 로컬 개발 환경 가이드

## 개요

Docker 컨테이너 없이 로컬에서 모든 서비스를 실행하는 방법을 안내합니다.

## 사전 요구사항

### 필수 설치
- **Java 21** (JDK)
- **Python 3.11+**
- **Node.js 18+** (프론트엔드 개발 시)
- **Redis** (로컬 또는 Upstash 사용)

### 선택적 설치
- **PostgreSQL** (로컬 또는 Neon 사용)
- **Maven/Gradle** (Java 빌드 도구)

---

## 서비스 포트 정리

| 서비스 | 포트 | 기술 스택 | 설명 |
|--------|------|-----------|------|
| **Java Gateway** | 8080 | Spring Cloud Gateway | 메인 API Gateway |
| **Agent Service** | 9000 | FastAPI (Python) | LLM API 및 SLLM 관리 |
| **RAG Service** | 9002 | FastAPI (Python) | RAG 엔진 |
| **Feed Service** | 9003 | FastAPI (Python) | Feed 크롤링 |
| **Chatbot Service** | 9004 | FastAPI (Python) | 챗봇 서비스 |
| **Auth Service** | 8081 | Spring Boot | 인증 서비스 |
| **ML Service** | 9010 | FastAPI (Python) | 머신러닝 서비스 |

---

## 1단계: Java Gateway 설정

### 1.1 환경 변수 설정

```bash
cd api.kroaddy.site/gateway
cp .env.example .env
# .env 파일을 편집하여 필요한 값 설정
```

### 1.2 로컬 프로파일로 실행

```bash
# Gradle 사용 (루트 프로젝트에서)
cd api.kroaddy.site
./gradlew :gateway:bootRun --args='--spring.profiles.active=local'

# 또는 gateway 디렉토리에서 직접 실행
cd api.kroaddy.site/gateway
./gradlew bootRun --args='--spring.profiles.active=local'
```

### 1.3 환경 변수로 서비스 URL 오버라이드

```bash
export SPRING_PROFILES_ACTIVE=local
export FEED_SERVICE_URL=http://localhost:9003
export RAG_SERVICE_URL=http://localhost:9002
export CHATBOT_SERVICE_URL=http://localhost:9004
export AGENT_SERVICE_URL=http://localhost:9000
export AUTH_SERVICE_URL=http://localhost:8081
export ML_SERVICE_URL=http://localhost:9010

./gradlew bootRun
```

---

## 2단계: Python 서비스 실행

### 2.1 Agent Service (포트 9000)

```bash
cd ai.kroaddy.site/gateway

# 가상 환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export OPENAI_API_KEY=your_openai_api_key  # 필요시

# 서비스 실행
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

### 2.2 RAG Service (포트 9002)

```bash
cd ai.kroaddy.site/services/chatbotservice/rag.kroaddy.site

# 가상 환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export OPENAI_API_KEY=your_openai_api_key  # 필요시

# 서비스 실행
uvicorn app.main:app --host 0.0.0.0 --port 9002 --reload
```

### 2.3 Feed Service (포트 9003)

```bash
cd ai.kroaddy.site/services/crawlerservice/feed.kroaddy.site

# 가상 환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서비스 실행
uvicorn app.main:app --host 0.0.0.0 --port 9003 --reload
```

### 2.4 Chatbot Service (포트 9004)

```bash
cd ai.kroaddy.site/services/chatbotservice

# 가상 환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export OPENAI_API_KEY=your_openai_api_key  # 필요시

# 서비스 실행
uvicorn app.main:app --host 0.0.0.0 --port 9004 --reload
```

### 2.5 ML Service (포트 9010)

```bash
cd ai.kroaddy.site/services/mlservice

# 가상 환경 생성 (선택사항)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경 변수 설정
export KAKAO_REST_API_KEY=your_kakao_api_key  # 필요시

# 서비스 실행
uvicorn app.main:app --host 0.0.0.0 --port 9010 --reload
```

---

## 3단계: Java 서비스 실행 (선택사항)

### 3.1 Auth Service (포트 8081)

```bash
cd service.kroaddy.site/auth-service

# Gradle 사용
./gradlew bootRun

# 또는 Maven 사용
./mvnw spring-boot:run
```

---

## 4단계: 실행 스크립트 사용 (권장)

### Windows (PowerShell)

```powershell
# 모든 Python 서비스 실행
.\scripts\start-python-services.ps1

# Java Gateway 실행
.\scripts\start-java-gateway.ps1
```

### Linux/Mac (Bash)

```bash
# 모든 Python 서비스 실행
chmod +x scripts/start-python-services.sh
./scripts/start-python-services.sh

# Java Gateway 실행
chmod +x scripts/start-java-gateway.sh
./scripts/start-java-gateway.sh
```

---

## 5단계: 서비스 확인

### Gateway 상태 확인

```bash
curl http://localhost:8080/
# 또는 브라우저에서 http://localhost:8080/docs 접속
```

### 각 서비스 상태 확인

```bash
# Agent Service
curl http://localhost:9000/

# RAG Service
curl http://localhost:9002/

# Feed Service
curl http://localhost:9003/

# Chatbot Service
curl http://localhost:9004/

# ML Service
curl http://localhost:9010/
```

### Gateway를 통한 API 호출

```bash
# Feed Service (Gateway 경유)
curl http://localhost:8080/api/feed/

# RAG Service (Gateway 경유)
curl http://localhost:8080/api/rag/

# Chatbot Service (Gateway 경유)
curl http://localhost:8080/api/chatbot/

# Agent Service (Gateway 경유)
curl http://localhost:8080/api/agent/

# ML Service (Gateway 경유)
curl http://localhost:8080/api/ml/
```

---

## 환경 변수 설정

### .env 파일 생성 (루트 디렉토리)

```bash
# 루트 디렉토리에 .env 파일 생성
cat > .env << EOF
# === 서비스 URL (로컬) ===
AUTH_SERVICE_URL=http://localhost:8081
ML_SERVICE_URL=http://localhost:9010
FEED_SERVICE_URL=http://localhost:9003
RAG_SERVICE_URL=http://localhost:9002
CHATBOT_SERVICE_URL=http://localhost:9004
AGENT_SERVICE_URL=http://localhost:9000

# === Redis ===
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=

# === API Keys ===
OPENAI_API_KEY=your_openai_api_key
KAKAO_REST_API_KEY=your_kakao_api_key

# === Spring Profile ===
SPRING_PROFILES_ACTIVE=local
EOF
```

### 환경 변수 로드 (Linux/Mac)

```bash
# .env 파일 로드
export $(cat .env | xargs)
```

### 환경 변수 로드 (Windows PowerShell)

```powershell
# .env 파일 로드
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
    }
}
```

---

## 문제 해결

### 포트 충돌

```bash
# Windows
netstat -ano | findstr :8080
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8080 | xargs kill -9
```

### 서비스 연결 실패

1. **서비스가 실행 중인지 확인**
   ```bash
   curl http://localhost:9000/health
   ```

2. **Gateway 로그 확인**
   ```bash
   # Java Gateway 로그에서 라우팅 정보 확인
   ```

3. **환경 변수 확인**
   ```bash
   echo $FEED_SERVICE_URL
   ```

### CORS 오류

- Gateway의 `CorsConfig.java`에서 허용된 Origin 확인
- 프론트엔드 포트가 허용 목록에 있는지 확인

---

## 개발 워크플로우

### 1. 서비스 시작 순서

1. **Redis 시작** (필요시)
   ```bash
   redis-server
   ```

2. **Python 서비스들 시작** (병렬 실행 가능)
   - Agent Service (9000)
   - RAG Service (9002)
   - Feed Service (9003)
   - Chatbot Service (9004)
   - ML Service (9010)

3. **Java 서비스들 시작** (필요시)
   - Auth Service (8081)

4. **Java Gateway 시작** (마지막)
   - Gateway (8080)

### 2. 핫 리로드

- **Python 서비스**: `--reload` 플래그 사용 (자동 재시작)
- **Java 서비스**: Spring Boot DevTools 사용 또는 IDE에서 실행

### 3. 디버깅

- **Python**: `--log-level debug` 플래그 사용
- **Java**: IDE 디버거 연결 또는 로그 레벨 조정

---

## 스크립트 예시

### start-all-services.sh (Linux/Mac)

```bash
#!/bin/bash

# 환경 변수 로드
export $(cat .env | xargs)

# Python 서비스들 백그라운드 실행
cd ai.kroaddy.site/gateway && uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload &
cd ai.kroaddy.site/services/chatbotservice/rag.kroaddy.site && uvicorn app.main:app --host 0.0.0.0 --port 9002 --reload &
cd ai.kroaddy.site/services/crawlerservice/feed.kroaddy.site && uvicorn app.main:app --host 0.0.0.0 --port 9003 --reload &
cd ai.kroaddy.site/services/chatbotservice && uvicorn app.main:app --host 0.0.0.0 --port 9004 --reload &
cd ai.kroaddy.site/services/mlservice && uvicorn app.main:app --host 0.0.0.0 --port 9010 --reload &

# Java Gateway 실행
cd api.kroaddy.site/gateway && ./gradlew bootRun --args='--spring.profiles.active=local'
```

### start-all-services.ps1 (Windows)

```powershell
# 환경 변수 로드
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
    }
}

# Python 서비스들 백그라운드 실행
Start-Process -NoNewWindow python -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9000", "--reload" -WorkingDirectory "ai.kroaddy.site\gateway"
Start-Process -NoNewWindow python -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9002", "--reload" -WorkingDirectory "ai.kroaddy.site\services\chatbotservice\rag.kroaddy.site"
Start-Process -NoNewWindow python -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9003", "--reload" -WorkingDirectory "ai.kroaddy.site\services\crawlerservice\feed.kroaddy.site"
Start-Process -NoNewWindow python -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9004", "--reload" -WorkingDirectory "ai.kroaddy.site\services\chatbotservice"
Start-Process -NoNewWindow python -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9010", "--reload" -WorkingDirectory "ai.kroaddy.site\services\mlservice"

# Java Gateway 실행
cd api.kroaddy.site\gateway
.\gradlew.bat bootRun --args='--spring.profiles.active=local'
```

---

## 참고사항

1. **포트 변경**: 각 서비스의 포트를 변경하려면:
   - Python: `--port` 옵션 변경
   - Java: `application-local.yaml`에서 `server.port` 변경
   - Gateway: `application-local.yaml`에서 서비스 URL 변경

2. **환경 변수 우선순위**:
   - 환경 변수 > application-local.yaml > application.yaml

3. **로깅**: 각 서비스의 로그는 별도 터미널에서 확인하거나 파일로 리다이렉트

4. **성능**: 로컬 개발 환경에서는 모든 서비스를 동시에 실행할 필요 없음 (필요한 서비스만 실행)

---

**작성일**: 2025년 1월

