"""Windows bilan avtomatik ishga tushish (HKCU Run kaliti, admin shart emas)."""

import logging
import sys
import winreg

from .paths import app_dir, is_frozen

log = logging.getLogger(__name__)

_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
_APP_NAME = "GestureDJ"


def _command() -> str:
    if is_frozen():
        return f'"{sys.executable}"'
    # Dev rejimi: pythonw (konsolsiz) bilan run.py
    pythonw = sys.executable.replace("python.exe", "pythonw.exe")
    return f'"{pythonw}" "{app_dir() / "run.py"}"'


def is_enabled() -> bool:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, _RUN_KEY) as key:
            winreg.QueryValueEx(key, _APP_NAME)
        return True
    except OSError:
        return False


def set_enabled(enabled: bool) -> bool:
    try:
        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER, _RUN_KEY, 0, winreg.KEY_SET_VALUE
        ) as key:
            if enabled:
                winreg.SetValueEx(key, _APP_NAME, 0, winreg.REG_SZ, _command())
                log.info("Avtostart yoqildi: %s", _command())
            else:
                try:
                    winreg.DeleteValue(key, _APP_NAME)
                except FileNotFoundError:
                    pass
                log.info("Avtostart o'chirildi")
        return True
    except OSError:
        log.exception("Avtostartni o'zgartirib bo'lmadi")
        return False
