# 🌾 Kisan AI - Agricultural Intelligence Assistant

**Empowering Farmers with AI-Driven Agricultural Solutions**

Kisan AI is an intelligent agricultural assistance platform designed to support Pakistani farmers with crop advice, disease detection from photos, fertilizer guidance, and mandi (market) rates — in Urdu, with voice input and audio answers. It runs as a Streamlit app backed by Groq's Llama models.

---

## ✨ Features

- 🤖 **AI-Powered Crop Advisory** – Chat with an agricultural expert in Urdu (text or voice)
- 🌱 **Disease Detection (Crop Doctor)** – Upload or photograph a crop; the AI checks its health and suggests treatment
- 🧪 **Fertilizer Advisor** – Fertilizer advice and per-bag rates for a crop, soil type, and area
- 💰 **Mandi Rates** – Current market rates for a crop across Pakistani cities
- 🔊 **Voice In / Voice Out** – Ask by microphone (Whisper transcription) and listen to answers (gTTS audio)
- 📄 **PDF / Text Download** – Save a diagnosis or chat as a file
- 🌐 **Urdu / English UI** – Full Urdu interface with an English option

Planned (not built yet): smart irrigation guidance, yield prediction, weather integration.

---

## 🛠️ Tech Stack

- **Frontend** – Streamlit
- **AI** – Groq (Llama 3.3 70B for text, Llama 3.2 11B Vision for photos, Whisper Large v3 for voice)
- **Audio** – gTTS, streamlit-mic-recorder
- **PDF export** – fpdf2
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
groq
gtts
streamlit-mic-recorder
pillow
fpdf
```

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Awaisranahmad/Kisan-Ai.git
cd Kisan-Ai
```

### 2. Set Up Your API Key

Copy the example secrets file and put your own key in it:

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
```

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

`secrets.toml` is git-ignored and must never be committed. You can also enter a key inside the app (sidebar → API Settings) without saving it to a file.

### 3. Run the Application

```bash
streamlit run app.py
```

### 4. Access the App

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

Tests cover image processing (`utils.process_image_to_b64`), graceful PDF/audio failure, the no-API-key guard in the AI engine, and a regression check that no real secrets file is tracked by git.

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
├── ai_engine.py            # Groq chat/vision calls + Urdu system prompt
├── config.py               # Groq client setup + Urdu/English UI texts
├── utils.py                # Image processing, audio playback, PDF export
├── ui_styles.py            # CSS styling
├── components/
│   ├── chat.py             # AI chat screen
│   ├── crop_doctor.py      # Photo-based crop diagnosis
│   ├── fertilizer.py       # Fertilizer advice + rates
│   ├── mandi.py            # Mandi rates
│   └── gallery.py          # Crop photo gallery
├── data/
│   └── crop_encyclopedia.py # Crop reference data (currently unused by the app)
├── tests/
│   └── test_kisan.py       # Pytest suite
├── requirements.txt        # Python dependencies
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

Kisan AI provides recommendations based on AI analysis. Always cross-reference critical farming decisions with local agricultural extension services or qualified agronomists. Mandi rates and fertilizer prices come from the AI model and may be outdated — verify before buying or selling.

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
