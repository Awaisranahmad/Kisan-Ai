import base64
import io
from PIL import Image
from gtts import gTTS
from fpdf import FPDF
import tempfile
from datetime import datetime
import streamlit as st

def play_audio(text, prompt_text="🔊 پلے"):
    try:
        clean_text = text.replace('|', ' ').replace('-', ' ').replace('#', ' ').replace('*', ' ')
        tts = gTTS(text=clean_text[:300], lang='ur', slow=False)
        tts.save("expert_voice.mp3")
        with open("expert_voice.mp3", "rb") as f:
            data = f.read()
            b64 = base64.b64encode(data).decode()
            md = f"""
            <div style="background: #e8f5e9; padding: 15px; border-radius: 15px; border: 2px solid #2e7d32; margin-top: 15px; text-align: center;">
                <p style="color: #2e7d32; font-weight: bold;">{prompt_text}</p>
                <audio controls style="width: 100%;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
            </div>"""
            st.markdown(md, unsafe_allow_html=True)
    except:
        pass

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

def create_pdf(text):
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_font('DejaVu', '', 'DejaVuSans.ttf', uni=True)
        pdf.set_font('DejaVu', '', 12)
        pdf.multi_cell(0, 10, text)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            pdf.output(tmp.name)
            return tmp.name
    except:
        return None

def download_pdf_button(content, filename_prefix="expert"):
    pdf_path = create_pdf(content)
    if pdf_path:
        with open(pdf_path, "rb") as f:
            st.download_button("📄 PDF ڈاؤن لوڈ", f,
                               file_name=f"{filename_prefix}_{datetime.now():%Y%m%d_%H%M%S}.pdf")
