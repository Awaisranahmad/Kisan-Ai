import streamlit as st
from streamlit_mic_recorder import mic_recorder
from config import t, get_groq_client
from ai_engine import get_ai_response
from utils import play_audio, download_pdf_button

def render_fertilizer():
    st.subheader(t("fertilizer"))
    
    if st.session_state.fert_history:
        st.write("---")
        st.subheader("🧪 پچھلی مشاورت")
        for i, item in enumerate(st.session_state.fert_history):
            with st.expander(f"مشاورت #{i+1} - {item['crop']}"):
                st.markdown(f"**فصل:** {item['crop']} | **مٹی:** {item['soil']} | **علاقہ:** {item['location']}")
                st.markdown(f"<div class='urdu-card'>{item['response']}</div>", unsafe_allow_html=True)
                if st.button(f"🔊 سنیں #{i+1}", key=f"fert_audio_{i}"):
                    play_audio(item['response'])

    with st.form("fert_form"):
        crop = st.text_input("فصل کا نام لکھیں:")
        soil = st.selectbox("مٹی کی قسم:", ["چکنی مٹی", "ریتلی", "میٹی", "کلر", "نمی"])
        location = st.text_input("علاقہ:")
        c1, c2 = st.columns([1, 4])
        with c1:
            audio_q = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='fert_mic')
        with c2:
            if audio_q and audio_q.get('id') != st.session_state.get("processed_id"):
                st.session_state.processed_id = audio_q.get('id')
                voice_text = ""
                client = get_groq_client()
                if client:
                    voice_text = client.audio.transcriptions.create(
                        file=("a.wav", audio_q['bytes']),
                        model="whisper-large-v3",
                        language="ur"
                    ).text
                    st.write(f"آواز: {voice_text}")
        
        submitted = st.form_submit_button(t('fertilizer_advice'))
        if submitted:
            if crop:
                prompt = f"Fertilizer advice for {crop}, soil type: {soil}, location: {location} in Pakistan. Provide current market prices per bag and recommend usage."
                if 'voice_text' in locals() and voice_text:
                    prompt += f" Additional voice: {voice_text}"
                ans = get_ai_response(prompt, is_khaad=True)
                st.session_state.fert_history.append({
                    "crop": crop, "soil": soil, "location": location, "response": ans
                })
                st.markdown(f"<div class='urdu-card'>{ans}</div>", unsafe_allow_html=True)
                play_audio(ans)
                download_pdf_button(ans, "fertilizer_advice")
            else:
                st.warning("فصل کا نام ضرور درج کریں۔")
