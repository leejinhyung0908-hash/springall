# Python 서비스들을 시작하는 PowerShell 스크립트
# 사용법: .\scripts\start-python-services.ps1

$ErrorActionPreference = "Stop"

Write-Host "Python 서비스 시작 중..." -ForegroundColor Green

# 루트 디렉토리로 이동
$rootDir = Split-Path -Parent $PSScriptRoot
Set-Location $rootDir

# 환경 변수 로드 (있는 경우)
if (Test-Path ".env") {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
        }
    }
    Write-Host "환경 변수 로드 완료" -ForegroundColor Yellow
}

# 로그 디렉토리 생성
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# 서비스 시작 함수
function Start-Service {
    param(
        [string]$ServiceName,
        [string]$ServiceDir,
        [int]$Port
    )
    
    Write-Host "시작: $ServiceName (포트 $Port)" -ForegroundColor Green
    
    if (-not (Test-Path $ServiceDir)) {
        Write-Host "경고: $ServiceDir 디렉토리가 없습니다. 건너뜁니다." -ForegroundColor Yellow
        return
    }
    
    $fullPath = Join-Path $rootDir $ServiceDir
    Set-Location $fullPath
    
    # 가상 환경 활성화 (있는 경우)
    $venvPath = Join-Path $fullPath "venv"
    if (Test-Path $venvPath) {
        & "$venvPath\Scripts\Activate.ps1"
    }
    
    # 서비스 실행 (백그라운드)
    $logFile = Join-Path $rootDir "logs\$ServiceName.log"
    $pidFile = Join-Path $rootDir "logs\$ServiceName.pid"
    
    $process = Start-Process -NoNewWindow -PassThru python `
        -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "$Port", "--reload" `
        -WorkingDirectory $fullPath `
        -RedirectStandardOutput $logFile `
        -RedirectStandardError $logFile
    
    $process.Id | Out-File -FilePath $pidFile -Encoding ASCII
    Write-Host "$ServiceName 시작됨 (PID: $($process.Id))" -ForegroundColor Green
    
    Set-Location $rootDir
}

# 서비스들 시작
Start-Service -ServiceName "agent-service" -ServiceDir "ai.kroaddy.site\gateway" -Port 9000
Start-Sleep -Seconds 1

Start-Service -ServiceName "rag-service" -ServiceDir "ai.kroaddy.site\services\chatbotservice\rag.kroaddy.site" -Port 9002
Start-Sleep -Seconds 1

Start-Service -ServiceName "feed-service" -ServiceDir "ai.kroaddy.site\services\crawlerservice\feed.kroaddy.site" -Port 9003
Start-Sleep -Seconds 1

Start-Service -ServiceName "chatbot-service" -ServiceDir "ai.kroaddy.site\services\chatbotservice" -Port 9004
Start-Sleep -Seconds 1

Start-Service -ServiceName "ml-service" -ServiceDir "ai.kroaddy.site\services\mlservice" -Port 9010

Write-Host "모든 Python 서비스 시작 완료!" -ForegroundColor Green
Write-Host "로그 확인: Get-Content logs\*.log -Wait" -ForegroundColor Yellow
Write-Host "서비스 중지: .\scripts\stop-python-services.ps1" -ForegroundColor Yellow

