# Daily Digest

一個可在本地運行的新聞摘要工具。使用者輸入感興趣的主題和位置後，系統會從 Google 新聞 RSS 擷取過去 24 小時內的多則熱門新聞，並使用 **本地 Ollama 模型或 OpenAI API（自動切換）** 生成智能總結與中英雙語重點。

A local news summarization tool. After entering topics of interest and location, the system fetches multiple trending news articles from the past 24 hours via Google News RSS, and uses **local Ollama models or OpenAI API (auto fallback)** to generate intelligent **bilingual (English + Traditional Chinese) summaries and key insights**.

---

## ✨ 主要功能 Features

- 🌐 **中英文雙語介面（英文優先）**  
  - 介面支援中英文切換，預設為英文。  
  - AI 產生的摘要也同時輸出 **英文 + 繁體中文**。

- 🌍 **多地區支援 + ISO-3166 自動偵測**  
  - 支援 20+ 個國家/地區（US, UK, Taiwan, Japan, Germany, etc.）。  
  - 使用者可以輸入文字位置（例如 `New York, USA`、`台北 台灣`、`東京 日本`），前端會嘗試解析並自動對應到後端定義的 **ISO-3166 國別代碼**。  
  - 從瀏覽器地理位置（HTML Geolocation + Nominatim）自動偵測國家，並映射到適合的 Google News region。  
  - 表單下方會顯示目前推斷的 `Region: Taiwan (TW)` 等提示。

- 📍 **位置自動偵測 + 手動輸入**  
  - 一鍵「📍 Detect My Location」，自動偵測所在國家 / 地區。  
  - 也可手動輸入城市 / 州 / 國家名稱。

- 📰 **多篇新聞 + Google News RSS**  
  - 一次獲取最多 **15 則**相關新聞。  
  - 預設使用 `topic + when:1d` 只抓近 24 小時新聞。  
  - 若自訂 `customUrl`，則直接抓取該 URL（RSS 或單篇文章）。

- 🔗 **Custom RSS / 單篇新聞網址都可用**  
  - 在「自訂 RSS / 新聞網址」欄位可以填：
    - RSS feed：`https://example.com/rss`  
    - 單篇新聞頁：`https://news-site.com/article/123`  
  - 後端會先用 RSS 解析，若不是 RSS 或沒有 entries，會自動 fallback 成「單篇新聞」模式（用 `<title>` + `<meta description>` 產生一篇新聞）。

- 🤖 **AI 智能總結（本地優先 + 雙語輸出）**  
  - 優先使用 **本地 Ollama 模型**（例如 `llama3.2:3b`，走 OpenAI 相容 API），若不可用則使用 OpenAI API。  
  - 後端統一透過 `ask_llm()` 對接 Ollama / OpenAI，前端不需要知道是哪一家。  
  - 每次請求會產生：
    - **英文版**：`Things to Watch Today` + `Take Away`  
    - **繁中版**：`今天需要注意的事情` + `Take Away`（翻譯自英文摘要）

- 🧠 **中文主題自動「翻成英文關鍵字」再查新聞**  
  - 若使用者輸入的 `topic` 含有中文（或其他 CJK），後端會：
    - 用 LLM 產生 1–2 個精簡的英文關鍵字（例如：`台股` → `taiwan stocks`）  
    - 實際查詢的 Google News query 會是：  
      `台股 OR taiwan stocks when:1d`  
  - 這樣就算使用者用中文輸入主題，仍然能透過英文關鍵字提高命中率。

- 🎨 **Gen Z 風格 UI + Dark Mode**  
  - 使用 Inter 字體 + 卡片式佈局。  
  - 支援 **Light / Dark Mode 切換**（右上角「🌙 / ☀️」）。  
  - 適合拿來 Demo / Side Project 展示。

- ⏳ **Loading Skeleton**  
  - 送出表單後，新聞列表區顯示 skeleton shimmer，提供更好的載入體驗。

- 📊 **News Analytics（新聞來源分析）**  
  - 自動統計目前結果中，新聞來源 domain（例如 `nytimes.com`, `bbc.com`）出現次數。  
  - 以簡單的 bar chart 顯示 Top 5 來源，作為「今天是誰在主導這個話題？」的 quick insight。

