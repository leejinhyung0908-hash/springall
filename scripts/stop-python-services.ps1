# Python 서비스들을 중지하는 PowerShell 스크립트
# 사용법: .\scripts\stop-python-services.ps1

$ErrorActionPreference = "Stop"

Write-Host "Python 서비스 중지 중..." -ForegroundColor Yellow

# 루트 디렉토리로 이동
$rootDir = Split-Path -Parent $PSScriptRoot
Set-Location $rootDir

# PID 파일이 있는 경우 프로세스 종료
$logsDir = Join-Path $rootDir "logs"
if (Test-Path $logsDir) {
    Get-ChildItem "$logsDir\*.pid" | ForEach-Object {
        $pid = Get-Content $_.FullName
        $serviceName = $_.BaseName
        
        try {
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($process) {
                Write-Host "중지: $serviceName (PID: $pid)" -ForegroundColor Red
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            } else {
                Write-Host "$serviceName는 이미 종료되었습니다." -ForegroundColor Yellow
            }
        } catch {
            Write-Host "$serviceName 프로세스를 찾을 수 없습니다." -ForegroundColor Yellow
        }
        
        Remove-Item $_.FullName -Force -ErrorAction SilentlyContinue
    }
}

# 포트 기반으로 프로세스 종료
$ports = @(9000, 9002, 9003, 9004, 9010)
foreach ($port in $ports) {
    $processes = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | 
        Select-Object -ExpandProperty OwningProcess -Unique
    
    foreach ($pid in $processes) {
        try {
            $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
            if ($process -and $process.ProcessName -eq "python") {
                Write-Host "포트 $port에서 실행 중인 프로세스 종료 (PID: $pid)" -ForegroundColor Red
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            }
        } catch {
            # 무시
        }
    }
}

Write-Host "모든 Python 서비스 중지 완료!" -ForegroundColor Yellow

