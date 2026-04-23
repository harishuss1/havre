"""
selectors.py — Kijiji Immobilier CSS selectors
Run debug_kijiji.py to verify these against the live site.
Last verified: needs verification
"""

# ── URLs ───────────────────────────────────────────────────────────────────────

# Kijiji real estate search — Montreal island, for sale
SEARCH_PAGE_URL = "https://www.kijiji.ca/b-real-estate/montreal/c34l80002"
SEARCH_PAGE_URL_PARAMS = "https://www.kijiji.ca/b-real-estate/montreal/c34l80002?price={min_price}__{max_price}&furnished=0"

# ── Listing cards ──────────────────────────────────────────────────────────────

LISTING_CARD       = "li[data-testid='listing-card-list-item']"
CARD_PRICE         = "p[data-testid='listing-price']"
CARD_TITLE         = "h3[class*='title']"
CARD_ADDRESS       = "span[data-testid='listing-location']"
CARD_DESCRIPTION   = "p[class*='description']"
CARD_LINK          = "a[data-testid='listing-link']"
CARD_IMAGE         = "img[class*='image']"
CARD_BEDROOMS      = "span[data-testid='bedrooms']"
CARD_BATHROOMS     = "span[data-testid='bathrooms']"

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