import streamlit as st
import google.generativeai as genai
from PIL import Image

# --- 1. API Key Setup (Streamlit Secrets Version) ---
# GitHub par key expose nahi hogi, hum Streamlit Cloud mein 'GEMINI_API_KEY' set karenge.
try:
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = st.sidebar.text_input("Enter Gemini API Key:", type="password")

    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
    else:
        st.warning("⚠️ API Key missing! Please set it in Streamlit Secrets.")
except Exception as e:
    st.error(f"Error connecting to AI: {e}")

# --- 2. UI Customization ---
st.set_page_config(page_title="Kisan AI Assistant", page_icon="🌾", layout="centered")

st.title("🌾 Kisan AI: Crop Doctor & Mandi Advisor")
st.markdown("""
    **Khush Amdeed!** Ye AI chatbot kisano ki madad ke liye banaya gaya hai. 
    Aap fasal ki beemari check kar sakte hain aur mandi ke rates jaan sakte hain.
""")
st.divider()

# --- 3. Sidebar Navigation ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2316/2316334.png", width=100)
    option = st.radio(
        'Main Menu:',
        ('📸 Crop Doctor', '💰 Mandi Advice', '💬 Agri Chat (Urdu)')
    )

# --- FEATURE 1: CROP DOCTOR ---
if option == '📸 Crop Doctor':
    st.header("Crop Disease Identifier")
    st.info("Fasal ke kharab hissay ki wazay (clear) photo upload karein.")
    
    uploaded_file = st.file_uploader("Upload Leaf Image", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Sample', use_container_width=True)
        
        if st.button("Beemari Check Karein"):
            with st.spinner('AI analysis kar raha hai...'):
                prompt = "Analyze this crop image. 1. Identify disease. 2. Give organic solution. 3. Give chemical solution. Answer in URDU for a farmer."
                response = model.generate_content([prompt, image])
                st.success("AI ka Mashwara:")
                st.write(response.text)

# --- FEATURE 2: MANDI ADVISOR ---
elif option == '💰 Mandi Advice':
    st.header("Mandi Price Trend")
    crop = st.text_input("Fasal ka naam (e.g. Tomato, Wheat):")
    if st.button("Check Trends"):
        with st.spinner('Fetching market data...'):
            prompt = f"Act as a Pakistani agriculture expert. Tell current market trends for {crop} and advice the farmer in Urdu."
            response = model.generate_content(prompt)
            st.info(response.text)

# --- FEATURE 3: GENERAL CHAT ---
else:
    st.header("Agri Help (Urdu)")
    user_query = st.text_input("Apna sawal yahan likhein:")
    if st.button("Send"):
        with st.spinner('Thinking...'):
            prompt = f"Answer this agricultural question in simple Urdu: {user_query}"
            response = model.generate_content(prompt)
            st.markdown(f"**AI:** {response.text}")
