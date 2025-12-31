# RAG Service

독립적인 RAG (Retrieval-Augmented Generation) 서비스입니다.

## 🚀 빠른 시작

### 1. 환경 설정

```bash
cd rag.kroaddy.site

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
uvicorn app.main:app --reload --host 0.0.0.0 --port 9002

# 또는
python -m app.main
```

### 4. Docker로 실행

```bash
docker build -t rag-service .
docker run -p 9002:9002 --env-file .env rag-service
```

## 📡 API 엔드포인트

### 1. 서비스 상태 확인
```bash
GET /
GET /health
```

### 2. 질문하기 (RAG)
```bash
POST /query
Content-Type: application/json

{
  "question": "서울에서 추천할 만한 관광지는?",
  "top_k": 5
}
```

### 3. 문서 검색
```bash
POST /search
Content-Type: application/json

{
  "query": "서울 관광지",
  "top_k": 5
}
```

### 4. 문서 추가
```bash
POST /documents
Content-Type: application/json

{
  "text": "서울의 대표적인 관광지로는 경복궁, 남산타워, 명동 등이 있습니다...",
  "metadata": {
    "source": "tour_guide",
    "category": "seoul"
  }
}
```

### 5. 문서 일괄 추가
```bash
POST /documents/batch
Content-Type: application/json

[
  {
    "text": "문서 1 내용...",
    "metadata": {"source": "doc1"}
  },
  {
    "text": "문서 2 내용...",
    "metadata": {"source": "doc2"}
  }
]
```

## 🔧 설정

`.env` 파일에서 다음 설정을 변경할 수 있습니다:

- **VECTOR_DB_TYPE**: `chroma` 또는 `faiss`
- **EMBEDDING_MODEL**: OpenAI 임베딩 모델 (예: `text-embedding-3-small`)
- **LLM_MODEL**: LLM 모델 (예: `gpt-3.5-turbo`)
- **TOP_K_RESULTS**: 검색 결과 개수 (기본값: 5)
- **SIMILARITY_THRESHOLD**: 유사도 임계값 (기본값: 0.7)

## 📁 구조

```
rag.kroaddy.site/
├── app/
│   ├── main.py              # FastAPI 애플리케이션
│   ├── rag_engine.py        # RAG 엔진 (검색 + 생성)
│   ├── vector_store.py      # 벡터 저장소 관리
│   ├── embeddings.py        # 임베딩 생성
│   └── config.py           # 설정 관리
├── vector_db/               # 벡터 DB 저장소
├── data/                    # 문서 저장소
├── Dockerfile
└── requirements.txt
```

## 📝 사용 예시

### Python 클라이언트

```python
import requests

# 질문하기
response = requests.post(
    "http://localhost:9002/query",
    json={"question": "서울 관광지 추천해줘"}
)
print(response.json())

# 문서 추가
response = requests.post(
    "http://localhost:9002/documents",
    json={
        "text": "서울의 대표 관광지 정보...",
        "metadata": {"source": "guide"}
    }
)
```

### cURL

```bash
# 질문하기
curl -X POST "http://localhost:9002/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "서울 관광지 추천해줘"}'
```

## 포트

- 기본 포트: **9002**

