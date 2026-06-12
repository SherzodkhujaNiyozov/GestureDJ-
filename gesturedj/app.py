"""Asosiy ish sikli: kamera -> MediaPipe HandLandmarker -> ishora -> audio.

Holatlar:
  STANDBY - past FPS, faqat "ochiq kaft" (faollashtirish) kutiladi
  ACTIVE  - to'liq FPS, pinch bilan volume, "musht" bilan standby'ga qaytish
"""

import logging
import threading
import time

import cv2
import mediapipe as mp
from mediapipe.tasks.python import BaseOptions
from mediapipe.tasks.python import vision

from . import config, gestures, media
from .audio import AudioController
from .model import ensure_model
from .smoothing import EMA

log = logging.getLogger(__name__)

STANDBY = "standby"
ACTIVE = "active"

# MediaPipe qo'l skeleti chiziqlari (preview uchun)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),          # bosh barmoq
    (0, 5), (5, 6), (6, 7), (7, 8),          # ko'rsatkich
    (5, 9), (9, 10), (10, 11), (11, 12),     # o'rta
    (9, 13), (13, 14), (14, 15), (15, 16),   # nomsiz
    (13, 17), (0, 17), (17, 18), (18, 19), (19, 20),  # jimjiloq + kaft
]


class GestureApp:
    def __init__(self):
        self.state = STANDBY
        self.stop_event = threading.Event()
        self.show_preview = False
        self.last_volume: float | None = None
        self.on_state_change = None  # tray icon yangilash uchun callback
        self.metrics: dict = {}  # sozlamalar oynasi uchun jonli holat

    # ------------------------------------------------------------------
    def run(self) -> None:
        """Ishchi thread'da chaqiriladi."""
        try:
            self._run()
        except Exception:
            log.exception("Ishchi sikl kutilmagan xato bilan to'xtadi")

    def _run(self) -> None:
        audio = AudioController()  # COM shu thread'da init bo'lishi kerak
        volume_ema = EMA(config.SMOOTHING_ALPHA)
        self.last_volume = audio.get_volume()
        log.info("Ishga tushdi: kamera=%s, volume=%.0f%%",
                 config.CAMERA_INDEX, self.last_volume * 100)

        def mute_toggle():
            muted = not audio.is_muted()
            audio.set_mute(muted)
            self.metrics["muted"] = muted

        cap = cv2.VideoCapture(config.CAMERA_INDEX, cv2.CAP_DSHOW)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, config.FRAME_WIDTH)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, config.FRAME_HEIGHT)

        landmarker = vision.HandLandmarker.create_from_options(
            vision.HandLandmarkerOptions(
                base_options=BaseOptions(model_asset_path=ensure_model()),
                running_mode=vision.RunningMode.VIDEO,
                num_hands=1,
                min_hand_detection_confidence=config.MIN_DETECTION_CONFIDENCE,
                min_tracking_confidence=config.MIN_TRACKING_CONFIDENCE,
            )
        )

        gesture_start: dict[str, float] = {}  # ishora qachondan beri ushlab turilibdi
        fired: set[str] = set()  # bir ishora uchun amal faqat bir marta bajarilsin
        preview_open = False
        start_time = time.monotonic()
        last_mute_check = 0.0

        try:
            while not self.stop_event.is_set():
                t0 = time.monotonic()

                ok, frame = cap.read()
                if not ok:
                    time.sleep(0.5)
                    continue

                frame = cv2.flip(frame, 1)  # ko'zgu - foydalanuvchiga tabiiy
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                timestamp_ms = int((t0 - start_time) * 1000)
                result = landmarker.detect_for_video(mp_image, timestamp_ms)

                lms = result.hand_landmarks[0] if result.hand_landmarks else None

                gesture = gestures.classify(lms) if lms else None
                self._track_hold(gesture, gesture_start)
                fired.intersection_update(gesture_start)  # ishora qo'yib yuborilsa qayta otishga ruxsat

                if self.state == STANDBY:
                    # 👍 thumbs-up -> faollashtirish
                    if self._held(gestures.THUMBS_UP, gesture_start, config.ACTIVATE_HOLD_SEC):
                        self._set_state(ACTIVE)
                        gesture_start.clear()
                        fired.clear()
                        volume_ema.reset()
                else:  # ACTIVE
                    # 👆 faqat ko'rsatkich barmoq -> trayga qaytish (standby)
                    if self._held(gestures.INDEX_UP, gesture_start, config.DEACTIVATE_HOLD_SEC):
                        self._set_state(STANDBY)
                        gesture_start.clear()
                        fired.clear()
                    elif lms is not None and gestures.is_volume_pose(lms):
                        # 🤏 pinch -> volume (uzluksiz)
                        ratio = gestures.pinch_ratio(lms)
                        target = self._ratio_to_volume(ratio)
                        volume_ema.alpha = config.SMOOTHING_ALPHA  # jonli sozlanadi
                        smoothed = volume_ema.update(target)
                        if (
                            self.last_volume is None
                            or abs(smoothed - self.last_volume) >= config.VOLUME_UPDATE_EPSILON
                        ):
                            audio.set_volume(smoothed)
                            self.last_volume = smoothed
                    else:
                        volume_ema.reset()
                        # Bir martalik amallar (gesture ushlab turilganda 1 marta)
                        for g, name, action in (
                            (gestures.FIST, "play/pause", media.play_pause),  # ✊ toggle
                            (gestures.BEAK, "mute toggle", mute_toggle),       # 🤌 toggle
                        ):
                            if g not in fired and self._held(g, gesture_start, config.ACTION_HOLD_SEC):
                                action()
                                fired.add(g)
                                log.info("Amal bajarildi: %s (gesture=%s)", name, g)

                # --- Jonli holat (sozlamalar oynasi o'qiydi) ---
                if t0 - last_mute_check > 1.0:
                    self.metrics["muted"] = audio.is_muted()
                    last_mute_check = t0
                self.metrics.update({
                    "state": self.state,
                    "gesture": gesture,
                    "hand": lms is not None,
                    "volume": self.last_volume,
                    "pinch": gestures.pinch_ratio(lms) if lms else None,
                    "spread": gestures.spread_gap(lms) if lms else None,
                    "beak": gestures.beak_cluster(lms) if lms else None,
                })

                # --- Preview oynasi (tray menyusidan yoqiladi) ---
                if self.show_preview:
                    if lms is not None:
                        self._draw_hand(frame, lms)
                        self._draw_debug(frame, lms, gesture, gesture_start)
                    self._draw_hud(frame)
                    cv2.imshow("GestureDJ", frame)
                    cv2.waitKey(1)
                    preview_open = True
                elif preview_open:
                    cv2.destroyWindow("GestureDJ")
                    preview_open = False

                # --- FPS cheklash (standby'da CPU tejaymiz) ---
                fps = config.ACTIVE_FPS if self.state == ACTIVE else config.STANDBY_FPS
                elapsed = time.monotonic() - t0
                time.sleep(max(0.0, 1.0 / fps - elapsed))
        finally:
            cap.release()
            landmarker.close()
            cv2.destroyAllWindows()

    # ------------------------------------------------------------------
    @staticmethod
    def _track_hold(gesture: str | None, start: dict[str, float]) -> None:
        now = time.monotonic()
        if gesture is None:
            start.clear()
            return
        start.setdefault(gesture, now)
        # boshqa ishoralar uzilib qoldi
        for g in list(start):
            if g != gesture:
                del start[g]

    @staticmethod
    def _held(gesture: str, start: dict[str, float], duration: float) -> bool:
        t = start.get(gesture)
        return t is not None and time.monotonic() - t >= duration

    @staticmethod
    def _ratio_to_volume(ratio: float) -> float:
        span = config.PINCH_MAX - config.PINCH_MIN
        return max(0.0, min(1.0, (ratio - config.PINCH_MIN) / span))

    def _set_state(self, state: str) -> None:
        self.state = state
        log.info("Holat o'zgardi: %s", state)
        if self.on_state_change:
            self.on_state_change(state)

    @staticmethod
    def _draw_hand(frame, lms) -> None:
        h, w = frame.shape[:2]
        pts = [(int(p.x * w), int(p.y * h)) for p in lms]
        for a, b in HAND_CONNECTIONS:
            cv2.line(frame, pts[a], pts[b], (0, 200, 0), 2)
        for p in pts:
            cv2.circle(frame, p, 4, (0, 100, 255), -1)

    @staticmethod
    def _draw_debug(frame, lms, gesture: str | None, gesture_start: dict[str, float]) -> None:
        """Kalibrlash paneli: barmoqlar holati, pinch qiymati, hold jarayoni."""
        h = frame.shape[0]
        names = ["thumb", "index", "middle", "ring", "pinky"]
        ext = gestures.fingers_extended(lms)
        for i, (name, on) in enumerate(zip(names, ext)):
            color = (0, 200, 0) if on else (60, 60, 200)
            cv2.putText(frame, name, (10, h - 110 + i * 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        pinch = gestures.pinch_ratio(lms)
        vol_pose = gestures.is_volume_pose(lms)
        cv2.putText(frame, f"pinch: {pinch:.2f} (min={config.PINCH_MIN} max={config.PINCH_MAX})  "
                           f"volume_pose: {'HA' if vol_pose else 'yoq'}",
                    (120, h - 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        cv2.putText(frame, f"spread: {gestures.spread_gap(lms):.2f}  "
                           f"beak: {gestures.beak_cluster(lms):.2f} (<{config.BEAK_CLUSTER_MAX} = mute toggle)",
                    (120, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)
        cv2.putText(frame, f"gesture: {gesture or '-'}",
                    (120, h - 70), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

        # Hold progress (amal bajarilishiga qancha qoldi)
        if gesture in gesture_start:
            need = {
                gestures.THUMBS_UP: config.ACTIVATE_HOLD_SEC,
                gestures.INDEX_UP: config.DEACTIVATE_HOLD_SEC,
            }.get(gesture, config.ACTION_HOLD_SEC)
            progress = min(1.0, (time.monotonic() - gesture_start[gesture]) / need)
            cv2.rectangle(frame, (120, h - 100), (320, h - 85), (80, 80, 80), 1)
            cv2.rectangle(frame, (120, h - 100), (120 + int(200 * progress), h - 85),
                          (0, 200, 0), -1)

    def _draw_hud(self, frame) -> None:
        color = (0, 200, 0) if self.state == ACTIVE else (128, 128, 128)
        label = "FAOL" if self.state == ACTIVE else "KUTISH (thumbs-up'ni 1s ko'rsating)"
        cv2.putText(frame, label, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
        if self.state == ACTIVE and self.last_volume is not None:
            cv2.putText(
                frame,
                f"Volume: {int(self.last_volume * 100)}%",
                (10, 60),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 200, 0),
                2,
            )
