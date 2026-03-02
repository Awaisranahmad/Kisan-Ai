import streamlit as st
from groq import Groq
from gtts import gTTS
import base64
import io
from streamlit_mic_recorder import mic_recorder
from PIL import Image

# --- 1. Connection Setup ---
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

if "messages" not in st.session_state:
    st.session_state.messages = []
if "processed_id" not in st.session_state:
    st.session_state.processed_id = None

# --- 2. Audio Function ---
def play_audio(text):
    try:
        clean_text = text.replace('|', ' ').replace('-', ' ').replace('#', ' ')
        tts = gTTS(text=clean_text[:300], lang='ur', slow=False)
        tts.save("expert_voice.mp3")
        with open("expert_voice.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
                <div style="background: #e8f5e9; padding: 15px; border-radius: 15px; border: 2px solid #2e7d32; margin-top: 15px; text-align: center;">
                    <p style="color: #2e7d32; font-weight: bold; margin-bottom: 8px;">🔊 جواب سننے کے لیے پلے دبائیں</p>
                    <audio controls style="width: 100%; height: 40px;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
                </div>
                """
            st.markdown(md, unsafe_allow_html=True)
    except: pass

# --- 3. Image Handling ---
def process_image_to_b64(uploaded_file):
    image = Image.open(uploaded_file)
    if image.mode != "RGB":
        image = image.convert("RGB")
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode('utf-8')

# --- 4. UI Styling ---
st.set_page_config(page_title="Kisan Expert Pro", page_icon="🚜", layout="centered")
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');
    .urdu-card { font-family: 'Noto Nastaliq Urdu', serif; direction: rtl; text-align: right; font-size: 20px; color: #1b5e20; background: #ffffff; padding: 20px; border-radius: 15px; border-right: 8px solid #2e7d32; line-height: 2.2; margin-bottom: 15px; }
    .header-container { background: #2e7d32; padding: 30px; border-radius: 0 0 30px 30px; color: white; text-align: center; margin-top: -60px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. Sidebar ---
with st.sidebar:
    st.title("کیسان مینو")
    menu = st.radio("آپشن منتخب کریں:", ["💬 چیٹ", "📸 کراپ ڈاکٹر", "🧪 کھاد ایڈوائزر", "💰 منڈی ریٹ"])

st.markdown("<div class='header-container'><h1>🚜 کسان دوست ایکسپرٹ</h1></div>", unsafe_allow_html=True)

# --- AI Logic (Updated to 90B Vision) ---
def get_ai_response(prompt, image_b64=None):
    # Sab se behtar model jo vision support karta hai
    vision_model = "llama-3.2-90b-vision-preview"
    text_model = "llama-3.3-70b-versatile"
    
    messages = [{"role": "system", "content": "You are a professional Pakistani Agri-Expert. Respond ONLY in Urdu script. No Hindi/English."}]
    
    if image_b64:
        messages.append({
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_b64}"}}
            ]
        })
        model = vision_model
    else:
        messages.append({"role": "user", "content": prompt})
        model = text_model
    
    try:
        chat = client.chat.completions.create(model=model, messages=messages)
        return chat.choices[0].message.content
    except Exception as e:
        return f"معذرت، نیٹ ورک کا مسئلہ ہے: {str(e)}"

# --- Pages ---
if menu == "💬 چیٹ":
    st.subheader("🎤 اپنا سوال پوچھیں")
    u_text = st.text_input("یہاں لکھیں...")
    if st.button("بھیجیں") and u_text:
        ans = get_ai_response(u_text)
        st.markdown(f"<div class='urdu-card'>{ans}</div>", unsafe_allow_html=True)
        play_audio(ans)

elif menu == "📸 کراپ ڈاکٹر":
    st.subheader("فصل کی تصویر سے بیماری پہچانیں")
    file = st.file_uploader("تصویر اپ لوڈ کریں (JFIF, JPG, PNG)", type=["jpg", "png", "jpeg", "jfif"])
    
    if file:
        st.image(file, caption="آپ کی تصویر", use_container_width=True)
        if st.button("بیماری کی تشخیص کریں"):
            with st.spinner("AI تصویر کا معائنہ کر رہا ہے..."):
                try:
                    img_b64 = process_image_to_b64(file)
                    ans = get_ai_response("Analyze this plant image. Identify the crop, the disease, and give treatment in Urdu.", image_b64=img_b64)
                    st.markdown(f"<div class='urdu-card'>{ans}</div>", unsafe_allow_html=True)
                    play_audio(ans)
                except Exception as e:
                    st.error(f"Error: {str(e)}")

elif menu == "💰 منڈی ریٹ":
    crop = st.text_input("فصل کا نام لکھیں:")
    if st.button("ریٹ دیکھیں"):
        ans = get_ai_response(f"Current Mandi rates for {crop} in Pakistan cities as a table.")
        st.markdown(ans)
        play_audio(ans)
