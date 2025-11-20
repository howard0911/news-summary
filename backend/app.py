import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote_plus

import feedparser
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request, send_from_directory
from openai import OpenAI

app = Flask(__name__, static_folder="../public", static_url_path="")

# 嘗試載入 .env 檔案
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print(f"✅ Loaded environment variables from .env file")
    else:
        # 如果 .env 不存在，嘗試從 config.env.example 載入（僅用於開發）
        config_example = Path(__file__).parent.parent / "config.env.example"
        if config_example.exists():
            load_dotenv(config_example)
            print(f"⚠️  Using config.env.example (please create .env file)")
except ImportError:
    print("⚠️  python-dotenv not installed, using environment variables only")

# OpenAI API 設定
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = None

def get_openai_client():
    """延遲初始化 OpenAI 客戶端，避免啟動時錯誤"""
    global client
    if client is not None:
        return client
    
    # 重新讀取環境變數（以防 .env 文件在運行時更新）
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        try:
            from dotenv import load_dotenv
            load_dotenv(env_path, override=True)
            api_key = os.getenv("OPENAI_API_KEY")
        except:
            api_key = OPENAI_API_KEY
    else:
        api_key = OPENAI_API_KEY
    
    if api_key and api_key != "your-openai-api-key-here" and api_key.strip():
        try:
            client = OpenAI(api_key=api_key.strip())
            print("✅ OpenAI API client initialized")
            return client
        except Exception as e:
            print(f"⚠️  Error initializing OpenAI client: {e}")
            print(f"   Error type: {type(e).__name__}")
            print("   AI summarization will be disabled.")
            return None
    else:
        print("⚠️  Warning: OPENAI_API_KEY not set. AI summarization will be disabled.")
        print("   Please check your .env file and ensure OPENAI_API_KEY is set correctly.")
        return None

# 地區配置：支援國家和主要城市
REGION_CONFIG: Dict[str, Dict[str, str]] = {
    # 亞洲
    "tw": {"hl": "zh-TW", "gl": "TW", "ceid": "TW:zh-Hant", "name": "Taiwan"},
    "hk": {"hl": "zh-HK", "gl": "HK", "ceid": "HK:zh-Hant", "name": "Hong Kong"},
    "cn": {"hl": "zh-CN", "gl": "CN", "ceid": "CN:zh-Hans", "name": "China"},
    "jp": {"hl": "ja", "gl": "JP", "ceid": "JP:ja", "name": "Japan"},
    "kr": {"hl": "ko", "gl": "KR", "ceid": "KR:ko", "name": "South Korea"},
    "sg": {"hl": "en-SG", "gl": "SG", "ceid": "SG:en", "name": "Singapore"},
    "in": {"hl": "en-IN", "gl": "IN", "ceid": "IN:en", "name": "India"},
    # 美洲
    "us": {"hl": "en-US", "gl": "US", "ceid": "US:en", "name": "United States"},
    "ca": {"hl": "en-CA", "gl": "CA", "ceid": "CA:en", "name": "Canada"},
    "mx": {"hl": "es-MX", "gl": "MX", "ceid": "MX:es", "name": "Mexico"},
    "br": {"hl": "pt-BR", "gl": "BR", "ceid": "BR:pt", "name": "Brazil"},
    # 歐洲
    "uk": {"hl": "en-GB", "gl": "GB", "ceid": "GB:en", "name": "United Kingdom"},
    "de": {"hl": "de", "gl": "DE", "ceid": "DE:de", "name": "Germany"},
    "fr": {"hl": "fr", "gl": "FR", "ceid": "FR:fr", "name": "France"},
    "it": {"hl": "it", "gl": "IT", "ceid": "IT:it", "name": "Italy"},
    "es": {"hl": "es", "gl": "ES", "ceid": "ES:es", "name": "Spain"},
    "nl": {"hl": "nl", "gl": "NL", "ceid": "NL:nl", "name": "Netherlands"},
    # 大洋洲
    "au": {"hl": "en-AU", "gl": "AU", "ceid": "AU:en", "name": "Australia"},
    "nz": {"hl": "en-NZ", "gl": "NZ", "ceid": "NZ:en", "name": "New Zealand"},
}
DEFAULT_REGION = REGION_CONFIG["us"]  # 默認改為美國（英文優先）

