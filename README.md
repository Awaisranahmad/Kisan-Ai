# 🌾 Kisan AI - Agricultural Intelligence Assistant

**Empowering Farmers with AI-Driven Agricultural Solutions**

Kisan AI is an intelligent agricultural assistance platform designed to support Pakistani farmers with crop advice, disease detection from photos, fertilizer guidance, and mandi (market) rates — in Urdu, with voice input and audio answers. It runs as a Streamlit app backed by Groq's Llama models.

---

## ✨ Features

- 🤖 **AI-Powered Crop Advisory** – Chat with an agricultural expert in Urdu (text or voice)
- 🌱 **Disease Detection (Crop Doctor)** – Upload or photograph a crop; the AI checks its health and suggests treatment
- 🧪 **Fertilizer Advisor** – Fertilizer advice and per-bag rates for a crop, soil type, and area
- 💰 **Mandi Rates (LIVE)** – Real daily rates from Punjab AMIS (amis.pk), not AI guesses — with the source and date shown
- 🔊 **Voice In / Voice Out** – Ask by microphone (Whisper transcription) and listen to answers (gTTS audio)
- 📄 **PDF / Text Download** – Save a diagnosis or chat as a PDF (proper Urdu script) or text file
- 🌐 **Urdu / English UI** – Full Urdu interface with an English option
- 🔧 **Any AI provider** – Models live in one file (`models.py`): Groq by default, but any OpenAI-compatible provider's model works (OpenAI, DeepSeek, OpenRouter, Gemini...)

Planned (not built yet): smart irrigation guidance, yield prediction, weather integration.

---

## 🛠️ Tech Stack

- **Frontend** – Streamlit
- **AI** – Any OpenAI-compatible provider (default: Groq — `openai/gpt-oss-120b` for text, `meta-llama/llama-4-scout-17b-16e-instruct` for photos, Whisper Large v3 for voice). All models are set in `models.py` — that one file is the only place a model ever needs changing.
- **Audio** – gTTS, streamlit-mic-recorder
- **PDF export** – fpdf2 with a bundled Noto Naskh Arabic font (proper Urdu script)
- **Live mandi rates** – Punjab AMIS (amis.pk) daily prices, fetched with requests + BeautifulSoup
- **Language** – Python 3.10+

---

## 📦 Requirements

