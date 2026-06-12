"""hand_landmarker.task model faylini boshqarish.

Model bir marta yuklab olinadi (~8MB) va models/ papkasida saqlanadi.
Keyin ilova to'liq oflayn ishlaydi.
"""

import urllib.request
from pathlib import Path

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task"
)
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "hand_landmarker.task"


def ensure_model() -> str:
    if not MODEL_PATH.exists():
        print(f"Model yuklab olinmoqda: {MODEL_URL}")
        MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(MODEL_URL, MODEL_PATH)
        print(f"Model saqlandi: {MODEL_PATH}")
    return str(MODEL_PATH)
