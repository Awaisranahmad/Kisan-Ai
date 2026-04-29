import streamlit as st
from config import t, get_groq_client
from ui_styles import load_styles
from components.chat import render_chat
from components.crop_doctor import render_crop_doctor
from components.fertilizer import render_fertilizer
from components.mandi import render_mandi
from components.gallery import render_gallery

st.set_page_config(page_title="Kisan Expert Pro", page_icon="🚜", layout="centered")

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "crop_history" not in st.session_state:
    st.session_state.crop_history = []
if "fert_history" not in st.session_state:
    st.session_state.fert_history = []
if "mandi_history" not in st.session_state:
    st.session_state.mandi_history = []
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = ""
if "processed_id" not in st.session_state:
    st.session_state.processed_id = None

# ---------- Load Styles ----------
load_styles()

# ---------- Sidebar ----------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2316/2316334.png", width=80)
    st.title(t("menu"))
    
    lang = st.selectbox("🌐 Language / زبان", ["ur", "en"], index=0)
    if lang != st.session_state.lang:
        st.session_state.lang = lang
        st.rerun()
    
    menu = st.radio(t("menu"), [t("chat"), t("crop_doctor"), t("fertilizer"), t("mandi")])
    
    if st.button(t("new_chat")):
        st.session_state.messages = []
        st.session_state.processed_id = None
        st.rerun()
    
    with st.expander(t("api_title"), expanded=False):
        key = st.text_input(t("enter_key"), type="password")
        if st.button(t("use_own_key")):
            st.session_state.user_api_key = key
            st.success("Key updated! Reloading...")
            st.rerun()
        if not get_groq_client():
            st.warning(t("no_api"))

# ---------- Header ----------
st.markdown(f"<div class='header-box'><h1>🚜 {t('title')}</h1><p>{t('subtitle')}</p></div>", unsafe_allow_html=True)

# ---------- Routing ----------
if menu == t("chat"):
    render_chat()
elif menu == t("crop_doctor"):
    render_crop_doctor()
elif menu == t("fertilizer"):
    render_fertilizer()
elif menu == t("mandi"):
    render_mandi()

# Gallery at bottom
render_gallery()
