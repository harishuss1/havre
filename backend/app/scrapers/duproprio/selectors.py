"""
selectors.py — DuProprio.com CSS selectors (verified against live site)
Last verified: 2025
"""

# ── URLs ───────────────────────────────────────────────────────────────────────

SEARCH_PAGE_URL = "https://duproprio.com/en/search/list?search=true&for_sale=1&is_for_sale=1&parent=1"
SEARCH_PAGE_URL_CITY = "https://duproprio.com/en/search/list?search=true&for_sale=1&is_for_sale=1&parent=1&city_name={city}"

# ── Listing cards ──────────────────────────────────────────────────────────────

LISTING_CARD  = "li.search-results-listings-list__item"

# Price — verified
CARD_PRICE    = "div[class*='price']"

# Address — verified
CARD_ADDRESS  = "div[class*='address']"

# Link — verified
# href: /en/{region}/{city}/{type}-for-sale/{slug}-{listing_id}
# e.g.  /en/quebec-rive-sud/st-nicolas/bungalow-for-sale/hab-2293-chemin-filteau-1128802
CARD_LINK     = "a[class*='link']"

# Thumbnail
CARD_IMAGE    = "img[class*='photo']"

# Bedrooms/bathrooms — not in first 1500 chars of card HTML
# Attempted but may return None; parsed from detail page if needed
CARD_BEDROOMS  = "div[class*='specs'] div[class*='bedroom']"
CARD_BATHROOMS = "div[class*='specs'] div[class*='bathroom']"
CARD_AREA      = "div[class*='specs'] div[class*='area']"

# ── Pagination ─────────────────────────────────────────────────────────────────

PAGINATION_NEXT = "a[rel='next']"

# ── Detail page ────────────────────────────────────────────────────────────────

DETAIL_DESCRIPTION = "div[class*='description']"
DETAIL_IMAGES      = "div[class*='gallery'] img, div[class*='photo'] img"

# ── URL parsing maps ───────────────────────────────────────────────────────────

# City and property type parsed from URL slug:
# /en/quebec-rive-sud/st-nicolas/bungalow-for-sale/...
#                     ^^^^^^^^^^ city slug (index 2)
#                                ^^^^^^^^ type slug (index 3, before -for-sale)

URL_TYPE_MAP = {
    "bungalow":      "house",
    "house":         "house",
    "maison":        "house",
    "cottage":       "house",
    "chalet":        "house",
    "semi-detached": "house",
    "home":          "house",
    "townhouse":     "house",
    "split-level":   "house",
    "condo":         "condo",
    "condominium":   "condo",
    "appartement":   "condo",
    "apartment":     "condo",
    "duplex":        "duplex",
    "triplex":       "duplex",
    "quadruplex":    "duplex",
    "multiplex":     "duplex",
    "plex":          "duplex",
    "land":          "land",
    "terrain":       "land",
    "lot":           "land",
    "commercial":    "other",
    "industriel":    "other",
}

PROPERTY_TYPE_MAP = URL_TYPE_MAP