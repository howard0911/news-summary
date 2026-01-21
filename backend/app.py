import os
import re
import json
import sqlite3
import threading
import time
import secrets
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from urllib.parse import quote_plus

import feedparser
from bs4 import BeautifulSoup
from flask import Flask, jsonify, request, send_from_directory
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash
from openai import OpenAI

app = Flask(__name__, static_folder="../public", static_url_path="")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", secrets.token_hex(32))

# ------------------------------
# Database (SQLite)
# ------------------------------
DB_PATH = os.getenv("DB_PATH", str(Path(__file__).parent / "app.db"))


def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    schema = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        username TEXT,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS preferences (
        user_id INTEGER PRIMARY KEY,
        topic TEXT,
        region TEXT,
        lang TEXT,
        sources TEXT,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS saved_preferences (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        topic TEXT,
        region TEXT,
        lang TEXT,
        sources TEXT,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS notification_settings (
        user_id INTEGER PRIMARY KEY,
        digest_time TEXT NOT NULL,
        enabled INTEGER NOT NULL DEFAULT 0,
        last_sent_date TEXT,
        updated_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        title TEXT NOT NULL,
        body TEXT NOT NULL,
        created_at TEXT NOT NULL,
        read_at TEXT,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS digests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        digest_date TEXT NOT NULL,
        summary_json TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """
    conn = get_db()
    try:
        conn.executescript(schema)
        # Best-effort migration for older databases.
        try:
            conn.execute("ALTER TABLE users ADD COLUMN username TEXT")
        except sqlite3.OperationalError:
            pass
        conn.commit()
    finally:
        conn.close()


serializer = URLSafeTimedSerializer(app.config["SECRET_KEY"])

init_db()


def now_iso() -> str:
    return datetime.utcnow().isoformat()


def generate_token(user_id: int) -> str:
    return serializer.dumps({"user_id": user_id})


def verify_token(token: str, max_age_seconds: int = 60 * 60 * 24 * 14) -> Optional[int]:
    try:
        data = serializer.loads(token, max_age=max_age_seconds)
        return int(data.get("user_id"))
    except (BadSignature, SignatureExpired, ValueError, TypeError):
        return None


def require_auth() -> Optional[int]:
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "", 1).strip()
        return verify_token(token)
    return None

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

# Groq config (OpenAI-compatible API, recommended free tier)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

# Native OpenAI model name (if you decide to use real OpenAI)
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# Behavior:
# - If local Ollama responds, use it.
# - Otherwise fall back to OpenAI (if OPENAI_API_KEY available).
# - You may force provider via ENV: AI_PROVIDER=ollama|openai|auto
AI_PROVIDER = os.getenv("AI_PROVIDER", "auto").lower()


def is_ollama_available(timeout: float = 1.0) -> bool:
    """Check whether Ollama local server appears to be running."""
    try:
        resp = requests.get(f"{OLLAMA_URL}/models", timeout=timeout)
        if resp.status_code == 200:
            return True
        resp2 = requests.get(OLLAMA_URL, timeout=timeout)
        return resp2.status_code == 200
    except Exception:
        return False


def get_openai_client():
    """Create a native OpenAI client if OPENAI_API_KEY is set."""
    if not OPENAI_API_KEY:
        return None
    try:
        if OPENAI_BASE_URL:
            return OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        return OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        print("Error initializing OpenAI client:", e)
        return None


def get_groq_client():
    """Create a Groq client using OpenAI-compatible API."""
    if not GROQ_API_KEY:
        return None
    try:
        return OpenAI(api_key=GROQ_API_KEY, base_url=GROQ_BASE_URL)
    except Exception as e:
        print("Error initializing Groq client:", e)
        return None


def get_llm_provider() -> Dict:
    """
    Decide which provider to use and return a descriptor dict:
    {
        "provider": "ollama" | "groq" | "openai" | "none",
        ...
    }
    """
    # 1) Explicit selection via env
    if AI_PROVIDER == "ollama":
        if is_ollama_available():
            return {"provider": "ollama", "model": OLLAMA_MODEL}
        return {"provider": "none", "reason": "OLLAMA_FORCED_but_unavailable"}

    if AI_PROVIDER == "groq":
        client = get_groq_client()
        if client:
            return {"provider": "groq", "client": client, "model": GROQ_MODEL}
        return {"provider": "none", "reason": "GROQ_FORCED_but_no_api_key"}

    if AI_PROVIDER == "openai":
        client = get_openai_client()
        if client:
            return {"provider": "openai", "client": client, "model": OPENAI_MODEL}
        return {"provider": "none", "reason": "OPENAI_FORCED_but_no_api_key"}

    # 2) Auto mode: prefer Ollama (local) → Groq (free cloud) → OpenAI (paid)
    if is_ollama_available():
        return {"provider": "ollama", "model": OLLAMA_MODEL}

    groq_client = get_groq_client()
    if groq_client:
        return {"provider": "groq", "client": groq_client, "model": GROQ_MODEL}

    openai_client = get_openai_client()
    if openai_client:
        return {"provider": "openai", "client": openai_client, "model": OPENAI_MODEL}

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
            r = requests.post(f"{OLLAMA_URL}/chat/completions", json=payload, timeout=timeout)
            r.raise_for_status()
            resp_json = r.json()
            return _parse_ollama_response(resp_json)
        except Exception as e:
            # If Ollama fails, try Groq first, then OpenAI
            print("Ollama request failed:", e)
            groq_client = get_groq_client()
            if groq_client:
                try:
                    resp = groq_client.chat.completions.create(
                        model=GROQ_MODEL,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                    return resp.choices[0].message.content
                except Exception as ge:
                    return f"[Groq Fallback Error] {e} | {ge}"
            openai_client = get_openai_client()
            if openai_client:
                try:
                    resp = openai_client.chat.completions.create(
                        model=OPENAI_MODEL,
                        messages=messages,
                        max_tokens=max_tokens,
                        temperature=temperature,
                    )
                    return resp.choices[0].message.content
                except Exception as oe:
                    return f"[OpenAI Fallback Error] {e} | {oe}"
            return f"[Error] Ollama failed and no Groq/OpenAI fallback available: {e}"

    # ---------- Groq / OpenAI (OpenAI-compatible clients) ----------
    if provider["provider"] in ("groq", "openai"):
        client = provider["client"]
        model = provider["model"]
        try:
            resp = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return resp.choices[0].message.content
        except Exception as e:
            prefix = "[Groq Error]" if provider["provider"] == "groq" else "[OpenAI Error]"
            return f"{prefix} {e}"

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
DEFAULT_REGION = REGION_CONFIG["us"]
MAX_NEWS_COUNT = 15


@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.post("/api/auth/signup")
def signup():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    if not email or not password:
        return jsonify({"error": "email_and_password_required"}), 400
    if len(password) < 8:
        return jsonify({"error": "password_too_short"}), 400
    if not username:
        username = email.split("@")[0] if "@" in email else email

    created_at = now_iso()
    password_hash = generate_password_hash(password)
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO users (email, username, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (email, username, password_hash, created_at),
        )
        conn.commit()
        user_row = conn.execute("SELECT id, email, username FROM users WHERE email = ?", (email,)).fetchone()
        user_id = user_row["id"]
    except sqlite3.IntegrityError:
        return jsonify({"error": "email_already_exists"}), 409
    finally:
        conn.close()

    token = generate_token(user_id)
    return jsonify({"token": token, "user": {"id": user_id, "email": email, "username": user_row["username"]}})


@app.post("/api/auth/login")
def login():
    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    if not email or not password:
        return jsonify({"error": "email_and_password_required"}), 400

    conn = get_db()
    try:
        row = conn.execute("SELECT id, email, username, password_hash FROM users WHERE email = ?", (email,)).fetchone()
    finally:
        conn.close()
    if not row or not check_password_hash(row["password_hash"], password):
        return jsonify({"error": "invalid_credentials"}), 401

    token = generate_token(row["id"])
    return jsonify({"token": token, "user": {"id": row["id"], "email": row["email"], "username": row["username"]}})


@app.get("/api/me")
def me():
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    try:
        row = conn.execute("SELECT id, email, username, created_at FROM users WHERE id = ?", (user_id,)).fetchone()
    finally:
        conn.close()
    if not row:
        return jsonify({"error": "user_not_found"}), 404
    return jsonify(
        {
            "user": {
                "id": row["id"],
                "email": row["email"],
                "username": row["username"],
                "created_at": row["created_at"],
            }
        }
    )


@app.post("/api/auth/change-password")
def change_password():
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    current_password = payload.get("current_password") or ""
    new_password = payload.get("new_password") or ""
    if not current_password or not new_password:
        return jsonify({"error": "passwords_required"}), 400
    if len(new_password) < 8:
        return jsonify({"error": "password_too_short"}), 400

    conn = get_db()
    try:
        row = conn.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,)).fetchone()
        if not row or not check_password_hash(row["password_hash"], current_password):
            return jsonify({"error": "invalid_current_password"}), 401
        conn.execute(
            "UPDATE users SET password_hash = ? WHERE id = ?",
            (generate_password_hash(new_password), user_id),
        )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"status": "ok"})


@app.post("/api/auth/update-profile")
def update_profile():
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    username = (payload.get("username") or "").strip()
    if not username:
        return jsonify({"error": "username_required"}), 400
    if len(username) < 2 or len(username) > 30:
        return jsonify({"error": "username_invalid_length"}), 400

    conn = get_db()
    try:
        conn.execute("UPDATE users SET username = ? WHERE id = ?", (username, user_id))
        conn.commit()
    finally:
        conn.close()

    return jsonify({"status": "ok", "username": username})


@app.get("/api/notification-settings")
def get_notification_settings():
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    try:
        row = conn.execute(
            "SELECT digest_time, enabled, last_sent_date, updated_at FROM notification_settings WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        return jsonify({"settings": None})
    return jsonify(
        {
            "settings": {
                "digest_time": row["digest_time"],
                "enabled": bool(row["enabled"]),
                "last_sent_date": row["last_sent_date"],
                "updated_at": row["updated_at"],
            }
        }
    )


@app.put("/api/notification-settings")
def update_notification_settings():
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    digest_time = (payload.get("digest_time") or "").strip()
    enabled = bool(payload.get("enabled"))
    if not digest_time:
        return jsonify({"error": "digest_time_required"}), 400

    updated_at = now_iso()
    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO notification_settings (user_id, digest_time, enabled, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                digest_time=excluded.digest_time,
                enabled=excluded.enabled,
                updated_at=excluded.updated_at
            """,
            (user_id, digest_time, int(enabled), updated_at),
        )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"status": "ok", "updated_at": updated_at})


