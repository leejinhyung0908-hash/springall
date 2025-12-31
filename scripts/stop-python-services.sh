#!/bin/bash

# Python 서비스들을 중지하는 스크립트
# 사용법: ./scripts/stop-python-services.sh

set -e

# 색상 정의
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Python 서비스 중지 중...${NC}"

# 루트 디렉토리로 이동
cd "$(dirname "$0")/.."

# PID 파일이 있는 경우 프로세스 종료
if [ -d "logs" ]; then
    for pidfile in logs/*.pid; do
        if [ -f "$pidfile" ]; then
            pid=$(cat "$pidfile")
            service_name=$(basename "$pidfile" .pid)
            
            if ps -p "$pid" > /dev/null 2>&1; then
                echo -e "${RED}중지: $service_name (PID: $pid)${NC}"
                kill "$pid" 2>/dev/null || true
            else
                echo -e "${YELLOW}$service_name는 이미 종료되었습니다.${NC}"
            fi
            
            rm -f "$pidfile"
        fi
    done
fi

# 포트 기반으로 프로세스 종료 (PID 파일이 없는 경우)
for port in 9000 9002 9003 9004 9010; do
    pid=$(lsof -ti:$port 2>/dev/null || true)
    if [ ! -z "$pid" ]; then
        echo -e "${RED}포트 $port에서 실행 중인 프로세스 종료 (PID: $pid)${NC}"
        kill "$pid" 2>/dev/null || true
    fi
done

echo -e "${YELLOW}모든 Python 서비스 중지 완료!${NC}"

