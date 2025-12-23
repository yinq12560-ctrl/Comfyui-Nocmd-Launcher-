@echo off
chcp 65001 >nul
title 启动 ComfyUI

echo 正在启动 ComfyUI...
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 清理端口
for /f "tokens=5" %%i in ('netstat -ano 2^>nul ^| findstr :8188') do (
    taskkill /f /pid %%i >nul 2>&1
)

REM 检查文件是否存在
if exist "python_embeded\python.exe" (
    echo ✓ 找到 Python
) else (
    echo ❌ 找不到 Python
    pause
    exit /b 1
)

if exist "ComfyUI\main.py" (
    echo ✓ 找到 ComfyUI
) else (
    echo ❌ 找不到 ComfyUI
    pause
    exit /b 1
)

REM 创建并运行VBS脚本进行隐藏启动
(
echo Set ws = CreateObject^("Wscript.Shell"^)
echo ws.CurrentDirectory = "%~dp0"
echo ws.Run "cmd /c .\python_embeded\python.exe -s ComfyUI\main.py --windows-standalone-build", 0, False
) > "%temp%\启动comfyui.vbs"

start "" wscript.exe "%temp%\启动comfyui.vbs"

echo ✅ 已启动！
echo 🌐 请等待浏览器自动打开...
echo.
echo 窗口将在10秒后关闭...
timeout /t 10 /nobreak >nul