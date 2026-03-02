import streamlit as st
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
