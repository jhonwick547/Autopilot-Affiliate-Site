# scripts/ensure_public.py
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
POSTS = PUBLIC / "posts"

PUBLIC.mkdir(parents=True, exist_ok=True)
POSTS.mkdir(parents=True, exist_ok=True)

def create_placeholder_post():
    fallback_post = POSTS / "welcome-placeholder.html"
    if fallback_post.exists():
        return
    html = f"""<!doctype html>
<html lang="en">
<head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
<title>Welcome — Autopilot Affiliate Site</title>
<style>body{{font-family:Inter,system-ui,sans-serif;max-width:900px;margin:28px auto;padding:12px}}</style>
</head><body>
<header style="background:#0b6ef6;color:#fff;padding:24px;text-align:center;"><h1>Welcome to Your Autopilot Affiliate Site</h1></header>
<main><h2>Next Steps</h2><p>Your automation will generate Amazon product reviews and comparisons automatically.</p><p><a href="../index.html">Return to home</a></p></main>
<footer style="text-align:center;color:#777">&copy; {datetime.utcnow().year} {os.getenv('SITE_NAME','Affiliate Site')}</footer>
</body></html>"""
    fallback_post.write_text(html, encoding="utf-8")
    print("Created placeholder")

def create_index():
    posts_links = []
    for p in sorted(POSTS.glob("*.html")):
        name = p.stem.replace("-", " ").title()
        posts_links.append(f"<li><a href='posts/{p.name}'>{name}</a></li>")
    if not posts_links:
        posts_links = ["<li>No posts available yet — please check back later.</li>"]
    html = f"""<!doctype html><html><head><meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/><title>{os.getenv('SITE_NAME','Affiliate Site')}</title></head><body><header style="text-align:center;background:#0b6ef6;color:#fff;padding:24px"><h1>{os.getenv('SITE_NAME','Affiliate Site')}</h1></header><main><ul>{''.join(posts_links)}</ul></main><footer style="text-align:center;color:#777">&copy; {datetime.utcnow().year} {os.getenv('SITE_NAME','Affiliate Site')}</footer></body></html>"""
    (PUBLIC / "index.html").write_text(html, encoding="utf-8")
    print("Created index.html")

def create_nojekyll_and_404():
    (PUBLIC / ".nojekyll").write_text("", encoding="utf-8")
    (PUBLIC / "404.html").write_text("<h1>404 — Page not found</h1>", encoding="utf-8")

def main():
    if not any(POSTS.glob("*.html")):
        create_placeholder_post()
    create_index()
    create_nojekyll_and_404()
    print("ensure_public done")

if __name__ == "__main__":
    main()
