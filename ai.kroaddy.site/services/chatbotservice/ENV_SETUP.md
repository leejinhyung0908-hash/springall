# 환경 변수 설정 가이드

## .env 파일 생성

챗봇 서비스를 사용하려면 OpenAI API 키가 필요합니다.

### 1. .env 파일 생성

`ai.kroaddy.site/services/chatbotservice/` 폴더에 `.env` 파일을 생성하세요:

```bash
cd ai.kroaddy.site/services/chatbotservice
```

`.env` 파일 내용:
```env
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2. OpenAI API 키 발급

1. [OpenAI Platform](https://platform.openai.com/) 접속
2. 계정 생성 또는 로그인
3. API Keys 메뉴에서 새 키 생성
4. 키를 복사하여 `.env` 파일에 붙여넣기

### 3. Docker Compose에서 사용

#### 방법 1: .env 파일 사용 (권장)

`.env` 파일을 생성하면 Docker Compose가 자동으로 로드합니다.

```bash
# .env 파일 생성 후
cd ai.kroaddy.site
docker compose up --build
```

#### 방법 2: 환경 변수로 직접 전달

`.env` 파일 없이 환경 변수로 직접 전달:

```powershell
# PowerShell
$env:OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
cd ai.kroaddy.site
docker compose up --build
```

```bash
# Linux/Mac
export OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
cd ai.kroaddy.site
docker compose up --build
```

### 4. .gitignore 확인

`.env` 파일은 Git에 커밋하지 않도록 `.gitignore`에 추가되어 있어야 합니다.

## 주의사항

⚠️ **중요**: 
- `.env` 파일은 절대 Git에 커밋하지 마세요
- API 키를 공개 저장소에 올리지 마세요
- 프로덕션 환경에서는 Docker Secrets나 환경 변수 관리 시스템을 사용하세요

## 문제 해결

### .env 파일이 없다는 오류

현재 Docker Compose 설정은 `.env` 파일이 없어도 실행됩니다. 
하지만 OpenAI API 키가 없으면 챗봇이 작동하지 않습니다.

API 키를 설정하는 방법:
1. `.env` 파일 생성 (위 방법 1)
2. 환경 변수로 전달 (위 방법 2)

