import sys
import logging


class WindowsStartupManager:
    REG_PATH = r"Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    APP_NAME = 'VirtualDeskmate'

    @staticmethod
    def _get_executable_path() -> str:
        if getattr(sys, 'frozen', False):
            return sys.executable
        return sys.argv[0]

    @staticmethod
    def is_enabled() -> bool:
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WindowsStartupManager.REG_PATH, 0, winreg.KEY_READ) as key:
                value, _ = winreg.QueryValueEx(key, WindowsStartupManager.APP_NAME)
                return bool(value)
        except Exception:
            return False

    @staticmethod
    def set_enabled(enabled: bool) -> None:
        try:
            import winreg
            path = WindowsStartupManager._get_executable_path()
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, WindowsStartupManager.REG_PATH, 0, winreg.KEY_SET_VALUE) as key:
                if enabled:
                    winreg.SetValueEx(key, WindowsStartupManager.APP_NAME, 0, winreg.REG_SZ, f'"{path}"')
                else:
                    try:
                        winreg.DeleteValue(key, WindowsStartupManager.APP_NAME)
                    except FileNotFoundError:
                        pass
        except Exception as e:
            logging.warning('Failed to set Windows startup: %s', e)


