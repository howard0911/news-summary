# 部署指南 | Deployment Guide

本指南將幫助您將 Daily Digest 部署到生產環境，讓其他人可以使用。

This guide will help you deploy Daily Digest to production so others can use it.

## 🚀 部署選項 | Deployment Options

### 選項 1: Railway（推薦 - 最簡單）Option 1: Railway (Recommended - Easiest)

Railway 提供免費額度，部署簡單：

1. **註冊 Railway 帳號**
   - 前往 https://railway.app
   - 使用 GitHub 登入

2. **連接 GitHub 倉庫**
   - 將代碼推送到 GitHub
   - 在 Railway 中選擇 "New Project" > "Deploy from GitHub repo"
   - 選擇您的倉庫

3. **設置環境變數**
   - 在 Railway 項目設置中添加：
     ```
     OPENAI_API_KEY=your-api-key-here
     FLASK_PORT=5000
     FLASK_DEBUG=False
     ```

4. **自動部署**
   - Railway 會自動檢測並部署
   - 會自動分配一個公開 URL

---

### 選項 2: Render（免費方案）Option 2: Render (Free Tier)

1. **註冊 Render 帳號**
   - 前往 https://render.com
   - 使用 GitHub 登入

2. **創建 Web Service**
   - 選擇 "New" > "Web Service"
   - 連接 GitHub 倉庫

3. **設置構建和啟動命令**
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn -w 4 -b 0.0.0.0:$PORT backend.app:app`

4. **設置環境變數**
   ```
   OPENAI_API_KEY=your-api-key-here
   FLASK_DEBUG=False
   ```

---

### 選項 3: Heroku Option 3: Heroku

1. **安裝 Heroku CLI**
   ```bash
   # macOS
   brew tap heroku/brew && brew install heroku
   
   # 或訪問 https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **登入 Heroku**
   ```bash
   heroku login
   ```

3. **創建應用**
   ```bash
   heroku create your-app-name
   ```

4. **設置環境變數**
   ```bash
   heroku config:set OPENAI_API_KEY=your-api-key-here
   heroku config:set FLASK_DEBUG=False
   ```

5. **部署**
   ```bash
   git push heroku main
   ```

---

### 選項 4: VPS/雲服務器（AWS, DigitalOcean, Linode等）Option 4: VPS/Cloud Server

#### 步驟 1: 準備服務器

```bash
# 更新系統
sudo apt update && sudo apt upgrade -y

# 安裝 Python 和 pip
sudo apt install python3 python3-pip python3-venv nginx -y
```

#### 步驟 2: 上傳代碼

```bash
# 使用 git clone 或 scp 上傳代碼
git clone your-repo-url
cd new_summary
```

#### 步驟 3: 設置環境

```bash
# 創建虛擬環境
python3 -m venv .venv
source .venv/bin/activate

# 安裝依賴
pip install -r requirements.txt
pip install gunicorn

# 創建 .env 文件
nano .env
# 添加：
# OPENAI_API_KEY=your-api-key-here
# FLASK_DEBUG=False
```

#### 步驟 4: 使用 Gunicorn 運行

```bash
# 測試運行
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app

# 使用 systemd 創建服務（推薦）
sudo nano /etc/systemd/system/daily-digest.service
```

添加以下內容：

```ini
[Unit]
Description=Daily Digest Web Application
After=network.target

[Service]
User=your-username
WorkingDirectory=/path/to/new_summary
Environment="PATH=/path/to/new_summary/.venv/bin"
ExecStart=/path/to/new_summary/.venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app

[Install]
WantedBy=multi-user.target
```

啟動服務：

```bash
sudo systemctl daemon-reload
sudo systemctl enable daily-digest
sudo systemctl start daily-digest
sudo systemctl status daily-digest
```

#### 步驟 5: 配置 Nginx 反向代理

```bash
sudo nano /etc/nginx/sites-available/daily-digest
```

添加：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

啟用配置：

```bash
sudo ln -s /etc/nginx/sites-available/daily-digest /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 步驟 6: 設置 SSL（使用 Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 📋 部署前檢查清單 | Pre-Deployment Checklist

- [ ] **環境變數設置**
  - [ ] `OPENAI_API_KEY` 已設置
  - [ ] `FLASK_DEBUG=False`（生產環境）
  - [ ] `FLASK_PORT` 已設置（如果需要）

- [ ] **安全檢查**
  - [ ] `.env` 文件已添加到 `.gitignore`
  - [ ] API key 不會被提交到 Git
  - [ ] 使用 HTTPS（生產環境）

- [ ] **依賴檢查**
  - [ ] `requirements.txt` 包含所有依賴
  - [ ] 已測試本地運行

- [ ] **功能測試**
  - [ ] 新聞獲取功能正常
  - [ ] AI 摘要功能正常（如果配置了 API key）
  - [ ] 位置偵測功能正常
  - [ ] 中英文切換正常

---

## 🔒 安全建議 | Security Recommendations

1. **保護 API Key**
   - 永遠不要將 API key 提交到 Git
   - 使用環境變數或密鑰管理服務
   - 定期輪換 API key

2. **使用 HTTPS**
   - 生產環境必須使用 HTTPS
   - 使用 Let's Encrypt 免費 SSL 證書

3. **限制訪問（可選）**
   - 如果需要，可以添加身份驗證
   - 使用防火牆限制 IP 訪問

4. **監控和日誌**
   - 設置日誌記錄
   - 監控 API 使用量
   - 設置錯誤告警

---

## 📊 監控和維護 | Monitoring & Maintenance

### 查看日誌

**Railway/Render:**
- 在平台的控制台查看日誌

**VPS:**
```bash
# 查看應用日誌
sudo journalctl -u daily-digest -f

# 查看 Nginx 日誌
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 更新應用

```bash
# 拉取最新代碼
git pull

# 重啟服務（VPS）
sudo systemctl restart daily-digest

# 或重新部署（Railway/Render）
# 平台會自動檢測並重新部署
```

---

## 💰 成本估算 | Cost Estimation

### 免費方案
- **Railway**: 每月 $5 免費額度（足夠小規模使用）
- **Render**: 免費方案（有休眠限制）
- **Heroku**: 不再提供免費方案

### 付費方案
- **VPS**: $5-10/月（DigitalOcean, Linode）
- **OpenAI API**: 按使用量計費（約 $0.0001-0.0003/請求）

---

## 🆘 常見問題 | FAQ

**Q: 部署後無法訪問？**
- 檢查防火牆設置
- 確認端口是否正確
- 檢查環境變數是否設置

**Q: AI 功能不工作？**
- 檢查 API key 是否正確設置
- 查看日誌確認錯誤訊息
- 測試 `/api/test-openai` 端點

**Q: 如何更新應用？**
- 推送新代碼到 Git
- 平台會自動重新部署
- 或手動重啟服務

---

## 📞 需要幫助？| Need Help?

如果遇到問題，請檢查：
1. 服務器日誌
2. 瀏覽器控制台錯誤
3. API 測試端點：`/api/health` 和 `/api/test-openai`
