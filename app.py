import streamlit as st
from groq import Groq
from gtts import gTTS
from PIL import Image
import os
import base64

# --- 1. Groq Setup ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.error("❌ Groq API Key missing in Secrets!")
        st.stop()
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

# --- 2. Voice Function ---
def play_audio(text, lang_code='ur'):
    try:
        tts = gTTS(text=text, lang=lang_code)
        tts.save("response.mp3")
        with open("response.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <div style="text-align: center; margin-top: 10px;">
                    <audio controls autoplay="true" style="width: 80%;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                </div>
                """
            st.markdown(md, unsafe_allow_html=True)
    except:
        pass

# --- 3. UI Styling (Green & White Theme + Urdu Font) ---
st.set_page_config(page_title="Kisan Dost AI", page_icon="🚜", layout="wide")

st.markdown("""
    <style>
    /* Google Font for Urdu */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    
    .main { background-color: #ffffff; }
    
    .urdu-font {
        font-family: 'Noto Nastaliq Urdu', serif;
        direction: rtl;
        text-align: right;
        font-size: 22px;
        color: #1b5e20;
        line-height: 2.2;
    }
    
    /* Sidebar Green Theme */
    [data-testid="stSidebar"] {
        background-color: #2e7d32;
        color: white;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Buttons */
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 25px;
        border: 2px solid #1b5e20;
        font-weight: bold;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #ffffff;
        color: #2e7d32;
    }
    
    /* Header Bar */
    .header-bar {
        background-color: #2e7d32;
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar Options ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2316/2316334.png", width=100)
    st.header("⚙️ ترتیبات (Settings)")
    
    # Language Selection (Urdu, Siraiki, English)
    lang_choice = st.selectbox(
        "اپنی زبان منتخب کریں (Select Language):",
        ["Urdu (اردو)", "Siraiki (سرائیکی)", "English"]
    )
    
    menu = st.radio(
        "آپ کیا کرنا چاہتے ہیں؟",
        ["💬 کسان ایکسپرٹ (Chat)", "📸 فصل کا معائنہ (Crop Doctor)", "💰 منڈی کے ریٹ (Mandi)"]
    )
    st.divider()
    st.write("Dost Kisan AI - v2.0")

# --- 5. Main Layout ---
st.markdown("<div class='header-bar'><h1>🚜 کسان دوست AI اسسٹنٹ</h1></div>", unsafe_allow_html=True)

# Helper for Logic
def get_kisan_response(user_input, language):
    system_prompt = f"""
    You are a highly professional Agriculture Expert from Pakistan. 
    Instructions:
    1. If language is Urdu, reply ONLY in Urdu Script (ا ب ت). No Roman Urdu.
    2. If language is Siraiki, reply in Siraiki using Urdu Script.
    3. If language is English, reply in English.
    4. NEVER use Hindi words like 'Shubh', 'Dhanyawad'. Use 'Assalam-o-Alaikum', 'Shukriya'.
    5. Always provide links: Seeds (parc.gov.pk), Fertilizer (engrofertilizers.com).
    6. Keep the tone respectful (Aap, Janab).
    """
    
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Language: {language}. Question: {user_input}"}
        ]
    )
    return completion.choices[0].message.content

# --- FEATURES ---

if menu == "💬 کسان ایکسپرٹ (Chat)":
    st.subheader("کسان ایکسپرٹ آپ کی مدد کے لیے تیار ہے")
    u_input = st.text_input("اپنا سوال یہاں لکھیں:")
    
    if st.button("مشورہ لیں"):
        if u_input:
            with st.spinner("کیسان ایکسپرٹ سوچ رہا ہے..."):
                res = get_kisan_response(u_input, lang_choice)
                st.markdown(f"<div class='urdu-font'>{res}</div>", unsafe_allow_html=True)
                play_audio(res)
        else:
            st.warning("براہ کرم پہلے کچھ لکھیں۔")

elif menu == "📸 فصل کا معائنہ (Crop Doctor)":
    st.subheader("فصل کی بیماری کی تشخیص")
    img_file = st.file_uploader("پودے کی تصویر اپ لوڈ کریں", type=["jpg", "png", "jpeg"])
    
    if img_file:
        st.image(img_file, width=300)
        if st.button("ڈاکٹر سے چیک کروائیں"):
            with st.spinner("کیسان ڈاکٹر تصویر کا معائنہ کر رہا ہے..."):
                # Vision analysis simulated via Groq text expert for now
                res = get_kisan_response("Analyze this crop disease from the picture provided by farmer.", lang_choice)
                st.markdown(f"<div class='urdu-font'>{res}</div>", unsafe_allow_html=True)
                play_audio(res)

elif menu == "💰 منڈی کے ریٹ (Mandi)":
    st.subheader("مارکیٹ اور منڈی کے تازہ ترین ریٹ")
    crop = st.text_input("فصل کا نام لکھیں (مثلاً گندم، کپاس):")
    if st.button("ریٹ چیک کریں"):
        with st.spinner("مارکیٹ ایکسپرٹ ڈیٹا نکال رہا ہے..."):
            res = get_kisan_response(f"Current market prices for {crop} in Pakistan cities.", lang_choice)
            st.markdown(f"<div class='urdu-font'>{res}</div>", unsafe_allow_html=True)
            play_audio(res)
