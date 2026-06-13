#!/usr/bin/env python3
"""Fetch brand product pages and report the best candidate image URL for each.

Reads (key TAB page_url) lines from a file given as argv[1].
Prints: STATUS<TAB>key<TAB>candidate_url  for review.
Does NOT modify anything — discovery only.
"""
import re
import sys
import urllib.request

UA = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
)


def best_image(html: str, base: str) -> str:
    for pat in (
        r'property=["\']og:image(?::secure_url)?["\']\s+content=["\']([^"\']+)["\']',
        r'content=["\']([^"\']+)["\']\s+property=["\']og:image["\']',
        r'name=["\']twitter:image["\']\s+content=["\']([^"\']+)["\']',
    ):
        m = re.search(pat, html, re.I)
        if m:
            return m.group(1)
    # fallback: first plausible product CDN image
    for m in re.finditer(r'(https?:)?//[^"\'\s]+?\.(?:jpg|jpeg|png|webp)', html, re.I):
        u = m.group(0)
        if any(b in u.lower() for b in ("favicon", "logo", "sprite", "icon", "placeholder")):
            continue
        if u.startswith("//"):
            u = "https:" + u
        return u
    return ""


def main() -> int:
    for line in open(sys.argv[1]):
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            continue
        key, url = line.split("\t")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=25) as resp:
                html = resp.read().decode("utf-8", "ignore")
            img = best_image(html, url)
            print(f"{'OK ' if img else 'NONE'}\t{key}\t{img}")
        except Exception as e:  # noqa: BLE001
            print(f"ERR({type(e).__name__}:{getattr(e,'code','')})\t{key}\t{url}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
