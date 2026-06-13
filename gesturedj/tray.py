"""Tizim tray ikonkasi (pystray) — GestureDJ brend logosi bilan."""

import logging

from PIL import Image

from .app import ACTIVE, GestureApp
from .paths import resource_dir

log = logging.getLogger(__name__)

_LOGO_DIR = resource_dir() / "assets" / "logo"


def _load_logo() -> Image.Image:
    img = Image.open(_LOGO_DIR / "gesturedj-mark-64.png").convert("RGBA")
    return img.resize((64, 64), Image.LANCZOS) if img.size != (64, 64) else img


def _icon_for(active: bool, base: Image.Image) -> Image.Image:
    """Faol = to'liq logo; kutish = biroz xira (holatni tray'da bilish uchun)."""
    if active:
        return base
    faded = base.copy()
    alpha = faded.getchannel("A").point(lambda a: int(a * 0.55))
    faded.putalpha(alpha)
    return faded


def create_icon(app: GestureApp, on_settings, on_quit) -> "pystray.Icon":
    import pystray

    base = _load_logo()
    active_icon = _icon_for(True, base)
    standby_icon = _icon_for(False, base)

    def toggle_preview(icon, item):
        app.show_preview = not app.show_preview

    icon = pystray.Icon(
        "GestureDJ",
        icon=standby_icon,
        title="GestureDJ - kutish rejimi",
        menu=pystray.Menu(
            pystray.MenuItem("Sozlamalar", lambda icon, item: on_settings(), default=True),
            pystray.MenuItem(
                "Preview ko'rsatish",
                toggle_preview,
                checked=lambda item: app.show_preview,
            ),
            pystray.MenuItem("Chiqish", lambda icon, item: on_quit()),
        ),
    )

    def on_state_change(state: str) -> None:
        active = state == ACTIVE
        icon.icon = active_icon if active else standby_icon
        icon.title = "GestureDJ - FAOL" if active else "GestureDJ - kutish rejimi"

    app.on_state_change = on_state_change
    return icon
