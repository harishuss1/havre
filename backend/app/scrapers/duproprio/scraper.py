"""
scraper.py — DuProprio.com Playwright scraper
"""

import asyncio
import random
import re
from datetime import datetime

from playwright.async_api import async_playwright, Page, BrowserContext

from ..base import BaseScraper, SearchCriteria, RawListing
from .selectors import (
    SEARCH_PAGE_URL,
    SEARCH_PAGE_URL_CITY,
    LISTING_CARD,
    CARD_PRICE,
    CARD_ADDRESS,
    CARD_BEDROOMS,
    CARD_BATHROOMS,
    CARD_AREA,
    CARD_LINK,
    CARD_IMAGE,
    PAGINATION_NEXT,
    URL_TYPE_MAP,
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

USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
]

MIN_DELAY = 2.0
MAX_DELAY = 5.0

def _dedupe_city(slug: str) -> str:
    """
    Removes duplicated city names in DuProprio slugs.
    "st-jean-sur-richelieu-st-jean-sur-richelieu" → "St Jean Sur Richelieu"
    "trois-rivieres-trois-rivieres-ouest" → "Trois Rivieres Ouest"
    """
    words = slug.replace("-", " ")
    parts = words.split()
    half = len(parts) // 2
    if half > 0 and parts[:half] == parts[half:half + half]:
        return " ".join(parts[half:]).title()
    return words.title()

