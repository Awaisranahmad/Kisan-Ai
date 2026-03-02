import streamlit as st
import google.generativeai as genai
from PIL import Image
from gtts import gTTS
import os
import base64

# --- 1. API Key Setup (Streamlit Secrets) ---
def setup_ai():
    try:
        if "GEMINI_API_KEY" in st.secrets:
            api_key = st.secrets["GEMINI_API_KEY"]
            genai.configure(api_key=api_key)
            
            # YAHAN CHANGE HAI: Hum model ko manually 'models/' prefix ke sath call kar rahe hain
            # Ye 'NotFound' error ko fix karne ka standard tarika hai
            model = genai.GenerativeModel(model_name='models/gemini-1.5-flash')
            return model
        else:
            st.error("❌ API Key 'GEMINI_API_KEY' not found in Secrets!")
            return None
    except Exception as e:
        st.error(f"❌ Connection Error: {e}")
        return None

model = setup_ai()

# --- 2. Audio Function ---
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
    except:
        pass

# --- 3. UI Design ---
st.set_page_config(page_title="Kisan Dost AI", page_icon="🚜")
st.title("🚜 Kisan Dost: AI Assistant")

lang_opt = st.sidebar.selectbox("Language / زبان", ["Urdu (اردو)", "Punjabi (پنجابی)", "English"])
option = st.sidebar.radio("Menu", ["📸 Crop Doctor", "💬 Agri Chat", "💰 Mandi Rates"])

st.divider()

# --- LOGIC HANDLING ---
if model:
    if option == "📸 Crop Doctor":
        st.header("Crop Disease Identifier")
        uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"])
        if uploaded_file:
            img = Image.open(uploaded_file)
            st.image(img, use_container_width=True)
            if st.button("Check Karein"):
                with st.spinner("AI analysis..."):
                    # Image input ke liye content list use karna zaroori hai
                    response = model.generate_content(["Identify disease and cure in Urdu.", img])
                    st.success(response.text)
                    play_audio(response.text)

    elif option == "💬 Agri Chat":
        st.header("Agri Advice")
        user_query = st.text_input("Sawal likhein:")
        if st.button("Puchein"):
            if user_query:
                with st.spinner("Thinking..."):
                    # Yahan hum check kar rahe hain ke text query sahi ja rahi hai
                    response = model.generate_content(f"Explain in simple {lang_opt}: {user_query}")
                    st.write(response.text)
                    play_audio(response.text)

    elif option == "💰 Mandi Rates":
        st.header("Mandi Rates")
        crop_name = st.text_input("Fasal:")
        if st.button("Rates"):
            response = model.generate_content(f"Mandi prices for {crop_name} in Pakistan in {lang_opt}")
            st.info(response.text)
            play_audio(response.text)
