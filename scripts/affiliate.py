# scripts/affiliate.py
from bs4 import BeautifulSoup
import re
from .site_config import SITE_BASE_URL
def build_aff_link(keyword, market):
    return f"{SITE_BASE_URL}/search?q={keyword.replace(' ','+')}"
def inject_affiliate_links(html, market):
    soup = BeautifulSoup(html, "html.parser")
    for p in soup.find_all(["p","li"]):
        if p.find("a"): continue
        text = p.get_text(" ", strip=True)
        if len(text.split())>6:
            a = soup.new_tag("a", href=build_aff_link(" ".join(text.split()[:4]), market), rel="nofollow noopener noreferrer")
            a.string = "Buy on Amazon"
            p.append(" ")
            p.append(a)
    return str(soup)
