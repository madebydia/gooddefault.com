#!/usr/bin/env python3
"""Fetch real product images for catalog rows that still use placeholders.

Reads a worklist (``data/image-sources.json``) mapping a catalog key to a
source URL (either a direct image or a product/landing page to pull the
``og:image`` from), downloads and validates each image, saves it under
``assets/products/`` using the same slug-and-hash naming as existing rows,
and rewrites ``data/product-images.json`` with the local ``src`` plus the
real pixel ``width``/``height`` and the originating ``source`` URL.

Run from anywhere:

    python3 scripts/fetch-product-images.py            # process every worklist entry
    python3 scripts/fetch-product-images.py KEY ...     # only the given catalog keys

The worklist value may be a bare URL string or an object::

    { "source": "https://...", "image": "https://...optional explicit image..." }

``image`` (when present) is downloaded directly; otherwise the page at
``source`` is fetched and its og:image / twitter:image is used.
"""

from __future__ import annotations

import hashlib
import io
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
IMAGES_JSON = ROOT / "data" / "product-images.json"
WORKLIST_JSON = ROOT / "data" / "image-sources.json"
PRODUCTS_DIR = ROOT / "assets" / "products"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)
HEADERS = {
    "User-Agent": UA,
    "Accept": "text/html,application/xhtml+xml,image/avif,image/webp,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}
MIN_PIXELS = 320  # reject tiny sprites / 1x1 trackers on the short edge


def normalize_key(value: str) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).lower()


def slugify(value: str) -> str:
    value = normalize_key(value).replace("&", " and ")
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def local_name(key: str, source: str) -> str:
    """Match existing convention: <category>-<brand>-<name> slug + 8 hex chars."""
    category, name, brand = key.split("|")
    slug = slugify(f"{category} {brand} {name}")[:80].rstrip("-")
    digest = hashlib.sha1(source.encode("utf-8")).hexdigest()[:8]
    return f"{slug}-{digest}.jpg"


class OgImageParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.og: str | None = None
        self.twitter: str | None = None
        self.first_img: str | None = None

    def handle_starttag(self, tag: str, attrs):  # type: ignore[override]
        a = {k.lower(): v for k, v in attrs if v}
        if tag == "meta":
            prop = a.get("property") or a.get("name")
            content = a.get("content")
            if content and prop == "og:image" and not self.og:
                self.og = content
            elif content and prop in {"twitter:image", "twitter:image:src"} and not self.twitter:
                self.twitter = content
        elif tag == "img" and not self.first_img:
            src = a.get("src") or a.get("data-src")
            if src and not src.startswith("data:"):
                self.first_img = src


def fetch(url: str, *, binary: bool) -> tuple[bytes, str]:
    req = Request(url, headers=HEADERS)
    with urlopen(req, timeout=45) as resp:
        return resp.read(), resp.headers.get("Content-Type", "")


def resolve_image_url(entry) -> tuple[str, str]:
    """Return (image_url, provenance_url)."""
    if isinstance(entry, str):
        source = entry
        explicit = None
    else:
        source = entry["source"]
        explicit = entry.get("image")

    if explicit:
        return explicit, source

    lower = source.split("?")[0].lower()
    if lower.endswith((".jpg", ".jpeg", ".png", ".webp", ".avif", ".gif")):
        return source, source

    html, ctype = fetch(source, binary=False)
    if "image/" in ctype:  # the "page" was actually an image
        return source, source

    parser = OgImageParser()
    parser.feed(html.decode("utf-8", "replace"))
    candidate = parser.og or parser.twitter or parser.first_img
    if not candidate:
        raise RuntimeError(f"no og:image/img found on page: {source}")
    return urljoin(source, candidate), source


def process(key: str, entry, images: dict) -> str:
    image_url, provenance = resolve_image_url(entry)
    data, ctype = fetch(image_url, binary=True)
    if "image/" not in ctype and not data[:4] in (b"\xff\xd8\xff\xe0", b"\x89PNG"):
        # Pillow will be the real arbiter; just continue.
        pass

    img = Image.open(io.BytesIO(data))
    img.load()
    width, height = img.size
    if min(width, height) < MIN_PIXELS:
        raise RuntimeError(f"image too small ({width}x{height}): {image_url}")

    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")
    elif img.mode == "L":
        img = img.convert("RGB")

    name = local_name(key, provenance)
    out = PRODUCTS_DIR / name
    img.save(out, "JPEG", quality=88, optimize=True)

    images[key] = {
        "height": height,
        "source": provenance,
        "src": f"assets/products/{name}",
        "width": width,
    }
    return f"{width}x{height} -> assets/products/{name}"


def main(argv: list[str]) -> int:
    images = json.loads(IMAGES_JSON.read_text("utf-8"))
    worklist = json.loads(WORKLIST_JSON.read_text("utf-8"))

    keys = argv or list(worklist.keys())
    ok, fail = 0, 0
    for key in keys:
        if key not in worklist:
            print(f"SKIP  {key}: not in worklist")
            continue
        try:
            result = process(key, worklist[key], images)
            print(f"OK    {key}: {result}")
            ok += 1
        except Exception as exc:  # noqa: BLE001 - report and keep going
            print(f"FAIL  {key}: {exc}")
            fail += 1

    IMAGES_JSON.write_text(
        json.dumps(images, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"\nDone. {ok} ok, {fail} failed. Wrote {IMAGES_JSON.relative_to(ROOT)}")
    return 1 if fail else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
