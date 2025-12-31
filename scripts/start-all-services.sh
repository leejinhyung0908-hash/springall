#!/bin/bash
# 전체 서비스를 시작하는 Bash 스크립트
# 사용법: ./scripts/start-all-services.sh

set -e

echo "========================================"
echo "  전체 서비스 시작"
echo "========================================"
echo ""

# 루트 디렉토리로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

# .env 파일 확인
if [ -f ".env" ]; then
    echo "✓ .env 파일 발견됨"
else
    echo "⚠️ 경고: .env 파일을 찾을 수 없습니다."
fi

echo ""
echo "1단계: Python 서비스 시작 중..."
echo "----------------------------------------"

# Python 서비스 시작 (백그라운드)
bash "$SCRIPT_DIR/start-python-services.sh" &
PYTHON_PID=$!

echo ""
echo "Python 서비스 시작 완료. 잠시 대기 중..."
sleep 3

echo ""
echo "2단계: Auth Service 시작 중..."
echo "----------------------------------------"

# Auth Service 시작 (백그라운드)
bash "$SCRIPT_DIR/start-auth-service.sh" &
AUTH_PID=$!

echo "Auth Service 시작됨 (PID: $AUTH_PID)"
sleep 3

echo ""
echo "3단계: Java Gateway 시작 중..."
echo "----------------------------------------"

# Java Gateway 시작 (백그라운드)
bash "$SCRIPT_DIR/start-java-gateway.sh" &
GATEWAY_PID=$!

echo "Java Gateway 시작됨 (PID: $GATEWAY_PID)"
sleep 3

echo ""
echo "========================================"
echo "  모든 서비스 시작 완료!"
echo "========================================"
echo ""
echo "서비스 상태 확인:"
echo "  ./scripts/check-services.sh"
echo ""
echo "서비스 중지:"
echo "  ./scripts/stop-python-services.sh  (Python 서비스)"
echo "  kill $AUTH_PID  (Auth Service)"
echo "  kill $GATEWAY_PID  (Gateway)"
echo ""
echo "서비스 URL:"
echo "  Gateway:        http://localhost:8080"
echo "  Gateway Docs:   http://localhost:8080/docs"
echo "  Auth Service:   http://localhost:8081"
echo "  Agent Service:  http://localhost:9000"
echo "  RAG Service:    http://localhost:9002"
echo "  Feed Service:   http://localhost:9003"
echo "  Chatbot Service: http://localhost:9004"
echo "  ML Service:     http://localhost:9010"
echo ""

