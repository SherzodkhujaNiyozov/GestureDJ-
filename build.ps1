# GestureDJ — EXE yig'ish skripti (PyInstaller)
# Ishlatish:  .\build.ps1
# Natija:     dist\GestureDJ\GestureDJ.exe

$ErrorActionPreference = "Stop"
$py = ".\.venv\Scripts\python.exe"
$pyi = ".\.venv\Scripts\pyinstaller.exe"

Write-Host "[1/4] PyInstaller borligini tekshirish..." -ForegroundColor Cyan
if (-not (Test-Path $pyi)) {
    Write-Host "  PyInstaller yo'q, o'rnatilmoqda..." -ForegroundColor Yellow
    & ".\.venv\Scripts\pip.exe" install pyinstaller
}

Write-Host "[2/4] Ikonka (.ico) yangilanmoqda..." -ForegroundColor Cyan
& $py scripts\make_icon.py

Write-Host "[3/4] Eski build tozalanmoqda..." -ForegroundColor Cyan
if (Test-Path dist)  { Remove-Item dist  -Recurse -Force }
if (Test-Path build) { Remove-Item build -Recurse -Force }

Write-Host "[4/4] EXE yig'ilmoqda (1-2 daqiqa)..." -ForegroundColor Cyan
& $pyi --noconfirm --noconsole --name GestureDJ `
    --icon assets\icon.ico `
    --collect-all mediapipe `
    --add-data "gesturedj\web;gesturedj\web" `
    --add-data "models;models" `
    --add-data "assets\logo;assets\logo" `
    run.py

Write-Host ""
Write-Host "TAYYOR -> dist\GestureDJ\GestureDJ.exe" -ForegroundColor Green
