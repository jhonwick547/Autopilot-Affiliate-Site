# scripts/site_config.py
import os
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
PUBLIC_POSTS = PUBLIC / "posts"
TEMPLATES = ROOT / "templates"
SITE_BASE_URL = os.getenv("SITE_BASE_URL", "https://USERNAME.github.io/REPO").rstrip("/")
SITE_NAME = os.getenv("SITE_NAME", "Affiliate Site")
