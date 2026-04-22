"""
scraper.py — Centris.ca Playwright scraper

Centris is the MLS platform used by Quebec real estate brokers.
It renders listings entirely in JavaScript, so we use a full
headless Chromium browser via Playwright.

Strategy:
  1. Navigate to the search page to get session cookies
  2. POST search criteria to Centris's internal JSON API
  3. Paginate through results, scraping each listing card
  4. Optionally fetch individual detail pages for extra fields
"""

import asyncio
import json
import random
import re
from datetime import datetime, timezone

from playwright.async_api import async_playwright, Page, BrowserContext

from ..base import BaseScraper, SearchCriteria, RawListing
from .selectors import (
    SEARCH_PAGE_URL,
    SEARCH_API_URL,
    LISTING_CARD,
    CARD_PRICE,
    CARD_ADDRESS,
    CARD_BEDROOMS,
    CARD_BATHROOMS,
    CARD_LINK,
    CARD_IMAGE,
    CARD_MLS_ID,
    PAGINATION_NEXT,
    CATEGORY_CODES,
    API_FILTER_MIN_PRICE,
    API_FILTER_MAX_PRICE,
    API_FILTER_BEDROOMS,
    API_FILTER_CATEGORY,
    DETAIL_DESCRIPTION,
    DETAIL_IMAGES,
)
from .parser import (
    parse_price,
    parse_bedrooms,
    parse_bathrooms,
    parse_area,
    parse_city,
    parse_postal_code,
    parse_region,
    parse_property_type,
    parse_external_id,
    parse_listing_url,
)

# Realistic browser user agents to rotate through
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# Seconds to wait between page navigations (randomised to appear human)
MIN_DELAY = 2.0
MAX_DELAY = 5.0


