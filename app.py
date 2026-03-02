import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os
import base64

# --- 1. API Key Setup ---
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error("API Key Missing!")

# --- 2. Audio Function (Jawab Sunne Ke Liye) ---
def play_audio(text, lang='ur'):
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

# --- 3. UI Layout ---
st.set_page_config(page_title="Kisan Dost AI", page_icon="🚜")
st.title("🚜 Kisan Dost: Awaz aur Tasveer wala Assistant")

# Language Selection
lang_opt = st.sidebar.selectbox("Apni Zaban Chunein / اپنی زبان منتخب کریں", 
                                ["Urdu (اردو)", "Punjabi (پنجابی)", "English"])

st.divider()

# --- Feature 1: Image Analysis (Crop Doctor) ---
st.header("📸 Fasal ki Beemari Check Karein")
uploaded_file = st.file_uploader("Pauday ki tasveer upload karein", type=["jpg", "png"])

if uploaded_file:
    img = Image.open(uploaded_file)
    st.image(img, width=300)
    if st.button("Check Karein"):
        with st.spinner("AI dekh raha hai..."):
            prompt = f"Analyze this plant image. Tell the disease and treatment in simple {lang_opt}. If it's Punjabi, use Urdu script but Punjabi words."
            response = model.generate_content([prompt, img])
            jawab = response.text
            st.success(jawab)
            play_audio(jawab) # AI bol kar sunaye ga

st.divider()

# --- Feature 2: Voice/Text Chat ---
st.header("💬 Sawal Puchein (Bol kar ya Likh kar)")
user_input = st.text_input("Yahan apna sawal likhein ya bolen:")

if st.button("Jawab Lein"):
    if user_input:
        with st.spinner("Soch raha hoon..."):
            prompt = f"You are a friendly agriculture expert. Answer this: '{user_input}' in simple {lang_opt}. Make it easy for an uneducated farmer."
            response = model.generate_content(prompt)
            jawab = response.text
            st.write(f"**AI ka Jawab:** {jawab}")
            play_audio(jawab) # AI bol kar sunaye ga
    else:
        st.warning("Pehle kuch likhein!")

# --- Feature 3: Mandi Rates ---
st.sidebar.header("💰 Mandi Rates")
crop = st.sidebar.text_input("Fasal ka naam:")
if st.sidebar.button("Rates Check"):
    prompt = f"Tell current market price trends for {crop} in Pakistan in {lang_opt}."
    response = model.generate_content(prompt)
    st.sidebar.write(response.text)
    play_audio(response.text)
