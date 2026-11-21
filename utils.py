"""Helpers: voice playback, image prep, PDF download.

PDF notes
---------
Urdu text needs a font with Urdu glyphs plus letter shaping
(arabic_reshaper) and right-to-left ordering (python-bidi). The font is
bundled in this repo at ``assets/fonts/NotoNaskhArabic.ttf`` — DejaVu
Sans was tried first but lacks the Urdu letters ے (yeh barree) and ہ
(heh goal), so those letters came out blank. The old code looked for a
font in the working directory, which does not exist, so every PDF button
silently did nothing. Failures are now reported to the user instead of
being swallowed.
"""
import base64
import io
import os
import re
import tempfile
from datetime import datetime

import arabic_reshaper
from bidi.algorithm import get_display
from PIL import Image
from gtts import gTTS
from fpdf import FPDF
from fpdf.enums import XPos, YPos

import streamlit as st

FONT_PATH = os.path.join(os.path.dirname(__file__), "assets", "fonts", "NotoNaskhArabic.ttf")


def play_audio(text, prompt_text="🔊 پلے"):
    """Play Urdu text as audio. Writes nothing to disk (in-memory MP3)."""
    try:
        clean_text = text.replace('|', ' ').replace('-', ' ').replace('#', ' ').replace('*', ' ')
        tts = gTTS(text=clean_text[:300], lang='ur', slow=False)
        buf = io.BytesIO()
        tts.write_to_fp(buf)
        b64 = base64.b64encode(buf.getvalue()).decode()
        md = f"""
        <div style="background: #e8f5e9; padding: 15px; border-radius: 15px; border: 2px solid #2e7d32; margin-top: 15px; text-align: center;">
            <p style="color: #2e7d32; font-weight: bold;">{prompt_text}</p>
            <audio controls style="width: 100%;"><source src="data:audio/mp3;base64,{b64}" type="audio/mp3"></audio>
        </div>"""
        st.markdown(md, unsafe_allow_html=True)
    except Exception:
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
    except Exception:
        return None


def _clean_markdown(text):
    """Strip the Markdown the AI answers contain so the PDF stays readable."""
    text = re.sub(r'[*_#`]+', '', text)
    text = text.replace('|', ' ')
    return text


def _shape_urdu_line(line):
    """Shape one line of Urdu for correct PDF rendering (reshaped + RTL)."""
    if not line.strip():
        return line
    try:
        return get_display(arabic_reshaper.reshape(line))
    except Exception:
        return line


def create_pdf(text):
    """Build a PDF from (Urdu) text. Returns the temp file path.

    Raises RuntimeError with a plain message when the PDF cannot be
    built (e.g. the bundled font is missing) — callers show the message
    instead of silently hiding the download button.
    """
    if not os.path.exists(FONT_PATH):
        raise RuntimeError(
            "PDF font missing: assets/fonts/NotoNaskhArabic.ttf not found in the repo."
        )
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_font('NotoNaskh', '', FONT_PATH)
    pdf.set_font('NotoNaskh', '', 12)
    for raw_line in _clean_markdown(text).splitlines():
        # new_x/new_y: start every line at the left margin, or fpdf2 runs
        # out of horizontal space after the first line.
        pdf.multi_cell(0, 10, _shape_urdu_line(raw_line),
                       new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        return tmp.name


def download_pdf_button(content, filename_prefix="expert"):
    try:
        pdf_path = create_pdf(content)
    except RuntimeError as exc:
        st.warning(f"PDF نہیں بن سکا: {exc}")
        return
    with open(pdf_path, "rb") as f:
        st.download_button("📄 PDF ڈاؤن لوڈ", f,
                           file_name=f"{filename_prefix}_{datetime.now():%Y%m%d_%H%M%S}.pdf")
