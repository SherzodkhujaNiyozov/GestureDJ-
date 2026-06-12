"""Sozlamalar/kalibrlash oynasi (pywebview).

Arxitektura: webview.start() asosiy thread'da bloklanib ishlaydi (Windows
talabi), tray esa run_detached() bilan alohida thread'da. Oyna yopilganda
yo'q qilinmaydi - yashirinadi, tray'dan qayta ochiladi. Tray'dan "Chiqish"
bosilganda destroy() chaqiriladi va webview.start() qaytadi.
"""

import logging

import webview

from . import autostart, config
from .app import GestureApp
from .paths import resource_dir

log = logging.getLogger(__name__)

HTML_PATH = resource_dir() / "gesturedj" / "web" / "index.html"

_window: webview.Window | None = None
_quitting = False  # True bo'lsa closing handler yopishga ruxsat beradi


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

    def get_autostart(self) -> bool:
        return autostart.is_enabled()

    def set_autostart(self, enabled: bool) -> bool:
        autostart.set_enabled(bool(enabled))
        return autostart.is_enabled()


def _eval(js: str) -> None:
    if _window is not None:
        try:
            _window.evaluate_js(js)
        except Exception:  # sahifa hali yuklanmagan bo'lishi mumkin
            pass


def _on_closing():
    """X bosilganda oynani yashiramiz, ilova tray'da ishlashda davom etadi.

    Muhim: destroy() ham shu hodisani chaqiradi - chiqayotganda (_quitting)
    yopishni bekor qilmaslik kerak, aks holda ilova hech qachon o'chmaydi.
    """
    if _quitting:
        return True
    if _window is not None:
        _eval("setPolling(false)")  # yashirin oyna CPU yemasin
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
        _eval("setPolling(true)")


def destroy() -> None:
    global _quitting
    _quitting = True
    if _window is not None:
        try:
            _window.events.closing -= _on_closing
        except Exception:
            pass
        _window.destroy()
