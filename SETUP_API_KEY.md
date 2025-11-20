# API Key 設定指南 | API Key Setup Guide

## 中文說明

### 步驟 1: 複製配置檔案

```bash
cp config.env.example .env
```

### 步驟 2: 編輯 .env 檔案

打開 `.env` 檔案，你會看到：

```
OPENAI_API_KEY=your-openai-api-key-here
```

將 `your-openai-api-key-here` 替換為你的實際 OpenAI API Key。

### 步驟 3: 獲取 OpenAI API Key

1. 前往 https://platform.openai.com/api-keys
2. 登入你的 OpenAI 帳號
3. 點擊 "Create new secret key"
4. 複製生成的 API Key
5. 將 API Key 貼到 `.env` 檔案中

### 步驟 4: 完成

儲存 `.env` 檔案後，重新啟動應用程式即可。

---

## English Instructions

### Step 1: Copy Configuration File

```bash
cp config.env.example .env
```

### Step 2: Edit .env File

Open the `.env` file, you'll see:

```
OPENAI_API_KEY=your-openai-api-key-here
```

Replace `your-openai-api-key-here` with your actual OpenAI API Key.

### Step 3: Get OpenAI API Key

1. Go to https://platform.openai.com/api-keys
2. Log in to your OpenAI account
3. Click "Create new secret key"
4. Copy the generated API Key
5. Paste the API Key into the `.env` file

### Step 4: Done

After saving the `.env` file, restart the application.

---

## 注意事項 | Notes

- **不要**將 `.env` 檔案提交到 Git（已在 .gitignore 中）
- 如果未設定 API Key，應用程式仍可運作，但不會生成 AI 摘要
- API Key 會產生費用，請注意使用量

- **Do NOT** commit the `.env` file to Git (already in .gitignore)
- If API Key is not set, the app will still work but won't generate AI summaries
- API Key usage incurs costs, please monitor your usage
