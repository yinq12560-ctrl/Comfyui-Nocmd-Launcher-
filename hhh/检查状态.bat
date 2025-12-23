@echo off
chcp 65001 >nul
title ComfyUI 状态检查
color 0B

REM 切换到脚本所在目录
cd /d "%~dp0"

echo ========================================
echo     ComfyUI 运行状态
echo     %date% %time%
echo ========================================
echo.

echo 检查端口 8188...
netstat -ano | findstr :8188
if errorlevel 1 (
    echo.
    echo 🔴 状态: 未运行
    echo 🔗 端口: 8188 空闲
) else (
    echo.
    echo 🟢 状态: 运行中
    echo 🔗 地址: http://127.0.0.1:8188
)

echo.
echo 检查Python进程...
tasklist | findstr /i python

echo.
echo ========================================
echo     按任意键退出...
echo ========================================
pause >nul