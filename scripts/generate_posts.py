# scripts/generate_posts.py
import os, openai, backoff
from pathlib import Path
from datetime import datetime
from .utils import slugify

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY required")
openai.api_key = OPENAI_API_KEY

RAW_DIR = Path("content/posts_raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

@backoff.on_exception(backoff.expo, Exception, max_tries=3)
def llm_article(keyword: str) -> str:
    prompt = f"""
You are a professional commerce editor. Write a high-quality HTML article titled: {keyword}

Requirements:
- 1300–2200 words.
- Use <h1> for title, then <h2> sections: Introduction, Top Picks, Comparison Table, Product Details, Pros & Cons, How to Choose, FAQs (5), Conclusion.
- Top Picks: list 5 recommended products with one-line rationale each.
- Include an HTML <table> comparing 5 attributes (price, rating, battery, warranty, connectivity) — use placeholders if unknown.
- For each product include a short specs <ul>.
- Add pros and cons for each product.
- Insert a single-line META comment at top: <!-- META: short meta description -->
- At end include a small <script type="application/ld+json"> JSON-LD snippet (we will fill canonical later).
- Use neutral, factual tone. Avoid inventing verifiable specs—if unknown, say "specs vary by model".
Return only the HTML fragment and the META comment.
"""
    resp = openai.ChatCompletion.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[{"role":"system","content":"You are an expert commerce SEO writer."},{"role":"user","content":prompt}],
        temperature=0.7,
        max_tokens=int(os.getenv("OPENAI_MAX_TOKENS","2200")),
    )
    try:
        content = resp.choices[0].message.content.strip()
    except Exception:
        content = getattr(resp.choices[0], "text", "").strip()
    if not content:
        raise ValueError("Empty response from LLM")
    return content

def generate(keyword: str) -> dict:
    html = llm_article(keyword)
    slug = slugify(keyword)
    path = RAW_DIR / f"{slug}.html"
    path.write_text(html, encoding="utf-8")
    return {"slug": slug, "keyword": keyword, "raw_path": str(path), "date": datetime.utcnow().date().isoformat()}
