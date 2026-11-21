"""Tests for Kisan-Ai helpers.

Run from the repo root:  python -m pytest tests/ -v
Requires the app dependencies plus pytest (see README, Tests section).

These tests deliberately avoid a live API key and a running Streamlit app:
pure helpers are tested directly, and the AI guard is tested with the
client monkeypatched.
"""

import base64
import io
import os
import subprocess
import sys
from types import SimpleNamespace

import pytest
from PIL import Image

# Make the repo root importable no matter where pytest is invoked from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _make_image(width, height, mode="RGB", color="green"):
    img = Image.new(mode, (width, height), color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_process_image_valid_returns_b64_jpeg():
    from utils import process_image_to_b64

    result = process_image_to_b64(_make_image(400, 300))
    assert isinstance(result, str)
    raw = base64.b64decode(result)
    assert raw[:2] == b"\xff\xd8"  # JPEG magic bytes
    out = Image.open(io.BytesIO(raw))
    assert out.size == (400, 300)


def test_process_image_invalid_returns_none():
    from utils import process_image_to_b64

    assert process_image_to_b64(io.BytesIO(b"not an image")) is None


def test_process_image_downsamples_large_image():
    from utils import process_image_to_b64

    result = process_image_to_b64(_make_image(2000, 1500))
    assert isinstance(result, str)
    out = Image.open(io.BytesIO(base64.b64decode(result)))
    assert out.size[0] <= 800 and out.size[1] <= 800


def test_process_image_converts_rgba_to_rgb():
    from utils import process_image_to_b64

    result = process_image_to_b64(_make_image(100, 100, mode="RGBA"))
    assert isinstance(result, str)
    out = Image.open(io.BytesIO(base64.b64decode(result)))
    assert out.mode == "RGB"


def test_create_pdf_builds_valid_pdf_for_urdu_text(tmp_path):
    """PDF export must work now that the font is bundled in the repo."""
    from utils import create_pdf

    path = create_pdf("گندم کی فصل کیسی ہے؟\n**اہم** نکات #1")
    try:
        assert os.path.exists(path)
        with open(path, "rb") as f:
            header = f.read(5)
            f.seek(0, os.SEEK_END)
            size = f.tell()
        assert header == b"%PDF-"
        assert size > 1000, "PDF looks empty"
    finally:
        if os.path.exists(path):
            os.remove(path)


def test_create_pdf_raises_clear_error_without_font(monkeypatch):
    """A missing font must raise a plain message, not silently hide the button."""
    import utils

    monkeypatch.setattr(utils, "FONT_PATH", "/nonexistent/NotoNaskhArabic.ttf")
    with pytest.raises(RuntimeError, match="font"):
        utils.create_pdf("test")


def test_clean_markdown_strips_formatting():
    from utils import _clean_markdown

    assert _clean_markdown("**اہم** # سرخی | جدول") == "اہم  سرخی   جدول"


# --- models.py: the one-file registry ---------------------------------------

def test_model_registry_providers_have_base_url_and_key():
    from models import PROVIDERS

    assert PROVIDERS, "no providers configured"
    for name, entry in PROVIDERS.items():
        assert entry["base_url"].startswith("https://"), name
        assert entry["api_key_name"], name


def test_active_models_reference_known_providers_and_differ_from_fallback():
    from models import (
        CHAT_MODEL,
        CHAT_MODEL_FALLBACK,
        PROVIDERS,
        VISION_MODEL,
        VISION_MODEL_FALLBACK,
    )

    for entry in (CHAT_MODEL, CHAT_MODEL_FALLBACK, VISION_MODEL, VISION_MODEL_FALLBACK):
        assert entry["provider"] in PROVIDERS, entry
        assert entry["model"], entry
    assert CHAT_MODEL != CHAT_MODEL_FALLBACK
    assert VISION_MODEL != VISION_MODEL_FALLBACK


def test_transcribe_models_reference_known_providers():
    from models import PROVIDERS, TRANSCRIBE_MODELS

    for provider in TRANSCRIBE_MODELS:
        assert provider in PROVIDERS


def test_model_chain_skips_duplicate_fallback():
    from models import model_chain

    primary = {"provider": "groq", "model": "m1"}
    assert model_chain(primary, primary) == [primary]
    fallback = {"provider": "groq", "model": "m2"}
    assert model_chain(primary, fallback) == [primary, fallback]


# --- ai_engine: fallback + plain error messages ------------------------------

class _ApiError(Exception):
    def __init__(self, status_code, message=""):
        self.status_code = status_code
        super().__init__(message)


class _FakeChatReply:
    def __init__(self, text):
        self.choices = [SimpleNamespace(message=SimpleNamespace(content=text))]


class _FakeClient:
    """OpenAI-compatible stub: behaviour maps model id -> 'ok' or exception."""

    def __init__(self, behaviour, transcript_text="transcribed text"):
        self._behaviour = behaviour
        self.calls = []
        self._transcript_text = transcript_text
        self.chat = SimpleNamespace(completions=self)
        self.audio = SimpleNamespace(transcriptions=self)

    def create(self, model=None, messages=None, file=None, language=None):
        if file is not None:  # transcription call
            return SimpleNamespace(text=self._transcript_text)
        self.calls.append(model)
        action = self._behaviour.get(model, "ok")
        if action == "ok":
            return _FakeChatReply(f"reply from {model}")
        raise action


def test_ai_response_uses_fallback_when_primary_model_is_gone(monkeypatch):
    """A retired primary model must not break the app — fallback answers."""
    import ai_engine
    from models import CHAT_MODEL, CHAT_MODEL_FALLBACK

    gone = _ApiError(404, "model_not_found")
    client = _FakeClient({CHAT_MODEL["model"]: gone})
    monkeypatch.setattr(ai_engine, "get_ai_client", lambda: client)
    monkeypatch.setattr(ai_engine, "t", lambda key: key)
    reply = ai_engine.get_ai_response("test question")
    assert reply == f"reply from {CHAT_MODEL_FALLBACK['model']}"
    assert client.calls == [CHAT_MODEL["model"], CHAT_MODEL_FALLBACK["model"]]


def test_ai_response_reports_wrong_key_plainly(monkeypatch):
    import ai_engine
    from models import CHAT_MODEL

    client = _FakeClient({CHAT_MODEL["model"]: _ApiError(401, "invalid api key")})
    monkeypatch.setattr(ai_engine, "get_ai_client", lambda: client)
    monkeypatch.setattr(ai_engine, "t", lambda key: key)
    assert ai_engine.get_ai_response("hi") == "key_error"


def test_ai_response_reports_rate_limit_plainly(monkeypatch):
    import ai_engine
    from models import CHAT_MODEL

    client = _FakeClient({CHAT_MODEL["model"]: _ApiError(429, "rate limit")})
    monkeypatch.setattr(ai_engine, "get_ai_client", lambda: client)
    monkeypatch.setattr(ai_engine, "t", lambda key: key)
    assert ai_engine.get_ai_response("hi") == "rate_limit"


def test_ai_response_reports_retired_models_when_both_fail(monkeypatch):
    import ai_engine
    from models import CHAT_MODEL, CHAT_MODEL_FALLBACK

    gone = _ApiError(404, "model_not_found")
    client = _FakeClient({CHAT_MODEL["model"]: gone, CHAT_MODEL_FALLBACK["model"]: gone})
    monkeypatch.setattr(ai_engine, "get_ai_client", lambda: client)
    monkeypatch.setattr(ai_engine, "t", lambda key: key)
    assert ai_engine.get_ai_response("hi") == "model_error"


def test_ai_response_uses_vision_model_for_images(monkeypatch):
    import ai_engine
    from models import VISION_MODEL

    client = _FakeClient({})
    monkeypatch.setattr(ai_engine, "get_ai_client", lambda: client)
    monkeypatch.setattr(ai_engine, "t", lambda key: key)
    reply = ai_engine.get_ai_response("check crop", image_b64="aGVsbG8=")
    assert reply == f"reply from {VISION_MODEL['model']}"
    assert client.calls == [VISION_MODEL["model"]]


def test_transcribe_audio_returns_text_and_never_raises(monkeypatch):
    import ai_engine

    monkeypatch.setattr(ai_engine, "get_ai_client", lambda: _FakeClient({}))
    assert ai_engine.transcribe_audio(b"fake-audio") == "transcribed text"

    monkeypatch.setattr(ai_engine, "get_ai_client", lambda: None)
    assert ai_engine.transcribe_audio(b"fake-audio") is None
    assert ai_engine.transcribe_audio(b"") is None


# --- mandi_data: live AMIS rates ---------------------------------------------

AMIS_SAMPLE_HTML = """
<span id="ctl00_cphPage_lblMsg">Wheat</span>
<td id="ctl00_cphPage_Grd"><table>
<tr><td>&nbsp;Dated:21-11-2026</td><td>Graph</td><td>Min</td><td>Max</td><td>FQP</td><td>Quantity</td></tr>
<tr><td>&nbsp;<b>1 <a>Lahore</a></b></td><td>Graph</td><td>15500</td><td>16200</td><td>15850</td><td>-</td></tr>
<tr><td>&nbsp;<b>2 <a>Multan</a></b></td><td>Graph</td><td>-</td><td>-</td><td>-</td><td>-</td></tr>
</table></td>
"""


def test_resolve_commodity_id_english_and_urdu():
    from mandi_data import resolve_commodity_id

    assert resolve_commodity_id("wheat") == 1
    assert resolve_commodity_id("گندم") == 1
    assert resolve_commodity_id("kapaas") == 49
    assert resolve_commodity_id("آلو") == 21
    assert resolve_commodity_id("unknown crop xyz") is None


def test_parse_rates_html_extracts_rows_and_date():
    from mandi_data import parse_rates_html

    data = parse_rates_html(AMIS_SAMPLE_HTML)
    assert data["ok"] is True
    assert data["commodity"] == "Wheat"
    assert data["dated"] == "21-11-2026"
    assert data["rows"][0] == {"market": "Lahore", "min": 15500, "max": 16200, "fqp": 15850}
    assert data["rows"][1]["market"] == "Multan"
    assert data["rows"][1]["min"] is None  # "-" means no data that day


def test_parse_rates_html_without_table_reports_error():
    from mandi_data import parse_rates_html

    assert parse_rates_html("<html><body>no table</body></html>")["ok"] is False


def test_fetch_mandi_rates_uses_live_page(monkeypatch):
    """requests.get is stubbed — no network in tests."""
    import mandi_data

    class _Resp:
        text = AMIS_SAMPLE_HTML

        def raise_for_status(self):
            pass

    monkeypatch.setattr(
        mandi_data.requests, "get", lambda *a, **k: _Resp()
    )
    data = mandi_data.fetch_mandi_rates("wheat")
    assert data["ok"] is True
    assert data["commodity"] == "Wheat"
    assert len(data["rows"]) == 2


def test_fetch_mandi_rates_unknown_crop_and_network_failure(monkeypatch):
    import mandi_data

    assert mandi_data.fetch_mandi_rates("unknown crop xyz")["ok"] is False

    def _boom(*a, **k):
        raise ConnectionError("offline")

    monkeypatch.setattr(mandi_data.requests, "get", _boom)
    data = mandi_data.fetch_mandi_rates("wheat")
    assert data["ok"] is False
    assert "AMIS" in data["error"]


def test_format_rates_markdown_shows_urdu_table():
    from mandi_data import format_rates_markdown, parse_rates_html

    table = format_rates_markdown(parse_rates_html(AMIS_SAMPLE_HTML))
    assert "Wheat" in table
    assert "21-11-2026" in table
    assert "AMIS Punjab" in table
    assert "| Lahore | 15,500 | 16,200 | 15,850 |" in table


def test_play_audio_does_not_raise():
    """Audio playback must never crash the app, even with no network."""
    from utils import play_audio

    play_audio("test")  # must not raise


def test_ai_response_without_client_returns_no_api_message(monkeypatch):
    """With no API key configured, the engine returns the no-API message
    instead of crashing."""
    import ai_engine

    monkeypatch.setattr(ai_engine, "get_ai_client", lambda: None)
    monkeypatch.setattr(ai_engine, "t", lambda key: "NO_API")
    assert ai_engine.get_ai_response("test question") == "NO_API"


def test_secrets_file_is_gitignored():
    """Regression test: .streamlit/secrets.toml must be ignored by git,
    so a real key can never be committed by accident."""
    r = subprocess.run(
        ["git", "check-ignore", "-q", ".streamlit/secrets.toml"],
        cwd=REPO_ROOT,
        capture_output=True,
    )
    assert r.returncode == 0, "secrets.toml is not covered by .gitignore"


def test_no_real_secrets_file_is_tracked():
    """No real secrets file may be tracked in the repo."""
    r = subprocess.run(
        ["git", "ls-files", ".streamlit/secrets.toml"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    assert r.stdout.strip() == "", "secrets.toml is still tracked by git"