@app.get("/api/notifications")
def list_notifications():
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT id, title, body, created_at, read_at
            FROM notifications
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT 100
            """,
            (user_id,),
        ).fetchall()
    finally:
        conn.close()

    items = []
    for row in rows:
        items.append(
            {
                "id": row["id"],
                "title": row["title"],
                "body": row["body"],
                "created_at": row["created_at"],
                "read_at": row["read_at"],
            }
        )
    return jsonify({"items": items})


@app.post("/api/notifications/<int:notification_id>/read")
def mark_notification_read(notification_id: int):
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    try:
        cur = conn.execute(
            """
            UPDATE notifications
            SET read_at = ?
            WHERE id = ? AND user_id = ?
            """,
            (now_iso(), notification_id, user_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "not_found"}), 404
    finally:
        conn.close()

    return jsonify({"status": "ok"})


@app.delete("/api/notifications/<int:notification_id>")
def delete_notification(notification_id: int):
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    try:
        cur = conn.execute(
            "DELETE FROM notifications WHERE id = ? AND user_id = ?",
            (notification_id, user_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "not_found"}), 404
    finally:
        conn.close()

    return jsonify({"status": "ok"})


@app.get("/api/preferences")
def get_preferences():
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    try:
        row = conn.execute(
            "SELECT topic, region, lang, sources, updated_at FROM preferences WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()
    if not row:
        return jsonify({"preferences": None})
    return jsonify(
        {
            "preferences": {
                "topic": row["topic"],
                "region": row["region"],
                "lang": row["lang"],
                "sources": json.loads(row["sources"]) if row["sources"] else None,
                "updated_at": row["updated_at"],
            }
        }
    )


@app.put("/api/preferences")
def update_preferences():
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip() or None
    region = (payload.get("region") or "").strip().lower() or None
    lang = (payload.get("lang") or "").strip().lower() or None
    sources = payload.get("sources")
    sources_json = json.dumps(sources) if sources is not None else None
    updated_at = now_iso()

    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO preferences (user_id, topic, region, lang, sources, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                topic=excluded.topic,
                region=excluded.region,
                lang=excluded.lang,
                sources=excluded.sources,
                updated_at=excluded.updated_at
            """,
            (user_id, topic, region, lang, sources_json, updated_at),
        )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"status": "ok", "updated_at": updated_at})


