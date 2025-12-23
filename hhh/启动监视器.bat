@echo off
chcp 65001 >nul
title 启动 ComfyUI 监视器

echo 正在启动 ComfyUI 系统托盘监视器...
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

echo 当前目录：%cd%
echo.

REM 检查文件是否存在
if exist "python_embeded\pythonw.exe" (
    echo ✓ 找到 pythonw.exe
) else (
    echo ❌ 找不到 pythonw.exe
    pause
    exit /b 1
)

if exist "监视器.pyw" (
    echo ✓ 找到 监视器.pyw
) else (
    echo ❌ 找不到 监视器.pyw
    pause
    exit /b 1
)

echo.
echo 正在启动监视器...

REM 尝试直接运行
start "" /B "python_embeded\pythonw.exe" "监视器.pyw"

if %errorlevel% neq 0 (
    echo ❌ 启动失败，错误代码：%errorlevel%
    echo.
    echo 尝试替代方法...
    
    REM 尝试使用python.exe
    if exist "python_embeded\python.exe" (
        echo 使用python.exe代替pythonw.exe...
        start "" /B "python_embeded\python.exe" "监视器.pyw"
    )
)

echo.
echo 提示：监视器将在后台运行，请查看系统托盘图标
timeout /t 3 /nobreak >nul