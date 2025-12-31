# 서비스 상태를 확인하는 PowerShell 스크립트
# 사용법: .\scripts\check-services.ps1

$ErrorActionPreference = "Continue"

Write-Host "서비스 상태 확인 중..." -ForegroundColor Cyan
Write-Host ""

# 서비스 포트 목록
$services = @{
    "Java Gateway" = 8080
    "Agent Service" = 9000
    "RAG Service" = 9002
    "Feed Service" = 9003
    "Chatbot Service" = 9004
    "ML Service" = 9010
    "Auth Service" = 8081
}

# 서비스 확인 함수
function Test-Service {
    param(
        [string]$ServiceName,
        [int]$Port
    )
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port" -Method Get -TimeoutSec 2 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            Write-Host "✓ $ServiceName (포트 $Port) - 실행 중" -ForegroundColor Green
            return $true
        }
    } catch {
        Write-Host "✗ $ServiceName (포트 $Port) - 실행 중이 아님" -ForegroundColor Red
        return $false
    }
    
    Write-Host "✗ $ServiceName (포트 $Port) - 실행 중이 아님" -ForegroundColor Red
    return $false
}

# 각 서비스 확인
$allRunning = $true
foreach ($service in $services.Keys) {
    $port = $services[$service]
    if (-not (Test-Service -ServiceName $service -Port $port)) {
        $allRunning = $false
    }
}

Write-Host ""
if ($allRunning) {
    Write-Host "모든 서비스가 실행 중입니다!" -ForegroundColor Green
} else {
    Write-Host "일부 서비스가 실행 중이 아닙니다." -ForegroundColor Yellow
    Write-Host "서비스를 시작하려면 .\scripts\start-python-services.ps1를 실행하세요." -ForegroundColor Yellow
}

