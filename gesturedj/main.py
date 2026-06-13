"""GestureDJ kirish nuqtasi.

Ishga tushirish:  python -m gesturedj.main   yoki   python run.py

Thread tuzilmasi:
  - asosiy thread: pywebview (sozlamalar oynasi, yashirin holda kutadi)
  - tray thread:   pystray (run_detached)
  - ishchi thread: kamera + MediaPipe + audio
"""

import logging
import logging.handlers
import os
import sys
import threading

from . import ui
from .app import GestureApp
from .paths import app_dir
from .tray import create_icon

LOG_DIR = app_dir() / "logs"


def _setup_logging() -> None:
    LOG_DIR.mkdir(exist_ok=True)
    handlers: list[logging.Handler] = [
        logging.handlers.RotatingFileHandler(
            LOG_DIR / "gesturedj.log", maxBytes=500_000, backupCount=2, encoding="utf-8"
        )
    ]
    # --noconsole exe'da sys.stderr = None bo'ladi; StreamHandler faqat
    # konsol mavjud bo'lganda qo'shiladi (aks holda emit xato beradi)
    if sys.stderr is not None:
        handlers.append(logging.StreamHandler())
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=handlers,
    )


def _hard_exit(code: int = 0) -> None:
    """Jarayonni kafolatli tugatadi. WebView2/pystray osilib qolsa ham ishlaydi."""
    try:
        logging.shutdown()
    except Exception:
        pass
    os._exit(code)


def main() -> None:
    no_ui = "--no-ui" in sys.argv  # diagnostika: sozlamalar oynasisiz (A/B test)

    _setup_logging()
    log = logging.getLogger(__name__)
    log.info("GestureDJ ishga tushmoqda%s", " (UI'siz rejim)" if no_ui else "")

    app = GestureApp()
    worker = threading.Thread(target=app.run, daemon=True)
    worker.start()

    def quit_app():
        """Tray 'Chiqish' (yoki oyna ichidan chiqish). Kafolatli tugatadi.

        Toza teardown (ui.destroy -> webview.start qaytishi) exe'da ba'zan
        WebView2 bilan osilib qoladi, shuning uchun watchdog qo'yamiz: 1.5s
        ichida toza chiqmasa, jarayonni majburan o'ldiramiz.
        """
        log.info("Chiqish so'raldi")
        app.stop_event.set()
        threading.Timer(1.5, _hard_exit).start()  # osilib qolsa - majburan
        try:
            icon.stop()
        except Exception:
            pass
        if not no_ui:
            try:
                ui.destroy()  # webview siklini tugatadi -> main davom etadi
            except Exception:
                _hard_exit()

    def on_settings():
        if no_ui:
            log.info("UI'siz rejimda sozlamalar oynasi yo'q")
        else:
            ui.show()

    icon = create_icon(app, on_settings=on_settings, on_quit=quit_app)

    try:
        if no_ui:
            icon.run()  # asosiy thread'da bloklanadi, webview yaratilmaydi
        else:
            icon.run_detached()
            ui.run(app, on_quit=quit_app)  # bloklanadi; quit_app/destroy qaytaradi
    except KeyboardInterrupt:
        log.info("Ctrl+C qabul qilindi")
        app.stop_event.set()

    worker.join(timeout=2)
    log.info("GestureDJ to'xtadi")
    _hard_exit(0)


if __name__ == "__main__":
    main()
