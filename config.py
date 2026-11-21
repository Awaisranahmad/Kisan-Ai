"""App config: language texts + AI client.

The AI client is built from ``models.py`` — the provider and model are
chosen there, so this file never hardcodes a model name.
"""
import os

import streamlit as st

try:
    # Lets a local .env file provide API keys (optional, no crash if absent).
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass

from models import CHAT_MODEL, get_provider


def _session_key():
    """Key the user pasted in the sidebar (empty outside a Streamlit run)."""
    try:
        return st.session_state.get("user_api_key", "") or ""
    except Exception:
        return ""


def _stored_key(api_key_name):
    """Key from .streamlit/secrets.toml, else environment / .env."""
    try:
        value = st.secrets.get(api_key_name, "") or ""
    except Exception:
        # No secrets file (e.g. running locally) — not an error.
        value = ""
    if not value:
        value = os.environ.get(api_key_name, "") or ""
    return value


def get_ai_client(provider_name=None):
    """Build an OpenAI-compatible client for a provider from models.py.

    Key lookup order: sidebar key -> secrets.toml -> .env / environment.
    Returns None when no key is available for that provider.
    """
    provider_name = provider_name or CHAT_MODEL["provider"]
    provider = get_provider(provider_name)
    api_key = _session_key() or _stored_key(provider["api_key_name"])
    if not api_key:
        return None
    from openai import OpenAI

    return OpenAI(api_key=api_key, base_url=provider["base_url"])


def get_groq_client():
    """Backwards-compatible name — returns the client for the active provider."""
    return get_ai_client()


# Language texts (UNCHANGED)
TEXTS = {
    "ur": {
        "title": "کیسان ایکسپرٹ پرو",
        "subtitle": "آپ کی فصل، ہماری فکر",
        "menu": "کیسان مینو",
        "chat": "💬 چیٹ",
        "crop_doctor": "📸 کراپ ڈاکٹر",
        "fertilizer": "🧪 کھاد ایڈوائزر",
        "mandi": "💰 منڈی ریٹ",
        "new_chat": "🔄 نئی چیٹ",
        "api_title": "🔑 API سیٹنگز",
        "enter_key": "اپنی GROQ API کی درج کریں:",
        "use_own_key": "اپنی کی استعمال کریں",
        "no_api": "API کی دستیاب نہیں۔",
        "key_error": "API کی غلط ہے۔ براہ کرم صحیح کی ڈالیں۔",
        "rate_limit": "حد ختم ہو گئی ہے۔ تھوڑی دیر بعد دوبارہ کوشش کریں۔",
        "model_error": "یہ AI ماڈل اب دستیاب نہیں۔ models.py میں ماڈل بدلیں۔",
        "send": "بھیجیں",
        "examine": "معائنہ کریں",
        "upload": "تصویر اپ لوڈ کریں",
        "camera": "تصویر کھینچیں",
        "download_pdf": "📄 PDF ڈاؤن لوڈ",
        "download_chat": "💾 چیٹ ڈاؤن لوڈ",
        "gallery_title": "🖼️ فصل کی تصاویر",
        "audio_prompt": "🔊 جواب سننے کے لیے پلے دبائیں",
        "fertilizer_advice": "مشورہ اور ریٹ لیں",
        "show_rate": "ریٹ دیکھیں",
    },
    "en": {
        "title": "Kisan Expert Pro",
        "subtitle": "Your Crop, Our Concern",
        "menu": "Farmer Menu",
        "chat": "💬 Chat",
        "crop_doctor": "📸 Crop Doctor",
        "fertilizer": "🧪 Fertilizer Advisor",
        "mandi": "💰 Mandi Rates",
        "new_chat": "🔄 New Chat",
        "api_title": "🔑 API Settings",
        "enter_key": "Enter your GROQ API Key:",
        "use_own_key": "Use Own Key",
        "no_api": "API key not available.",
        "key_error": "API key is wrong. Please enter a correct key.",
        "rate_limit": "Rate limit reached. Please try again in a little while.",
        "model_error": "This AI model is no longer available. Change the model in models.py.",
        "send": "Send",
        "examine": "Examine",
        "upload": "Upload Image",
        "camera": "Take Photo",
        "download_pdf": "📄 Download PDF",
        "download_chat": "💾 Download Chat",
        "gallery_title": "🖼️ Crop Gallery",
        "audio_prompt": "🔊 Play to listen",
        "fertilizer_advice": "Get Advice & Rates",
        "show_rate": "Show Rates",
    }
}

def t(key):
    try:
        lang = st.session_state.get("lang", "ur")
    except Exception:
        lang = "ur"  # outside a Streamlit run (e.g. tests)
    return TEXTS.get(lang, TEXTS["ur"]).get(key, key)
