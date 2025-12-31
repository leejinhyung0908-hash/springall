#!/bin/bash

# Java Gateway를 시작하는 스크립트
# 사용법: ./scripts/start-java-gateway.sh

set -e

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Java Gateway 시작 중...${NC}"

# 루트 디렉토리로 이동
cd "$(dirname "$0")/.."

# 환경 변수는 시스템 환경 변수 또는 실행 시 인자로 전달
echo -e "${GREEN}API Gateway 시작 중...${NC}"

# 루트 프로젝트 디렉토리로 이동 (멀티 프로젝트 구조)
cd api.kroaddy.site

# Gradle 실행 권한 확인
if [ ! -x "./gradlew" ]; then
    chmod +x ./gradlew
fi

# 로컬 프로파일로 실행 (gateway 서브프로젝트 지정)
echo -e "${GREEN}Spring Profile: local${NC}"
./gradlew :gateway:bootRun --args='--spring.profiles.active=local'

