from pathlib import Path
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from .site_config import PUBLIC, SITE_BASE_URL, SITEMAPS_DIR

def _iso(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat(timespec="seconds")

def build_sitemap():
    SITEMAPS_DIR.mkdir(parents=True, exist_ok=True)
    urls=[]
    posts_dir = PUBLIC / "posts"
    if posts_dir.exists():
        for p in sorted(posts_dir.glob("*.html")):
            urls.append({"loc": f"{SITE_BASE_URL}/posts/{p.name}", "lastmod": _iso(p.stat().st_mtime), "priority":"0.7", "changefreq":"weekly"})
    root = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for u in urls:
        el = ET.SubElement(root, "url")
        ET.SubElement(el, "loc").text = u["loc"]
        ET.SubElement(el, "lastmod").text = u["lastmod"]
        ET.SubElement(el, "changefreq").text = u["changefreq"]
        ET.SubElement(el, "priority").text = u["priority"]
    data = b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(root, encoding="utf-8")
    (PUBLIC / "sitemap_index.xml").write_bytes(data)
    (PUBLIC / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {SITE_BASE_URL}/sitemap_index.xml\n", encoding="utf-8")
