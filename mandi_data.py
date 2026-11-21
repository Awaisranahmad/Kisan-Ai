"""Live mandi rates from Punjab AMIS (amis.pk) — the official source.

The app used to ask the AI for "current" mandi rates, but a language
model has no live prices, so those rates were invented. This module
fetches the real daily auction/wholesale prices published by the
Agriculture Marketing Information Service, Punjab.

If the fetch fails (no internet, site down, unknown crop), the caller
gets ``{"ok": False, ...}`` and must say so honestly instead of showing
an AI guess as a real rate.
"""
import re

import requests
from bs4 import BeautifulSoup

AMIS_URL = "http://www.amis.pk/ViewPrices.aspx"
AMIS_SOURCE = "AMIS Punjab (amis.pk)"
TIMEOUT_SECONDS = 15

# Crop name (English or Urdu) -> AMIS commodity id.
# Verified against amis.pk on 2026-11-21.
COMMODITY_IDS = {
    "wheat": 1, "gandum": 1, "گندم": 1,
    "rice": 3, "basmati": 3, "چاول": 3,
    "rice irri": 4, "irri": 4,
    "sugar": 7, "chini": 7, "چینی": 7,
    "gram": 8, "chana": 8, "چنا": 8,
    "maize": 17, "makki": 17, "مکئی": 17,
    "millet": 18, "bajra": 18, "باجرہ": 18,
    "potato": 21, "aalu": 21, "aloo": 21, "آلو": 21,
    "onion": 23, "piyaz": 23, "پیاز": 23,
    "garlic": 24, "lehsan": 24, "لہسن": 24,
    "tomato": 26, "tamatar": 26, "ٹماٹر": 26,
    "peas": 35, "matar": 35, "مٹر": 35,
    "cotton": 49, "phutti": 49, "kapas": 49, "kapaas": 49, "کپاس": 49, "پھٹی": 49,
    "chilli": 29, "mirch": 29, "مرچ": 29,
    "cauliflower": 33, "phool gobhi": 33, "پھول گوبھی": 33,
    "banana": 42, "kela": 42, "کیلا": 42,
    "kinnow": 45, "کنو": 45,
    "mango": 48, "aam": 48, "آم": 48,
}

# Shown first when present — the big Punjab mandis.
PREFERRED_MARKETS = [
    "Lahore", "Faisalabad", "Multan", "Rawalpindi", "Gujranwala",
    "Sialkot", "Sahiwal", "Okara", "BahawalPur", "Sargodha",
    "Jhang", "Gujrat", "Kasur", "Sheikhupura", "Vehari",
]


def resolve_commodity_id(crop_name):
    """Map a crop name (English/Urdu) to an AMIS commodity id, or None."""
    if not crop_name:
        return None
    name = crop_name.strip().lower()
    if name in COMMODITY_IDS:
        return COMMODITY_IDS[name]
    for key, cid in COMMODITY_IDS.items():
        if key in name or name in key:
            return cid
    return None


def _to_int(text):
    text = (text or "").strip().replace(",", "")
    if text in ("", "-"):
        return None
    try:
        return int(float(text))
    except ValueError:
        return None


def parse_rates_html(html):
    """Parse an AMIS ViewPrices page into structured rates.

    Returns ``{"ok": True, "commodity": ..., "dated": ..., "rows": [...]}``
    or ``{"ok": False, "error": ...}`` when the table is missing.
    """
    soup = BeautifulSoup(html, "html.parser")
    # The id sits on the <td> wrapping the price table (not on a <table>).
    grid = soup.find(id="ctl00_cphPage_Grd")
    if grid is None:
        return {"ok": False, "error": "AMIS rates table not found on the page."}
    name_tag = soup.find("span", id="ctl00_cphPage_lblMsg")
    commodity = name_tag.get_text(strip=True) if name_tag else ""

    dated = ""
    rows = []
    for tr in grid.find_all("tr"):
        cells = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
        if len(cells) < 5:
            continue
        if cells[0].startswith("Dated:"):
            dated = cells[0].replace("Dated:", "").strip()
            continue
        market = re.sub(r"^\d+\s*", "", cells[0]).strip()
        if not market or market.lower() in ("graph",):
            continue
        rows.append({
            "market": market,
            "min": _to_int(cells[2]),
            "max": _to_int(cells[3]),
            "fqp": _to_int(cells[4]),
        })
    if not rows:
        return {"ok": False, "error": "No market rows found in the AMIS table."}
    return {
        "ok": True,
        "commodity": commodity,
        "dated": dated,
        "unit": "Rs/100Kg",
        "source": AMIS_SOURCE,
        "rows": rows,
    }


def fetch_mandi_rates(crop_name, timeout=TIMEOUT_SECONDS):
    """Fetch today's live rates for ``crop_name`` from AMIS Punjab."""
    cid = resolve_commodity_id(crop_name)
    if cid is None:
        return {
            "ok": False,
            "error": f"'{crop_name}' ka live rate AMIS par nahi mila.",
        }
    try:
        resp = requests.get(
            AMIS_URL,
            params={"searchType": 0, "commodityId": cid},
            timeout=timeout,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        resp.raise_for_status()
    except Exception as exc:  # noqa: BLE001 - surfaced as a plain message
        return {"ok": False, "error": f"AMIS se rate nahi mil saka: {exc}"}
    data = parse_rates_html(resp.text)
    if data.get("ok"):
        data["crop"] = crop_name.strip()
    return data


def pick_rows(rows, limit=12):
    """Preferred big mandis first, markets with real prices before
    ones with no trading today, capped at ``limit``."""
    with_data = [r for r in rows if r["fqp"] is not None or r["min"] is not None]
    preferred = [r for r in with_data if r["market"] in PREFERRED_MARKETS]
    rest = [r for r in with_data if r["market"] not in PREFERRED_MARKETS]
    picked = preferred + rest
    if len(picked) < limit:
        picked += [r for r in rows if r not in picked][: limit - len(picked)]
    return picked[:limit]


def format_rates_markdown(data, limit=12):
    """Render fetched rates as a Markdown table (Urdu headers)."""
    rows = pick_rows(data["rows"], limit=limit)
    lines = [
        f"**{data.get('commodity') or data.get('crop', '')} — {data.get('dated', '')}**",
        f"ماخذ: {data['source']} (فی 100 کلو)",
        "",
        "| شہر | کم سے کم | زیادہ سے زیادہ | اوسط |",
        "|---|---|---|---|",
    ]
    for r in rows:
        fmt = lambda v: f"{v:,}" if v is not None else "-"
        lines.append(f"| {r['market']} | {fmt(r['min'])} | {fmt(r['max'])} | {fmt(r['fqp'])} |")
    if len(data["rows"]) > limit:
        lines.append("")
        lines.append(f"({len(data['rows']) - limit} مزید منڈیاں {data['source']} پر دیکھیں۔)")
    return "\n".join(lines)