- 🚀 **Deployment-friendly**  
  - 提供：
    - `start.sh` / `start.bat` 本機啟動腳本  
    - `Dockerfile`（搭配 `gunicorn`）  
    - `Procfile`（適用於 Heroku/Railway/Render 類平台）  
  - 環境變數控制 AI Provider、Ollama / OpenAI、Flask 參數。

---

## 🧱 技術棧 Tech Stack

### Backend

- Flask  
- Feedparser（解析 Google News RSS）  
- BeautifulSoup（清理 HTML / 單篇新聞 fallback）  
- Requests（對 Ollama / 外部 API 發 request）  
- `openai` Python SDK（對 OpenAI 及 OpenAI 相容 API）  
- `python-dotenv`（本機讀取 `.env`）

### Frontend

- 原生 HTML / CSS / JavaScript（單頁）  
- 雙語 UI（英文 / 繁體中文）  
- Dark Mode + Skeleton Loader + 簡易 bar chart analytics  
- HTML Geolocation + Nominatim 反查國家

---

## ⚙️ 環境需求 Requirements

- Python 3.10+（建議 3.11，專案預設為 3.11）  
- 可以連線到 Google News RSS & Nominatim API 的網路  
- **選用 Optional：**
  - 本地安裝並啟動 Ollama（推薦，支援離線 / 本地摘要）
  - 有效的 OpenAI API Key（雲端模式或作為 Ollama fallback）

---

## 🔑 環境變數設定 Environment Variables

以下為主要環境變數說明（可在 `.env` 或部署平台設定）：

```env
# AI provider: auto / ollama / openai
AI_PROVIDER=auto

# Ollama（本地 OpenAI 相容 API）
OLLAMA_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2:3b

# OpenAI（cloud 或 fallback）
OPENAI_API_KEY=sk-xxxxx   # 不要 hard-code 到程式裡，也不要 commit

# 若你使用的是自架 proxy / 相容 API（例如 LM Studio / DeepSeek proxy）
# 才需要設定 OPENAI_BASE_URL
# OPENAI_BASE_URL=https://api.openai.com/v1

# Flask
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=True
```

> 🚨 建議：不要把實際的 `OPENAI_API_KEY` 寫進 repo，請使用 `.env` 或部署平台（Railway / Render / Heroku）的環境變數機制。

---

## 🚀 快速開始 Quick Start（本機）

### 方法一：啟動腳本（推薦）

macOS / Linux:

```bash
./start.sh
```

Windows:

```cmd
start.bat
```

啟動腳本會：

1. 檢查 Python / venv  
2. 建立虛擬環境（如不存在）  
3. 安裝依賴 `pip install -r requirements.txt`  
4. 載入 `.env`、檢查 Ollama / OpenAI 可用性  
5. 啟動 Flask 伺服器（預設 `http://localhost:5000`）

### 方法二：手動啟動

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

