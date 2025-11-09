# scripts/trending_aggregator.py
import json, logging
from pathlib import Path
from typing import List
from .amazon_scraper import scrape_bestsellers

log = logging.getLogger("trending")
log.setLevel(logging.INFO)

PRODUCTS_FILE = Path("content") / "products.json"

def read_products_titles(limit: int = 20) -> List[str]:
    if PRODUCTS_FILE.exists():
        try:
            data = json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))
            titles = [p.get("title","").strip() for p in data if p.get("title")]
            return titles[:limit]
        except Exception as e:
            log.warning("Failed to read products.json: %s", e)
    return []

def amazon_fallback(limit=20):
    items = scrape_bestsellers("US", limit=limit)
    titles = [it.get("title") for it in items if it.get("title")]
    return titles[:limit]

def aggregate_trends(markets=("IN","US"), per_source=6):
    limit = max(per_source * len(markets), 10)
    titles = read_products_titles(limit=limit)
    if titles:
        log.info("Using %d titles from products.json", len(titles))
        return titles[:limit]
    log.info("No products.json found, falling back to Amazon bestsellers scraping")
    return amazon_fallback(limit=limit)
