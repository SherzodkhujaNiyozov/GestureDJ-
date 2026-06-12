"""Media tugmalarini Windows'ga yuborish (play/pause).

Eslatma: Windows'da play va pause uchun ALOHIDA tugma yo'q - bitta
VK_MEDIA_PLAY_PAUSE toggle tugmasi bor. Shuning uchun "ochiq kaft = play"
va "musht = pause" ikkalasi ham shu toggle'ni bosadi; media allaqachon
o'ynayotgan bo'lsa kaft uni pauza qilib qo'yishi mumkin.
"""

import ctypes

VK_MEDIA_PLAY_PAUSE = 0xB3
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002


def play_pause() -> None:
    user32 = ctypes.windll.user32
    user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY, 0)
    user32.keybd_event(VK_MEDIA_PLAY_PAUSE, 0, KEYEVENTF_EXTENDEDKEY | KEYEVENTF_KEYUP, 0)
