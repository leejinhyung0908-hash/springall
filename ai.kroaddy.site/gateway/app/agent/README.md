# Agent 모듈

Gateway 내부의 Agent 모듈로, LLM API 및 SLLM 로컬 DB를 관리합니다.

## 구조

```
agent/
├── __init__.py
├── main.py          # Agent API 엔드포인트
├── llm_api.py       # 외부 LLM API 통신 (OpenAI, Anthropic)
└── sllm_db.py       # SLLM 로컬 DB 관리 (SQLite)
```

## 기능

### 1. LLM API
- OpenAI API 통신
- Anthropic API 통신
- 채팅 완성 기능

### 2. SLLM 로컬 DB
- 모델 등록 및 관리
- 대화 기록 저장
- 응답 캐싱

## API 엔드포인트

- `GET /agent/` - Agent 서비스 상태
- `POST /agent/chat` - LLM 채팅
- `POST /agent/models/register` - SLLM 모델 등록
- `GET /agent/models` - 모델 목록 조회
- `GET /agent/models/{model_name}` - 모델 정보 조회
- `GET /agent/conversations` - 대화 기록 조회

## 설정

`.env` 파일에 다음 환경 변수를 설정하세요:

```env
OPENAI_API_KEY=your_openai_key
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_BASE_URL=https://api.openai.com/v1
ANTHROPIC_BASE_URL=https://api.anthropic.com/v1
```

## 사용 예시

### LLM 채팅
```bash
curl -X POST "http://localhost:9000/agent/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "안녕하세요"}],
    "model": "gpt-3.5-turbo",
    "provider": "openai"
  }'
```

### SLLM 모델 등록
```bash
curl -X POST "http://localhost:9000/agent/models/register" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "llama-2-7b",
    "model_type": "llama",
    "model_path": "/path/to/model",
    "config": {"temperature": 0.7}
  }'
```

