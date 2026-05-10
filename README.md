# 🌾 Kisan AI - Agricultural Intelligence Assistant

**Empowering Farmers with AI-Driven Agricultural Solutions**

Kisan AI is an intelligent agricultural assistance platform designed to support farmers with real-time insights, crop recommendations, disease detection, and market information. Leveraging advanced AI models and machine learning, this tool bridges the gap between modern technology and traditional farming.

---

## ✨ Features

- 🤖 **AI-Powered Crop Advisory** – Get personalized recommendations for crop selection, planting schedules, and cultivation practices
- 🌱 **Disease & Pest Detection** – Upload images to identify crop diseases and receive treatment suggestions
- 💧 **Smart Irrigation Guidance** – Optimize water usage with weather-based irrigation recommendations
- 📊 **Crop Yield Prediction** – AI-powered forecasts for expected yields based on historical data
- 🛒 **Market Intelligence** – Real-time commodity prices and market trends
- 🌤️ **Weather Integration** – Location-based weather forecasts and alerts
- 💬 **Interactive Chat Support** – 24/7 agricultural expert assistant
- 📱 **Mobile-Friendly UI** – Responsive design for farmers on the go

---

## 🎯 Use Cases

- **New Farmers** – Learn best practices and get guided recommendations
- **Experienced Farmers** – Optimize yield and reduce costs with data-driven insights
- **Agricultural Extension Workers** – Support village-level farming communities
- **Agricultural Businesses** – Integrate AI insights into supply chain planning

---

## 🛠️ Tech Stack

- **Backend Framework** – Python
- **AI/ML Engine** – LangChain, Groq (Llama models)
- **Frontend** – Streamlit
- **Database** – Python-based data structures (or PostgreSQL/MongoDB)
- **APIs** – Weather APIs, Agricultural data sources
- **Language** – Python 3.10+

---

## 📦 Requirements

- Python 3.10 or higher
- Groq API key ([Get one for free](https://console.groq.com/))
- Modern web browser

### Required Python Packages

```
streamlit
langchain-groq
langchain-core
python-dotenv
requests
pillow
```

Install dependencies:

```bash
pip install streamlit langchain-groq langchain-core python-dotenv requests pillow
```

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Awaisranahmad/Kisan-Ai.git
cd Kisan-Ai
```

### 2. Set Up Environment Variables

Create a `.streamlit/secrets.toml` file:

```toml
GROQ_API_KEY = "your_groq_api_key_here"
```

Or set an environment variable:

```bash
export GROQ_API_KEY="your_groq_api_key_here"
```

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

## 💡 Usage Examples

### Get Crop Recommendations

> **Farmer:** I want to grow crops in Maharashtra with monsoon season approaching. What should I plant?  
> **Kisan AI:** [Provides region-specific, season-appropriate crop recommendations]

### Disease Detection

1. Click the image upload button
2. Take or upload a photo of your crop
3. AI analyzes and provides disease identification and treatment options

### Check Market Prices

> **Farmer:** What's the current market price for wheat?  
> **Kisan AI:** [Shows real-time commodity prices across major markets]

---

## 📂 Project Structure

```
Kisan-Ai/
├── app.py                 # Main Streamlit application
├── utils/
│   ├── crop_advisor.py    # Crop recommendation logic
│   ├── disease_detector.py # Disease detection module
│   ├── market_data.py     # Market price integration
│   └── weather.py         # Weather API integration
├── data/
│   ├── crops.json         # Crop database
│   └── regions.json       # Region-specific data
├── requirements.txt       # Python dependencies
└── .streamlit/
    └── secrets.toml       # API keys (not in version control)
```

---

## 🔒 Security & Privacy

- **Secure API Keys** – Never hardcoded; stored in environment variables
- **Data Privacy** – User data is not stored; only processed for insights
- **Secure Communications** – HTTPS for all API calls
- **Model Safety** – AI responses are validated before presentation

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

Kisan AI provides recommendations based on AI analysis. Always cross-reference critical farming decisions with local agricultural extension services or qualified agronomists.

---

## 📄 License

This project is open-source and available under the [MIT License](LICENSE).

---

## 📞 Support & Contact

For issues, questions, or suggestions:

- 📧 **Email**: [Your contact email]
- 🐛 **GitHub Issues**: [Open an issue](https://github.com/Awaisranahmad/Kisan-Ai/issues)
- 💬 **Discussions**: [Start a discussion](https://github.com/Awaisranahmad/Kisan-Ai/discussions)

---

## 🙏 Acknowledgements

- [Groq](https://groq.com/) for powerful LLM APIs
- [Streamlit](https://streamlit.io/) for the amazing web framework
- [LangChain](https://www.langchain.com/) for AI orchestration
- Agricultural experts and farming communities for guidance

---

**Made with 🌾 for the farming community**

*Bringing AI to the fields, one farm at a time.*
