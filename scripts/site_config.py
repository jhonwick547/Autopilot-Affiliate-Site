import os
from pathlib import Path

SITE_BASE_URL = os.getenv("SITE_BASE_URL", "https://USERNAME.github.io/REPO").rstrip("/")
parts = SITE_BASE_URL.split("/")
BASE_PATH = "" if len(parts) <= 3 else "/" + parts[3]

AFFILIATE_TAGS = {
    "IN": os.getenv("AFFILIATE_TAG_IN", "yourtag-21"),
    "US": os.getenv("AFFILIATE_TAG_US", "yourtag-20"),
}

AMAZON_DOMAINS = {"IN":"amazon.in", "US":"amazon.com"}

ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
PUBLIC_POSTS = PUBLIC / "posts"
PUBLIC_IMAGES = PUBLIC / "images"
SITEMAPS_DIR = PUBLIC / "sitemaps"
SITE_NAME = os.getenv("SITE_NAME", "AI Affiliate Guides")
