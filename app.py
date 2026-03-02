import streamlit as st
from groq import Groq
import asyncio
import edge_tts
import base64
import os
from streamlit_mic_recorder import mic_recorder
from PIL import Image

# --- 1. Connection & Session ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_id" not in st.session_state:
    st.session_state.processed_id = None

# --- 2. Stable Male Voice Logic ---
async def generate_male_voice(text):
    VOICE = "ur-PK-ImranNeural"
    # Text ko saaf karna taake audio error na aaye
    clean_text = text.replace('|', ' ').replace('-', ' ').replace('#', ' ').replace('*', ' ').strip()
    
    if not clean_text:
        return False
        
    communicate = edge_tts.Communicate(clean_text[:250], VOICE)
    await communicate.save("male_expert.mp3")
    return True

def play_audio(text):
    try:
        # Purani file delete karna taake nayi sahi bane
        if os.path.exists("male_expert.mp3"):
            os.remove("male_expert.mp3")
            
        success = asyncio.run(generate_male_voice(text))
        
        if success and os.path.exists("male_expert.mp3"):
            with open("male_expert.mp3", "rb") as f:
                data = f.read()
                b64 = base64.b64encode(data).decode()
                md = f"""
                    <div style="background: #e8f5e9; padding: 15px; border-radius: 15px; border: 2px solid #2e7d32; margin-top: 15px; text-align: center;">
                        <p style="color: #2e7d32; font-weight: bold; margin-bottom: 8px;">👨🏻‍🌾 ماہر کیسان کی آواز سنیں (مردانہ)</p>
                        <audio controls style="width: 100%; height: 40px;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                    </div>
                    """
                st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.warning("Awaz generate karne mein masla hua, lekin aap jawab niche parh sakte hain.")

# --- 3. Premium UI Styling ---
st.set_page_config(page_title="Kisan Expert Pro", page_icon="🚜", layout="centered")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    .stApp { background-color: #f9fbf9; }
    [data-testid="stSidebar"] { background-color: #e8f5e9 !important; }
    .urdu-card { 
        font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: right; 
        font-size: 20px; color: #1b5e20; background: #ffffff; padding: 22px; 
        border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
        margin-bottom: 15px; border-right: 8px solid #2e7d32; line-height: 2.3;
    }
    .user-bubble { 
        font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: left; 
        background: #DCF8C6; padding: 12px 18px; border-radius: 15px 15px 0 15px; 
        margin-bottom: 10px; color: #075E54; display: inline-block; float: left;
    }
    .header-box { background: #2e7d32; padding: 25px; border-radius: 0 0 25px 25px; color: white; text-align: center; margin-top: -65px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2316/2316334.png", width=80)
    st.title("کیسان مینو")
    menu = st.radio("آپشن منتخب کریں:", ["💬 چیٹ", "📸 کراپ ڈاکٹر", "🧪 کھاد ایڈوائزر", "💰 منڈی ریٹ"])
    if st.button("🔄 نئی چیٹ"):
        st.session_state.messages = []
        st.session_state.processed_id = None
        st.rerun()

st.markdown("<div class='header-box'><h1>🚜 کسان دوست ایکسپرٹ</h1><p>خالص اردو اور مردانہ آواز</p></div>", unsafe_allow_html=True)

# --- 5. AI Logic ---
def get_ai_response(prompt, is_mandi=False):
    sys_prompt = "You are a professional Agri-Expert. Respond ONLY in Urdu script. NO Hindi/English/Roman words. Greeting: 'Assalam-o-Alaikum'."
    if is_mandi:
        sys_prompt += " Provide a Markdown Table for rates."
    
    messages = [{"role": "system", "content": sys_prompt}]
    messages.extend(st.session_state.messages[-3:])
    messages.append({"role": "user", "content": prompt})
    
    try:
        chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
        return chat.choices[0].message.content
    except: return "معذرت، نیٹ ورک کا مسئلہ ہے۔"

# --- 6. Features Navigation ---
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
    file = st.file_uploader("تصویر اپ لوڈ کریں", type=["jpg", "png", "jpeg"])
    if file:
        st.image(file, use_container_width=True)
        if st.button("ڈاکٹر سے مشورہ لیں"):
            ans = get_ai_response("Analyze this plant disease and provide treatment in Urdu.")
            st.markdown(f"<div class='urdu-card'>{ans}</div>", unsafe_allow_html=True)
            play_audio(ans)

elif menu == "💰 منڈی ریٹ":
    st.subheader("تازہ ترین منڈی ریٹ")
    crop = st.text_input("فصل کا نام لکھیں:")
    if st.button("ریٹ لسٹ دیکھیں"):
        ans = get_ai_response(f"Current Mandi rates for {crop} in Pakistan cities", is_mandi=True)
        st.markdown(ans)
        play_audio("یہ آپ کے مطلوبہ ریٹ کی تفصیل ہے۔")
