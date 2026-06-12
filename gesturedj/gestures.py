"""21 ta qo'l landmark'idan ishoralarni aniqlash.

MediaPipe landmark indekslari:
  0=wrist, 4=thumb_tip, 8=index_tip, 12=middle_tip, 16=ring_tip, 20=pinky_tip
  Har bir barmoq: MCP -> PIP -> DIP -> TIP

Ishoralar:
  THUMBS_UP - faqat bosh barmoq ochiq, tepaga qaragan -> faollashtirish
  INDEX_UP  - faqat ko'rsatkich barmoq ochiq           -> standby'ga qaytish
  FIST      - musht                                     -> play/pause toggle
  BEAK      - barcha barmoq uchlari jips (🤌)          -> mute/unmute toggle
  OPEN_PALM - kaft ochiq (hozircha amal biriktirilmagan)
  volume pose - bosh+ko'rsatkich ochiq, qolganlari yopiq -> pinch bilan volume
"""

import math

from . import config

WRIST = 0
THUMB_MCP, THUMB_TIP = 2, 4
INDEX_MCP, INDEX_PIP, INDEX_TIP = 5, 6, 8
MIDDLE_MCP, MIDDLE_PIP, MIDDLE_TIP = 9, 10, 12
RING_PIP, RING_TIP = 14, 16
PINKY_PIP, PINKY_TIP = 18, 20

TIPS = [THUMB_TIP, INDEX_TIP, MIDDLE_TIP, RING_TIP, PINKY_TIP]

THUMBS_UP = "thumbs_up"
INDEX_UP = "index_up"
OPEN_PALM = "open_palm"
FIST = "fist"
BEAK = "beak"


def _dist(a, b) -> float:
    return math.hypot(a.x - b.x, a.y - b.y)


def hand_size(lms) -> float:
    """Kaft o'lchami - masofalarni normalizatsiya qilish uchun (kamera
    uzoq/yaqinligiga bog'liq bo'lmasligi uchun)."""
    return _dist(lms[WRIST], lms[MIDDLE_MCP]) or 1e-6


def _finger_extended(lms, tip: int, pip: int) -> bool:
    """Barmoq ochiqmi: uchi bilakdan PIP bo'g'imiga nisbatan uzoqroq bo'lsa."""
    return _dist(lms[WRIST], lms[tip]) > _dist(lms[WRIST], lms[pip]) * 1.15


def _thumb_extended(lms) -> bool:
    return _dist(lms[THUMB_TIP], lms[INDEX_MCP]) > hand_size(lms) * 0.5


def fingers_extended(lms) -> list[bool]:
    """[thumb, index, middle, ring, pinky]"""
    return [
        _thumb_extended(lms),
        _finger_extended(lms, INDEX_TIP, INDEX_PIP),
        _finger_extended(lms, MIDDLE_TIP, MIDDLE_PIP),
        _finger_extended(lms, RING_TIP, RING_PIP),
        _finger_extended(lms, PINKY_TIP, PINKY_PIP),
    ]


# ----------------------------------------------------------------------
# Kalibrlash uchun metrikalar (debug panelda ham ko'rsatiladi)

def beak_cluster(lms) -> float:
    """Barmoq uchlari markazdan o'rtacha qancha uzoq (kaft o'lchamiga nisbatan).

    Kichik qiymat = uchlar jips (🤌). BEAK uchun config.BEAK_CLUSTER_MAX dan
    kichik bo'lishi kerak.
    """
    size = hand_size(lms)
    cx = sum(lms[t].x for t in TIPS) / 5
    cy = sum(lms[t].y for t in TIPS) / 5
    return max(
        math.hypot(lms[t].x - cx, lms[t].y - cy) for t in TIPS
    ) / size


def beak_reach(lms) -> float:
    """O'rta barmoq uchi bilakdan qancha uzoqda. Mushtdan farqlash uchun:
    BEAK'da barmoqlar oldinga cho'zilgan, mushtda kaftga yig'ilgan."""
    return _dist(lms[WRIST], lms[MIDDLE_TIP]) / hand_size(lms)


def spread_gap(lms) -> float:
    """Qo'shni barmoq uchlari orasidagi o'rtacha masofa (kaft o'lchamiga
    nisbatan). Kichik = 4 barmoq jips (BEAK_OPEN belgisi), katta =
    barmoqlar yoyilgan oddiy ochiq kaft."""
    size = hand_size(lms)
    gaps = [
        _dist(lms[INDEX_TIP], lms[MIDDLE_TIP]),
        _dist(lms[MIDDLE_TIP], lms[RING_TIP]),
        _dist(lms[RING_TIP], lms[PINKY_TIP]),
    ]
    return sum(gaps) / len(gaps) / size


def pinch_ratio(lms) -> float:
    """Bosh barmoq va ko'rsatkich barmoq uchlari orasidagi normalangan masofa."""
    return _dist(lms[THUMB_TIP], lms[INDEX_TIP]) / hand_size(lms)


# ----------------------------------------------------------------------

def is_volume_pose(lms) -> bool:
    """Volume holati (1-rasm): bosh + ko'rsatkich ochiq, qolganlari yopiq."""
    f = fingers_extended(lms)
    return f[0] and f[1] and not f[2] and not f[3] and not f[4]


def classify(lms) -> str | None:
    """Statik ishorani aniqlash."""
    f = fingers_extended(lms)
    thumb, index, middle, ring, pinky = f

    # BEAK birinchi tekshiriladi: uchlar jips bo'lsa barmoqlar "ochiq"
    # ko'rinishi mumkin va OPEN_PALM bilan adashadi
    if (
        beak_cluster(lms) < config.BEAK_CLUSTER_MAX
        and beak_reach(lms) > config.BEAK_MIN_REACH
    ):
        return BEAK

    if index and not thumb and not middle and not ring and not pinky:
        return INDEX_UP

    # Thumbs-up: faqat bosh barmoq ochiq va uchi bilakdan tepada
    if thumb and not index and not middle and not ring and not pinky:
        if lms[THUMB_TIP].y < lms[WRIST].y:
            return THUMBS_UP
        return None

    if index and middle and ring and pinky:
        return OPEN_PALM

    if not index and not middle and not ring and not pinky:
        return FIST

    return None
