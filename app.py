import streamlit as st
from groq import Groq
from gtts import gTTS
import os
import base64

# --- 1. Groq API Setup ---
try:
    if "GROQ_API_KEY" in st.secrets:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
    else:
        st.error("❌ Groq API Key nahi mili!")
        st.stop()
except Exception as e:
    st.error(f"❌ Connection Error: {e}")
    st.stop()

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
        st.warning("Audio play nahi ho saki.")

# --- 3. UI Design ---
st.set_page_config(page_title="Kisan Dost AI (Groq)", page_icon="🚜")
st.title("🚜 Kisan Dost: Fast AI Assistant")

st.sidebar.title("Settings")
lang_opt = st.sidebar.selectbox("Language / زبان", ["Urdu (اردو)", "Punjabi (پنجابی)", "English"])
option = st.sidebar.radio("Menu", ["💬 Agri Chat", "💰 Mandi Rates"])

st.divider()

# --- CHAT LOGIC ---
if option == "💬 Agri Chat":
    st.header("Agricultural Expert Advice")
    user_query = st.text_input("Apna sawal likhein:")
    
    if st.button("Jawab Lein"):
        if user_query:
            with st.spinner("Groq AI soch raha hai..."):
                # Groq Model Call
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are a helpful agriculture expert. Answer in simple {lang_opt}."
                        },
                        {
                            "role": "user",
                            "content": user_query,
                        }
                    ],
                    model="llama-3.3-70b-versatile", # Groq ka sab se best model
                )
                jawab = chat_completion.choices[0].message.content
                st.markdown(f"**AI:** {jawab}")
                play_audio(jawab)
        else:
            st.warning("Pehle sawal likhein!")

elif option == "💰 Mandi Rates":
    st.header("Mandi Price Advisor")
    crop = st.text_input("Fasal ka naam:")
    if st.button("Check Rates"):
        with st.spinner("Checking..."):
            chat_completion = client.chat.completions.create(
                messages=[{"role": "user", "content": f"Tell current market price trends for {crop} in Pakistan in {lang_opt}"}],
                model="llama-3.3-70b-versatile",
            )
            jawab = chat_completion.choices[0].message.content
            st.info(jawab)
            play_audio(jawab)

st.sidebar.write("Powered by Groq Llama 3")
