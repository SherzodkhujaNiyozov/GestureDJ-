"""Fayl yo'llari: oddiy (dev) va PyInstaller exe rejimlarini birlashtiradi.

Exe rejimida:
  - resource_dir() -> _internal papka (faqat o'qish: web/, bundled model)
  - app_dir()      -> exe yonidagi papka (yozish: config.json, logs/, models/)
Dev rejimida ikkalasi ham loyiha ildizi.
"""

import sys
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent


def is_frozen() -> bool:
    return getattr(sys, "frozen", False)


def app_dir() -> Path:
    """Yoziladigan fayllar uchun (config.json, logs/, yuklab olingan model)."""
    if is_frozen():
        return Path(sys.executable).resolve().parent
    return _PROJECT_ROOT


def resource_dir() -> Path:
    """Bundle qilingan resurslar uchun (web/, model)."""
    if is_frozen():
        return Path(sys._MEIPASS)
    return _PROJECT_ROOT
