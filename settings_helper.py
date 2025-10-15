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

    # Click-through settings removed

    def get_lock_position(self) -> bool:
        return bool(self.settings.value('behavior/lockPosition', False, type=bool))

    def set_lock_position(self, enabled: bool) -> None:
        self.settings.setValue('behavior/lockPosition', bool(enabled))

    # --- Chat / OpenAI settings ---
    def get_api_key(self) -> str:
        key = self.settings.value('chat/apiKey', type=str)
        return key or ''

    def set_api_key(self, key: str) -> None:
        self.settings.setValue('chat/apiKey', key or '')

    def get_model(self) -> str:
        return self.settings.value('chat/model', 'gpt-4o-mini', type=str)

    def set_model(self, model: str) -> None:
        self.settings.setValue('chat/model', model or 'gpt-4o-mini')

    def get_persona(self) -> str:
        return self.settings.value('chat/persona', 'You are a helpful, friendly desk companion.', type=str)

    def set_persona(self, persona: str) -> None:
        self.settings.setValue('chat/persona', persona or 'You are a helpful, friendly desk companion.')

    def get_chat_name(self) -> str:
        return self.settings.value('chat/name', 'DeskMate', type=str)

    def set_chat_name(self, name: str) -> None:
        self.settings.setValue('chat/name', name or 'DeskMate')


