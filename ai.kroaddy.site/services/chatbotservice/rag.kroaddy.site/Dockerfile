FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# 벡터 DB 및 데이터 디렉토리 생성
RUN mkdir -p vector_db data

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "9002"]

