"""assets/logo/ dagi PNG'lardan ko'p o'lchamli exe ikonkasi (.ico) yasaydi.

Ishlatish: python scripts/make_icon.py
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
LOGO_DIR = ROOT / "assets" / "logo"
OUT = ROOT / "assets" / "icon.ico"
SIZES = [16, 32, 48, 64, 128, 256]


def _load(size: int) -> Image.Image:
    """Aniq o'lchamdagi PNG bo'lsa o'shani, bo'lmasa 512'dan kichraytiradi."""
    exact = LOGO_DIR / f"gesturedj-mark-{size}.png"
    src = exact if exact.exists() else LOGO_DIR / "gesturedj-mark-512.png"
    img = Image.open(src).convert("RGBA")
    return img if img.size == (size, size) else img.resize((size, size), Image.LANCZOS)


def main() -> None:
    base = _load(256)
    base.save(OUT, format="ICO", sizes=[(s, s) for s in SIZES])
    print(f"Saqlandi: {OUT} ({', '.join(map(str, SIZES))})")


if __name__ == "__main__":
    main()
