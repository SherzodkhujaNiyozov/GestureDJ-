"""GestureDJ sozlamalari.

Default qiymatlar shu faylda. Loyiha ildizidagi config.json mavjud bo'lsa,
undagi qiymatlar defaultlarni bekor qiladi. Sozlamalar oynasi save()
orqali config.json'ga yozadi - kod o'zgarmaydi.
"""

import json
import logging

from .paths import app_dir

log = logging.getLogger(__name__)

CONFIG_PATH = app_dir() / "config.json"

DEFAULTS: dict = {
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
    """Defaultlarni qo'llab, config.json bo'lsa ustidan yozadi."""
    globals().update(DEFAULTS)
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            known = {k: v for k, v in data.items() if k in DEFAULTS}
            globals().update(known)
            log.info("config.json yuklandi (%d ta qiymat)", len(known))
        except (json.JSONDecodeError, OSError) as e:
            log.warning("config.json o'qib bo'lmadi, defaultlar ishlatiladi: %s", e)


def current() -> dict:
    """Hozirgi amaldagi sozlamalar."""
    return {k: globals()[k] for k in DEFAULTS}


def update(values: dict) -> None:
    """Sozlamalarni jonli qo'llash (faqat ma'lum kalitlar, tip tekshiruv bilan)."""
    for k, v in values.items():
        if k in DEFAULTS and isinstance(v, (int, float)):
            globals()[k] = type(DEFAULTS[k])(v)


def save() -> None:
    CONFIG_PATH.write_text(
        json.dumps(current(), indent=2, ensure_ascii=False), encoding="utf-8"
    )
    log.info("config.json saqlandi")


def reset() -> None:
    globals().update(DEFAULTS)
    if CONFIG_PATH.exists():
        CONFIG_PATH.unlink()
    log.info("Sozlamalar defaultga qaytarildi")


load()
