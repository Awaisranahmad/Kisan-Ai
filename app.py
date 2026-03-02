import streamlit as st
from groq import Groq
from gtts import gTTS
from PIL import Image
import base64
from streamlit_mic_recorder import mic_recorder

# --- 1. Setup ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_audio_id" not in st.session_state:
    st.session_state.processed_audio_id = None

# --- 2. Voice Output Function ---
def play_audio(text):
    try:
        tts = gTTS(text=text, lang='ur')
        tts.save("res.mp3")
        with open("res.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <div style="background: #f1f8e9; padding: 10px; border-radius: 10px; border: 1px solid #2e7d32; margin: 10px 0; text-align: center;">
                    <p style="color: #2e7d32; font-weight: bold; margin-bottom: 5px;">🔊 Jawab Suniye (AI Voice)</p>
                    <audio controls autoplay style="width: 100%;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                </div>
                """
            st.markdown(md, unsafe_allow_html=True)
    except: pass

# --- 3. UI Styling (Wahi Green & White Theme) ---
st.set_page_config(page_title="Kisan Expert Pro", page_icon="🌾", layout="centered")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    .urdu-font { font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: right; font-size: 22px; color: #1b5e20; line-height: 2.2; background: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px; }
    .user-msg { font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: left; background: #e8f5e9; padding: 10px; border-radius: 10px; margin-bottom: 5px; color: #2e7d32; }
    .header-box { background: #2e7d32; padding: 20px; border-radius: 0 0 20px 20px; color: white; text-align: center; margin-top: -60px; }
    [data-testid="stSidebar"] { background-color: #1b5e20; color: white; }
    .stButton>button { background-color: #2e7d32; color: white; border-radius: 20px; width: 100%; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar (Wapas Saare Options) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2316/2316334.png", width=80)
    st.title("Kisan Expert")
    lang_choice = st.selectbox("Zaban / زبان:", ["Urdu (اردو)", "Siraiki (سرائیکی)", "English"])
    menu = st.radio("Menu:", ["💬 Chat (Sawal o Jawab)", "📸 Crop Doctor (Tasveer)", "🧪 Khaad Advisor", "💰 Mandi Rates"])
    if st.button("🔄 New Chat / چیٹ صاف کریں"):
        st.session_state.messages = []
        st.session_state.processed_audio_id = None
        st.rerun()

st.markdown("<div class='header-box'><h1>🚜 Kisan Dost AI Expert</h1></div>", unsafe_allow_html=True)

# --- 5. AI Logic ---
def ask_kisan_ai(prompt, chat_type="general"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    system_msg = f"You are a professional Agri-Expert from Pakistan. Reply in {lang_choice} script only. No Roman Urdu, No Chinese. Use 'Assalam-o-Alaikum'."
    
    messages = [{"role": "system", "content": system_msg}]
    messages.extend(st.session_state.messages[-5:])
    
    with st.spinner("Kisan Expert soch raha hai..."):
        chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
        ans = chat.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": ans})
    st.rerun()

# Display Chat
for m in st.session_state.messages:
    cls = "user-msg" if m["role"] == "user" else "urdu-font"
    st.markdown(f"<div class='{cls}'>{m['content']}</div>", unsafe_allow_html=True)

if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    play_audio(st.session_state.messages[-1]["content"])

st.divider()

# --- 6. Input Section (Loop Fixed) ---
st.write("### 🎤 Bol Kar Ya Likh Kar Puchein")
cols = st.columns([1, 4])

with cols[0]:
    audio_data = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='kisan_mic')

with cols[1]:
    user_text = st.text_input("", placeholder="Yahan apna sawal likhein...", label_visibility="collapsed")
    send_btn = st.button("Bhejein (Send)")

# Voice Logic (No Loop)
if audio_data:
    if audio_data.get('id') != st.session_state.processed_audio_id:
        st.session_state.processed_audio_id = audio_data.get('id')
        with st.spinner("Awaz suni ja rahi hai..."):
            try:
                rec = client.audio.transcriptions.create(
                    file=("audio.wav", audio_data['bytes']),
                    model="whisper-large-v3",
                    language="ur"
                )
                if rec.text.strip():
                    ask_kisan_ai(rec.text)
            except: st.error("Mic error!")

# Text Logic
if send_btn and user_text:
    ask_kisan_ai(user_text)

# --- 7. Additional Sections based on Menu ---
if menu == "📸 Crop Doctor (Tasveer)":
    st.write("---")
    file = st.file_uploader("Pauday ki tasveer dein", type=["jpg","png"])
    if file: st.image(file, width=300)

elif menu == "🧪 Khaad Advisor":
    st.info("Khaad ke bare mein sawal puchein (e.g. Urea kitni dalun?)")

elif menu == "💰 Mandi Rates":
    st.info("Fasal ka naam likhein mandi rates ke liye.")
