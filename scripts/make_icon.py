"""Vaqtinchalik exe ikonkasi yaratish (logo tayyor bo'lguncha).

Ishlatish: python scripts/make_icon.py [logo.png]
PNG berilsa undan .ico yasaydi, berilmasa oddiy placeholder chizadi.
"""

import sys
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "assets" / "icon.ico"
SIZES = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]


def placeholder() -> Image.Image:
    img = Image.new("RGBA", (256, 256), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((8, 8, 248, 248), radius=56, fill=(67, 56, 202, 255))
    # Audio to'lqin ustunlari (header SVG'dagi kabi)
    bars = [(52, 100, 156), (84, 70, 186), (116, 110, 146), (148, 50, 206), (180, 90, 166), (212, 120, 136)]
    for x, y1, y2 in bars:
        d.line([(x, y1), (x, y2)], fill=(248, 250, 252, 255), width=16)
    return img


def main() -> None:
    OUT.parent.mkdir(exist_ok=True)
    if len(sys.argv) > 1:
        img = Image.open(sys.argv[1]).convert("RGBA").resize((256, 256))
    else:
        img = placeholder()
    img.save(OUT, format="ICO", sizes=SIZES)
    print(f"Saqlandi: {OUT}")


if __name__ == "__main__":
    main()
