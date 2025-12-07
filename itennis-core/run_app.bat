@echo off
REM What2Eat 项目运行脚本
REM 
REM 使用说明:
REM   run_app.bat       - 启动主程序
REM   run_app.bat debug - 启用调试模式运行

echo.
echo ========================================
echo         What2Eat - 今天吃什么？
echo ========================================
echo.

cd /d "%~dp0"

REM 设置虚拟环境Python路径
set PYTHON_EXE=..\..\..venv\Scripts\python.exe
if not exist "%PYTHON_EXE%" (
    echo ❌ 错误: 未找到虚拟环境Python
    echo 路径: %PYTHON_EXE%
    echo 请先创建虚拟环境或使用系统Python
    set PYTHON_EXE=python
)

REM 检查Python环境
echo 🔍 检查Python环境...
"%PYTHON_EXE%" --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ 错误: 无法运行Python
    pause
    exit /b 1
)

REM 检查必要的依赖
echo 🔍 检查项目依赖...
"%PYTHON_EXE%" -c "import yaml" >nul 2>&1
if %errorlevel% neq 0 (
    echo 📦 安装项目依赖...
    "%PYTHON_EXE%" -m pip install pyyaml
    if %errorlevel% neq 0 (
        echo ❌ 依赖安装失败
        pause
        exit /b 1
    )
)

REM 检查参数
set RUN_MODE=%1
if "%RUN_MODE%"=="debug" (
    echo 🐛 启用调试模式
    set WHAT2EAT_DEBUG=true
) else (
    set WHAT2EAT_DEBUG=false
)

REM 启动程序
echo 🚀 启动 What2Eat 程序...
echo.
echo 💡 提示: 按 Ctrl+C 可退出程序
echo.

cd src
"%PYTHON_EXE%" -m __main__

REM 检查程序退出状态
if %errorlevel% equ 0 (
    echo.
    echo ✅ 程序正常退出
) else (
    echo.
    echo ❌ 程序异常退出 (错误代码: %errorlevel%)
)

echo.
pause