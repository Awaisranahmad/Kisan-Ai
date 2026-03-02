import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
import os
from streamlit_mic_recorder import mic_recorder
from PIL import Image

# --- 1. Connection Setup ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_id" not in st.session_state:
    st.session_state.processed_id = None

# --- 2. Voice Output Function ---
def play_audio(text):
    try:
        clean_text = text.replace('|', ' ').replace('-', ' ').replace('#', ' ').replace('*', ' ')
        tts = gTTS(text=clean_text[:300], lang='ur', slow=False)
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

# --- 3. Image Processing ---
def process_image_to_b64(uploaded_file):
    image = Image.open(uploaded_file)
    if image.mode != "RGB":
        image = image.convert("RGB")
    # Image size kam karna taake model jaldi process kare
    image.thumbnail((800, 800))
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=85)
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# --- 4. UI Styling ---
st.set_page_config(page_title="Kisan Expert Pro", page_icon="🚜", layout="centered")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    .stApp { background-color: #f9fbf9; }
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
    .header-container { background: #2e7d32; padding: 30px; border-radius: 0 0 30px 30px; color: white; text-align: center; margin-top: -60px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2316/2316334.png", width=80)
    st.title("کیسان مینو")
    menu = st.radio("آپشن منتخب کریں:", ["💬 چیٹ", "📸 کراپ ڈاکٹر", "🧪 کھاد ایڈوائزر", "💰 منڈی ریٹ"])
    if st.button("🔄 نئی چیٹ شروع کریں"):
        st.session_state.messages = []
        st.session_state.processed_id = None
        st.rerun()

st.markdown("<div class='header-container'><h1>🚜 کسان دوست ایکسپرٹ</h1><p>خالص اردو اور مکمل رہنمائی</p></div>", unsafe_allow_html=True)

# --- 6. AI Logic (The Fix) ---
def get_ai_response(prompt, image_b64=None, is_mandi=False):
    # Try multiple models in case one fails
    vision_models = ["llama-3.2-11b-vision-preview", "llama-3.2-90b-vision-preview"]
    text_model = "llama-3.3-70b-versatile"
    
    sys_prompt = "You are a professional Agri-Expert from Pakistan. Respond ONLY in Urdu script. Strictly NO English/Hindi words."
    if is_mandi: sys_prompt += " Provide a Markdown Table for rates."

    # Decide which model to use
    selected_model = vision_models[0] if image_b64 else text_model
    
    messages = [{"role": "system", "content": sys_prompt}]
    
    if image_b64:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
            ]
        })
    else:
        messages.append({"role": "user", "content": prompt})

    try:
        chat = client.chat.completions.create(model=selected_model, messages=messages, timeout=20.0)
        return chat.choices[0].message.content
    except Exception as e:
        # Fallback if first vision model fails
        if image_b64:
            try:
                chat = client.chat.completions.create(model=vision_models[1], messages=messages)
                return chat.choices[0].message.content
            except: pass
        return "معذرت، ابھی سرور پر بوجھ ہے یا انٹرنیٹ کا مسئلہ ہے۔ براہ کرم ایک بار دوبارہ کوشش کریں۔"

# --- 7. Navigation ---
if menu == "💬 چیٹ":
    for m in st.session_state.messages:
        style = "user-bubble" if m["role"] == "user" else "urdu-card"
        st.markdown(f"<div class='{style}'>{m['content']}</div>", unsafe_allow_html=True)

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
            try:
                q = client.audio.transcriptions.create(file=("a.wav", audio['bytes']), model="whisper-large-v3", language="ur").text
            except: st.error("آواز پہچاننے میں مسئلہ ہوا۔")
    elif send and u_text: q = u_text

    if q:
        ans = get_ai_response(q)
        st.session_state.messages.append({"role": "user", "content": q})
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        play_audio(st.session_state.messages[-1]["content"])

elif menu == "📸 کراپ ڈاکٹر":
    st.subheader("بیماری کی تشخیص")
    
    file = st.file_uploader("تصویر اپ لوڈ کریں", type=["jpg", "png", "jpeg", "jfif"])
    if file:
        st.image(file, use_container_width=True)
        if st.button("بیماری چیک کریں"):
            with st.spinner("AI معائنہ کر رہا ہے..."):
                img_b64 = process_image_to_b64(file)
                ans = get_ai_response("Analyze this plant image. Identify the crop, the disease, and give treatment in Urdu.", image_b64=img_b64)
                st.markdown(f"<div class='urdu-card'>{ans}</div>", unsafe_allow_html=True)
                play_audio(ans)

elif menu == "💰 منڈی ریٹ":
    st.subheader("تازہ ترین ریٹ")
    crop = st.text_input("فصل کا نام:")
    if st.button("ریٹ حاصل کریں"):
        ans = get_ai_response(f"Mandi rates for {crop} in Pakistan as a table", is_mandi=True)
        st.markdown(ans)
        play_audio("یہ رہی ریٹ لسٹ")
