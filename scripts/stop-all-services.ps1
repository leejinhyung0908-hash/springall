# 전체 서비스를 중지하는 PowerShell 스크립트
# 사용법: .\scripts\stop-all-services.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  전체 서비스 중지" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 루트 디렉토리로 이동
$rootDir = Split-Path -Parent $PSScriptRoot
Set-Location $rootDir

# Python 서비스 중지
Write-Host "1단계: Python 서비스 중지 중..." -ForegroundColor Yellow
& "$PSScriptRoot\stop-python-services.ps1"

Write-Host ""
Write-Host "2단계: Java 서비스 중지 중..." -ForegroundColor Yellow

# Java 서비스 프로세스 찾기 및 중지
$javaProcesses = Get-Process -Name "java" -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -like "*gateway*" -or 
    $_.CommandLine -like "*auth-service*" -or
    $_.Path -like "*gateway*" -or
    $_.Path -like "*auth-service*"
}

if ($javaProcesses) {
    foreach ($proc in $javaProcesses) {
        Write-Host "Java 프로세스 중지: PID $($proc.Id)" -ForegroundColor Yellow
        Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
    }
} else {
    Write-Host "실행 중인 Java 서비스를 찾을 수 없습니다." -ForegroundColor Gray
}

# 포트별로 프로세스 중지
$ports = @(8080, 8081)
foreach ($port in $ports) {
    $process = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | 
        Select-Object -ExpandProperty OwningProcess -Unique
    
    if ($process) {
        Write-Host "포트 $port 사용 중인 프로세스 중지: PID $process" -ForegroundColor Yellow
        Stop-Process -Id $process -Force -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  모든 서비스 중지 완료!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

