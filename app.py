import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
import os
from streamlit_mic_recorder import mic_recorder
from PIL import Image
from fpdf import FPDF
import tempfile
from datetime import datetime

# ---------------------- Page Config ----------------------
st.set_page_config(page_title="Kisan Expert Pro", page_icon="🚜", layout="centered")

# ---------------------- Language Dictionary ----------------------
if "lang" not in st.session_state:
    st.session_state.lang = "ur"

texts = {
    "ur": {
        "title": "کیسان ایکسپرٹ پرو",
        "subtitle": "آپ کی فصل، ہماری فکر",
        "menu": "کیسان مینو",
        "chat": "💬 چیٹ",
        "crop_doctor": "📸 کراپ  ڈاکٹر",
        "fertilizer": "🧪 کھاد ایڈوائزر",
        "mandi": "💰 منڈی ریٹ",
        "new_chat": "🔄 نئی چیٹ",
        "api_title": "🔑 API سیٹنگز",
        "enter_key": "اپنی GROQ API کی درج کریں:",
        "use_own_key": "اپنی کی استعمال کریں",
        "no_api": "API کی دستیاب نہیں۔ برائے مہربانی اپنی کی ڈالیں۔",
        "send": "بھیجیں",
        "mic_start": "🎤",
        "mic_stop": "⏹️",
        "text_placeholder": "یہاں لکھیں...",
        "upload": "تصویر اپ لوڈ کریں",
        "camera": "تصویر کھینچیں",
        "examine": "معائنہ کریں",
        "crop_input": "فصل کا نام لکھیں:",
        "soil_type": "مٹی کی قسم:",
        "location": "علاقہ:",
        "fertilizer_advice": "مشورہ اور ریٹ لیں",
        "crop_name_mandi": "فصل کا نام (مثلاً گندم، کپاس):",
        "show_rate": "ریٹ دیکھیں",
        "download_pdf": "📄 PDF ڈاؤن لوڈ",
        "download_chat": "💾 چیٹ ڈاؤن لوڈ",
        "gallery_title": "🖼️ فصل کی تصاویر",
        "healthy": "صحت مند",
        "unhealthy": "بیمار",
        "audio_prompt": "🔊 جواب سننے کے لیے پلے دبائیں",
        "fert_history": "🧪 کھاد کی مشاورت",
        "mandi_history": "💰 منڈی ریٹس",
        "crop_history": "📸 فصل کی تشخیص",
    },
    "en": {
        "title": "Kisan Expert Pro",
        "subtitle": "Your Crop, Our Concern",
        "menu": "Farmer Menu",
        "chat": "💬 Chat",
        "crop_doctor": "📸 Crop Doctor",
        "fertilizer": "🧪 Fertilizer Advisor",
        "mandi": "💰 Mandi Rates",
        "new_chat": "🔄 New Chat",
        "api_title": "🔑 API Settings",
        "enter_key": "Enter your GROQ API Key:",
        "use_own_key": "Use Own Key",
        "no_api": "API key not available. Please enter your key.",
        "send": "Send",
        "mic_start": "🎤",
        "mic_stop": "⏹️",
        "text_placeholder": "Write here...",
        "upload": "Upload Image",
        "camera": "Take Photo",
        "examine": "Examine",
        "crop_input": "Crop Name:",
        "soil_type": "Soil Type:",
        "location": "Location:",
        "fertilizer_advice": "Get Advice & Rates",
        "crop_name_mandi": "Crop Name (e.g., Wheat, Cotton):",
        "show_rate": "Show Rates",
        "download_pdf": "📄 Download PDF",
        "download_chat": "💾 Download Chat",
        "gallery_title": "🖼️ Crop Gallery",
        "healthy": "Healthy",
        "unhealthy": "Unhealthy",
        "audio_prompt": "🔊 Play to listen",
        "fert_history": "🧪 Fertilizer History",
        "mandi_history": "💰 Mandi History",
        "crop_history": "📸 Crop Diagnosis",
    }
}
t = lambda key: texts[st.session_state.lang].get(key, key)

# ---------------------- Session State ----------------------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_id" not in st.session_state:
    st.session_state.processed_id = None
if "crop_history" not in st.session_state:
    st.session_state.crop_history = []   # list of dicts: {img_b64, response}
if "fert_history" not in st.session_state:
    st.session_state.fert_history = []   # list of dicts: {crop, soil, location, response}
if "mandi_history" not in st.session_state:
    st.session_state.mandi_history = []  # list of dicts: {crop, response}
