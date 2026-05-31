import streamlit as st

def load_styles():
    st.markdown("""
    <style>
    /* ══════════════════════════════════════
       GOOGLE FONT (URDU)
    ══════════════════════════════════════ */
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu&display=swap');

    /* ══════════════════════════════════════
       CSS VARIABLES – Light Mode (default)
    ══════════════════════════════════════ */
    :root {
        --bg-primary: #f9fbf9;
        --bg-secondary: #ffffff;
        --bg-sidebar: #e8f5e9;
        --text-primary: #1b5e20;
        --text-muted: #2e7d32;
        --accent: #2e7d32;
        --accent-light: #c8e6c9;
        --border: #c8e6c9;
        --card-bg: #ffffff;
        --card-shadow: rgba(0,0,0,0.05);
        --bubble-user-bg: #DCF8C6;
        --bubble-user-text: #075E54;
        --header-bg: #2e7d32;
        --header-text: #ffffff;
        --input-bg: #ffffff;
        --input-border: #c8e6c9;
        --input-text: #1b5e20;
        --btn-bg: #2e7d32;
        --btn-hover: #1b5e20;
        --btn-text: #ffffff;
    }

    /* ══════════════════════════════════════
       DARK MODE OVERRIDES
    ══════════════════════════════════════ */
    @media (prefers-color-scheme: dark) {
        :root {
            --bg-primary: #121212;
            --bg-secondary: #1e1e1e;
            --bg-sidebar: #1a2a1a;
            --text-primary: #c8e6c9;
            --text-muted: #81c784;
            --accent: #4caf50;
            --accent-light: #2e7d32;
            --border: #2e7d32;
            --card-bg: #1e1e1e;
            --card-shadow: rgba(0,255,0,0.05);
            --bubble-user-bg: #2e7d32;
            --bubble-user-text: #e8f5e9;
            --header-bg: #1b5e20;
            --header-text: #ffffff;
            --input-bg: #2a2a2a;
            --input-border: #4caf50;
            --input-text: #e8f5e9;
            --btn-bg: #4caf50;
            --btn-hover: #388e3c;
            --btn-text: #ffffff;
        }
        .stApp, body, [data-testid="stAppViewContainer"] {
            background-color: var(--bg-primary) !important;
            color: var(--text-primary) !important;
        }
        [data-testid="stSidebar"] {
            background-color: var(--bg-sidebar) !important;
            border-right: 2px solid var(--border) !important;
        }
        input, textarea, .stTextInput input, .stTextArea textarea, .stNumberInput input,
        .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] {
            background-color: var(--input-bg) !important;
            color: var(--input-text) !important;
            border: 1px solid var(--input-border) !important;
        }
        .stButton button, .stFormSubmitButton button {
            background-color: var(--btn-bg) !important;
            color: #ffffff !important;
        }
        .stButton button:hover {
            background-color: var(--btn-hover) !important;
        }
    }

    /* ══════════════════════════════════════
       BASE & GLOBAL STYLES
    ══════════════════════════════════════ */
    .stApp {
        background-color: var(--bg-primary) !important;
    }
    [data-testid="stAppViewContainer"] {
        color: var(--text-primary) !important;
    }
    [data-testid="stSidebar"] {
        background-color: var(--bg-sidebar) !important;
        border-right: 2px solid var(--border) !important;
    }
    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }

    /* Headings, labels, general text */
    h1, h2, h3, h4, h5, h6, p, label, .stMarkdown, .stCaption {
        color: var(--text-primary) !important;
    }

    /* Input fields */
    input, textarea, .stTextInput input, .stTextArea textarea, .stNumberInput input,
    .stSelectbox div[data-baseweb="select"], .stMultiSelect div[data-baseweb="select"] {
        background-color: var(--input-bg) !important;
        color: var(--input-text) !important;
        border: 1px solid var(--input-border) !important;
        border-radius: 8px !important;
    }
    ::placeholder {
        color: #6b8e6b !important;
    }

    /* Selectbox dropdown items */
    div[role="listbox"] li {
        background-color: var(--bg-secondary) !important;
        color: var(--text-primary) !important;
    }
    div[role="listbox"] li:hover {
        background-color: var(--accent-light) !important;
    }

    /* Buttons – TEXT ALWAYS WHITE */
    .stButton button, .stFormSubmitButton button {
        background-color: var(--btn-bg) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: bold !important;
    }
    .stButton button:hover {
        background-color: var(--btn-hover) !important;
    }

    /* Radio buttons */
    .stRadio div[role="radiogroup"] label {
        color: var(--text-primary) !important;
        background-color: var(--bg-secondary) !important;
        border: 1px solid var(--border) !important;
        border-radius: 10px !important;
        padding: 8px 16px !important;
    }

   /* Buttons – TEXT ALWAYS WHITE, no green */
.stButton > button,
.stFormSubmitButton > button,
button[kind="primary"] {
    color: #ffffff !important;
    background-color: var(--btn-bg) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: bold !important;
}
.stButton > button:hover,
.stFormSubmitButton > button:hover,
button[kind="primary"]:hover {
    background-color: var(--btn-hover) !important;
    color: #ffffff !important;
}
.stButton > button:focus,
.stFormSubmitButton > button:focus {
    color: #ffffff !important;
    outline: none !important;
}

    /* Download button */
    .stDownloadButton button {
        background-color: var(--accent-light) !important;
        color: var(--accent) !important;
        border: 1px solid var(--accent) !important;
    }

    /* ══════════════════════════════════════
       CUSTOM UI COMPONENTS
    ══════════════════════════════════════ */
    .urdu-card {
        font-family: 'Noto Nastaliq Urdu', serif;
        direction: rtl;
        text-align: right;
        font-size: 20px;
        color: var(--text-primary);
        background: var(--card-bg);
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px var(--card-shadow);
        margin-bottom: 15px;
        border-right: 10px solid var(--accent);
        line-height: 2.4;
    }
    .user-bubble {
        font-family: 'Noto Nastaliq Urdu', serif;
        direction: rtl;
        text-align: left;
        background: var(--bubble-user-bg);
        padding: 15px;
        border-radius: 15px 15px 0 15px;
        margin-bottom: 10px;
        color: var(--bubble-user-text);
        display: inline-block;
        float: left;
        clear: both;
        max-width: 80%;
    }
    .assistant-bubble {
        font-family: 'Noto Nastaliq Urdu', serif;
        direction: rtl;
        text-align: right;
        background: var(--card-bg);
        padding: 15px;
        border-radius: 15px 15px 15px 0;
        margin-bottom: 10px;
        border-right: 5px solid var(--accent);
        float: right;
        clear: both;
        max-width: 80%;
        color: var(--text-primary);
    }
    .stMarkdown table {
        width: 100%;
        direction: rtl;
        border-collapse: collapse;
        border-radius: 10px;
        overflow: hidden;
        margin: 20px 0;
    }
    .stMarkdown th {
        background-color: var(--accent) !important;
        color: white !important;
        padding: 12px !important;
        text-align: center !important;
    }
    .stMarkdown td {
        background-color: var(--card-bg) !important;
        color: var(--text-primary) !important;
        padding: 10px !important;
        text-align: center !important;
        border-bottom: 1px solid var(--border) !important;
    }
    .header-box {
        background: var(--header-bg);
        padding: 35px;
        border-radius: 0 0 35px 35px;
        color: var(--header-text);
        text-align: center;
        margin-top: -65px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    }

    /* ══════════════════════════════════════
       HEADER TEXT ALWAYS WHITE
    ══════════════════════════════════════ */
    .header-box h1,
    .header-box p {
        color: #ffffff !important;
    }

    @media (max-width: 600px) {
        .urdu-card, .user-bubble, .assistant-bubble { font-size: 16px; padding: 15px; }
        .header-box { padding: 20px; }
    }
    </style>
    """, unsafe_allow_html=True)
