@echo off
REM News Digest Startup Script for Windows
REM 方便測試和發布的啟動腳本

echo 🚀 Starting News Digest Server...

REM 檢查 Python 環境
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.10+ first.
    pause
    exit /b 1
)

REM 檢查虛擬環境
if not exist ".venv" (
    echo 📦 Creating virtual environment...
    python -m venv .venv
)

REM 啟動虛擬環境
echo 🔧 Activating virtual environment...
call .venv\Scripts\activate.bat

REM 安裝依賴
echo 📥 Installing dependencies...
pip install -q -r requirements.txt

REM 檢查 OpenAI API Key
if "%OPENAI_API_KEY%"=="" (
    echo ⚠️  Warning: OPENAI_API_KEY is not set.
    echo    The AI summarization feature will not work.
    echo    Set it with: set OPENAI_API_KEY=your-key-here
    echo.
)

REM 讀取環境變數（如果存在 .env 文件）
if exist ".env" (
    echo 📄 Loading environment variables from .env...
    for /f "tokens=*" %%a in (.env) do (
        set "%%a"
    )
)

REM 設置默認值
if "%FLASK_HOST%"=="" set FLASK_HOST=0.0.0.0
if "%FLASK_PORT%"=="" set FLASK_PORT=5000
if "%FLASK_DEBUG%"=="" set FLASK_DEBUG=True

echo.
echo ✅ Ready to start!
echo 📍 Server will be available at: http://localhost:%FLASK_PORT%
echo.

REM 啟動服務器
python backend\app.py

pause
