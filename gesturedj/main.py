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
    file_handler = logging.handlers.RotatingFileHandler(
        LOG_DIR / "gesturedj.log", maxBytes=500_000, backupCount=2, encoding="utf-8"
    )
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[file_handler, logging.StreamHandler()],
    )


def main() -> None:
    no_ui = "--no-ui" in sys.argv  # diagnostika: sozlamalar oynasisiz (A/B test)

    _setup_logging()
    log = logging.getLogger(__name__)
    log.info("GestureDJ ishga tushmoqda%s", " (UI'siz rejim)" if no_ui else "")

    app = GestureApp()
    worker = threading.Thread(target=app.run, daemon=True)
    worker.start()

    def quit_app():
        app.stop_event.set()
        if not no_ui:
            ui.destroy()  # webview siklini tugatadi -> main davom etadi

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
            ui.run(app)  # bloklanadi; quit_app yoki oyna destroy bo'lganda qaytadi
            icon.stop()
    except KeyboardInterrupt:
        log.info("Ctrl+C qabul qilindi")

    app.stop_event.set()
    worker.join(timeout=3)
    log.info("GestureDJ to'xtadi")
    # WebView2/pystray ortda non-daemon thread qoldirishi mumkin -
    # toza log'dan keyin jarayonni kafolatli tugatamiz
    logging.shutdown()
    os._exit(0)


if __name__ == "__main__":
    main()