@app.get("/api/saved-preferences")
def list_saved_preferences():
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    try:
        rows = conn.execute(
            """
            SELECT id, topic, region, lang, sources, created_at
            FROM saved_preferences
            WHERE user_id = ?
            ORDER BY created_at DESC
            """,
            (user_id,),
        ).fetchall()
    finally:
        conn.close()

    items = []
    for row in rows:
        items.append(
            {
                "id": row["id"],
                "topic": row["topic"],
                "region": row["region"],
                "lang": row["lang"],
                "sources": json.loads(row["sources"]) if row["sources"] else None,
                "created_at": row["created_at"],
            }
        )
    return jsonify({"items": items})


@app.post("/api/saved-preferences")
def save_preferences():
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    payload = request.get_json(silent=True) or {}
    topic = (payload.get("topic") or "").strip() or None
    region = (payload.get("region") or "").strip().lower() or None
    lang = (payload.get("lang") or "").strip().lower() or None
    sources = payload.get("sources")
    sources_json = json.dumps(sources) if sources is not None else None

    if not any([topic, region, lang, sources]):
        conn = get_db()
        try:
            row = conn.execute(
                "SELECT topic, region, lang, sources FROM preferences WHERE user_id = ?",
                (user_id,),
            ).fetchone()
        finally:
            conn.close()
        if row:
            topic = topic or row["topic"]
            region = region or row["region"]
            lang = lang or row["lang"]
            sources_json = sources_json or row["sources"]

    created_at = now_iso()
    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO saved_preferences (user_id, topic, region, lang, sources, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user_id, topic, region, lang, sources_json, created_at),
        )
        conn.commit()
    finally:
        conn.close()

    return jsonify({"status": "ok", "created_at": created_at})


