<img src="assets/logo/gesturedj-mark-128.png" align="left" width="84" height="84" alt="GestureDJ logo">

# GestureDJ

> Control your PC's audio with hand gestures — webcam + MediaPipe, lives in
> the Windows system tray. Pinch to set volume, fist to play/pause, beak to
> mute. 100% local, no external APIs.

<br clear="left">


Qo'l ishoralari bilan Windows tizim ovozini boshqaruvchi desktop ilova.
Webcam orqali qo'lingizni kuzatadi (MediaPipe), tizim tray'ida ishlaydi.
To'liq lokal — internetga ma'lumot yubormaydi, tashqi API ishlatmaydi.

<!-- TODO: demo GIF shu yerga (ScreenToGif bilan yozib oling) -->

**Texnologiyalar:** Python · MediaPipe Tasks (HandLandmarker) · OpenCV ·
pycaw · pystray · pywebview

## Maxfiylik 🔒

- 📷 **Kamera tasviri hech qayerga yuborilmaydi** — barchasi lokal qayta ishlanadi
- 🚫 Telemetriya, analitika, kuzatuv — **yo'q**
- 🌐 Yagona tarmoq chaqiruvi: birinchi ishga tushishda modelni yuklash (HTTPS + SHA-256 tekshiruv). EXE'da model ichida — **to'liq oflayn**
- 🔑 Administrator huquqi **kerak emas**

To'liq tafsilot: [SECURITY.md](SECURITY.md)

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

Diagnostika uchun sozlamalar oynasisiz rejim: `python run.py --no-ui`

Ilova tray'da paydo bo'ladi. Tray menyusidan:
- **Sozlamalar** (yoki ikonkaga ikki marta bosish) — jonli kalibrlash va
  sozlamalar oynasi: hozirgi gesture, volume, pinch/beak metrikalari,
  threshold slider'lari. O'zgarishlar darhol qo'llanadi va `config.json`
  ga saqlanadi
- **Preview ko'rsatish** — kamera + qo'l skeleti oynasini ochish (debug uchun)
- **Chiqish** — ilovani yopish

Sozlamalar oynasini yopsangiz ilova tray'da ishlashda davom etadi.
Sozlamalar oynasida **"Windows bilan ishga tushsin"** belgisi bor —
yoqsangiz ilova tizim bilan birga avtomatik ochiladi.
Loglar `logs/gesturedj.log` faylida.

## Texnologiyalar

- [MediaPipe Hands](https://developers.google.com/mediapipe) — qo'lning 21 nuqtasini lokal aniqlash (internet kerak emas)
- OpenCV — kamera oqimi
- pycaw — Windows Core Audio API (volume)
- pystray — tizim tray ikonkasi

## EXE qilib qadoqlash (PyInstaller)

**Oson yo'l** — tayyor skript (ikonkani yangilaydi, eski build'ni tozalaydi, yig'adi):

```powershell
.\build.ps1
```

**Qo'lda** — bosqichma-bosqich:

```powershell
# 1. PyInstaller'ni o'rnatish (bir marta)
.\.venv\Scripts\pip install pyinstaller

# 2. Logodan ikonka yasash (logo o'zgarsa qayta)
.\.venv\Scripts\python scripts\make_icon.py

# 3. Yig'ish
.\.venv\Scripts\pyinstaller --noconfirm --noconsole --name GestureDJ `
  --icon assets\icon.ico --collect-all mediapipe `
  --add-data "gesturedj\web;gesturedj\web" --add-data "models;models" `
  --add-data "assets\logo;assets\logo" `
  run.py
```

Flaglar nima qiladi:
- `--noconsole` — qora terminal oynasisiz ishlaydi (tray ilova uchun)
- `--collect-all mediapipe` — MediaPipe'ning yashirin model/resurs fayllarini qo'shadi (busiz ishlamaydi)
- `--add-data "manba;maqsad"` — web UI, model va logoni exe ichiga qadoqlaydi
- `--icon` — exe va oyna ikonkasi

Natija: `dist\GestureDJ\` papkasi — `GestureDJ.exe` ni ishga tushiring.
Model, web UI va logo exe ichiga qadoqlanadi; `config.json` va `logs/` exe
yonida yaratiladi.

Eslatmalar:
- onedir rejimi ataylab tanlangan (onefile har ochilishda sekin)
- Windows Defender yangi exe'larni ba'zan shubhali deb belgilashi mumkin —
  bu PyInstaller'ning ma'lum false-positive muammosi
- Xato bo'lsa `logs/gesturedj.log` ga qarang (konsol yo'q rejimda yagona manba)

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
