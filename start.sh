#!/bin/bash

# News Digest Startup Script
# 方便測試和發布的啟動腳本

echo "🚀 Starting News Digest Server..."

# 檢查 Python 環境
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.10+ first."
    exit 1
fi

# 檢查虛擬環境
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

# 啟動虛擬環境
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# 安裝依賴
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# 讀取環境變數（如果存在 .env 文件）
if [ -f ".env" ]; then
    echo "📄 Loading environment variables from .env..."
    export $(cat .env | grep -v '^#' | xargs)
elif [ -f "config.env.example" ]; then
    echo "📋 Creating .env file from config.env.example..."
    cp config.env.example .env
    echo "⚠️  Please edit .env file and add your OPENAI_API_KEY"
    echo "   Then run this script again."
    exit 1
fi

# 檢查 OpenAI API Key
if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your-openai-api-key-here" ]; then
    echo "⚠️  Warning: OPENAI_API_KEY is not set or is using placeholder value."
    echo "   The AI summarization feature will not work."
    echo ""
    echo "   To set it up:"
    echo "   1. Copy config.env.example to .env: cp config.env.example .env"
    echo "   2. Edit .env and replace 'your-openai-api-key-here' with your actual API key"
    echo "   3. Or set it with: export OPENAI_API_KEY='your-key-here'"
    echo ""
fi

# 設置默認值
export FLASK_HOST=${FLASK_HOST:-"0.0.0.0"}
export FLASK_PORT=${FLASK_PORT:-"5000"}
export FLASK_DEBUG=${FLASK_DEBUG:-"True"}

echo ""
echo "✅ Ready to start!"
echo "📍 Server will be available at: http://localhost:${FLASK_PORT}"
echo ""

# 啟動服務器
python backend/app.py