if "user_api_key" not in st.session_state:
    st.session_state.user_api_key = ""

# ---------------------- Groq Client Initialization ----------------------
def get_groq_client():
    # Pehle secrets try karo
    api_key = st.secrets.get("GROQ_API_KEY", "")
    if api_key:
        return Groq(api_key=api_key)
    # Phir user entered key
    if st.session_state.user_api_key:
        return Groq(api_key=st.session_state.user_api_key)
    return None

client = get_groq_client()

# ---------------------- Audio Playback ----------------------
def play_audio(text):
    try:
        clean_text = text.replace('|', ' ').replace('-', ' ').replace('#', ' ').replace('*', ' ')
        tts = gTTS(text=clean_text[:300], lang='ur', slow=False)
        tts.save("expert_voice.mp3")
        with open("expert_voice.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <div style="background: #e8f5e9; padding: 15px; border-radius: 15px; border: 2px solid #2e7d32; margin-top: 15px; text-align: center;">
                    <p style="color: #2e7d32; font-weight: bold; margin-bottom: 8px;">{t('audio_prompt')}</p>
                    <audio controls style="width: 100%; height: 40px;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                </div>
                """
            st.markdown(md, unsafe_allow_html=True)
    except:
        pass

# ---------------------- Image Processing ----------------------
def process_image_to_b64(image_data):
    try:
        image = Image.open(image_data)
        if image.mode != "RGB":
            image = image.convert("RGB")
        image.thumbnail((800, 800))
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG", quality=85)
        return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except:
        return None

# ---------------------- PDF Generation ----------------------
def create_pdf(text, filename_prefix="expert_report"):
    try:
        # Note: For proper Urdu rendering, you need to add a Unicode font file.
        # Download 'Noto Nastaliq Urdu' font and place it in the same folder.
        # Then uncomment the line below and use it.
        # pdf.add_font('Noto', '', 'NotoNastaliqUrdu-Regular.ttf', uni=True)
        # For now, we use a generic approach with DejaVu (may not display Urdu correctly).
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        # Add a simple font (will show squares for Urdu if font not added)
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True) 
        pdf.set_font('DejaVu', '', 12)
        pdf.multi_cell(0, 10, text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            return tmp.name
    except:
        return None

# ---------------------- AI Response Function ----------------------
def get_ai_response(prompt, image_b64=None, is_mandi=False, is_khaad=False):
    if not client:
        return t('no_api')
    model = "llama-3.2-11b-vision-preview" if image_b64 else "llama-3.3-70b-versatile"
    sys_prompt = "You are a professional Agri-Expert from Pakistan. "
    if st.session_state.lang == "ur":
        sys_prompt += "Respond ONLY in Urdu script. No Hindi/English."
    else:
        sys_prompt += "Respond in English only."

    if is_mandi:
        sys_prompt += " Provide a Markdown Table: City (شہر), Unit (یونٹ - فی من/فی کلو), Min (کم سے کم ریٹ), Max (زیادہ سے زیادہ ریٹ). Always mention if the rate is per 40kg (mann) or per kg."
    if is_khaad:
        sys_prompt += " Provide details and a table for Fertilizer rates: Name (کھاد کا نام), Unit (یونٹ - فی بیگ), Price (ریٹ)."

    messages = [{"role": "system", "content": sys_prompt}]
    if image_b64:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
            ]
        })
    else:
        messages.append({"role": "user", "content": prompt})

    try:
        chat = client.chat.completions.create(model=model, messages=messages)
        return chat.choices[0].message.content
    except Exception as e:
        return f"⚠️ Error: {str(e)}"

# ---------------------- Real Mandi API Placeholder ----------------------
def fetch_real_mandi_rates(crop):
    """
    Yahan aap real API call kar sakte hain.
    Example using 'Agmarknet' or any Pakistan Mandi API.
    Documentation link: https://example.com/api (put real link)
    """
    # Mock data for demo
    mock_data = f"""
    | شہر | یونٹ | کم سے کم | زیادہ سے زیادہ |
    |---|---|---|---|
    | لاہور | فی 40 کلو | 3500 | 3800 |
    | کراچی | فی 40 کلو | 3400 | 3750 |
    | فیصل آباد | فی 40 کلو | 3450 | 3720 |
    """
    return mock_data
    # Real API call example:
    # import requests
    # response = requests.get(f"https://real-api.com/mandi?crop={crop}")
    # return response.json()

# ---------------------- Premium UI Styling ----------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
.stApp { background-color: #f9fbf9; }
[data-testid="stSidebar"] { background-color: #e8f5e9 !important; border-right: 2px solid #c8e6c9; }
.urdu-card { 
    font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: right; 
    font-size: 20px; color: #1b5e20; background: #ffffff; padding: 25px; 
    border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.05); 
    margin-bottom: 15px; border-right: 10px solid #2e7d32; line-height: 2.4;
}
.user-bubble { 
    font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: left; 
    background: #DCF8C6; padding: 15px; border-radius: 15px 15px 0 15px; 
    margin-bottom: 10px; color: #075E54; display: inline-block; float: left;
    clear: both; max-width: 80%;
}
.assistant-bubble {
    font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: right;
    background: #ffffff; padding: 15px; border-radius: 15px 15px 15px 0;
    margin-bottom: 10px; border-right: 5px solid #2e7d32;
    float: right; clear: both; max-width: 80%;
}
.stMarkdown table { width: 100%; direction: rtl; border-collapse: collapse; border-radius: 10px; overflow: hidden; margin: 20px 0; }
.stMarkdown th { background-color: #2e7d32 !important; color: white !important; padding: 12px !important; text-align: center !important; }
.stMarkdown td { background-color: white !important; color: #333 !important; padding: 10px !important; text-align: center !important; border-bottom: 1px solid #eee !important; }
.header-box { background: #2e7d32; padding: 35px; border-radius: 0 0 35px 35px; color: white; text-align: center; margin-top: -65px; box-shadow: 0 4px 12px rgba(0,0,0,0.2); }
/* Responsive */
@media (max-width: 600px) {
    .urdu-card, .user-bubble, .assistant-bubble { font-size: 16px; padding: 15px; }
    .header-box { padding: 20px; }
}
</style>
""", unsafe_allow_html=True)