@app.delete("/api/saved-preferences/<int:pref_id>")
def delete_saved_preference(pref_id: int):
    user_id = require_auth()
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db()
    try:
        cur = conn.execute(
            "DELETE FROM saved_preferences WHERE id = ? AND user_id = ?",
            (pref_id, user_id),
        )
        conn.commit()
        if cur.rowcount == 0:
            return jsonify({"error": "not_found"}), 404
    finally:
        conn.close()

    return jsonify({"status": "ok"})


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
    custom_url = request.args.get("customUrl", "").strip()
    lang = request.args.get("lang", "en").lower()

    # validate region
    if region_key not in REGION_CONFIG:
        region_key = "us"
    region = REGION_CONFIG.get(region_key, DEFAULT_REGION)

    feed_url = custom_url or build_google_news_feed(topic, region)
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
    if out and not out.startswith("[Error]") and not out.startswith("[Ollama Error]") and not out.startswith("[OpenAI Error]") and not out.startswith("[Groq Error]") and not out.startswith("[Groq Fallback Error]"):
        # Try to parse sections
        if lang.startswith("zh"):
            things_to_watch = extract_section(out, "今天需要注意的事情")
            takeaway = extract_section(out, "Take Away")
        else:
            things_to_watch = extract_section(out, "Things to Watch Today")
            takeaway = extract_section(out, "Take Away")
        return {"things_to_watch": things_to_watch or out, "takeaway": takeaway or out}
    return {"things_to_watch": out, "takeaway": out}


