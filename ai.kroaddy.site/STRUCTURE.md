# ai.kroaddy.site 프로젝트 구조

## 개요

`ai.kroaddy.site`는 마이크로서비스 아키텍처를 기반으로 한 AI 서비스 플랫폼입니다. FastAPI를 사용하여 각 서비스를 독립적으로 운영하며, Gateway 서비스를 통해 통합 관리합니다.

## 전체 구조

```
ai.kroaddy.site/
├── gateway/              # API Gateway 서비스
├── services/             # 마이크로서비스들
│   ├── authservice/      # 인증 서비스
│   ├── chatbotservice/   # 챗봇 서비스 (RAG 포함)
│   ├── crawlerservice/   # 크롤링 서비스
│   ├── mlservice/        # 머신러닝 서비스
│   ├── common/           # 공통 모듈 (비어있음)
│   └── transformer/      # 변환 서비스 (비어있음)
├── requirements.txt      # 루트 레벨 의존성
├── Dockerfile            # 루트 레벨 Dockerfile
└── .gitignore           # Git 무시 파일
```

---

## 1. Gateway 서비스

**위치**: `gateway/`  
**포트**: 9000  
**역할**: API Gateway 및 프록시 서버

### 구조

```
gateway/
├── app/
│   ├── main.py              # FastAPI 메인 애플리케이션
│   └── agent/               # Agent 서비스 모듈
│       ├── main.py          # Agent 라우터
│       ├── llm_api.py       # LLM API 클라이언트
│       ├── sllm_db.py       # SLLM 데이터베이스 관리
│       ├── __init__.py
│       └── README.md
├── Dockerfile
└── requirements.txt
```

### 주요 기능

- **프록시 서비스**: Feed, RAG, Chatbot 서비스로 요청 프록시
- **Agent 서비스**: LLM API 통합 및 SLLM 관리
- **CORS 처리**: 모든 서비스에 대한 CORS 미들웨어 제공

### 환경 변수

- `FEED_SERVICE_URL`: Feed 서비스 URL (기본값: `http://feedservice:9003`)
- `RAG_SERVICE_URL`: RAG 서비스 URL (기본값: `http://ragservice:9002`)
- `CHATBOT_SERVICE_URL`: Chatbot 서비스 URL (기본값: `http://chatbotservice:9004`)

---

## 2. Services

### 2.1 Auth Service

**위치**: `services/authservice/`  
**역할**: 인증 및 권한 관리

```
authservice/
├── app/
│   ├── main.py          # FastAPI 애플리케이션
│   └── __init__.py
└── Dockerfile
```

### 2.2 Chatbot Service

**위치**: `services/chatbotservice/`  
**역할**: 가격 분석 챗봇 및 대화형 AI 서비스

```
chatbotservice/
├── app/
│   ├── main.py              # FastAPI 메인 애플리케이션
│   ├── config.py            # 설정 파일
│   ├── pl.py                # PL (Price List?) 모듈
│   ├── price_analyzer.py    # 가격 분석 모듈
│   └── __init__.py
├── rag.kroaddy.site/        # RAG 서비스 (별도 서브서비스)
│   ├── app/
│   │   ├── main.py          # RAG FastAPI 애플리케이션
│   │   ├── config.py
│   │   ├── embeddings.py    # 임베딩 생성
│   │   ├── rag_engine.py    # RAG 엔진
│   │   └── vector_store.py  # 벡터 스토어 관리
│   ├── data/                # 데이터 디렉토리
│   ├── vector_db/           # 벡터 데이터베이스
│   │   └── chroma_db/       # ChromaDB 저장소
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
├── Dockerfile
├── requirements.txt
└── README.md
```

### 주요 기능

- **가격 분석**: 상품 가격 분석 및 바가지 탐지
- **대화형 챗봇**: 사용자와의 대화 처리
- **RAG (Retrieval-Augmented Generation)**: 벡터 검색 기반 답변 생성

### 문서

- `API_KEY_TROUBLESHOOTING.md`: API 키 문제 해결 가이드
- `ENV_SETUP.md`: 환경 설정 가이드
- `FRONTEND_INTEGRATION.md`: 프론트엔드 통합 가이드
- `GATEWAY_CONNECTION.md`: Gateway 연결 가이드
- `USER_PROFILE_INTEGRATION.md`: 사용자 프로필 통합 가이드

### 2.3 Crawler Service

**위치**: `services/crawlerservice/`  
**역할**: 웹 크롤링 및 데이터 수집

