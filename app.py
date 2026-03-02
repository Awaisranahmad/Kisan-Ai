import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
from streamlit_mic_recorder import mic_recorder
from PIL import Image

# --- 1. Connection ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_id" not in st.session_state:
    st.session_state.processed_id = None

# --- 2. Male-Like Voice Output (Manual Play) ---
def play_audio(text):
    try:
        # 'ur' language with custom settings
        tts = gTTS(text=text, lang='ur', slow=False)
        tts.save("expert_voice.mp3")
        with open("expert_voice.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <div style="background: #f1f8e9; padding: 10px; border-radius: 10px; border: 1px solid #2e7d32; margin: 10px 0; text-align: center;">
                    <p style="color: #2e7d32; font-weight: bold; margin-bottom: 5px;">🔊 جواب سننے کے لیے پلے بٹن دبائیں (Mardana Awaz)</p>
                    <audio controls style="width: 100%;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                </div>
                """
            st.markdown(md, unsafe_allow_html=True)
    except: pass

# --- 3. UI Styling (Light Green Sidebar) ---
st.set_page_config(page_title="Kisan Expert Pro", page_icon="🚜")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    [data-testid="stSidebar"] { background-color: #e8f5e9 !important; }
    [data-testid="stSidebar"] * { color: #1b5e20 !important; }
    .urdu-font { 
        font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: right; 
        font-size: 22px; color: #1b5e20; background: #ffffff; padding: 18px; 
        border-radius: 12px; box-shadow: 2px 2px 8px rgba(0,0,0,0.1); 
        margin-bottom: 10px; border-right: 8px solid #2e7d32; 
    }
    .user-msg { 
        font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: left; 
        background: #f1f8e9; padding: 12px; border-radius: 10px; 
        margin-bottom: 10px; color: #2e7d32; border-left: 5px solid #2e7d32;
    }
    .header-box { background: #2e7d32; padding: 25px; border-radius: 0 0 25px 25px; color: white; text-align: center; margin-top: -65px; }
    .link-style { color: #2e7d32; text-decoration: underline; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2316/2316334.png", width=70)
    st.title("کیسان مینو")
    lang_choice = st.selectbox("زبان", ["Urdu (اردو)", "Siraiki (سرائیکی)", "English"])
    menu = st.radio("آپشنز", ["💬 چیٹ", "📸 کراپ ڈاکٹر", "🧪 کھاد ایڈوائزر", "💰 منڈی ریٹ"])
    st.write("---")
    st.markdown("### 🔗 اہم لنکس")
    st.markdown("[بیج کے ریٹ (PARC)](http://www.parc.gov.pk/)")
    st.markdown("[کھاد کے ریٹ (Engro)](https://www.engrofertilizers.com/)")
    if st.button("🔄 نئی چیٹ"):
        st.session_state.messages = []
        st.session_state.processed_id = None
        st.rerun()

st.markdown("<div class='header-box'><h1>🚜 کسان دوست ایکسپرٹ</h1></div>", unsafe_allow_html=True)

# --- 5. AI Logic (Zero Tolerance for Non-Urdu) ---
def get_ai_response(prompt):
    sys_prompt = (
        f"You are a professional Pakistani Agriculture Expert. Respond ONLY in {lang_choice} script. "
        "Strictly DO NOT use any Hindi words (like 'dhanyawad', 'kripya', 'shubh'). "
        "DO NOT use English alphabets in sentences. "
        "Use pure Pakistani Urdu terminology. Example: Instead of 'elements', use 'ajza'. "
        "Include links to 'parc.gov.pk' or 'engrofertilizers.com' if necessary."
    )
    
    messages = [{"role": "system", "content": sys_prompt}]
    messages.extend(st.session_state.messages[-3:])
    messages.append({"role": "user", "content": prompt})
    
    try:
        chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
        return chat.choices[0].message.content
    except: return "معذرت، نیٹ ورک کا مسئلہ ہے۔"

# --- 6. Navigating Features ---

if menu == "💬 چیٹ":
    for m in st.session_state.messages:
        cls = "user-msg" if m["role"] == "user" else "urdu-font"
        st.markdown(f"<div class='{cls}'>{m['content']}</div>", unsafe_allow_html=True)
        if m["role"] == "assistant" and m == st.session_state.messages[-1]:
            play_audio(m["content"])

    st.write("---")
    st.subheader("🎤 اپنا سوال پوچھیں")
    c1, c2 = st.columns([1, 4])
    with c1:
        audio_in = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='main_mic')
    with c2:
        u_text = st.text_input("یہاں لکھیں...", key="text_in", label_visibility="collapsed")
        send = st.button("بھیجیں")

    q = ""
    if audio_in and audio_in.get('id') != st.session_state.processed_id:
        st.session_state.processed_id = audio_in.get('id')
        trans = client.audio.transcriptions.create(file=("audio.wav", audio_in['bytes']), model="whisper-large-v3", language="ur")
        q = trans.text
    elif send and u_text:
        q = u_text

    if q:
        ans = get_ai_response(q)
        st.session_state.messages.append({"role": "user", "content": q})
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()

elif menu == "📸 کراپ ڈاکٹر":
    st.subheader("فصل کا معائنہ")
    file = st.file_uploader("تصویر اپ لوڈ کریں", type=["jpg", "png", "jpeg", "jfif"])
    if file:
        st.image(file, use_container_width=True)
        if st.button("ڈاکٹر سے مشورہ لیں"):
            ans = get_ai_response("Analyze this plant image and provide cure in pure Urdu.")
            st.markdown(f"<div class='urdu-font'>{ans}</div>", unsafe_allow_html=True)
            play_audio(ans)

elif menu == "🧪 کھاد ایڈوائزر":
    st.subheader("کھاد کا مشورہ")
    f_q = st.text_input("اپنی زمین کا حال لکھیں:")
    if st.button("پوچھیں"):
        ans = get_ai_response(f_q)
        st.markdown(f"<div class='urdu-font'>{ans}</div>", unsafe_allow_html=True)
        play_audio(ans)

elif menu == "💰 منڈی ریٹ":
    st.subheader("منڈی ریٹ")
    crop = st.text_input("فصل کا نام:")
    if st.button("ریٹ دیکھیں"):
        ans = get_ai_response(f"Mandi rates for {crop} in Pakistan.")
        st.markdown(f"<div class='urdu-font'>{ans}</div>", unsafe_allow_html=True)
        play_audio(ans)
