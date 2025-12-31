# OpenAI API 키 오류 해결 가이드

## 문제: 401 Invalid API Key 오류

### 증상
- "Incorrect API key provided" 에러 메시지
- Error code: 401
- invalid_api_key 오류

### 해결 방법

#### 1. 환경 변수 확인

```powershell
# Docker 컨테이너에서 확인
cd ai.kroaddy.site
docker compose exec chatbotservice env | findstr OPENAI
```

#### 2. .env 파일 확인

`ai.kroaddy.site/.env` 파일이 있는지 확인하고, 올바른 API 키가 설정되어 있는지 확인:

```bash
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

#### 3. Docker Compose 환경 변수 확인

`ai.kroaddy.site/docker-compose.yaml`에서 환경 변수가 올바르게 설정되어 있는지 확인:

```yaml
chatbotservice:
  environment:
    - OPENAI_API_KEY=${OPENAI_API_KEY:-}
```

#### 4. API 키 유효성 확인

OpenAI 플랫폼에서 API 키가 유효한지 확인:
- https://platform.openai.com/account/api-keys
- API 키가 활성화되어 있는지 확인
- API 키가 만료되지 않았는지 확인

#### 5. 컨테이너 재시작

환경 변수를 변경한 경우:

```powershell
cd ai.kroaddy.site

# 컨테이너 중지
docker compose stop chatbotservice

# 환경 변수 설정 (실제 API 키로 변경)
$env:OPENAI_API_KEY="sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"

# 컨테이너 시작
docker compose up -d chatbotservice

# 로그 확인
docker compose logs -f chatbotservice
```

### 주의사항

1. **API 키 보안**: `.env` 파일은 절대 Git에 커밋하지 마세요
2. **API 키 형식**: `sk-proj-` 또는 `sk-`로 시작해야 합니다
3. **권한 확인**: API 키에 필요한 권한이 있는지 확인하세요

### 에러 메시지 개선

이제 API 키 오류가 발생하면 사용자에게는 간단한 메시지만 표시되고, 상세한 에러 정보는 서버 로그에만 기록됩니다.

