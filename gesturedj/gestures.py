"""21 ta qo'l landmark'idan ishoralarni aniqlash.

MediaPipe landmark indekslari:
  0=wrist, 4=thumb_tip, 8=index_tip, 12=middle_tip, 16=ring_tip, 20=pinky_tip
  Har bir barmoq: MCP -> PIP -> DIP -> TIP
"""

import math

WRIST = 0
THUMB_TIP = 4
INDEX_MCP, INDEX_PIP, INDEX_TIP = 5, 6, 8
MIDDLE_MCP, MIDDLE_PIP, MIDDLE_TIP = 9, 10, 12
RING_PIP, RING_TIP = 14, 16
PINKY_PIP, PINKY_TIP = 18, 20

OPEN_PALM = "open_palm"
FIST = "fist"


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


def classify(lms) -> str | None:
    """Statik ishorani aniqlash: open_palm / fist / None."""
    f = fingers_extended(lms)
    if all(f):
        return OPEN_PALM
    if not any(f[1:]):  # 4 barmoq yopiq (bosh barmoq hisobga olinmaydi)
        return FIST
    return None


def is_volume_pose(lms) -> bool:
    """Volume boshqarish holati: middle+ring+pinky ochiq turishi shart.

    Bu tasodifiy chimdishlarda volume o'zgarib ketishining oldini oladi.
    """
    f = fingers_extended(lms)
    return f[2] and f[3] and f[4]


def pinch_ratio(lms) -> float:
    """Bosh barmoq va ko'rsatkich barmoq uchlari orasidagi normalangan masofa."""
    return _dist(lms[THUMB_TIP], lms[INDEX_TIP]) / hand_size(lms)
