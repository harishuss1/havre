"""
parser.py — DuProprio field extraction helpers
"""

import re
from .selectors import PROPERTY_TYPE_MAP


def parse_price(raw: str | None) -> int:
    if not raw:
        return 0
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else 0


def parse_bedrooms(raw: str | None) -> int | None:
    if not raw:
        return None
    raw = raw.strip().lower()
    if "studio" in raw:
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
    if not raw:
        return ""
    return re.sub(r"\s*\(.*?\)", "", raw).strip()


def parse_postal_code(raw: str | None) -> str:
    if not raw:
        return ""
    match = re.search(r"[A-Za-z]\d[A-Za-z]\s?\d[A-Za-z]\d", raw)
    return match.group(0).upper() if match else ""


def parse_region(address: str | None) -> str:
    if not address:
        return ""
    match = re.search(
        r"\b(QC|ON|BC|AB|MB|SK|NS|NB|NL|PE|NT|YT|NU)\b",
        address.upper()
    )
    return match.group(1) if match else "QC"  # DuProprio is Quebec-focused


def parse_property_type(raw: str | None) -> str:
    if not raw:
        return "other"
    key = raw.strip().lower()
    for pattern, normalised in PROPERTY_TYPE_MAP.items():
        if pattern in key:
            return normalised
    return "other"


def parse_external_id(raw: str | None) -> str:
    if not raw:
        return ""
    match = re.search(r"\d+", raw)
    return match.group(0) if match else ""


def parse_listing_url(href: str | None, base: str = "https://duproprio.com") -> str:
    if not href:
        return ""
    if href.startswith("http"):
        return href
    return base + href