# Daily Digest

一個可在本地運行的新聞摘要工具。使用者輸入感興趣的主題和位置後，系統會從 Google 新聞 RSS 擷取過去 24 小時內的多則熱門新聞，並使用 OpenAI API 生成智能總結和關鍵洞察。

A local news summarization tool. After entering topics of interest and location, the system fetches multiple trending news articles from the past 24 hours via Google News RSS, and uses OpenAI API to generate intelligent summaries and key insights.

## ✨ 主要功能 Features

- 🌐 **中英文雙語支援（英文優先）** - 完整的中英文界面切換，默認語言為英文
- 🌍 **多地區支援** - 支援 20+ 個國家/地區，包括主要城市
- 📍 **位置自動偵測** - 一鍵偵測當前位置並自動選擇對應地區
- ✏️ **手動輸入地區** - 支援自定義城市或地區名稱
- 🤖 **AI 智能總結** - 使用 OpenAI GPT 生成「今天需要注意的事情」和「Take Away」
- 📰 **多篇新聞** - 一次獲取最多 15 則相關新聞
- 🎨 **Gen Z 風格設計** - 現代、活潑、充滿活力的用戶界面
- 🔗 **簡潔展示** - 新聞列表只顯示標題和連結，重點突出 AI 總結
- 🚀 **發布就緒** - 包含啟動腳本和環境配置，方便測試和部署

- 🌐 **Bilingual Support (English First)** - Full Chinese/English interface switching, default language is English
- 🌍 **Multi-Region Support** - Supports 20+ countries/regions including major cities
- 📍 **Auto Location Detection** - One-click location detection with automatic region selection
- ✏️ **Custom Region Input** - Support custom city or region names
- 🤖 **AI-Powered Summaries** - Uses OpenAI GPT to generate "Things to Watch Today" and "Take Away"
- 📰 **Multiple Articles** - Fetch up to 15 relevant news articles at once
- 🎨 **Gen Z Design** - Modern, vibrant, energetic user interface
- 🔗 **Clean Display** - News list shows only titles and links, highlighting AI summaries
- 🚀 **Production Ready** - Includes startup scripts and environment configuration for easy testing and deployment

## 技術棧 Tech Stack

- **後端 Backend**: Flask + feedparser + BeautifulSoup + OpenAI API
- **前端 Frontend**: 原生 HTML/CSS/JS（單頁靜態介面）Native HTML/CSS/JS (Single Page)

## 環境需求 Requirements

- Python 3.10+（含 `venv`）
- OpenAI API Key（用於 AI 總結功能）
- 可連線到外部 RSS 來源的網路

- Python 3.10+ (with `venv`)
- OpenAI API Key (for AI summarization)
- Internet connection to external RSS sources

## 🚀 快速部署到生產環境 | Quick Deploy to Production

想要讓其他人使用？查看 [DEPLOYMENT.md](DEPLOYMENT.md) 獲取完整的部署指南。

Want to make it available to others? Check [DEPLOYMENT.md](DEPLOYMENT.md) for complete deployment guide.

