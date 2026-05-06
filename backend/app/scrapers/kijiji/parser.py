"""
parser.py — Kijiji field extraction helpers
"""

import re
from .selectors import PROPERTY_TYPE_MAP


def parse_price(raw: str | None) -> int:
    if not raw:
        return 0
    # Kijiji sometimes shows "Please Contact" or "Swap/Trade"
    if not any(c.isdigit() for c in (raw or "")):
        return 0
    # Strip decimal cents before removing non-digits (e.g. "$369,900.00" → "$369,900")
    raw = re.sub(r"\.\d+", "", raw)
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else 0


def parse_bedrooms(raw: str | None) -> int | None:
    if not raw:
        return None
    raw = raw.strip().lower()
    if "studio" in raw or "bachelor" in raw:
        return 0
    match = re.search(r"(\d+)", raw)
    return int(match.group(1)) if match else None


def parse_bathrooms(raw: str | None) -> int | None:
    if not raw:
        return None
    match = re.search(r"(\d+)", raw.strip())
    return int(match.group(1)) if match else None


def parse_area(raw: str | None) -> int | None:
    if not raw:
        return None
    digits = re.sub(r"[^\d.]", "", raw.replace(" ", ""))
    if not digits:
        return None
    try:
        value = float(digits)
    except ValueError:
        return None
    if "m²" in raw or "m2" in raw.lower():
        value = value * 10.7639
    return int(value)


def parse_city(raw: str | None) -> str:
    """
    Kijiji location format: "Montréal / Island" or "Laval"
    We take everything before the slash.
    """
    if not raw:
        return ""
    city = raw.split("/")[0].strip()
    return re.sub(r"\s*\(.*?\)", "", city).strip()


def parse_postal_code(raw: str | None) -> str:
    if not raw:
        return ""
    match = re.search(r"[A-Za-z]\d[A-Za-z]\s?\d[A-Za-z]\d", raw)
    return match.group(0).upper() if match else ""


def parse_region(address: str | None) -> str:
    if not address:
        return "QC"
    match = re.search(
        r"\b(QC|ON|BC|AB|MB|SK|NS|NB|NL|PE|NT|YT|NU)\b",
        address.upper()
    )
    return match.group(1) if match else "QC"


def parse_property_type(title: str | None) -> str:
    """
    Kijiji doesn't have a type field on cards — infer from listing title.
    e.g. "3 bedroom condo for sale" → "condo"
    """
    if not title:
        return "other"
    lower = title.lower()
    for keyword, prop_type in PROPERTY_TYPE_MAP.items():
        if keyword in lower:
            return prop_type
    return "other"


def parse_external_id(url: str | None) -> str:
    """
    Extracts Kijiji ad ID from the URL.
    "/v-condos-for-sale/montreal/beautiful-condo/1234567890" → "1234567890"
    """
    if not url:
        return ""
    match = re.search(r"/(\d+)$", url.rstrip("/"))
    return match.group(1) if match else ""


def parse_listing_url(href: str | None, base: str = "https://www.kijiji.ca") -> str:
    if not href:
        return ""
    if href.startswith("http"):
        return href
    return base + href