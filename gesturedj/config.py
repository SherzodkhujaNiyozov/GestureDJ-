"""GestureDJ sozlamalari."""

# Kamera
CAMERA_INDEX = 0
FRAME_WIDTH = 640
FRAME_HEIGHT = 480

# FPS rejimlari (CPU tejash uchun standby'da past FPS)
ACTIVE_FPS = 20
STANDBY_FPS = 5

# Ishorani qancha vaqt ushlab turish kerak (sekund)
ACTIVATE_HOLD_SEC = 1.0   # ochiq kaft -> faollashtirish
DEACTIVATE_HOLD_SEC = 1.0  # musht -> standby

# MediaPipe
MIN_DETECTION_CONFIDENCE = 0.7
MIN_TRACKING_CONFIDENCE = 0.6

# Pinch (chimdish) -> volume xaritalash
# pinch_ratio = thumb_tip va index_tip orasidagi masofa / kaft o'lchami
PINCH_MIN = 0.15  # shu va undan kichik -> volume 0%
PINCH_MAX = 1.00  # shu va undan katta -> volume 100%

# Silliqlash (jitter'ga qarshi). 0..1, kichikroq = silliqroq lekin sekinroq
SMOOTHING_ALPHA = 0.25

# Volume'ni necha foiz o'zgarganda yangilash (WS/CPU tejash)
VOLUME_UPDATE_EPSILON = 0.01
