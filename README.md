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

---

## 📁 Project Structure

```
backend/app.py        # Groq / OpenAI / Ollama automatic provider
public/index.html     # RSS selector + geolocation + dark mode
requirements.txt
Dockerfile
```

---

## 📜 License

Free for personal and non‑commercial use.  
Feel free to modify and extend the project.

