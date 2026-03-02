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

# --- 2. Male-Style Voice Output ---
def play_audio(text):
    try:
        # Hindi words filter out karne ke liye clean text
        clean_text = text.replace('|', ' ').replace('-', ' ')
        tts = gTTS(text=clean_text, lang='ur', slow=False)
        tts.save("expert_voice.mp3")
        with open("expert_voice.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <div style="background: #f1f8e9; padding: 10px; border-radius: 10px; border: 1px solid #2e7d32; margin: 10px 0; text-align: center;">
                    <p style="color: #2e7d32; font-weight: bold;">🔊 جواب سننے کے لیے پلے دبائیں</p>
                    <audio controls style="width: 100%;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                </div>
                """
            st.markdown(md, unsafe_allow_html=True)
    except: pass

# --- 3. UI Styling ---
st.set_page_config(page_title="Kisan Expert Pro", page_icon="🚜")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    [data-testid="stSidebar"] { background-color: #e8f5e9 !important; }
    .urdu-font { 
        font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: right; 
        font-size: 20px; color: #1b5e20; background: #ffffff; padding: 15px; 
        border-radius: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); 
        margin-bottom: 10px; border-right: 5px solid #2e7d32; 
    }
    .header-box { background: #2e7d32; padding: 20px; border-radius: 0 0 20px 20px; color: white; text-align: center; margin-top: -60px; }
    /* Table Styling */
    table { width: 100%; direction: rtl; border-collapse: collapse; margin: 10px 0; }
    th { background-color: #2e7d32; color: white; padding: 10px; }
    td { border: 1px solid #ddd; padding: 8px; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar ---
with st.sidebar:
    st.header("کیسان مینو")
    menu = st.radio("آپشنز", ["💬 چیٹ", "📸 کراپ ڈاکٹر", "🧪 کھاد ایڈوائزر", "💰 منڈی ریٹ"])
    st.write("---")
    st.markdown("### 🔗 اہم لنکس")
    st.markdown("[بیج کے ریٹ (PARC)](http://www.parc.gov.pk/)")
    if st.button("🔄 نئی چیٹ"):
        st.session_state.messages = []
        st.rerun()

st.markdown("<div class='header-box'><h1>🚜 کسان دوست ایکسپرٹ</h1></div>", unsafe_allow_html=True)

# --- 5. AI Logic (Table Support) ---
def get_ai_response(prompt, is_mandi=False):
    sys_prompt = (
        "You are a professional Agri-Expert in Pakistan. Respond ONLY in Urdu script. "
        "Strictly NO Hindi/English words. "
    )
    if is_mandi:
        sys_prompt += "When asked for rates, ALWAYS provide a Markdown TABLE with columns: City (شہر), Min Price (کم سے کم ریٹ), Max Price (زیادہ سے زیادہ ریٹ). Use current estimated market prices per 40kg (Mund)."
    
    messages = [{"role": "system", "content": sys_prompt}]
    messages.extend(st.session_state.messages[-3:])
    messages.append({"role": "user", "content": prompt})
    
    try:
        chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
        return chat.choices[0].message.content
    except: return "معذرت، نیٹ ورک کا مسئلہ ہے۔"

# --- 6. Features ---

if menu == "💬 چیٹ":
    for m in st.session_state.messages:
        role_class = "urdu-font" if m["role"] == "assistant" else ""
        st.markdown(f"<div class='{role_class}'>{m['content']}</div>", unsafe_allow_html=True)
    
    st.write("---")
    c1, c2 = st.columns([1, 4])
    with c1:
        audio = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='mic')
    with c2:
        text_in = st.text_input("سوال لکھیں...")
        send = st.button("بھیجیں")

    q = ""
    if audio and audio.get('id') != st.session_state.processed_id:
        st.session_state.processed_id = audio.get('id')
        q = client.audio.transcriptions.create(file=("a.wav", audio['bytes']), model="whisper-large-v3", language="ur").text
    elif send and text_in: q = text_in

    if q:
        ans = get_ai_response(q)
        st.session_state.messages.append({"role": "user", "content": q})
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()

elif menu == "💰 منڈی ریٹ":
    st.subheader("تازہ ترین منڈی ریٹ (فی 40 کلو)")
    
    crop = st.text_input("فصل کا نام لکھیں (مثلاً گندم، کپاس):")
    if st.button("ریٹ کی لسٹ دیکھیں"):
        with st.spinner("ریٹ تلاش کیے جا رہے ہیں..."):
            ans = get_ai_response(f"Current market rates for {crop} in different cities of Pakistan.", is_mandi=True)
            st.markdown(ans, unsafe_allow_html=True) # Table rendering
            play_audio("یہ آپ کی مطلوبہ فصل کے تازہ ترین منڈی ریٹ کی لسٹ ہے۔")

# (Baqi sections wahi rahenge...)
