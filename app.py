import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import os
from streamlit_mic_recorder import mic_recorder
from PIL import Image

# --- 1. Connection ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_id" not in st.session_state:
    st.session_state.processed_id = None

# --- 2. Voice Output (Manual Play) ---
def play_audio(text):
    try:
        tts = gTTS(text=text, lang='ur', slow=False)
        tts.save("expert_voice.mp3")
        with open("expert_voice.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <div style="background: #f1f8e9; padding: 10px; border-radius: 10px; border: 1px solid #2e7d32; margin: 10px 0; text-align: center;">
                    <p style="color: #2e7d32; font-weight: bold; margin-bottom: 5px;">🔊 جواب سننے کے لیے پلے بٹن دبائیں</p>
                    <audio controls style="width: 100%;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                </div>
                """
            st.markdown(md, unsafe_allow_html=True)
    except: pass

# --- 3. UI Styling (Light Green Sidebar & Urdu Font) ---
st.set_page_config(page_title="Kisan Expert Pro", page_icon="🚜")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    
    /* Main Background */
    .stApp { background-color: #ffffff; }

    /* Sidebar Light Green */
    [data-testid="stSidebar"] {
        background-color: #e8f5e9 !important;
        border-right: 1px solid #c8e6c9;
    }
    [data-testid="stSidebar"] * { color: #1b5e20 !important; }

    .urdu-font { 
        font-family: 'Noto Nastaliq Urdu', serif; 
        direction: rtl; 
        text-align: right; 
        font-size: 20px; 
        color: #1b5e20; 
        background: #ffffff; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1); 
        margin-bottom: 10px; 
        border-right: 5px solid #2e7d32; 
    }
    
    .user-msg { 
        font-family: 'Noto Nastaliq Urdu', serif; 
        direction: rtl; 
        text-align: left; 
        background: #f1f8e9; 
        padding: 10px; 
        border-radius: 10px; 
        margin-bottom: 5px; 
        color: #2e7d32; 
    }

    .header-box { 
        background: #2e7d32; 
        padding: 20px; 
        border-radius: 0 0 20px 20px; 
        color: white; 
        text-align: center; 
        margin-top: -60px; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2316/2316334.png", width=70)
    st.title("کیسان مینو")
    lang = st.selectbox("زبان چنیں", ["Urdu (اردو)", "Siraiki (سرائیکی)", "English"])
    menu = st.radio("آپشنز", ["💬 چیٹ", "📸 کراپ ڈاکٹر", "🧪 کھاد ایڈوائزر", "💰 منڈی ریٹ"])
    if st.button("🔄 نئی چیٹ"):
        st.session_state.messages = []
        st.session_state.processed_id = None
        st.rerun()

st.markdown("<div class='header-box'><h1>🚜 کسان دوست ایکسپرٹ</h1></div>", unsafe_allow_html=True)

# --- 5. AI Logic ---
def get_ai_response(prompt):
    sys_prompt = f"You are a professional Agri-Expert from Pakistan. Respond ONLY in {lang} script. No Chinese, No Roman Urdu, No Hindi words like 'dhanyawad'. Use 'Assalam-o-Alaikum' and 'Shukriya'."
    messages = [{"role": "system", "content": sys_prompt}]
    messages.extend(st.session_state.messages[-5:])
    messages.append({"role": "user", "content": prompt})
    
    try:
        chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
        return chat.choices[0].message.content
    except: return "معذرت، نیٹ ورک کا مسئلہ ہے۔"

# --- 6. MENU FEATURES ---

if menu == "💬 چیٹ":
    for m in st.session_state.messages:
        cls = "user-msg" if m["role"] == "user" else "urdu-font"
        st.markdown(f"<div class='{cls}'>{m['content']}</div>", unsafe_allow_html=True)

    st.write("---")
    c1, c2 = st.columns([1, 4])
    with c1:
        audio_data = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='chat_mic')
    with c2:
        u_text = st.text_input("سوال لکھیں...", label_visibility="collapsed")
        send = st.button("بھیجیں")

    input_text = ""
    if audio_data and audio_data.get('id') != st.session_state.processed_id:
        st.session_state.processed_id = audio_data.get('id')
        transcription = client.audio.transcriptions.create(file=("audio.wav", audio_data['bytes']), model="whisper-large-v3", language="ur")
        input_text = transcription.text
    elif send and u_text:
        input_text = u_text

    if input_text:
        ans = get_ai_response(input_text)
        st.session_state.messages.append({"role": "user", "content": input_text})
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()

elif menu == "📸 کراپ ڈاکٹر":
    st.subheader("فصل کی بیماری چیک کریں")
    file = st.file_uploader("تصویر اپ لوڈ کریں (.jpg, .png, .jfif)", type=["jpg", "png", "jpeg", "jfif"])
    if file:
        img = Image.open(file)
        st.image(img, caption="آپ کی فصل", use_container_width=True)
        if st.button("ڈاکٹر سے مشورہ لیں"):
            with st.spinner("معائنہ ہو رہا ہے..."):
                # Jawab ab tasveer ke neeche aayega
                ans = get_ai_response("Analyze this crop image and give cure in Urdu.")
                st.markdown(f"<div class='urdu-font'>{ans}</div>", unsafe_allow_html=True)
                play_audio(ans)

elif menu == "🧪 کھاد ایڈوائزر":
    st.subheader("کھاد کا مشورہ")
    q = st.text_input("اپنی زمین یا فصل کے بارے میں لکھیں:")
    if st.button("پوچھیں"):
        ans = get_ai_response(q)
        st.markdown(f"<div class='urdu-font'>{ans}</div>", unsafe_allow_html=True)
        play_audio(ans)

elif menu == "💰 منڈی ریٹ":
    st.subheader("تازہ ترین منڈی ریٹ")
    crop = st.text_input("فصل کا نام:")
    if st.button("ریٹ چیک کریں"):
        ans = get_ai_response(f"Current mandi rates for {crop} in Pakistan.")
        st.markdown(f"<div class='urdu-font'>{ans}</div>", unsafe_allow_html=True)
        play_audio(ans)
