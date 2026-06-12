"""GestureDJ kirish nuqtasi.

Ishga tushirish:  python -m gesturedj.main   yoki   python run.py
"""

import threading

from .app import GestureApp
from .tray import run_tray


def main() -> None:
    app = GestureApp()
    worker = threading.Thread(target=app.run, daemon=True)
    worker.start()
    run_tray(app)  # tray yopilganda dastur tugaydi
    app.stop_event.set()
    worker.join(timeout=3)


if __name__ == "__main__":
    main()
