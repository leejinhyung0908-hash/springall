#!/bin/bash

# 서비스 상태를 확인하는 스크립트
# 사용법: ./scripts/check-services.sh

set -e

# 색상 정의
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "서비스 상태 확인 중..."
echo ""

# 서비스 포트 목록
declare -A services=(
    ["Java Gateway"]="8080"
    ["Agent Service"]="9000"
    ["RAG Service"]="9002"
    ["Feed Service"]="9003"
    ["Chatbot Service"]="9004"
    ["ML Service"]="9010"
    ["Auth Service"]="8081"
)

# 서비스 확인 함수
check_service() {
    local service_name=$1
    local port=$2
    
    if curl -s -o /dev/null -w "%{http_code}" "http://localhost:$port" > /dev/null 2>&1; then
        echo -e "${GREEN}✓${NC} $service_name (포트 $port) - 실행 중"
        return 0
    else
        echo -e "${RED}✗${NC} $service_name (포트 $port) - 실행 중이 아님"
        return 1
    fi
}

# 각 서비스 확인
all_running=true
for service in "${!services[@]}"; do
    port=${services[$service]}
    if ! check_service "$service" "$port"; then
        all_running=false
    fi
done

echo ""
if [ "$all_running" = true ]; then
    echo -e "${GREEN}모든 서비스가 실행 중입니다!${NC}"
else
    echo -e "${YELLOW}일부 서비스가 실행 중이 아닙니다.${NC}"
    echo -e "${YELLOW}서비스를 시작하려면 ./scripts/start-python-services.sh를 실행하세요.${NC}"
fi

