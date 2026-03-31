@echo off
chcp 65001 >nul
setlocal

cd /d "%~dp0"

echo === ContestTrace 一键运行 ===
echo 1) 环境检查
echo 2) 打开主菜单
echo.

echo [1/2] 正在检查环境...
python check_env.py
if errorlevel 1 (
  echo.
  echo 环境检查未通过，请先按提示安装依赖后再运行。
  pause
  exit /b 1
)

echo.
echo [2/2] 启动主菜单...
python run_app.py
pause

