import streamlit as st
from streamlit_mic_recorder import mic_recorder
from config import t, get_groq_client
from ai_engine import get_ai_response
from utils import play_audio, download_pdf_button

def render_chat():
    # دکھانے والا حصہ
    for m in st.session_state.messages:
        if m["role"] == "user":
            st.markdown(f"<div class='user-bubble'>{m['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='assistant-bubble'>{m['content']}</div>", unsafe_allow_html=True)

    st.write("---")
    st.subheader("🎤 اپنا سوال پوچھیں")
    c1, c2 = st.columns([1, 4])
    with c1:
        audio = mic_recorder(start_prompt="🎤", stop_prompt="⏹️", key='chat_mic')
    with c2:
        u_text = st.text_input("یہاں لکھیں...", key="u_input", label_visibility="collapsed")
        send = st.button(t('send'))

    q = ""
    if audio and audio.get('id') != st.session_state.get("processed_id"):
        st.session_state.processed_id = audio.get('id')
        client = get_groq_client()
        if client:
            q = client.audio.transcriptions.create(
                file=("a.wav", audio['bytes']),
                model="whisper-large-v3",
                language="ur"
            ).text
    elif send and u_text:
        q = u_text

    if q:
        ans = get_ai_response(q)
        st.session_state.messages.append({"role": "user", "content": q})
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()

    if st.session_state.messages:
        chat_text = "\n\n".join([
            f"{'صارف' if m['role']=='user' else 'ایکسپرٹ'}: {m['content']}" 
            for m in st.session_state.messages
        ])
        st.download_button(t('download_chat'), chat_text, file_name="chat.txt")

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        play_audio(st.session_state.messages[-1]["content"])
        download_pdf_button(st.session_state.messages[-1]["content"])
