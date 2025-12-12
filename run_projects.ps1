$PathToDjango = "C:\Users\User\BI_mvp\backend_django"   # путь к Django-проекту
$PathToFastAPI = "C:\Users\User\BI_mvp\fastapi_ml"      # путь к FastAPI-проекту
$VenvPath = "C:\Users\User\BI_mvp\.venv"                # путь к виртуальному окружению
$PythonExe = Join-Path $VenvPath "Scripts\python.exe"   # путь к python.exe в .venv
$FastAPIAppModule = "app.main:app"                      # модуль FastAPI (поправьте при необходимости)
$FastAPIPort = 8001
$DjangoPort = 8000

# Папка для логов (создаётся, но в варианте 1 логи не будут автоматически перенаправляться)
$LogsDir = Join-Path (Get-Location) "logs"
if (-not (Test-Path $LogsDir)) {
    New-Item -Path $LogsDir -ItemType Directory | Out-Null
}

function Write-ErrAndExit([string]$msg) {
    Write-Host "ERROR: $msg" -ForegroundColor Red
    exit 1
}

# Проверки наличия директорий и python
if (-not (Test-Path $PathToDjango)) { Write-ErrAndExit "Django path not found: $PathToDjango" }
if (-not (Test-Path $PathToFastAPI)) { Write-ErrAndExit "FastAPI path not found: $PathToFastAPI" }
if (-not (Test-Path $PythonExe)) { Write-ErrAndExit "Python executable not found in venv: $PythonExe" }

# Проверка версий django и uvicorn (информативно)
function Get-PackageVersion([string]$pkg) {
    try {
        $res = & $PythonExe -c "import importlib; m=importlib.import_module('$pkg'); print(getattr(m,'__version__','unknown'))" 2>$null
        if ($LASTEXITCODE -ne 0) { return $null }
        return $res.Trim()
    } catch { return $null }
}
$djangoVer = Get-PackageVersion "django"
$uvicornVer = Get-PackageVersion "uvicorn"
if ($djangoVer) { Write-Host "Django version: $djangoVer" } else { Write-Host "Warning: Django not found in venv" -ForegroundColor Yellow }
if ($uvicornVer) { Write-Host "uvicorn version: $uvicornVer" } else { Write-Host "Warning: uvicorn not found in venv" -ForegroundColor Yellow }

# Проверка свободности порта
function Test-PortFree([int]$port) {
    try {
        $listener = [System.Net.Sockets.TcpListener]::new([System.Net.IPAddress]::Any, $port)
        $listener.Start()
        $listener.Stop()
        return $true
    } catch {
        return $false
    }
}
if (-not (Test-PortFree $DjangoPort)) { Write-Host "Port $DjangoPort appears to be in use." -ForegroundColor Yellow }
if (-not (Test-PortFree $FastAPIPort)) { Write-Host "Port $FastAPIPort appears to be in use." -ForegroundColor Yellow }

# Команды запуска
$DjangoArgs = "$PathToDjango\manage.py runserver 0.0.0.0:$DjangoPort"
$FastAPIArgs = "-m uvicorn $FastAPIAppModule --host 0.0.0.0 --port $FastAPIPort --app-dir `"$PathToFastAPI`" --reload"

Write-Host "Запуск Django:"
Write-Host "  $PythonExe $DjangoArgs"
Write-Host "Запуск FastAPI:"
Write-Host "  $PythonExe $FastAPIArgs"

# Запускаем Django в новом окне (без RedirectStandardOutput/RedirectStandardError)
$startInfoDjango = @{
    FilePath = $PythonExe
    ArgumentList = $DjangoArgs
    WorkingDirectory = $PathToDjango
    NoNewWindow = $false
}
$procD = Start-Process @startInfoDjango -PassThru

# Запускаем FastAPI в новом окне (без Redirect...)
$startInfoFast = @{
    FilePath = $PythonExe
    ArgumentList = $FastAPIArgs
    WorkingDirectory = $PathToFastAPI
    NoNewWindow = $false
}
$procF = Start-Process @startInfoFast -PassThru

Start-Sleep -Milliseconds 300

Write-Host ""
Write-Host "Процессы запущены (если Start-Process вернул объекты):"
if ($procD) { Write-Host "  Django PID: $($procD.Id)" } else { Write-Host "  Django PID: (не получен)" }
if ($procF) { Write-Host "  FastAPI PID: $($procF.Id)" } else{ Write-Host "  FastAPI PID: (не получен)" }

Write-Host ""
Write-Host "Окна приложений открыты отдельно. Вывод приложений виден в этих окнах."
Write-Host "Если нужно сохранить вывод в файл, можно в дальнейшем запускать через cmd.exe с перенаправлением:"
Write-Host "  cmd /c `"$PythonExe $DjangoArgs`" > C:\path\to\logs\django.log 2>&1"
Write-Host "  cmd /c `"$PythonExe $FastAPIArgs`" > C:\path\to\logs\fastapi.log 2>&1"

Write-Host ""
Write-Host "Для остановки процессов — закройте соответствующие окна или используйте Stop-Process -Id <PID>."
