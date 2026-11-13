#!/usr/bin/env python3
"""Builds the flash gallery: resizes originals into web-sized webp files in
flash/images/ and fills the FLASH block of flash/index.html, newest first.

Requires macOS `sips` and `cwebp` (brew install webp).
"""
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "images" / "flash (2019-2026) organize by new at top old later."
PAGE = ROOT / "flash" / "index.html"
OUT_IMAGES = ROOT / "flash" / "images"
MAX_EDGE = 1000
QUALITY = 80
EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp"}


def sort_key(name):
    """Higher sorts first (newer). Dates are inferred from file names."""
    lower = name.lower()
    numbers = re.findall(r"\d+", Path(lower).stem)
    num = int(numbers[-1]) if numbers else 0
    if lower.startswith("flash2023-"):
        rank = 70
    elif lower.startswith("flash-2023-"):
        rank = 60
    elif lower.startswith("flashsheetmarch23"):
        rank = 55
    elif lower.startswith("flash-2022-dec"):
        rank = 50
    elif lower.startswith("flash2022-"):
        rank = 40
    elif lower.startswith("flash-"):
        rank = 30
        num = 0
    elif lower.startswith("flash2020"):
        rank = 20
    else:
        rank = 10
    return (rank, num, lower)


def convert(src, dest):
    with tempfile.TemporaryDirectory() as tmp:
        resized = Path(tmp) / "resized.png"
        subprocess.run(
            ["sips", "-Z", str(MAX_EDGE), "-s", "format", "png", str(src), "--out", str(resized)],
            check=True, capture_output=True,
        )
        subprocess.run(
            ["cwebp", "-quiet", "-q", str(QUALITY), str(resized), "-o", str(dest)],
            check=True,
        )


def main():
    files = {}
    for path in SRC.iterdir():
        if path.suffix.lower() in EXTENSIONS:
            files.setdefault(path.stem.lower(), path)
    ordered = sorted(files.values(), key=lambda p: sort_key(p.name), reverse=True)

    OUT_IMAGES.mkdir(parents=True, exist_ok=True)
    items = []
    for index, path in enumerate(ordered, start=1):
        dest = OUT_IMAGES / f"flash-{index:03d}.webp"
        if not dest.exists():
            convert(path, dest)
        items.append(
            f'                <img src="images/{dest.name}" alt="Flash design {index}" loading="lazy" decoding="async">'
        )

    html = PAGE.read_text(encoding="utf-8")
    block = "<!-- FLASH:START -->\n" + "\n".join(items) + "\n                <!-- FLASH:END -->"
    html = re.sub(r"<!-- FLASH:START -->.*?<!-- FLASH:END -->", lambda _: block, html, flags=re.S)
    PAGE.write_text(html, encoding="utf-8")
    print(f"Wrote {len(items)} flash images")


if __name__ == "__main__":
    main()
