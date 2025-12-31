FROM python:3.11-slim 
# 파이썬 3.13 대신 안정적인 3.11을 사용합니다.

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 도구 설치
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    default-jdk \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Java 환경 변수 설정
ENV JAVA_HOME=/usr/lib/jvm/default-java
ENV PATH=$JAVA_HOME/bin:$PATH

# requirements.txt 복사 및 의존성 설치
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# --- KoELECTRA 모델 파일 및 폰트 복사 (필수) ---
# 로컬 경로: app/resources/koelectra_local -> 컨테이너: /app/resources/koelectra_local
COPY app/resources/koelectra_local ./app/resources/koelectra_local

# WordCloud/KoNLP를 위한 한국어 폰트 복사 (파일명과 경로는 실제와 일치해야 함)
COPY app/resources/data/D2Coding.ttf ./app/resources/data/D2Coding.ttf
# ----------------------------------------------------

# 앱 코드 복사
COPY app ./app

# 포트 노출
EXPOSE 9010

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:9010/health')" || exit 1

# 서버 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9010"]