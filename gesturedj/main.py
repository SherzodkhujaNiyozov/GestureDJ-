"""GestureDJ kirish nuqtasi.

Ishga tushirish:  python -m gesturedj.main   yoki   python run.py

Thread tuzilmasi:
  - asosiy thread: pywebview (sozlamalar oynasi, yashirin holda kutadi)
  - tray thread:   pystray (run_detached)
  - ishchi thread: kamera + MediaPipe + audio
"""

import logging
import logging.handlers
import threading
from pathlib import Path

from . import ui
from .app import GestureApp
from .tray import create_icon

LOG_DIR = Path(__file__).resolve().parent.parent / "logs"


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
    _setup_logging()
    log = logging.getLogger(__name__)
    log.info("GestureDJ ishga tushmoqda")

    app = GestureApp()
    worker = threading.Thread(target=app.run, daemon=True)
    worker.start()

    def quit_app():
        app.stop_event.set()
        ui.destroy()  # webview siklini tugatadi -> main davom etadi

    icon = create_icon(app, on_settings=ui.show, on_quit=quit_app)
    icon.run_detached()

    ui.run(app)  # bloklanadi; quit_app yoki oyna destroy bo'lganda qaytadi

    app.stop_event.set()
    icon.stop()
    worker.join(timeout=3)
    log.info("GestureDJ to'xtadi")


if __name__ == "__main__":
    main()