# ---------------------- Sidebar ----------------------
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2316/2316334.png", width=80)
    st.title(t("menu"))
    
    # Language toggle
    lang_choice = st.selectbox("🌐 Language / زبان", ["ur", "en"], index=0)
    if lang_choice != st.session_state.lang:
        st.session_state.lang = lang_choice
        st.rerun()

    menu = st.radio(t("menu"), [t("chat"), t("crop_doctor"), t("fertilizer"), t("mandi")])
    if st.button(t("new_chat")):
        st.session_state.messages = []
        st.session_state.processed_id = None
        st.rerun()

    # API Settings
    with st.expander(t("api_title"), expanded=False):
        user_key = st.text_input(t("enter_key"), type="password", key="user_key_input")
        if st.button(t("use_own_key")):
            st.session_state.user_api_key = user_key
            st.success("API key updated! Reloading...")
            st.rerun()
        if not client:
            st.warning(t("no_api"))

# ---------------------- Header ----------------------
st.markdown(f"<div class='header-box'><h1>🚜 {t('title')}</h1><p>{t('subtitle')}</p></div>", unsafe_allow_html=True)

# ---------------------- Chat Section ----------------------
if menu == t("chat"):
    # Display history
    for m in st.session_state.messages:
        if m["role"] == "user":
            st.markdown(f"<div class='user-bubble'>{m['content']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='assistant-bubble'>{m['content']}</div>", unsafe_allow_html=True)

    st.write("---")
    st.subheader(f"🎤 {t('text_placeholder')}")
    c1, c2 = st.columns([1, 4])
    with c1:
        audio = mic_recorder(start_prompt=t('mic_start'), stop_prompt=t('mic_stop'), key='chat_mic')
    with c2:
        u_text = st.text_input(t('text_placeholder'), key="u_input", label_visibility="collapsed")
        send = st.button(t('send'))

    q = ""
    if audio and audio.get('id') != st.session_state.processed_id:
        st.session_state.processed_id = audio.get('id')
        if client:
            q = client.audio.transcriptions.create(file=("a.wav", audio['bytes']), model="whisper-large-v3", language="ur").text
        else:
            st.warning(t('no_api'))
    elif send and u_text:
        q = u_text

    if q:
        ans = get_ai_response(q)
        st.session_state.messages.append({"role": "user", "content": q})
        st.session_state.messages.append({"role": "assistant", "content": ans})
        st.rerun()

    # Download chat
    if st.session_state.messages:
        chat_text = "\n\n".join([f"{'صارف' if m['role']=='user' else 'ایکسپرٹ'}: {m['content']}" for m in st.session_state.messages])
        st.download_button(label=t('download_chat'), data=chat_text, file_name=f"chat_{datetime.now():%Y%m%d_%H%M%S}.txt", mime="text/plain")

    if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
        play_audio(st.session_state.messages[-1]["content"])
        # PDF download for last response
        pdf_path = create_pdf(st.session_state.messages[-1]["content"])
        if pdf_path:
            with open(pdf_path, "rb") as f:
                st.download_button(t("download_pdf"), f, file_name=f"expert_response_{datetime.now():%Y%m%d_%H%M%S}.pdf")