# 新聞數量設定（獲取更多新聞）
MAX_NEWS_COUNT = 15


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/test-openai")
def test_openai():
    """測試 OpenAI API 是否可用"""
    openai_client = get_openai_client()
    if not openai_client:
        return jsonify({
            "status": "error",
            "message": "OpenAI client not initialized",
            "api_key_set": bool(OPENAI_API_KEY and OPENAI_API_KEY != "your-openai-api-key-here")
        }), 503
    
    try:
        # 簡單測試請求
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Say 'test'"}],
            max_tokens=5
        )
        return jsonify({
            "status": "success",
            "message": "OpenAI API is working",
            "response": response.choices[0].message.content
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
            "error_type": type(e).__name__
        }), 500


@app.get("/api/regions")
def get_regions():
    """獲取所有支援的地區列表"""
    regions = []
    for key, config in REGION_CONFIG.items():
        regions.append({
            "code": key,
            "name": config.get("name", key.upper())
        })
    return jsonify({"regions": regions})


@app.get("/api/news")
def get_news():
    topic = request.args.get("topic", "").strip() or "trending"
    region_key = request.args.get("region", "us").lower()  # 默認改為美國
    custom_url = request.args.get("customUrl", "").strip()
    lang = request.args.get("lang", "en").lower()  # 默認改為英文

    # 處理地址輸入：嘗試從地址中提取地區代碼
    # 如果 region_key 不在配置中，嘗試匹配或使用默認值
    if region_key not in REGION_CONFIG:
        # 嘗試從地址中提取國家/地區關鍵字
        region_key_lower = region_key.lower()
        for key, config in REGION_CONFIG.items():
            if key in region_key_lower or config.get("name", "").lower() in region_key_lower:
                region_key = key
                break
        else:
            # 如果找不到匹配，使用默認值
            region_key = "us"
    
    region = REGION_CONFIG.get(region_key, DEFAULT_REGION)

    feed_url = custom_url or build_google_news_feed(topic, region)
    entries = fetch_feed_entries(feed_url)

    if not entries:
        error_msg = "無法取得新聞，請稍後再試" if lang == "zh" else "Failed to fetch news, please try again later"
        return jsonify({"items": [], "error": error_msg}), 502

    # 獲取更多新聞（最多 MAX_NEWS_COUNT 篇）
    news_items = [serialize_entry(entry) for entry in entries[:MAX_NEWS_COUNT]]

    # 使用 OpenAI 生成總結
    takeaway = None
    openai_client = get_openai_client()
    if openai_client and news_items:
        try:
            takeaway = generate_takeaway(news_items, lang, openai_client)
        except Exception as e:
            print(f"OpenAI API 錯誤: {e}")
            takeaway = None

    return jsonify({
        "items": news_items,
        "source": feed_url,
        "takeaway": takeaway
    })


def build_google_news_feed(topic: str, region: Dict[str, str]) -> str:
    encoded_topic = quote_plus(topic)
    # 限制為24小時內的新聞，按熱度排序
    # 使用 when:1d 限制24小時內，Google News RSS 默認按熱度排序
    return (
        "https://news.google.com/rss/search?q="
        f"{encoded_topic}+when:1d&hl={region['hl']}&gl={region['gl']}&ceid={region['ceid']}"
    )


def fetch_feed_entries(feed_url: str) -> List[feedparser.FeedParserDict]:
    parsed = feedparser.parse(feed_url)
    if parsed.bozo:
        return []
    entries = parsed.entries
    
    # Google News RSS 已經按熱度排序，但我們可以根據發布時間進一步排序
    # 確保最新的熱門新聞在前
    entries.sort(key=lambda x: (
        x.get("published_parsed") or (1970, 1, 1, 0, 0, 0, 0, 0, 0)
    ), reverse=True)
    
    return entries


def serialize_entry(entry: feedparser.FeedParserDict) -> Dict[str, Optional[str]]:
    """序列化新聞條目，只保留標題和連結"""
    published = normalize_published(entry)

    return {
        "title": entry.get("title", "(無標題)"),
        "link": entry.get("link"),
        "published": published,
    }


