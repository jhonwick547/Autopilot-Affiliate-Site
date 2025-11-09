# scripts/generate_and_publish.py
"""
Orchestrator:
- Prefer scraped products.json (amazon_scraper output)
- For each product title selected:
    - call generate_posts.generate()
    - call images.download_image() (OpenAI Images)
    - render_post() into public/posts/
- Build index + sitemap, ensure basics
"""

import os
import json
import logging
from pathlib import Path
from .trending_aggregator import aggregate_trends
from .generate_posts import generate
from .images import download_image
from .render import render_post, render_index, write_basics
from .sitemap_build import build_sitemap
from .utils import today_iso

log = logging.getLogger("orchestrator")
log.setLevel(logging.INFO)

CONTENT = Path("content")
PRODUCTS_FILE = CONTENT / "products.json"
PUBLIC = Path("public")


def read_products(limit=20):
    if PRODUCTS_FILE.exists():
        try:
            data = json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))
            return data[:limit]
        except Exception as e:
            log.warning("Failed to read products.json: %s", e)
    return []


def main():
    posts_info = []
    markets = os.getenv("MARKETS", "IN,US").split(",")
    per_market = int(os.getenv("POSTS_PER_MARKET", "2"))

    # Prefer product-driven generation if products.json exists
    products = read_products(limit=per_market * len(markets))
    if products:
        log.info("Using %d scraped products from products.json", len(products))
        topics = [p.get("title") for p in products if p.get("title")]
    else:
        # As fallback, aggregate titles (this will call amazon bestsellers fallback)
        topics = aggregate_trends(markets=tuple(markets), per_source=per_market)
        log.info("Collected %d fallback product topics", len(topics))

    # Limit to desired number
    max_posts = per_market * len(markets)
    chosen = topics[:max_posts]

    for t in chosen:
        try:
            meta = generate(t)
            hero = None
            try:
                hero = download_image(t)
            except Exception as e:
                log.warning("Image generation failed for '%s': %s", t, e)
            out = render_post(Path(meta["raw_path"]), title=meta["keyword"].title(), market="IN", hero_url=hero)
            posts_info.append({"title": meta["keyword"].title(), "filename": Path(out).name, "date": today_iso()})
            log.info("Published: %s -> %s", t, out)
        except Exception as e:
            log.exception("Failed to generate for topic '%s': %s", t, e)

    # Sort newest first
    posts_info = sorted(posts_info, key=lambda x: x["date"], reverse=True)

    # Write index, basics, and sitemap
    write_basics()
    render_index(posts_info)
    try:
        build_sitemap()
    except Exception as e:
        log.warning("Sitemap build failed: %s", e)

    log.info("Generation complete — %d posts published", len(posts_info))


if __name__ == "__main__":
    main()
