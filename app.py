import streamlit as stimport streamlit as st
from groq import Groq
from gtts import gTTS
from PIL import Image
import base64
from streamlit_mic_recorder import mic_recorder

# --- 1. Groq Setup ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.error("❌ API Key missing in Secrets!")
        st.stop()
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

# --- 2. Voice Output Function ---
def play_audio(text):
    try:
        tts = gTTS(text=text, lang='ur')
        tts.save("response.mp3")
        with open("response.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <div style="background-color: #e8f5e9; padding: 10px; border-radius: 15px; border: 1px solid #2e7d32; margin-top: 20px;">
                    <p style="text-align: center; color: #2e7d32; font-weight: bold;">🔊 جواب سنیں (AI Voice)</p>
                    <audio controls autoplay="true" style="width: 100%;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                </div>
                """
            st.markdown(md, unsafe_allow_html=True)
    except:
        pass

# --- 3. UI Styling (Green & White Modern Theme) ---
st.set_page_config(page_title="Kisan Dost AI", page_icon="🚜", layout="centered")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    
    .urdu-font {
        font-family: 'Noto Nastaliq Urdu', serif;
        direction: rtl;
        text-align: right;
        font-size: 26px;
        color: #1b5e20;
        line-height: 2.8;
        background: #f1f8e9;
        padding: 20px;
        border-radius: 15px;
        border-right: 10px solid #2e7d32;
        margin-bottom: 20px;
    }
    
    /* Input Box Styling */
    .stTextInput input {
        border: 2px solid #2e7d32 !important;
        border-radius: 15px !important;
        padding: 15px !important;
        font-size: 18px !important;
    }

    /* Voice Section Styling */
    .voice-box {
        background: #ffffff;
        border: 2px dashed #2e7d32;
        padding: 20px;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 20px;
    }

    .header-box {
        background: linear-gradient(90deg, #1b5e20, #2e7d32);
        padding: 30px;
        border-radius: 0 0 30px 30px;
        color: white;
        text-align: center;
        margin-top: -60px;
        box-shadow: 0px 4px 15px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Main UI ---
st.markdown("<div class='header-box'><h1>🚜 کسان دوست: آپ کا اے آئی مشیر</h1><p>بول کر یا لکھ کر سوال پوچھیں</p></div>", unsafe_allow_html=True)
st.write("---")

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2316/2316334.png", width=80)
    st.title("Settings")
    lang_choice = st.selectbox("Zaban / زبان:", ["Urdu (اردو)", "Siraiki (سرائیکی)", "English"])
    menu = st.radio("Menu:", ["💬 کسان مشورہ (Chat)", "📸 تصویر سے معائنہ", "💰 منڈی ریٹ"])

# --- Logic Helper ---
def get_ai_response(text_input):
    system_msg = f"You are a professional Agri-Expert in Pakistan. Reply ONLY in {lang_choice} script. Use 'Assalam-o-Alaikum'. Keep language simple for a farmer. Mention seeds (parc.gov.pk) or fertilizers (engrofertilizers.com) where needed."
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": text_input}]
    )
    return completion.choices[0].message.content

# --- FEATURES ---

if menu == "💬 کسان مشورہ (Chat)":
    
    # 🎤 VOICE INPUT SECTION
    st.markdown("<div class='voice-box'>", unsafe_allow_html=True)
    st.write("### 🎤 اپنی بات ریکارڈ کریں")
    st.write("نیچے بٹن دبائیں اور اپنا سوال بولیں:")
    audio_data = mic_recorder(
        start_prompt="بولنا شروع کریں (Start) 🎤", 
        stop_prompt="روک دیں اور بھیجیں (Stop) ⏹️", 
        key='recorder'
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.write("--- یا ---")

    # ✍️ TEXT INPUT SECTION
    user_text = st.text_input("✍️ یہاں اپنا سوال لکھیں:", placeholder="مثلاً: گندم کو کھاد کب ڈالنی ہے؟")

    final_input = ""
    
    # Process Voice
    if audio_data:
        with st.spinner("آپ کی آواز سنی جا رہی ہے..."):
            try:
                transcription = client.audio.transcriptions.create(
                    file=("audio.wav", audio_data['bytes']),
                    model="whisper-large-v3",
                    language="ur"
                )
                final_input = transcription.text
                st.info(f"آپ نے کہا: {final_input}")
            except:
                st.error("آواز سمجھنے میں مسئلہ ہوا۔ دوبارہ کوشش کریں۔")

    # Process Text
    elif user_text:
        final_input = user_text

    # Generate Response
    if final_input:
        with st.spinner("کیسان ایکسپرٹ جواب تیار کر رہا ہے..."):
            res = get_ai_response(final_input)
            st.markdown(f"<div class='urdu-font'>{res}</div>", unsafe_allow_html=True)
            play_audio(res)

elif menu == "📸 تصویر سے معائنہ":
    st.header("📸 پودے کی تصویر اپ لوڈ کریں")
    file = st.file_uploader("", type=["jpg","png","jpeg"])
    if file:
        st.image(file, width=400, caption="آپ کا پودا")
        if st.button("معائنہ شروع کریں"):
            res = get_ai_response("Analyze crop from farmer description and give Urdu advice.")
            st.markdown(f"<div class='urdu-font'>{res}</div>", unsafe_allow_html=True)
            play_audio(res)

elif menu == "💰 منڈی ریٹ":
    st.header("💰 منڈی کے تازہ ترین ریٹ")
    crop = st.text_input("فصل کا نام لکھیں:")
    if st.button("ریٹ معلوم کریں"):
        res = get_ai_response(f"Current market prices for {crop} in Pakistan.")
        st.markdown(f"<div class='urdu-font'>{res}</div>", unsafe_allow_html=True)
        play_audio(res)
from groq import Groq
from gtts import gTTS
from PIL import Image
import base64
from streamlit_mic_recorder import mic_recorder # Nayi Library

# --- 1. Groq Setup ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.error("❌ API Key missing!")
        st.stop()
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

# --- 2. Voice Output Function (AI Bol Kar Bataye) ---
def play_audio(text):
    try:
        tts = gTTS(text=text, lang='ur')
        tts.save("response.mp3")
        with open("response.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <div style="text-align: center;">
                    <audio controls autoplay="true" style="width: 100%;">
                    <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                    </audio>
                </div>
                """
            st.markdown(md, unsafe_allow_html=True)
    except:
        pass

# --- 3. UI Styling (Green & White Theme) ---
st.set_page_config(page_title="Kisan Dost AI", page_icon="🚜", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    .urdu-font {
        font-family: 'Noto Nastaliq Urdu', serif;
        direction: rtl;
        text-align: right;
        font-size: 24px;
        color: #1b5e20;
        line-height: 2.5;
    }
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 20px;
        font-weight: bold;
    }
    [data-testid="stSidebar"] { background-color: #1b5e20; }
    .header-box { background-color: #2e7d32; padding: 15px; border-radius: 10px; color: white; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar ---
with st.sidebar:
    st.title("🚜 ترتیبات (Settings)")
    lang_choice = st.selectbox("Zaban / زبان:", ["Urdu (اردو)", "Siraiki (سرائیکی)", "English"])
    menu = st.radio("Menu:", ["💬 کسان ایکسپرٹ (Chat)", "📸 فصل کا معائنہ", "💰 منڈی ریٹ"])

st.markdown("<div class='header-box'><h1>🚜 کسان دوست AI اسسٹنٹ</h1></div>", unsafe_allow_html=True)

# --- AI Logic Helper ---
def get_ai_response(text_input):
    system_msg = f"You are a Pakistani Agri-Expert. Reply ONLY in {lang_choice} script. No Roman Urdu. Use 'Assalam-o-Alaikum'. Provide website links for seeds/fertilizers."
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": system_msg}, {"role": "user", "content": text_input}]
    )
    return completion.choices[0].message.content

# --- MAIN FEATURES ---

if menu == "💬 کسان ایکسپرٹ (Chat)":
    st.subheader("آپ اپنا سوال بول کر یا لکھ کر پوچھ سکتے ہیں")
    
    # --- VOICE INPUT SECTION ---
    st.write("🎤 **بول کر سوال پوچھیں (Record Button دبائیں):**")
    audio_data = mic_recorder(start_prompt="Record Start 🎤", stop_prompt="Stop & Send ⏹️", key='recorder')
    
    user_text = st.text_input("✍️ **یا یہاں لکھیں:**")

    # Processing Input
    final_input = ""
    if audio_data:
        # Voice to Text (Transcribe)
        with st.spinner("آپ کی آواز کو سمجھا جا رہا ہے..."):
            try:
                # Groq Whisper model for Urdu/Punjabi voice to text
                transcription = client.audio.transcriptions.create(
                    file=("audio.wav", audio_data['bytes']),
                    model="whisper-large-v3",
                    language="ur"
                )
                final_input = transcription.text
                st.info(f"آپ نے کہا: {final_input}")
            except Exception as e:
                st.error("Awaz samajhne mein masla hua.")

    elif user_text:
        final_input = user_text

    if final_input:
        with st.spinner("کیسان ایکسپرٹ جواب تیار کر رہا ہے..."):
            res = get_ai_response(final_input)
            st.markdown(f"<div class='urdu-font'>{res}</div>", unsafe_allow_html=True)
            play_audio(res)

elif menu == "📸 فصل کا معائنہ":
    st.header("فصل کی تصویر بھیجیں")
    file = st.file_uploader("Upload Image", type=["jpg","png"])
    if file:
        st.image(file, width=300)
        if st.button("Check Karwein"):
            res = get_ai_response("Analyze this crop image and give Urdu advice.")
            st.markdown(f"<div class='urdu-font'>{res}</div>", unsafe_allow_html=True)
            play_audio(res)

elif menu == "💰 منڈی ریٹ":
    st.header("منڈی کے تازہ ترین ریٹ")
    crop = st.text_input("Fasal ka naam:")
    if st.button("Check Rates"):
        res = get_ai_response(f"Current mandi rates for {crop} in Pakistan.")
        st.markdown(f"<div class='urdu-font'>{res}</div>", unsafe_allow_html=True)
        play_audio(res)
