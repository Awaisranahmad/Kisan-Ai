"""Offline crop reference data (Urdu).

Powers the Crop Doctor's Fasal Guide — instant crop info with no API
key needed. Values are general guidance for Punjab, Pakistan; always
cross-check critical decisions with local agricultural extension
services or a qualified agronomist.
"""

CROP_DB = {
    "گندم": {
        "pest": "چوہا، سنڈی",
        "water": "4-5 پانی",
        "urea": "2 بوری فی ایکڑ",
        "season": "ربیع (نومبر-دسمبر)"
    },
    "کپاس": {
        "pest": "سفید مکھی، گلابی سنڈی",
        "water": "10-12 پانی",
        "urea": "3 بوری فی ایکڑ",
        "season": "خریف (اپریل-مئی)"
    },
    "چاول": {
        "pest": "تنے کا بورر، پتا لپیٹک",
        "water": "15-20 پانی",
        "urea": "2.5 بوری فی ایکڑ",
        "season": "خریف (جون-جولائی)"
    },
    "مکئی": {
        "pest": "تنے کا بورر، فوجی سنڈی",
        "water": "6-8 پانی",
        "urea": "2.5 بوری فی ایکڑ",
        "season": "خریف (جون-جولائی)"
    },
    "آلو": {
        "pest": "پتوں کا جھلساؤ، سفید مکھی",
        "water": "8-10 پانی",
        "urea": "2 بوری فی ایکڑ",
        "season": "ربیع (اکتوبر-نومبر)"
    },
    "گنا": {
        "pest": "تنے کا بورر، سفید مکھی",
        "water": "12-15 پانی",
        "urea": "3 بوری فی ایکڑ",
        "season": "بہار (فروری-مارچ)"
    }
}

# Every entry must carry exactly these fields — tests check this.
CROP_FIELDS = ("pest", "water", "urea", "season")


def list_crops():
    """Crop names in the encyclopedia, in display order."""
    return list(CROP_DB)


def get_crop_info(crop_name):
    """Info dict for one crop, or {} when the crop is unknown.

    Returns a copy, so callers cannot mutate the shared data.
    """
    return dict(CROP_DB.get(crop_name, {}))