class CentrisScraper(BaseScraper):
    source_name = "centris"

    def __init__(self, headless: bool = True, max_pages: int = 10):
        """
        Args:
            headless: Run browser invisibly (True for production, False for debugging)
            max_pages: Safety cap on pagination — stops after this many pages
        """
        self.headless = headless
        self.max_pages = max_pages

    # ── Public interface ───────────────────────────────────────────────────────

    async def fetch_listings(self, criteria: SearchCriteria) -> list[dict]:
        """
        Main entry point. Launches Playwright, scrapes Centris, returns raw dicts.
        """
        print(f"[centris] Starting scrape — criteria: {criteria}")
        raw_listings: list[dict] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await self._create_context(browser)
            page = await context.new_page()

            try:
                # Step 1: Navigate to the search page to initialise the session
                city_slug = self._build_city_slug(criteria.cities)
                search_url = SEARCH_PAGE_URL.format(city=city_slug)
                print(f"[centris] Loading search page: {search_url}")
                await page.goto(search_url, wait_until="networkidle", timeout=30_000)
                await self._random_delay()

                # Step 2: Apply search filters via the Centris internal API
                await self._apply_filters(page, criteria)
                await self._random_delay()

                # Step 3: Paginate and collect listing cards
                page_num = 1
                while page_num <= self.max_pages:
                    print(f"[centris] Scraping page {page_num}...")
                    cards = await self._scrape_listing_cards(page)
                    raw_listings.extend(cards)

                    if len(raw_listings) >= criteria.max_results:
                        print(f"[centris] Reached max_results ({criteria.max_results}), stopping")
                        break

                    has_next = await self._go_to_next_page(page)
                    if not has_next:
                        print(f"[centris] No more pages after page {page_num}")
                        break

                    page_num += 1
                    await self._random_delay()

            except Exception as e:
                print(f"[centris] Scrape error: {e}")
                raise
            finally:
                await browser.close()

        print(f"[centris] Done — collected {len(raw_listings)} raw listings")
        filtered = self._apply_client_filters(raw_listings, criteria)
        print(f"[centris] After client-side filtering: {len(filtered)} listings")
        return filtered[:criteria.max_results]
    
    def _apply_client_filters(self, listings: list[dict], criteria: SearchCriteria) -> list[dict]:
        """
        Filters scraped listings by price and bedrooms client-side.
        Used as fallback when the Centris filter API returns 404.
        """
        result = []
        for l in listings:
            price = parse_price(l.get("price"))
            beds = parse_bedrooms(l.get("bedrooms"))

            if criteria.min_price and price < criteria.min_price:
                continue
            if criteria.max_price and price > criteria.max_price:
                continue
            if criteria.min_bedrooms and beds is not None and beds < criteria.min_bedrooms:
                continue

            result.append(l)
        return result

    def normalise(self, raw: list[dict]) -> list[RawListing]:
        """
        Maps raw Centris dicts → shared RawListing schema.
        """
        listings: list[RawListing] = []

        for item in raw:
            try:
                address_full = item.get("address", "")
                city_raw = item.get("city", "")

                listing = RawListing(
                    source=self.source_name,
                    external_id=parse_external_id(item.get("card_id")),
                    title=item.get("title", "").strip(),
                    address=address_full.strip(),
                    city=parse_city(city_raw),
                    region=parse_region(address_full),
                    postal_code=parse_postal_code(address_full),
                    price=parse_price(item.get("price")),
                    bedrooms=parse_bedrooms(item.get("bedrooms")),
                    bathrooms=parse_bathrooms(item.get("bathrooms")),
                    size_sqft=parse_area(item.get("area")),
                    property_type=parse_property_type(item.get("property_type")),
                    listing_url=parse_listing_url(item.get("url")),
                    images=item.get("images", []),
                    description=item.get("description", ""),
                    listed_at=None,  # Centris doesn't expose this on the card
                    raw=item,
                )
                listings.append(listing)
            except Exception as e:
                print(f"[centris] Failed to normalise listing {item.get('card_id')}: {e}")
                continue

        print(f"[centris] Normalised {len(listings)} listings")
        return listings

    # ── Private helpers ────────────────────────────────────────────────────────

    async def _create_context(self, browser) -> BrowserContext:
        """Creates a browser context with realistic headers."""
        return await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1440, "height": 900},
            locale="fr-CA",
            timezone_id="America/Toronto",
            extra_http_headers={
                "Accept-Language": "fr-CA,fr;q=0.9,en-CA;q=0.8,en;q=0.7",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            }
        )

    async def _apply_filters(self, page: Page, criteria: SearchCriteria) -> None:
        """
        Applies search criteria by POSTing to Centris's internal filter API.
        Centris uses session-based filtering — we POST the criteria, then the
        search results page reflects those filters.
        """
        # Build the filter payload
        filters: dict = {}

        if criteria.min_price is not None:
            filters[API_FILTER_MIN_PRICE] = criteria.min_price
        if criteria.max_price is not None:
            filters[API_FILTER_MAX_PRICE] = criteria.max_price
        if criteria.min_bedrooms is not None:
            filters[API_FILTER_BEDROOMS] = criteria.min_bedrooms

        # Map property types to Centris category codes
        if criteria.property_types:
            codes = [
                CATEGORY_CODES.get(pt, 0)
                for pt in criteria.property_types
                if pt in CATEGORY_CODES and CATEGORY_CODES[pt] != 0
            ]
            if codes:
                filters[API_FILTER_CATEGORY] = codes[0]  # Centris takes one at a time

        if not filters:
            print("[centris] No filters to apply, using default search")
            return

        print(f"[centris] Applying filters: {filters}")

        # Execute filter POST via the page's fetch context (shares session cookies)
        result = await page.evaluate(
            """async ({ url, payload }) => {
                const res = await fetch(url, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json; charset=utf-8', 'X-Requested-With': 'XMLHttpRequest' },
                    body: JSON.stringify(payload)
                });
                return res.status;
            }""",
            {"url": SEARCH_API_URL, "payload": filters},
        )
        print(f"[centris] Filter API response status: {result}")

        # Reload the page to apply the new filters
        await page.reload(wait_until="networkidle", timeout=30_000)
        await self._wait_for_listings(page)

    async def _wait_for_listings(self, page: Page) -> None:
        """Waits until listing cards are visible on the page."""
        try:
            await page.wait_for_selector(LISTING_CARD, timeout=15_000)
        except Exception:
            print("[centris] Warning: listing cards did not appear within timeout")

    async def _scrape_listing_cards(self, page: Page) -> list[dict]:
        """
        Extracts data from all listing cards visible on the current page.
        Returns a list of raw dicts with site-specific field names.
        """
        await self._wait_for_listings(page)

        # Scroll to load any lazy-loaded cards
        await self._scroll_page(page)

        cards = await page.query_selector_all(LISTING_CARD)
        print(f"[centris] Found {len(cards)} cards on this page")

        results = []
        for card in cards:
            try:
                raw = await self._extract_card_data(card)
                if raw:
                    results.append(raw)
            except Exception as e:
                print(f"[centris] Card extraction error: {e}")
                continue

        return results

    async def _extract_card_data(self, card) -> dict | None:
        """Extracts all fields from a single listing card element."""

        # MLS ID from <meta itemprop="sku" content="...">
        meta_el = await card.query_selector(CARD_MLS_ID)
        card_id = await meta_el.get_attribute("content") if meta_el else None

        # Price
        price_el = await card.query_selector(CARD_PRICE)
        price = await price_el.inner_text() if price_el else ""

        # Address block contains street + city on separate lines e.g.:
        # "2000, boulevard René-Lévesque Ouest, apt. 2006\nMontréal (Ville-Marie)"
        address_el = await card.query_selector(CARD_ADDRESS)
        address_full = await address_el.inner_text() if address_el else ""
        address_lines = [l.strip() for l in address_full.strip().splitlines() if l.strip()]
        street  = address_lines[0] if len(address_lines) > 0 else ""
        city    = address_lines[1] if len(address_lines) > 1 else ""

        # Bedrooms
        bed_el = await card.query_selector(CARD_BEDROOMS)
        bedrooms = await bed_el.inner_text() if bed_el else None

        # Bathrooms
        bath_el = await card.query_selector(CARD_BATHROOMS)
        bathrooms = await bath_el.inner_text() if bath_el else None

        # Link — href looks like /en/condos~for-sale~montreal-ville-marie/20324685
        link_el = await card.query_selector(CARD_LINK)
        url = await link_el.get_attribute("href") if link_el else None

        if not url:
            return None  # Skip cards without a link

        # Property type parsed from URL slug (no badge on cards)
        property_type = self._type_from_url(url)

        # Title = street address (no separate title field on cards)
        title = street or address_full

        # Thumbnail image
        img_el = await card.query_selector(CARD_IMAGE)
        image_src = await img_el.get_attribute("src") if img_el else None
        images = [image_src] if image_src else []

        return {
            "card_id": card_id,
            "price": price.strip(),
            "address": street.strip(),
            "city": city.strip(),
            "bedrooms": bedrooms.strip() if bedrooms else None,
            "bathrooms": bathrooms.strip() if bathrooms else None,
            "area": None,   # not available on cards; detail page only
            "url": url,
            "title": title,
            "images": images,
            "property_type": property_type,
            "description": "",
            "scraped_at": datetime.now(timezone.utc).isoformat(),
        }

    @staticmethod
    def _type_from_url(url: str) -> str:
        """
        Parses property type from the Centris URL slug.
        /en/condos~for-sale~montreal → 'condo'
        /en/houses~for-sale~montreal → 'house'
        """
        from .selectors import URL_TYPE_MAP
        if not url:
            return "other"
        # First path segment after /en/ contains the type
        # e.g. ['', 'en', 'condos~for-sale~montreal-ville-marie', '20324685']
        parts = url.strip("/").split("/")
        if len(parts) >= 2:
            slug = parts[1].split("~")[0].lower()
            return URL_TYPE_MAP.get(slug, "other")
        return "other"

    async def _scroll_page(self, page: Page) -> None:
        """
        Scrolls the page gradually to trigger lazy-loaded listing images
        and ensure all cards in the viewport are fully rendered.
        """
        scroll_height = await page.evaluate("document.body.scrollHeight")
        current = 0
        step = 600

        while current < scroll_height:
            current = min(current + step, scroll_height)
            await page.evaluate(f"window.scrollTo(0, {current})")
            await asyncio.sleep(0.2)

        # Scroll back to top so pagination controls are visible
        await page.evaluate("window.scrollTo(0, 0)")
        await asyncio.sleep(0.5)

    async def _go_to_next_page(self, page: Page) -> bool:
        next_btn = await page.query_selector(PAGINATION_NEXT)
        if not next_btn:
            return False

        is_disabled = await next_btn.get_attribute("aria-disabled")
        if is_disabled == "true":
            return False

        try:
            await next_btn.click()
            await page.wait_for_load_state("networkidle", timeout=45_000)
            return True
        except Exception as e:
            print(f"[centris] Pagination timeout, stopping: {e}")
            return False

    async def _fetch_detail_page(self, page: Page, url: str) -> dict:
        """
        Optional: visits the individual listing detail page to get
        the full description and all photos.

        This is expensive (one request per listing) so it's disabled
        by default. Enable for listings you want to bookmark/save.
        """
        await page.goto(url, wait_until="networkidle", timeout=30_000)
        await self._random_delay()

        # Full description
        desc_el = await page.query_selector(DETAIL_DESCRIPTION)
        description = await desc_el.inner_text() if desc_el else ""

        # All gallery images
        img_els = await page.query_selector_all(DETAIL_IMAGES)
        images = []
        for img in img_els:
            src = await img.get_attribute("src") or await img.get_attribute("data-src")
            if src and src not in images:
                images.append(src)

        return {"description": description.strip(), "images": images}

    @staticmethod
    async def _random_delay() -> None:
        """Sleeps for a random duration to avoid bot detection."""
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        await asyncio.sleep(delay)

    @staticmethod
    def _build_city_slug(cities: list[str]) -> str:
        """
        Converts a city name to Centris URL slug format.
        "Montréal" → "montreal"
        "Saint-Lambert" → "saint-lambert"
        Falls back to "montreal" if no city provided.
        """
        if not cities:
            return "montreal"

        city = cities[0]  # Centris search is one city at a time
        # Remove accents (simplified — for production use 'unidecode' package)
        replacements = {
            "é": "e", "è": "e", "ê": "e", "ë": "e",
            "à": "a", "â": "a", "ä": "a",
            "î": "i", "ï": "i",
            "ô": "o", "ö": "o",
            "ù": "u", "û": "u", "ü": "u",
            "ç": "c",
        }
        slug = city.lower()
        for accented, plain in replacements.items():
            slug = slug.replace(accented, plain)

        # Replace spaces with hyphens, strip non-alphanumeric
        slug = re.sub(r"[^a-z0-9-]", "-", slug)
        slug = re.sub(r"-+", "-", slug).strip("-")
        return slug