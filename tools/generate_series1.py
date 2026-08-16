#!/usr/bin/env python3
import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "series1.json"
HTML_PATH = ROOT / "series1.html"
START_MARKER = "<!-- SERIES1:START -->"
END_MARKER = "<!-- SERIES1:END -->"


def load_artworks():
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return json.load(f)


def render_artwork(art):
    image = html.escape(str(art.get("image", "")), quote=True)
    alt = html.escape(str(art.get("alt", "")), quote=True)
    title = html.escape(str(art.get("title", "")))
    date = html.escape(str(art.get("date", "")))
    medium = html.escape(str(art.get("medium", "")))
    size = html.escape(str(art.get("size", "")))

    return (
        "            <article class=\"post\">\n"
        f"                <img src=\"{image}\" alt=\"{alt}\">\n"
        "                <div class=\"post-meta\">\n"
        f"                    <strong>{title}</strong> {date}<br>\n"
        f"                    {medium}. {size}<br>\n"
        "                </div>\n"
        "            </article>"
    )


def generate_block(artworks):
    rows = [render_artwork(art) for art in artworks]
    return "\n\n".join(rows)


def update_series1_html(new_block):
    content = HTML_PATH.read_text(encoding="utf-8")
    start = content.find(START_MARKER)
    end = content.find(END_MARKER)

    if start == -1 or end == -1 or end < start:
        raise RuntimeError(
            "Could not find valid SERIES1 markers in series1.html. "
            "Add <!-- SERIES1:START --> and <!-- SERIES1:END -->."
        )

    start_insert = start + len(START_MARKER)
    replacement = "\n" + new_block + "\n            "
    updated = content[:start_insert] + replacement + content[end:]
    HTML_PATH.write_text(updated, encoding="utf-8")


def main():
    artworks = load_artworks()
    new_block = generate_block(artworks)
    update_series1_html(new_block)
    print(f"Updated series1.html with {len(artworks)} artworks.")


if __name__ == "__main__":
    main()
