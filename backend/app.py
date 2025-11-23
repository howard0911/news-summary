import os
import re
import json
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote_plus

import feedparser
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request, send_from_directory
from openai import OpenAI

app = Flask(__name__, static_folder="../public", static_url_path="")

# ------------------------------
# Load environment variables
# ------------------------------
try:
    from dotenv import load_dotenv
    env_path = Path(__file__).parent.parent / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        print("✅ Loaded environment variables from .env file")
    else:
        config_example = Path(__file__).parent.parent / "config.env.example"
        if config_example.exists():
            load_dotenv(config_example)
            print("⚠️ Using config.env.example (please create .env file)")
except ImportError:
    print("⚠️ python-dotenv not installed, using system environment only")

# ------------------------------
# Config: Ollama and OpenAI
# ------------------------------
# Ollama local URL and default model (you confirmed these)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/v1")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

# OpenAI config (optional, used if Ollama not available)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")  # optional (e.g., proxy)

# Behavior:
# - If local Ollama responds, use it.
# - Otherwise fall back to OpenAI (if OPENAI_API_KEY available).
# - You may force provider via ENV: AI_PROVIDER=ollama|openai|auto
AI_PROVIDER = os.getenv("AI_PROVIDER", "auto").lower()


def is_ollama_available(timeout: float = 1.0) -> bool:
    """Check whether Ollama local server appears to be running."""
    try:
        # Query models endpoint (works for many Ollama setups)
        resp = requests.get(f"{OLLAMA_URL}/models", timeout=timeout)
        if resp.status_code == 200:
            return True
        # Some Ollama setups expose /v1 or root; try root quickly
        resp2 = requests.get(OLLAMA_URL, timeout=timeout)
        return resp2.status_code == 200
    except Exception:
        return False


def get_openai_client():
    """Lazy-create an OpenAI client if API key present."""
    if not OPENAI_API_KEY:
        return None
    try:
        # Initialize OpenAI client with optional base_url
        client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        return client
    except Exception as e:
        print("Error initializing OpenAI client:", e)
        return None


def get_llm_provider() -> Dict:
    """
    Decide which provider to use and return a descriptor dict:
    {
        'provider': 'ollama'|'openai'|'none',
        ...provider-specific fields...
    }
    """
    # If forced by env
    if AI_PROVIDER == "ollama":
        if is_ollama_available():
            return {"provider": "ollama", "base_url": OLLAMA_URL, "model": OLLAMA_MODEL}
        else:
            return {"provider": "none", "reason": "OLLAMA_FORCED_but_unavailable"}

    if AI_PROVIDER == "openai":
        client = get_openai_client()
        if client:
            return {"provider": "openai", "client": client, "model": OLLAMA_MODEL}
        else:
            return {"provider": "none", "reason": "OPENAI_FORCED_but_no_api_key"}

    # Auto mode: prefer Ollama if available, else OpenAI if key present
    if is_ollama_available():
        return {"provider": "ollama", "base_url": OLLAMA_URL, "model": OLLAMA_MODEL}
    client = get_openai_client()
    if client:
        return {"provider": "openai", "client": client, "model": OLLAMA_MODEL}
    return {"provider": "none", "reason": "no_provider_available"}


# ------------------------------
# Unified LLM call helper
# ------------------------------
def _parse_ollama_response(resp_json: Dict) -> str:
    """
    Attempt to parse various Ollama response shapes.
    Common shapes:
    - {"choices":[{"message":{"content":"..."}}], ...}
    - {"message":{"content":"..."}}
    - {"choices":[{"content":"..."}]}
    """
    if not isinstance(resp_json, dict):
        return str(resp_json)
    # Try choices -> message -> content
    try:
        choices = resp_json.get("choices")
        if choices and isinstance(choices, list) and len(choices) > 0:
            first = choices[0]
            # nested message
            if isinstance(first, dict) and "message" in first and isinstance(first["message"], dict):
                return first["message"].get("content", "")
            # direct content
            if isinstance(first, dict) and "content" in first:
                return first.get("content", "")
        # fallback to top-level message.content
        if "message" in resp_json and isinstance(resp_json["message"], dict):
            return resp_json["message"].get("content", "")
    except Exception:
        pass
    # last resort: return json dump
    return json.dumps(resp_json)


