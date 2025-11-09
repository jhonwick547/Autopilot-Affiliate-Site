import os, base64, logging
from pathlib import Path
import openai
from backoff import on_exception, expo

log = logging.getLogger("images")
log.setLevel(logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    log.warning("OPENAI_API_KEY missing — no image generation.")

PUBLIC_IMAGES = Path("public/images")
PUBLIC_IMAGES.mkdir(parents=True, exist_ok=True)

@on_exception(expo, Exception, max_tries=3)
def openai_generate_image(query: str, size="1024x512") -> str | None:
    if not OPENAI_API_KEY:
        return None
    prompt = (f"Professional hero photo for: {query}. Clean light background, centered product, e-commerce style, high detail, no watermark.")
    resp = openai.Image.create(prompt=prompt, n=1, size=size, response_format="b64_json")
    data = resp["data"][0]
    b64 = data["b64_json"]
    img_bytes = base64.b64decode(b64)
    safe = "".join(ch for ch in query if ch.isalnum() or ch in (" ", "-")).strip().replace(" ", "-")[:80]
    out = PUBLIC_IMAGES / f"{safe}.jpg"
    out.write_bytes(img_bytes)
    log.info("Saved image %s", out)
    return f"/images/{safe}.jpg"

def download_image(query: str) -> str | None:
    try:
        return openai_generate_image(query)
    except Exception as e:
        log.warning("OpenAI image generation failed: %s", e)
        return None
