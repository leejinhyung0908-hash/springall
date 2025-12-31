# 전체 서비스를 시작하는 PowerShell 스크립트
# 사용법: .\scripts\start-all-services.ps1
#
# 실행 순서:
# 1. Python 서비스들 (Agent, RAG, Feed, Chatbot, ML)
# 2. Auth Service (Java)
# 3. Java Gateway

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  전체 서비스 시작" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 루트 디렉토리로 이동
$rootDir = Split-Path -Parent $PSScriptRoot
Set-Location $rootDir

# .env 파일 확인
if (Test-Path ".env") {
    Write-Host "✓ .env 파일 발견됨" -ForegroundColor Green
} else {
    Write-Host "⚠️ 경고: .env 파일을 찾을 수 없습니다." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "1단계: Python 서비스 시작 중..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

# Python 서비스 시작
& "$PSScriptRoot\start-python-services.ps1"

Write-Host ""
Write-Host "Python 서비스 시작 완료. 잠시 대기 중..." -ForegroundColor Green
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "2단계: Auth Service 시작 중..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

# Auth Service 시작 (새 창에서)
$authServiceScript = Join-Path $PSScriptRoot "start-auth-service.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", "`"$authServiceScript`"" -WindowStyle Normal

Write-Host "Auth Service 시작됨 (새 창에서 실행 중)" -ForegroundColor Green
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "3단계: Java Gateway 시작 중..." -ForegroundColor Yellow
Write-Host "----------------------------------------" -ForegroundColor Gray

# Java Gateway 시작 (새 창에서)
$gatewayScript = Join-Path $PSScriptRoot "start-java-gateway.ps1"
Start-Process powershell -ArgumentList "-NoExit", "-File", "`"$gatewayScript`"" -WindowStyle Normal

Write-Host "Java Gateway 시작됨 (새 창에서 실행 중)" -ForegroundColor Green
Start-Sleep -Seconds 3

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  모든 서비스 시작 완료!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "서비스 상태 확인:" -ForegroundColor Yellow
Write-Host "  .\scripts\check-services.ps1" -ForegroundColor White
Write-Host ""
Write-Host "서비스 중지:" -ForegroundColor Yellow
Write-Host "  .\scripts\stop-python-services.ps1  (Python 서비스)" -ForegroundColor White
Write-Host "  Auth Service와 Gateway는 각각의 창에서 Ctrl+C로 중지" -ForegroundColor White
Write-Host ""
Write-Host "서비스 URL:" -ForegroundColor Yellow
Write-Host "  Gateway:        http://localhost:8080" -ForegroundColor White
Write-Host "  Gateway Docs:   http://localhost:8080/docs" -ForegroundColor White
Write-Host "  Auth Service:   http://localhost:8081" -ForegroundColor White
Write-Host "  Agent Service:  http://localhost:9000" -ForegroundColor White
Write-Host "  RAG Service:    http://localhost:9002" -ForegroundColor White
Write-Host "  Feed Service:   http://localhost:9003" -ForegroundColor White
Write-Host "  Chatbot Service: http://localhost:9004" -ForegroundColor White
Write-Host "  ML Service:     http://localhost:9010" -ForegroundColor White
Write-Host ""

