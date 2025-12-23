@echo off
chcp 65001 >nul
title 安装监视器依赖

echo 正在安装监视器所需依赖...
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 检查文件是否存在
if exist "python_embeded\python.exe" (
    echo ✓ 找到 Python
) else (
    echo ❌ 找不到 Python
    pause
    exit /b 1
)

REM 使用便携版Python安装
python_embeded\python.exe -m pip install --upgrade pip
python_embeded\python.exe -m pip install pystray Pillow requests win10toast

echo.
echo ✅ 依赖安装完成！
echo.
echo 现在可以运行"启动监视器.bat"了
pause