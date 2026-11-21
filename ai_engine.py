"""AI calls. Models come from ``models.py`` — nothing is hardcoded here.

Behaviour:
- The primary model is tried first; if it fails because the model is
  gone/retired, the fallback model from ``models.py`` is tried.
- Errors are reported in plain words instead of one generic message:
  wrong key, rate limit, retired model, or a real network problem.
"""
from config import get_ai_client, t
from models import (
    CHAT_MODEL,
    CHAT_MODEL_FALLBACK,
    TRANSCRIBE_MODELS,
    VISION_MODEL,
    VISION_MODEL_FALLBACK,
    model_chain,
)


def _is_model_error(exc):
    """True when the error means 'this model does not exist any more'."""
    status = getattr(exc, "status_code", None)
    if status == 404:
        return True
    text = str(exc).lower()
    return any(
        phrase in text
        for phrase in (
            "model_not_found",
            "model not found",
            "decommissioned",
            "does not exist",
            "is not a valid model",
        )
    )


def _is_auth_error(exc):
    status = getattr(exc, "status_code", None)
    if status == 401:
        return True
    text = str(exc).lower()
    return "authentication" in text or "invalid api key" in text or "incorrect api key" in text


def _is_rate_limit(exc):
    status = getattr(exc, "status_code", None)
    if status == 429:
        return True
    return "rate limit" in str(exc).lower() or "rate_limit" in str(exc).lower()


def _chat_complete(client, messages, chain):
    """Try each model in ``chain`` in order; return the first reply text."""
    last_error = None
    for entry in chain:
        try:
            chat = client.chat.completions.create(model=entry["model"], messages=messages)
            return chat.choices[0].message.content
        except Exception as exc:  # noqa: BLE001 - classified below
            last_error = exc
            if _is_model_error(exc):
                continue  # try the fallback model
            raise
    raise last_error


def get_ai_response(prompt, image_b64=None, is_mandi=False, is_khaad=False):
    client = get_ai_client()
    if not client:
        return t('no_api')

    if image_b64:
        chain = model_chain(VISION_MODEL, VISION_MODEL_FALLBACK)
    else:
        chain = model_chain(CHAT_MODEL, CHAT_MODEL_FALLBACK)

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
        return _chat_complete(client, messages, chain)
    except Exception as exc:  # noqa: BLE001 - user-facing message, not a crash
        if _is_auth_error(exc):
            return t('key_error')
        if _is_rate_limit(exc):
            return t('rate_limit')
        if _is_model_error(exc):
            return t('model_error')
        return "معذرت، نیٹ ورک کا مسئلہ ہے۔ براہ کرم دوبارہ کوشش کریں۔"


def transcribe_audio(audio_bytes):
    """Speech -> Urdu text using the active provider's whisper model.

    Returns the transcribed text, or None when transcription is not
    available (no key, provider has no speech model, or the call fails).
    Never raises — callers treat None as 'no voice input'.
    """
    if not audio_bytes:
        return None
    client = get_ai_client()
    if not client:
        return None
    model = TRANSCRIBE_MODELS.get(CHAT_MODEL["provider"])
    if not model:
        return None
    try:
        result = client.audio.transcriptions.create(
            file=("a.wav", audio_bytes),
            model=model,
            language="ur",
        )
        return result.text
    except Exception:
        return None
