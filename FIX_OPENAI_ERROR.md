# 修復 OpenAI 庫錯誤

如果遇到 `TypeError: __init__() got an unexpected keyword argument 'proxies'` 錯誤，請按照以下步驟修復：

## 方法一：升級 OpenAI 庫（推薦）

```bash
# 激活虛擬環境（如果使用）
source .venv/bin/activate  # macOS/Linux
# 或
.venv\Scripts\activate  # Windows

# 升級 OpenAI 和相關依賴
pip install --upgrade openai httpx

# 或重新安裝所有依賴
pip install -r requirements.txt --upgrade
```

## 方法二：使用延遲初始化（已實現）

代碼已經更新為延遲初始化 OpenAI 客戶端，這樣即使庫版本有問題，也不會在啟動時崩潰。

如果 OpenAI 客戶端初始化失敗，系統會：
- 繼續運行（不會崩潰）
- 顯示警告訊息
- 禁用 AI 摘要功能
- 仍然可以顯示新聞列表

## 檢查是否修復

啟動服務器後，查看終端輸出：
- ✅ `OpenAI API client initialized` - 成功
- ⚠️ `Error initializing OpenAI client: ...` - 需要升級庫
- ⚠️ `OPENAI_API_KEY not set` - 需要設置 API key

## 如果問題仍然存在

1. **檢查 Python 版本**：建議使用 Python 3.10+
   ```bash
   python --version
   ```

2. **清理並重新安裝**：
   ```bash
   pip uninstall openai httpx
   pip install openai>=1.40.0 httpx>=0.27.0
   ```

3. **使用虛擬環境**（推薦）：
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   pip install -r requirements.txt
   ```
