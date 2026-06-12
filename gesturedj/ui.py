"""Sozlamalar/kalibrlash oynasi (pywebview).

Arxitektura: webview.start() asosiy thread'da bloklanib ishlaydi (Windows
talabi), tray esa run_detached() bilan alohida thread'da. Oyna yopilganda
yo'q qilinmaydi - yashirinadi, tray'dan qayta ochiladi. Tray'dan "Chiqish"
bosilganda destroy() chaqiriladi va webview.start() qaytadi.
"""

import logging
from pathlib import Path

import webview

from . import config
from .app import GestureApp

log = logging.getLogger(__name__)

HTML_PATH = Path(__file__).resolve().parent / "web" / "index.html"

_window: webview.Window | None = None


class Api:
    """JS tomonidan chaqiriladigan ko'prik (pywebview.api.*)."""

    def __init__(self, app: GestureApp):
        self._app = app

    def get_state(self) -> dict:
        return dict(self._app.metrics)

    def get_config(self) -> dict:
        return config.current()

    def set_config(self, values: dict) -> dict:
        config.update(values)
        config.save()
        return config.current()

    def reset_config(self) -> dict:
        config.reset()
        return config.current()


def _on_closing():
    """X bosilganda oynani yashiramiz, ilova tray'da ishlashda davom etadi."""
    if _window is not None:
        _window.hide()
    return False  # yopishni bekor qilish


def run(app: GestureApp) -> None:
    """Asosiy thread'da bloklanib ishlaydi; destroy() chaqirilganda qaytadi."""
    global _window
    _window = webview.create_window(
        "GestureDJ — Sozlamalar",
        url=str(HTML_PATH),
        js_api=Api(app),
        width=960,
        height=720,
        min_size=(720, 560),
        hidden=True,
        background_color="#0F0F23",
    )
    _window.events.closing += _on_closing
    webview.start()
    log.info("UI sikli tugadi")


def show() -> None:
    if _window is not None:
        _window.show()
        _window.restore()


def destroy() -> None:
    if _window is not None:
        _window.destroy()