```
crawlerservice/
├── app/
│   ├── main.py              # FastAPI 메인 애플리케이션
│   ├── save/                # 저장 디렉토리
│   ├── bs_demo/             # BeautifulSoup 데모
│   │   ├── overcharge_detection/  # 바가지 탐지
│   │   │   └── kakao/       # 카카오맵 크롤러
│   │   │       ├── router.py      # API 라우터
│   │   │       ├── crawler.py     # 크롤러 통합 모듈
│   │   │       ├── search_kakao.py # 카카오맵 검색
│   │   │       ├── detail.py      # 상세 정보 추출
│   │   │       └── __init__.py
│   │   └── risk_detection/  # 위험 탐지
│   │       ├── aggregate.py       # 뉴스 집계
│   │       ├── hazard_analyzer.py # 위험 분석
│   │       ├── bugsmusic.py       # 벅스뮤직 크롤러
│   │       ├── naver.py           # 네이버 크롤러
│   │       ├── daum.py            # 다음 크롤러
│   │       └── google.py          # 구글 크롤러
│   └── sel_demo/            # Selenium 데모
│       └── danawa.py        # 다나와 크롤러
├── feed.kroaddy.site/       # Feed 서비스 (별도 서브서비스)
│   ├── app/
│   │   ├── main.py
│   │   ├── bs_demo/         # 위험 탐지 크롤러들
│   │   └── sel_demo/        # Selenium 크롤러들
│   ├── Dockerfile
│   ├── requirements.txt
│   └── README.md
├── Dockerfile
└── requirements.txt
```

### 주요 기능

- **카카오맵 크롤링**: 장소 검색 및 메뉴 가격 추출
- **바가지 탐지**: 메뉴 가격 분석 및 바가지 탐지
- **위험 탐지**: 뉴스 크롤링 및 위험 요소 분석
- **다양한 소스 크롤링**: 네이버, 다음, 구글, 벅스뮤직, 다나와 등

### API 엔드포인트 (카카오맵)

- `GET /kakao/search`: 카카오맵 장소 검색
- `GET /kakao/crawl/{place_id}`: 특정 장소의 메뉴 정보 크롤링

### 2.4 ML Service

**위치**: `services/mlservice/`  
**역할**: 머신러닝 모델 및 데이터 분석 서비스

```
mlservice/
├── app/
│   ├── main.py                      # FastAPI 메인 애플리케이션
│   ├── config.py                    # 설정 파일
│   ├── nlp/                         # 자연어 처리 모듈
│   │   ├── nlp_router.py           # NLP 라우터
│   │   ├── emma/                    # Emma 워드클라우드
│   │   │   └── emma_wordcloud.py
│   │   ├── samsung/                 # 삼성 워드클라우드
│   │   │   └── samsung_wordcloud.py
│   │   └── review/                  # 리뷰 감정 분석
│   │       ├── emotion_inference.py
│   │       └── corpus/              # 리뷰 코퍼스 (47개 JSON 파일)
│   ├── seoul_crime/                 # 서울 범죄 데이터 분석
│   │   ├── seoul_router.py
│   │   ├── seoul_service.py
│   │   ├── seoul_data.py
│   │   ├── seoul_method.py
│   │   ├── seoul_model.py
│   │   ├── google_map_singleton.py
│   │   └── kakao_map_singleton.py
│   ├── titanic/                     # 타이타닉 데이터셋 분석
│   │   ├── titanic_router.py
│   │   ├── titanic_service.py
│   │   ├── titanic_dataset.py
│   │   ├── titanic_method.py
│   │   └── titanic_model.py
│   ├── us_unemployment/             # 미국 실업률 데이터 분석
│   │   ├── router.py
│   │   └── service.py
│   ├── resources/                   # 리소스 파일
│   │   ├── crime/                   # 범죄 데이터
│   │   │   ├── cctv.csv
│   │   │   ├── crime.csv
│   │   │   ├── kr-state.json
│   │   │   ├── pop.xls
│   │   │   ├── us_unemployment.csv
│   │   │   └── us-states.json
│   │   ├── data/                    # 일반 데이터
│   │   │   ├── D2Coding.ttf
│   │   │   ├── kr-Report_2018.txt
│   │   │   └── stopwords.txt
│   │   ├── koelectra_local/         # KoELECTRA 모델
│   │   │   ├── config.json
│   │   │   ├── model.safetensors
│   │   │   ├── pytorch_model.bin
│   │   │   ├── tokenizer.json
│   │   │   └── vocab.txt
│   │   └── titanic/                 # 타이타닉 데이터셋
│   │       ├── test.csv
│   │       └── train.csv
│   ├── save/                        # 생성된 결과 파일
│   │   ├── crime_heatmap.png
│   │   ├── crime_cctv_map.html
│   │   ├── emma_wordcloud.png
│   │   ├── samsung_wordcloud.png
│   │   └── us_unemployment_map.html
│   ├── create_crime_cctv_map.py     # 범죄-CCTV 맵 생성
│   └── create_crime_heatmap.py      # 범죄 히트맵 생성
├── Dockerfile
├── requirements.txt
├── README.md
├── POSTMAN_GUIDE.md
└── RUN_SERVICE.md
```

