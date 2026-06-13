#!/usr/bin/env python3
"""Download a real product/brand image for a catalog key and update data/product-images.json.

Usage: set-product-image.py "<category|name|brand key>" "<image-url>"

Validates the download is a real raster image, names it by the repo's
convention (slug(category-brand-name)-sha1(key)[:8].jpg), writes it under
assets/products/, and updates the JSON entry (source/src/width/height).
"""
import hashlib
import io
import json
import re
import sys
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "data" / "product-images.json"
ASSETS = ROOT / "assets" / "products"

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def slugify(text: str) -> str:
    text = text.lower().replace("&", " and ")
    text = re.sub(r"[^a-z0-9]+", "-", text)
    return text.strip("-")


def main() -> int:
    key, url = sys.argv[1], sys.argv[2]
    data = json.loads(JSON_PATH.read_text())
    if key not in data:
        print(f"ERROR: key not found: {key!r}", file=sys.stderr)
        return 2
    category, name, brand = key.split("|")

    req = urllib.request.Request(url, headers={"User-Agent": UA, "Referer": url})
    with urllib.request.urlopen(req, timeout=30) as resp:
        ctype = resp.headers.get("Content-Type", "")
        raw = resp.read()
    if not raw or "image" not in ctype.lower():
        print(f"ERROR: not an image (Content-Type={ctype!r}, {len(raw)} bytes)", file=sys.stderr)
        return 3

    img = Image.open(io.BytesIO(raw))
    img.verify()
    img = Image.open(io.BytesIO(raw))
    w, h = img.size
    # Accept product shots (square-ish) and wide brand logos alike.
    if w < 200 or h < 60:
        print(f"ERROR: image too small ({w}x{h})", file=sys.stderr)
        return 4
    if img.mode in ("RGBA", "P", "LA"):
        img = img.convert("RGB")

    h8 = hashlib.sha1(key.encode()).hexdigest()[:8]
    fname = f"{slugify(category + '-' + brand + '-' + name)}-{h8}.jpg"
    out = ASSETS / fname
    img.save(out, "JPEG", quality=88)

    data[key] = {"height": h, "source": url, "src": f"assets/products/{fname}", "width": w}
    JSON_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=True, sort_keys=True) + "\n")
    print(f"OK {fname} {w}x{h} <- {url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
