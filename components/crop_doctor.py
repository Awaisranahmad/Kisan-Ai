import streamlit as st
from streamlit_mic_recorder import mic_recorder
from config import t, get_groq_client
from ai_engine import get_ai_response
from utils import play_audio, process_image_to_b64, download_pdf_button
import base64

def render_crop_doctor():
    st.subheader(t("crop_doctor"))
    
    # پچھلی تشخیص
    if st.session_state.crop_history:
        st.write("---")
        st.subheader("📋 پچھلی تشخیص")
        for i, item in enumerate(st.session_state.crop_history):
            with st.expander(f"تفتیش #{i+1}"):
                if item.get("img_b64"):
                    st.image(base64.b64decode(item["img_b64"]), width=200)
                st.markdown(f"<div class='urdu-card'>{item['response']}</div>", unsafe_allow_html=True)
                if st.button(f"🔊 سنیں #{i+1}", key=f"hist_audio_{i}"):
                    play_audio(item['response'])

    option = st.radio("انتخاب کریں:", [t('upload'), t('camera')])
    image_data = None
    if option == t('upload'):
        file = st.file_uploader(t('upload'), type=["jpg", "png", "jpeg", "jfif", "webp", "bmp", "tiff"])
        if file:
            image_data = file
            st.image(file, use_container_width=True)
    else:
        cam = st.camera_input(t('camera'))
        if cam:
            image_data = cam
            st.image(cam, use_container_width=True)

    c1, c2 = st.columns([1, 4])
    with c1:
        audio_q = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='crop_mic')
    with c2:
        extra_q = st.text_input("اضافی سوال (optional)", key="crop_q")
    
    if st.button(t('examine')):
        if image_data:
            img_b64 = process_image_to_b64(image_data)
            if img_b64:
                prompt = "Iss tasweer mein mojood fasal ki sehat check karo. Agar fasal bilkul sehatmand (achhi) hai to batao, warna agar koi kami, bemari ya nuqsaan ho to us ki wazahat karo aur behtari ke liye mukammal hidayat Urdu mein do. Sirf Urdu script istemal karo."
                if extra_q:
                    prompt += f" Additional question: {extra_q}"
                # اگر آواز میں بھی کوئی سوال ہو
                if audio_q and audio_q.get('id') != st.session_state.get("processed_id"):
                    st.session_state.processed_id = audio_q.get('id')
                    client = get_groq_client()
                    if client:
                        voice_text = client.audio.transcriptions.create(
                            file=("a.wav", audio_q['bytes']),
                            model="whisper-large-v3",
                            language="ur"
                        ).text
                        prompt += f" Voice query: {voice_text}"
                ans = get_ai_response(prompt, image_b64=img_b64)
                st.session_state.crop_history.append({"img_b64": img_b64, "response": ans})
                st.markdown(f"<div class='urdu-card'>{ans}</div>", unsafe_allow_html=True)
                play_audio(ans)
                download_pdf_button(ans, "crop_diagnosis")
        else:
            st.warning("پہلے تصویر دیں۔")