**最簡單的方式（推薦）| Easiest Way (Recommended):**
1. 將代碼推送到 GitHub
2. 在 [Railway](https://railway.app) 或 [Render](https://render.com) 註冊
3. 連接 GitHub 倉庫並設置環境變數
4. 自動部署完成！

## 快速開始 Quick Start

### 方法一：使用啟動腳本（推薦）Method 1: Using Startup Script (Recommended)

**macOS/Linux:**
```bash
./start.sh
```

**Windows:**
```cmd
start.bat
```

啟動腳本會自動：
- 檢查 Python 環境
- 創建虛擬環境（如果不存在）
- 安裝所有依賴
- 檢查 OpenAI API Key
- 啟動服務器

The startup script will automatically:
- Check Python environment
- Create virtual environment (if not exists)
- Install all dependencies
- Check OpenAI API Key
- Start the server

### 方法二：手動啟動 Method 2: Manual Setup

#### 1. 設定 OpenAI API Key

**方法一：使用 .env 檔案（推薦）**

```bash
# 複製配置範例檔案
cp config.env.example .env

# 編輯 .env 檔案，填入你的 OpenAI API Key
# 打開 .env 檔案，將 your-openai-api-key-here 替換為你的實際 API Key
```

**方法二：使用環境變數**

```bash
# macOS/Linux
export OPENAI_API_KEY="your-api-key-here"

# Windows (PowerShell)
$env:OPENAI_API_KEY="your-api-key-here"
```

**注意**: 
- 如果未設定 API Key，系統仍可運作，但不會生成 AI 總結
- 系統會在前端顯示「AI 摘要功能目前不可用」的提示
- 獲取 API Key: https://platform.openai.com/api-keys

**Note**: 
- If API key is not set, the system will still work but won't generate AI summaries
- The system will display "AI summarization is currently unavailable" notice in the frontend
- Get API Key: https://platform.openai.com/api-keys

#### 2. 安裝依賴 Install Dependencies

```bash
# 建立虛擬環境 Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安裝依賴 Install dependencies
pip install -r requirements.txt
```

#### 3. 啟動伺服器 Start Server

```bash
# 使用默認配置
python backend/app.py

# 或使用環境變數自定義
FLASK_HOST=0.0.0.0 FLASK_PORT=8080 FLASK_DEBUG=False python backend/app.py
```

啟動後瀏覽器開啟 <http://localhost:5000> 即可看到問卷與摘要。

After starting, open <http://localhost:5000> in your browser to see the questionnaire and summaries.

## 使用方式 Usage

1. **選擇語言** - 點擊右上角的「中文」或「English」切換語言（默認為英文）
2. **輸入位置** - 在地址欄位中輸入你的位置，格式為：城市，州/省，國家
   - 例如：`New York, NY, USA` 或 `London, UK` 或 `台北，台灣`
3. **填寫主題** - 輸入感興趣的新聞主題，可選填自訂 RSS 網址
4. **生成摘要** - 點擊「Generate Daily Digest」按鈕
5. **查看結果** - 系統會顯示：
   - **今日重點**（如果 AI 功能可用）：AI 生成的「今天需要注意的事情」和「Take Away」
   - **AI 狀態提示**（如果 AI 功能不可用）：顯示「AI 摘要功能目前不可用」
   - **新聞列表**：過去 24 小時內所有相關新聞的標題和連結（字體較小，便於瀏覽）

**注意**：系統只會獲取過去 24 小時內的新聞。

1. **Select Language** - Click "中文" or "English" in the top right to switch languages (default is English)
2. **Enter Location** - Enter your location in the address field, format: City, State/Province, Country
   - Examples: `New York, NY, USA` or `London, UK` or `Taipei, Taiwan`
3. **Enter Topics** - Enter news topics of interest, optionally provide custom RSS URL
4. **Generate Digest** - Click "Generate Daily Digest" button
5. **View Results** - The system will display:
   - **Today's Highlights** (if AI is available): AI-generated "Things to Watch Today" and "Take Away"
   - **AI Status Notice** (if AI is unavailable): Shows "AI summarization is currently unavailable"
   - **News List**: Titles and links of all relevant news articles from the past 24 hours (smaller font for easy browsing)

**Note**: The system only fetches news from the past 24 hours.

## 主要流程 Workflow

1. 使用者輸入想看的新聞類別、地區，及可選的 RSS/新聞網址
2. 後端根據輸入動態組合 Google 新聞 RSS，或直接解析使用者提供的 RSS
3. 取回最新條目（最多 15 則）
4. 使用 OpenAI API 分析所有新聞標題，生成：
   - 「今天需要注意的事情」（2-3 個重點）
   - 「Take Away」（一句話總結最重要的洞察）
5. 前端以 Gen Z 風格呈現 AI 總結和新聞列表

1. User inputs news category, region, and optional RSS/news URL
2. Backend dynamically constructs Google News RSS or parses user-provided RSS
3. Fetches latest entries (up to 15 articles)
4. Uses OpenAI API to analyze all news headlines and generate:
   - "Things to Watch Today" (2-3 key points)
   - "Take Away" (one sentence summarizing the most important insight)
5. Frontend displays AI summaries and news list in Gen Z style

## 發布配置 Production Configuration

### 環境變數 Environment Variables

| 變數 Variable | 說明 Description | 默認值 Default |
|--------------|-----------------|---------------|
| `OPENAI_API_KEY` | OpenAI API 密鑰 | 無（必需）None (Required) |
| `FLASK_HOST` | 服務器主機地址 | `0.0.0.0` |
| `FLASK_PORT` | 服務器端口 | `5000` |
| `FLASK_DEBUG` | 調試模式 | `True` |

### 生產環境部署 Production Deployment

```bash
# 設置生產環境變數
export FLASK_HOST=0.0.0.0
export FLASK_PORT=5000
export FLASK_DEBUG=False
export OPENAI_API_KEY=your-api-key-here

# 使用生產級 WSGI 服務器（推薦）
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

### Docker 部署（可選）Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "backend/app.py"]
```

## 客製化建議 Customization

- **更多地區**: 在 `backend/app.py` 的 `REGION_CONFIG` 中新增國家代碼
- **調整新聞數量**: 修改 `backend/app.py` 中的 `MAX_NEWS_COUNT` 變數
- **更換 AI 模型**: 在 `generate_takeaway()` 函數中修改 `model` 參數（如使用 `gpt-4`）
- **前端樣式**: 修改 `public/index.html` 中的 CSS 變數和樣式
- **位置服務**: 可替換 Nominatim API 為其他地理編碼服務

- **More Regions**: Add country codes to `REGION_CONFIG` in `backend/app.py`
- **Adjust News Count**: Modify `MAX_NEWS_COUNT` variable in `backend/app.py`
- **Change AI Model**: Modify `model` parameter in `generate_takeaway()` function (e.g., use `gpt-4`)
- **Frontend Styling**: Modify CSS variables and styles in `public/index.html`
- **Location Service**: Replace Nominatim API with other geocoding services

## 支援的地區 Supported Regions

目前支援以下 20+ 個國家/地區：

**亞洲 Asia**: Taiwan, Hong Kong, China, Japan, South Korea, Singapore, India  
**美洲 Americas**: United States, Canada, Mexico, Brazil  
**歐洲 Europe**: United Kingdom, Germany, France, Italy, Spain, Netherlands  
**大洋洲 Oceania**: Australia, New Zealand

可通過「Custom Input」模式輸入其他城市或地區名稱。

Currently supports the following 20+ countries/regions:

**Asia**: Taiwan, Hong Kong, China, Japan, South Korea, Singapore, India  
**Americas**: United States, Canada, Mexico, Brazil  
**Europe**: United Kingdom, Germany, France, Italy, Spain, Netherlands  
**Oceania**: Australia, New Zealand

You can enter other cities or region names via "Custom Input" mode.

## 限制 Limitations

- 依賴第三方 RSS 是否可用；若無法連線會顯示錯誤
- 需要有效的 OpenAI API Key 才能使用 AI 總結功能
- 位置偵測需要瀏覽器權限，某些瀏覽器可能不支援
- 未設計登入或個人化歷史紀錄，僅為互動展示
- AI 總結基於新聞標題，而非完整文章內容
- 位置偵測使用免費的 Nominatim API，可能有速率限制

- Depends on third-party RSS availability; will show error if connection fails
- Requires valid OpenAI API Key to use AI summarization
- Location detection requires browser permissions; some browsers may not support it
- No login or personalized history, interactive demo only
- AI summaries are based on news headlines, not full article content
- Location detection uses free Nominatim API which may have rate limits

## 費用說明 Cost Notes

使用 OpenAI API 會產生費用。本專案使用 `gpt-4o-mini` 模型，每次請求約消耗：
- 輸入 tokens: ~200-300 tokens
- 輸出 tokens: ~200-500 tokens
- 預估成本: 每次請求約 $0.0001-0.0003 USD

Using OpenAI API incurs costs. This project uses `gpt-4o-mini` model, each request consumes approximately:
- Input tokens: ~200-300 tokens
- Output tokens: ~200-500 tokens
- Estimated cost: ~$0.0001-0.0003 USD per request

## 授權 License

本專案為示範用途，可自由使用和修改。

This project is for demonstration purposes and can be freely used and modified.