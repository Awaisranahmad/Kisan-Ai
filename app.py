import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import os
from streamlit_mic_recorder import mic_recorder
from PIL import Image

# --- 1. Setup ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_id" not in st.session_state:
    st.session_state.processed_id = None

# --- 2. Manual Voice Output (No Autoplay) ---
def play_audio(text):
    try:
        tts = gTTS(text=text, lang='ur', slow=False)
        tts.save("expert_voice.mp3")
        with open("expert_voice.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            # Yahan autoplay="false" kar diya hai
            md = f"""
                <div style="background: #f1f8e9; padding: 10px; border-radius: 10px; border: 1px solid #2e7d32; margin: 10px 0; text-align: center;">
                    <p style="color: #2e7d32; font-weight: bold; margin-bottom: 5px;">🔊 جواب سننے کے لیے پلے بٹن دبائیں</p>
                    <audio controls style="width: 100%;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                </div>
                """
            st.markdown(md, unsafe_allow_html=True)
    except Exception:
        pass

# --- 3. UI Styling ---
st.set_page_config(page_title="Kisan Expert Pro", page_icon="🚜")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    .urdu-font { font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: right; font-size: 20px; color: #1b5e20; background: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px; border-right: 5px solid #2e7d32; }
    .user-msg { font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: left; background: #e8f5e9; padding: 10px; border-radius: 10px; margin-bottom: 5px; color: #2e7d32; border-left: 5px solid #2e7d32; }
    .header-box { background: #2e7d32; padding: 20px; border-radius: 0 0 20px 20px; color: white; text-align: center; margin-top: -60px; }
    [data-testid="stSidebar"] { background-color: #1b5e20; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2316/2316334.png", width=70)
    st.title("Kisan Expert")
    lang = st.selectbox("Zaban", ["Urdu (اردو)", "Siraiki (سرائیکی)", "English"])
    menu = st.radio("Menu", ["💬 Chat", "📸 Crop Doctor", "🧪 Khaad Advisor", "💰 Mandi Rates"])
    if st.button("🔄 New Chat"):
        st.session_state.messages = []
        st.session_state.processed_id = None
        st.rerun()

st.markdown("<div class='header-box'><h1>🚜 کسان دوست ایکسپرٹ</h1></div>", unsafe_allow_html=True)

# --- 5. AI Logic ---
def ask_ai(prompt):
    st.session_state.messages.append({"role": "user", "content": prompt})
    sys_prompt = f"You are a professional Agri-Expert from Pakistan. Respond in {lang} script. Strictly NO Hindi words like 'dhanyawad'. Use 'Assalam-o-Alaikum' and 'Shukriya'."
    messages = [{"role": "system", "content": sys_prompt}]
    messages.extend(st.session_state.messages[-5:])
    
    with st.spinner("جواب تیار ہو رہا ہے..."):
        try:
            chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
            ans = chat.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ans})
        except: st.error("Error!")
    st.rerun()

# Display Chat
for m in st.session_state.messages:
    cls = "user-msg" if m["role"] == "user" else "urdu-font"
    st.markdown(f"<div class='{cls}'>{m['content']}</div>", unsafe_allow_html=True)

# Audio (No Autoplay)
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    play_audio(st.session_state.messages[-1]["content"])

st.write("---")

# --- 6. Input Section ---
st.write("### 🎤 بولیں یا لکھیں")
c1, c2 = st.columns([1, 4])
with c1:
    audio_data = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='kisan_mic')
with c2:
    u_text = st.text_input("", placeholder="یہاں سوال لکھیں...", label_visibility="collapsed")
    send = st.button("ارسال کریں (Send)")

if audio_data is not None:
    if audio_data.get('id') != st.session_state.processed_id:
        st.session_state.processed_id = audio_data.get('id')
        try:
            transcription = client.audio.transcriptions.create(
                file=("audio.wav", audio_data['bytes']), model="whisper-large-v3", language="ur"
            )
            if transcription.text.strip(): ask_ai(transcription.text)
        except: pass

if send and u_text: ask_ai(u_text)

# --- 7. Crop Doctor (Fixed .jfif Support) ---
if menu == "📸 Crop Doctor":
    st.subheader("فصل کی تصویر اپ لوڈ کریں")
    # Yahan maine .jfif ko support mein shamil kar diya hai
    file = st.file_uploader("Upload Image", type=["jpg", "png", "jpeg", "jfif"])
    if file:
        img = Image.open(file)
        st.image(img, caption="Aap ki upload karda tasveer", use_container_width=True)
        if st.button("Check Karwein"):
            ask_ai("Analyze this crop image situation in Urdu.")
