"""AI models — ALL in ONE file.

To change a model in the future, edit ONLY this file. Nothing else in the
app hardcodes a model name.

How it works
------------
The app talks to every provider through the OpenAI-compatible chat API
(`client.chat.completions.create`). Groq, OpenAI, DeepSeek, OpenRouter,
xAI, Gemini and most other providers expose that same API — only the
server address (``base_url``) and the API key change. So any provider's
model can be used by adding one entry to ``PROVIDERS`` and naming it
below.

How to switch models
---------------------
1. Chat (text) model: change ``CHAT_MODEL``.
2. Vision model (crop photo diagnosis): change ``VISION_MODEL``.
3. If a model is retired, change the one line and the app works again.
   A fallback model is tried automatically if the main one fails
   (see ``CHAT_MODEL_FALLBACK`` / ``VISION_MODEL_FALLBACK``).

How to add a new provider
--------------------------
Add one entry to ``PROVIDERS``::

    "myprovider": {
        "base_url": "https://api.myprovider.com/v1",
        "api_key_name": "MYPROVIDER_API_KEY",  # key name in secrets.toml / .env
    },

Then use it in ``CHAT_MODEL`` / ``VISION_MODEL`` like::

    CHAT_MODEL = {"provider": "myprovider", "model": "some-model-id"}

Current models (verified 2026-11-21)
-------------------------------------
The old models (``llama-3.2-11b-vision-preview``, retired 2025-04-14, and
``llama-3.3-70b-versatile``, retired 2026-08-16) no longer answer on
Groq. The replacements below are Groq's own recommendations.
"""

# --- Providers: name -> server address + key name ---------------------------
# ``api_key_name`` is the key looked up in .streamlit/secrets.toml, in a
# .env file, and in the environment. The user can also paste a key in the
# app's sidebar — that key is used for the active provider.
PROVIDERS = {
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "api_key_name": "GROQ_API_KEY",
    },
    "openai": {
        "base_url": "https://api.openai.com/v1",
        "api_key_name": "OPENAI_API_KEY",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "api_key_name": "DEEPSEEK_API_KEY",
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "api_key_name": "OPENROUTER_API_KEY",
    },
    "gemini": {
        # Google's OpenAI-compatible endpoint.
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "api_key_name": "GEMINI_API_KEY",
    },
}

# --- Active models: change ONLY these lines to switch models ----------------
# Text chat, fertilizer advice, mandi explanations.
CHAT_MODEL = {"provider": "groq", "model": "openai/gpt-oss-120b"}
# Tried automatically if CHAT_MODEL fails (e.g. the model was retired).
CHAT_MODEL_FALLBACK = {"provider": "groq", "model": "openai/gpt-oss-20b"}

# Crop photo diagnosis (must be a vision model — it reads images).
VISION_MODEL = {
    "provider": "groq",
    "model": "meta-llama/llama-4-scout-17b-16e-instruct",
}
# Tried automatically if VISION_MODEL fails.
VISION_MODEL_FALLBACK = {
    "provider": "groq",
    "model": "meta-llama/llama-4-maverick-17b-128e-instruct",
}

# --- Voice transcription (speech -> text) -----------------------------------
# Model per provider. A provider not listed here has no transcription —
# voice input is then skipped instead of crashing.
TRANSCRIBE_MODELS = {
    "groq": "whisper-large-v3",
    "openai": "whisper-1",
}


def get_provider(name):
    """Return the provider entry for ``name`` (raises KeyError if unknown)."""
    return PROVIDERS[name]


def model_chain(primary, fallback):
    """Return [primary, fallback] as a list, skipping a duplicate fallback."""
    chain = [primary]
    if fallback and fallback != primary:
        chain.append(fallback)
    return chain
