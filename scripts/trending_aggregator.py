# scripts/trending_aggregator.py
"""
Aggregator simplified to return product titles from content/products.json (scraper output).
If products.json isn't present, fall back to scraping Amazon bestsellers for titles.
No Google News, no YouTube scraping — only Amazon-focused.
"""

import json
import logging
from pathlib import Path
from typing import List
from .amazon_scraper import scrape_bestsellers

log = logging.getLogger("trending")
log.setLevel(logging.INFO)

CONTENT_DIR = Path("content")
PRODUCTS_FILE = CONTENT_DIR / "products.json"


def read_products_titles(limit: int = 20) -> List[str]:
    """Read product titles from content/products.json (created by amazon_scraper)."""
    if PRODUCTS_FILE.exists():
        try:
            data = json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))
            titles = [p.get("title", "").strip() for p in data if p.get("title")]
            titles = [t for t in titles if t]
            log.info("Loaded %d titles from %s", len(titles), PRODUCTS_FILE)
            return titles[:limit]
        except Exception as e:
            log.warning("Failed to read products.json: %s", e)
    return []


def amazon_fallback(limit: int = 20) -> List[str]:
    """Fallback: scrape Amazon bestsellers titles via amazon_scraper helper."""
    try:
        items = scrape_bestsellers("US", limit=limit)
        titles = [it.get("title") for it in items if it.get("title")]
        return titles[:limit]
    except Exception as e:
        log.warning("amazon_fallback failed: %s", e)
        return []


def aggregate_trends(markets=("IN", "US"), per_source=6) -> List[str]:
    """
    Returns a list of product titles derived from scraped products.json
    or falls back to Amazon bestsellers scraping.
    """
    limit = max(per_source * len(markets), 10)
    titles = read_products_titles(limit=limit)
    if titles:
        return titles[:limit]
    log.info("No products.json found; falling back to scraping Amazon bestsellers")
    return amazon_fallback(limit=limit)
