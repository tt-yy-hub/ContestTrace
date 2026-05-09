@echo off
setlocal

echo =======================================
echo ContestTrace One-Click (Frontend + LLM)
echo =======================================
echo Frontend: http://127.0.0.1:8000
echo Recommend API: http://127.0.0.1:8001
echo Model: llama3.1
echo.

where ollama >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Ollama not found in PATH.
  echo Please install Ollama first: https://ollama.com/download
  pause
  exit /b 1
)

echo [1/4] Checking Ollama service (127.0.0.1:11434)...
netstat -ano | findstr "127.0.0.1:11434" >nul
if errorlevel 1 (
  echo Ollama is not running, starting service window...
  start "Ollama Service" cmd /k "ollama serve"
) else (
  echo Ollama is already running, skip starting service.
)

echo [2/4] Waiting Ollama API ready...
set OLLAMA_READY=0
for /L %%i in (1,1,8) do (
  powershell -NoProfile -Command "try { $r=Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:11434/api/tags' -TimeoutSec 2; if($r.StatusCode -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }"
  if not errorlevel 1 (
    set OLLAMA_READY=1
    goto :OLLAMA_READY_OK
  )
  timeout /t 1 /nobreak >nul
)

:OLLAMA_READY_OK
if "%OLLAMA_READY%"=="1" (
  echo Ollama API is ready.
) else (
  echo [WARN] Ollama API not confirmed ready yet.
  echo        If recommendation fails, wait a few seconds and retry.
)

echo Checking model llama3.1...
ollama show llama3.1 >nul 2>nul
if errorlevel 1 (
  echo [WARN] Model llama3.1 not found locally.
  echo        Run: ollama pull llama3.1
)

echo [3/4] Starting recommendation API...
start "ContestTrace Recommendation API" cmd /k "cd /d %~dp0 && python contesttrace\backend\recommend_server.py"

echo [4/4] Starting frontend server...
start "ContestTrace Frontend" cmd /k "cd /d %~dp0\contesttrace\frontend && python -m http.server 8000"

echo Waiting frontend health check...
set FRONTEND_READY=0
for /L %%i in (1,1,12) do (
  powershell -NoProfile -Command "try { $r=Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8000/index.html' -TimeoutSec 2; if($r.StatusCode -eq 200){ exit 0 } else { exit 1 } } catch { exit 1 }"
  if not errorlevel 1 (
    set FRONTEND_READY=1
    goto :FRONTEND_READY_OK
  )
  timeout /t 1 /nobreak >nul
)

:FRONTEND_READY_OK
if "%FRONTEND_READY%"=="1" (
  echo Opening browser...
  start "" "http://127.0.0.1:8000/index.html"
) else (
  echo [WARN] Frontend still not ready, skip auto-open.
  echo        Please open manually: http://127.0.0.1:8000/index.html
)

echo.
echo Startup commands sent.
echo Open http://127.0.0.1:8000/index.html
pause
