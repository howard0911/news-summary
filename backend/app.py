import os
import re
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

import requests
import feedparser
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory
from openai import OpenAI

# ------------------------------
# Env & basic config
# ------------------------------

BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR.parent / "public"

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "auto").lower()
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/v1").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:3b")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", "5000"))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

# Regions (ISO-3166-ish) config used both by backend & frontend
REGIONS: List[Dict[str, str]] = [
    {"code": "us", "name": "United States", "hl": "en-US", "gl": "US", "ceid": "US:en"},
    {"code": "uk", "name": "United Kingdom", "hl": "en-GB", "gl": "GB", "ceid": "GB:en"},
    {"code": "ca", "name": "Canada", "hl": "en-CA", "gl": "CA", "ceid": "CA:en"},
    {"code": "au", "name": "Australia", "hl": "en-AU", "gl": "AU", "ceid": "AU:en"},
    {"code": "tw", "name": "Taiwan", "hl": "zh-TW", "gl": "TW", "ceid": "TW:zh-Hant"},
    {"code": "hk", "name": "Hong Kong", "hl": "zh-HK", "gl": "HK", "ceid": "HK:zh-Hant"},
    {"code": "jp", "name": "Japan", "hl": "ja-JP", "gl": "JP", "ceid": "JP:ja"},
    {"code": "kr", "name": "South Korea", "hl": "ko-KR", "gl": "KR", "ceid": "KR:ko"},
    {"code": "sg", "name": "Singapore", "hl": "en-SG", "gl": "SG", "ceid": "SG:en"},
    {"code": "in", "name": "India", "hl": "en-IN", "gl": "IN", "ceid": "IN:en"},
    {"code": "de", "name": "Germany", "hl": "de-DE", "gl": "DE", "ceid": "DE:de"},
    {"code": "fr", "name": "France", "hl": "fr-FR", "gl": "FR", "ceid": "FR:fr"},
    {"code": "es", "name": "Spain", "hl": "es-ES", "gl": "ES", "ceid": "ES:es"},
    {"code": "it", "name": "Italy", "hl": "it-IT", "gl": "IT", "ceid": "IT:it"},
    {"code": "br", "name": "Brazil", "hl": "pt-BR", "gl": "BR", "ceid": "BR:pt"},
    {"code": "mx", "name": "Mexico", "hl": "es-MX", "gl": "MX", "ceid": "MX:es"},
    {"code": "id", "name": "Indonesia", "hl": "id-ID", "gl": "ID", "ceid": "ID:id"},
    {"code": "th", "name": "Thailand", "hl": "th-TH", "gl": "TH", "ceid": "TH:th"},
    {"code": "ph", "name": "Philippines", "hl": "en-PH", "gl": "PH", "ceid": "PH:en"},
    {"code": "my", "name": "Malaysia", "hl": "en-MY", "gl": "MY", "ceid": "MY:en"},
]

DEFAULT_REGION = REGIONS[0]  # US

app = Flask(__name__, static_folder=str(PUBLIC_DIR), static_url_path="")

# ------------------------------
# Helpers
# ------------------------------


def find_region(region: Optional[str]) -> Dict[str, str]:
    """Find region config by ISO code or fuzzy name."""
    if not region:
        return DEFAULT_REGION
    key = region.strip().lower()
    # direct code
    for r in REGIONS:
        if r["code"].lower() == key:
            return r
    # fuzzy name
    for r in REGIONS:
        if key in r["name"].lower():
            return r
    # special mapping
    if key in {"gb", "england"}:
        return next((r for r in REGIONS if r["code"] == "uk"), DEFAULT_REGION)
    return DEFAULT_REGION


def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""
    soup = BeautifulSoup(raw_html, "html.parser")
    return soup.get_text(" ", strip=True)


def is_ollama_available(timeout: float = 0.5) -> bool:
    """Quick check if Ollama endpoint looks alive."""
    if not OLLAMA_URL:
        return False
    try:
        resp = requests.get(f"{OLLAMA_URL}/models", timeout=timeout)
        return resp.status_code == 200
    except Exception:
        return False


