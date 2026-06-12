"""Tizim tray ikonkasi (pystray)."""

import pystray
from PIL import Image, ImageDraw

from .app import ACTIVE, GestureApp


def _make_icon(active: bool) -> Image.Image:
    """Oddiy dumaloq ikonka: yashil = faol, kulrang = kutish."""
    img = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    color = (46, 204, 113, 255) if active else (130, 130, 130, 255)
    d.ellipse((4, 4, 60, 60), fill=color)
    d.text((18, 18), "DJ", fill=(255, 255, 255, 255))
    return img


def run_tray(app: GestureApp) -> None:
    """Asosiy thread'da bloklanib ishlaydi."""

    def toggle_preview(icon, item):
        app.show_preview = not app.show_preview

    def quit_app(icon, item):
        app.stop_event.set()
        icon.stop()

    icon = pystray.Icon(
        "GestureDJ",
        icon=_make_icon(False),
        title="GestureDJ - kutish rejimi",
        menu=pystray.Menu(
            pystray.MenuItem(
                "Preview ko'rsatish",
                toggle_preview,
                checked=lambda item: app.show_preview,
            ),
            pystray.MenuItem("Chiqish", quit_app),
        ),
    )

    def on_state_change(state: str) -> None:
        active = state == ACTIVE
        icon.icon = _make_icon(active)
        icon.title = "GestureDJ - FAOL" if active else "GestureDJ - kutish rejimi"

    app.on_state_change = on_state_change
    icon.run()
