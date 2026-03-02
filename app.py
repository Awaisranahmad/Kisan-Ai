import streamlit as st
from groq import Groq
from gtts import gTTS
from PIL import Image
import base64
from streamlit_mic_recorder import mic_recorder

# --- 1. Groq & Session Setup ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.error("API Key missing!")
        st.stop()
except Exception as e:
    st.stop()

# Session State for History
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- 2. Voice Output Function ---
def play_audio(text):
    try:
        tts = gTTS(text=text, lang='ur')
        tts.save("response.mp3")
        with open("response.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <div style="background: #e8f5e9; padding: 10px; border-radius: 10px; border: 1px solid #2e7d32; margin: 10px 0; text-align: center;">
                    <p style="color: #2e7d32; font-weight: bold; margin-bottom: 5px;">🔊 جواب سنیں</p>
                    <audio controls autoplay style="width: 100%;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                </div>
                """
            st.markdown(md, unsafe_allow_html=True)
    except: pass

# --- 3. UI Styling (Clean Green) ---
st.set_page_config(page_title="Kisan Dost Pro", page_icon="🌾")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    .urdu-text { font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: right; font-size: 20px; line-height: 2; color: #1b5e20; background: #f9f9f9; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-right: 5px solid #2e7d32; }
    .user-text { font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: left; background: #e1f5fe; padding: 10px; border-radius: 10px; margin-bottom: 10px; color: #01579b; border-left: 5px solid #0288d1; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #2e7d32; color: white; border: none; font-weight: bold; }
    .recording-text { color: #d32f2f; font-weight: bold; text-align: center; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar & New Chat ---
with st.sidebar:
    st.header("🚜 کیسان دوست")
    lang = st.selectbox("زبان چنیں", ["Urdu (اردو)", "Siraiki (سرائیکی)", "English"])
    
    st.write("---")
    # NEW CHAT BUTTON
    if st.button("🔄 نئی چیٹ شروع کریں (New Chat)"):
        st.session_state.messages = []
        st.rerun()
    
    menu = st.radio("مینو", ["💬 مشورہ", "📸 تصویر", "🧪 کھاد", "💰 منڈی"])
    st.write("---")
    st.caption("Pakistan Agriculture AI v2.5")

st.markdown("<h2 style='text-align: center; color: #2e7d32;'>🌾 کیسان دوست ایکسپرٹ</h2>", unsafe_allow_html=True)

# --- 5. Logic Handling ---
def process_input(user_text):
    if user_text:
        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_text})
        
        # Build context
        context = [{"role": "system", "content": f"You are a helpful Agri-Expert in Pakistan. Reply in {lang} script only. No Roman. Use respectful tone."}]
        for m in st.session_state.messages[-5:]: # Last 5 messages context
            context.append(m)
            
        try:
            with st.spinner("کیسان ایکسپرٹ جواب لکھ رہا ہے..."):
                response = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=context)
                ans = response.text if hasattr(response, 'text') else response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": ans})
        except:
            st.error("نیٹ ورک کا مسئلہ ہے۔ دوبارہ کوشش کریں۔")
        st.rerun()

# --- Display History First ---
for msg in st.session_state.messages:
    div_class = "user-text" if msg["role"] == "user" else "urdu-text"
    st.markdown(f"<div class='{div_class}'>{msg['content']}</div>", unsafe_allow_html=True)

# Audio play for last message only
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    play_audio(st.session_state.messages[-1]["content"])

st.write("---")

# --- Input Section ---
st.write("### 🎤 بولیں یا لکھیں")
cols = st.columns([1, 4])

with cols[0]:
    audio_data = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='main_mic')

with cols[1]:
    user_msg = st.text_input("", placeholder="یہاں اپنا سوال لکھیں...", label_visibility="collapsed")

# Handle Voice Input (Fixed Error handling)
if audio_data and 'bytes' in audio_data:
    try:
        with st.spinner("آواز پروسیس ہو رہی ہے..."):
            transcription = client.audio.transcriptions.create(
                file=("audio.wav", audio_data['bytes']),
                model="whisper-large-v3",
                language="ur"
            )
            if transcription.text:
                process_input(transcription.text)
    except Exception as e:
        # Silent error for cleaner UI
        pass

# Handle Text Input
if st.button("ارسال کریں (Send)"):
    if user_msg:
        process_input(user_msg)
