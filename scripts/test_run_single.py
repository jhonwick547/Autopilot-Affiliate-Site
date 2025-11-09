# robust test runner (module-safe)
from pathlib import Path
import sys, os, traceback
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from scripts.trending_aggregator import aggregate_trends
from scripts.generate_posts import generate
from scripts.images import download_image
from scripts.render import render_post, render_index, write_basics
from scripts.utils import today_iso

def main():
    MARKETS = os.getenv("MARKETS","IN,US").split(",")
    PER_MARKET = int(os.getenv("TEST_PER_MARKET","2"))
    print("→ MARKETS:", MARKETS, "PER_MARKET:", PER_MARKET)

    topics = aggregate_trends(markets=tuple(MARKETS), per_source=PER_MARKET)
    print("Collected topics:", topics)
    if not topics:
        raise SystemExit("No trending topics found")

    topic = topics[0]
    print("Selected topic:", topic)

    print("Generating article…")
    meta = generate(topic)
    print("Metadata:", meta)

    print("Generating hero image…")
    hero = None
    try:
        hero = download_image(topic)
        print("Hero image:", hero)
    except Exception:
        traceback.print_exc()

    out = render_post(Path(meta["raw_path"]), title=meta["keyword"].title(), market="IN", hero_url=hero)
    write_basics()
    render_index([{"title": meta["keyword"].title(), "filename": Path(out).name, "date": today_iso()}])
    print("Done. Post written to:", out)
    print(Path(out).read_text(encoding="utf-8")[:1200])

if __name__ == "__main__":
    main()
