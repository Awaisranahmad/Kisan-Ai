import streamlit as st
from streamlit_mic_recorder import mic_recorder
from config import t
from ai_engine import get_ai_response, transcribe_audio
from mandi_data import fetch_mandi_rates, format_rates_markdown
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
            voice_text = transcribe_audio(audio_q['bytes']) or ""

    if st.button(t('show_rate')):
        if crop:
            prompt_crop = crop
            if voice_text:
                prompt_crop = voice_text
            # 1. Live rates first — real AMIS Punjab data, never invented.
            live = fetch_mandi_rates(prompt_crop)
            if live.get("ok"):
                table = format_rates_markdown(live)
                st.markdown(table, unsafe_allow_html=True)
                explain_prompt = (
                    f"Explain these real mandi rates in simple Urdu for a farmer. "
                    f"Use ONLY the numbers in this table, do not invent any other rate. "
                    f"Say which city is cheapest and which is most expensive. Table:\n{table}"
                )
                ans = get_ai_response(explain_prompt, is_mandi=True)
                st.markdown(ans, unsafe_allow_html=True)
                full = table + "\n\n" + ans
                st.session_state.mandi_history.append({"crop": crop, "response": full})
                play_audio("یہ رہی ریٹ کی تفصیل جس میں یونٹ بھی شامل ہیں۔")
                download_pdf_button(full, "mandi_rates")
            else:
                # 2. No live data: say so honestly, AI estimate is labelled as one.
                st.warning(f"⚠️ Live rate نہیں مل سکا ({live.get('error', '')}) — نیچے AI کا اندازہ ہے، سرکاری ریٹ نہیں۔")
                prompt = f"Current Mandi rates for {prompt_crop} in Pakistan cities with units (mann/kg). Provide only Urdu Markdown table."
                ans = get_ai_response(prompt, is_mandi=True)
                labelled = "⚠️ **نوٹ: یہ AI کا اندازہ ہے، live سرکاری ریٹ نہیں۔**\n\n" + ans
                st.markdown(labelled, unsafe_allow_html=True)
                st.session_state.mandi_history.append({"crop": crop, "response": labelled})
                play_audio("یہ رہی ریٹ کی تفصیل جس میں یونٹ بھی شامل ہیں۔")
                download_pdf_button(labelled, "mandi_rates")
        else:
            st.warning("فصل کا نام لکھیں۔")
