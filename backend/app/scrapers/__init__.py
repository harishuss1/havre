"""
scrapers/__init__.py — Source registry

To add a new source: import it here and add to SOURCE_REGISTRY.
Nothing else changes.
"""

from .centris import CentrisScraper
from .duproprio import DuProprioScraper
from .kijiji import KijijiScraper

SOURCE_REGISTRY: dict[str, type] = {
    "centris":   CentrisScraper,
    "duproprio": DuProprioScraper,
    "kijiji":    KijijiScraper,
}


def get_scraper(source_name: str):
    cls = SOURCE_REGISTRY.get(source_name)
    if not cls:
        raise ValueError(
            f"Unknown scraper source: '{source_name}'. "
            f"Available: {list(SOURCE_REGISTRY.keys())}"
        )
    return cls()