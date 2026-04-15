"""
selectors.py — Centris.ca CSS selectors (verified against live site)
Last verified: 2025
"""

# ── Search page URLs ───────────────────────────────────────────────────────────

SEARCH_API_URL     = "https://www.centris.ca/property/UpdateQuery"
SEARCH_RESULTS_URL = "https://www.centris.ca/property/GetInscriptions"
SEARCH_PAGE_URL    = "https://www.centris.ca/en/properties~for-sale~{city}"

# ── Listing cards ──────────────────────────────────────────────────────────────

LISTING_CARD   = "div.shell"

# MLS number lives in a <meta itemprop="sku"> inside each card
CARD_MLS_ID    = "meta[itemprop='sku']"   # read content="" attribute

# Price
CARD_PRICE     = "div.price span"

# Address block — contains both street + city on separate lines
CARD_ADDRESS   = "div.address"            # full text, split on \n to get parts

# Bedrooms / bathrooms
CARD_BEDROOMS  = "div.cac"
CARD_BATHROOMS = "div.sdb"

# Area — not present on listing cards; fetched from detail page only
CARD_AREA      = None

# Link to detail page — property type encoded in href slug
# e.g. /en/condos~for-sale~montreal-ville-marie/20324685
CARD_LINK      = "a.a-more-detail"

# Thumbnail image
CARD_IMAGE     = "a.property-thumbnail-summary-link img"

# ── Pagination ─────────────────────────────────────────────────────────────────

PAGINATION_NEXT    = "li.next a"
PAGINATION_CURRENT = "li.pager-current"

# ── Detail page ────────────────────────────────────────────────────────────────

DETAIL_DESCRIPTION = "div#description div.row"
DETAIL_IMAGES      = "div.primary-photo img, div.thumbnail-photos img"

# ── API filter keys ────────────────────────────────────────────────────────────

API_FILTER_MIN_PRICE = "PriceMin"
API_FILTER_MAX_PRICE = "PriceMax"
API_FILTER_BEDROOMS  = "BedroomMin"
API_FILTER_CATEGORY  = "Category"

CATEGORY_CODES = {
    "house":  1,
    "condo":  2,
    "duplex": 3,
    "land":   5,
    "other":  0,
}

# ── Property type parsed from URL slug ─────────────────────────────────────────

# e.g. /en/condos~for-sale~montreal → "condo"
URL_TYPE_MAP = {
    "condos":        "condo",
    "condominium":   "condo",
    "houses":        "house",
    "house":         "house",
    "residential":   "house",
    "residentials":  "house",
    "duplex":        "duplex",
    "duplexs":       "duplex",
    "multiplex":     "duplex",
    "plexs":         "duplex",
    "lands":         "land",
    "terrain":       "land",
    "commercial":    "other",
}