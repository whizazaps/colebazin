#!/usr/bin/env python3
import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def load_artworks(series_key):
    data_path = ROOT / "data" / f"series{series_key}.json"
    with data_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def render_artwork(art):
    image = html.escape(str(art.get("image", "")), quote=True)
    alt = html.escape(str(art.get("alt", "")), quote=True)
    title = html.escape(str(art.get("title", "")))
    date = html.escape(str(art.get("date", "")))
    medium = html.escape(str(art.get("medium", "")))
    size = html.escape(str(art.get("size", "")))

    details = ", ".join(part for part in (medium, size) if part)

    return (
        "            <article class=\"post\">\n"
        f"                <img src=\"{image}\" alt=\"{alt}\">\n"
        "                <div class=\"post-meta\">\n"
        f"                    <strong>{title}</strong> {date}<br>\n"
        f"                    {details}<br>\n"
        "                </div>\n"
        "            </article>"
    )


def generate_block(artworks):
    rows = [render_artwork(art) for art in artworks if not art.get("hidden")]
    return "\n\n".join(rows)


def update_series_html(series_key, new_block):
    html_path = ROOT / f"series{series_key}.html"
    start_marker = f"<!-- SERIES{str(series_key).upper()}:START -->"
    end_marker = f"<!-- SERIES{str(series_key).upper()}:END -->"
    content = html_path.read_text(encoding="utf-8")
    start = content.find(start_marker)
    end = content.find(end_marker)

    if start == -1 or end == -1 or end < start:
        raise RuntimeError(
            f"Could not find valid SERIES{str(series_key).upper()} markers in series{series_key}.html. "
            f"Add {start_marker} and {end_marker}."
        )

    start_insert = start + len(start_marker)
    replacement = "\n" + new_block + "\n            "
    updated = content[:start_insert] + replacement + content[end:]
    html_path.write_text(updated, encoding="utf-8")
    return html_path


def main():
    series_key = sys.argv[1] if len(sys.argv) > 1 else "1"
    artworks = load_artworks(series_key)
    new_block = generate_block(artworks)
    html_path = update_series_html(series_key, new_block)
    print(f"Updated {html_path.name} with {len(artworks)} artworks.")


if __name__ == "__main__":
    main()
