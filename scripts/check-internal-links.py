#!/usr/bin/env python3
"""Check local links and asset references in the static site."""

from __future__ import annotations

import json
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlparse


ROOT = Path(__file__).resolve().parents[1]
HTML_FILES = sorted(ROOT.glob("*.html"))
SKIP_SCHEMES = {"http", "https", "mailto", "tel", "javascript", "data"}


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.references: list[tuple[str, str, int]] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {name.lower(): value for name, value in attrs if value}

        element_id = attributes.get("id")
        if element_id:
            self.ids.add(element_id)

        for attribute in ("href", "src"):
            value = attributes.get(attribute)
            if value:
                self.references.append((attribute, value, self.getpos()[0]))

        if tag == "meta" and attributes.get("property") in {"og:image", "twitter:image"}:
            value = attributes.get("content")
            if value:
                self.references.append(("content", value, self.getpos()[0]))


def is_external(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme in SKIP_SCHEMES or value.startswith("//")


def normalize_target(source: Path, value: str) -> tuple[Path, str | None]:
    parsed = urlparse(value)
    path_text = unquote(parsed.path)
    fragment = unquote(parsed.fragment) if parsed.fragment else None

    if not path_text:
        return source, fragment

    if path_text in {".", "./"}:
        return ROOT / "index.html", fragment

    if path_text.startswith("/"):
        path_text = path_text.lstrip("/")
        if not path_text:
            return ROOT / "index.html", fragment
        if path_text.endswith("/"):
            return (ROOT / path_text / "index.html").resolve(), fragment
        return (ROOT / path_text).resolve(), fragment

    if path_text.endswith("/"):
        return (ROOT / path_text / "index.html").resolve(), fragment

    return (source.parent / path_text).resolve(), fragment


def display_path(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def collect_html() -> tuple[dict[Path, LinkParser], list[str]]:
    parsers: dict[Path, LinkParser] = {}
    errors: list[str] = []

    for html_file in HTML_FILES:
        parser = LinkParser()
        try:
            parser.feed(html_file.read_text(encoding="utf-8"))
        except Exception as exc:  # pragma: no cover - defensive CLI reporting
            errors.append(f"{display_path(html_file)}: could not parse HTML: {exc}")
            continue
        parsers[html_file.resolve()] = parser

    return parsers, errors


def check_html_references(parsers: dict[Path, LinkParser]) -> list[str]:
    errors: list[str] = []

    for source, parser in parsers.items():
        for attribute, value, line in parser.references:
            if is_external(value):
                continue

            target, fragment = normalize_target(source, value)
            if not target.exists():
                errors.append(
                    f"{display_path(source)}:{line}: {attribute} target missing: {value}"
                )
                continue

            if fragment:
                target_parser = parsers.get(target.resolve())
                if target_parser and fragment not in target_parser.ids:
                    errors.append(
                        f"{display_path(source)}:{line}: anchor missing: {value}"
                    )

    return errors


def check_product_images() -> list[str]:
    errors: list[str] = []
    image_map_path = ROOT / "data" / "product-images.json"
    if not image_map_path.exists():
        return errors

    try:
        product_images = json.loads(image_map_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"{display_path(image_map_path)}: invalid JSON: {exc}"]

    for product_key, image in sorted(product_images.items()):
        src = image.get("src") if isinstance(image, dict) else None
        if not src:
            errors.append(f"{display_path(image_map_path)}: {product_key}: missing src")
            continue

        if is_external(src):
            continue

        target = (ROOT / src).resolve()
        if not target.exists():
            errors.append(
                f"{display_path(image_map_path)}: {product_key}: image missing: {src}"
            )

    return errors


def main() -> int:
    parsers, errors = collect_html()
    errors.extend(check_html_references(parsers))
    errors.extend(check_product_images())

    if errors:
        print("Internal link check failed:\n")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Internal link check passed for {len(parsers)} HTML files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
