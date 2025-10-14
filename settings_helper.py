import os
from PyQt5.QtCore import QSettings


class SettingsHelper:
    def __init__(self):
        self.settings = QSettings('VirtualPartner', 'VirtualDeskmate')

    def get_last_gif_path(self) -> str:
        path = self.settings.value('paths/lastGif', type=str)
        return path if path and os.path.exists(path) else ''

    def set_last_gif_path(self, path: str) -> None:
        self.settings.setValue('paths/lastGif', path)

    def get_opacity(self) -> float:
        value = self.settings.value('ui/opacity', 1.0, type=float)
        return max(0.2, min(1.0, value))

    def set_opacity(self, value: float) -> None:
        self.settings.setValue('ui/opacity', max(0.2, min(1.0, float(value))))

    def get_size(self) -> int:
        return int(self.settings.value('ui/size', 250))

    def set_size(self, value: int) -> None:
        clamped = max(96, min(600, int(value)))
        self.settings.setValue('ui/size', clamped)

    def get_click_through(self) -> bool:
        return bool(self.settings.value('behavior/clickThrough', False, type=bool))

    def set_click_through(self, enabled: bool) -> None:
        self.settings.setValue('behavior/clickThrough', bool(enabled))

    def get_lock_position(self) -> bool:
        return bool(self.settings.value('behavior/lockPosition', False, type=bool))

    def set_lock_position(self, enabled: bool) -> None:
        self.settings.setValue('behavior/lockPosition', bool(enabled))


