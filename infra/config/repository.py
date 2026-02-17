from qgis.core import QgsSettings

from .settings import SETTINGS_NAMESPACE, DEFAULTS


class ConfigRepository:

    def __init__(self):
        self._settings = QgsSettings()
        self._prefix = f"{SETTINGS_NAMESPACE}/"

    def get(self, key, fallback=None):
        default = fallback if fallback is not None else DEFAULTS.get(key)
        value = self._settings.value(self._prefix + key, default)
        expected = DEFAULTS.get(key)
        if isinstance(expected, bool):
            if isinstance(value, str):
                return value.lower() in ("true", "1", "yes")
            return bool(value)
        if isinstance(expected, int) and not isinstance(expected, bool):
            try:
                return int(value)
            except (TypeError, ValueError):
                return expected
        return value

    def set(self, key, value):
        self._settings.setValue(self._prefix + key, value)

    def remove(self, key):
        self._settings.remove(self._prefix + key)

    def all_keys(self):
        self._settings.beginGroup(SETTINGS_NAMESPACE)
        keys = self._settings.childKeys()
        self._settings.endGroup()
        return keys