def build_user_digest_payload(user_id: int) -> Optional[Dict]:
    conn = get_db()
    try:
        pref = conn.execute(
            "SELECT topic, region, lang, sources FROM preferences WHERE user_id = ?",
            (user_id,),
        ).fetchone()
    finally:
        conn.close()

    topic = "trending"
    region_key = "us"
    lang = "en"
    sources = None
    if pref:
        topic = pref["topic"] or topic
        region_key = pref["region"] or region_key
        lang = pref["lang"] or lang
        sources = json.loads(pref["sources"]) if pref["sources"] else None

    if region_key not in REGION_CONFIG:
        region_key = "us"

    region = REGION_CONFIG.get(region_key, DEFAULT_REGION)
    feed_url = build_google_news_feed(topic, region)
    if sources:
        # If sources provided, use first as custom URL/preset; for now default to Google News.
        pass
    entries = fetch_feed_entries(feed_url)
    if not entries:
        return None

    news_items = [serialize_entry(e) for e in entries[:MAX_NEWS_COUNT]]
    takeaway = generate_takeaway(news_items, lang)
    return {"items": news_items, "takeaway": takeaway, "lang": lang}


def create_digest_and_notification(user_id: int) -> bool:
    payload = build_user_digest_payload(user_id)
    if not payload:
        return False

    digest_date = datetime.utcnow().strftime("%Y-%m-%d")
    summary_json = json.dumps(payload)
    created_at = now_iso()
    title = "Daily Digest"
    body = payload.get("takeaway", {}).get("takeaway") or "Your daily digest is ready."

    conn = get_db()
    try:
        conn.execute(
            """
            INSERT INTO digests (user_id, digest_date, summary_json, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, digest_date, summary_json, created_at),
        )
        conn.execute(
            """
            INSERT INTO notifications (user_id, title, body, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (user_id, title, body, created_at),
        )
        conn.execute(
            "UPDATE notification_settings SET last_sent_date = ? WHERE user_id = ?",
            (digest_date, user_id),
        )
        conn.commit()
    finally:
        conn.close()

    return True


def notification_loop():
    while True:
        try:
            now_local = datetime.now()
            current_time = now_local.strftime("%H:%M")
            today = now_local.strftime("%Y-%m-%d")
            conn = get_db()
            try:
                rows = conn.execute(
                    """
                    SELECT user_id, digest_time, enabled, last_sent_date
                    FROM notification_settings
                    WHERE enabled = 1
                    """
                ).fetchall()
            finally:
                conn.close()
            for row in rows:
                if row["digest_time"] != current_time:
                    continue
                if row["last_sent_date"] == today:
                    continue
                create_digest_and_notification(row["user_id"])
        except Exception as e:
            print("notification_loop error:", e)
        time.sleep(60)


def start_notification_scheduler():
    t = threading.Thread(target=notification_loop, daemon=True)
    t.start()


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
    init_db()
    import socket
    start_notification_scheduler()

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
