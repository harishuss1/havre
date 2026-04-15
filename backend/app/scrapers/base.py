"""
base.py — BaseScraper abstract class

Every source scraper in Havre inherits from this class and implements
two methods: fetch_listings() and normalise(). That's the entire contract.
Adding a new source = new folder + subclass. Nothing else changes.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class SearchCriteria:
    """
    Filters a user passes to the scraper.
    All fields are optional — omitting one means 'no restriction'.
    """
    min_price: int | None = None
    max_price: int | None = None
    min_bedrooms: int | None = None
    cities: list[str] = field(default_factory=list)
    property_types: list[str] = field(default_factory=list)  # house, condo, duplex, land, other
    max_results: int = 100


@dataclass
class RawListing:
    """
    Normalised listing schema shared across all scrapers.
    Every scraper's normalise() method must return a list of these.
    """
    source: str                        # e.g. "centris", "duproprio"
    external_id: str                   # listing ID on the source site
    title: str
    address: str
    city: str
    region: str
    postal_code: str
    price: int                         # CAD, no cents
    bedrooms: int | None
    bathrooms: int | None
    size_sqft: int | None
    property_type: str                 # house | condo | duplex | land | other
    listing_url: str
    images: list[str] = field(default_factory=list)
    description: str = ""
    listed_at: datetime | None = None
    raw: dict[str, Any] = field(default_factory=dict)  # original raw data for debugging


class BaseScraper(ABC):
    """
    Abstract base class for all Havre source scrapers.

    Usage:
        class CentrisScraper(BaseScraper):
            source_name = "centris"

            async def fetch_listings(self, criteria):
                # ... playwright logic ...
                return raw_data

            def normalise(self, raw):
                # ... map raw fields to RawListing ...
                return [RawListing(...)]
    """

    # Subclasses must set this to the source identifier (e.g. "centris")
    source_name: str = ""

    @abstractmethod
    async def fetch_listings(self, criteria: SearchCriteria) -> list[dict]:
        """
        Launch the browser, navigate the site, and return raw listing data
        as a list of dicts. Do not normalise here — just collect.
        """
        ...

    @abstractmethod
    def normalise(self, raw: list[dict]) -> list[RawListing]:
        """
        Map raw site-specific dicts to the shared RawListing schema.
        This is the only place that knows about a source's field names.
        """
        ...

    async def run(self, criteria: SearchCriteria) -> list[RawListing]:
        """
        Convenience method: fetch + normalise in one call.
        Celery tasks call this — they don't need to know the two-step.
        """
        raw = await self.fetch_listings(criteria)
        return self.normalise(raw)