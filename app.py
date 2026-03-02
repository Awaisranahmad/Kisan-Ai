import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os
import base64

# --- 1. API Key Setup (Streamlit Secrets) ---
def setup_ai():
    try:
        # Check if key exists in Streamlit Secrets
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            # Using 'gemini-1.5-flash' which is the most stable for images
            model = genai.GenerativeModel('gemini-1.5-flash')
            return model
        else:
            st.error("❌ API Key 'GEMINI_API_KEY' not found in Streamlit Secrets!")
            return None
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return None

model = setup_ai()

# --- 2. Audio Function (AI to speak Urdu/Punjabi) ---
def play_audio(text, lang='ur'):
    try:
        tts = gTTS(text=text, lang=lang)
        tts.save("response.mp3")
        with open("response.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <audio controls autoplay="true">
                <source src="data:audio/mp3;base64,{b64}" type="audio/mp3">
                </audio>
                """
            st.markdown(md, unsafe_allow_html=True)
    except Exception as e:
        st.warning("Audio generate nahi ho saki, lekin text niche maujood hai.")

# --- 3. UI Design ---
st.set_page_config(page_title="Kisan Dost AI", page_icon="🚜", layout="centered")

# Custom CSS for better look
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #2e7d32; color: white; }
    </style>
    """, unsafe_allow_html=True)

st.title("🚜 Kisan Dost: AI Assistant")
st.write("Sawal puchein, photo dikhayein, ya mandi ke rates jaan'ne ke liye niche options use karein.")

# Language Selection Sidebar
st.sidebar.title("Settings")
lang_opt = st.sidebar.selectbox("Apni Zaban Chunein (Select Language):", 
                                ["Urdu (اردو)", "Punjabi (پنجابی)", "English"])

# Navigation Menu
option = st.sidebar.radio("Main Menu", ["📸 Crop Doctor", "💬 Agri Chat", "💰 Mandi Rates"])

st.divider()

# --- FEATURE 1: CROP DOCTOR (Image) ---
if option == "📸 Crop Doctor":
    st.header("Crop Disease Identifier")
    st.write("Fasal ya pauday ke kharab hissay ki tasveer upload karein.")
    
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file and model:
        img = Image.open(uploaded_file)
        st.image(img, caption="Fasal ki photo", use_container_width=True)
        
        if st.button("Beemari Check Karein"):
            with st.spinner("AI analysis kar raha hai..."):
                prompt = f"Identify the disease in this plant image and suggest organic/chemical cures in simple {lang_opt} for a farmer."
                response = model.generate_content([prompt, img])
                jawab = response.text
                st.success(jawab)
                play_audio(jawab)

# --- FEATURE 2: AGRI CHAT (Text/Voice) ---
elif option == "💬 Agri Chat":
    st.header("Agricultural Expert Advice")
    user_query = st.text_input("Apna sawal yahan likhein (e.g. Faslon ko paani kab dein?):")
    
    if st.button("Jawab Lein") and model:
        if user_query:
            with st.spinner("Soch raha hoon..."):
                prompt = f"Act as an expert agricultural consultant. Answer this question: '{user_query}' in simple, helpful {lang_opt}."
                response = model.generate_content(user_query)
                jawab = response.text
                st.markdown(f"**Jawab:** {jawab}")
                play_audio(jawab)
        else:
            st.warning("Pehle apna sawal likhein!")

# --- FEATURE 3: MANDI RATES ---
elif option == "💰 Mandi Rates":
    st.header("Mandi Price Advisor")
    crop_name = st.text_input("Fasal ka naam likhein (e.g. Wheat, Rice, Cotton):")
    
    if st.button("Check Market Trends") and model:
        with st.spinner("Market data check ho raha hai..."):
            prompt = f"Tell current market price trends and selling advice for {crop_name} in Pakistan in {lang_opt}."
            response = model.generate_content(prompt)
            jawab = response.text
            st.info(jawab)
            play_audio(jawab)

st.sidebar.divider()
st.sidebar.write("Developed for Farmers of Pakistan 🇵🇰")
