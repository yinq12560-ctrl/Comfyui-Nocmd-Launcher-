@echo off
chcp 65001 >nul
title 关闭 ComfyUI
color 0C

echo 正在关闭 ComfyUI...
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

echo 查找占用端口 8188 的进程...
set "count=0"

for /f "tokens=5" %%i in ('netstat -ano 2^>nul ^| findstr :8188') do (
    echo 发现进程 PID: %%i
    taskkill /f /pid %%i >nul 2>&1
    
    if errorlevel 1 (
        echo ❌ 无法终止进程 %%i
    ) else (
        echo ✅ 已终止进程 %%i
        set /a count+=1
    )
)

echo.
if %count%==0 (
    echo ℹ️  未发现运行中的 ComfyUI
) else (
    echo ✅ 共关闭了 %count% 个进程
)

echo.
echo 窗口将在5秒后关闭...
timeout /t 5 /nobreak >nul