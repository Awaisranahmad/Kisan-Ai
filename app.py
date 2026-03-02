import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
from streamlit_mic_recorder import mic_recorder

# --- 1. Connection Setup ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Initialize session states
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_audio_id" not in st.session_state:
    st.session_state.processed_audio_id = None

# --- 2. Audio Playback Function ---
def play_audio(text):
    try:
        tts = gTTS(text=text, lang='ur')
        tts.save("res.mp3")
        with open("res.mp3", "rb") as f:
            data = f.read()
            b64 = base64.base64encode(data).decode()
            md = f'<audio id="ai_audio" controls autoplay style="width:100%"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>'
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
        st.session_state.processed_audio_id = None
        st.rerun()
    lang = st.selectbox("Zaban", ["Urdu", "Siraiki", "English"])

# --- 5. Logic to ask AI ---
def ask_kisan_ai(prompt):
    # Avoid duplicate prompts
    if not prompt: return
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    context = [{"role": "system", "content": f"You are a Pakistani Agri-Expert. Reply in {lang} script only. No Roman Urdu."}]
    context.extend(st.session_state.messages[-5:])
    
    with st.spinner("AI سوچ رہا ہے..."):
        try:
            chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=context)
            ans = chat.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ans})
        except:
            st.error("Connection error.")
    st.rerun()

# --- 6. Display Chat History ---
for m in st.session_state.messages:
    cls = "user" if m["role"] == "user" else "urdu"
    st.markdown(f"<div class='{cls}'>{m['content']}</div>", unsafe_allow_html=True)

# Play audio ONLY for the latest assistant message
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    # Hum ek container use karenge taake audio baar baar load na ho
    with st.container():
        play_audio(st.session_state.messages[-1]["content"])

st.divider()

# --- 7. Input Section (FIXED VOID LOOP) ---
st.write("### 🎤 بولیں یا لکھیں")
cols = st.columns([1, 4])

with cols[0]:
    # Mic recorder returns an object with an 'id'
    audio_output = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='kisan_mic')

with cols[1]:
    text_msg = st.text_input("Sawal Likhein...", key="text_in", placeholder="Yahan likhein...")
    send_btn = st.button("Bhejein (Send)")

# Handle Voice Input with ID verification
if audio_output is not None:
    # 'id' change hone par hi process karega
    current_id = audio_output.get('id')
    if current_id != st.session_state.processed_audio_id:
        st.session_state.processed_audio_id = current_id # Mark as processed
        
        with st.spinner("Awaz process ho rahi hai..."):
            try:
                rec = client.audio.transcriptions.create(
                    file=("audio.wav", audio_output['bytes']),
                    model="whisper-large-v3",
                    language="ur"
                )
                if rec.text.strip():
                    ask_kisan_ai(rec.text)
            except Exception as e:
                st.error("Audio error.")

# Handle Text Input
if send_btn and text_msg:
    ask_kisan_ai(text_msg)
