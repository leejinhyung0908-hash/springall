# Auth Service를 시작하는 PowerShell 스크립트
# Auth Service는 auth와 log 기능을 모두 제공합니다 (포트 8081)
# 사용법: .\scripts\start-auth-service.ps1

$ErrorActionPreference = "Stop"

Write-Host "Auth Service 시작 중..." -ForegroundColor Green

# 루트 디렉토리로 이동
$rootDir = Split-Path -Parent $PSScriptRoot
Set-Location $rootDir

# .env 파일 확인 (Spring Boot가 자동으로 읽음)
if (Test-Path ".env") {
    Write-Host ".env 파일 발견됨 (Spring Boot가 자동으로 로드합니다)" -ForegroundColor Green
} else {
    Write-Host "경고: .env 파일을 찾을 수 없습니다." -ForegroundColor Yellow
}

# Auth Service 디렉토리로 이동
$serviceDir = Join-Path $rootDir "service.kroaddy.site"
Set-Location $serviceDir

# Gradle 실행 권한 확인
$gradlewPath = Join-Path $serviceDir "gradlew.bat"
if (-not (Test-Path $gradlewPath)) {
    Write-Host "오류: gradlew.bat를 찾을 수 없습니다." -ForegroundColor Red
    exit 1
}

# Auth Service 실행 (멀티 프로젝트 구조)
Write-Host "Auth Service 실행 중 (포트 8081)..." -ForegroundColor Green
Write-Host "Auth API: http://localhost:8081/api/auth/**" -ForegroundColor Yellow
Write-Host "Log API: http://localhost:8081/api/log/**" -ForegroundColor Yellow

# 포트를 명시적으로 설정
$env:SERVER_PORT = "8081"

# Gradle 실행 (환경 변수는 Process 레벨에서 자동으로 상속됨)
Write-Host "Gradle 실행 중..." -ForegroundColor Cyan
& .\gradlew.bat :auth-service:bootRun --args='--server.port=8081'

