import streamlit as st
from config import get_groq_client, t

def get_ai_response(prompt, image_b64=None, is_mandi=False, is_khaad=False):
    client = get_groq_client()
    if not client:
        return t('no_api')
    
    model = "llama-3.2-11b-vision-preview" if image_b64 else "llama-3.3-70b-versatile"
    sys_prompt = "You are a professional Agri-Expert from Pakistan. "
    
    if st.session_state.lang == "ur":
        sys_prompt += "Respond ONLY in Urdu script. No Hindi/English."
    else:
        sys_prompt += "Respond in English only."

    if is_mandi:
        sys_prompt += " Provide a Markdown Table: City (شہر), Unit (یونٹ - فی من/فی کلو), Min, Max."
    if is_khaad:
        sys_prompt += " Provide details and a table for Fertilizer rates: Name (کھاد کا نام), Unit (یونٹ - فی بیگ), Price (ریٹ)."

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
        return f"⚠️ Error: {str(e)}"
