#!/bin/bash

# Auth Service를 시작하는 스크립트
# Auth Service는 auth와 log 기능을 모두 제공합니다 (포트 8081)
# 사용법: ./scripts/start-auth-service.sh

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Auth Service 시작 중...${NC}"

# 루트 디렉토리로 이동
cd "$(dirname "$0")/.."

# .env 파일 확인 (Spring Boot가 자동으로 읽음)
if [ -f .env ]; then
    echo -e "${GREEN}.env 파일 발견됨 (Spring Boot가 자동으로 로드합니다)${NC}"
else
    echo -e "${YELLOW}경고: .env 파일을 찾을 수 없습니다.${NC}"
fi

# Auth Service 디렉토리로 이동
cd service.kroaddy.site

# Gradle 실행 권한 확인
if [ ! -x "./gradlew" ]; then
    chmod +x ./gradlew
fi

# Auth Service 실행 (멀티 프로젝트 구조)
echo -e "${GREEN}Auth Service 실행 중 (포트 8081)...${NC}"
echo -e "${YELLOW}Auth API: http://localhost:8081/api/auth/**${NC}"
echo -e "${YELLOW}Log API: http://localhost:8081/api/log/**${NC}"

# 포트를 명시적으로 설정
export SERVER_PORT=8081
./gradlew :auth-service:bootRun --args='--server.port=8081'

