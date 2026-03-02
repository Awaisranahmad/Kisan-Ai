import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
from streamlit_mic_recorder import mic_recorder
from PIL import Image

# --- 1. Setup ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_id" not in st.session_state:
    st.session_state.processed_id = None

# --- 2. Male-Style Voice Output (Manual Play) ---
def play_audio(text):
    try:
        # Voice ko mardana touch dene ke liye language settings
        tts = gTTS(text=text, lang='ur', slow=False)
        tts.save("expert_voice.mp3")
        with open("expert_voice.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <div style="background: #f1f8e9; padding: 10px; border-radius: 10px; border: 1px solid #2e7d32; margin: 10px 0; text-align: center;">
                    <p style="color: #2e7d32; font-weight: bold; margin-bottom: 5px;">🔊 Jawab sunne ke liye play dabayein</p>
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
    .user-msg { 
        font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: left; 
        background: #f1f8e9; padding: 10px; border-radius: 10px; 
        margin-bottom: 5px; color: #2e7d32; border-left: 5px solid #2e7d32;
    }
    .header-box { background: #2e7d32; padding: 20px; border-radius: 0 0 20px 20px; color: white; text-align: center; margin-top: -60px; }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2316/2316334.png", width=70)
    st.title("Kisan Menu")
    menu = st.radio("Options", ["💬 Chat", "📸 Crop Doctor", "🧪 Khaad Advisor", "💰 Mandi Rate"])
    st.write("---")
    st.markdown("### 🔗 Links")
    st.markdown("[PARC Rates](http://www.parc.gov.pk/)")
    if st.button("🔄 New Chat"):
        st.session_state.messages = []
        st.session_state.processed_id = None
        st.rerun()

st.markdown("<div class='header-box'><h1>🚜 Kisan Dost Expert</h1></div>", unsafe_allow_html=True)

# --- 5. AI Logic ---
def get_ai_response(prompt, is_mandi=False):
    sys_prompt = "You are a Pakistani Agri-Expert. Use ONLY Urdu script. No Hindi words like 'dhanyawad' or 'shubh'. Only use 'Assalam-o-Alaikum' and 'Shukriya'."
    if is_mandi:
        sys_prompt += " Provide a table for city rates."
    
    messages = [{"role": "system", "content": sys_prompt}]
    messages.extend(st.session_state.messages[-3:])
    messages.append({"role": "user", "content": prompt})
    
    try:
        chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=messages)
        return chat.choices[0].message.content
    except: return "Connection error."

# --- 6. Main Chat Flow ---

if menu == "💬 Chat":
    # Display History
    for m in st.session_state.messages:
        cls = "user-msg" if m["role"] == "user" else "urdu-font"
        st.markdown(f"<div class='{cls}'>{m['content']}</div>", unsafe_allow_html=True)
        if m["role"] == "assistant" and m == st.session_state.messages[-1]:
            play_audio(m["content"])

    st.write("---")
    st.subheader("🎤 Bol kar sawal puchein")
    
    # Voice Input (Stop karte hi send ho jayega)
    audio_data = mic_recorder(start_prompt="Record Karein", stop_prompt="Stop (Send Ho Jayega)", key='voice_mic')

    if audio_data is not None:
        if audio_data.get('id') != st.session_state.processed_id:
            st.session_state.processed_id = audio_data.get('id')
            with st.spinner("Aap ki awaz suni ja rahi hai..."):
                transcription = client.audio.transcriptions.create(
                    file=("audio.wav", audio_data['bytes']),
                    model="whisper-large-v3",
                    language="ur"
                )
                if transcription.text.strip():
                    user_q = transcription.text
                    ans = get_ai_response(user_q)
                    st.session_state.messages.append({"role": "user", "content": user_q})
                    st.session_state.messages.append({"role": "assistant", "content": ans})
                    st.rerun()

    # Manual Text Input (Alternative)
    u_text = st.text_input("Ya yahan likhein...", key="chat_text")
    if st.button("Bhejein") and u_text:
        ans = get_ai_response(u_text)
        st.session_state.messages.append({"role": "user", "content": u_text})
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()

elif menu == "💰 Mandi Rate":
    st.subheader("Mandi Rates List")
    crop = st.text_input("Fasal ka naam (e.g. Gandum):")
    if st.button("List Dekhein"):
        ans = get_ai_response(f"Rates for {crop} in Pakistan", is_mandi=True)
        st.markdown(ans)
        play_audio("Ye rahi aap ki mandi rates ki list.")
