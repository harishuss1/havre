"""
selectors.py — Kijiji Immobilier CSS selectors
Run debug_kijiji.py to verify these against the live site.
Last verified: 2026-05-05
"""

# ── URLs ───────────────────────────────────────────────────────────────────────

# Kijiji real estate for-sale listings — Greater Montreal
SEARCH_PAGE_URL = "https://www.kijiji.ca/b-a-vendre/grand-montreal/c30353001l80002"
SEARCH_PAGE_URL_PARAMS = "https://www.kijiji.ca/b-a-vendre/grand-montreal/c30353001l80002?price={min_price}__{max_price}"

# ── Listing cards ──────────────────────────────────────────────────────────────
# Note: data-testid values are "listing-card-list-item-0", "-1", etc. — use starts-with (^=)

LISTING_CARD       = "li[data-testid^='listing-card-list-item']"
CARD_PRICE         = "[data-testid='listing-price']"
CARD_TITLE         = "h3[data-testid='listing-title']"
CARD_ADDRESS       = "[data-testid='listing-location']"
CARD_DESCRIPTION   = "p[class*='description']"
CARD_LINK          = "a[data-testid='listing-link']"
CARD_IMAGE         = "img[data-testid='listing-card-image']"
CARD_BEDROOMS      = None   # not present on list cards — infer from title
CARD_BATHROOMS     = None   # not present on list cards

# ── Pagination ─────────────────────────────────────────────────────────────────

PAGINATION_NEXT    = "a[data-testid='pagination-next-link']"

# ── Detail page ────────────────────────────────────────────────────────────────

DETAIL_DESCRIPTION = "div[itemprop='description']"
DETAIL_IMAGES      = "div[class*='heroImageContainer'] img"

# ── Property type map ──────────────────────────────────────────────────────────

# Parsed from listing title keywords
PROPERTY_TYPE_MAP = {
    "condo":      "condo",
    "condominium":"condo",
    "house":      "house",
    "maison":     "house",
    "bungalow":   "house",
    "duplex":     "duplex",
    "triplex":    "duplex",
    "multiplex":  "duplex",
    "plex":       "duplex",
    "land":       "land",
    "terrain":    "land",
    "lot":        "land",
    "commercial": "other",
    "loft":       "condo",
    "studio":     "condo",
}