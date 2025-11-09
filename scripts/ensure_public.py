# scripts/ensure_public.py
"""
Ensure the public/ directory is valid and non-empty before deployment.

This prevents "404 Page Not Found" on GitHub Pages when no posts were generated.
It creates:
- public/index.html (if missing)
- a fallback placeholder post (if no posts)
- a .nojekyll file to disable Jekyll processing
- a simple 404.html
"""

import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
POSTS = PUBLIC / "posts"

PUBLIC.mkdir(parents=True, exist_ok=True)
POSTS.mkdir(parents=True, exist_ok=True)


def create_placeholder_post():
    """Create a default placeholder post so GitHub Pages never 404s."""
    fallback_post = POSTS / "welcome-placeholder.html"
    if fallback_post.exists():
        return
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>Welcome — Autopilot Affiliate Site</title>
  <style>
    body{{font-family:Inter,system-ui,sans-serif;max-width:900px;margin:28px auto;padding:12px;line-height:1.6}}
    header{{background:#0b6ef6;color:#fff;padding:24px;border-radius:12px}}
    a{{color:#0b6ef6;text-decoration:none}}
  </style>
</head>
<body>
  <header>
    <h1>Welcome to Your Autopilot Affiliate Site</h1>
    <p>This is a placeholder article to prevent 404 errors.</p>
  </header>
  <main>
    <h2>Next Steps</h2>
    <p>Your automation will soon generate real Amazon product reviews and comparisons.</p>
    <p>Check back after the next build or <a href="../index.html">return to the home page</a>.</p>
  </main>
  <footer style="text-align:center;color:#777;margin-top:40px;">
    &copy; {datetime.utcnow().year} Autopilot Affiliate Site
  </footer>
</body>
</html>
"""
    fallback_post.write_text(html, encoding="utf-8")
    print(f"Created placeholder post: {fallback_post}")


def create_index():
    """Create index.html if missing or empty, linking to all posts."""
    posts_links = []
    for post in sorted(POSTS.glob("*.html")):
        name = post.stem.replace("-", " ").title()
        posts_links.append(f"<li><a href='posts/{post.name}'>{name}</a></li>")

    if not posts_links:
        posts_links = ["<li>No posts available yet — please check back later.</li>"]

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"/>
  <meta name="viewport" content="width=device-width,initial-scale=1"/>
  <title>{os.getenv("SITE_NAME","Affiliate Site")}</title>
  <style>
    body{{font-family:Inter,system-ui,sans-serif;max-width:900px;margin:28px auto;padding:12px;line-height:1.6}}
    header{{text-align:center;background:#0b6ef6;color:#fff;padding:24px;border-radius:12px}}
    a{{color:#0b6ef6;text-decoration:none}}
  </style>
</head>
<body>
  <header>
    <h1>{os.getenv("SITE_NAME","Affiliate Site")}</h1>
    <p>Latest Amazon Product Reviews and Buying Guides</p>
  </header>
  <main>
    <ul>
      {''.join(posts_links)}
    </ul>
  </main>
  <footer style="text-align:center;color:#777;margin-top:40px;">
    &copy; {datetime.utcnow().year} {os.getenv("SITE_NAME","Affiliate Site")}
  </footer>
</body>
</html>
"""
    (PUBLIC / "index.html").write_text(html, encoding="utf-8")
    print("Created fallback index.html")


def create_nojekyll_and_404():
    """Prevent Jekyll filtering and ensure a valid 404 page."""
    (PUBLIC / ".nojekyll").write_text("", encoding="utf-8")
    (PUBLIC / "404.html").write_text(
        "<!doctype html><h1>404 — Page Not Found</h1><p>The content may not exist yet. Please go back to the <a href='./index.html'>home page</a>.</p>",
        encoding="utf-8",
    )


def main():
    if not any(POSTS.glob("*.html")):
        create_placeholder_post()
    create_index()
    create_nojekyll_and_404()
    print("✅ ensure_public completed — public/ is ready for deployment")


if __name__ == "__main__":
    main()