- Python 3.10 or higher
- Groq API key ([Get one for free](https://console.groq.com/))
- Modern web browser

Install dependencies:

```bash
pip install -r requirements.txt
```

### Required Python Packages

```
streamlit
openai>=1.0
gtts
streamlit-mic-recorder
pillow
fpdf2>=2.7
arabic-reshaper>=3.0
python-bidi>=0.6
requests>=2.0
beautifulsoup4>=4.0
python-dotenv>=1.0
```

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Awaisranahmad/Kisan-Ai.git
cd Kisan-Ai
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up Your API Key (3 tareeqay — koi aik kaafi hai)

Sab se pehle key lein: Groq ki free key [console.groq.com/keys](https://console.groq.com/keys) se milti hai (sign up karein, "Create API Key" dabayein).

**Tareeqa 1 — App ke andar (sab se asaan):** App chalayein, sidebar mein "🔑 API سیٹنگز" kholein, key paste karein, "اپنی کی استعمال کریں" dabayein. Key sirf aap ke browser session mein rehti hai, file mein save nahi hoti.

**Tareeqa 2 — secrets file (Streamlit Cloud ke liye):**

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

Phir `.streamlit/secrets.toml` mein apni key likhein:

```toml
GROQ_API_KEY = "gsk_apni_asli_key_yahan_dalein"
```

`secrets.toml` git-ignored hai aur kabhi commit nahi honi chahiye.

**Tareeqa 3 — .env file (local run ke liye):**

```bash
cp .env.example .env
```

Phir `.env` mein likhein:

```env
GROQ_API_KEY=your-groq-key-here
```

### 4. Model kaisa badalna hai (sirf aik file — `models.py`)

Saare models aik hi file mein hain: **`models.py`**. Model badalne ke liye aur kahin jaane ki zaroorat nahi — sirf is file ki ye lines badlein:

```python
CHAT_MODEL = {"provider": "groq", "model": "openai/gpt-oss-120b"}
VISION_MODEL = {"provider": "groq", "model": "meta-llama/llama-4-scout-17b-16e-instruct"}
```

Agar model band ho jaye to app khud backup model (`CHAT_MODEL_FALLBACK` / `VISION_MODEL_FALLBACK`) pe chal parti hai.

**Kisi bhi aur company ka model kaise lagayein?** `models.py` mein `PROVIDERS` mein aik entry add karein — sirf server ka address aur key ka naam:

```python
"myprovider": {
    "base_url": "https://api.myprovider.com/v1",
    "api_key_name": "MYPROVIDER_API_KEY",
},
```

Phir usay `CHAT_MODEL` mein use karein:

```python
CHAT_MODEL = {"provider": "myprovider", "model": "some-model-id"}
```

Pehle se maujood providers: Groq, OpenAI, DeepSeek, OpenRouter, Gemini. In mein se kisi ki bhi key `.env` ya `secrets.toml` mein daal dein — bas wohi key chahiye jo provider aap `models.py` mein chunein.

### 5. Run the Application

```bash
streamlit run app.py
```

### 6. Access the App

Open your browser and navigate to:

```
http://localhost:8501
```

---

## 🧪 Tests

Run the test suite (no API key needed):

```bash
pip install pytest
python -m pytest tests/ -v
```

Tests cover image processing (`utils.process_image_to_b64`), PDF building with real Urdu text (font bundled, shaping correct), the model registry in `models.py`, AI fallback when a model is retired, plain error messages (wrong key / rate limit), voice transcription (never crashes), live mandi-rate parsing from AMIS Punjab (offline sample HTML), and a regression check that no real secrets file is tracked by git. 27 tests, no API key needed.

---

## 💡 Usage Examples

### Get Crop Recommendations

> **Farmer:** I want to grow crops in Punjab with the Rabi season approaching. What should I plant?
> **Kisan AI:** [Provides region-specific, season-appropriate crop recommendations in Urdu]

### Disease Detection

1. Click the image upload button
2. Take or upload a photo of your crop
3. AI analyzes and provides disease identification and treatment options in Urdu

### Check Market Prices

> **Farmer:** What's the current mandi rate for wheat?
> **Kisan AI:** [Shows a table of rates across Pakistani cities in Urdu]

---

## 📂 Project Structure

```
Kisan-Ai/
├── app.py                  # Main Streamlit application (routing, sidebar)
├── ai_engine.py            # Chat/vision calls with fallback + plain error messages
├── models.py               # ALL AI models + providers in ONE file — edit only this to change a model
├── mandi_data.py           # Live mandi rates from Punjab AMIS (amis.pk)
├── config.py               # AI client setup (any provider) + Urdu/English UI texts
├── utils.py                # Image processing, audio playback, PDF export (Urdu font bundled)
├── ui_styles.py            # CSS styling
├── components/
│   ├── chat.py             # AI chat screen
│   ├── crop_doctor.py      # Photo-based crop diagnosis
│   ├── fertilizer.py       # Fertilizer advice + rates
│   ├── mandi.py            # Mandi rates (live AMIS data first, labelled AI estimate as fallback)
│   └── gallery.py          # Crop photo gallery
├── data/
│   └── crop_encyclopedia.py # Crop reference data (currently unused by the app)
├── assets/
│   └── fonts/
│       └── NotoNaskhArabic.ttf # Bundled Urdu font for PDF export
├── tests/
│   └── test_kisan.py       # Pytest suite (27 tests)
├── requirements.txt        # Python dependencies
├── .env.example            # Template — copy to .env (never commit the real one)
└── .streamlit/
    ├── secrets.toml.example # Template — copy to secrets.toml (never commit the real one)
    └── secrets.toml        # Your real key (git-ignored, not in the repo)
```

---

## 🔒 Security & Privacy

- **API keys are never committed** – The key lives in `.streamlit/secrets.toml`, which is git-ignored; only a placeholder `.example` file is in the repo. The old tracked `secrets.toml` held only a placeholder value ("put your real key here"), never a real key — it was removed on 2026-11-21 so a real key can never be committed by accident.
- **User data is not stored** – Chats and diagnoses live only in the browser session.
- **AI output is rendered as text** – Model responses are shown in styled cards, not executed.

---

## 📝 Changelog

- **2026-11-21 — Models, PDF, live mandi rates, any provider:** the old models were retired by Groq (`llama-3.2-11b-vision-preview` shut down 2025-04-14, `llama-3.3-70b-versatile` shut down 2026-08-16), so the app's AI had stopped working. All models now live in one new file, `models.py` — change only that file to switch models, and the app falls back automatically if a model is retired. Any OpenAI-compatible provider works (Groq, OpenAI, DeepSeek, OpenRouter, Gemini). PDF download fixed: bundled Noto Naskh Arabic font + proper Urdu shaping, and failures now show a message instead of silently doing nothing. Mandi rates are now LIVE from Punjab AMIS (amis.pk) with source + date shown; if live data is unavailable the AI estimate is clearly labelled as an estimate. Errors now say what is wrong (wrong key / rate limit / retired model) instead of one generic message. Voice transcription no longer crashes the app when it fails. Tests grew to 27 (`tests/test_kisan.py`).

- **2026-11-21 — Repo hygiene + tests:** removed the tracked `.streamlit/secrets.toml` (it held only a placeholder, never a real key) so a real key can never be committed by accident, added `.gitignore` + `secrets.toml.example`, added MIT `LICENSE`, added a pytest suite (`tests/test_kisan.py`, 9 tests), and corrected the README (requirements, project structure, features).

---

## 🤝 Contributing

Contributions are welcome! To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please ensure all contributions follow the project's code standards and include appropriate documentation.

---

## ⚠️ Disclaimer

Kisan AI provides recommendations based on AI analysis. Always cross-reference critical farming decisions with local agricultural extension services or qualified agronomists. Mandi rates shown are the live daily prices from Punjab AMIS (amis.pk) with the date shown; when live data is unavailable the app labels the AI estimate clearly as an estimate. Fertilizer prices come from the AI model and may be outdated — verify before buying or selling.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 📞 Support & Contact

For issues, questions, or suggestions:

- 🐛 **GitHub Issues**: [Open an issue](https://github.com/Awaisranahmad/Kisan-Ai/issues)
- 💬 **Discussions**: [Start a discussion](https://github.com/Awaisranahmad/Kisan-Ai/discussions)

---

## 🙏 Acknowledgements

- [Groq](https://groq.com/) for powerful LLM APIs
- [Streamlit](https://streamlit.io/) for the amazing web framework
- Agricultural experts and farming communities for guidance

---

**Made with 🌾 for the farming community**

*Bringing AI to the fields, one farm at a time.*
