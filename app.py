import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
from streamlit_mic_recorder import mic_recorder

# --- 1. Setup ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "last_speech" not in st.session_state:
    st.session_state.last_speech = None

# --- 2. Audio Play Function ---
def play_audio(text):
    try:
        tts = gTTS(text=text, lang='ur')
        tts.save("res.mp3")
        with open("res.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f'<audio controls autoplay style="width:100%"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
            st.markdown(md, unsafe_allow_html=True)
    except: pass

# --- 3. UI Styling ---
st.set_page_config(page_title="Kisan AI", page_icon="🌾")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    .urdu { font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: right; font-size: 20px; background: #f1f8e9; padding: 15px; border-radius: 10px; margin-bottom: 10px; border-right: 5px solid #2e7d32; }
    .user { font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: left; background: #e3f2fd; padding: 10px; border-radius: 10px; margin-bottom: 10px; border-left: 5px solid #1565c0; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar ---
with st.sidebar:
    st.title("🚜 کیسان دوست")
    if st.button("🔄 نئی چیٹ (New Chat)"):
        st.session_state.messages = []
        st.session_state.last_speech = None
        st.rerun()
    lang = st.selectbox("Zaban", ["Urdu", "Siraiki", "English"])

# --- 5. Main Logic ---
def ask_kisan_ai(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    context = [{"role": "system", "content": f"You are a Pakistani Agri-Expert. Reply in {lang} script. No Roman Urdu."}]
    context.extend(st.session_state.messages[-5:])
    
    with st.spinner("AI سوچ رہا ہے..."):
        chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=context)
        ans = chat.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": ans})
    st.rerun()

# Display Chat
for m in st.session_state.messages:
    cls = "user" if m["role"] == "user" else "urdu"
    st.markdown(f"<div class='{cls}'>{m['content']}</div>", unsafe_allow_html=True)

if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    play_audio(st.session_state.messages[-1]["content"])

st.divider()

# --- 6. Input Section (Loop Fix) ---
st.write("### 🎤 بولیں یا لکھیں")
cols = st.columns([1, 4])

with cols[0]:
    # Recording handle
    audio = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='my_mic')

with cols[1]:
    text_msg = st.text_input("Sawal Likhein...", label_visibility="collapsed")
    send_btn = st.button("Bhejein (Send)")

# Check Voice Input
if audio:
    # Check if this is a NEW recording, not the old one
    if audio['id'] != st.session_state.get('last_speech_id'):
        st.session_state.last_speech_id = audio['id'] # Store unique ID to prevent loop
        with st.spinner("Awaz process ho rahi hai..."):
            try:
                rec = client.audio.transcriptions.create(
                    file=("audio.wav", audio['bytes']),
                    model="whisper-large-v3",
                    language="ur"
                )
                if rec.text:
                    ask_kisan_ai(rec.text)
            except: st.error("Mic error!")

# Check Text Input
if send_btn and text_msg:
    ask_kisan_ai(text_msg)
