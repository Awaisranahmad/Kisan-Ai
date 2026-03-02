import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
from streamlit_mic_recorder import mic_recorder
from PIL import Image

# --- 1. Connection Setup ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_id" not in st.session_state:
    st.session_state.processed_id = None

# --- 2. Male Voice Output (Mardana Awaz) ---
def play_audio(text):
    try:
        # Table aur special symbols ko hata kar voice saaf karna
        clean_text = text.replace('|', ' ').replace('-', ' ').replace('#', ' ')
        # gTTS Urdu language settings for natural male-like tone
        tts = gTTS(text=clean_text[:250], lang='ur', slow=False)
        tts.save("expert_voice.mp3")
        with open("expert_voice.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <div style="background: #e8f5e9; padding: 15px; border-radius: 15px; border: 2px solid #2e7d32; margin-top: 15px; text-align: center;">
                    <p style="color: #2e7d32; font-weight: bold; margin-bottom: 8px;">🔊 جواب سننے کے لیے پلے دبائیں</p>
                    <audio controls style="width: 100%; height: 40px;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                </div>
                """
            st.markdown(md, unsafe_allow_html=True)
    except: pass

# --- 3. UI Styling (Wahi Layout) ---
st.set_page_config(page_title="Kisan Expert Pro", page_icon="🚜", layout="centered")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    
    .stApp { background-color: #f9fbf9; }
    [data-testid="stSidebar"] { background-color: #e8f5e9 !important; border-right: 2px solid #c8e6c9; }
    
    .urdu-card { 
        font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: right; 
        font-size: 20px; color: #1b5e20; background: #ffffff; padding: 20px; 
        border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
        margin-bottom: 15px; border-right: 8px solid #2e7d32; line-height: 2.2;
    }
    
    .user-bubble { 
        font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: left; 
        background: #DCF8C6; padding: 12px 18px; border-radius: 15px 15px 0 15px; 
        margin-bottom: 10px; color: #075E54; display: inline-block; float: left; width: fit-content;
    }

    .stMarkdown table { 
        width: 100%; direction: rtl; border-collapse: collapse; border-radius: 10px; overflow: hidden; 
        box-shadow: 0 2px 10px rgba(0,0,0,0.1); margin: 20px 0;
    }
    .stMarkdown th { background-color: #2e7d32 !important; color: white !important; padding: 12px !important; text-align: center !important; }
    .stMarkdown td { background-color: white !important; color: #333 !important; padding: 10px !important; text-align: center !important; border-bottom: 1px solid #eee !important; }

    .header-container { background: #2e7d32; padding: 30px; border-radius: 0 0 30px 30px; color: white; text-align: center; margin-top: -60px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2316/2316334.png", width=80)
    st.title("کیسان مینو")
    menu = st.radio("آپشن منتخب کریں:", ["💬 چیٹ", "📸 کراپ ڈاکٹر", "🧪 کھاد ایڈوائزر", "💰 منڈی ریٹ"])
    st.divider()
    if st.button("🔄 نئی چیٹ شروع کریں"):
        st.session_state.messages = []
        st.session_state.processed_id = None
        st.rerun()

st.markdown("<div class='header-container'><h1>🚜 کسان دوست ایکسپرٹ</h1><p>آپ کی فصل، ہماری فکر</p></div>", unsafe_allow_html=True)

# --- 5. AI Logic (Strict One-Script Enforcement) ---
def get_ai_response(prompt, is_mandi=False):
    sys_prompt = (
        "You are a professional Agriculture Expert from Pakistan. Respond ONLY in Urdu script. "
        "Strictly DO NOT use Hindi, Chinese, or English words in the sentences. "
        "Do not use words like 'dhanyawad', 'kripya', or 'shubh'. Use 'Assalam-o-Alaikum' and 'Shukriya'. "
        "If you mention technical terms, write them in Urdu script (e.g., Nitrogen as نائٹروجن)."
    )
    if is_mandi:
        sys_prompt += " Provide a clean Markdown Table for city rates with columns: City (شہر), Min Rate (کم سے کم ریٹ), Max Rate (زیادہ سے زیادہ ریٹ)."
    
    messages = [{"role": "system", "content": sys_prompt}]
    messages.extend(st.session_state.messages[-3:])
    messages.append({"role": "user", "content": prompt})
    
    try:
        chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
        return chat.choices[0].message.content
    except: return "نیٹ ورک کا مسئلہ ہے، دوبارہ کوشش کریں۔"

# --- 6. Navigation Logic ---

if menu == "💬 چیٹ":
    for m in st.session_state.messages:
        if m["role"] == "user":
            st.markdown(f"<div style='overflow: auto;'><div class='user-bubble'>{m['content']}</div></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='urdu-card'>{m['content']}</div>", unsafe_allow_html=True)
            if m == st.session_state.messages[-1]:
                play_audio(m["content"])

    st.write("---")
    st.subheader("🎤 اپنا سوال پوچھیں")
    c1, c2 = st.columns([1, 4])
    with c1:
        audio = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='chat_mic')
    with c2:
        u_text = st.text_input("یہاں لکھیں...", key="u_input", label_visibility="collapsed")
        send = st.button("بھیجیں")

    q = ""
    if audio and audio.get('id') != st.session_state.processed_id:
        st.session_state.processed_id = audio.get('id')
        with st.spinner("سن رہا ہوں..."):
            q = client.audio.transcriptions.create(file=("a.wav", audio['bytes']), model="whisper-large-v3", language="ur").text
    elif send and u_text: q = u_text

    if q:
        ans = get_ai_response(q)
        st.session_state.messages.append({"role": "user", "content": q})
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()

elif menu == "📸 کراپ ڈاکٹر":
    st.subheader("فصل کی بیماری کا معائنہ")
    file = st.file_uploader("تصویر اپ لوڈ کریں", type=["jpg", "png", "jpeg", "jfif"])
    if file:
        st.image(file, use_container_width=True)
        if st.button("ڈاکٹر سے مشورہ لیں"):
            ans = get_ai_response("Analyze this plant disease and give treatment in Urdu.")
            st.markdown(f"<div class='urdu-card'>{ans}</div>", unsafe_allow_html=True)
            play_audio(ans)

elif menu == "🧪 کھاد ایڈوائزر":
    st.subheader("کھاد کا بہترین استعمال")
    q_khaad = st.text_input("اپنی فصل اور زمین کی قسم لکھیں:")
    if st.button("مشورہ لیں"):
        ans = get_ai_response(q_khaad)
        st.markdown(f"<div class='urdu-card'>{ans}</div>", unsafe_allow_html=True)
        play_audio(ans)

elif menu == "💰 منڈی ریٹ":
    st.subheader("تازہ ترین منڈی ریٹ لسٹ")
    crop = st.text_input("فصل کا نام لکھیں:")
    if st.button("ریٹ لسٹ حاصل کریں"):
        ans = get_ai_response(f"Current market rates for {crop} in Pakistan cities", is_mandi=True)
        st.markdown(ans, unsafe_allow_html=True)
        play_audio("یہ آپ کے مطلوبہ ریٹ کی تفصیل ہے۔")
