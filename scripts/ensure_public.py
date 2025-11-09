# scripts/ensure_public.py
"""
Ensure public/ has at least an index and one post to avoid GitHub Pages 404.
This helper is intentionally small and safe — called by the workflow.
"""

import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
POSTS = PUBLIC / "posts"

PUBLIC.mkdir(parents=True, exist_ok=True)
POSTS.mkdir(parents=True, exist_ok=True)

# If there are no posts, create a fallback placeholder post
if not any(POSTS.glob("*.html")):
    fallback_post = POSTS / "welcome-placeholder.html"
    if not fallback_post.exists():
        fallback_html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/>
    <meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>Welcome — Autopilot Site</title>
    <style>body{{font-family:Inter,system-ui,sans-serif;max-width:900px;margin:28px auto;padding:12px}}</style>
  </head>
  <body>
    <header style="background:#0b6ef6;color:#fff;padding:24px;text-align:center;">
      <h1>Welcome — Autopilot Affiliate Site</h1>
      <p>Automatically created placeholder to prevent a 404 page.</p>
    </header>
    <main>
      <h2>Site status</h2>
      <p>This placeholder exists because the generator produced no posts during this run. Check Actions logs for the 'generate' step.</p>
    </main>
    <footer style="text-align:center;padding:12px;color:#777">© {os.getenv('SITE_NAME','Affiliate Site')}</footer>
  </body>
</html>"""
        fallback_post.write_text(fallback_html, encoding="utf-8")

# Ensure index.html exists and references posts
index = PUBLIC / "index.html"
if not index.exists():
    posts_list = []
    for p in sorted(POSTS.glob("*.html")):
        posts_list.append(f"<li><a href='posts/{p.name}'>{p.stem.replace('-',' ').title()}</a></li>")
    listing = "<ul>" + ("\n".join(posts_list) if posts_list else "<li>Welcome — no posts yet</li>") + "</ul>"
    index_html = f"""<!doctype html>
<html>
  <head>
    <meta charset="utf-8"/><meta name="viewport" content="width=device-width,initial-scale=1"/>
    <title>{os.getenv('SITE_NAME','Affiliate Site')}</title>
    <style>body{{font-family:Inter,system-ui,sans-serif;max-width:900px;margin:20px auto;padding:12px}}</style>
  </head>
  <body>
    <header style="background:#0b6ef6;color:#fff;padding:20px;text-align:center;"><h1>{os.getenv('SITE_NAME','Affiliate Site')}</h1></header>
    <main style="max-width:900px;margin:20px auto;padding:12px;"><h2>Latest Posts</h2>{listing}</main>
    <footer style="text-align:center;padding:12px;color:#666">© {os.getenv('SITE_NAME','Affiliate Site')}</footer>
  </body>
</html>"""
    index.write_text(index_html, encoding="utf-8")

# Ensure .nojekyll exists
(ROOT / "public" / ".nojekyll").write_text("", encoding="utf-8")
print("ensure_public: done")
