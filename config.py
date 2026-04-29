import streamlit as st
from groq import Groq

# ---------- API Setup ----------
def get_groq_client():
    """Secrets se key le, nahi to user session key se"""
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if api_key:
        return Groq(api_key=api_key)
    user_key = st.session_state.get("user_api_key", "")
    if user_key:
        return Groq(api_key=user_key)
    return None

# ---------- Language Setup ----------
if "lang" not in st.session_state:
    st.session_state.lang = "ur"

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
    """Translate function"""
    return TEXTS.get(st.session_state.lang, TEXTS["ur"]).get(key, key)
