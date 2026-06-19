import os

from PyQt6.QtCore import QSettings
from app.utils import project_root

DEFAULTS: dict[str, str] = {
    "studentId": "",
    "password": "",
    "acYear": "",
    "acTerm": "",
    "acWeek": "1",
    "showWeekendCourses": "true",
    "autoRefresh": "true",
    "enableLightBlock": "false",
}

def get_qt_settings() -> QSettings:
    return QSettings(
        os.path.join(project_root, "app", "store", "settings.ini"),
        QSettings.Format.IniFormat,
    )

class Settings:
    def __init__(self):
        self._qt_settings = get_qt_settings()

    def value(self, key: str) -> str:
        val = self._qt_settings.value(key)
        if val is None:
            return DEFAULTS.get(key, "")
        return val

    def setValue(self, key: str, value: str):
        self._qt_settings.setValue(key, value)

    def sync(self):
        self._qt_settings.sync()

    def get_qt_settings(self) -> QSettings:
        return self._qt_settings

def get() -> Settings:
    if not hasattr(get, "_instance"):
        get._instance = Settings()
    return get._instance
