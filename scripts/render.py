# scripts/render.py
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape
from datetime import datetime
from .site_config import PUBLIC, PUBLIC_POSTS, TEMPLATES, SITE_BASE_URL, SITE_NAME
from .affiliate import inject_affiliate_links

env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=select_autoescape(["html"]))
post_tpl = env.get_template("post_template.html")
index_tpl = env.get_template("index_template.html")

def render_post(raw_html_path: Path, title: str, market: str, hero_url: str | None) -> str:
    raw_html = Path(raw_html_path).read_text(encoding="utf-8")
    html = inject_affiliate_links(raw_html, market)
    canonical = f"{SITE_BASE_URL}/posts/{raw_html_path.stem}.html"
    out_html = post_tpl.render(
        title=title,
        content=html,
        meta_description=title,
        canonical_url=canonical,
        site_name=SITE_NAME,
        year=datetime.utcnow().year,
        hero_url=hero_url,
    )
    PUBLIC_POSTS.mkdir(parents=True, exist_ok=True)
    out_path = PUBLIC_POSTS / f"{raw_html_path.stem}.html"
    out_path.write_text(out_html, encoding="utf-8")
    return str(out_path)

def render_index(posts_info: list):
    PUBLIC.mkdir(parents=True, exist_ok=True)
    html = index_tpl.render(site_name=SITE_NAME, posts=posts_info)
    (PUBLIC / "index.html").write_text(html, encoding="utf-8")

def write_basics():
    PUBLIC.mkdir(parents=True, exist_ok=True)
    (PUBLIC / ".nojekyll").write_text("", encoding="utf-8")
    (PUBLIC / "404.html").write_text("<h1>Page not found</h1>", encoding="utf-8")
