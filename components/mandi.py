import streamlit as st
from streamlit_mic_recorder import mic_recorder
from config import t, get_groq_client
from ai_engine import get_ai_response
from utils import play_audio, download_pdf_button

def render_mandi():
    st.subheader(t("mandi"))
    
    if st.session_state.mandi_history:
        st.write("---")
        st.subheader("💰 پچھلے ریٹ")
        for i, item in enumerate(st.session_state.mandi_history):
            with st.expander(f"ریٹ #{i+1} - {item['crop']}"):
                st.markdown(item['response'], unsafe_allow_html=True)
                if st.button(f"🔊 سنیں #{i+1}", key=f"mandi_audio_{i}"):
                    play_audio("یہ رہی ریٹ کی تفصیل جس میں یونٹ بھی شامل ہیں۔")

    crop = st.text_input("فصل کا نام (مثلاً گندم، کپاس):")
    c1, c2 = st.columns([1, 4])
    with c1:
        audio_q = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='mandi_mic')
    with c2:
        voice_text = ""
        if audio_q and audio_q.get('id') != st.session_state.get("processed_id"):
            st.session_state.processed_id = audio_q.get('id')
            client = get_groq_client()
            if client:
                voice_text = client.audio.transcriptions.create(
                    file=("a.wav", audio_q['bytes']),
                    model="whisper-large-v3",
                    language="ur"
                ).text
    
    if st.button(t('show_rate')):
        if crop:
            prompt = f"Current Mandi rates for {crop} in Pakistan cities with units (mann/kg). Provide only Urdu Markdown table."
            if voice_text:
                prompt += f" Voice query: {voice_text}"
            ans = get_ai_response(prompt, is_mandi=True)
            st.session_state.mandi_history.append({"crop": crop, "response": ans})
            st.markdown(ans, unsafe_allow_html=True)
            play_audio("یہ رہی ریٹ کی تفصیل جس میں یونٹ بھی شامل ہیں۔")
            download_pdf_button(ans, "mandi_rates")
        else:
            st.warning("فصل کا نام لکھیں۔")
