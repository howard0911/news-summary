# Daily Digest – AI News Summarizer (Groq Edition)

Daily Digest is a lightweight, AI‑powered news dashboard that generates concise daily summaries using fast and free **Groq LLMs**.  
It aggregates global news from **Google News** or selected **RSS sources** (BBC, CNN, NYT, Guardian, etc.) and produces bilingual summaries (English → Chinese optional).

---

## 🌟 Overview

Daily Digest helps you quickly understand the most important news of the day.  
It supports:

- Google News (topic + region/city input)
- RSS source selector  
- AI summaries using Groq models
- City‑level location detection  
- Dark mode UI  
- Email/password auth (SQLite)
- Settings + saved preferences + notifications pages
- Fast loading with skeleton screens  

This version is optimized for **Groq** as a free and high‑performance AI backend.

---

## ✨ Features

### 🔹 Multiple News Sources
- Default: Google News by topic + location  
- Optional: Choose specific RSS feeds (BBC, CNN, NYT, Guardian, WSJ, etc.)

### 🔹 AI‑Generated Summaries (via Groq)
- “Today’s Key Points”  
- English summary + auto‑translated Chinese summary  
- Powered by Groq’s open‑source LLMs (fast, free)

### 🔹 Modern UI
- Clean responsive layout  
- Dark mode  
- Loading skeleton  
- City‑level geolocation detection (e.g., “Chicago, United States”)
- Account menu with settings, notifications, and saved preferences
- Saved preferences history (multi‑entry, deletable, with timestamps)
- Notification settings for daily digest time
- Preferences saved from Home appear in Saved Preferences history
- Backend scheduler generates in‑app notifications on schedule

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the backend
```bash
python backend/app.py
```

### 3. Open in browser
```
http://localhost:5000
```

If port 5000 is in use, run:
```bash
PORT=5001 python backend/app.py
```

---

## ⚙️ Environment Variables (recommended Groq setup)

This project supports **Groq / OpenAI / Ollama**, but Groq is recommended for free usage.

### ▶ Use Groq (recommended & free)
Add to `.env` or Railway / Render environment variables:

```
AI_PROVIDER=groq
GROQ_API_KEY=your_groq_key
GROQ_MODEL=llama-3.1-8b-instant
GROQ_BASE_URL=https://api.groq.com/openai/v1
```

### ▶ Switch to OpenAI (optional)
```
AI_PROVIDER=openai
OPENAI_API_KEY=your_openai_key
OPENAI_MODEL=gpt-4o-mini
```

### ▶ Use local Ollama (optional)
```
AI_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434/v1
OLLAMA_MODEL=llama3.2:3b
```

### ▶ App settings (optional)
```
SECRET_KEY=your_secret_key
DB_PATH=backend/app.db
```

---

## 📁 Project Structure

```
backend/app.py        # Groq / OpenAI / Ollama automatic provider
backend/app.db        # SQLite user data (auto-created)
public/index.html     # Main UI + auth entry
public/account.html   # Settings (account + notification settings)
public/preferences.html # Saved preferences history
public/notifications.html # Notifications feed
requirements.txt
Dockerfile
```

---

## 🔐 Auth & Preferences API

- `POST /api/auth/signup` (email + password)
- `POST /api/auth/login`
- `GET /api/me`
- `POST /api/auth/change-password`
- `POST /api/auth/update-profile`
- `GET /api/preferences`
- `PUT /api/preferences`
- `GET /api/saved-preferences`
- `POST /api/saved-preferences`
- `DELETE /api/saved-preferences/:id`
- `GET /api/notifications`
- `POST /api/notifications/:id/read`
- `DELETE /api/notifications/:id`
- `GET /api/notification-settings`
- `PUT /api/notification-settings`

---

## 📜 License

Free for personal and non‑commercial use.  
Feel free to modify and extend the project.
