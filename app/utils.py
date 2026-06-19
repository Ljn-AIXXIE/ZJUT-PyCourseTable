import datetime
import os

import os
from PyQt6.QtCore import QSettings

_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def get_settings() -> QSettings:
    return QSettings(
        os.path.join(_project_root, "settings.ini"),
        QSettings.Format.IniFormat,
    )


def apply_system_accent_color():
    """Apply the Windows system accent color to Fluent widgets."""
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\DWM",
        )
        value, _ = winreg.QueryValueEx(key, "AccentColor")
        winreg.CloseKey(key)

        b = (value >> 16) & 0xFF
        g = (value >> 8) & 0xFF
        r = value & 0xFF

        from qfluentwidgets import setThemeColor
        setThemeColor(f"#{r:02x}{g:02x}{b:02x}", save=False)
    except Exception:
        pass


def parseRawHeader(header: str) -> dict[str, str]:
    dic: dict = {}
    for item in header.split('\n'):
        if item.strip() == '': continue
        tempArr = item.split(': ')
        dic[tempArr[0].strip()] = tempArr[1]
    return dic

def encrypt_password(password: str, exponent_hex: str, modulus_hex: str) -> str:
    e = int(exponent_hex, 16)
    m = int(modulus_hex, 16)

    k = (m.bit_length() + 7) // 8
    num_digits = (k + 1) // 2  # ceil(k / 2)
    chunk_size = max(2 * (num_digits - 1), 2)

    reversed_pwd = password[::-1]
    a = [ord(c) for c in reversed_pwd]

    while len(a) % chunk_size != 0:
        a.append(0)

    parts = []
    num_digits = chunk_size // 2

    for i in range(0, len(a), chunk_size):
        block = 0
        for d in range(num_digits):
            lo = a[i + d * 2]
            hi = a[i + d * 2 + 1]
            digit_val = lo | (hi << 8)
            block |= digit_val << (d * 16)

        encrypted = pow(block, e, m)
        parts.append(f"{encrypted:x}")

    return " ".join(parts)

def check_dir(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def parse_course_week(zcd: str) -> set[int]:
    _zcd = zcd.replace("周", "")
    s: set[int] = set()
    for part in _zcd.split(","):
        if '-' in part:
            ranges: list[str] = part.split('-')
            for num in range(int(ranges[0]), int(ranges[1]) + 1):
                s.add(num)
        else:
            s.add(int(part))
    return s

def parse_course_date(first_date: str, acWeek: int, week: int) -> str:
    dt: datetime.datetime = datetime.datetime.strptime(first_date, "%Y-%m-%d")
    dt = dt + datetime.timedelta(days=7*(acWeek-1)) + datetime.timedelta(days=week-1)
    return dt.strftime("%Y-%m-%d")