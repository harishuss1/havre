"""
parser.py — Centris field extraction helpers

Takes raw strings scraped from the page and converts them into
clean typed values. All the messy string parsing lives here,
keeping the scraper and normaliser clean.
"""

import re


def parse_price(raw: str | None) -> int:
    """
    "$1 250 000" → 1250000
    "1,250,000 $" → 1250000
    Returns 0 if unparseable.
    """
    if not raw:
        return 0
    digits = re.sub(r"[^\d]", "", raw)
    return int(digits) if digits else 0


def parse_bedrooms(raw: str | None) -> int | None:
    """
    "3 + 1"  → 3   (we take the main floor count)
    "3"      → 3
    "Studio" → 0
    """
    if not raw:
        return None
    raw = raw.strip().lower()
    if "studio" in raw:
        return 0
    match = re.search(r"(\d+)", raw)
    return int(match.group(1)) if match else None


def parse_bathrooms(raw: str | None) -> int | None:
    """
    "2" → 2
    "1 + 1" → 1
    """
    if not raw:
        return None
    match = re.search(r"(\d+)", raw.strip())
    return int(match.group(1)) if match else None


def parse_area(raw: str | None) -> int | None:
    """
    "1 200 pi²" → 1200  (pieds carrés = sqft, direct)
    "120 m²"    → 1292  (convert m² → sqft)
    """
    if not raw:
        return None

    digits = re.sub(r"[^\d.]", "", raw.replace(" ", ""))
    if not digits:
        return None

    try:
        value = float(digits)
    except ValueError:
        return None

    # Centris uses "pi²" for sqft, "m²" for sqm
    if "m²" in raw or "m2" in raw.lower():
        value = value * 10.7639  # sqm → sqft

    return int(value)


def parse_city(raw: str | None) -> str:
    """
    "Montréal (Rosemont–La Petite-Patrie)" → "Montréal"
    "Laval" → "Laval"
    Strips borough names in parentheses.
    """
    if not raw:
        return ""
    return re.sub(r"\s*\(.*?\)", "", raw).strip()


def parse_postal_code(raw: str | None) -> str:
    """
    Extracts Canadian postal code from an address string.
    "123 Rue Masson, Montréal, QC H2G 1M1" → "H2G 1M1"
    """
    if not raw:
        return ""
    match = re.search(r"[A-Za-z]\d[A-Za-z]\s?\d[A-Za-z]\d", raw)
    return match.group(0).upper() if match else ""


def parse_region(address: str | None) -> str:
    """
    Best-effort region extraction from a full address.
    "123 Rue Masson, Montréal, QC H2G 1M1" → "QC"
    """
    if not address:
        return ""
    # Look for Canadian province abbreviation
    match = re.search(
        r"\b(QC|ON|BC|AB|MB|SK|NS|NB|NL|PE|NT|YT|NU)\b",
        address.upper()
    )
    return match.group(1) if match else ""


def parse_property_type(raw: str | None) -> str:
    """
    Maps property type string to our enum.
    Now receives already-parsed values from _type_from_url()
    so just pass through valid values or default to 'other'.
    """
    valid = {"house", "condo", "duplex", "land", "other"}
    if not raw:
        return "other"
    return raw if raw in valid else "other"


def parse_external_id(card_id_attr: str | None) -> str:
    """
    Extracts the numeric MLS ID from the card's HTML id attribute.
    "listing-12345678" → "12345678"
    """
    if not card_id_attr:
        return ""
    match = re.search(r"\d+", card_id_attr)
    return match.group(0) if match else ""


def parse_listing_url(href: str | None, base: str = "https://www.centris.ca") -> str:
    """
    Ensures the listing URL is absolute.
    "/en/houses~for-sale~montreal/12345678" → "https://www.centris.ca/en/..."
    """
    if not href:
        return ""
    if href.startswith("http"):
        return href
    return base + href