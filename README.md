<img src="assets/logo/gesturedj-mark-128.png" align="left" width="92" height="92" alt="GestureDJ logo">

# GestureDJ

**Control your PC's audio with hand gestures.** A lightweight Windows app that
watches your webcam, recognizes hand gestures, and adjusts the system volume,
plays/pauses media, and mutes — all from across the room. It lives quietly in
the system tray and runs **100% on your machine**.

<br clear="left">

<!-- 📹 TODO: Add a demo GIF here. Record with ScreenToGif (https://www.screentogif.com):
     show pinch→volume, fist→play/pause, beak→mute. A 5–10s loop is perfect. -->
<!-- ![GestureDJ demo](assets/demo.gif) -->

<p align="left">
  <img alt="Platform" src="https://img.shields.io/badge/platform-Windows-0078D6">
  <img alt="Python" src="https://img.shields.io/badge/python-3.11+-3776AB">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-22C55E">
  <img alt="Privacy" src="https://img.shields.io/badge/privacy-100%25%20local-6366F1">
</p>

---

## What you can do

| Gesture | Action |
|---|---|
| 👍 **Thumbs-up** (hold 1s) | **Activate** gesture control |
| 👆 **Index finger up** (hold 1s) | **Deactivate** — send the app back to standby |
| 🤏 **Pinch** (thumb + index, other fingers down) | **Set volume** — the wider the gap, the louder |
| ✊ **Fist** | **Play / Pause** (media key, works with Spotify, YouTube, etc.) |
| 🤌 **Fingertips together** | **Mute / Unmute** |

When idle, the app sits in **standby** at a low frame rate to save CPU and only
watches for the activation gesture. You activate it with a thumbs-up, do your
thing, then dismiss it — so a random hand movement never changes your volume by
accident.

The hand position is shown live in the settings window, and a tray icon tells
you the state at a glance (dim = standby, bright = active).

---

## 🔒 Privacy — why you have nothing to fear

GestureDJ uses your camera, so this matters. Here's exactly what it does and,
more importantly, what it **does not** do:

- 📷 **Your video never leaves the device.** Frames are processed only in memory,
  on your computer, by a local model (Google MediaPipe). No image, frame, or
  hand data is ever sent anywhere.
- 💾 **Nothing is recorded.** The app never saves video or screenshots. Each
  frame is discarded after it's processed.
- 🚫 **No telemetry, analytics, or tracking** of any kind.
- 🌐 **One single network call, ever:** on first run it downloads the ~8 MB
  detection model over HTTPS (verified with a pinned **SHA‑256** hash). The
  packaged `.exe` already bundles the model and the fonts, so it runs **fully
  offline** — opening the settings window contacts no external server.
- 🔑 **No administrator rights required.** Everything runs as a normal user.

Full details: **[SECURITY.md](SECURITY.md)** · All code is open — every network
call and file operation is visible in [`gesturedj/`](gesturedj/).

---

## Download & run (for users)

> **Requirements:** Windows 10/11 and a webcam.

1. Go to the [**Releases**](https://github.com/SherzodkhujaNiyozov/GestureDJ-/releases)
   page and download `GestureDJ-windows.zip`.
2. **Unzip the whole folder** somewhere you can write to (e.g. your Desktop or
   Documents — not `C:\Program Files`).
3. Run **`GestureDJ.exe`** inside the unzipped folder.
4. The app appears in your system tray. **Double-click the tray icon** to open
   the settings window, or **right-click → Settings**.

**First-run notes:**
- **Windows SmartScreen / Defender may warn you** about an unknown publisher.
  This is normal for new, unsigned apps built with PyInstaller — it does not mean
  the app is malicious (the code is fully open). Click *More info → Run anyway*,
  or add the folder to Defender exclusions.
- Keep the whole folder together — `GestureDJ.exe` needs the `_internal` folder
  next to it. Don't move the `.exe` out on its own.

---

## Run from source (for developers)

```powershell
# 1. Clone
git clone https://github.com/SherzodkhujaNiyozov/GestureDJ-.git
cd GestureDJ-

# 2. Create a virtual environment and install deps
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt

# 3. Run
.\.venv\Scripts\python run.py
```

On first run the hand-detection model (~8 MB) is downloaded automatically into
`models/`. Diagnostic mode without the settings window: `python run.py --no-ui`.

---

## Using the app

The app runs in the tray. Right-click the icon for the menu:

- **Settings** (also: double-click the icon) — opens the control window with:
  - **Live status:** current gesture, volume bar, mute indicator, and live
    `pinch` / `beak` / `spread` meters for calibration
  - **Sliders** for every threshold (hold times, pinch range, smoothing, beak
    sensitivity, FPS). Changes apply **instantly** and are saved to `config.json`
  - **Language picker** — 🇺🇿 Oʻzbek · 🇬🇧 English · 🇪🇸 Español · 🇯🇵 日本語 · 🇷🇺 Русский
  - **"Launch with Windows"** toggle (optional autostart)
  - **"Quit app"** button
- **Show preview** — opens a debug window with the live camera feed and hand
  skeleton (handy for fine-tuning thresholds)
- **Quit** — fully closes the app and releases the camera

Closing the settings window with **X** keeps the app running in the tray.
Settings live in `config.json` and logs in `logs/gesturedj.log` (next to the
app). Neither contains personal data.

---

## Build your own `.exe`

**One command** (refreshes the icon, cleans the old build, packages everything):

```powershell
.\build.ps1
```

**Or manually, step by step:**

```powershell
.\.venv\Scripts\pip install pyinstaller          # 1. once
.\.venv\Scripts\python scripts\make_icon.py      # 2. build .ico from the logo
.\.venv\Scripts\pyinstaller --noconfirm --noconsole --name GestureDJ `
  --icon assets\icon.ico --collect-all mediapipe `
  --add-data "gesturedj\web;gesturedj\web" `
  --add-data "models;models" `
  --add-data "assets\logo;assets\logo" `
  run.py                                          # 3. package
```

What the flags do:
- `--noconsole` — no black terminal window (it's a tray app)
- `--collect-all mediapipe` — pulls in MediaPipe's hidden model/resource files (required)
- `--add-data "src;dest"` — bundles the web UI, model, and logo into the exe
- `--icon` — sets the exe and window icon

Output: `dist\GestureDJ\` — run `GestureDJ.exe`. The model, web UI, and fonts are
bundled inside; `config.json` and `logs/` are created next to the exe.

> **onedir, not onefile** — onedir is intentional: onefile unpacks everything to
> a temp folder on every launch (slow, 10–20s). onedir starts instantly.

**To publish a release:** zip the *entire* `dist\GestureDJ\` folder (not just the
`.exe`) and upload the zip to GitHub Releases. The ~240 MB zip fits well within
GitHub's 2 GB per-file limit.

---

## How it works

```
gesturedj/
  main.py       — entry point: starts the worker thread, tray, and UI
  app.py        — state machine (standby/active) + the camera loop
  gestures.py   — turns 21 hand landmarks into gestures (the math)
  audio.py      — system volume via pycaw (Windows Core Audio)
  media.py      — media keys (play/pause)
  smoothing.py  — EMA filter to remove jitter
  model.py      — downloads & SHA-256-verifies the detection model
  paths.py      — dev vs frozen (.exe) path handling
  autostart.py  — optional "launch with Windows" (HKCU registry)
  tray.py       — system-tray icon and menu (pystray)
  ui.py         — settings window (pywebview) + JS↔Python bridge
  web/          — settings UI (HTML/CSS/JS, dark theme, local fonts, i18n)
  config.py     — defaults + config.json load/save (validated & clamped)
```

The camera loop runs on a worker thread; gesture detection is done locally by
MediaPipe's HandLandmarker. The settings window is a local HTML page rendered by
the OS WebView, talking to Python through a small, validated API bridge.

**Tech stack:** Python · [MediaPipe Tasks](https://developers.google.com/mediapipe)
(HandLandmarker) · OpenCV · pycaw · pystray · pywebview · PyInstaller

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Hand not detected | Improve lighting; make sure your hand is fully in frame. Open **Show preview** to see what the camera sees. |
| Gestures feel unreliable | Open **Settings → Show preview** and watch the live `pinch`/`beak`/`spread` meters, then tune the sliders to your hand. |
| Volume jumps around | Lower the **Smoothing** slider (smaller = smoother). |
| Defender flagged the exe | Known PyInstaller false positive. *More info → Run anyway*, or add an exclusion. The source is fully open. |
| App won't start / crashes | Check `logs/gesturedj.log` next to the exe — it records the error. |

---

## License

[MIT](LICENSE) © Sherzodkhuja Niyozov
