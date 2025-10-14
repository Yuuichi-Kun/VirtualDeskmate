import sys
import os
import logging


def resource_path(relative_path: str) -> str:
    try:
        base_path = sys._MEIPASS  # type: ignore[attr-defined]
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)


def setup_logging() -> None:
    try:
        appdata = os.getenv('APPDATA') or os.path.expanduser('~')
        log_dir = os.path.join(appdata, 'VirtualDeskmate', 'logs')
        os.makedirs(log_dir, exist_ok=True)
        log_file = os.path.join(log_dir, 'app.log')
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
        logging.info('Logging initialized')
    except Exception as e:
        logging.basicConfig(level=logging.INFO)
        logging.warning('Logging setup failed: %s', e)