### 주요 기능

- **서울 범죄 데이터 분석**: 범죄 발생 지역 분석 및 시각화
- **NLP 분석**: 워드클라우드 생성, 리뷰 감정 분석
- **타이타닉 데이터셋 분석**: 머신러닝 모델 학습 및 예측
- **미국 실업률 분석**: 지도 기반 시각화

### 문서

- `POSTMAN_GUIDE.md`: Postman API 테스트 가이드
- `RUN_SERVICE.md`: 서비스 실행 가이드
- `HEATMAP_GUIDE.md`: 히트맵 생성 가이드
- `MAP_VISUALIZATION_GUIDE.md`: 지도 시각화 가이드

---

## 3. 기술 스택

### 프레임워크 및 라이브러리

- **FastAPI**: 웹 프레임워크
- **Uvicorn**: ASGI 서버
- **Selenium**: 웹 자동화 및 크롤링
- **BeautifulSoup**: HTML 파싱
- **ChromaDB**: 벡터 데이터베이스
- **KoELECTRA**: 한국어 언어 모델
- **Pandas**: 데이터 처리
- **Matplotlib/Plotly**: 데이터 시각화

### 인프라

- **Docker**: 컨테이너화
- **Docker Compose**: 서비스 오케스트레이션

---

## 4. 서비스 포트

| 서비스 | 포트 | 설명 |
|--------|------|------|
| Gateway | 9000 | API Gateway |
| RAG Service | 9002 | RAG 서비스 |
| Feed Service | 9003 | Feed 서비스 |
| Chatbot Service | 9004 | 챗봇 서비스 |

---

## 5. 주요 기능 요약

### 5.1 크롤링 기능
- 카카오맵 장소 검색 및 메뉴 추출
- 뉴스 크롤링 (네이버, 다음, 구글)
- 음악 차트 크롤링 (벅스뮤직)
- 쇼핑몰 크롤링 (다나와)

### 5.2 AI 기능
- 가격 분석 및 바가지 탐지
- RAG 기반 질의응답
- 리뷰 감정 분석
- 워드클라우드 생성

### 5.3 데이터 분석
- 범죄 데이터 분석 및 시각화
- 실업률 데이터 분석
- 머신러닝 모델 학습 및 예측

---

## 6. 개발 가이드

### 환경 변수 설정

각 서비스는 환경 변수를 통해 설정됩니다. 주요 환경 변수:

- `KAKAO_REST_API_KEY`: 카카오맵 API 키
- `OPENAI_API_KEY`: OpenAI API 키 (챗봇 서비스)
- `FEED_SERVICE_URL`: Feed 서비스 URL
- `RAG_SERVICE_URL`: RAG 서비스 URL
- `CHATBOT_SERVICE_URL`: Chatbot 서비스 URL

### Docker 실행

```bash
# 전체 서비스 실행
docker-compose up -d

# 특정 서비스만 실행
docker-compose up -d crawler-service
```

### 로컬 실행

```bash
# Gateway 서비스
cd gateway
uvicorn app.main:app --host 0.0.0.0 --port 9000

# Crawler 서비스
cd services/crawlerservice
uvicorn app.main:app --host 0.0.0.0 --port 8000

# ML 서비스
cd services/mlservice
uvicorn app.main:app --host 0.0.0.0 --port 8001
```

---

## 7. 데이터 저장소

### 벡터 데이터베이스
- **ChromaDB**: RAG 서비스의 벡터 스토어 (`chatbotservice/rag.kroaddy.site/vector_db/chroma_db/`)

### 파일 저장소
- **CSV 파일**: 크롤링 데이터 (`crawlerservice/app/save/`)
- **이미지/HTML**: 분석 결과 파일 (`mlservice/app/save/`)

---

## 8. 향후 개선 사항

- [ ] `common/` 모듈 구현
- [ ] `transformer/` 서비스 구현
- [ ] 통합 로깅 시스템
- [ ] 모니터링 및 메트릭 수집
- [ ] API 문서 자동화 (Swagger/OpenAPI)

---

## 9. 참고 문서

각 서비스별 README 및 가이드 문서:

- `gateway/app/agent/README.md`: Agent 서비스 가이드
- `services/chatbotservice/README.md`: 챗봇 서비스 가이드
- `services/mlservice/README.md`: ML 서비스 가이드
- `services/mlservice/POSTMAN_GUIDE.md`: API 테스트 가이드

---

**최종 업데이트**: 2025년 1월