class DuProprioScraper(BaseScraper):
    source_name = "duproprio"

    def __init__(self, headless: bool = True, max_pages: int = 10):
        self.headless = headless
        self.max_pages = max_pages

    async def fetch_listings(self, criteria: SearchCriteria) -> list[dict]:
        print(f"[duproprio] Starting scrape — criteria: {criteria}")
        raw_listings: list[dict] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=self.headless)
            context = await self._create_context(browser)
            page = await context.new_page()

            try:
                city = criteria.cities[0] if criteria.cities else ""
                url = SEARCH_PAGE_URL_CITY.format(city=city) if city else SEARCH_PAGE_URL
                if criteria.min_price:
                    url += f"&min_price={criteria.min_price}"
                if criteria.max_price:
                    url += f"&max_price={criteria.max_price}"
                if criteria.min_bedrooms:
                    url += f"&num_bedroom_min={criteria.min_bedrooms}"

                print(f"[duproprio] Loading: {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
                await asyncio.sleep(5)

                page_num = 1
                while page_num <= self.max_pages:
                    print(f"[duproprio] Scraping page {page_num}...")
                    cards = await self._scrape_listing_cards(page)
                    raw_listings.extend(cards)

                    if len(raw_listings) >= criteria.max_results:
                        print(f"[duproprio] Reached max_results ({criteria.max_results})")
                        break

                    has_next = await self._go_to_next_page(page)
                    if not has_next:
                        print(f"[duproprio] No more pages after page {page_num}")
                        break

                    page_num += 1
                    await self._random_delay()

            except Exception as e:
                print(f"[duproprio] Scrape error: {e}")
                raise
            finally:
                await browser.close()

        print(f"[duproprio] Done — collected {len(raw_listings)} raw listings")
        filtered = self._apply_client_filters(raw_listings, criteria)
        print(f"[duproprio] After filtering: {len(filtered)} listings")
        return filtered[:criteria.max_results]

    def normalise(self, raw: list[dict]) -> list[RawListing]:
        listings = []
        for item in raw:
            try:
                listing = RawListing(
                    source=self.source_name,
                    external_id=item.get("card_id", ""),
                    title=item.get("address", "").strip(),
                    address=item.get("address", "").strip(),
                    city=parse_city(item.get("city", "")),
                    region="QC",
                    postal_code="",
                    price=parse_price(item.get("price")),
                    bedrooms=parse_bedrooms(item.get("bedrooms")),
                    bathrooms=parse_bathrooms(item.get("bathrooms")),
                    size_sqft=parse_area(item.get("area")),
                    property_type=item.get("property_type", "other"),
                    listing_url=parse_listing_url(item.get("url")),
                    images=item.get("images", []),
                    description="",
                    listed_at=None,
                    raw=item,
                )
                listings.append(listing)
            except Exception as e:
                print(f"[duproprio] Failed to normalise: {e}")
                continue
        print(f"[duproprio] Normalised {len(listings)} listings")
        return listings

    async def _create_context(self, browser) -> BrowserContext:
        return await browser.new_context(
            user_agent=random.choice(USER_AGENTS),
            viewport={"width": 1440, "height": 900},
            locale="en-CA",
            timezone_id="America/Toronto",
        )

    async def _scrape_listing_cards(self, page: Page) -> list[dict]:
        try:
            await page.wait_for_selector(LISTING_CARD, timeout=15_000)
        except Exception:
            print("[duproprio] Warning: listing cards did not appear")
            return []

        await self._scroll_page(page)
        cards = await page.query_selector_all(LISTING_CARD)
        print(f"[duproprio] Found {len(cards)} cards")

        results = []
        for card in cards:
            try:
                raw = await self._extract_card_data(card)
                if raw:
                    results.append(raw)
            except Exception as e:
                print(f"[duproprio] Card error: {e}")
        return results

    async def _extract_card_data(self, card) -> dict | None:
        # Link first — we derive city, type, and ID from the URL
        link_el = await card.query_selector(CARD_LINK)
        url = await link_el.get_attribute("href") if link_el else None
        if not url:
            return None

        # Parse city, property type, and ID from URL
        # e.g. /en/quebec-rive-sud/st-nicolas/bungalow-for-sale/hab-...-1128802
        city, property_type, card_id = self._parse_url(url)

        price_el  = await card.query_selector(CARD_PRICE)
        price     = await price_el.inner_text() if price_el else ""

        address_el = await card.query_selector(CARD_ADDRESS)
        address    = await address_el.inner_text() if address_el else ""

        # Bedrooms — may not be present on all cards
        bed_el    = await card.query_selector(CARD_BEDROOMS)
        bedrooms  = await bed_el.inner_text() if bed_el else None

        bath_el   = await card.query_selector(CARD_BATHROOMS)
        bathrooms = await bath_el.inner_text() if bath_el else None

        area_el   = await card.query_selector(CARD_AREA)
        area      = await area_el.inner_text() if area_el else None

        img_el    = await card.query_selector(CARD_IMAGE)
        image_src = await img_el.get_attribute("src") if img_el else None

        return {
            "card_id":       card_id,
            "price":         price.strip(),
            "address":       address.strip(),
            "city":          city,
            "bedrooms":      bedrooms.strip() if bedrooms else None,
            "bathrooms":     bathrooms.strip() if bathrooms else None,
            "area":          area.strip() if area else None,
            "url":           url,
            "property_type": property_type,
            "images":        [image_src] if image_src else [],
            "scraped_at":    datetime.utcnow().isoformat(),
        }

    @staticmethod
    def _parse_url(url: str) -> tuple[str, str, str]:
        path = url.replace("https://duproprio.com", "").replace("http://duproprio.com", "")
        parts = [p for p in path.split("/") if p]

        type_idx = next(
            (i for i, p in enumerate(parts) if "-for-sale" in p or "-a-vendre" in p or "-for-rent" in p),
            None
        )
        if type_idx is None or type_idx == 0:
            return "", "other", ""

        # City slug — deduplicate repeated halves
        # e.g. "st-jean-sur-richelieu-st-jean-sur-richelieu" → "St Jean Sur Richelieu"
        city_slug = parts[type_idx - 1]
        city = _dedupe_city(city_slug)

        type_slug = re.sub(r"-(for-sale|a-vendre|for-rent|a-louer).*", "", parts[type_idx])
        property_type = URL_TYPE_MAP.get(type_slug.lower(), "other")

        id_match = re.search(r"(\d+)$", parts[-1])
        card_id = id_match.group(1) if id_match else ""

        return city, property_type, card_id

    def _apply_client_filters(self, listings: list[dict], criteria: SearchCriteria) -> list[dict]:
        result = []
        for l in listings:
            price = parse_price(l.get("price"))
            beds  = parse_bedrooms(l.get("bedrooms"))
            if criteria.min_price and price < criteria.min_price:
                continue
            if criteria.max_price and price > criteria.max_price:
                continue
            if criteria.min_bedrooms and beds is not None and beds < criteria.min_bedrooms:
                continue
            result.append(l)
        return result

    async def _scroll_page(self, page: Page) -> None:
        height = await page.evaluate("document.body.scrollHeight")
        current, step = 0, 600
        while current < height:
            current = min(current + step, height)
            await page.evaluate(f"window.scrollTo(0, {current})")
            await asyncio.sleep(0.2)
        await page.evaluate("window.scrollTo(0, 0)")

    async def _go_to_next_page(self, page: Page) -> bool:
        next_btn = await page.query_selector(PAGINATION_NEXT)
        if not next_btn:
            return False
        try:
            await next_btn.click()
            await page.wait_for_load_state("domcontentloaded", timeout=45_000)
            await asyncio.sleep(3)
            return True
        except Exception as e:
            print(f"[duproprio] Pagination error: {e}")
            return False

    @staticmethod
    async def _random_delay() -> None:
        await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))