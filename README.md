# Daily Digest – AI News Summarizer / AI 新聞每日摘要工具

English | 中文

## 🌟 Overview｜概述
Daily Digest is a lightweight AI-powered news dashboard.
Now powered by **Groq open-source LLMs**, providing **fast & free** news summarization.

Daily Digest 是一款輕量 AI 新聞摘要工具，
現在支援 **Groq 開源模型（免費又高速）**，可自動生成新聞重點整理與雙語摘要。

支援：
- **Google News**（主題 + 城市/地區）
- **RSS 新聞來源選單**（BBC / CNN / NYT / Guardian 等）
- **AI 雙語摘要**（英文 ➜ 中文）

## ✨ Features｜功能特色
### 🔹 Multiple News Sources 多來源
- 預設使用 Google News 搜尋
- 可選擇特定 RSS（BBC、CNN、NYT、Guardian…）

### 🔹 AI Summaries with Groq（English + Chinese）
AI 會輸出：
- "Today’s Key Points"（英文）
- 中文要點摘要（自動翻譯）

### 🔹 Modern UI 現代化介面
- Dark Mode（深色模式）
- Loading Skeleton（載入骨架）
- 地理位置自動偵測，可細到「城市」層級（例如 Chicago, United States）

## 🚀 Quick Start｜快速開始
### Install & Run
```bash
pip install -r requirements.txt
python backend/app.py
```

Visit in browser:
```
http://localhost:5000
```

## ⚙️ Environment Variables｜環境變數（Groq 推薦設定）
本專案支援 **Groq / OpenAI / Ollama**，
但最推薦 & 完全免費的方案是 **Groq**。

### ▶ 使用 Groq（免費高速）
在 `.env` 或 Railway / Render 設：
```
AI_PROVIDER=groq
GROQ_API_KEY=你的_groq_key
GROQ_MODEL=llama-3.1-8b-instant
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

### ▶ 如果你想切回 OpenAI
```
AI_PROVIDER=openai
OPENAI_API_KEY=你的key
OPENAI_MODEL=gpt-4o-mini
```

### ▶ 如果你在本機想用 Ollama
```
AI_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2:3b
```

## 📁 Project Structure｜專案結構
```
backend/app.py        # Groq / OpenAI / Ollama 自動切換
public/index.html     # RSS 選單 + 城市級地點偵測 + Dark Mode
requirements.txt
Dockerfile
```

## 📜 License｜授權
Free for personal and non-commercial use.
可自由使用與修改（個人與非商業用途）。
