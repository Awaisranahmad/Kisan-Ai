import streamlit as st
from groq import Groq
import asyncio
import edge_tts
import base64
import io
from streamlit_mic_recorder import mic_recorder

# --- 1. Connection ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_id" not in st.session_state:
    st.session_state.processed_id = None

# --- 2. Guaranteed Male Voice (In-Memory) ---
async def get_male_audio_binary(text):
    VOICE = "ur-PK-ImranNeural"
    clean_text = text.replace('|', ' ').replace('-', ' ').replace('#', ' ').strip()
    
    if not clean_text:
        return None
        
    communicate = edge_tts.Communicate(clean_text[:250], VOICE)
    audio_data = b""
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_data += chunk["data"]
    return audio_data

def play_audio(text):
    try:
        # Audio ko memory mein generate karna
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        audio_binary = loop.run_until_complete(get_male_audio_binary(text))
        
        if audio_binary:
            b64 = base64.b64encode(audio_binary).decode()
            md = f"""
                <div style="background: #f1f8e9; padding: 15px; border-radius: 15px; border: 2px solid #2e7d32; margin-top: 15px; text-align: center;">
                    <p style="color: #2e7d32; font-weight: bold;">👨🏻‍🌾 ماہر کیسان کی آواز (مردانہ)</p>
                    <audio controls autoplay style="width: 100%;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                </div>
                """
            st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Voice Error: {e}")

# --- 3. UI Styling ---
st.set_page_config(page_title="Kisan Expert Pro", page_icon="🚜")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    .urdu-card { 
        font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: right; 
        font-size: 20px; color: #1b5e20; background: #ffffff; padding: 20px; 
        border-radius: 12px; border-right: 8px solid #2e7d32; line-height: 2.2; margin-bottom: 10px;
    }
    .user-bubble { 
        font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: left; 
        background: #DCF8C6; padding: 12px; border-radius: 15px; color: #075E54;
    }
    .header-box { background: #2e7d32; padding: 20px; border-radius: 0 0 20px 20px; color: white; text-align: center; margin-top: -65px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Main App ---
st.markdown("<div class='header-box'><h1>🚜 کسان دوست ایکسپرٹ</h1></div>", unsafe_allow_html=True)

menu = st.sidebar.radio("کیسان مینو", ["💬 چیٹ", "💰 منڈی ریٹ"])

def get_ai_response(prompt, is_mandi=False):
    sys_prompt = "You are a professional Agri-Expert. Respond ONLY in Urdu script. NO Hindi words. Greeting: 'Assalam-o-Alaikum'."
    if is_mandi: sys_prompt += " Provide a Markdown Table for rates."
    
    try:
        chat = client.chat.completions.create(model="llama-3.3-70b-versatile", 
                                            messages=[{"role": "system", "content": sys_prompt},
                                                      {"role": "user", "content": prompt}])
        return chat.choices[0].message.content
    except: return "نیٹ ورک کا مسئلہ ہے۔"

if menu == "💬 چیٹ":
    for m in st.session_state.messages:
        role_style = "user-bubble" if m["role"] == "user" else "urdu-card"
        st.markdown(f"<div class='{role_style}'>{m['content']}</div>", unsafe_allow_html=True)

    st.write("---")
    audio_in = mic_recorder(start_prompt="🎤 بات کریں", stop_prompt="⏹️ روکیں", key='mic')
    
    if audio_in and audio_in.get('id') != st.session_state.processed_id:
        st.session_state.processed_id = audio_in.get('id')
        user_q = client.audio.transcriptions.create(file=("a.wav", audio_in['bytes']), model="whisper-large-v3", language="ur").text
        ans = get_ai_response(user_q)
        st.session_state.messages.append({"role": "user", "content": user_q})
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        play_audio(st.session_state.messages[-1]["content"])

elif menu == "💰 منڈی ریٹ":
    crop = st.text_input("فصل کا نام لکھیں:")
    if st.button("ریٹ دیکھیں"):
        ans = get_ai_response(f"Rates for {crop} in Pakistan", is_mandi=True)
        st.markdown(ans)
        play_audio("یہ رہی آپ کی مطلوبہ ریٹ لسٹ")