# ---------------------- Crop Doctor Section ----------------------
elif menu == t("crop_doctor"):
    st.subheader(t("crop_doctor"))
    
    # Show previous diagnoses
    if st.session_state.crop_history:
        st.markdown("---")
        st.subheader(t("crop_history"))
        for i, item in enumerate(st.session_state.crop_history):
            with st.expander(f"تفتیش #{i+1}", expanded=False):
                if item.get("img_b64"):
                    st.image(base64.b64decode(item["img_b64"]), width=200)
                st.markdown(f"<div class='urdu-card'>{item['response']}</div>", unsafe_allow_html=True)
                # Audio for history
                if st.button(f"🔊 سنیں #{i+1}", key=f"hist_audio_{i}"):
                    play_audio(item['response'])

    # Input options
    option = st.radio("انتخاب کریں:", [t("upload"), t("camera")])
    image_data = None
    if option == t("upload"):
        file = st.file_uploader(t("upload"), type=["jpg", "png", "jpeg", "jfif", "webp", "bmp", "tiff"])
        if file:
            image_data = file
            st.image(file, caption="Uploaded", use_container_width=True)
    else:
        camera_file = st.camera_input(t("camera"))
        if camera_file:
            image_data = camera_file
            st.image(camera_file, caption="Camera Snap", use_container_width=True)

    # Text/voice question
    c1, c2 = st.columns([1, 4])
    with c1:
        audio_q = mic_recorder(start_prompt=t('mic_start'), stop_prompt=t('mic_stop'), key='crop_mic')
    with c2:
        extra_q = st.text_input("اضافی سوال (optional)", key="crop_q")
    
    if st.button(t("examine")):
        if image_data is not None:
            img_b64 = process_image_to_b64(image_data)
            if img_b64:
                prompt = "Iss tasweer mein mojood fasal ki sehat check karo. Agar fasal bilkul sehatmand (achhi) hai to batao, warna agar koi kami, bemari ya nuqsaan ho to us ki wazahat karo aur behtari ke liye mukammal hidayat Urdu mein do. Sirf Urdu script istemal karo."
                if extra_q:
                    prompt += f" Additional question: {extra_q}"
                # Also handle voice query
                if audio_q and audio_q.get('id') != st.session_state.processed_id:
                    st.session_state.processed_id = audio_q.get('id')
                    if client:
                        voice_text = client.audio.transcriptions.create(file=("a.wav", audio_q['bytes']), model="whisper-large-v3", language="ur").text
                        prompt += f" User voice query: {voice_text}"
                ans = get_ai_response(prompt, image_b64=img_b64)
                # Save to history
                st.session_state.crop_history.append({"img_b64": img_b64, "response": ans})
                st.markdown(f"<div class='urdu-card'>{ans}</div>", unsafe_allow_html=True)
                play_audio(ans)
                # PDF
                pdf_path = create_pdf(ans)
                if pdf_path:
                    with open(pdf_path, "rb") as f:
                        st.download_button(t("download_pdf"), f, file_name=f"crop_diagnosis_{datetime.now():%Y%m%d_%H%M%S}.pdf")
            else:
                st.error("تصویر پروسیس نہیں ہو سکی۔")
        else:
            st.warning("پہلے تصویر دیں۔")

