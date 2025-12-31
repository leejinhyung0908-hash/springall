# Feed Service

크롤링 및 피드 수집 서비스입니다.

## 구조

```
feed.kroaddy.site/
├── app/
│   ├── main.py              # FastAPI 애플리케이션
│   ├── bs_demo/             # BeautifulSoup 크롤러
│   │   ├── bugsmusic.py
│   │   ├── aggregate.py
│   │   ├── hazard_analyzer.py
│   │   ├── naver.py
│   │   ├── daum.py
│   │   └── google.py
│   └── sel_demo/            # Selenium 크롤러
│       └── danawa.py
├── Dockerfile
└── requirements.txt
```

## API 엔드포인트

- `GET /` - 서비스 상태
- `GET /bugsmusic` - Bugs Music 차트 크롤링
- `GET /danawa` - 다나와 제품 크롤링
- `GET /news?keywords=키워드1,키워드2` - 뉴스 수집
- `GET /risk?keywords=키워드1,키워드2` - 위험 지역 분석
- `GET /hazard?keywords=키워드1,키워드2` - 위험도 상세 분석

## 실행

```bash
# 개발 모드
uvicorn app.main:app --reload --host 0.0.0.0 --port 9003

# Docker
docker build -t feed-service .
docker run -p 9003:9003 feed-service
```

## 포트

- 기본 포트: **9003**

