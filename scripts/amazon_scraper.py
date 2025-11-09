"""
amazon_scraper.py
- Preferred: uses Amazon Product Advertising API if PA_API_* secrets present.
- Fallback: polite HTML scraping of Best Sellers and category top-N with backoff.
- Output: content/products.json (list of product dicts)
"""
import os, json, time, random, logging
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from backoff import on_exception, expo
from requests.exceptions import RequestException

log = logging.getLogger("amazon_scraper")
log.setLevel(logging.INFO)

OUT = Path("content")
OUT.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT / "products.json"

PA_ACCESS = os.getenv("PA_API_ACCESS_KEY")
PA_SECRET = os.getenv("PA_API_SECRET")
PA_TAG = os.getenv("PA_API_TAG")
PROXY_LIST = os.getenv("PROXY_LIST")  # optional comma-separated

HEADERS = {"User-Agent":"Mozilla/5.0 (compatible; ScraperBot/1.0; +https://example.com/bot)"}

def get_proxy_session():
    s = requests.Session()
    if PROXY_LIST:
        proxies = [p.strip() for p in PROXY_LIST.split(",") if p.strip()]
        if proxies:
            p = random.choice(proxies)
            s.proxies.update({"http":p,"https":p})
    s.headers.update(HEADERS)
    return s

@on_exception(expo, RequestException, max_tries=4)
def fetch(url, session=None):
    s = session or get_proxy_session()
    r = s.get(url, timeout=12)
    r.raise_for_status()
    time.sleep(0.8 + random.random()*0.6)
    return r.text

def parse_bestsellers_html(html, limit=10):
    soup = BeautifulSoup(html, "html.parser")
    items=[]
    # try common list selectors
    for sel in ["#zg-ordered-list li",".zg-item-immersion",".a-carousel"]:
        for el in soup.select(sel):
            title_el = el.select_one("img[alt], .p13n-sc-truncate, .a-link-normal")
            if title_el:
                title = title_el.get("alt") or title_el.get_text(" ", strip=True)
                if title and len(title)>8:
                    items.append({"title": title.strip()})
            if len(items)>=limit: break
        if len(items)>=limit: break
    return items[:limit]

def paapi_fetch_products():
    # Placeholder: user should implement PA-API usage here.
    # If you have PA-API credentials, implement signed requests to Product Advertising API.
    log.info("PA-API credentials present but PA-API client not implemented. Skipping.")
    return []

def scrape_bestsellers(market="IN", limit=10):
    url = "https://www.amazon.in/gp/bestsellers" if market=="IN" else "https://www.amazon.com/Best-Sellers/zgbs"
    try:
        html = fetch(url)
    except Exception as e:
        log.warning("fetch bestsellers failed: %s", e)
        return []
    items = parse_bestsellers_html(html, limit=limit)
    return items

def run():
    products=[]
    # prefer PA-API if creds available
    if PA_ACCESS and PA_SECRET and PA_TAG:
        try:
            products = paapi_fetch_products()
        except Exception as e:
            log.warning("PA-API failed: %s", e)
    if not products:
        # fallback: scrape bestsellers for each market
        markets = ["IN","US"]
        for m in markets:
            try:
                found = scrape_bestsellers(m, limit=20)
                for f in found:
                    products.append({"market":m,"title":f["title"]})
            except Exception as e:
                log.warning("scrape failed for %s: %s", m, e)
    # dedupe + minimal normalize
    seen=set(); out=[]
    for p in products:
        t = p.get("title","").strip()
        key = t.lower()
        if not t or key in seen: continue
        seen.add(key)
        out.append({"title": t, "market": p.get("market","US"), "source":"amazon_bestsellers"})
    OUT_FILE.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Wrote %d products to %s", len(out), OUT_FILE)

if __name__ == "__main__":
    run()
