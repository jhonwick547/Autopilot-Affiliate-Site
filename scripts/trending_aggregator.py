import feedparser, time, random, logging
from backoff import on_exception, expo
from requests.exceptions import RequestException
import requests
from bs4 import BeautifulSoup

log = logging.getLogger("trending")
log.setLevel(logging.INFO)

GOOGLE_NEWS = {
    "IN":"https://news.google.com/rss?hl=en-IN&gl=IN&ceid=IN:en",
    "US":"https://news.google.com/rss?hl=en-US&gl=US&ceid=US:en"
}
YOUTUBE_TRENDING = "https://www.youtube.com/feed/trending"
HEADERS = {"User-Agent":"Mozilla/5.0 (compatible; TrendBot/1.0; +https://example.com/bot)"}

def clean_title(t: str) -> str:
    t = t.split(" - ")[0].split(" | ")[0]
    t = t.replace("Review","").replace("review","").strip()
    return "".join(ch for ch in t if ord(ch) < 128).strip()

def google_trends(market="US", limit=6):
    url = GOOGLE_NEWS.get(market, GOOGLE_NEWS["US"])
    log.info("Fetching Google News feed %s", url)
    feed = feedparser.parse(url)
    topics=[]
    for e in feed.entries[:limit*2]:
        t = clean_title(e.title)
        if len(t)>6:
            topics.append(t)
            if len(topics)>=limit: break
    return topics

from backoff import on_exception, expo
import requests
@on_exception(expo, RequestException, max_tries=3)
def fetch_url(url):
    r = requests.get(url, headers=HEADERS, timeout=12)
    r.raise_for_status()
    time.sleep(0.6)
    return r.text

def youtube_trend_scrape(limit=6):
    try:
        html = fetch_url(YOUTUBE_TRENDING)
    except Exception as e:
        log.warning("YouTube scrape failed: %s", e)
        return []
    soup = BeautifulSoup(html, "html.parser")
    titles=[]
    for a in soup.select("a#video-title")[:limit]:
        t = a.get("title") or a.get_text(strip=True)
        if t: titles.append(clean_title(t))
    return titles

def amazon_bestsellers(market="US", limit=6):
    from requests.exceptions import RequestException
    url = "https://www.amazon.in/gp/bestsellers" if market=="IN" else "https://www.amazon.com/Best-Sellers/zgbs"
    log.info("Fetching Amazon bestsellers: %s", url)
    try:
        html = fetch_url(url)
    except Exception as e:
        log.warning("Amazon fetch failed: %s", e)
        return []
    soup = BeautifulSoup(html, "html.parser")
    items=[]
    selectors=[".p13n-sc-truncate",".zg-item-immersion .p13n-sc-truncate","#zg-ordered-list .a-link-normal"]
    for sel in selectors:
        for el in soup.select(sel):
            t = el.get_text(" ",strip=True)
            t = clean_title(t)
            if t and len(t)>8:
                items.append(t)
            if len(items)>=limit: break
        if len(items)>=limit: break
    if len(items)<limit:
        for img in soup.select("img[alt]"):
            alt=clean_title(img["alt"])
            if alt and len(alt)>8: items.append(alt)
            if len(items)>=limit: break
    return items[:limit]

def aggregate_trends(markets=("IN","US"), per_source=4):
    keywords=[]
    for m in markets:
        try: keywords += google_trends(m, limit=per_source)
        except Exception as e: log.warning("google_trends failed %s", e)
        try: keywords += amazon_bestsellers(m, limit=per_source)
        except Exception as e: log.warning("amazon_bestsellers failed %s", e)
    try: keywords += youtube_trend_scrape(limit=per_source)
    except Exception as e: log.warning("youtube_trend_scrape failed %s", e)
    seen=set(); out=[]
    for k in keywords:
        kk=k.lower()
        if kk in seen: continue
        if any(b in kk for b in ("election","war","covid","crime")): continue
        seen.add(kk); out.append(k)
    return out[: max(10, per_source*len(markets))]
