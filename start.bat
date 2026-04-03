@echo off
chcp 65001 >nul
echo ========================================
echo     能源行业信息情报系统 - 启动脚本
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

REM 安装后端依赖
cd /d "%~dp0backend"
echo [1/4] 正在检查后端依赖...
pip install -r requirements.txt -q 2>nul

REM 创建必要的目录
if not exist "logs" mkdir logs
if not exist "..\data" mkdir ..\data

REM 构建前端（如果 node 可用）
cd /d "%~dp0frontend"
where node >nul 2>&1
if %errorlevel%==0 (
    if not exist "dist" (
        echo [2/4] 正在构建前端...
        call npm install --silent 2>nul
        call npm run build 2>nul
        if errorlevel 1 (
            echo [警告] 前端构建失败，将仅启动 API 服务
        ) else (
            echo [2/4] 前端构建完成
        )
    ) else (
        echo [2/4] 前端已构建，跳过
    )
) else (
    echo [警告] 未检测到 Node.js，跳过前端构建
    echo         如需前端界面，请先安装 Node.js 并执行：
    echo         cd frontend ^&^& npm install ^&^& npm run build
)

REM 启动后端服务
cd /d "%~dp0backend"
echo.
echo ========================================
echo [3/4] 正在启动服务...
echo.
echo     访问地址：http://localhost:8000
echo     API 文档：http://localhost:8000/docs
echo ========================================
echo.

python main.py

pause
