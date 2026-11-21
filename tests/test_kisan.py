"""Tests for Kisan-Ai helpers.

Run from the repo root:  python -m pytest tests/ -v
Requires the app dependencies plus pytest (see README, Tests section).

These tests deliberately avoid a live Groq key and a running Streamlit app:
pure helpers are tested directly, and the AI guard is tested with the
client monkeypatched to None.
"""

import base64
import io
import os
import subprocess
import sys

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


def test_create_pdf_returns_none_without_font():
    """PDF export needs DejaVuSans.ttf, which is not shipped in the repo,
    so it must fail gracefully (None) instead of crashing the app."""
    from utils import create_pdf

    assert create_pdf("test") is None


def test_play_audio_does_not_raise():
    """Audio playback must never crash the app, even with no network."""
    from utils import play_audio

    play_audio("test")  # must not raise


def test_ai_response_without_client_returns_no_api_message(monkeypatch):
    """With no Groq key configured, the engine returns the no-API message
    instead of crashing."""
    import ai_engine

    monkeypatch.setattr(ai_engine, "get_groq_client", lambda: None)
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
