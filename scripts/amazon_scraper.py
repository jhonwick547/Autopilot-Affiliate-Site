# scripts/amazon_scraper.py
import os, json, random, logging
from pathlib import Path
from backoff import on_exception, expo
from requests.exceptions import RequestException
import requests
from bs4 import BeautifulSoup

log = logging.getLogger("amazon_scraper")
log.setLevel(logging.INFO)

OUT = Path("content")
OUT.mkdir(parents=True, exist_ok=True)
OUT_FILE = OUT / "products.json"

PA_ACCESS = os.getenv("PA_API_ACCESS_KEY")
PA_SECRET = os.getenv("PA_API_SECRET")
PA_TAG = os.getenv("PA_API_TAG")
PROXY_LIST = os.getenv("PROXY_LIST")

HEADERS = {"User-Agent":"Mozilla/5.0 (compatible; AutopilotBot/1.0)"}

def get_session():
    s = requests.Session()
    s.headers.update(HEADERS)
    if PROXY_LIST:
        proxies = [p.strip() for p in PROXY_LIST.split(",") if p.strip()]
        if proxies:
            p = random.choice(proxies)
            s.proxies.update({"http":p,"https":p})
    return s

@on_exception(expo, RequestException, max_tries=3)
def fetch(url):
    s = get_session()
    resp = s.get(url, timeout=12)
    resp.raise_for_status()
    return resp.text

def parse_bestsellers(html, limit=20):
    soup = BeautifulSoup(html, "lxml")
    items=[]
    # try a few selectors
    for sel in ["#zg-ordered-list li", ".zg-item-immersion", ".a-carousel-card"]:
        for el in soup.select(sel):
            title_el = el.select_one("img[alt], .p13n-sc-truncate, .a-link-normal")
            if title_el:
                title = title_el.get("alt") or title_el.get_text(" ", strip=True)
                if title and len(title)>8:
                    items.append({"title": title.strip()})
            if len(items)>=limit:
                break
        if len(items)>=limit:
            break
    return items[:limit]

def paapi_fetch_products():
    # Optional: implement PA-API integration here if you have credentials.
    # Return list of dicts with keys: title, market, asin, url, price, rating, reviews_count, features, image_urls, category
    log.info("PA-API credentials present but PA-API client not implemented. Skipping PA-API.")
    return []

def scrape_bestsellers(market="US", limit=20):
    url = "https://www.amazon.in/gp/bestsellers" if market=="IN" else "https://www.amazon.com/Best-Sellers/zgbs"
    try:
        html = fetch(url)
    except Exception as e:
        log.warning("Failed fetch %s: %s", url, e)
        return []
    return parse_bestsellers(html, limit=limit)

def run():
    products=[]
    if PA_ACCESS and PA_SECRET and PA_TAG:
        try:
            products = paapi_fetch_products()
        except Exception as e:
            log.warning("PA-API error: %s", e)
    if not products:
        for m in ["IN","US"]:
            found = scrape_bestsellers(m, limit=30)
            for f in found:
                products.append({"title": f["title"], "market": m, "source": "bestsellers"})
    # normalize & dedupe
    seen=set(); out=[]
    for p in products:
        t = p.get("title","").strip()
        if not t: continue
        key=t.lower()
        if key in seen: continue
        seen.add(key)
        out.append({
            "title": t,
            "market": p.get("market","US"),
            "asin": p.get("asin",""),
            "price": p.get("price",""),
            "rating": p.get("rating",""),
            "reviews_count": p.get("reviews_count",""),
            "features": p.get("features",[]),
            "image_urls": p.get("image_urls",[]),
            "url": p.get("url",""),
            "source": p.get("source","scrape")
        })
    OUT_FILE.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    log.info("Wrote %d products to %s", len(out), OUT_FILE)

if __name__ == "__main__":
    run()
