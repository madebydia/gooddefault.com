#!/usr/bin/env python3
"""Local ingest server: the browser POSTs base64 image bytes for a catalog key,
this validates + saves the file and updates data/product-images.json.

Used only for brand CDNs that block non-browser HTTP clients with a bot
challenge. Run: python3 scripts/image-ingest-server.py 8787
POST text/plain base64 body to  http://localhost:8787/save?key=<urlencoded key>&source=<urlencoded url>
"""
import base64
import hashlib
import io
import json
import re
import sys
import urllib.parse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "data" / "product-images.json"
ASSETS = ROOT / "assets" / "products"


def slugify(text: str) -> str:
    text = text.lower().replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", "-", text).strip("-")


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "*")
        self.send_header("Access-Control-Allow-Private-Network", "true")

    def do_OPTIONS(self):  # noqa: N802
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):  # noqa: N802
        q = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        key = q.get("key", [""])[0]
        source = q.get("source", [""])[0]
        n = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(n)
        try:
            raw = base64.b64decode(body)
            data = json.loads(JSON_PATH.read_text())
            if key not in data:
                raise ValueError(f"key not found: {key!r}")
            category, name, brand = key.split("|")
            img = Image.open(io.BytesIO(raw))
            img.verify()
            img = Image.open(io.BytesIO(raw))
            w, h = img.size
            if w < 200 or h < 200:
                raise ValueError(f"too small {w}x{h}")
            if img.mode in ("RGBA", "P", "LA"):
                img = img.convert("RGB")
            h8 = hashlib.sha1(key.encode()).hexdigest()[:8]
            fname = f"{slugify(category + '-' + brand + '-' + name)}-{h8}.jpg"
            img.save(ASSETS / fname, "JPEG", quality=88)
            data[key] = {"height": h, "source": source or "browser-fetch",
                         "src": f"assets/products/{fname}", "width": w}
            JSON_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=True, sort_keys=True) + "\n")
            msg = f"OK {fname} {w}x{h}"
            print(msg, flush=True)
            self.send_response(200)
        except Exception as e:  # noqa: BLE001
            msg = f"ERR {type(e).__name__}: {e}"
            print(msg, flush=True)
            self.send_response(400)
        self._cors()
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(msg.encode())

    def log_message(self, *a):  # silence default logging
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8787
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
