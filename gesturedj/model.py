"""hand_landmarker.task model faylini boshqarish.

Model bir marta yuklab olinadi (~8MB) va models/ papkasida saqlanadi.
Keyin ilova to'liq oflayn ishlaydi.

Xavfsizlik: yuklab olingan fayl SHA-256 bilan tekshiriladi (supply-chain
himoyasi). Almashtirilgan/buzilgan model qabul qilinmaydi.
"""

import hashlib
import logging
import urllib.request
from pathlib import Path

log = logging.getLogger(__name__)

MODEL_URL = (
    "https://storage.googleapis.com/mediapipe-models/hand_landmarker/"
    "hand_landmarker/float16/latest/hand_landmarker.task"
)
# Ishonchli model fayli hash'i (pinlangan). Google modelni yangilasa yangilanadi.
MODEL_SHA256 = "fbc2a30080c3c557093b5ddfc334698132eb341044ccee322ccf8bcf3607cde1"
_REL = Path("models") / "hand_landmarker.task"


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_model() -> str:
    from .paths import app_dir, resource_dir

    bundled = resource_dir() / _REL  # exe ichiga qadoqlangan nusxa (ishonchli)
    if bundled.exists():
        return str(bundled)

    local = app_dir() / _REL

    # Mavjud nusxa buzilgan/o'zgargan bo'lsa - qayta yuklash uchun o'chiramiz
    if local.exists() and _sha256(local) != MODEL_SHA256:
        log.warning("Model hash mos kelmadi, qayta yuklanadi: %s", local)
        local.unlink()

    if not local.exists():
        log.info("Model yuklab olinmoqda: %s", MODEL_URL)
        local.parent.mkdir(parents=True, exist_ok=True)
        tmp = local.with_suffix(".part")
        urllib.request.urlretrieve(MODEL_URL, tmp)  # HTTPS
        digest = _sha256(tmp)
        if digest != MODEL_SHA256:
            tmp.unlink(missing_ok=True)
            raise RuntimeError(
                f"Model SHA-256 mos kelmadi (kutilgan {MODEL_SHA256[:12]}…, "
                f"olingan {digest[:12]}…) — yuklash rad etildi"
            )
        tmp.replace(local)  # atomik
        log.info("Model tekshirildi va saqlandi: %s", local)

    return str(local)