def ask_llm(messages: List[Dict], max_tokens: int = 500, temperature: float = 0.7, timeout: float = 30.0) -> str:
    """
    messages: list of {"role":"system|user|assistant", "content": "..."}
    Returns: generated text (or error string starting with [Error])
    """
    provider = get_llm_provider()

    if provider["provider"] == "none":
        return "[Error] No LLM provider available: " + provider.get("reason", "")

    # ---------- Ollama ----------
    if provider["provider"] == "ollama":
        payload = {
            "model": provider["model"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        try:
            r = requests.post(f"{provider['base_url']}/chat/completions", json=payload, timeout=timeout)
            r.raise_for_status()
            resp_json = r.json()
            return _parse_ollama_response(resp_json)
        except Exception as e:
            # If Ollama fails, attempt fallback to OpenAI (if available)
            print("Ollama request failed:", e)
            client = get_openai_client()
            if client:
                try:
                    resp = client.chat.completions.create(
                        model=provider.get("model", "gpt-4o-mini"),
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                    return resp.choices[0].message.content
                except Exception as oe:
                    return f"[OpenAI Fallback Error] {oe}"
            return f"[Ollama Error] {e}"

    # ---------- OpenAI ----------
    if provider["provider"] == "openai":
        client: OpenAI = provider["client"]
        try:
            resp = client.chat.completions.create(
                model=provider.get("model", "gpt-4o-mini"),
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return resp.choices[0].message.content
        except Exception as e:
            print("OpenAI request failed:", e)
            # Try Ollama as fallback if available
            if is_ollama_available():
                try:
                    payload = {
                        "model": OLLAMA_MODEL,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": max_tokens,
                    }
                    r = requests.post(f"{OLLAMA_URL}/chat/completions", json=payload, timeout=timeout)
                    r.raise_for_status()
                    return _parse_ollama_response(r.json())
                except Exception as oe:
                    return f"[OpenAI Error] {e} | [Ollama Fallback Error] {oe}"
            return f"[OpenAI Error] {e}"

    return "[Error] Unknown provider flow"


# ------------------------------
# Region config and feed helpers
# ------------------------------
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

PRESET_RSS_FEEDS: Dict[str, Dict[str, str]] = {
    "bbc_world": {
        "label": "BBC News - World",
        "url": "http://feeds.bbci.co.uk/news/world/rss.xml",
    },
    "cnn_world": {
        "label": "CNN.com - World",
        "url": "http://rss.cnn.com/rss/edition_world.rss",
    },
    "cnbc_international": {
        "label": "CNBC International: Top News",
        "url": "https://www.cnbc.com/id/100727362/device/rss/rss.html",
    },
    "ndtv_world": {
        "label": "NDTV News - World",
        "url": "http://feeds.feedburner.com/ndtvnews-world-news",
    },
    "nyt_world": {
        "label": "NYT - World News",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
    },
    "google_top": {
        "label": "Google News - Top stories",
        "url": "https://news.google.com/rss",
    },
    "wapo_world": {
        "label": "Washington Post - World",
        "url": "http://feeds.washingtonpost.com/rss/world",
    },
    "reddit_worldnews": {
        "label": "Reddit - r/worldnews",
        "url": "https://www.reddit.com/r/worldnews/.rss",
    },
    "toi_world": {
        "label": "Times of India - World",
        "url": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms",
    },
    "guardian_world": {
        "label": "The Guardian - World news",
        "url": "https://www.theguardian.com/world/rss",
    },
    "yahoo_news": {
        "label": "Yahoo News - Latest",
        "url": "https://www.yahoo.com/news/rss",
    },
    "huffpost_world": {
        "label": "HuffPost - World News",
        "url": "https://www.huffpost.com/section/world-news/feed",
    },
    "nyt_top": {
        "label": "NYT - Top Stories",
        "url": "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
    },
    "fox_news": {
        "label": "FOX News - Latest",
        "url": "http://feeds.foxnews.com/foxnews/latest",
    },
    "wsj_world": {
        "label": "WSJ - World News",
        "url": "https://feeds.a.dj.com/rss/RSSWorldNews.xml",
    },
    "latimes_world": {
        "label": "LA Times - World & Nation",
        "url": "https://www.latimes.com/world-nation/rss2.0.xml",
    },
    "cnn_international": {
        "label": "CNN - International Edition",
        "url": "http://rss.cnn.com/rss/edition.rss",
    },
    "yahoo_mostviewed": {
        "label": "Yahoo News - Most viewed",
        "url": "https://news.yahoo.com/rss/mostviewed",
    },
    "cnbc_us": {
        "label": "CNBC - US Top News",
        "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    },
    "politico_playbook": {
        "label": "Politico - Playbook",
        "url": "https://rss.politico.com/playbook.xml",
    },
}

DEFAULT_REGION = REGION_CONFIG["us"]
MAX_NEWS_COUNT = 15


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/test-llm")
def test_llm():
    """
    Test the active LLM provider by running a tiny prompt.
    Response returns the provider decision and the LLM reply.
    """
    provider = get_llm_provider()
    test_prompt = [{"role": "user", "content": "Say: test"}]
    reply = ask_llm(test_prompt, max_tokens=10)
    return jsonify({"provider": provider.get("provider"), "reply": reply})


@app.get("/api/regions")
def get_regions():
    regions = []
    for key, config in REGION_CONFIG.items():
        regions.append({"code": key, "name": config.get("name", key.upper())})
    return jsonify({"regions": regions})



@app.get("/api/news")
def get_news():
    topic = request.args.get("topic", "").strip() or "trending"
    region_key = request.args.get("region", "us").lower()
    lang = request.args.get("lang", "en").lower()
    preset_id = (request.args.get("presetId") or "").strip()

    # validate region
    if region_key not in REGION_CONFIG:
        region_key = "us"
    region = REGION_CONFIG.get(region_key, DEFAULT_REGION)

    # decide feed url priority: preset -> google news
    feed_url = None
    if preset_id and preset_id in PRESET_RSS_FEEDS:
        feed_url = PRESET_RSS_FEEDS[preset_id]["url"]
    else:
        feed_url = build_google_news_feed(topic, region)

    entries = fetch_feed_entries(feed_url)

    if not entries:
        error_msg = "無法取得新聞，請稍後再試" if lang.startswith("zh") else "Failed to fetch news, please try again later"
        return jsonify({"items": [], "error": error_msg}), 502

    news_items = [serialize_entry(e) for e in entries[:MAX_NEWS_COUNT]]

    takeaway = None
    # generate takeaway using LLM (will auto-switch)
    try:
        if news_items:
            takeaway = generate_takeaway(news_items, lang)
    except Exception as e:
        print("LLM generate_takeaway error:", e)
        takeaway = None

    return jsonify({"items": news_items, "source": feed_url, "takeaway": takeaway})


    news_items = [serialize_entry(e) for e in entries[:MAX_NEWS_COUNT]]

    takeaway = None
    # generate takeaway using LLM (will auto-switch)
    try:
        if news_items:
            takeaway = generate_takeaway(news_items, lang)
    except Exception as e:
        print("LLM generate_takeaway error:", e)
        takeaway = None

    return jsonify({"items": news_items, "source": feed_url, "takeaway": takeaway})


    news_items = [serialize_entry(e) for e in entries[:MAX_NEWS_COUNT]]

    takeaway = None
    # generate takeaway using LLM (will auto-switch)
    try:
        if news_items:
            takeaway = generate_takeaway(news_items, lang)
    except Exception as e:
        print("LLM generate_takeaway error:", e)
        takeaway = None

    return jsonify({"items": news_items, "source": feed_url, "takeaway": takeaway})


def build_google_news_feed(topic: str, region: Dict[str, str]) -> str:
    encoded_topic = quote_plus(topic)
    return (
        "https://news.google.com/rss/search?q="
        f"{encoded_topic}+when:1d&hl={region['hl']}&gl={region['gl']}&ceid={region['ceid']}"
    )


def fetch_feed_entries(feed_url: str) -> List[feedparser.FeedParserDict]:
    parsed = feedparser.parse(feed_url)
    if parsed.bozo:
        return []
    entries = parsed.entries
    # sort by published time (most recent first)
    entries.sort(key=lambda x: (x.get("published_parsed") or (1970, 1, 1, 0, 0, 0, 0, 0, 0)), reverse=True)
    return entries


def serialize_entry(entry: feedparser.FeedParserDict) -> Dict[str, Optional[str]]:
    published = normalize_published(entry)
    return {"title": entry.get("title", "(無標題)"), "link": entry.get("link"), "published": published}


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


def generate_takeaway(news_items: List[Dict], lang: str = "zh") -> Optional[Dict[str, str]]:
    """Generate a short summary/takeaway using the configured LLM provider."""
    titles = [item["title"] for item in news_items[:10]]
    news_text = "\n".join([f"{i+1}. {t}" for i, t in enumerate(titles)])

    if lang.startswith("zh"):
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

    messages = [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}]

    out = ask_llm(messages, max_tokens=500, temperature=0.7)
    if out and not out.startswith("[Error]") and not out.startswith("[Ollama Error]") and not out.startswith("[OpenAI Error]"):
        # Try to parse sections
        if lang.startswith("zh"):
            things_to_watch = extract_section(out, "今天需要注意的事情")
            takeaway = extract_section(out, "Take Away")
        else:
            things_to_watch = extract_section(out, "Things to Watch Today")
            takeaway = extract_section(out, "Take Away")
        return {"things_to_watch": things_to_watch or out, "takeaway": takeaway or out}
    return {"things_to_watch": out, "takeaway": out}


def extract_section(text: str, section_name: str) -> Optional[str]:
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
    import socket

    host = os.getenv("FLASK_HOST", "0.0.0.0")
    default_port = int(os.getenv("FLASK_PORT", "5001"))
    debug = os.getenv("FLASK_DEBUG", "True").lower() == "true"

    def find_free_port(start_port):
        port = start_port
        max_attempts = 10
        for _ in range(max_attempts):
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(("", port))
                sock.close()
                return port
            except OSError:
                port += 1
        return start_port

    port = int(os.environ.get("PORT", 5000))
    print("Current PORT:", os.getenv("PORT"))
    app.run(host=host, port=port, debug=debug)