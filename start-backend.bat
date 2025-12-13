@echo off
REM 快速启动前后端服务的脚本

echo ========================================
echo   AiTeni 网球智能教练 - 开发环境启动
echo ========================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [1/3] 检查后端依赖...
cd /d "%~dp0aiteni-backend"

REM 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo [提示] 发现虚拟环境，正在激活...
    call venv\Scripts\activate.bat
) else (
    echo [提示] 未发现虚拟环境，使用全局 Python
)

REM 检查依赖是否安装
python -c "import django" >nul 2>&1
if errorlevel 1 (
    echo [警告] Django 未安装，正在安装依赖...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo [错误] 依赖安装失败
        pause
        exit /b 1
    )
)

echo [2/3] 启动后端服务...
echo.
echo ----------------------------------------
echo 后端服务地址: http://localhost:8000
echo ----------------------------------------
echo.
echo [提示] 保持此窗口打开
echo [提示] 按 Ctrl+C 停止服务
echo.

REM 启动后端服务
python manage.py runserver 0.0.0.0:8000

pause
