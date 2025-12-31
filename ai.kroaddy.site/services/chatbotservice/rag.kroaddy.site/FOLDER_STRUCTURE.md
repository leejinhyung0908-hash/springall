# RAG Service 폴더 구조 설명

이 문서는 `rag.kroaddy.site` 폴더의 구조와 각 파일의 역할을 설명합니다.

## 📁 전체 폴더 구조

```
rag.kroaddy.site/
├── app/                          # 메인 애플리케이션 코드
│   ├── __init__.py              # Python 패키지 초기화 파일
│   ├── main.py                  # FastAPI 애플리케이션 진입점
│   ├── config.py                # 환경 변수 및 설정 관리
│   ├── embeddings.py            # 임베딩 생성 모듈
│   ├── vector_store.py          # 벡터 저장소 관리 모듈
│   └── rag_engine.py            # RAG 엔진 (검색 + 생성)
├── data/                         # 문서 데이터 저장 디렉토리
│   └── .gitkeep                 # Git에서 빈 폴더 추적용
├── vector_db/                    # 벡터 데이터베이스 저장 디렉토리
│   └── .gitkeep                 # Git에서 빈 폴더 추적용
├── .env                         # 환경 변수 파일 (Git 제외)
├── .gitignore                   # Git 제외 파일 목록
├── Dockerfile                   # Docker 이미지 빌드 설정
├── requirements.txt             # Python 패키지 의존성
├── README.md                    # 프로젝트 기본 문서
└── OPENAI_CONNECTION_STRATEGY.md # OpenAI 연결 전략 가이드
```

---

## 📂 상세 설명

### `/app/` - 메인 애플리케이션 코드

#### `app/__init__.py`
- **역할**: Python 패키지 초기화 파일
- **내용**: 패키지 버전 정보 (`__version__ = "1.0.0"`)
- **의존성**: 없음

#### `app/main.py`
- **역할**: FastAPI 애플리케이션의 진입점
- **주요 기능**:
  - FastAPI 앱 초기화 및 CORS 설정
  - RAG 엔진 및 벡터 저장소 초기화
  - API 엔드포인트 정의:
    - `GET /` - 서비스 상태 확인
    - `GET /health` - 헬스 체크
    - `POST /query` - 질문에 대한 답변 생성 (RAG)
    - `POST /search` - 문서 검색 (생성 없음)
    - `POST /documents` - 단일 문서 추가
    - `POST /documents/batch` - 여러 문서 일괄 추가
- **의존성**: 
  - `app.rag_engine.RAGEngine`
  - `app.vector_store.VectorStore`
  - FastAPI, Pydantic

#### `app/config.py`
- **역할**: 환경 변수 및 설정 관리
- **주요 설정**:
  - API Keys: `OPENAI_API_KEY`, `HUGGINGFACE_API_KEY`
  - 모델 설정: `EMBEDDING_MODEL`, `LLM_MODEL`
  - 벡터 저장소 설정: `VECTOR_DB_TYPE`, `VECTOR_DB_PATH`, `COLLECTION_NAME`
  - 검색 설정: `TOP_K_RESULTS`, `SIMILARITY_THRESHOLD`
  - 서버 설정: `HOST`, `PORT`
- **의존성**: `python-dotenv` (`.env` 파일 로드)

#### `app/embeddings.py`
- **역할**: 텍스트를 벡터로 변환하는 임베딩 생성 모듈
- **주요 클래스**: `EmbeddingGenerator`
- **주요 메서드**:
  - `_initialize_embeddings()`: 임베딩 모델 초기화 (OpenAI 또는 HuggingFace)
  - `embed_text(text: str)`: 단일 텍스트를 벡터로 변환
  - `embed_documents(texts: list[str])`: 여러 문서를 벡터로 변환
- **폴백 전략**: OpenAI API 키가 없으면 HuggingFace 모델 사용
- **의존성**: 
  - `app.config` (환경 변수)
  - `langchain_openai`, `langchain_community`

#### `app/vector_store.py`
- **역할**: 벡터 저장소 관리 (ChromaDB 또는 FAISS)
- **주요 클래스**: `VectorStore`
- **주요 메서드**:
  - `_initialize_vector_store()`: 벡터 저장소 초기화
  - `add_documents(documents: List[Document])`: 문서 추가
  - `search_with_score(query: str, k: int)`: 유사도 점수와 함께 검색
  - `delete_collection()`: 컬렉션 삭제
- **지원 저장소**: ChromaDB (기본), FAISS
- **의존성**: 
  - `app.embeddings.EmbeddingGenerator`
  - `app.config`
  - `langchain_community.vectorstores`

#### `app/rag_engine.py`
- **역할**: RAG (Retrieval-Augmented Generation) 엔진 - 검색 + 생성
- **주요 클래스**: `RAGEngine`
- **주요 메서드**:
  - `_initialize_llm()`: LLM 초기화 (OpenAI 또는 HuggingFace)
  - `_create_qa_chain()`: 질문-답변 체인 생성
  - `query(question: str)`: 질문에 대한 답변 생성 (검색 + 생성)
  - `search_only(query: str, k: int)`: 검색만 수행 (생성 없음)
- **작동 방식**:
  1. 사용자 질문을 받음
  2. 벡터 저장소에서 관련 문서 검색
  3. 검색된 문서를 컨텍스트로 사용하여 LLM이 답변 생성
- **의존성**: 
  - `app.vector_store.VectorStore`
  - `app.config`
  - `langchain_openai`, `langchain.chains`

---

### `/data/` - 문서 데이터 저장 디렉토리

