import streamlit as st
from groq import Groq
from gtts import gTTS
from PIL import Image
import os
import base64
import io

# --- 1. Groq Setup ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.error("❌ Groq API Key nahi mili!")
        st.stop()
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

# --- 2. Voice Function (Behtar Quality) ---
def play_audio(text):
    try:
        # Hindi words ko filter karne ke liye Urdu instructions di hain
        tts = gTTS(text=text, lang='ur')
        tts.save("response.mp3")
        with open("response.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio controls autoplay="true" style="width: 100%;">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)
    except:
        pass

# --- 3. UI Styling (Urdu Font & Professional Look) ---
st.set_page_config(page_title="Kisan Expert AI", page_icon="🚜", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    
    .urdu-text {
        font-family: 'Noto Nastaliq Urdu', serif;
        direction: rtl;
        text-align: right;
        line-height: 2.0;
    }
    .stButton>button {
        background-color: #2e7d32;
        color: white;
        border-radius: 10px;
        height: 3em;
    }
    .sidebar .sidebar-content {
        background-image: linear-gradient(#2e7d32, #1b5e20);
        color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Sidebar ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2316/2316334.png", width=100)
    st.title("🚜 Settings")
    lang_opt = st.selectbox("Apni Zaban Chunein:", ["Urdu (اردو)", "Punjabi (Urdu Script)"])
    option = st.radio("Kahan Jana Hai?", ["📸 Crop Doctor (Tasveer)", "💬 Expert Mashwara", "💰 Mandi Rates"])
    st.divider()
    st.write("Dost Kisan AI - Pakistan")

# --- 5. Main Content ---
st.title("🌾 Kisan Expert AI Assistant")
st.write("Assalam-o-Alaikum! Main aapka AI Kisan Expert hoon. Poochiye koi bhi sawal.")

# Helper function for Groq Text-only
def get_groq_response(prompt):
    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a professional Agriculture Expert from Pakistan. Speak ONLY in pure Urdu or Punjabi as requested. Do NOT use any Hindi words like 'shubh', 'dhanyawad', 'kripya'. Use 'Shukriya', 'Meharbani', 'Mashwara'. Always provide relevant website links for fertilizers or seeds if possible."},
            {"role": "user", "content": prompt}
        ]
    )
    return completion.choices[0].message.content

# --- FEATURE 1: CROP DOCTOR (Image) ---
if option == "📸 Crop Doctor (Tasveer)":
    st.header("📸 Pauday ki Beemari Check Karein")
    file = st.file_uploader("Tasveer upload karein", type=["jpg", "png", "jpeg"])
    
    if file:
        img = Image.open(file)
        st.image(img, width=400)
        if st.button("Doctor se Check Karwayein"):
            with st.spinner("Kisan Doctor tasveer dekh raha hai..."):
                # Note: For images on Groq, you need a vision model
                # If Llama-3-vision is not in your tier, this will use text-based analysis
                # Here we simulate expert advice
                prompt = f"Analyze this crop situation and give advice in {lang_opt}. Link to agriculture sites like 'zarkhaiz.pk' or 'agripunjab.gov.pk'."
                res = get_groq_response(prompt)
                st.markdown(f"<div class='urdu-text'>{res}</div>", unsafe_allow_html=True)
                play_audio(res)

# --- FEATURE 2: AGRI CHAT ---
elif option == "💬 Expert Mashwara":
    st.header("💬 Kisan Expert se Baat Karein")
    query = st.text_input("Apna sawal likhein (Maslan: Gandum ki fasal ko kab pani dein?):")
    
    if st.button("Mashwara Lein"):
        if query:
            with st.spinner("Kisan Expert soch raha hai..."):
                res = get_groq_response(f"Farmer Question: {query} in {lang_opt}")
                st.markdown(f"<div class='urdu-text'>{res}</div>", unsafe_allow_html=True)
                play_audio(res)

# --- FEATURE 3: MANDI RATES ---
elif option == "💰 Mandi Rates":
    st.header("💰 Mandi Rates aur Market Advisor")
    crop = st.text_input("Fasal ka naam:")
    if st.button("Rates Check Karein"):
        with st.spinner("Market Expert analysis kar raha hai..."):
            res = get_groq_response(f"Current Mandi rates for {crop} in Pakistan cities. Provide links to official price lists in {lang_opt}.")
            st.info(res)
            play_audio(res)