# ---------------------- Fertilizer Advisor Section ----------------------
elif menu == t("fertilizer"):
    st.subheader(t("fertilizer"))
    
    # Show history
    if st.session_state.fert_history:
        st.markdown("---")
        st.subheader(t("fert_history"))
        for i, item in enumerate(st.session_state.fert_history):
            with st.expander(f"مشاورت #{i+1} - {item['crop']}", expanded=False):
                st.markdown(f"**فصل:** {item['crop']}  |  **مٹی:** {item['soil']}  |  **علاقہ:** {item['location']}")
                st.markdown(f"<div class='urdu-card'>{item['response']}</div>", unsafe_allow_html=True)
                if st.button(f"🔊 سنیں #{i+1}", key=f"fert_audio_{i}"):
                    play_audio(item['response'])

    with st.form("fert_form"):
        crop = st.text_input(t("crop_input"))
        soil = st.selectbox(t("soil_type"), ["چکنی مٹی", "ریتلی", "میٹی", "کلر", "نمی"], index=0)
        location = st.text_input(t("location"))
        c1, c2 = st.columns([1, 4])
        with c1:
            audio_q = mic_recorder(start_prompt=t('mic_start'), stop_prompt=t('mic_stop'), key='fert_mic')
        with c2:
            voice_text = ""
            if audio_q and audio_q.get('id') != st.session_state.processed_id:
                st.session_state.processed_id = audio_q.get('id')
                if client:
                    voice_text = client.audio.transcriptions.create(file=("a.wav", audio_q['bytes']), model="whisper-large-v3", language="ur").text
                    st.write(f"آواز: {voice_text}")
        submitted = st.form_submit_button(t("fertilizer_advice"))
        if submitted:
            if crop:
                prompt = f"Fertilizer advice for {crop}, soil type: {soil}, location: {location} in Pakistan. Provide current market prices per bag and recommend usage."
                if voice_text:
                    prompt += f" Additional voice note: {voice_text}"
                ans = get_ai_response(prompt, is_khaad=True)
                st.session_state.fert_history.append({"crop": crop, "soil": soil, "location": location, "response": ans})
                st.markdown(f"<div class='urdu-card'>{ans}</div>", unsafe_allow_html=True)
                play_audio(ans)
                pdf_path = create_pdf(ans)
                if pdf_path:
                    with open(pdf_path, "rb") as f:
                        st.download_button(t("download_pdf"), f, file_name=f"fertilizer_advice_{datetime.now():%Y%m%d_%H%M%S}.pdf")
            else:
                st.warning("فصل کا نام ضرور درج کریں۔")

# ---------------------- Mandi Rates Section ----------------------
elif menu == t("mandi"):
    st.subheader(t("mandi"))
    
    # Show history
    if st.session_state.mandi_history:
        st.markdown("---")
        st.subheader(t("mandi_history"))
        for i, item in enumerate(st.session_state.mandi_history):
            with st.expander(f"ریٹ #{i+1} - {item['crop']}", expanded=False):
                st.markdown(item['response'], unsafe_allow_html=True)
                if st.button(f"🔊 سنیں #{i+1}", key=f"mandi_audio_{i}"):
                    play_audio("یہ رہی ریٹ کی تفصیل جس میں یونٹ بھی شامل ہیں۔")

    crop = st.text_input(t("crop_name_mandi"))
    c1, c2 = st.columns([1, 4])
    with c1:
        audio_q = mic_recorder(start_prompt=t('mic_start'), stop_prompt=t('mic_stop'), key='mandi_mic')
    with c2:
        voice_text = ""
        if audio_q and audio_q.get('id') != st.session_state.processed_id:
            st.session_state.processed_id = audio_q.get('id')
            if client:
                voice_text = client.audio.transcriptions.create(file=("a.wav", audio_q['bytes']), model="whisper-large-v3", language="ur").text

    if st.button(t("show_rate")):
        if crop:
            # Decide whether to use AI or real API
            # Uncomment next line to use real API
            # ans = fetch_real_mandi_rates(crop)
            # AI Fallback
            prompt = f"Current Mandi rates for {crop} in Pakistan cities with units (mann/kg). Provide only Urdu Markdown table."
            if voice_text:
                prompt += f" Voice query: {voice_text}"
            ans = get_ai_response(prompt, is_mandi=True)
            st.session_state.mandi_history.append({"crop": crop, "response": ans})
            st.markdown(ans, unsafe_allow_html=True)
            play_audio("یہ رہی ریٹ کی تفصیل جس میں یونٹ بھی شامل ہیں۔")
            pdf_path = create_pdf(ans)
            if pdf_path:
                with open(pdf_path, "rb") as f:
                    st.download_button(t("download_pdf"), f, file_name=f"mandi_rates_{datetime.now():%Y%m%d_%H%M%S}.pdf")
        else:
            st.warning("فصل کا نام لکھیں۔")

# ---------------------- Crop Gallery ----------------------
with st.expander(t("gallery_title")):
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://agrihunt.com/images/crops/tomato_healthy.jpg", caption=t("healthy"))
    with col2:
        st.image("https://agrihunt.com/images/crops/tomato_disease.jpg", caption=t("unhealthy"))
