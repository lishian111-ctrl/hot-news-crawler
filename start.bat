@echo off
chcp 65001 >nul
echo ========================================
echo     能源行业热点资讯系统 - 启动脚本
echo ========================================
echo.

cd /d "%~dp0backend"

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

REM 检查虚拟环境
if not exist "venv" (
    echo [提示] 正在创建虚拟环境...
    python -m venv venv
)

REM 激活虚拟环境
echo [提示] 激活虚拟环境...
call venv\Scripts\activate.bat

REM 安装依赖
echo [提示] 检查并安装依赖...
pip install -r requirements.txt -q

REM 创建必要的目录
if not exist "logs" mkdir logs
if not exist "..\data" mkdir ..\data

REM 启动应用
echo.
echo ========================================
echo     正在启动服务...
echo     访问地址：http://localhost:8000
echo     API 文档：http://localhost:8000/docs
echo ========================================
echo.

python main.py

pause
