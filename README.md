# GestureDJ 🎚️🖐️

Qo'l ishoralari bilan Windows tizim ovozini boshqaruvchi desktop ilova.
Webcam orqali qo'lingizni kuzatadi (MediaPipe), tizim tray'ida ishlaydi.

## Ishoralar

| Ishora | Vazifa |
|--------|--------|
| 🖐️ Ochiq kaft (1 soniya) | Boshqaruvni **faollashtirish** |
| ✊ Musht (1 soniya) | Boshqaruvni **o'chirish** (standby) |
| 🤏 Chimdish (middle/ring/pinky ochiq holda) | **Volume** — barmoqlar orasi qancha keng, ovoz shuncha baland |

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
- **Preview ko'rsatish** — kamera + qo'l skeleti oynasini ochish (debug uchun)
- **Chiqish** — ilovani yopish

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
  main.py      - kirish nuqtasi (worker thread + tray)
  app.py       - holat mashinasi (standby/active), kamera sikli
  gestures.py  - landmark'lardan ishora aniqlash
  audio.py     - pycaw orqali volume boshqarish
  smoothing.py - EMA (titroqqa qarshi silliqlash)
  tray.py      - pystray ikonka va menyu
  config.py    - barcha sozlamalar
```
