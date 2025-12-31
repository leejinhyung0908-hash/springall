# Chatbot Service

OpenAI API를 사용한 가격 분석 챗봇 서비스입니다.

## 🚀 빠른 시작

### 1. 환경 설정

```bash
cd ai.kroaddy.site/services/chatbotservice

# .env 파일 생성 (선택사항)
# OPENAI_API_KEY=your_key_here
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. 서버 실행

```bash
# 개발 모드
uvicorn app.main:app --reload --host 0.0.0.0 --port 9004

# 또는
python -m app.main
```

### 4. Docker로 실행

```bash
docker build -t chatbot-service .
docker run -p 9004:9004 --env-file .env chatbot-service
```

## 📡 API 엔드포인트

### 1. 서비스 상태 확인

```bash
GET /
GET /health
```

### 2. 챗봇 대화

```bash
POST /chat
Content-Type: application/json

{
  "message": "안녕, 오늘 날씨 어때?",
  "conversation_history": [
    {"role": "user", "content": "안녕하세요"},
    {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
  ]
}
```

### 3. 가격 분석

```bash
POST /analyze-price
Content-Type: application/json

{
  "product_name": "아이폰 15",
  "price": 1200000,
  "context": "최신 스마트폰, 애플 제품"
}
```

## 🔧 설정

`.env` 파일에서 다음 설정을 변경할 수 있습니다:

- **OPENAI_API_KEY**: OpenAI API 키 (필수)
- **모델 설정**: `price_analyzer.py`에서 변경 가능
  - `model`: 사용할 모델 (기본값: `gpt-3.5-turbo`)
  - `temperature`: 창의성 조절 (기본값: `0.7`)
  - `max_tokens`: 응답 길이 제한 (기본값: `300`)

## 📁 구조

```
chatbotservice/
├── app/
│   ├── main.py              # FastAPI 애플리케이션
│   └── price_analyzer.py    # 챗봇 로직
├── Dockerfile
├── requirements.txt
└── README.md
```

## 📝 사용 예시

### Python 클라이언트

```python
import requests

# 챗봇 대화
response = requests.post(
    "http://localhost:9004/chat",
    json={"message": "안녕, 오늘 날씨 어때?"}
)
print(response.json())

# 가격 분석
response = requests.post(
    "http://localhost:9004/analyze-price",
    json={
        "product_name": "아이폰 15",
        "price": 1200000,
        "context": "최신 스마트폰"
    }
)
print(response.json())
```

### cURL

```bash
# 챗봇 대화
curl -X POST "http://localhost:9004/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "안녕, 오늘 날씨 어때?"}'

# 가격 분석
curl -X POST "http://localhost:9004/analyze-price" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "아이폰 15",
    "price": 1200000,
    "context": "최신 스마트폰"
  }'
```

## 포트

- 기본 포트: **9004**

