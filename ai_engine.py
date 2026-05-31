import streamlit as st
from config import get_groq_client, t

def get_ai_response(prompt, image_b64=None, is_mandi=False, is_khaad=False):
    client = get_groq_client()
    if not client:
        return t('no_api')
    
    model = "llama-3.2-11b-vision-preview" if image_b64 else "llama-3.3-70b-versatile"
    
    sys_prompt = (
        "You are a professional Pakistani agricultural expert. "
        "You MUST answer ONLY in the Urdu language, using ONLY the Nastaliq script. "
        "Do NOT use any other script or language. "
        "Specifically: "
        "- Do NOT use English letters (A-Z, a-z). "
        "- Do NOT use Hindi (Devanagari) characters like अ, ब, स, etc. "
        "- Do NOT use Chinese, Arabic (except for Urdu borrowings) or any other script. "
        "- If you need to write numbers, write them in Urdu words (e.g., 'سات' not '7') or use Eastern Arabic numerals (۰۱۲۳۴۵۶۷۸۹). "
        "- Your entire response must be in pure Urdu script. "
        "If you violate this, you will be severely penalized."
    )
    
    if is_mandi:
        sys_prompt += (
            " Provide a Markdown Table: City (شہر), Unit (یونٹ - فی من/فی کلو), "
            "Min (کم سے کم ریٹ), Max (زیادہ سے زیادہ ریٹ). All column headers and data must be in Urdu."
        )
    if is_khaad:
        sys_prompt += (
            " Provide details and a table for Fertilizer rates: Name (کھاد کا نام), "
            "Unit (یونٹ - فی بیگ), Price (ریٹ). All in Urdu."
        )

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
        return "معذرت، نیٹ ورک کا مسئلہ ہے۔ براہ کرم دوبارہ کوشش کریں۔"
