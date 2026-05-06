"""
scraper.py — Kijiji Immobilier Playwright scraper

Kijiji is a classifieds site with a mix of private sellers and agents.
Listings update frequently — good for catching new properties fast.
Pagination uses numbered pages in the URL.
"""

import asyncio
import random
import re
from datetime import datetime

from playwright.async_api import async_playwright, Page, BrowserContext

from ..base import BaseScraper, SearchCriteria, RawListing
from .selectors import (
    SEARCH_PAGE_URL,
    LISTING_CARD,
    CARD_PRICE,
    CARD_TITLE,
    CARD_ADDRESS,
    CARD_LINK,
    CARD_IMAGE,
    PAGINATION_NEXT,
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


class KijijiScraper(BaseScraper):
    source_name = "kijiji"

    def __init__(self, headless: bool = True, max_pages: int = 10):
        self.headless = headless
        self.max_pages = max_pages

    async def fetch_listings(self, criteria: SearchCriteria) -> list[dict]:
        print(f"[kijiji] Starting scrape — criteria: {criteria}")
        raw_listings: list[dict] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=self.headless,
                args=["--disable-blink-features=AutomationControlled", "--no-sandbox"],
            )
            context = await self._create_context(browser)
            await context.add_init_script(
                "Object.defineProperty(navigator, 'webdriver', { get: () => undefined });"
            )
            page = await context.new_page()

            try:
                # Build URL with price filter
                url = SEARCH_PAGE_URL
                params = []
                if criteria.min_price or criteria.max_price:
                    min_p = criteria.min_price or 0
                    max_p = criteria.max_price or 99999999
                    params.append(f"price={min_p}__{max_p}")
                if params:
                    url += "?" + "&".join(params)

                print(f"[kijiji] Loading: {url}")
                await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
                print("[kijiji] Waiting 8s for JS to render...")
                await asyncio.sleep(8)

                page_num = 1
                while page_num <= self.max_pages:
                    print(f"[kijiji] Scraping page {page_num}...")
                    cards = await self._scrape_listing_cards(page)
                    raw_listings.extend(cards)

                    if len(raw_listings) >= criteria.max_results:
                        print(f"[kijiji] Reached max_results ({criteria.max_results})")
                        break

                    has_next = await self._go_to_next_page(page)
                    if not has_next:
                        print(f"[kijiji] No more pages after page {page_num}")
                        break

                    page_num += 1
                    await self._random_delay()

            except Exception as e:
                print(f"[kijiji] Scrape error: {e}")
                raise
            finally:
                await browser.close()

        print(f"[kijiji] Done — collected {len(raw_listings)} raw listings")
        filtered = self._apply_client_filters(raw_listings, criteria)
        print(f"[kijiji] After filtering: {len(filtered)} listings")
        return filtered[:criteria.max_results]

    def normalise(self, raw: list[dict]) -> list[RawListing]:
        listings = []
        for item in raw:
            try:
                address_full = item.get("address", "")
                title = item.get("title", "")
                listing = RawListing(
                    source=self.source_name,
                    external_id=parse_external_id(item.get("url")),
                    title=title.strip(),
                    address=address_full.strip(),
                    city=parse_city(address_full),
                    region=parse_region(address_full),
                    postal_code=parse_postal_code(address_full),
                    price=parse_price(item.get("price")),
                    bedrooms=parse_bedrooms(item.get("bedrooms")),
                    bathrooms=None,   # not on Kijiji cards
                    size_sqft=None,   # not on Kijiji cards
                    property_type=parse_property_type(title),
                    listing_url=parse_listing_url(item.get("url")),
                    images=item.get("images", []),
                    description=item.get("description", ""),
                    listed_at=None,
                    raw=item,
                )
                listings.append(listing)
            except Exception as e:
                print(f"[kijiji] Failed to normalise listing: {e}")
                continue
        print(f"[kijiji] Normalised {len(listings)} listings")
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
            print("[kijiji] Warning: listing cards did not appear")
            return []

        await self._scroll_page(page)
        cards = await page.query_selector_all(LISTING_CARD)
        print(f"[kijiji] Found {len(cards)} cards")

        results = []
        for card in cards:
            try:
                raw = await self._extract_card_data(card)
                if raw:
                    results.append(raw)
            except Exception as e:
                print(f"[kijiji] Card error: {e}")
        return results

    async def _extract_card_data(self, card) -> dict | None:
        title_el  = await card.query_selector(CARD_TITLE)
        title     = await title_el.inner_text() if title_el else ""

        price_el  = await card.query_selector(CARD_PRICE)
        price     = await price_el.inner_text() if price_el else ""

        addr_el   = await card.query_selector(CARD_ADDRESS)
        address   = await addr_el.inner_text() if addr_el else ""

        # Bedrooms not shown on list cards — will be inferred from title in normalise()
        bedrooms  = None

        link_el   = await card.query_selector(CARD_LINK)
        url       = await link_el.get_attribute("href") if link_el else None

        img_el    = await card.query_selector(CARD_IMAGE)
        image_src = await img_el.get_attribute("src") if img_el else None

        if not url or not title:
            return None

        # Skip non-sale listings (rentals sneak into results)
        title_lower = title.lower()
        if any(w in title_lower for w in ["for rent", "à louer", "rental", "location"]):
            return None

        return {
            "title":       title.strip(),
            "price":       price.strip(),
            "address":     address.strip(),
            "bedrooms":    bedrooms.strip() if bedrooms else None,
            "url":         url,
            "images":      [image_src] if image_src else [],
            "description": "",
            "scraped_at":  datetime.utcnow().isoformat(),
        }

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
            await asyncio.sleep(5)
            return True
        except Exception as e:
            print(f"[kijiji] Pagination error: {e}")
            return False

    @staticmethod
    async def _random_delay() -> None:
        await asyncio.sleep(random.uniform(MIN_DELAY, MAX_DELAY))