export FLASK_PORT=5000  # or set in .env
python backend/app.py
```

瀏覽器開啟：

```text
http://localhost:5000
```

---

## 🌐 後端 API 介面 Backend API

### `GET /api/news`

Query 參數：

- `topic`（必填）– 主題（可以是中文 / 英文，如 `台股`, `AI`, `crypto`）  
- `region`（選填）– ISO-3166 國別代碼或名稱（例如 `us`, `tw`, `japan`）  
- `customUrl`（選填）– 自訂 RSS / 新聞 URL（可以是 RSS feed 或一般新聞頁）  
- `lang`（前端用）– `en` / `zh`，後端目前會直接產生雙語摘要，這個欄位主要是前端判斷顯示哪種語言。

回傳格式（成功）：

```jsonc
{
  "items": [
    {
      "title": "Some news title...",
      "link": "https://example.com/article",
      "summary": "Plain-text summary from RSS (or meta description if single article).",
      "published": "Mon, 20 Nov 2025 10:00:00 GMT",
      "source": "NYTimes"
    }
  ],
  "source": "https://news.google.com/rss/search?...",
  "takeaway": {
    "en": {
      "things_to_watch": "1. ...\n2. ...",
      "takeaway": "One-sentence key insight."
    },
    "zh": {
      "things_to_watch": "1. ...\n2. ...",
      "takeaway": "繁體中文關鍵總結。"
    }
  },
  "ai_error": null
}
```

若 AI 失敗（Ollama / OpenAI 都不可用或錯誤），`takeaway` 會是 `null`，並在 `ai_error` 中附上錯誤訊息，前端會顯示提示。

---

### `GET /api/regions`

回傳目前支援的地區列表，前端會拿來做 region 推斷：

```json
{
  "regions": [
    { "code": "us", "name": "United States" },
    { "code": "tw", "name": "Taiwan" },
    ...
  ]
}
```

---

## 🗺️ Region & Google News RSS 設計

後端內建一個 `REGIONS` 常數，使用 ISO-3166-ish code + Google News 所需的 `hl` / `gl` / `ceid`，例如：

```python
REGIONS = [
    {"code": "us", "name": "United States", "hl": "en-US", "gl": "US", "ceid": "US:en"},
    {"code": "tw", "name": "Taiwan", "hl": "zh-TW", "gl": "TW", "ceid": "TW:zh-Hant"},
    {"code": "jp", "name": "Japan", "hl": "ja-JP", "gl": "JP", "ceid": "JP:ja"},
    ...
]
```

Google News RSS URL 會長這樣：

```text
https://news.google.com/rss/search?q=<topic%20when:1d>&hl=<hl>&gl=<gl>&ceid=<ceid>
```

- `topic` 來自前端 input（若含中文，會經過 LLM 擴展）  
- 自動在 query 加上 `when:1d` 只抓近 24 小時的新聞  
- `hl` / `gl` / `ceid` 依地區變換（語系 + 國家）

---

## 🧠 AI Summarization 流程

1. 後端收集前 10 則新聞標題，組成一個大 prompt。  
2. 呼叫 `ask_llm(messages)`：
   - 若 `AI_PROVIDER=ollama` → 只呼叫 Ollama  
   - 若 `AI_PROVIDER=openai` → 只呼叫 OpenAI  
   - 若 `AI_PROVIDER=auto` → **先呼叫 Ollama，失敗再用 OpenAI**  
3. LLM 會依固定格式輸出：

   ```text
   【Things to Watch Today】
   1. ...
   2. ...
   3. ...

   【Take Away】
   ...
   ```

4. 後端用 `extract_section()` 擷取 `Things to Watch Today` / `Take Away` 文字。  
5. 再將英文摘要丟給 LLM，請它翻譯成繁體中文，同樣使用固定格式。  
6. 最後回傳：

   ```json
   {
     "en": {...},
     "zh": {...}
   }
   ```

---

## 🐳 Docker & 部署 Deploy

### Dockerfile（摘要）

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000
ENV FLASK_DEBUG=False

CMD ["sh", "-c", "gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} backend.app:app"]
```

### 使用本機 Ollama（方案 A：host network）

Mac / Linux 上：

```bash
docker build -t daily-digest .

docker run --rm -it \
  --network host \
  -e AI_PROVIDER=auto \
  -e OLLAMA_URL=http://localhost:11434/v1 \
  -e OLLAMA_MODEL=llama3.2:3b \
  -e OPENAI_API_KEY=sk-xxxxx \
  daily-digest
```

- `--network host` 讓容器內的 `http://localhost:11434` 其實指向 **Host 的 Ollama**。  
- Flask 預設跑在 `5000`，直接開 `http://localhost:5000` 即可。

> 若在雲端平台（Railway / Render / Heroku 等），通常無法直接跑 Ollama，建議改為：
> `AI_PROVIDER=openai`，並只使用 OpenAI 模型。

---

## 🔚 限制 Limitations

- 依賴 Google News RSS 可用性。  
- 需要 Ollama 或 OpenAI API 才能使用 AI 摘要。  
- 地理位置偵測需瀏覽器給權限。  
- 摘要目前只基於「標題」生成（可延伸到 description / content）。  
- 分析圖表僅做簡單 domain 次數統計，不是完整的媒體偏好分析。  
- 若自訂 URL 指向的網站擋爬蟲或需要登入，fallback 單篇新聞解析可能會失敗（此時仍會顯示「沒有新聞」）。

---

## 📄 License

本專案可自由使用與修改。  
This project is free to use and modify.
