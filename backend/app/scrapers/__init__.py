"""
scrapers/__init__.py — Source registry

This is the one place that knows about all available scrapers.
To add a new source: import it here and add it to SOURCE_REGISTRY.
Nothing else needs to change.
"""

from .centris import CentrisScraper

# Maps source name → scraper class
# Celery tasks and the API both look up scrapers from this dict.
SOURCE_REGISTRY: dict[str, type] = {
    "centris": CentrisScraper,
    # "duproprio": DuProprioScraper,   ← uncomment when ready
    # "kijiji": KijijiScraper,         ← uncomment when ready
}


def get_scraper(source_name: str):
    """Returns an instantiated scraper for the given source name."""
    cls = SOURCE_REGISTRY.get(source_name)
    if not cls:
        raise ValueError(f"Unknown scraper source: '{source_name}'. "
                         f"Available: {list(SOURCE_REGISTRY.keys())}")
    return cls()