def sanitize_html(raw_html: str) -> str:
    soup = BeautifulSoup(raw_html, "html.parser")
    text = soup.get_text(separator=" ")
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_published(entry: feedparser.FeedParserDict) -> Optional[str]:
    if "published_parsed" in entry and entry.published_parsed:
        dt = datetime(*entry.published_parsed[:6])
        return dt.strftime("%Y-%m-%d %H:%M")
    return entry.get("published")


def generate_takeaway(news_items: List[Dict], lang: str = "zh", openai_client=None) -> Optional[Dict[str, str]]:
    """使用 OpenAI API 生成新聞總結和 take away"""
    if not openai_client:
        openai_client = get_openai_client()
    if not openai_client:
        return None

    # 準備新聞標題列表
    titles = [item["title"] for item in news_items[:10]]  # 最多使用10篇標題
    news_text = "\n".join([f"{i+1}. {title}" for i, title in enumerate(titles)])

    # 根據語言選擇提示詞
    if lang == "zh":
        system_prompt = "你是一位專業的新聞分析師，擅長從多則新聞中提取關鍵洞察。"
        user_prompt = f"""以下是今天最新的新聞標題：

{news_text}

請根據這些新聞標題，為我總結：
1. 今天需要注意的事情（2-3個重點，每點簡潔明瞭）
2. 一個關鍵的 take away（一句話總結最重要的洞察）

請用繁體中文回答，格式如下：
【今天需要注意的事情】
1. ...
2. ...
3. ...

【Take Away】
..."""
    else:
        system_prompt = "You are a professional news analyst skilled at extracting key insights from multiple news articles."
        user_prompt = f"""Here are today's latest news headlines:

{news_text}

Please summarize based on these headlines:
1. Things to watch today (2-3 key points, concise and clear)
2. A key takeaway (one sentence summarizing the most important insight)

Please respond in English in the following format:
【Things to Watch Today】
1. ...
2. ...
3. ...

【Take Away】
..."""

    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o-mini",  # 使用較便宜的模型
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=500,
            timeout=30.0  # 添加超時設置
        )

        content = response.choices[0].message.content

        # 解析回應
        if lang == "zh":
            things_to_watch = extract_section(content, "今天需要注意的事情")
            takeaway = extract_section(content, "Take Away")
        else:
            things_to_watch = extract_section(content, "Things to Watch Today")
            takeaway = extract_section(content, "Take Away")

        return {
            "things_to_watch": things_to_watch or content,
            "takeaway": takeaway or "無法生成總結"
        }
    except Exception as e:
        print(f"OpenAI API 錯誤: {e}")
        return None


def extract_section(text: str, section_name: str) -> Optional[str]:
    """從文本中提取特定區塊的內容"""
    # 嘗試多種格式匹配
    patterns = [
        rf"【{section_name}】\s*(.*?)(?=【|$)",
        rf"\[{section_name}\]\s*(.*?)(?=\[|$)",
        rf"{section_name}:\s*(.*?)(?=\n\n|$)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1).strip()

    return None


if __name__ == "__main__":
    import os
    import socket
    # 從環境變數讀取配置，方便發布和測試
    host = os.getenv("FLASK_HOST", "0.0.0.0")
    default_port = int(os.getenv("FLASK_PORT", "5001"))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"
    
    # 檢查端口是否可用，如果被占用則嘗試下一個端口
    def find_free_port(start_port):
        port = start_port
        max_attempts = 10
        for _ in range(max_attempts):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(('', port))
                sock.close()
                return port
            except OSError:
                port += 1
        return start_port  # 如果都不可用，返回原始端口
        
    port = int(os.environ.get("PORT", 5000))
    port = find_free_port(default_port)
    if port != default_port:
        print(f"⚠️  Port {default_port} is in use, using port {port} instead")
    
    print(f"🚀 Starting Daily Digest Server...")
    print(f"📍 Host: {host}")
    print(f"🔌 Port: {port}")
    print(f"🐛 Debug: {debug}")
    print(f"🌐 Open: http://localhost:{port}")
    
    app.run(host="0.0.0.0", port=port, debug=debug)
