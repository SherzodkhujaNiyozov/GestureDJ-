"""GestureDJ sozlamalari.

Default qiymatlar shu faylda. Loyiha ildizidagi config.json mavjud bo'lsa,
undagi qiymatlar defaultlarni bekor qiladi. Sozlamalar oynasi save()
orqali config.json'ga yozadi - kod o'zgarmaydi.
"""

import json
import logging
import os

from .paths import app_dir

log = logging.getLogger(__name__)

CONFIG_PATH = app_dir() / "config.json"

# Xavfsiz oraliqlar: qo'lda tahrirlangan yoki buzilgan config.json ilovani
# nosog'lom holatga keltira olmasligi uchun har bir son shu chegaraga siqiladi.
BOUNDS: dict = {
    "CAMERA_INDEX": (0, 10),
    "FRAME_WIDTH": (160, 1920),
    "FRAME_HEIGHT": (120, 1080),
    "ACTIVE_FPS": (1, 60),
    "STANDBY_FPS": (1, 30),
    "ACTIVATE_HOLD_SEC": (0.1, 10.0),
    "DEACTIVATE_HOLD_SEC": (0.1, 10.0),
    "ACTION_HOLD_SEC": (0.1, 10.0),
    "MIN_DETECTION_CONFIDENCE": (0.1, 1.0),
    "MIN_TRACKING_CONFIDENCE": (0.1, 1.0),
    "BEAK_CLUSTER_MAX": (0.01, 1.0),
    "BEAK_MIN_REACH": (0.1, 3.0),
    "PINCH_MIN": (0.0, 2.0),
    "PINCH_MAX": (0.0, 3.0),
    "SMOOTHING_ALPHA": (0.01, 1.0),
    "VOLUME_UPDATE_EPSILON": (0.0, 0.5),
}
LANGUAGES = ("uz", "en", "es", "ja", "ru")


def _clamp(key, value):
    lo, hi = BOUNDS[key]
    return type(DEFAULTS[key])(max(lo, min(hi, value)))

DEFAULTS: dict = {
    # Til (UI tili): uz | en | es | ja | ru
    "LANG": "uz",

    # Kamera
    "CAMERA_INDEX": 0,
    "FRAME_WIDTH": 640,
    "FRAME_HEIGHT": 480,

    # FPS rejimlari (CPU tejash uchun standby'da past FPS)
    "ACTIVE_FPS": 20,
    "STANDBY_FPS": 5,

    # Ishorani qancha vaqt ushlab turish kerak (sekund)
    "ACTIVATE_HOLD_SEC": 1.0,    # thumbs-up -> faollashtirish
    "DEACTIVATE_HOLD_SEC": 1.0,  # ko'rsatkich barmoq -> standby
    "ACTION_HOLD_SEC": 0.5,      # play/pause/mute uchun

    # MediaPipe (o'zgartirilsa qayta ishga tushirish kerak)
    "MIN_DETECTION_CONFIDENCE": 0.7,
    "MIN_TRACKING_CONFIDENCE": 0.6,

    # BEAK (mute toggle, barmoq uchlari jips) chegaralari
    "BEAK_CLUSTER_MAX": 0.30,
    "BEAK_MIN_REACH": 1.10,

    # Pinch (chimdish) -> volume xaritalash
    "PINCH_MIN": 0.15,
    "PINCH_MAX": 1.00,

    # Silliqlash (jitter'ga qarshi). 0..1, kichikroq = silliqroq lekin sekinroq
    "SMOOTHING_ALPHA": 0.25,

    # Volume'ni necha foiz o'zgarganda yangilash
    "VOLUME_UPDATE_EPSILON": 0.01,
}


def load() -> None:
    """Defaultlarni qo'llab, config.json bo'lsa ustidan yozadi (validatsiya bilan)."""
    globals().update(DEFAULTS)
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                update(data)  # update() tip + oraliq tekshiruvini bajaradi
                log.info("config.json yuklandi")
        except (json.JSONDecodeError, OSError, ValueError) as e:
            log.warning("config.json o'qib bo'lmadi, defaultlar ishlatiladi: %s", e)


def current() -> dict:
    """Hozirgi amaldagi sozlamalar."""
    return {k: globals()[k] for k in DEFAULTS}


def update(values: dict) -> None:
    """Sozlamalarni jonli qo'llash. Faqat ma'lum kalitlar; tip tekshiruvi va
    sonlar uchun xavfsiz oraliqqa siqish (clamp)."""
    if not isinstance(values, dict):
        return
    for k, v in values.items():
        if k not in DEFAULTS:
            continue
        dtype = type(DEFAULTS[k])
        if k == "LANG":
            if v in LANGUAGES:
                globals()[k] = v
        elif dtype in (int, float) and isinstance(v, (int, float)) and not isinstance(v, bool):
            globals()[k] = _clamp(k, v) if k in BOUNDS else dtype(v)


def save() -> None:
    """Atomik yozish: vaqtinchalik faylga yozib, keyin almashtirish - jarayon
    yozish payti uzilsa ham config.json buzilmaydi."""
    try:
        tmp = CONFIG_PATH.with_suffix(".tmp")
        tmp.write_text(
            json.dumps(current(), indent=2, ensure_ascii=False), encoding="utf-8"
        )
        os.replace(tmp, CONFIG_PATH)
        log.info("config.json saqlandi")
    except OSError as e:
        # Masalan Program Files'ga yozish huquqi bo'lmasligi mumkin
        log.warning("config.json saqlanmadi: %s", e)


def reset() -> None:
    globals().update(DEFAULTS)
    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()
    log.info("Sozlamalar defaultga qaytarildi")


load()
