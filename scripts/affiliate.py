from bs4 import BeautifulSoup
import re
from .site_config import AFFILIATE_TAGS, AMAZON_DOMAINS

PRODUCT_HINTS = ["monitor","laptop","headphone","keyboard","mouse","webcam","tv","smartphone","tablet","camera","router","ssd","hdd","mic","projector","speaker","printer"]

def build_aff_link(keyword: str, market: str) -> str:
    tag = AFFILIATE_TAGS.get(market, next(iter(AFFILIATE_TAGS.values())))
    domain = AMAZON_DOMAINS.get(market, "amazon.com")
    safe_kw = re.sub(r"[^a-zA-Z0-9\\s]", "", keyword).strip().replace(" ", "+")
    return f"https://www.{domain}/s?k={safe_kw}&tag={tag}"

def inject_affiliate_links(html: str, market: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    candidates = soup.find_all(["p","li","h2","h3"])
    for el in candidates:
        text = el.get_text(" ", strip=True)
        if len(text) < 20 or el.find("a"):
            continue
        if any(h in text.lower() for h in PRODUCT_HINTS):
            kw = " ".join(text.split()[:5])
            a = soup.new_tag("a", href=build_aff_link(kw, market), target="_blank", rel="nofollow noopener noreferrer", **{"class":"buy-btn"})
            a.string = "Buy on Amazon"
            el.append(" ")
            el.append(a)
    return str(soup)
