# Java Gateway를 시작하는 PowerShell 스크립트
# 사용법: .\scripts\start-java-gateway.ps1

$ErrorActionPreference = "Stop"

Write-Host "Java Gateway 시작 중..." -ForegroundColor Green

# 루트 디렉토리로 이동
$rootDir = Split-Path -Parent $PSScriptRoot
Set-Location $rootDir

# 환경 변수는 시스템 환경 변수 또는 실행 시 인자로 전달
Write-Host "API Gateway 시작 중..." -ForegroundColor Green

# 루트 프로젝트 디렉토리로 이동 (멀티 프로젝트 구조)
$apiRootDir = Join-Path $rootDir "api.kroaddy.site"
Set-Location $apiRootDir

# Gradle 실행 권한 확인
$gradlewPath = Join-Path $apiRootDir "gradlew.bat"
if (-not (Test-Path $gradlewPath)) {
    Write-Host "오류: gradlew.bat를 찾을 수 없습니다." -ForegroundColor Red
    exit 1
}

# 로컬 프로파일로 실행 (gateway 서브프로젝트 지정)
Write-Host "Spring Profile: local" -ForegroundColor Green
& .\gradlew.bat :gateway:bootRun --args='--spring.profiles.active=local'

