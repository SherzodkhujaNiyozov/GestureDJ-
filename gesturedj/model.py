"""hand_landmarker.task model faylini boshqarish.

Model bir marta yuklab olinadi (~8MB) va models/ papkasida saqlanadi.
Keyin ilova to'liq oflayn ishlaydi.
"""

import logging
import urllib.request
from pathlib import Path

log = logging.getLogger(__name__)

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task"
)
_REL = Path("models") / "hand_landmarker.task"


def ensure_model() -> str:
    from .paths import app_dir, resource_dir

    bundled = resource_dir() / _REL  # exe ichiga qadoqlangan nusxa
    if bundled.exists():
        return str(bundled)

    local = app_dir() / _REL
    if not local.exists():
        log.info("Model yuklab olinmoqda: %s", MODEL_URL)
        local.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(MODEL_URL, local)
        log.info("Model saqlandi: %s", local)
    return str(local)
