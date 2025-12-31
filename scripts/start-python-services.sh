#!/bin/bash

# Python 서비스들을 시작하는 스크립트
# 사용법: ./scripts/start-python-services.sh

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Python 서비스 시작 중...${NC}"

# 루트 디렉토리로 이동
cd "$(dirname "$0")/.."

# 환경 변수 로드 (있는 경우)
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${YELLOW}환경 변수 로드 완료${NC}"
fi

# Python 가상 환경 확인
check_venv() {
    local service_dir=$1
    if [ -d "$service_dir/venv" ]; then
        echo "source $service_dir/venv/bin/activate"
    else
        echo ""
    fi
}

# 서비스 시작 함수
start_service() {
    local service_name=$1
    local service_dir=$2
    local port=$3
    
    echo -e "${GREEN}시작: $service_name (포트 $port)${NC}"
    
    if [ ! -d "$service_dir" ]; then
        echo -e "${YELLOW}경고: $service_dir 디렉토리가 없습니다. 건너뜁니다.${NC}"
        return
    fi
    
    cd "$service_dir"
    
    # 가상 환경 활성화 (있는 경우)
    if [ -d "venv" ]; then
        source venv/bin/activate
    fi
    
    # 의존성 확인
    if [ ! -f "requirements.txt" ]; then
        echo -e "${YELLOW}경고: requirements.txt가 없습니다.${NC}"
    fi
    
    # 서비스 실행 (백그라운드)
    uvicorn app.main:app --host 0.0.0.0 --port "$port" --reload > "../logs/${service_name}.log" 2>&1 &
    echo $! > "../logs/${service_name}.pid"
    
    echo -e "${GREEN}$service_name 시작됨 (PID: $(cat ../logs/${service_name}.pid))${NC}"
    
    cd - > /dev/null
}

# 로그 디렉토리 생성
mkdir -p logs

# 서비스들 시작
start_service "agent-service" "ai.kroaddy.site/gateway" 9000
sleep 1

start_service "rag-service" "ai.kroaddy.site/services/chatbotservice/rag.kroaddy.site" 9002
sleep 1

start_service "feed-service" "ai.kroaddy.site/services/crawlerservice/feed.kroaddy.site" 9003
sleep 1

start_service "chatbot-service" "ai.kroaddy.site/services/chatbotservice" 9004
sleep 1

start_service "ml-service" "ai.kroaddy.site/services/mlservice" 9010

echo -e "${GREEN}모든 Python 서비스 시작 완료!${NC}"
echo -e "${YELLOW}로그 확인: tail -f logs/*.log${NC}"
echo -e "${YELLOW}서비스 중지: ./scripts/stop-python-services.sh${NC}"

