import os, openai, backoff
from pathlib import Path
from datetime import datetime
from .utils import slugify

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing")
openai.api_key = OPENAI_API_KEY

RAW_DIR = Path("content/posts_raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

@backoff.on_exception(backoff.expo, Exception, max_tries=3)
def llm_article(keyword: str) -> str:
    prompt = f"""
Write a comprehensive, professional buying guide and comparison article titled: {keyword}
Include:
- short intro
- top 5-7 recommended products (names and a brief rationale)
- comparison table of features
- specs bullets for each product (if unknown, use placeholders)
- pros and cons
- definitive buyer's guide and purchasing tips
- FAQs (5)
- conclusion and call to action
Output valid HTML fragment using <h1>, <h2>, <h3>, <p>, <ul>, <li>, <table>.
Aim for 1200-2000 words. Be neutral, professional, and avoid making unverified factual claims.
"""
    resp = openai.ChatCompletion.create(
        model=os.getenv("OPENAI_MODEL","gpt-4o-mini"),
        messages=[
            {"role":"system","content":"You are a professional commerce editor and SEO writer."},
            {"role":"user","content":prompt}
        ],
        temperature=0.6,
        max_tokens=2200,
    )
    # read common response shapes
    try:
        content = resp.choices[0].message.content.strip()
    except Exception:
        content = getattr(resp.choices[0], "text", "").strip()
    if not content:
        raise ValueError("Empty content returned by LLM")
    return content

def generate(keyword: str) -> dict:
    html = llm_article(keyword)
    slug = slugify(keyword)
    path = RAW_DIR / f"{slug}.html"
    path.write_text(html, encoding="utf-8")
    return {"slug": slug, "keyword": keyword, "raw_path": str(path), "date": datetime.utcnow().date().isoformat()}
