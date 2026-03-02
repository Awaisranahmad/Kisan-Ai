import streamlit as st
from groq import Groq
from gtts import gTTS
from PIL import Image
import base64
from streamlit_mic_recorder import mic_recorder

# --- 1. Groq & Session State Setup ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.error("❌ API Key missing!")
        st.stop()
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

# Chat History maintain karne ke liye session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- 2. Voice Output Function ---
def play_audio(text):
    try:
        tts = gTTS(text=text, lang='ur')
        tts.save("response.mp3")
        with open("response.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <div style="background-color: #f1f8e9; padding: 10px; border-radius: 10px; border: 1px solid #2e7d32; margin: 10px 0;">
                    <p style="text-align: center; color: #2e7d32; margin-bottom: 5px;">🔊 Jawab Suniye</p>
                    <audio controls autoplay="true" style="width: 100%;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                </div>
                """
            st.markdown(md, unsafe_allow_html=True)
    except: pass

# --- 3. UI Styling ---
st.set_page_config(page_title="Kisan Expert Pro", page_icon="🌾", layout="centered")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    .urdu-font { font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: right; font-size: 22px; color: #1b5e20; line-height: 2.2; background: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); margin-bottom: 10px; }
    .user-msg { font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: left; background: #e8f5e9; padding: 10px; border-radius: 10px; margin-bottom: 5px; color: #2e7d32; }
    .header-box { background: #2e7d32; padding: 20px; border-radius: 0 0 20px 20px; color: white; text-align: center; margin-top: -60px; }
    .recording-pulse { color: red; font-weight: bold; animation: blinker 1s linear infinite; }
    @keyframes blinker { 50% { opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2316/2316334.png", width=80)
    st.title("Kisan Expert")
    lang_choice = st.selectbox("Zaban / زبان:", ["Urdu (اردو)", "Siraiki (سرائیکی)", "English"])
    menu = st.radio("Menu:", ["💬 Chat (Sawal o Jawab)", "📸 Crop Doctor (Tasveer)", "🧪 Khaad Advisor (Fertilizer)", "💰 Mandi Rates"])
    if st.button("Chat Clear Karein"):
        st.session_state.chat_history = []
        st.rerun()

st.markdown("<div class='header-box'><h1>🚜 Kisan Dost AI Expert</h1></div>", unsafe_allow_html=True)

# --- 5. AI Logic with History ---
def get_ai_response(user_input, chat_type="general"):
    # System prompt based on menu
    system_prompts = {
        "general": f"You are an expert Agri-Consultant. Language: {lang_choice}. Keep history in mind. Reply in Urdu script only.",
        "khaad": f"You are a Fertilizer Expert. Suggest Urea, DAP, NPK based on soil. Language: {lang_choice}. Reply in Urdu script.",
        "doctor": f"You are a Plant Pathologist. Analyze symptoms and give cures. Language: {lang_choice}."
    }
    
    # Context building
    messages = [{"role": "system", "content": system_prompts.get(chat_type)}]
    for chat in st.session_state.chat_history[-4:]: # Last 4 chats for memory
        messages.append({"role": chat["role"], "content": chat["content"]})
    messages.append({"role": "user", "content": user_input})
    
    completion = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
    return completion.choices[0].message.content

# --- FEATURES ---

# A: CHAT & VOICE INTERFACE
def voice_and_text_ui(chat_type):
    # Voice Input Area
    st.write("### 🎤 Bol Kar Sawal Puchein")
    audio_data = mic_recorder(start_prompt="Record Start 🎤", stop_prompt="Stop & Send ⏹️", key=f'recorder_{chat_type}')
    
    if audio_data:
        st.markdown("<p class='recording-pulse'>🔴 Recording Process Ho Rahi Hai...</p>", unsafe_allow_html=True)
        try:
            transcription = client.audio.transcriptions.create(
                file=("audio.wav", audio_data['bytes']), model="whisper-large-v3", language="ur"
            )
            process_input(transcription.text, chat_type)
        except: st.error("Voice error!")

    # Text Input
    user_text = st.text_input("✍️ Ya Yahan Likhein:", key=f"text_{chat_type}", placeholder="Sawal likhein...")
    if st.button("Bhejein (Send)", key=f"btn_{chat_type}"):
        process_input(user_text, chat_type)

def process_input(user_input, chat_type):
    if user_input:
        res = get_ai_response(user_input, chat_type)
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        st.session_state.chat_history.append({"role": "assistant", "content": res})
        st.rerun()

# --- DISPLAY CHAT HISTORY ---
for chat in st.session_state.chat_history:
    role_class = "user-msg" if chat["role"] == "user" else "urdu-font"
    st.markdown(f"<div class='{role_class}'>{chat['content']}</div>", unsafe_allow_html=True)
    if chat["role"] == "assistant":
        if chat == st.session_state.chat_history[-1]: # Only play audio for last msg
            play_audio(chat["content"])

# --- MENU NAVIGATION ---
if menu == "💬 Chat (Sawal o Jawab)":
    voice_and_text_ui("general")

elif menu == "📸 Crop Doctor (Tasveer)":
    st.subheader("Tasveer Se Beemari Check Karein")
    file = st.file_uploader("Upload Leaf/Crop Image", type=["jpg","png"])
    if file:
        st.image(file, width=300)
        st.success("Tasveer upload ho gayi! Ab niche sawal puchein.")
        voice_and_text_ui("doctor")

elif menu == "🧪 Khaad Advisor (Fertilizer)":
    st.subheader("Khaad aur Zameen ki Sehat")
    st.info("Apni fasal aur zameen ki halat batayein, AI aapko sahi khaad batayega.")
    voice_and_text_ui("khaad")

elif menu == "💰 Mandi Rates":
    st.subheader("Mandi Rates Advisor")
    voice_and_text_ui("general")
