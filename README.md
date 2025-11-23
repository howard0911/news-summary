# Daily Digest – AI News Summarizer / AI 新聞每日摘要工具

English | 中文

## 🌟 Overview 概述
Daily Digest is a lightweight AI-powered news dashboard.
You can follow global headlines using Google News (default) or choose specific RSS sources such as BBC, CNN, NYTimes, Guardian, and more.

Daily Digest 是一款輕量級的 AI 新聞摘要工具。  
你可以使用 Google News（預設）或選擇特定 RSS 來源（如 BBC、CNN、NYTimes）。

AI automatically produces bilingual summaries (English + Chinese).  
AI 會自動產生雙語摘要（英文 + 中文）。

## ✨ Features 功能特點
### 🔹 Multiple News Sources 多新聞來源
- Default: Google News by topic & region  
- Or pick an RSS source: BBC / CNN / NYT / Guardian / WSJ / Yahoo…

預設依主題＋地區抓取 Google News  
或直接選擇 RSS 來源（如 BBC、CNN、NYT…）

### 🔹 AI Summaries (English + Chinese)
AI produces:
- Today’s Key Points  
- Takeaways (English → 中文翻譯)

AI 會產生：
- 今日重點  
- 中英文摘要（自動翻譯）

### 🔹 Favorites 收藏組合
Store your frequently used combinations (Topic + Location + Source).  
Favorites are stored in your browser only.

可收藏常用組合（主題＋地區＋來源），存於瀏覽器。

### 🔹 Modern UI 現代化介面
- Dark Mode  
- Loading Skeleton  
- Simple Analytics

## 🚀 Quick Start 快速開始
```bash
pip install -r requirements.txt
python backend/app.py
```

Visit:  
http://localhost:5000

## ⚙️ Environment Variables 環境變數
AI_PROVIDER=openai  
OPENAI_API_KEY=your-key  
OPENAI_MODEL=gpt-4o-mini  

## 📁 Project Structure 專案結構
backend/app.py  
public/index.html  
requirements.txt  
Dockerfile  

## 📜 License 授權
Free to use & modify for personal projects.  
個人可自由使用、修改。