- **역할**: 원본 문서 파일 저장 (PDF, DOCX, TXT 등)
- **Git 관리**: `.gitignore`에 의해 제외됨 (`.gitkeep`만 추적)
- **용도**: 사용자가 업로드한 문서를 임시 저장하거나 원본 보관

---

### `/vector_db/` - 벡터 데이터베이스 저장 디렉토리

- **역할**: 벡터화된 문서 데이터 저장
- **Git 관리**: `.gitignore`에 의해 제외됨 (`.gitkeep`만 추적)
- **하위 구조**:
  - `chroma_db/`: ChromaDB 사용 시 저장 위치
  - `faiss_index/`: FAISS 사용 시 저장 위치
- **용도**: 문서 임베딩 벡터와 메타데이터 저장

---

### 루트 파일들

#### `.env`
- **역할**: 환경 변수 파일 (로컬 개발용)
- **Git 관리**: `.gitignore`에 의해 제외됨
- **주요 변수**: `OPENAI_API_KEY`, `EMBEDDING_MODEL`, `LLM_MODEL` 등
- **참고**: `OPENAI_CONNECTION_STRATEGY.md`에서 상세 설명

#### `.gitignore`
- **역할**: Git에서 제외할 파일/폴더 목록
- **제외 항목**:
  - 환경 변수: `.env`
  - 벡터 DB: `vector_db/`, `*.faiss`, `*.pkl`
  - 데이터: `data/`, `*.pdf`, `*.docx`, `*.txt`
  - Python: `__pycache__/`, `*.pyc`, `venv/`
  - IDE: `.vscode/`, `.idea/`
  - 로그: `*.log`, `logs/`

#### `Dockerfile`
- **역할**: Docker 이미지 빌드 설정
- **기본 이미지**: `python:3.11-slim`
- **작업 순서**:
  1. 작업 디렉토리 설정 (`/app`)
  2. `requirements.txt` 복사 및 패키지 설치
  3. `app/` 폴더 복사
  4. `vector_db`, `data` 디렉토리 생성
  5. 서버 실행 명령 (`uvicorn app.main:app --host 0.0.0.0 --port 9002`)

#### `requirements.txt`
- **역할**: Python 패키지 의존성 목록
- **주요 패키지**:
  - 웹 프레임워크: `fastapi`, `uvicorn`, `pydantic`
  - 환경 변수: `python-dotenv`
  - RAG: `langchain`, `langchain-openai`, `langchain-community`
  - 벡터 저장소: `chromadb`
  - LLM: `openai`, `tiktoken`
  - 문서 처리: `pypdf`, `python-docx`, `beautifulsoup4`
  - 유틸리티: `httpx`, `aiofiles`

#### `README.md`
- **역할**: 프로젝트 기본 문서
- **내용**: 빠른 시작, API 엔드포인트, 설정, 사용 예시

#### `OPENAI_CONNECTION_STRATEGY.md`
- **역할**: OpenAI API 연결 전략 가이드
- **내용**: API 키 설정, 환경 변수 구성, Docker 설정, 연결 테스트, 에러 처리, 비용 관리 등

---

## 🔄 모듈 간 의존성 관계

```
main.py
  ├── rag_engine.py
  │     ├── vector_store.py
  │     │     ├── embeddings.py
  │     │     │     └── config.py
  │     │     └── config.py
  │     └── config.py
  └── vector_store.py
        ├── embeddings.py
        │     └── config.py
        └── config.py
```

**의존성 흐름**:
1. `main.py`가 `RAGEngine`과 `VectorStore`를 초기화
2. `RAGEngine`이 `VectorStore`를 사용하여 문서 검색
3. `VectorStore`가 `EmbeddingGenerator`를 사용하여 임베딩 생성
4. 모든 모듈이 `config.py`에서 설정을 읽음

---

## 🚀 실행 흐름

1. **서버 시작** (`main.py`):
   - FastAPI 앱 생성
   - CORS 설정
   - `RAGEngine` 초기화
     - `VectorStore` 초기화
       - `EmbeddingGenerator` 초기화 (OpenAI 또는 HuggingFace)
       - 벡터 저장소 로드 또는 생성 (ChromaDB 또는 FAISS)
     - LLM 초기화 (OpenAI 또는 HuggingFace)
     - QA 체인 생성

2. **API 요청 처리**:
   - `/query`: 질문 → 벡터 검색 → LLM 답변 생성
   - `/search`: 질문 → 벡터 검색만 수행
   - `/documents`: 문서 → 임베딩 생성 → 벡터 저장소에 추가

---

## 📝 주요 개념

### RAG (Retrieval-Augmented Generation)
- **검색(Retrieval)**: 벡터 저장소에서 관련 문서 검색
- **생성(Generation)**: 검색된 문서를 컨텍스트로 사용하여 LLM이 답변 생성

### 임베딩 (Embedding)
- 텍스트를 고차원 벡터로 변환하여 의미적 유사도를 계산 가능하게 함
- OpenAI 또는 HuggingFace 모델 사용

### 벡터 저장소 (Vector Store)
- 임베딩된 문서를 저장하고 유사도 검색을 수행
- ChromaDB (기본) 또는 FAISS 지원

---

## 🔧 설정 변경 방법

모든 설정은 `.env` 파일 또는 환경 변수로 변경 가능:

```env
# .env 파일 예시
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-3.5-turbo
VECTOR_DB_TYPE=chroma
TOP_K_RESULTS=5
SIMILARITY_THRESHOLD=0.7
```

---

## 📚 추가 문서

- **기본 사용법**: `README.md`
- **OpenAI 연결**: `OPENAI_CONNECTION_STRATEGY.md`

