import streamlit as st

def load_styles():
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
    @media (max-width: 600px) {
        .urdu-card, .user-bubble, .assistant-bubble { font-size: 16px; padding: 15px; }
        .header-box { padding: 20px; }
    }
    </style>
    """, unsafe_allow_html=True)
