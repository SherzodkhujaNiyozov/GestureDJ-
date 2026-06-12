# GestureDJ 🎚️🖐️

Qo'l ishoralari bilan Windows tizim ovozini boshqaruvchi desktop ilova.
Webcam orqali qo'lingizni kuzatadi (MediaPipe), tizim tray'ida ishlaydi.

## Ishoralar

| Ishora | Vazifa |
|--------|--------|
| 👍 Thumbs-up (1 soniya) | Boshqaruvni **faollashtirish** |
| 👆 Faqat ko'rsatkich barmoq (1 soniya) | Boshqaruvni **o'chirish** (standby) |
| 🤏 Bosh + ko'rsatkich barmoq ochiq, qolganlari yopiq | **Volume** — barmoqlar orasi qancha keng, ovoz shuncha baland |
| ✊ Musht | **Play/Pause** toggle (media tugmasi) |
| 🤌 Barmoq uchlari jips | **Mute/Unmute** toggle |

Standby rejimida ilova past FPS'da ishlaydi (CPU tejaladi) va faqat
faollashtirish ishorasini kutadi.

## O'rnatish

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
```

## Ishga tushirish

```powershell
.\.venv\Scripts\python run.py
```

Ilova tray'da paydo bo'ladi. Tray menyusidan:
- **Sozlamalar** (yoki ikonkaga ikki marta bosish) — jonli kalibrlash va
  sozlamalar oynasi: hozirgi gesture, volume, pinch/beak metrikalari,
  threshold slider'lari. O'zgarishlar darhol qo'llanadi va `config.json`
  ga saqlanadi
- **Preview ko'rsatish** — kamera + qo'l skeleti oynasini ochish (debug uchun)
- **Chiqish** — ilovani yopish

Sozlamalar oynasini yopsangiz ilova tray'da ishlashda davom etadi.
Loglar `logs/gesturedj.log` faylida.

## Texnologiyalar

- [MediaPipe Hands](https://developers.google.com/mediapipe) — qo'lning 21 nuqtasini lokal aniqlash (internet kerak emas)
- OpenCV — kamera oqimi
- pycaw — Windows Core Audio API (volume)
- pystray — tizim tray ikonkasi

## EXE qilib qadoqlash (PyInstaller)

```powershell
.\.venv\Scripts\pip install pyinstaller
.\.venv\Scripts\pyinstaller --noconsole --name GestureDJ `
  --collect-all mediapipe --collect-all cv2 `
  run.py
```

Natija: `dist\GestureDJ\GestureDJ.exe` (onedir rejimi tavsiya etiladi —
onefile sekin ochiladi).

## Arxitektura

```
gesturedj/
  main.py      - kirish nuqtasi (worker thread + tray + UI)
  app.py       - holat mashinasi (standby/active), kamera sikli
  gestures.py  - landmark'lardan ishora aniqlash
  audio.py     - pycaw orqali volume boshqarish
  media.py     - media tugmalari (play/pause)
  smoothing.py - EMA (titroqqa qarshi silliqlash)
  tray.py      - pystray ikonka va menyu
  ui.py        - pywebview sozlamalar oynasi (JS<->Python ko'prik)
  web/         - sozlamalar oynasi UI (HTML/CSS/JS, dark theme)
  config.py    - default sozlamalar + config.json yuklash/saqlash
```
