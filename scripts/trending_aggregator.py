# scripts/trending_aggregator.py
"""
Simplified aggregator: return product titles from content/products.json (scraper output).
If products.json isn't present, fall back to the lightweight Amazon bestsellers scraper.
No Google News / YouTube scraping.
"""
import json
import logging
import time
from pathlib import Path
from .amazon_scraper import scrape_bestsellers
from requests.exceptions import RequestException

log = logging.getLogger("trending")
log.setLevel(logging.INFO)

CONTENT_DIR = Path("content")
PRODUCTS_FILE = CONTENT_DIR / "products.json"

def read_products_titles(limit=20):
    if PRODUCTS_FILE.exists():
        try:
            data = json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))
            titles = [p.get("title","").strip() for p in data if p.get("title")]
            titles = [t for t in titles if t]
            log.info("Loaded %d titles from %s", len(titles), PRODUCTS_FILE)
            return titles[:limit]
        except Exception as e:
            log.warning("Failed to read products.json: %s", e)
    return []

def amazon_fallback(limit=20):
    # use the existing scraper helper to get bestseller titles
    try:
        items = scrape_bestsellers("US", limit=limit)
        titles = [it.get("title") for it in items if it.get("title")]
        return titles[:limit]
    except RequestException as e:
        log.warning("amazon_fallback failed: %s", e)
        return []

def aggregate_trends(markets=("IN","US"), per_source=6):
    """
    Returns a list of keywords (product titles) derived from scraped products.json
    or fallbacks. This deliberately avoids Google/YouTube sources.
    """
    limit = max(per_source * len(markets), 10)
    titles = read_products_titles(limit=limit)
    if titles:
        return titles[:limit]
    # fallback to Amazon bestsellers (simple scrape)
    log.info("No products.json found; falling back to scraping Amazon bestsellers")
    return amazon_fallback(limit=limit)