def get_openai_client() -> Optional[OpenAI]:
    """Create OpenAI client if API key exists."""
    if not OPENAI_API_KEY:
        return None
    try:
        kwargs: Dict[str, str] = {"api_key": OPENAI_API_KEY}
        if OPENAI_BASE_URL:
            kwargs["base_url"] = OPENAI_BASE_URL
        return OpenAI(**kwargs)
    except Exception as e:
        print("Error initializing OpenAI client:", e)
        return None


def _parse_ollama_response(resp_json: Dict) -> str:
    """
    Handle OpenAI-compatible Ollama responses, e.g.:
    - {"choices":[{"message":{"content":"..."}}]}
    """
    if not isinstance(resp_json, dict):
        return str(resp_json)
    try:
        choices = resp_json.get("choices")
        if choices and isinstance(choices, list):
            first = choices[0]
            if isinstance(first, dict):
                if "message" in first and isinstance(first["message"], dict):
                    content = first["message"].get("content")
                    if content:
                        return str(content)
                if "content" in first:
                    return str(first["content"])
    except Exception:
        pass
    # fallback try message.content
    message = resp_json.get("message")
    if isinstance(message, dict) and message.get("content"):
        return str(message["content"])
    return json.dumps(resp_json)


def is_llm_error(text: Optional[str]) -> bool:
    if not text:
        return True
    text = text.strip()
    if not text:
        return True
    return text.startswith("[Error]") or text.startswith("[Ollama Error]") or text.startswith("[OpenAI Error]")


def ask_llm(
    messages: List[Dict[str, str]],
    max_tokens: int = 512,
    temperature: float = 0.7,
    timeout: float = 20.0,
) -> str:
    """
    Unified LLM caller:
    - If AI_PROVIDER=ollama → only Ollama
    - If AI_PROVIDER=openai → only OpenAI
    - If AI_PROVIDER=auto → try Ollama, then OpenAI
    """
    provider = AI_PROVIDER

    def call_ollama() -> str:
        if not is_ollama_available():
            return "[Ollama Error] Ollama endpoint not available"
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
        except Exception as e:
            return f"[Ollama Error] {e}"

    def call_openai() -> str:
        client = get_openai_client()
        if not client:
            return "[OpenAI Error] OpenAI client not available"
        try:
            resp = client.chat.completions.create(
                model=OLLAMA_MODEL,  # 可視需要改成真正的 OpenAI model 名稱
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            choice = resp.choices[0]
            if choice.message and choice.message.content:
                return str(choice.message.content)
            return "[OpenAI Error] Empty completion"
        except Exception as e:
            return f"[OpenAI Error] {e}"

    # Provider routing
    if provider == "ollama":
        return call_ollama()
    if provider == "openai":
        return call_openai()

    # auto
    out = call_ollama()
    if not is_llm_error(out):
        return out
    # try openai
    out2 = call_openai()
    if not is_llm_error(out2):
        return out2
    # both failed
    return f"[Error] No provider responded successfully. Ollama={out} | OpenAI={out2}"


SECTION_PATTERN_CACHE: Dict[str, re.Pattern] = {}


def extract_section(text: str, title: str) -> Optional[str]:
    """
    Extract content between a header like:
    【Title】
    ...
    next header or end
    """
    if not text:
        return None
    key = title.lower()
    if key not in SECTION_PATTERN_CACHE:
        pattern = re.compile(
            rf"【\s*{re.escape(title)}\s*】(.*?)(?=【|$)",
            re.IGNORECASE | re.DOTALL,
        )
        SECTION_PATTERN_CACHE[key] = pattern
    m = SECTION_PATTERN_CACHE[key].search(text)
    if not m:
        return None
    return m.group(1).strip()


def contains_cjk(text: str) -> bool:
    """Return True if the string contains CJK characters (e.g., Chinese)."""
    if not text:
        return False
    return bool(re.search(r"[\u4e00-\u9fff]", text))


def expand_topic_with_translation(topic: str, region_code: Optional[str] = None) -> str:
    """If topic contains CJK, ask LLM for English keywords and build a combined query."""
    topic = (topic or "").strip()
    if not topic:
        return "trending"

    # If no CJK, just return original topic
    if not contains_cjk(topic):
        return topic

    region_cfg = find_region(region_code) if region_code else DEFAULT_REGION
    region_name = region_cfg["name"]

    system_prompt = (
        "You are a bilingual assistant that helps map non-English news topics "
        "to effective English search keywords for Google News."
    )
    user_prompt = f"""The user entered a news topic (possibly in Chinese or another language):

"{topic}"

This topic is for the region: {region_name}.

Please propose 1-2 very short English search keywords that would work well for a Google News query about this topic.
Return ONLY the keywords as a comma-separated list, without any explanations, numbering, or extra text.
Example: elections, us politics"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ]

    out = ask_llm(messages, max_tokens=64, temperature=0.3)
    if is_llm_error(out):
        # fall back to original topic if translation fails
        return topic

    # Parse comma / newline separated keywords
    parts = re.split(r"[,，\n]+", out)
    keywords = []
    for p in parts:
        kw = p.strip()
        if kw:
            keywords.append(kw)

    if not keywords:
        return topic

    # Limit to at most 2 keywords to keep query short & robust
    keywords = keywords[:2]

    # Combine original topic + English keywords using OR
    combined = topic + " OR " + " OR ".join(keywords)
    return combined


def generate_takeaway(news_items: List[Dict], region_code: Optional[str] = None) -> Optional[Dict[str, Dict[str, str]]]:
    """
    Generate bilingual summary:
    {
      "en": {"things_to_watch": "...", "takeaway": "..."},
      "zh": {"things_to_watch": "...", "takeaway": "..."}
    }
    """
    if not news_items:
        return None

    titles = [item["title"] for item in news_items[:10]]
    news_text = "\n".join(f"{idx+1}. {t}" for idx, t in enumerate(titles))

    region_cfg = find_region(region_code) if region_code else DEFAULT_REGION
    region_name = region_cfg["name"]

    # Step 1: English summary
    system_prompt_en = "You are a professional news analyst skilled at extracting key insights from multiple news articles."
    user_prompt_en = f"""Here are today's latest news headlines (for region: {region_name}):

{news_text}

Please focus on what matters for people in {region_name}.

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

    messages_en = [
        {"role": "system", "content": system_prompt_en},
        {"role": "user", "content": user_prompt_en},
    ]

    out_en = ask_llm(messages_en, max_tokens=500, temperature=0.7)
    if is_llm_error(out_en):
        return {"error": out_en}

    things_en = extract_section(out_en, "Things to Watch Today")
    takeaway_en = extract_section(out_en, "Take Away")

    en_payload = {
        "things_to_watch": (things_en or out_en or "").strip(),
        "takeaway": (takeaway_en or out_en or "").strip(),
    }

    # Step 2: translate to Traditional Chinese
    system_prompt_zh = "你是一位專業的新聞翻譯與摘要助手，擅長將英文新聞摘要翻譯成精準的繁體中文。"
    user_prompt_zh = f"""請將以下英文摘要翻譯成精準、自然的繁體中文，保留原本的結構與段落格式。

請使用以下格式輸出：

【今天需要注意的事情】
1. ...
2. ...
3. ...

【Take Away】
...

以下是英文內容：

{out_en}
"""

    messages_zh = [
        {"role": "system", "content": system_prompt_zh},
        {"role": "user", "content": user_prompt_zh},
    ]

    out_zh = ask_llm(messages_zh, max_tokens=600, temperature=0.7)
    if is_llm_error(out_zh):
        zh_payload = {
            "things_to_watch": "",
            "takeaway": out_zh,
        }
    else:
        things_zh = extract_section(out_zh, "今天需要注意的事情")
        takeaway_zh = extract_section(out_zh, "Take Away")
        zh_payload = {
            "things_to_watch": (things_zh or out_zh or "").strip(),
            "takeaway": (takeaway_zh or out_zh or "").strip(),
        }

    return {
        "en": en_payload,
        "zh": zh_payload,
    }


# ------------------------------
# RSS / News helpers
# ------------------------------


def build_google_news_url(topic: str, region_code: str) -> str:
    region_cfg = find_region(region_code)
    hl = region_cfg["hl"]
    gl = region_cfg["gl"]
    ceid = region_cfg["ceid"]
    # If topic contains CJK, expand it with English translations to improve recall
    processed_topic = expand_topic_with_translation(topic, region_code)
    # Add when:1d to bias toward last 24 hours
    query = f"{processed_topic} when:1d"
    return (
        "https://news.google.com/rss/search?"
        f"q={requests.utils.quote(query)}&hl={hl}&gl={gl}&ceid={ceid}"
    )


def parse_feed(url: str, max_items: int = 15) -> List[Dict]:
    """Parse RSS feed. If it's not a real feed, try to treat it as a single-article page."""
    feed = feedparser.parse(url)
    items: List[Dict] = []

    # Case 1: normal RSS feed
    if getattr(feed, "entries", None):
        for entry in feed.entries[:max_items]:
            title = entry.get("title", "").strip()
            link = entry.get("link", "").strip()
            summary = clean_html(entry.get("summary", "") or entry.get("description", ""))
            published = entry.get("published", "") or entry.get("updated", "")
            source = ""
            if "source" in entry and getattr(entry.source, "title", None):
                source = entry.source.title
            items.append(
                {
                    "title": title,
                    "link": link,
                    "summary": summary,
                    "published": published,
                    "source": source,
                }
            )
        return items

    # Case 2: Not RSS or empty RSS -> treat as single article
    try:
        resp = requests.get(url, timeout=6)
        resp.raise_for_status()
    except Exception:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else url

    desc_tag = soup.find("meta", attrs={"name": "description"})
    summary = desc_tag.get("content", "").strip() if desc_tag else ""

    items.append(
        {
            "title": title,
            "link": url,
            "summary": summary,
            "published": "",
            "source": "",
        }
    )
    return items


# ------------------------------
# Routes
# ------------------------------


@app.route("/")
def index():
    # Serve index.html from public folder
    if PUBLIC_DIR.exists():
        return send_from_directory(PUBLIC_DIR, "index.html")
    # Fallback: try same folder
    return send_from_directory(BASE_DIR, "index.html")


@app.route("/api/regions")
def api_regions():
    return jsonify({"regions": [{"code": r["code"], "name": r["name"]} for r in REGIONS]})


@app.route("/api/news")
def api_news():
    topic = request.args.get("topic", "").strip() or "trending"
    region_param = request.args.get("region", "").strip().lower()
    custom_url = request.args.get("customUrl", "").strip()
    # frontend still passes 'lang', but backend now always generates both en & zh
    _frontend_lang = request.args.get("lang", "en")

    region_cfg = find_region(region_param or DEFAULT_REGION["code"])

    try:
        if custom_url:
            feed_url = custom_url
        else:
            feed_url = build_google_news_url(topic, region_cfg["code"])

        items = parse_feed(feed_url, max_items=15)

        takeaway = None
        ai_error = None
        if items:
            try:
                raw_takeaway = generate_takeaway(items, region_cfg["code"])
                if isinstance(raw_takeaway, dict) and "error" in raw_takeaway:
                    ai_error = raw_takeaway.get("error")
                else:
                    takeaway = raw_takeaway
            except Exception as e:
                ai_error = str(e)

        return jsonify(
            {
                "items": items,
                "source": feed_url,
                "takeaway": takeaway,
                "ai_error": ai_error,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------------
# Entrypoint
# ------------------------------

if __name__ == "__main__":
    # For local dev, honour FLASK_HOST / FLASK_PORT
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
